"""Exploratory post-hoc analyses E1-E3 on T1's contexts (PREREG amendment 3). Run on the VM after the grid.

For T1's 12 seed-0 literal contexts, keep 0.10/0.25/0.50 and the frozen RoD config:
  E1  streamed scorer (streamed.py) vs the unchunked scorer: identical block choices? Plus determinism vs T1's rows.
  E2  exact-KV oracle: the scorer's blocks, but their exact KV gathered from the full prefill (needs a full backing store).
  E3  oracle-block selection: the needle's block forced plus the scorer's other picks, re-prefilled as RoD does.
  E23 both oracles: the needle's block with exact KV, an upper bound for this store design at that budget.
Writes eval/results/posthoc_T1.json and eval/results/posthoc_T1.rows.jsonl.
Usage (VM, ~/p02): HF_HUB_OFFLINE=1 ~/venv_kvp/bin/python components/recall_on_demand/posthoc_T1.py
"""
from __future__ import annotations

import json
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "eval"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kvbench_torch as kb  # noqa: E402
from streamed import softmax_lift_streamed, transient_bytes_streamed  # noqa: E402

CFG = {"layer": 5, "bits": 4, "scorer": "softmax_lift", "lexical": False, "qsel": "content"}


def choose(r, nblk, En, m):
    rb = F.pad(r, (0, nblk * kb.BLOCK - En), value=float("-inf")).view(nblk, kb.BLOCK).max(1).values
    return sorted(torch.topk(rb, min(m, nblk)).indices.tolist())


@torch.inference_mode()
def answer_with(E, st, q_ids, blocks, Kf=None, Vf=None):
    """Answer from resident KV + the given blocks: exact KV from Kf/Vf if given, else re-prefilled like rod_answer."""
    T, ev0, ev1 = st["T"], st["ev0"], st["ev1"]
    addK, addV = [[] for _ in range(E.nl)], [[] for _ in range(E.nl)]
    for b in sorted(blocks):
        s, e = ev0 + b * kb.BLOCK, min(ev0 + (b + 1) * kb.BLOCK, ev1)
        if Kf is not None:
            for l in range(E.nl):
                addK[l].append(Kf[l][:, :, s:e])
                addV[l].append(Vf[l][:, :, s:e])
        else:
            c = kb.Cache([k[:, :, :kb.N_SINK] for k in st["Kr"]], [v[:, :, :kb.N_SINK] for v in st["Vr"]])
            E.forward(st["ids"][s:e].tolist(), s, c)
            for l in range(E.nl):
                addK[l].append(c.tk[l])
                addV[l].append(c.tv[l])
    aug = kb.Cache([torch.cat([st["Kr"][l]] + addK[l], 2) for l in range(E.nl)],
                   [torch.cat([st["Vr"][l]] + addV[l], 2) for l in range(E.nl)])
    return E.answer(aug, T, q_ids)


