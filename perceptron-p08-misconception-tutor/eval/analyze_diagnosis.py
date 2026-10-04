"""Derived diagnosis numbers from the committed eval/results/diagnosis.json (no API calls).

Run:  .venv/bin/python -m eval.analyze_diagnosis
Out:  eval/results/diagnosis_derived.json
Computes the exec->TF-IDF hybrid, executable-path precision when it fires, LLM accuracy split by whether
the executable path fires, and 95% bootstrap CIs (2,000 resamples, seed 0).
"""
from __future__ import annotations

import json
import pathlib
import random
from collections import Counter

RES = pathlib.Path(__file__).parent / "results"


def main() -> None:
    d = json.loads((RES / "diagnosis.json").read_text())
    rows = d["B_mvp_closed_set"]["rows"]
    n = len(rows)
    exec_pick = lambda r: r["matched"][0] if len(r["matched"]) == 1 else None
    preds = {
        "majority": lambda r: Counter(x["code"] for x in rows).most_common(1)[0][0],
        "tfidf": lambda r: r["tfidf"],
        "exec_then_tfidf": lambda r: exec_pick(r) or r["tfidf"],
        "llm": lambda r: r.get("llm"),
        "exec_then_llm": lambda r: exec_pick(r) or r.get("llm"),
    }
    rng = random.Random(0)
    out = {"source": d.get("command"), "n": n, "accuracy": {}, "ci95": {}}
    for name, f in preds.items():
        hits = [f(r) == r["code"] for r in rows]
        out["accuracy"][name] = sum(hits) / n
        boots = sorted(sum(hits[rng.randrange(n)] for _ in range(n)) / n for _ in range(2000))
        out["ci95"][name] = [boots[50], boots[1949]]
    fired = [r for r in rows if exec_pick(r)]
    rest = [r for r in rows if not exec_pick(r)]
    out["exec_fires_unique"] = len(fired)
    out["exec_correct_when_fires"] = sum(exec_pick(r) == r["code"] for r in fired)
    out["llm_acc_when_exec_fires"] = sum(r.get("llm") == r["code"] for r in fired) / max(1, len(fired))
    out["llm_acc_when_exec_silent"] = sum(r.get("llm") == r["code"] for r in rest) / max(1, len(rest))
    (RES / "diagnosis_derived.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
