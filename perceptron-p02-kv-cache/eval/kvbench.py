"""kvbench — walking skeleton + eval harness for KV-cache compression on Apple silicon (MLX).

One long context (WikiText-103 text with 4 synthetic "magic number" needles, RULER-style) is prefilled
once with the full cache. Each method then compresses that cache *before* any question is seen
(query-agnostic protocol, = chat history), and the same 4 questions are asked of every method (paired).
`snapkv_qa` is the query-aware upper reference (it sees the question before compressing).

Methods: full | quant{8,4,2} (KIVI-style per-token group quantisation, group 64, emulated: stored packed,
dequantised for attention) | streaming (StreamingLLM: 4 sinks + recent) | h2o (accumulated attention,
half recent) | snapkv (observation window = last 64 context tokens, avg-pool 5) | knorm (lowest key L2
norm) | snapkv_qa | rod (spike: StreamingLLM resident half-budget + recall-on-demand: 2-bit key sketch of
one layer + token ids; on a question, re-prefill the top evicted 64-token blocks).

Memory = bytes the method keeps for the context: KV tensors + quantisation scales/biases + sketches +
token ids. Positions are never re-indexed (RoPE already applied), so no index bytes are needed.

Reproduce: .venv/bin/python eval/kvbench.py --ctx 4096 --n 12 --seed 0 --name ctx4k_s0
"""
from __future__ import annotations

import argparse
import json
import math
import platform
import random
import time
from pathlib import Path

import mlx.core as mx
from mlx_lm import load

ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "mlx-community/Llama-3.2-1B-Instruct-4bit"
N_SINK, N_RECENT, WIN = 4, 64, 64
ADJ = ("amber azure bold brisk calm coral crimson dusty eager fuzzy gentle golden hollow icy jade keen "
       "lunar misty noble olive proud quiet rapid rusty silent silver solar tidal urban velvet vivid wild").split()
NOUN = ("otter falcon maple harbor lantern meadow comet canyon willow beacon cobra glacier heron island "
        "jaguar kettle lotus marble nebula orchid pepper quartz raven saddle tiger tulip violin walrus").split()


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p, d = k / n, 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 4), round(c + h, 4))


# ---------------- workload: needles in a WikiText haystack ----------------
def make_sample(tok, paras, ctx_tokens, n_needles, rng):
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
        nd["depth"] = round(0.05 + 0.9 * (j + rng.random()) / n_needles, 3)
    for nd in sorted(needles, key=lambda x: -x["depth"]):
        body.insert(round(nd["depth"] * len(body)), f"The special magic number for {nd['key']} is {nd['value']}.")
    text = ("Below is a long text. Hidden in it are several special magic numbers. Read carefully; "
            "you will be asked about them later.\n\n" + "\n".join(body))
    out = []
    for nd in needles:
        q = f"What is the special magic number for {nd['key']} mentioned in the text above? Answer with the number only."
        full = tok.apply_chat_template([{"role": "user", "content": text + "\n\n@@SPLIT@@" + q}],
                                       tokenize=False, add_generation_prompt=True)
        pre, post = full.split("@@SPLIT@@")
        out.append((pre, post, nd))
    ctx_ids = tok.encode(out[0][0], add_special_tokens=False)
    return ctx_ids, [(tok.encode(post, add_special_tokens=False), nd) for _, post, nd in out]


