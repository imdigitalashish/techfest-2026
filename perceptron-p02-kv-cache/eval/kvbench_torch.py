"""kvbench_torch — PyTorch (CPU) twin of eval/kvbench.py, used for all measured numbers in this repo.

Same protocol, workload, methods, byte accounting and statistics as the MLX harness (eval/kvbench.py), which stays
the Apple-silicon path. Weights: mlx-community/Llama-3.2-1B-Instruct-4bit dequantised to fp16 safetensors by
eval/azure/setup_torch.sh, then computed in fp32 on CPU; KV stored as fp16 (32 KiB/token, as in the MLX deployment).

Protocol (shared-context multi-query, query-agnostic): one context (WikiText-103 + 4 synthetic needles) is
prefilled once; each method builds its store BEFORE any question is seen; the same 4 questions are answered
from that store alone (paired across methods). Not a multi-turn dialogue.

Methods: full | int8/int4/int2 (per-token group-64 affine quantisation of K and V, stored packed; not KIVI's
per-channel keys) | streaming (4 sinks + recent) | random (sinks + recent 64 + random) | h2o (accumulated
attention + recent half) | snapkv (last-64-token observation window, pool 5) | knorm (low key L2 norm) |
snapkv_qa (ORACLE: selects with the question) | rod (spike: resident streaming KV + packed 2-bit single-layer key
sketch + int32 ids; question queries pick 64-token blocks to re-prefill) | rodlex (control: same store, no sketch,
IDF lexical block choice) | kvp_* (NVIDIA kvpress reference presses: StreamingLLM, SnapKV, ObservedAttention ~ H2O,
Knorm, ExpectedAttention, TOVA; run in a venv with kvpress 0.5.5 / transformers<5.3). rod/rodlex KV budgets shrink by
every stored extra byte (sketch, window queries, ids), so their answer-time bytes never exceed the baselines'.

Reproduce (on the VM): python eval/kvbench_torch.py --ctx 4096 --n 12 --seed 0 --style literal --name <name>
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import platform
import random
import resource
import time
from collections import Counter, defaultdict
from pathlib import Path

import torch
import torch.nn.functional as F
from safetensors.torch import load_file
from transformers import AutoTokenizer, LlamaConfig, LlamaForCausalLM
from transformers.models.llama.modeling_llama import apply_rotary_pos_emb

ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "mlx-community/Llama-3.2-1B-Instruct-4bit"
WEIGHTS = ROOT / ".data" / "llama32_1b_q4deq_fp16.safetensors"
CONFIG = ROOT / ".data" / "llama32_1b_config.json"
N_SINK, N_RECENT, WIN, BLOCK = 4, 64, 64, 64
KV_DTYPE = torch.float16  # the MLX 4-bit model computes in fp16, so its KV cache is fp16 (2 B/value)
DATE = "26 Jul 2024"  # pinned: the Llama 3.2 chat template otherwise inserts today's date
ADJ = ("amber azure bold brisk calm coral crimson dusty eager fuzzy gentle golden hollow icy jade keen "
       "lunar misty noble olive proud quiet rapid rusty silent silver solar tidal urban velvet vivid wild").split()
NOUN = ("otter falcon maple harbor lantern meadow comet canyon willow beacon cobra glacier heron island "
        "jaguar kettle lotus marble nebula orchid pepper quartz raven saddle tiger tulip violin walrus").split()
STYLES = {
    "literal": ("The special magic number for {k} is {v}.",
                "What is the special magic number for {k} mentioned in the text above? Answer with the number only."),
    "paraphrase": ("Note for the record: {k} was issued the access code {v}.",
                   "Which seven-digit code was issued to {k}? Reply with the digits only."),
    # amendment 1 (T3): the question names the key with synonyms of the needle's words -> no lexical overlap on keys
    "alias": ("The vault of the {k} opens with the code {v}.",
              "Which code opens the vault of the {k}? Reply with the digits only."),
}
SYN_ADJ = [("big", "large"), ("small", "little"), ("fast", "quick"), ("old", "ancient"), ("happy", "cheerful"),
           ("cold", "chilly"), ("rich", "wealthy"), ("smart", "clever"), ("angry", "furious"), ("quiet", "silent"),
           ("tired", "sleepy"), ("strong", "powerful")]
SYN_NOUN = [("dog", "hound"), ("car", "automobile"), ("house", "home"), ("boat", "ship"), ("doctor", "physician"),
            ("child", "kid"), ("rock", "stone"), ("road", "street"), ("gift", "present"), ("shop", "store"),
            ("sofa", "couch"), ("hat", "cap")]


def nb(t):
    return t.numel() * t.element_size()


# ---------------- storage ----------------
class Packed:
    """Affine group quantisation over the last axis (group 64), codes bit-packed into uint8, scale/bias in the KV dtype (fp16)."""

    def __init__(self, x, bits, group=64):
        self.shape, self.dtype, self.bits, self.group = x.shape, x.dtype, bits, group
        xf = x.float().reshape(-1, group)
        n = 2 ** bits - 1
        lo, hi = xf.min(1, keepdim=True).values, xf.max(1, keepdim=True).values
        self.scale = ((hi - lo) / n).clamp_min(1e-8).to(x.dtype)
        self.bias = lo.to(x.dtype)
        q = torch.round((xf - self.bias.float()) / self.scale.float()).clamp(0, n).to(torch.uint8)
        per = 8 // bits
        q = q.view(-1, group // per, per)
        packed = torch.zeros(q.shape[:2], dtype=torch.uint8)
        for i in range(per):
            packed |= q[:, :, i] << (bits * i)
        self.q = packed

    @property
    def nbytes(self):
        return nb(self.q) + nb(self.scale) + nb(self.bias)

    def dense(self):
        per, n = 8 // self.bits, 2 ** self.bits - 1
        q = torch.stack([(self.q >> (self.bits * i)) & n for i in range(per)], -1).reshape(-1, self.group)
        return (q.float() * self.scale.float() + self.bias.float()).reshape(self.shape).to(self.dtype)


def dense(x):
    return x.dense() if isinstance(x, Packed) else x


def xbytes(x):
    return x.nbytes if isinstance(x, Packed) else nb(x)


class Cache:
    """Per-layer stored past (tensor or Packed) + dense tail of tokens appended while answering."""

    def __init__(self, K=None, V=None, nl=None):
        n = len(K) if K is not None else nl
        self.K = list(K) if K is not None else [None] * n
        self.V = list(V) if V is not None else [None] * n
        self.tk, self.tv = [None] * n, [None] * n

    def fork(self):
        c = Cache(self.K, self.V)
        c.tk, c.tv = list(self.tk), list(self.tv)
        return c

    def kv(self, li):
        ks = [dense(x) for x in (self.K[li], self.tk[li]) if x is not None]
        vs = [dense(x) for x in (self.V[li], self.tv[li]) if x is not None]
        if not ks:
            return None, None
        return (ks[0], vs[0]) if len(ks) == 1 else (torch.cat(ks, 2), torch.cat(vs, 2))

    def append(self, li, k, v):
        self.tk[li] = k if self.tk[li] is None else torch.cat([self.tk[li], k], 2)
        self.tv[li] = v if self.tv[li] is None else torch.cat([self.tv[li], v], 2)

    def stored_bytes(self):
        return sum(xbytes(x) for x in self.K + self.V if x is not None)


# ---------------- workload ----------------
def chat(tok, content):
    return tok.apply_chat_template([{"role": "user", "content": content}], tokenize=False,
                                   add_generation_prompt=True, date_string=DATE)


def make_sample(tok, paras, ctx_tokens, n_needles, rng, style="literal"):
    tn, tq = STYLES[style]
    keys, needles = set(), []
    if style == "alias":
        for a, w in zip(rng.sample(SYN_ADJ, n_needles), rng.sample(SYN_NOUN, n_needles)):
            j = int(rng.random() < 0.5)
            needles.append({"key": f"{a[j]} {w[j]}", "qkey": f"{a[1 - j]} {w[1 - j]}",
                            "value": str(rng.randint(1_000_000, 9_999_999))})
    while len(needles) < n_needles:
        k = f"{rng.choice(ADJ)}-{rng.choice(NOUN)}"
        if k not in keys:
            keys.add(k)
            needles.append({"key": k, "value": str(rng.randint(1_000_000, 9_999_999))})
    i, body, n_tok = rng.randrange(0, len(paras) - 2000), [], 0
    budget = ctx_tokens - 90 - 16 * n_needles
    while n_tok < budget:
        body.append(paras[i])
        n_tok += len(tok.encode(paras[i], add_special_tokens=False)) + 1
        i += 1
    for j, nd in enumerate(needles):
        nd["depth_target"] = round(0.05 + 0.9 * (j + rng.random()) / n_needles, 3)
    for nd in sorted(needles, key=lambda x: -x["depth_target"]):
        body.insert(round(nd["depth_target"] * len(body)), tn.format(k=nd["key"], v=nd["value"]))
    text = ("Below is a long text. Hidden in it are several special codes and numbers. Read carefully; "
            "you will be asked about them later.\n\n" + "\n".join(body))
    pre, out = None, []
    for nd in needles:
        pre, post = chat(tok, text + "\n\n@@SPLIT@@" + tq.format(k=nd.get("qkey", nd["key"]))).split("@@SPLIT@@")
        out.append((tok.encode(post, add_special_tokens=False), nd))
    ctx_ids = tok.encode(pre, add_special_tokens=False)
    for _, nd in out:
        nd["n_q_content"] = len(tok.encode(tq.format(k=nd.get("qkey", nd["key"])), add_special_tokens=False))
        pat = tok.encode(nd["value"], add_special_tokens=False)
        nd["pos"] = next((p for p in range(len(ctx_ids) - len(pat) + 1) if ctx_ids[p:p + len(pat)] == pat), -1)
        nd["depth_tok"] = round(nd["pos"] / len(ctx_ids), 3)
    return ctx_ids, out


# ---------------- engine: explicit-cache Llama forward over HF modules ----------------
class Engine:
    def __init__(self, model, tok):
        self.model, self.tok, self.inner = model, tok, model.model
        c = model.config
        self.nh, self.nkv, self.nl = c.num_attention_heads, c.num_key_value_heads, c.num_hidden_layers
        self.hd = getattr(c, "head_dim", None) or c.hidden_size // c.num_attention_heads
        self.scale = self.hd ** -0.5
        ids = tok.convert_tokens_to_ids(["<|eot_id|>", "<|eom_id|>", "<|end_of_text|>"])
        self.eos = {i for i in ids if isinstance(i, int)} | {tok.eos_token_id}

    @torch.inference_mode()
    def forward(self, ids, pos0, cache, capture=0, acc=None):
        L, g = len(ids), self.nh // self.nkv
        x = self.inner.embed_tokens(torch.tensor([ids]))
        cos, sin = self.inner.rotary_emb(x, torch.arange(pos0, pos0 + L)[None])
        caps = {}
        for li, layer in enumerate(self.inner.layers):
            at = layer.self_attn
            h = layer.input_layernorm(x)
            q = at.q_proj(h).view(1, L, self.nh, self.hd).transpose(1, 2)
            k = at.k_proj(h).view(1, L, self.nkv, self.hd).transpose(1, 2)
            v = at.v_proj(h).view(1, L, self.nkv, self.hd).transpose(1, 2)
            q, k = apply_rotary_pos_emb(q, k, cos, sin)
            k, v = k.to(KV_DTYPE), v.to(KV_DTYPE)
            pk, pv = cache.kv(li)
            S0 = 0 if pk is None else pk.shape[2]
            kk = k if pk is None else torch.cat([pk, k], 2)
            vv = v if pv is None else torch.cat([pv, v], 2)
            cache.append(li, k, v)
            kf, vf = kk.to(q.dtype), vv.to(q.dtype)
            mask = (torch.arange(S0 + L)[None, :] <= (S0 + torch.arange(L))[:, None]) if L > 1 else None
            o = F.scaled_dot_product_attention(q, kf.repeat_interleave(g, 1), vf.repeat_interleave(g, 1),
                                               attn_mask=mask, scale=self.scale)
            if capture:
                caps[li] = q[:, :, -capture:, :]
            if acc is not None:  # H2O statistic: attention mass each key receives
                s = torch.matmul((q * self.scale).reshape(1, self.nkv, g, L, self.hd),
                                 kf[:, :, None].transpose(-1, -2)).float()
                if mask is not None:
                    s = s.masked_fill(~mask, float("-inf"))
                p = torch.softmax(s, -1).sum((2, 3))[0]
                if acc[li] is not None:
                    p[:, :acc[li].shape[1]] += acc[li]
                acc[li] = p
            x = x + at.o_proj(o.transpose(1, 2).reshape(1, L, -1))
            x = x + layer.mlp(layer.post_attention_layernorm(x))
        return self.inner.norm(x), caps

    def prefill(self, ids, chunk=256):
        c, acc, T, caps = Cache(nl=self.nl), [None] * self.nl, len(ids), None
        bounds = list(range(0, T - WIN, chunk)) + [T - WIN]
        for a, b in zip(bounds, bounds[1:] + [T]):
            _, cp = self.forward(ids[a:b], a, c, capture=WIN if b == T else 0, acc=acc)
            if b == T:
                caps = cp
        return c.tk, c.tv, acc, caps

    @torch.inference_mode()
    def answer(self, store, pos, q_ids, max_new=10):
        c = store.fork()
        h, _ = self.forward(q_ids, pos, c)
        out, p = [], pos + len(q_ids)
        t = int(self.model.lm_head(h[:, -1, :]).argmax(-1))
        for _ in range(max_new):
            if t in self.eos:
                break
            out.append(t)
            h, _ = self.forward([t], p, c)
            p += 1
            t = int(self.model.lm_head(h[:, -1, :]).argmax(-1))
        return self.tok.decode(out)


# ---------------- scorers / selectors ----------------
def avgpool(x, k=5):
    return F.avg_pool1d(x[None], k, stride=1, padding=k // 2, count_include_pad=True)[0]


def window_scores(qw, Kl, scale, causal):
    nkv, S, w = Kl.shape[1], Kl.shape[2], qw.shape[2]
    g = qw.shape[1] // nkv
    s = torch.matmul((qw * scale).reshape(1, nkv, g, w, -1), Kl.to(qw.dtype)[:, :, None].transpose(-1, -2)).float()
    if causal:
        s = s.masked_fill(~(torch.arange(S)[None, :] <= (S - w + torch.arange(w))[:, None]), float("-inf"))
    return avgpool(torch.softmax(s, -1).sum((2, 3))[0])


def topk_idx(score, B, T, n_recent=N_RECENT):
    pos = torch.arange(T)
    force = (pos < N_SINK) | (pos >= T - n_recent)
    s = torch.where(force[None], torch.tensor(1e30), score.float())
    return torch.sort(torch.topk(s, B, dim=1).indices, dim=1).values


def stream_idx(T, B, nkv):
    i = torch.cat([torch.arange(N_SINK), torch.arange(T - (B - N_SINK), T)])
    return i[None].expand(nkv, B)


def gather(X, idx):
    return torch.gather(X[0], 1, idx[:, :, None].expand(-1, -1, X.shape[-1]))[None].contiguous()


# ---------------- spike: Recall-on-Demand ----------------
SCORERS = ("softmax_sum", "max_logit", "lift_mean", "lift_max", "softmax_lift")


def block_scores(qq, wq, sk, scale, scorer, nkv):
    """Per-key relevance of evicted keys. qq [1,nh,Lq,hd] question queries; wq [1,nh,W,hd] context-window queries
    (used by the contrastive lift* scorers to cancel keys that every query attends to); sk [1,nkv,E,hd] -> [E]."""
    g = qq.shape[1] // nkv
    lq = torch.matmul((qq * scale).reshape(1, nkv, g, qq.shape[2], -1), sk[:, :, None].transpose(-1, -2)).float()[0]
    if scorer == "softmax_sum":
        s = torch.softmax(lq, -1).sum((1, 2))
    elif scorer == "max_logit":
        s = lq.amax((1, 2))
    else:
        lw = torch.matmul((wq * scale).reshape(1, nkv, g, wq.shape[2], -1), sk[:, :, None].transpose(-1, -2)).float()[0]
        if scorer == "lift_mean":
            s = lq.mean((1, 2)) - lw.mean((1, 2))
        elif scorer == "lift_max":
            s = lq.amax((1, 2)) - lw.mean((1, 2))
        else:
            s = torch.softmax(lq, -1).mean((1, 2)) - torch.softmax(lw, -1).mean((1, 2))
    return s.max(0).values


def rod_build(E, Kf, Vf, ctx_ids, B, cfg, caps):
    """cfg: dict(layer, bits, scorer, lexical). Store = resident streaming KV + packed sketch (+ window queries for
    lift scorers) + int32 token ids. Every stored byte is deducted from the KV budget B (tokens x 32 KiB)."""
    T, per_tok = len(ctx_ids), 2 * E.nl * E.nkv * E.hd * 2
    lexical, layer_s = cfg["lexical"], cfg["layer"]
    wq = None if lexical or not cfg["scorer"].startswith(("lift", "softmax_lift")) else caps[layer_s].to(KV_DTYPE).contiguous()
    sk_per_tok = 0 if lexical else E.nkv * (E.hd * cfg["bits"] // 8 + 4)
    extra = sk_per_tok * T + 4 * T + (nb(wq) if wq is not None else 0)
    B_kv = max(N_SINK + 2, B - math.ceil(extra / per_tok))
    B_res = max(N_SINK + 1, B_kv // 2)
    idx = stream_idx(T, B_res, E.nkv)
    Kr, Vr = [gather(k, idx) for k in Kf], [gather(v, idx) for v in Vf]
    ev0, ev1 = N_SINK, T - (B_res - N_SINK)
    sketch = None if lexical else Packed(Kf[layer_s][:, :, ev0:ev1], cfg["bits"])
    ids = torch.tensor(ctx_ids, dtype=torch.int32)
    st = {"Kr": Kr, "Vr": Vr, "sketch": sketch, "wq": wq, "ids": ids, "ev0": ev0, "ev1": ev1, "B_res": B_res,
          "B_rec": B_kv - B_res, "T": T, "cfg": cfg}
    st["sketch_bytes"] = (sketch.nbytes if sketch else 0) + (nb(wq) if wq is not None else 0)
    st["stored_bytes"] = sum(nb(x) for x in Kr + Vr) + st["sketch_bytes"] + nb(ids)
    return st


@torch.inference_mode()
def rod_answer(E, st, q_ids, n_content, halo=0):
    T, ev0, ev1, cfg = st["T"], st["ev0"], st["ev1"], st["cfg"]
    En = ev1 - ev0
    nblk, m = -(-En // BLOCK), max(0, st["B_rec"] // BLOCK)
    n_use = n_content if cfg["qsel"] == "content" else len(q_ids)
    if m == 0 or En <= 0:
        order = []
    elif cfg["lexical"]:
        ids = st["ids"][ev0:ev1].tolist()
        blocks = [set(ids[i * BLOCK:(i + 1) * BLOCK]) for i in range(nblk)]
        df = Counter(t for b in blocks for t in b)
        qset = set(q_ids[:n_use])
        sc = [sum(math.log((nblk + 1) / (df[t] + 1)) for t in qset if t in b) for b in blocks]
        order = sorted(range(nblk), key=lambda i: -sc[i])[:m]
    else:
        _, caps = E.forward(q_ids, T, Cache(st["Kr"], st["Vr"]), capture=len(q_ids))
        qq = caps[cfg["layer"]][:, :, :n_use].float()
        wq = st["wq"].float() if st["wq"] is not None else None
        r = block_scores(qq, wq, st["sketch"].dense().float(), E.scale, cfg["scorer"], E.nkv)
        rb = F.pad(r, (0, nblk * BLOCK - En), value=float("-inf")).view(nblk, BLOCK).max(1).values
        order = torch.topk(rb, min(m, nblk)).indices.tolist()
    chosen = sorted(order)
    addK, addV = [[] for _ in range(E.nl)], [[] for _ in range(E.nl)]
    for b in chosen:
        s = ev0 + b * BLOCK
        e, hs = min(s + BLOCK, ev1), max(ev0, s - halo)
        c = Cache([k[:, :, :N_SINK] for k in st["Kr"]], [v[:, :, :N_SINK] for v in st["Vr"]])
        E.forward(st["ids"][hs:e].tolist(), hs, c)
        for l in range(E.nl):
            addK[l].append(c.tk[l][:, :, s - hs:])
            addV[l].append(c.tv[l][:, :, s - hs:])
    aug = Cache([torch.cat([st["Kr"][l]] + addK[l], 2) for l in range(E.nl)],
                [torch.cat([st["Vr"][l]] + addV[l], 2) for l in range(E.nl)])
    text = E.answer(aug, T, q_ids)
    rec = sum(nb(x) for l in range(E.nl) for x in addK[l] + addV[l])
    return text, chosen, rec


# ---------------- reference baselines: NVIDIA kvpress presses (optional; separate venv, transformers<5.3) ----------------
KVP = {"kvp_streaming": "StreamingLLMPress", "kvp_snapkv": "SnapKVPress", "kvp_observed": "ObservedAttentionPress",
       "kvp_knorm": "KnormPress", "kvp_expected": "ExpectedAttentionPress", "kvp_tova": "TOVAPress"}


@torch.inference_mode()
def kvp_store(E, ctx_ids, method, keep_frac):
    import kvpress
    press = getattr(kvpress, KVP[method])(compression_ratio=1 - keep_frac)
    model = E.model
    impl = "eager" if method == "kvp_observed" else "sdpa"  # ObservedAttentionPress needs attention weights
    model.config._attn_implementation = impl
    with press(model):
        out = model(torch.tensor([ctx_ids]), use_cache=True, logits_to_keep=1)
    model.config._attn_implementation = "sdpa"
    pkv = out.past_key_values
    layers = getattr(pkv, "layers", None)
    K = [(layers[l].keys if layers is not None else pkv.key_cache[l]).to(KV_DTYPE).contiguous() for l in range(E.nl)]
    V = [(layers[l].values if layers is not None else pkv.value_cache[l]).to(KV_DTYPE).contiguous() for l in range(E.nl)]
    return Cache(K, V)


# ---------------- statistics ----------------
def boot_ci(per_ctx, reps=2000, seed=0):
    """Context-clustered bootstrap 95% CI of a mean; per_ctx: list of (sum, count) per context."""
    rng, n = random.Random(seed), len(per_ctx)
    st = sorted(sum(s for s, _ in smp) / max(1, sum(c for _, c in smp))
                for smp in ([per_ctx[rng.randrange(n)] for _ in range(n)] for _ in range(reps)))
    return (round(st[int(0.025 * reps)], 4), round(st[int(0.975 * reps) - 1], 4))


def boot_delta(diffs, reps=2000, seed=0):
    rng, n = random.Random(seed), len(diffs)
    st = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps))
    return (round(st[int(0.025 * reps)], 4), round(st[int(0.975 * reps) - 1], 4))


def load_model():
    cfg = json.loads(CONFIG.read_text())
    for k in ("quantization", "quantization_config"):
        cfg.pop(k, None)
    config = LlamaConfig(**cfg)
    with torch.device("meta"):
        model = LlamaForCausalLM(config)
    sd = {k: v.float() for k, v in load_file(str(WEIGHTS)).items()}
    missing, unexpected = model.load_state_dict(sd, strict=False, assign=True)
    assert not unexpected and set(missing) <= {"lm_head.weight"}, (missing, unexpected)
    if "lm_head.weight" in missing:
        model.lm_head.weight = model.model.embed_tokens.weight
    model.model.rotary_emb = type(model.model.rotary_emb)(config=config)  # rebuild inv_freq off the meta device
    return model.float().eval()


# ---------------- driver ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ctx", type=int, default=4096)
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--needles", type=int, default=4)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--fracs", default="0.1,0.25,0.5")
    ap.add_argument("--methods", default="full,int8,int4,int2,streaming,random,h2o,snapkv,knorm,snapkv_qa,rod,rodlex")
    ap.add_argument("--style", default="literal", choices=list(STYLES))
    ap.add_argument("--rod_layer", type=int, default=8)
    ap.add_argument("--rod_bits", type=int, default=2)
    ap.add_argument("--halo", type=int, default=0)
    ap.add_argument("--rod_scorer", default="softmax_sum", choices=SCORERS)
    ap.add_argument("--rod_qsel", default="all", choices=["all", "content"])
    ap.add_argument("--lex_qsel", default="content", choices=["all", "content"])
    ap.add_argument("--kvp_fracs", default="0.1,0.25", help="keep fractions for kvpress methods")
    ap.add_argument("--threads", type=int, default=torch.get_num_threads())
    ap.add_argument("--name", default=None)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    torch.manual_seed(a.seed)
    name = a.name or f"torch_ctx{a.ctx}_n{a.n}_s{a.seed}_{a.style}"
    outdir = ROOT / "eval" / "results"
    outdir.mkdir(parents=True, exist_ok=True)
    paras = (ROOT / ".data" / "haystack.txt").read_text(encoding="utf-8").split("\n")
    snap = (glob.glob(os.path.expanduser(f"~/.cache/huggingface/hub/models--{MODEL_ID.replace('/', '--')}/snapshots/*")) or ["?"])[0]
    tok = AutoTokenizer.from_pretrained(snap if snap != "?" else MODEL_ID)
    model = load_model()
    E = Engine(model, tok)
    per_tok = 2 * E.nl * E.nkv * E.hd * 2
    rng = random.Random(a.seed)
    fracs = [float(f) for f in a.fracs.split(",")]
    methods = a.methods.split(",")
    configs = [(m, 1.0) for m in ("full", "int8", "int4", "int2") if m in methods]
    configs += [(m, f) for m in ("streaming", "random", "h2o", "snapkv", "knorm", "snapkv_qa", "rod", "rodlex")
                if m in methods for f in fracs]
    configs += [(m, float(f)) for m in KVP if m in methods for f in a.kvp_fracs.split(",")]
    rows, t0 = [], time.time()
    for si in range(a.n):
        ctx_ids, qs = make_sample(tok, paras, a.ctx, a.needles, rng, a.style)
        T = len(ctx_ids)
        tp = time.time()
        Kf, Vf, acc, caps = E.prefill(ctx_ids)
        prefill_s = time.time() - tp
        full_bytes = sum(nb(x) for x in Kf + Vf)
        assert full_bytes == T * per_tok, (full_bytes, T * per_tok)
        print(f"sample {si + 1}/{a.n} T={T} prefill={prefill_s:.1f}s", flush=True)
        for m, f in configs:
            B = max(N_SINK + N_RECENT + 1, round(f * T))
            tb, store, st = time.time(), None, None
            if m == "full":
                store = Cache(Kf, Vf)
            elif m.startswith("int"):
                bits = int(m[3:])
                store = Cache([Packed(k, bits) for k in Kf], [Packed(v, bits) for v in Vf])
            elif m in ("streaming", "random", "h2o", "snapkv", "knorm"):
                if m == "streaming":
                    idxs = [stream_idx(T, B, E.nkv)] * E.nl
                elif m == "random":
                    gen = torch.Generator().manual_seed(a.seed * 1000 + si)
                    idxs = [topk_idx(torch.rand(E.nkv, T, generator=gen), B, T) for _ in range(E.nl)]
                elif m == "h2o":
                    idxs = [topk_idx(acc[l], B, T, n_recent=B // 2) for l in range(E.nl)]
                elif m == "snapkv":
                    idxs = [topk_idx(window_scores(caps[l], Kf[l], E.scale, True), B, T) for l in range(E.nl)]
                else:
                    idxs = [topk_idx(-Kf[l][0].float().norm(dim=-1), B, T) for l in range(E.nl)]
                store = Cache([gather(Kf[l], idxs[l]) for l in range(E.nl)], [gather(Vf[l], idxs[l]) for l in range(E.nl)])
            elif m in ("rod", "rodlex"):
                cfg = {"layer": a.rod_layer, "bits": a.rod_bits, "scorer": a.rod_scorer, "lexical": m == "rodlex",
                       "qsel": a.lex_qsel if m == "rodlex" else a.rod_qsel}
                st = rod_build(E, Kf, Vf, ctx_ids, B, cfg, caps)
            elif m in KVP:
                store = kvp_store(E, ctx_ids, m, f)
            build_s = time.time() - tb
            for qi, (q_ids, nd) in enumerate(qs):
                ta, extra = time.time(), {}
                if m == "snapkv_qa":
                    _, qc = E.forward(q_ids, T, Cache(Kf, Vf), capture=len(q_ids))
                    idxs = [topk_idx(window_scores(qc[l], Kf[l], E.scale, False), B, T) for l in range(E.nl)]
                    sq = Cache([gather(Kf[l], idxs[l]) for l in range(E.nl)], [gather(Vf[l], idxs[l]) for l in range(E.nl)])
                    text, kb = E.answer(sq, T, q_ids), sq.stored_bytes()
                    ab = kb
                elif st is not None:
                    text, chosen, rec = rod_answer(E, st, q_ids, nd["n_q_content"], halo=a.halo)
                    kb, ab = st["stored_bytes"], st["stored_bytes"] + rec
                    in_ev = st["ev0"] <= nd["pos"] < st["ev1"]
                    extra = {"recalled_blocks": chosen, "needle_evicted": in_ev, "sketch_bytes": st["sketch_bytes"],
                             "needle_block_hit": bool(in_ev and (nd["pos"] - st["ev0"]) // BLOCK in chosen)}
                else:
                    text, kb = E.answer(store, T, q_ids), store.stored_bytes()
                    ab = kb
                rows.append({"sample": si, "q": qi, "T": T, "depth_tok": nd["depth_tok"], "pos": nd["pos"],
                             "value": nd["value"], "method": m, "frac": f, "B": B, "stored_bytes": kb,
                             "answer_time_bytes": ab, "full_bytes": full_bytes,
                             "correct": nd["value"] in text.replace(",", ""), "answer": text.strip()[:48],
                             "answer_s": round(time.time() - ta, 3), "build_s": round(build_s, 3),
                             "prefill_s": round(prefill_s, 2), **extra})
            del store, st
        print(f"  done sample {si + 1} elapsed={time.time() - t0:.0f}s", flush=True)
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by[(r["method"], r["frac"])][r["sample"]].append(r)
    table = []
    for (m, f), ctxs in sorted(by.items()):
        rs = [r for v in ctxs.values() for r in v]
        k = sum(r["correct"] for r in rs)
        ev = sum(bool(r.get("needle_evicted")) for r in rs)
        table.append({"method": m, "frac": f, "n_q": len(rs), "n_ctx": len(ctxs), "acc": round(k / len(rs), 4),
                      "ci95_ctx_boot": boot_ci([(sum(r["correct"] for r in v), len(v)) for v in ctxs.values()]),
                      "stored_MiB": round(sum(r["stored_bytes"] for r in rs) / len(rs) / 2**20, 3),
                      "answer_time_MiB": round(sum(r["answer_time_bytes"] for r in rs) / len(rs) / 2**20, 3),
                      "full_MiB": round(sum(r["full_bytes"] for r in rs) / len(rs) / 2**20, 3),
                      "compression_x": round(sum(r["full_bytes"] for r in rs) / sum(r["stored_bytes"] for r in rs), 2),
                      "s_per_answer": round(sum(r["answer_s"] for r in rs) / len(rs), 3), "oracle": m == "snapkv_qa",
                      "needle_block_hit": (round(sum(bool(r.get("needle_block_hit")) for r in rs) / max(1, ev), 4)
                                           if m in ("rod", "rodlex") else None),
                      "n_needle_evicted": ev if m in ("rod", "rodlex") else None})
    deltas = []
    for f in fracs:
        for A, Bm in (("rod", "streaming"), ("rod", "snapkv"), ("rod", "h2o"), ("rod", "knorm"), ("rod", "rodlex"),
                      ("rod", "kvp_streaming"), ("rod", "kvp_snapkv"), ("rod", "kvp_observed"), ("rod", "kvp_knorm"),
                      ("rod", "kvp_expected"), ("rodlex", "streaming"), ("snapkv", "streaming"), ("h2o", "streaming")):
            if (A, f) in by and (Bm, f) in by:
                d = [sum(r["correct"] for r in by[(A, f)][s]) / len(by[(A, f)][s]) -
                     sum(r["correct"] for r in by[(Bm, f)][s]) / len(by[(Bm, f)][s]) for s in by[(A, f)] if s in by[(Bm, f)]]
                deltas.append({"frac": f, "a": A, "b": Bm, "delta_acc": round(sum(d) / len(d), 4),
                               "ci95_ctx_boot": boot_delta(d), "n_ctx": len(d)})
    cpu = next((l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")), platform.processor()) \
        if os.path.exists("/proc/cpuinfo") else platform.processor()
    meta = {"name": name, "backend": "torch-cpu", "model": f"{MODEL_ID} (dequantised, fp32 compute)", "model_snapshot": snap,
            "kv_dtype": str(KV_DTYPE), "kv_bytes_per_token": per_tok, "ctx_target": a.ctx, "n_contexts": a.n,
            "needles": a.needles, "seed": a.seed, "style": a.style, "fracs": fracs, "methods": methods,
            "rod_layer": a.rod_layer, "rod_bits": a.rod_bits, "rod_scorer": a.rod_scorer, "rod_qsel": a.rod_qsel,
            "lex_qsel": a.lex_qsel, "kvp_fracs": a.kvp_fracs, "halo": a.halo, "block": BLOCK, "chat_date": DATE,
            "torch": torch.__version__, "threads": a.threads, "cpu": cpu, "machine": platform.platform(),
            "peak_rss_GiB": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20, 2),
            "wall_s": round(time.time() - t0, 1),
            "command": f"python eval/kvbench_torch.py --ctx {a.ctx} --n {a.n} --needles {a.needles} --seed {a.seed} "
                       f"--fracs {a.fracs} --methods {a.methods} --style {a.style} --rod_layer {a.rod_layer} "
                       f"--rod_bits {a.rod_bits} --rod_scorer {a.rod_scorer} --rod_qsel {a.rod_qsel} --lex_qsel {a.lex_qsel} "
                       f"--kvp_fracs {a.kvp_fracs} --halo {a.halo} --threads {a.threads} --name {name}"}
    (outdir / f"{name}.json").write_text(json.dumps({"meta": meta, "table": table, "paired_deltas": deltas}, indent=1))
    with open(outdir / f"{name}.rows.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    lines = ["| method | keep frac | n_q (ctx) | recall | 95% CI (ctx bootstrap) | stored MiB | answer-time MiB | compression | s/answer (CPU) | needle-block hit |",
             "|" + "---|" * 10]
    for t in table:
        lines.append(f"| {t['method']}{' (oracle)' if t['oracle'] else ''} | {t['frac']} | {t['n_q']} ({t['n_ctx']}) | {t['acc']:.3f} | "
                     f"{t['ci95_ctx_boot'][0]:.2f}–{t['ci95_ctx_boot'][1]:.2f} | {t['stored_MiB']} | {t['answer_time_MiB']} | "
                     f"{t['compression_x']}× | {t['s_per_answer']} | {'' if t['needle_block_hit'] is None else t['needle_block_hit']} |")
    lines += ["", "| keep frac | A − B | Δ recall | 95% CI (paired ctx bootstrap) | contexts |", "|---|---|---|---|---|"]
    lines += [f"| {d['frac']} | {d['a']} − {d['b']} | {d['delta_acc']:+.3f} | {d['ci95_ctx_boot'][0]:+.2f} … {d['ci95_ctx_boot'][1]:+.2f} | {d['n_ctx']} |"
              for d in deltas]
    (outdir / f"{name}.md").write_text(f"# {name}\n\n`{meta['command']}`\n\n{meta['backend']} · {cpu} · torch {torch.__version__} · "
                                       f"wall {meta['wall_s']} s\n\n" + "\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
