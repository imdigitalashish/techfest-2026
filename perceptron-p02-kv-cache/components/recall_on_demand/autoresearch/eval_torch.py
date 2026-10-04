"""FROZEN dev evaluator for C7 Recall-on-Demand (torch). The tuning loop never edits this file.

Dev split only: seeds 100-109, both needle styles. The pre-registered tests use seeds 0 and 1 and never enter tuning.
For each scorer variant it computes the isolated C7 metric, needle-block hit@m: the share of questions whose needle
lies in the evicted region and whose 64-token block is among the m blocks the scorer would re-prefill. m comes from
the RoD budget at keep fraction 0.10 (primary) and 0.25. No text generation is needed.

Variants: scorer {softmax_sum, max_logit, lift_mean, lift_max, softmax_lift} x question tokens {all, content}
x sketch bits {2, 4} x sketch layer {0..15}, plus the lexical control (IDF token overlap) with {all, content}.
lift* contrast the question's attention with the attention of the context's last 64 tokens (the prefill window),
which cancels keys every query attends to (sink-like and formatting tokens).

Usage (VM): python components/recall_on_demand/autoresearch/eval_torch.py --seeds 100-109 --ctx 4096
Prints `hit_at_m=<float>` for --variant (default: the C7 config in results.tsv) and writes the full table.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "eval"))
import kvbench_torch as kb  # noqa: E402

SCORERS = ("softmax_sum", "max_logit", "lift_mean", "lift_max", "softmax_lift")


def block_scores(qq, wq, sk, scale, scorer, nkv):
    """qq: [1,nh,Lq,hd] question queries; wq: [1,nh,W,hd] window queries; sk: [1,nkv,E,hd] -> [E] key scores."""
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


def top_blocks(s, m, block=kb.BLOCK):
    E = s.shape[0]
    nblk = -(-E // block)
    rb = torch.nn.functional.pad(s, (0, nblk * block - E), value=float("-inf")).view(nblk, block).max(1).values
    return set(torch.topk(rb, min(m, nblk)).indices.tolist())


def lexical_blocks(ids, qset, m, block=kb.BLOCK):
    nblk = -(-len(ids) // block)
    blocks = [set(ids[i * block:(i + 1) * block]) for i in range(nblk)]
    df = Counter(t for b in blocks for t in b)
    sc = [sum(math.log((nblk + 1) / (df[t] + 1)) for t in qset if t in b) for b in blocks]
    return set(sorted(range(nblk), key=lambda i: -sc[i])[:m])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="100-109")
    ap.add_argument("--ctx", type=int, default=4096)
    ap.add_argument("--styles", default="literal,paraphrase")
    ap.add_argument("--fracs", default="0.1,0.25")
    ap.add_argument("--variant", default="lift_mean/content/2/8")
    ap.add_argument("--out", default="dev_sweep")
    a = ap.parse_args()
    s0, s1 = map(int, a.seeds.split("-"))
    if s0 <= 1 <= s1 or s0 <= 0 <= s1:
        sys.exit("dev seeds must not include the test seeds 0-1")
    torch.set_num_threads(torch.get_num_threads())
    snap = kb.glob.glob(kb.os.path.expanduser("~/.cache/huggingface/hub/models--mlx-community--Llama-3.2-1B-Instruct-4bit/snapshots/*"))[0]
    tok = kb.AutoTokenizer.from_pretrained(snap)
    E = kb.Engine(kb.load_model(), tok)
    paras = (ROOT / ".data" / "haystack.txt").read_text(encoding="utf-8").split("\n")
    fracs = [float(f) for f in a.fracs.split(",")]
    hits = defaultdict(lambda: [0, 0])  # (variant, frac) -> [hits, n]
    per_tok = 2 * E.nl * E.nkv * E.hd * 2
    t0 = time.time()
    for style in a.styles.split(","):
        for seed in range(s0, s1 + 1):
            ctx_ids, qs = kb.make_sample(tok, paras, a.ctx, 4, random.Random(seed), style)
            T = len(ctx_ids)
            Kf, Vf, _, caps = E.prefill(ctx_ids)
            for f in fracs:
                sk_cache = {}
                B = round(f * T)
                B_kv = B - math.ceil((E.nkv * (E.hd * 2 // 8 + 4) * T + 4 * T) / per_tok)
                B_res = B_kv // 2
                m = (B_kv - B_res) // kb.BLOCK
                ev0, ev1 = kb.N_SINK, T - (B_res - kb.N_SINK)
                idx = kb.stream_idx(T, B_res, E.nkv)
                Kr, Vr = [kb.gather(k, idx) for k in Kf], [kb.gather(v, idx) for v in Vf]
                for q_ids, nd in qs:
                    if not (ev0 <= nd["pos"] < ev1):
                        continue
                    nblk = (nd["pos"] - ev0) // kb.BLOCK
                    _, qc = E.forward(q_ids, T, kb.Cache(Kr, Vr), capture=len(q_ids))
                    for qsel in ("all", "content"):
                        n_use = nd["n_q_content"] if qsel == "content" else len(q_ids)
                        lex = lexical_blocks(ctx_ids[ev0:ev1], set(q_ids[:n_use]), m)
                        h = hits[(f"lexical/{qsel}", f)]
                        h[0] += nblk in lex
                        h[1] += 1
                        for bits in (2, 4):
                            for layer in range(E.nl):
                                key = (bits, layer, ev0, ev1)
                                if key not in sk_cache:
                                    sk_cache[key] = kb.Packed(Kf[layer][:, :, ev0:ev1], bits).dense().float()
                                sk = sk_cache[key]
                                qq = qc[layer][:, :, :n_use].float()
                                for sc in SCORERS:
                                    chosen = top_blocks(block_scores(qq, caps[layer].float(), sk, E.scale, sc, E.nkv), m)
                                    h = hits[(f"{sc}/{qsel}/{bits}/{layer}", f)]
                                    h[0] += nblk in chosen
                                    h[1] += 1
            print(f"{style} seed {seed} T={T} elapsed {time.time() - t0:.0f}s", flush=True)
    rows = sorted(({"variant": v, "frac": f, "hit": round(k / max(1, n), 4), "n": n} for (v, f), (k, n) in hits.items()),
                  key=lambda r: (r["frac"], -r["hit"]))
    out = ROOT / "components" / "recall_on_demand" / "autoresearch" / f"{a.out}.json"
    out.write_text(json.dumps({"seeds": a.seeds, "ctx": a.ctx, "styles": a.styles, "rows": rows}, indent=0))
    for f in fracs:
        print(f"--- frac {f}: top 12")
        for r in [r for r in rows if r["frac"] == f][:12]:
            print(f"{r['variant']:28s} hit={r['hit']:.3f} n={r['n']}")
        lx = [r for r in rows if r["frac"] == f and r["variant"].startswith("lexical")]
        print("lexical:", [(r["variant"], r["hit"]) for r in lx])
    sel = [r for r in rows if r["variant"] == a.variant and r["frac"] == fracs[0]]
    print(f"hit_at_m={sel[0]['hit'] if sel else float('nan'):.4f}")


if __name__ == "__main__":
    main()
