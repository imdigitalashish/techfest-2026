"""E6 (exploratory, post hoc; PREREG amendment 5): generation-length sensitivity on T2's contexts.

T2's full cache often restates the question ("The seven-digit code issued to ...") and is cut off by the harness's
max_new=10 before the number. This re-answers T2's 12 contexts (seed 1, paraphrase) with max_new=32 for full,
StreamingLLM, the question-aware SnapKV oracle and RoD (frozen config). It scores (a) lenient = the value appears
anywhere (as registered) and (b) strict = the FIRST 7-digit number in the answer equals the value.
Writes eval/results/e6_maxnew32_T2.json (+ rows). Usage (VM, ~/p02):
HF_HUB_OFFLINE=1 ~/venv_kvp/bin/python components/recall_on_demand/posthoc_maxnew.py
"""
from __future__ import annotations

import functools
import json
import random
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "eval"))
import kvbench_torch as kb  # noqa: E402

CFG = {"layer": 5, "bits": 4, "scorer": "softmax_lift", "lexical": False, "qsel": "content"}
MAX_NEW = 32


def main():
    snap = kb.glob.glob(kb.os.path.expanduser("~/.cache/huggingface/hub/models--mlx-community--Llama-3.2-1B-Instruct-4bit/snapshots/*"))[0]
    tok = kb.AutoTokenizer.from_pretrained(snap)
    E = kb.Engine(kb.load_model(), tok)
    E.answer = functools.partial(kb.Engine.answer, E, max_new=MAX_NEW)  # rod_answer calls E.answer(aug, T, q_ids)
    paras = (ROOT / ".data" / "haystack.txt").read_text(encoding="utf-8").split("\n")
    rng, rows, t0 = random.Random(1), [], time.time()
    for si in range(12):
        ctx_ids, qs = kb.make_sample(tok, paras, 4096, 4, rng, "paraphrase")
        T = len(ctx_ids)
        Kf, Vf, _, caps = E.prefill(ctx_ids)
        for m, f in (("full", 1.0), ("streaming", 0.1), ("streaming", 0.25), ("snapkv_qa", 0.25), ("rod", 0.1), ("rod", 0.25)):
            B = max(kb.N_SINK + kb.N_RECENT + 1, round(f * T))
            st = kb.rod_build(E, Kf, Vf, ctx_ids, B, CFG, caps) if m == "rod" else None
            for qi, (q_ids, nd) in enumerate(qs):
                if m == "full":
                    text = E.answer(kb.Cache(Kf, Vf), T, q_ids)
                elif m == "streaming":
                    idx = kb.stream_idx(T, B, E.nkv)
                    text = E.answer(kb.Cache([kb.gather(k, idx) for k in Kf], [kb.gather(v, idx) for v in Vf]), T, q_ids)
                elif m == "snapkv_qa":
                    _, qc = E.forward(q_ids, T, kb.Cache(Kf, Vf), capture=len(q_ids))
                    idxs = [kb.topk_idx(kb.window_scores(qc[l], Kf[l], E.scale, False), B, T) for l in range(E.nl)]
                    text = E.answer(kb.Cache([kb.gather(Kf[l], idxs[l]) for l in range(E.nl)],
                                             [kb.gather(Vf[l], idxs[l]) for l in range(E.nl)]), T, q_ids)
                else:
                    text, _, _ = kb.rod_answer(E, st, q_ids, nd["n_q_content"])
                clean = text.replace(",", "")
                first = re.search(r"\d{7}", clean)
                rows.append({"sample": si, "q": qi, "method": m, "frac": f, "answer": text.strip()[:120],
                             "lenient": nd["value"] in clean, "strict": bool(first and first.group(0) == nd["value"])})
        print(f"context {si + 1}/12 T={T} elapsed {time.time() - t0:.0f}s", flush=True)
    summ = defaultdict(dict)
    for (m, f) in sorted({(r["method"], r["frac"]) for r in rows}):
        rs = [r for r in rows if r["method"] == m and r["frac"] == f]
        summ[f"{m}@{f}"] = {"n": len(rs), "lenient": sum(r["lenient"] for r in rs) / len(rs), "strict": sum(r["strict"] for r in rs) / len(rs)}
    out = {"label": "EXPLORATORY post hoc (PREREG amendment 5): T2 contexts, max_new=32", "summary": summ, "wall_s": round(time.time() - t0, 1),
           "command": "HF_HUB_OFFLINE=1 ~/venv_kvp/bin/python components/recall_on_demand/posthoc_maxnew.py"}
    (ROOT / "eval" / "results" / "e6_maxnew32_T2.json").write_text(json.dumps(out, indent=1))
    with open(ROOT / "eval" / "results" / "e6_maxnew32_T2.rows.jsonl", "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
