"""kvbench v2 — walking skeleton + eval harness for KV-cache compression (MLX; Apple GPU or Linux/macOS CPU).

Protocol (shared-context *multi-query*, query-agnostic): one long context (WikiText-103 text + 4 synthetic needles,
RULER-style) is prefilled once. Each method builds a *store* from that prefill BEFORE any question is seen. The
same 4 questions are then answered from the store alone (paired across methods). This is multi-query over one
compressed context, not a true multi-turn dialogue (that is a planned stretch).

Methods (names are honest about what is implemented):
  full                      uncompressed fp16/bf16 KV
  int8 / int4 / int2        per-token group-64 uniform (affine) quantisation of K and V, stored packed
                            (NOT KIVI's per-channel key scheme); dequantised one layer at a time for attention
  streaming                 StreamingLLM-style: 4 sinks + most recent tokens
  random                    sinks + recent 64 + uniformly random others (control)
  h2o                       H2O-style: attention mass accumulated over all prefill queries + recent half-budget
  snapkv                    SnapKV-style: last 64 context queries as observation window, avg-pool 5, + sinks/recent
  knorm                     lowest key L2 norm + sinks/recent
  snapkv_qa                 ORACLE reference: sees the question (computed with the full cache) before selecting
  rod                       spike — Recall-on-Demand: resident StreamingLLM KV + packed 2-bit key sketch of one layer
                            + int32 token ids; per question, the question's own queries pick evicted 64-token
                            blocks to re-prefill (sinks + optional halo as context, original positions)
  rodlex                    control — same store without the sketch; blocks chosen by IDF-weighted token overlap
For rod/rodlex the KV budget is reduced by ceil((sketch + id bytes) / bytes_per_token) so answer-time bytes never
exceed the baselines' at the same keep fraction.

Reproduce: .venv/bin/python eval/kvbench.py --ctx 4096 --n 12 --seed 0 --name ctx4k_s0 [--device cpu]
"""
from __future__ import annotations

import argparse
import json
import math
import platform
import random
import time
from collections import Counter, defaultdict
from pathlib import Path

import mlx.core as mx
from mlx_lm import load
from mlx_lm.utils import dequantize_model

ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "mlx-community/Llama-3.2-1B-Instruct-4bit"
N_SINK, N_RECENT, WIN = 4, 64, 64
KV_DTYPE = mx.float16  # the 4-bit model computes in fp16; KV stored as fp16 whatever the compute dtype
ADJ = ("amber azure bold brisk calm coral crimson dusty eager fuzzy gentle golden hollow icy jade keen "
       "lunar misty noble olive proud quiet rapid rusty silent silver solar tidal urban velvet vivid wild").split()
NOUN = ("otter falcon maple harbor lantern meadow comet canyon willow beacon cobra glacier heron island "
        "jaguar kettle lotus marble nebula orchid pepper quartz raven saddle tiger tulip violin walrus").split()
STYLES = {
    "literal": ("The special magic number for {k} is {v}.",
                "What is the special magic number for {k} mentioned in the text above? Answer with the number only."),
    "paraphrase": ("Note for the record: {k} was issued the access code {v}.",
                   "Which seven-digit code was issued to {k}? Reply with the digits only."),
}


# ---------------- storage ----------------
class Packed:
    """Group-quantised tensor kept packed; .dense() materialises a transient copy."""

    def __init__(self, x, bits, group=64):
        self.shape, self.dtype, self.bits, self.group = x.shape, x.dtype, bits, group
        self.q = mx.quantize(x.reshape(-1, x.shape[-1]), group_size=group, bits=bits)
        mx.eval(self.q)

    @property
    def nbytes(self):
        return sum(a.nbytes for a in self.q)

    def dense(self):
        return mx.dequantize(*self.q, group_size=self.group, bits=self.bits).reshape(self.shape).astype(self.dtype)


def dense(x):
    return x.dense() if isinstance(x, Packed) else x


class Cache:
    """Per-layer stored past (array or Packed) + dense tail of tokens appended while answering."""

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
        if len(ks) == 1:
            return ks[0], vs[0]
        return mx.concatenate(ks, axis=2), mx.concatenate(vs, axis=2)

    def append(self, li, k, v):
        self.tk[li] = k if self.tk[li] is None else mx.concatenate([self.tk[li], k], axis=2)
        self.tv[li] = v if self.tv[li] is None else mx.concatenate([self.tv[li], v], axis=2)

    def stored_bytes(self):
        return sum(x.nbytes for x in self.K + self.V if x is not None)


