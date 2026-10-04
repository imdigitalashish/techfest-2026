"""FROZEN evaluator for C7 Recall-on-Demand — the autoresearch loop must not edit this file.

Prints one scalar line `hit_at_m=<float>` (share of calibration questions whose needle block is among the
m blocks RoD would re-prefill), then secondary metrics as JSON.

Usage: .venv/bin/python components/recall_on_demand/autoresearch/eval.py [--layer 8 --bits 2 --block 64 --seeds 100-104]
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "eval"))
import mlx.core as mx  # noqa: E402
from mlx_lm import load  # noqa: E402

import kvbench as kb  # noqa: E402

CTX, NEEDLES, RES_FRAC, M_BLOCKS = 4096, 4, 0.05, 3


def needle_pos(tok, ctx_ids, value):
    pat = tok.encode(value, add_special_tokens=False)
    for i in range(len(ctx_ids) - len(pat) + 1):
        if ctx_ids[i:i + len(pat)] == pat:
            return i
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layer", type=int, default=8)
    ap.add_argument("--bits", type=int, default=2)
    ap.add_argument("--block", type=int, default=64)
    ap.add_argument("--seeds", default="100-104")
    a = ap.parse_args()
    s0, s1 = map(int, a.seeds.split("-"))
    paras = (ROOT / ".data" / "haystack.txt").read_text(encoding="utf-8").split("\n")
    model, tok = load(kb.MODEL_ID)
    E = kb.Engine(model, tok)
    hits, n, sk_b, t_q = 0, 0, 0, 0.0
    for seed in range(s0, s1 + 1):
        rng = random.Random(seed)
        ctx_ids, qs = kb.make_sample(tok, paras, CTX, NEEDLES, rng)
        T = len(ctx_ids)
        K, V, _, _ = E.prefill(ctx_ids)
        B_res = max(kb.N_SINK + 1, round(RES_FRAC * T))
        idx = kb.stream_idx(T, B_res, E.nkv)
        Kr, Vr = [kb.gather(k, idx) for k in K], [kb.gather(v, idx) for v in V]
        ev0, ev1 = kb.N_SINK, T - (B_res - kb.N_SINK)
        sk, sb = kb.qdq(K[a.layer][:, :, ev0:ev1], a.bits)
        sk_b += sb / max(1, ev1 - ev0)
        for q_ids, nd in qs:
            p = needle_pos(tok, ctx_ids, nd["value"])
            if p is None or not (ev0 <= p < ev1):
                continue  # needle resident or not found: not a recall question
            t = time.time()
            _, caps = E.forward(q_ids, T, list(Kr), list(Vr), capture=len(q_ids))
            qq, g = caps[a.layer], E.nh // E.nkv
            rel = ((qq * E.scale).reshape(1, E.nkv, g, qq.shape[2], E.hd) @ sk[:, :, None].swapaxes(-1, -2)).astype(mx.float32)
            r = mx.softmax(rel, axis=-1).sum(axis=(0, 2, 3)).max(axis=0)
            En = ev1 - ev0
            nb = -(-En // a.block)
            rb = mx.pad(r, [(0, nb * a.block - En)]).reshape(nb, a.block).max(axis=1)
            chosen = set(mx.argsort(-rb)[:M_BLOCKS].tolist())
            t_q += time.time() - t
            hits += int((p - ev0) // a.block in chosen)
            n += 1
    print(f"hit_at_m={hits / max(1, n):.4f}")
    print(json.dumps({"n_questions": n, "sketch_bytes_per_token": round(sk_b / (s1 - s0 + 1), 1),
                      "ms_per_question": round(1000 * t_q / max(1, n), 1), "layer": a.layer, "bits": a.bits,
                      "block": a.block, "seeds": a.seeds}))


if __name__ == "__main__":
    main()