# ---------------- engine: explicit-cache Llama forward over mlx-lm weights ----------------
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

    def forward(self, ids, pos0, K, V, capture=0, acc=None):
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
            S0 = 0 if K[li] is None else K[li].shape[2]
            if S0:
                k, v = mx.concatenate([K[li], k], axis=2), mx.concatenate([V[li], v], axis=2)
            K[li], V[li] = k, v
            mask = (mx.arange(S0 + L)[None, :] <= (S0 + mx.arange(L))[:, None]) if L > 1 else None
            o = mx.fast.scaled_dot_product_attention(q, k, v, scale=self.scale, mask=mask)
            if capture:
                caps[li] = q[:, :, -capture:, :]
            if acc is not None:  # H2O statistic: attention mass each key receives
                s = ((q * self.scale).reshape(1, self.nkv, g, L, self.hd) @ k[:, :, None].swapaxes(-1, -2)).astype(mx.float32)
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
        K, V, acc = [None] * self.nl, [None] * self.nl, [None] * self.nl
        T, caps = len(ids), None
        bounds = list(range(0, T - WIN, chunk)) + [T - WIN]
        for a, b in zip(bounds, bounds[1:] + [T]):
            _, c = self.forward(ids[a:b], a, K, V, capture=WIN if b == T else 0, acc=acc)
            mx.eval([t for t in K + V + acc if t is not None])
            if b == T:
                caps = c
        return K, V, acc, caps

    def answer(self, Kc, Vc, pos, q_ids, max_new=8):
        K, V = list(Kc), list(Vc)
        h, _ = self.forward(q_ids, pos, K, V)
        out, p = [], pos + len(q_ids)
        t = mx.argmax(self.logits(h[:, -1, :]), axis=-1).item()
        for _ in range(max_new):
            if t in self.eos:
                break
            out.append(t)
            h, _ = self.forward([t], p, K, V)
            p += 1
            t = mx.argmax(self.logits(h[:, -1, :]), axis=-1).item()
        return self.tok.decode(out)


