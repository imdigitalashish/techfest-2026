"""Pre-registered analysis for C6 v0.3 (eval/preregistration/c6_v03.md). Do not edit after registration.

Reads eval/results/c6_v03_prereg.json (seeds 20-29). Usage: .venv/bin/python eval/prereg_c6_v03_analysis.py
"""
import json
import pathlib

import numpy as np
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
runs = json.load(open(ROOT / "eval" / "results" / "c6_v03_prereg.json"))["runs"]
assert [x["seed"] for x in runs] == list(range(20, 30)), "registered seeds are 20-29"


def paired_vals(d) -> dict:
    d = np.asarray(d, dtype=float)
    t = stats.ttest_1samp(d, 0.0, alternative="greater")
    half = stats.t.ppf(0.975, len(d) - 1) * d.std(ddof=1) / np.sqrt(len(d))
    return {"mean_diff": float(d.mean()), "ci95": [float(d.mean() - half), float(d.mean() + half)],
            "p_one_sided": float(t.pvalue), "seeds_positive": int((d > 0).sum()), "n": int(len(d))}


def paired(a: str, b: str) -> dict:
    return {"comparison": f"{a} - {b}", **paired_vals([x["policies"][a]["normalised"] - x["policies"][b]["normalised"] for x in runs])}


out = {"H1_challenger_vs_rule": paired("challenger", "rule"),
       "H2_rule_vs_best_arm_only": paired("rule", "best_arm_only"),
       "S1_rule_vs_status_quo": paired("rule", "status_quo"),
       "S2_gated_vs_rule": paired("gated", "rule"),
       "S3_perfect_linkage_challenger_minus_rule": paired_vals([x["linkage_sensitivity"]["perfect_linkage_challenger_minus_rule"] for x in runs]),
       "gate_pass_count": int(sum(x["gate"]["pass"] for x in runs)),
       "H3_floors_all": bool(all(x["policies"][p]["floor_ok"] for x in runs for p in ("rule", "challenger", "gated"))),
       "H3_budgets_all": bool(all(x["policies"][p]["within_budget"] for x in runs for p in x["policies"])),
       "H3_holdout_untreated_all": bool(all(x["policies"][p]["holdout_treated"] == 0 for x in runs for p in ("rule", "challenger", "gated"))),
       "means": {p: float(np.mean([x["policies"][p]["normalised"] for x in runs])) for p in runs[0]["policies"]},
       "sds": {p: float(np.std([x["policies"][p]["normalised"] for x in runs], ddof=1)) for p in runs[0]["policies"]},
       "value_means": {p: float(np.mean([x["policies"][p]["value"] for x in runs])) for p in runs[0]["policies"]},
       "eligible_mean": float(np.mean([x["eligible"] for x in runs])),
       "pilot_train_mean": float(np.mean([x["pilot_train"] for x in runs])),
       "gate_validation_mean": float(np.mean([x["gate"]["n_validation"] for x in runs]))}
h1 = out["H1_challenger_vs_rule"]
out["H1_pass"] = bool(h1["mean_diff"] > 0 and h1["p_one_sided"] < 0.05)
h2 = out["H2_rule_vs_best_arm_only"]
out["H2_pass"] = bool(h2["mean_diff"] > 0 and h2["p_one_sided"] < 0.05)
out["H3_pass"] = out["H3_floors_all"] and out["H3_budgets_all"] and out["H3_holdout_untreated_all"]
(ROOT / "eval" / "results" / "c6_v03_prereg_analysis.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: v for k, v in out.items() if k not in ("means", "sds", "value_means")}, indent=1))