# ---------------- workload ----------------
def make_sample(tok, paras, ctx_tokens, n_needles, rng, style="literal"):
    tn, tq = STYLES[style]
    keys, needles = set(), []
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
    pres, out = None, []
    for nd in needles:
        full = tok.apply_chat_template([{"role": "user", "content": text + "\n\n@@SPLIT@@" + tq.format(k=nd["key"])}],
                                       tokenize=False, add_generation_prompt=True)
        pre, post = full.split("@@SPLIT@@")
        pres = pre
        out.append((tok.encode(post, add_special_tokens=False), nd))
    ctx_ids = tok.encode(pres, add_special_tokens=False)
    for _, nd in out:
        pat = tok.encode(nd["value"], add_special_tokens=False)
        nd["pos"] = next((p for p in range(len(ctx_ids) - len(pat) + 1) if ctx_ids[p:p + len(pat)] == pat), -1)
        nd["depth_tok"] = round(nd["pos"] / len(ctx_ids), 3)
    return ctx_ids, out


# ---------------- engine: explicit-cache Llama forward over frozen mlx-lm weights ----------------
class Engine:
    def __init__(self, model, tok):
        self.model, self.tok, self.inner = model, tok, model.model
        a = self.inner.layers[0].self_attn
        self.nh, self.nkv, self.hd, self.scale = a.n_heads, a.n_kv_heads, a.head_dim, a.scale
        self.nl = len(self.inner.layers)
        self.eos = set(getattr(tok, "eos_token_ids", None) or [tok.eos_token_id])

    def logits(self, h):
        if getattr(self.model.args, "tie_word_embeddings", False):
            return self.inner.embed_tokens.as_linear(h)
        return self.model.lm_head(h)

    def forward(self, ids, pos0, cache, capture=0, acc=None):
        L, g = len(ids), self.nh // self.nkv
        x = self.inner.embed_tokens(mx.array([ids]))
        caps = {}
        for li, layer in enumerate(self.inner.layers):
            at = layer.self_attn
            h = layer.input_layernorm(x)
            q = at.q_proj(h).reshape(1, L, self.nh, self.hd).transpose(0, 2, 1, 3)
            k = at.k_proj(h).reshape(1, L, self.nkv, self.hd).transpose(0, 2, 1, 3)
            v = at.v_proj(h).reshape(1, L, self.nkv, self.hd).transpose(0, 2, 1, 3)
            q, k = at.rope(q, offset=pos0), at.rope(k, offset=pos0)
            k, v = k.astype(KV_DTYPE), v.astype(KV_DTYPE)
            pk, pv = cache.kv(li)
            S0 = 0 if pk is None else pk.shape[2]
            kk = k if pk is None else mx.concatenate([pk, k], axis=2)
            vv = v if pv is None else mx.concatenate([pv, v], axis=2)
            cache.append(li, k, v)
            mask = (mx.arange(S0 + L)[None, :] <= (S0 + mx.arange(L))[:, None]) if L > 1 else None
            kk, vv = kk.astype(q.dtype), vv.astype(q.dtype)
            o = mx.fast.scaled_dot_product_attention(q, kk, vv, scale=self.scale, mask=mask)
            if capture:
                caps[li] = q[:, :, -capture:, :]
            if acc is not None:  # H2O statistic: attention mass each key receives
                s = ((q * self.scale).reshape(1, self.nkv, g, L, self.hd) @ kk[:, :, None].swapaxes(-1, -2)).astype(mx.float32)
                if mask is not None:
                    s = mx.where(mask, s, -mx.inf)
                p = mx.softmax(s, axis=-1).sum(axis=(2, 3))[0]
                if acc[li] is not None:
                    p = p + mx.pad(acc[li], [(0, 0), (0, p.shape[1] - acc[li].shape[1])])
                acc[li] = p
            x = x + at.o_proj(o.transpose(0, 2, 1, 3).reshape(1, L, -1))
            x = x + layer.mlp(layer.post_attention_layernorm(x))
        return self.inner.norm(x), caps

    def prefill(self, ids, chunk=256):
        c, acc, T, caps = Cache(nl=self.nl), [None] * self.nl, len(ids), None
        bounds = list(range(0, T - WIN, chunk)) + [T - WIN]
        for a, b in zip(bounds, bounds[1:] + [T]):
            _, cp = self.forward(ids[a:b], a, c, capture=WIN if b == T else 0, acc=acc)
            mx.eval([t for t in c.tk + c.tv + acc if t is not None])
            if b == T:
                caps = cp
        return c.tk, c.tv, acc, caps

    def answer(self, store, pos, q_ids, max_new=8):
        c = store.fork()
        h, _ = self.forward(q_ids, pos, c)
        out, p = [], pos + len(q_ids)
        t = mx.argmax(self.logits(h[:, -1, :]), axis=-1).item()
        for _ in range(max_new):
            if t in self.eos:
                break
            out.append(t)
            h, _ = self.forward([t], p, c)
            p += 1
            t = mx.argmax(self.logits(h[:, -1, :]), axis=-1).item()
        return self.tok.decode(out)