# ---------------- scorers / selectors / store ----------------
def avgpool(x, k=5):
    xp = mx.pad(x, [(0, 0), (k // 2, k // 2)])
    cs = mx.pad(mx.cumsum(xp, axis=1), [(0, 0), (1, 0)])
    return (cs[:, k:] - cs[:, :-k]) / k


def window_scores(qw, Kl, scale, causal):
    nkv, S, w = Kl.shape[1], Kl.shape[2], qw.shape[2]
    g = qw.shape[1] // nkv
    s = ((qw * scale).reshape(1, nkv, g, w, -1) @ Kl[:, :, None].swapaxes(-1, -2)).astype(mx.float32)
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


def qdq(X, bits, group=64):
    wq, sc, bi = mx.quantize(X.reshape(-1, X.shape[-1]), group_size=group, bits=bits)
    Y = mx.dequantize(wq, sc, bi, group_size=group, bits=bits).reshape(X.shape).astype(X.dtype)
    return Y, wq.nbytes + sc.nbytes + bi.nbytes


def nbytes(Ks, Vs):
    return sum(k.nbytes + v.nbytes for k, v in zip(Ks, Vs))


# ---------------- spike: recall-on-demand over a StreamingLLM resident cache ----------------
def rod_answer(E, K, V, T, ctx_ids, q_ids, B, layer_s, block=64, sketch_bits=2):
    B_res = max(N_SINK + 1, B // 2)
    idx = stream_idx(T, B_res, E.nkv)
    Kr, Vr = [gather(k, idx) for k in K], [gather(v, idx) for v in V]
    ev0, ev1 = N_SINK, T - (B_res - N_SINK)
    sk, sk_bytes = qdq(K[layer_s][:, :, ev0:ev1], sketch_bits)
    _, caps = E.forward(q_ids, T, list(Kr), list(Vr), capture=len(q_ids))
    qq, g = caps[layer_s], E.nh // E.nkv
    rel = ((qq * E.scale).reshape(1, E.nkv, g, qq.shape[2], E.hd) @ sk[:, :, None].swapaxes(-1, -2)).astype(mx.float32)
    r = mx.softmax(rel, axis=-1).sum(axis=(0, 2, 3)).max(axis=0)
    E_n = ev1 - ev0
    nb = -(-E_n // block)
    rb = mx.pad(r, [(0, nb * block - E_n)]).reshape(nb, block).max(axis=1)
    m = max(0, (B - B_res) // block)
    chosen = sorted(mx.argsort(-rb)[:m].tolist())
    blocks = []
    for b in chosen:
        s, e = ev0 + b * block, min(ev0 + (b + 1) * block, ev1)
        Ks, Vs = [k[:, :, :N_SINK] for k in Kr], [v[:, :, :N_SINK] for v in Vr]
        E.forward(ctx_ids[s:e], s, Ks, Vs)
        blocks.append(([k[:, :, N_SINK:] for k in Ks], [v[:, :, N_SINK:] for v in Vs]))
    Ka = [mx.concatenate([Kr[l]] + [bk[0][l] for bk in blocks], axis=2) for l in range(E.nl)]
    Va = [mx.concatenate([Vr[l]] + [bk[1][l] for bk in blocks], axis=2) for l in range(E.nl)]
    text = E.answer(Ka, Va, T, q_ids)
    resident = nbytes(Kr, Vr)
    return text, {"resident_bytes": resident + sk_bytes + 4 * T, "answer_time_bytes": nbytes(Ka, Va) + sk_bytes + 4 * T,
                  "sketch_bytes": sk_bytes, "id_bytes": 4 * T, "recalled_blocks": chosen}


# ---------------- driver ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ctx", type=int, default=4096)
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--needles", type=int, default=4)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--fracs", default="0.1,0.25,0.5")
    ap.add_argument("--methods", default="full,quant8,quant4,quant2,streaming,h2o,snapkv,knorm,snapkv_qa,rod")
    ap.add_argument("--rod_layer", type=int, default=8)
    ap.add_argument("--name", default=None)
    a = ap.parse_args()
    name = a.name or f"ctx{a.ctx}_n{a.n}_s{a.seed}"
    outdir = ROOT / "eval" / "results"
    outdir.mkdir(parents=True, exist_ok=True)
    paras = (ROOT / ".data" / "haystack.txt").read_text(encoding="utf-8").split("\n")
    model, tok = load(MODEL_ID)
    E = Engine(model, tok)
    weights_bytes = mx.get_active_memory()
    rng = random.Random(a.seed)
    fracs = [float(f) for f in a.fracs.split(",")]
    methods = a.methods.split(",")
    rows, t0 = [], time.time()
    per_tok = 2 * E.nl * E.nkv * E.hd * 2
    for si in range(a.n):
        ctx_ids, qs = make_sample(tok, paras, a.ctx, a.needles, rng)
        T = len(ctx_ids)
        mx.reset_peak_memory()
        tp = time.time()
        K, V, acc, caps = E.prefill(ctx_ids)
        prefill_s, peak = time.time() - tp, mx.get_peak_memory()
        full_bytes = nbytes(K, V)
        caches = {}
        for m in methods:
            if m == "full":
                caches[(m, 1.0)] = (K, V, full_bytes)
            elif m.startswith("quant"):
                bits = int(m[5:])
                kq = [qdq(k, bits) for k in K]
                vq = [qdq(v, bits) for v in V]
                caches[(m, 1.0)] = ([x[0] for x in kq], [x[0] for x in vq], sum(x[1] for x in kq + vq))
            elif m in ("streaming", "h2o", "snapkv", "knorm"):
                for f in fracs:
                    B = max(N_SINK + N_RECENT + 1, round(f * T))
                    if m == "streaming":
                        idxs = [stream_idx(T, B, E.nkv)] * E.nl
                    elif m == "h2o":
                        idxs = [topk_idx(acc[l], B, T, n_recent=B // 2) for l in range(E.nl)]
                    elif m == "snapkv":
                        idxs = [topk_idx(window_scores(caps[l], K[l], E.scale, True), B, T) for l in range(E.nl)]
                    else:
                        idxs = [topk_idx(-mx.linalg.norm(K[l][0].astype(mx.float32), axis=-1), B, T) for l in range(E.nl)]
                    Kc = [gather(K[l], idxs[l]) for l in range(E.nl)]
                    Vc = [gather(V[l], idxs[l]) for l in range(E.nl)]
                    mx.eval(Kc, Vc)
                    caches[(m, f)] = (Kc, Vc, nbytes(Kc, Vc))
        for qi, (q_ids, nd) in enumerate(qs):
            base = {"sample": si, "q": qi, "T": T, "depth": nd["depth"], "value": nd["value"],
                    "full_bytes": full_bytes, "prefill_s": round(prefill_s, 2), "prefill_peak_bytes": peak}
            jobs = [(m, f) for (m, f) in caches] + [(m, f) for m in ("snapkv_qa", "rod") if m in methods for f in fracs]
            for m, f in jobs:
                ta = time.time()
                extra = {}
                if (m, f) in caches:
                    Kc, Vc, kb = caches[(m, f)]
                    text = E.answer(Kc, Vc, T, q_ids)
                elif m == "snapkv_qa":
                    B = max(N_SINK + N_RECENT + 1, round(f * T))
                    _, qc = E.forward(q_ids, T, list(K), list(V), capture=len(q_ids))
                    idxs = [topk_idx(window_scores(qc[l], K[l], E.scale, False), B, T) for l in range(E.nl)]
                    Kc = [gather(K[l], idxs[l]) for l in range(E.nl)]
                    Vc = [gather(V[l], idxs[l]) for l in range(E.nl)]
                    kb = nbytes(Kc, Vc)
                    text = E.answer(Kc, Vc, T, q_ids)
                else:
                    B = max(N_SINK + N_RECENT + 1, round(f * T))
                    text, extra = rod_answer(E, K, V, T, ctx_ids, q_ids, B, a.rod_layer)
                    kb = extra.pop("resident_bytes")
                ok = nd["value"] in text.replace(",", "")
                rows.append({**base, "method": m, "frac": f, "kept_bytes": kb, "correct": ok,
                             "answer": text.strip()[:40], "answer_s": round(time.time() - ta, 3), **extra})
        print(f"sample {si + 1}/{a.n} T={T} prefill={prefill_s:.1f}s elapsed={time.time() - t0:.0f}s", flush=True)
    summ = {}
    for r in rows:
        s = summ.setdefault((r["method"], r["frac"]), {"k": 0, "n": 0, "bytes": 0.0, "full": 0.0, "lat": 0.0, "abytes": 0.0})
        s["k"] += r["correct"]; s["n"] += 1; s["bytes"] += r["kept_bytes"]; s["full"] += r["full_bytes"]
        s["lat"] += r["answer_s"]; s["abytes"] += r.get("answer_time_bytes", r["kept_bytes"])
    table = []
    for (m, f), s in sorted(summ.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        table.append({"method": m, "frac": f, "n": s["n"], "acc": round(s["k"] / s["n"], 4), "ci95": wilson(s["k"], s["n"]),
                      "kept_MiB": round(s["bytes"] / s["n"] / 2**20, 3), "answer_time_MiB": round(s["abytes"] / s["n"] / 2**20, 3),
                      "compression_x": round(s["full"] / s["bytes"], 2), "answer_s": round(s["lat"] / s["n"], 3)})
    meta = {"name": name, "model": MODEL_ID, "kv_bytes_per_token_fp16": per_tok, "ctx_target": a.ctx, "n_contexts": a.n,
            "needles": a.needles, "seed": a.seed, "fracs": fracs, "rod_layer": a.rod_layer, "weights_active_bytes": weights_bytes,
            "mlx": mx.__version__, "machine": platform.platform(), "wall_s": round(time.time() - t0, 1),
            "command": f".venv/bin/python eval/kvbench.py --ctx {a.ctx} --n {a.n} --needles {a.needles} --seed {a.seed} "
                       f"--fracs {a.fracs} --methods {a.methods} --rod_layer {a.rod_layer} --name {name}"}
    (outdir / f"{name}.json").write_text(json.dumps({"meta": meta, "table": table}, indent=1))
    with open(outdir / f"{name}.rows.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    lines = ["| method | keep frac | n | recall acc | 95% CI | kept KV MiB | answer-time MiB | compression | s/answer |", "|" + "---|" * 9]
    for t in table:
        lines.append(f"| {t['method']} | {t['frac']} | {t['n']} | {t['acc']:.3f} | {t['ci95'][0]:.2f}–{t['ci95'][1]:.2f} | "
                     f"{t['kept_MiB']} | {t['answer_time_MiB']} | {t['compression_x']}× | {t['answer_s']} |")
    (outdir / f"{name}.md").write_text(f"# {name}\n\n`{meta['command']}`\n\n" + "\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
