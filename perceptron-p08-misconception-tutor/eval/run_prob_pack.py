"""Part 4 `prob_pack` (pre-registered in eval/llm_gap_protocol.md, Addendum A): can an LLM produce the exact
answer key AND the targeted misconception's wrong answer for a probability / expected-value practice problem?
Our executable pack computes both exactly (components/bugs/probability.py), so it is correct by construction;
this part measures how often an LLM-only generator would ship a wrong key or a wrong distractor. SYNTHETIC items.

Run: AZURE_OPENAI_ENDPOINT=... nice -n 10 .venv/bin/python -m eval.run_prob_pack [--offline] [--dry] [--limit N]
Out: eval/results/llm_gaps_prob_pack.json, eval/results/llm_gaps_prob_pack_responses.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction

import numpy as np

from components.bugs.probability import CODES, DESCRIPTIONS, build, canon
from eval.run_llm_gaps import MODELS, PRICE_SOURCE, RES, ci, load_store, parse_json, query, r4, save_store, usage_summary

P_PROB = """You are writing the answer key for a probability practice problem that targets a known misconception.

Problem: {stem}
Misconception: {desc}

Give (1) the exact correct answer and (2) the exact answer that a student holding this misconception would give. Write each as an integer or a fraction a/b in lowest terms.
Reply with JSON only: {{"correct": "...", "misconception_answer": "..."}}"""


def to_frac(x):
    try:
        return Fraction(str(x).strip().replace(" ", ""))
    except (ValueError, ZeroDivisionError):
        return None


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="gpt-4.1-mini,gpt-5.4-mini,gpt-5.5")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args(argv)
    models = [m for m in a.models.split(",") if m]
    items = build()
    rows_in = [{"item_id": it.item_id, "prompt": P_PROB.format(stem=it.stem, desc=DESCRIPTIONS[it.code])} for it in items]
    res = {"part": "prob_pack", "protocol": "eval/llm_gap_protocol.md (Addendum A)", "price_source": PRICE_SOURCE,
           "counts": {c: sum(1 for it in items if it.code == c) for c in CODES}, "methods": {}, "usage": {}, "invalid": {},
           "decisions": {}, "command": "python -m eval.run_prob_pack " + " ".join(argv if argv is not None else sys.argv[1:])}
    res["methods"]["EXEC"] = {"key_correct": 1.0, "bug_correct": 1.0, "both_correct": 1.0, "note": "exact by construction"}
    store = load_store("prob_pack")
    for m in ([] if a.dry else models):
        sub = rows_in[: a.limit] if a.limit else rows_in
        out = {r["item_id"]: r for r in query(sub, m, store, a.offline)}
        key_ok, bug_ok, both, inv, per = [], [], [], 0, {c: [] for c in CODES}
        for it in items:
            r = out.get(it.item_id)
            if r is None:
                continue
            d = parse_json(r["content"])
            k = to_frac(d.get("correct")) if isinstance(d, dict) else None
            b = to_frac(d.get("misconception_answer")) if isinstance(d, dict) else None
            inv += k is None or b is None
            key_ok.append(k == it.key)
            bug_ok.append(b == it.bug)
            both.append(k == it.key and b == it.bug)
            per[it.code].append(k == it.key and b == it.bug)
        res["methods"][f"LLM:{m}"] = {"n": len(both), "key_correct": r4(np.mean(key_ok)), "key_ci": ci(key_ok),
                                      "bug_correct": r4(np.mean(bug_ok)), "bug_ci": ci(bug_ok),
                                      "both_correct": r4(np.mean(both)), "both_ci": ci(both),
                                      "both_by_code": {c: r4(np.mean(v)) for c, v in per.items() if v}}
        res["usage"][m] = usage_summary(list(out.values()), m)
        res["invalid"][m] = inv
        ci_b = res["methods"][f"LLM:{m}"]["both_ci"]
        res["decisions"][m] = {"H7_both_correct": res["methods"][f"LLM:{m}"]["both_correct"], "H7_ci": ci_b,
                               "H7_gap": bool(ci_b[1] < 0.95)}
    if not a.dry and not a.offline:
        save_store("prob_pack", store)
    res["total_cost_usd_estimate"] = round(sum(u["cost_usd_estimate"] for u in res["usage"].values()), 4)
    if not a.dry and not a.limit:
        (RES / "llm_gaps_prob_pack.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: res[k] for k in ("counts", "decisions", "invalid", "usage", "total_cost_usd_estimate")}, default=str))
    for name, mtr in res["methods"].items():
        print(name, json.dumps(mtr)[:300])
    if a.dry:
        for it in items[::12]:
            print(it.item_id, "|", it.stem, "| key", canon(it.key), "| bug", canon(it.bug))


if __name__ == "__main__":
    main()
