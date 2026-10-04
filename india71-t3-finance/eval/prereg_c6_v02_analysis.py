"""Pre-registered analysis for the C6 v0.2 test (see eval/preregistration/c6_v02.md). Do not edit after registration.

Reads eval/results/c6_v02_prereg.json (seeds 10-19) and prints the registered tests.
Usage (from india71-t3-finance/): .venv/bin/python eval/prereg_c6_v02_analysis.py
"""
import json
import pathlib

import numpy as np
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
r = json.load(open(ROOT / "eval" / "results" / "c6_v02_prereg.json"))
runs = r["runs"]
assert [x["seed"] for x in runs] == list(range(10, 20)), "registered seeds are 10-19"


def paired(a: str, b: str) -> dict:
    d = np.array([x["policies"][a]["normalised"] - x["policies"][b]["normalised"] for x in runs])
    t = stats.ttest_1samp(d, 0.0, alternative="greater")
    half = stats.t.ppf(0.975, len(d) - 1) * d.std(ddof=1) / np.sqrt(len(d))
    return {"comparison": f"{a} - {b}", "mean_diff": float(d.mean()), "ci95": [float(d.mean() - half), float(d.mean() + half)],
            "p_one_sided": float(t.pvalue), "seeds_positive": int((d > 0).sum()), "n": int(len(d))}


out = {"H1_challenger_who_vs_rule": paired("challenger_who", "rule"),
       "H2_rule_vs_best_arm_only": paired("rule", "best_arm_only"),
       "S1_rule_vs_status_quo": paired("rule", "status_quo"),
       "S2_challenger_model_arm_vs_rule": paired("challenger", "rule"),
       "S3_gated_vs_rule": paired("gated", "rule"),
       "gate_pass_count": int(sum(x["gate"]["pass"] for x in runs)),
       "means": {p: float(np.mean([x["policies"][p]["normalised"] for x in runs])) for p in runs[0]["policies"]},
       "sds": {p: float(np.std([x["policies"][p]["normalised"] for x in runs], ddof=1)) for p in runs[0]["policies"]}}
out["H1_pass"] = bool(out["H1_challenger_who_vs_rule"]["mean_diff"] > 0 and out["H1_challenger_who_vs_rule"]["p_one_sided"] < 0.05)
out["H2_pass"] = bool(out["H2_rule_vs_best_arm_only"]["mean_diff"] > 0 and out["H2_rule_vs_best_arm_only"]["p_one_sided"] < 0.05)
(ROOT / "eval" / "results" / "c6_v02_prereg_analysis.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