# ---------------- scorers / selectors ----------------
def avgpool(x, k=5):
    xp = mx.pad(x, [(0, 0), (k // 2, k // 2)])
    cs = mx.pad(mx.cumsum(xp, axis=1), [(0, 0), (1, 0)])
    return (cs[:, k:] - cs[:, :-k]) / k


def window_scores(qw, Kl, scale, causal):
    nkv, S, w = Kl.shape[1], Kl.shape[2], qw.shape[2]
    g = qw.shape[1] // nkv
    s = ((qw * scale).reshape(1, nkv, g, w, -1) @ Kl.astype(qw.dtype)[:, :, None].swapaxes(-1, -2)).astype(mx.float32)
    if causal:
        s = mx.where(mx.arange(S)[None, :] <= (S - w + mx.arange(w))[:, None], s, -mx.inf)
    return avgpool(mx.softmax(s, axis=-1).sum(axis=(2, 3))[0])


def topk_idx(score, B, T, n_recent=N_RECENT):
    pos = mx.arange(T)
    force = (pos < N_SINK) | (pos >= T - n_recent)
    s = mx.where(force[None], mx.array(1e30, mx.float32), score.astype(mx.float32))
    return mx.sort(mx.argsort(-s, axis=1)[:, :B], axis=1)


def stream_idx(T, B, nkv):
    i = mx.concatenate([mx.arange(N_SINK), mx.arange(T - (B - N_SINK), T)])
    return mx.broadcast_to(i[None], (nkv, B))


def gather(X, idx):
    nkv, B = idx.shape
    return mx.take_along_axis(X[0], mx.broadcast_to(idx[:, :, None], (nkv, B, X.shape[-1])), axis=1)[None]


# ---------------- spike: Recall-on-Demand ----------------
def rod_build(E, Kf, Vf, ctx_ids, B, layer_s, bits, lexical):
    T, per_tok = len(ctx_ids), 2 * E.nl * E.nkv * E.hd * 2
    sk_per_tok = 0 if lexical else E.nkv * (E.hd * bits // 8 + 4)
    B_kv = max(N_SINK + 2, B - math.ceil((sk_per_tok * T + 4 * T) / per_tok))
    B_res = max(N_SINK + 1, B_kv // 2)
    idx = stream_idx(T, B_res, E.nkv)
    Kr, Vr = [gather(k, idx) for k in Kf], [gather(v, idx) for v in Vf]
    ev0, ev1 = N_SINK, T - (B_res - N_SINK)
    sketch = None if lexical else Packed(Kf[layer_s][:, :, ev0:ev1], bits)
    ids = mx.array(ctx_ids, dtype=mx.int32)
    mx.eval(Kr, Vr, ids)
    st = {"Kr": Kr, "Vr": Vr, "sketch": sketch, "ids": ids, "ev0": ev0, "ev1": ev1, "B_res": B_res,
          "B_rec": B_kv - B_res, "T": T, "lexical": lexical, "layer": layer_s}
    st["stored_bytes"] = sum(x.nbytes for x in Kr + Vr) + (sketch.nbytes if sketch else 0) + ids.nbytes
    return st


def rod_answer(E, st, q_ids, block=64, halo=0):
    T, ev0, ev1 = st["T"], st["ev0"], st["ev1"]
    En = ev1 - ev0
    nb, m = -(-En // block), max(0, st["B_rec"] // block)
    if m == 0 or En <= 0:
        order = []
    elif st["lexical"]:
        ids = st["ids"][ev0:ev1].tolist()
        blocks = [set(ids[i * block:(i + 1) * block]) for i in range(nb)]
        df = Counter(t for b in blocks for t in b)
        qset = set(q_ids)
        sc = [sum(math.log((nb + 1) / (df[t] + 1)) for t in qset if t in b) for b in blocks]
        order = sorted(range(nb), key=lambda i: -sc[i])[:m]
    else:
        _, caps = E.forward(q_ids, T, Cache(st["Kr"], st["Vr"]), capture=len(q_ids))
        qq, g = caps[st["layer"]], E.nh // E.nkv
        sk = st["sketch"].dense().astype(qq.dtype)
        rel = ((qq * E.scale).reshape(1, E.nkv, g, qq.shape[2], E.hd) @ sk[:, :, None].swapaxes(-1, -2)).astype(mx.float32)
        r = mx.softmax(rel, axis=-1).sum(axis=(0, 2, 3)).max(axis=0)
        rb = mx.pad(r, [(0, nb * block - En)]).reshape(nb, block).max(axis=1)
        order = mx.argsort(-rb)[:m].tolist()
    chosen = sorted(order)
    addK, addV = [[] for _ in range(E.nl)], [[] for _ in range(E.nl)]
    for b in chosen:
        s = ev0 + b * block
        e, hs = min(s + block, ev1), max(ev0, s - halo)
        c = Cache([k[:, :, :N_SINK] for k in st["Kr"]], [v[:, :, :N_SINK] for v in st["Vr"]])
        E.forward(st["ids"][hs:e].tolist(), hs, c)
        for l in range(E.nl):
            addK[l].append(c.tk[l][:, :, s - hs:])
            addV[l].append(c.tv[l][:, :, s - hs:])
    aug = Cache([mx.concatenate([st["Kr"][l]] + addK[l], axis=2) for l in range(E.nl)],
                [mx.concatenate([st["Vr"][l]] + addV[l], axis=2) for l in range(E.nl)])
    text = E.answer(aug, T, q_ids)
    rec = sum(x.nbytes for l in range(E.nl) for x in addK[l] + addV[l])
    return text, chosen, rec


# ---------------- statistics ----------------
def boot_ci(per_ctx, reps=2000, seed=0):
    """Context-clustered bootstrap CI of a mean; per_ctx: list of (sum, count) per context."""
    rng, n = random.Random(seed), len(per_ctx)
    st = []
    for _ in range(reps):
        smp = [per_ctx[rng.randrange(n)] for _ in range(n)]
        st.append(sum(s for s, _ in smp) / max(1, sum(c for _, c in smp)))
    st.sort()
    return (round(st[int(0.025 * reps)], 4), round(st[int(0.975 * reps) - 1], 4))


def boot_delta(diffs, reps=2000, seed=0):
    rng, n = random.Random(seed), len(diffs)
    st = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(reps))
    return (round(st[int(0.025 * reps)], 4), round(st[int(0.975 * reps) - 1], 4))


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
    ap.add_argument("--device", default="gpu", choices=["gpu", "cpu"])
    ap.add_argument("--weights", default="q4", choices=["q4", "bf16", "fp32"],
                    help="q4 = 4-bit weights as shipped; bf16/fp32 = the same weights dequantised (faster on CPU)")
    ap.add_argument("--name", default=None)
    a = ap.parse_args()
    if a.device == "cpu":
        mx.set_default_device(mx.cpu)
    name = a.name or f"ctx{a.ctx}_n{a.n}_s{a.seed}_{a.style}"
    outdir = ROOT / "eval" / "results"
    outdir.mkdir(parents=True, exist_ok=True)
    paras = (ROOT / ".data" / "haystack.txt").read_text(encoding="utf-8").split("\n")
    model, tok = load(MODEL_ID)
    if a.weights != "q4":
        model = dequantize_model(model)
        model.set_dtype(mx.float32 if a.weights == "fp32" else mx.bfloat16)
    E = Engine(model, tok)
    weights_bytes = mx.get_active_memory()
    rng = random.Random(a.seed)
    fracs = [float(f) for f in a.fracs.split(",")]
    methods = a.methods.split(",")
    configs = [(m, 1.0) for m in ("full", "int8", "int4", "int2") if m in methods]
    configs += [(m, f) for m in ("streaming", "random", "h2o", "snapkv", "knorm", "snapkv_qa", "rod", "rodlex")
                if m in methods for f in fracs]
    rows, t0 = [], time.time()
    for si in range(a.n):
        ctx_ids, qs = make_sample(tok, paras, a.ctx, a.needles, rng, a.style)
        T = len(ctx_ids)
        mx.reset_peak_memory()
        tp = time.time()
        Kf, Vf, acc, caps = E.prefill(ctx_ids)
        prefill_s, peak = time.time() - tp, mx.get_peak_memory()
        full_bytes = sum(x.nbytes for x in Kf + Vf)
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
                    key = mx.random.key(a.seed * 1000 + si)
                    idxs = [topk_idx(mx.random.uniform(shape=(E.nkv, T), key=mx.random.split(key, E.nl)[l]), B, T)
                            for l in range(E.nl)]
                elif m == "h2o":
                    idxs = [topk_idx(acc[l], B, T, n_recent=B // 2) for l in range(E.nl)]
                elif m == "snapkv":
                    idxs = [topk_idx(window_scores(caps[l], Kf[l], E.scale, True), B, T) for l in range(E.nl)]
                else:
                    idxs = [topk_idx(-mx.linalg.norm(Kf[l][0].astype(mx.float32), axis=-1), B, T) for l in range(E.nl)]
                store = Cache([gather(Kf[l], idxs[l]) for l in range(E.nl)], [gather(Vf[l], idxs[l]) for l in range(E.nl)])
                mx.eval(store.K, store.V)
            elif m in ("rod", "rodlex"):
                st = rod_build(E, Kf, Vf, ctx_ids, B, a.rod_layer, a.rod_bits, lexical=(m == "rodlex"))
            build_s = time.time() - tb
            for qi, (q_ids, nd) in enumerate(qs):
                ta, extra = time.time(), {}
                if m == "snapkv_qa":
                    _, qc = E.forward(q_ids, T, Cache(Kf, Vf), capture=len(q_ids))
                    idxs = [topk_idx(window_scores(qc[l], Kf[l], E.scale, False), B, T) for l in range(E.nl)]
                    sq = Cache([gather(Kf[l], idxs[l]) for l in range(E.nl)], [gather(Vf[l], idxs[l]) for l in range(E.nl)])
                    text, kb, ab = E.answer(sq, T, q_ids), sq.stored_bytes(), sq.stored_bytes()
                elif st is not None:
                    text, chosen, rec = rod_answer(E, st, q_ids, halo=a.halo)
                    kb, ab = st["stored_bytes"], st["stored_bytes"] + rec
                    in_ev = st["ev0"] <= nd["pos"] < st["ev1"]
                    extra = {"recalled_blocks": chosen, "needle_evicted": in_ev,
                             "needle_block_hit": (in_ev and (nd["pos"] - st["ev0"]) // 64 in chosen)}
                else:
                    text, kb = E.answer(store, T, q_ids), store.stored_bytes()
                    ab = kb
                rows.append({"sample": si, "q": qi, "T": T, "depth_tok": nd["depth_tok"], "value": nd["value"],
                             "method": m, "frac": f, "B": B, "stored_bytes": kb, "answer_time_bytes": ab,
                             "full_bytes": full_bytes, "correct": nd["value"] in text.replace(",", ""),
                             "answer": text.strip()[:40], "answer_s": round(time.time() - ta, 3),
                             "build_s": round(build_s, 3), "prefill_s": round(prefill_s, 2),
                             "prefill_peak_bytes": peak, **extra})
            del store, st
        print(f"  done sample {si + 1} elapsed={time.time() - t0:.0f}s", flush=True)
    # ---- summary ----
    by = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by[(r["method"], r["frac"])][r["sample"]].append(r)
    table = []
    for (m, f), ctxs in sorted(by.items()):
        rs = [r for v in ctxs.values() for r in v]
        k = sum(r["correct"] for r in rs)
        table.append({"method": m, "frac": f, "n_q": len(rs), "n_ctx": len(ctxs), "acc": round(k / len(rs), 4),
                      "ci95_ctx_boot": boot_ci([(sum(r["correct"] for r in v), len(v)) for v in ctxs.values()]),
                      "stored_MiB": round(sum(r["stored_bytes"] for r in rs) / len(rs) / 2**20, 3),
                      "answer_time_MiB": round(sum(r["answer_time_bytes"] for r in rs) / len(rs) / 2**20, 3),
                      "compression_x": round(sum(r["full_bytes"] for r in rs) / sum(r["stored_bytes"] for r in rs), 2),
                      "s_per_answer": round(sum(r["answer_s"] for r in rs) / len(rs), 3),
                      "oracle": m == "snapkv_qa",
                      "needle_block_hit": (round(sum(bool(r.get("needle_block_hit")) for r in rs) /
                                                 max(1, sum(bool(r.get("needle_evicted")) for r in rs)), 4)
                                           if m in ("rod", "rodlex") else None)})
    deltas = []
    for f in fracs:
        for A, Bm in (("rod", "streaming"), ("rod", "snapkv"), ("rod", "rodlex"), ("snapkv", "streaming"), ("rod", "h2o")):
            if (A, f) in by and (Bm, f) in by:
                d = [sum(r["correct"] for r in by[(A, f)][s]) / len(by[(A, f)][s]) -
                     sum(r["correct"] for r in by[(Bm, f)][s]) / len(by[(Bm, f)][s]) for s in by[(A, f)] if s in by[(Bm, f)]]
                deltas.append({"frac": f, "a": A, "b": Bm, "delta_acc": round(sum(d) / len(d), 4), "ci95_ctx_boot": boot_delta(d)})
    meta = {"name": name, "model": MODEL_ID, "kv_bytes_per_token": 2 * E.nl * E.nkv * E.hd * 2, "ctx_target": a.ctx,
            "n_contexts": a.n, "needles": a.needles, "seed": a.seed, "style": a.style, "fracs": fracs,
            "rod_layer": a.rod_layer, "rod_bits": a.rod_bits, "halo": a.halo, "device": a.device, "weights": a.weights, "kv_dtype": str(KV_DTYPE),
            "weights_active_bytes": weights_bytes, "mlx": mx.__version__, "machine": platform.platform(),
            "wall_s": round(time.time() - t0, 1),
            "command": f"python eval/kvbench.py --ctx {a.ctx} --n {a.n} --needles {a.needles} --seed {a.seed} --fracs {a.fracs} "
                       f"--methods {a.methods} --style {a.style} --rod_layer {a.rod_layer} --rod_bits {a.rod_bits} "
                       f"--halo {a.halo} --device {a.device} --weights {a.weights} --name {name}"}
    (outdir / f"{name}.json").write_text(json.dumps({"meta": meta, "table": table, "paired_deltas": deltas}, indent=1))
    with open(outdir / f"{name}.rows.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    lines = ["| method | keep frac | n_q (ctx) | recall | 95% CI (ctx bootstrap) | stored MiB | answer-time MiB | compression | s/answer | needle-block hit |",
             "|" + "---|" * 10]
    for t in table:
        lines.append(f"| {t['method']}{' (oracle)' if t['oracle'] else ''} | {t['frac']} | {t['n_q']} ({t['n_ctx']}) | {t['acc']:.3f} | "
                     f"{t['ci95_ctx_boot'][0]:.2f}–{t['ci95_ctx_boot'][1]:.2f} | {t['stored_MiB']} | {t['answer_time_MiB']} | "
                     f"{t['compression_x']}× | {t['s_per_answer']} | {'' if t['needle_block_hit'] is None else t['needle_block_hit']} |")
    lines += ["", "| keep frac | A − B | Δ recall | 95% CI (paired ctx bootstrap) |", "|---|---|---|---|"]
    lines += [f"| {d['frac']} | {d['a']} − {d['b']} | {d['delta_acc']:+.3f} | {d['ci95_ctx_boot'][0]:+.2f} … {d['ci95_ctx_boot'][1]:+.2f} |"
              for d in deltas]
    (outdir / f"{name}.md").write_text(f"# {name}\n\n`{meta['command']}`\n\nmachine: {meta['machine']} · wall {meta['wall_s']} s\n\n"
                                       + "\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