def main():
    rec = {}
    p = ROOT / "eval" / "results" / "T1_literal_s0.rows.jsonl"
    if p.exists():
        for l in p.read_text().splitlines():
            r = json.loads(l)
            if r["method"] == "rod":
                rec[(r["sample"], r["q"], round(r["frac"], 4))] = r
    snap = kb.glob.glob(kb.os.path.expanduser("~/.cache/huggingface/hub/models--mlx-community--Llama-3.2-1B-Instruct-4bit/snapshots/*"))[0]
    tok = kb.AutoTokenizer.from_pretrained(snap)
    E = kb.Engine(kb.load_model(), tok)
    paras = (ROOT / ".data" / "haystack.txt").read_text(encoding="utf-8").split("\n")
    rng, rows, t0, worst = random.Random(0), [], time.time(), 0.0
    for si in range(12):
        ctx_ids, qs = kb.make_sample(tok, paras, 4096, 4, rng, "literal")
        T = len(ctx_ids)
        Kf, Vf, _, caps = E.prefill(ctx_ids)
        for f in (0.1, 0.25, 0.5):
            B = max(kb.N_SINK + kb.N_RECENT + 1, round(f * T))
            st = kb.rod_build(E, Kf, Vf, ctx_ids, B, CFG, caps)
            En = st["ev1"] - st["ev0"]
            nblk, m = -(-En // kb.BLOCK), max(0, st["B_rec"] // kb.BLOCK)
            for qi, (q_ids, nd) in enumerate(qs):
                ok = lambda txt: nd["value"] in txt.replace(",", "")
                _, cq = E.forward(q_ids, T, kb.Cache(st["Kr"], st["Vr"]), capture=len(q_ids))
                qq, wq = cq[CFG["layer"]][:, :, :nd["n_q_content"]].float(), st["wq"].float()
                ru = kb.block_scores(qq, wq, st["sketch"].dense().float(), E.scale, "softmax_lift", E.nkv)
                rs = softmax_lift_streamed(qq, wq, st["sketch"], E.scale, E.nkv)
                worst = max(worst, float((ru - rs).abs().max()))
                cu, cs = choose(ru, nblk, En, m) if m else [], choose(rs, nblk, En, m) if m else []
                evicted = st["ev0"] <= nd["pos"] < st["ev1"]
                nb = (nd["pos"] - st["ev0"]) // kb.BLOCK if evicted else None
                co = cu if nb is None or nb in cu or m == 0 else sorted([nb] + [b for b in cu if b != nb][:m - 1])
                row = {"sample": si, "q": qi, "frac": f, "T": T, "m": m, "needle_evicted": evicted, "needle_block": nb,
                       "chosen_unchunked": cu, "chosen_streamed": cs, "streamed_equal": cu == cs,
                       "e2_exactkv_correct": ok(answer_with(E, st, q_ids, cu, Kf, Vf)),
                       "e3_oracleblk_correct": ok(answer_with(E, st, q_ids, co)),
                       "e23_both_correct": ok(answer_with(E, st, q_ids, co, Kf, Vf))}
                r1 = rec.get((si, qi, round(f, 4)))
                if r1 is not None:
                    row["t1_recorded_equal"] = r1["recalled_blocks"] == cu
                    row["rod_correct_T1"] = r1["correct"]
                rows.append(row)
        print(f"context {si + 1}/12 T={T} elapsed {time.time() - t0:.0f}s", flush=True)
    summ = defaultdict(dict)
    for f in (0.1, 0.25, 0.5):
        rs_ = [r for r in rows if r["frac"] == f]
        n = len(rs_)
        summ[str(f)] = {"n": n, "m_mean": sum(r["m"] for r in rs_) / n,
                        "streamed_equal": sum(r["streamed_equal"] for r in rs_),
                        "t1_recorded_equal": sum(r.get("t1_recorded_equal", False) for r in rs_),
                        "rod_T1_acc": (sum(r["rod_correct_T1"] for r in rs_ if "rod_correct_T1" in r) / n) if rec else None,
                        "e2_exactkv_acc": sum(r["e2_exactkv_correct"] for r in rs_) / n,
                        "e3_oracleblk_acc": sum(r["e3_oracleblk_correct"] for r in rs_) / n,
                        "e23_both_acc": sum(r["e23_both_correct"] for r in rs_) / n}
    out = {"label": "EXPLORATORY (PREREG amendment 3); T1 contexts, frozen RoD config", "summary": summ,
           "max_abs_score_diff_streamed_vs_unchunked": worst,
           "transient_bytes_streamed_chunk256_upper_bound": transient_bytes_streamed(Lq=20),
           "command": "HF_HUB_OFFLINE=1 ~/venv_kvp/bin/python components/recall_on_demand/posthoc_T1.py",
           "wall_s": round(time.time() - t0, 1)}
    (ROOT / "eval" / "results" / "posthoc_T1.json").write_text(json.dumps(out, indent=1))
    with open(ROOT / "eval" / "results" / "posthoc_T1.rows.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
