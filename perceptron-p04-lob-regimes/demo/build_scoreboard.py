"""Export the committed held-out results the demo page shows into one small JSON (no recomputation).

    cd perceptron-p04-lob-regimes && python demo/build_scoreboard.py

Reads eval/results/v2_holdout.json, v2_holdout_posthoc_ablation.json, v2_holdout_posthoc_heads.json and
head_usage.md; writes demo/results/scoreboard.json. Every number keeps its status label.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

DEMO = Path(__file__).resolve().parent
ER = DEMO.parent / "eval" / "results"

PRE1, PRE2, POSTDEV, POSTHOC = ("pre-registered primary", "pre-registered secondary", "post-dev secondary",
                                "post-hoc exploratory")
ROWS = [  # (policy, source file, display name, what it is, status of its Δ vs static)
    ("static_snorm", "v2_holdout", "Static model", "one logistic head, static normalisation (baseline)", "baseline"),
    ("ks_refit", "v2_holdout", "Textbook KS → refit", "naive KS alarm (α = 1e-3) triggers a refit", PRE2),
    ("ksc_refit", "v2_holdout", "Calibrated KS → refit", "empirical-null KS alarm triggers a refit", PRE2),
    ("spike", "v2_holdout", "Registered spike (Fixed-Share)", "H1: registered hypothesis", PRE1),
    ("static_enorm", "v2_holdout_posthoc_ablation", "One EWMA head", "same EWMA features as the gate, one head", POSTHOC),
    ("head_lo_only", "v2_holdout_posthoc_heads", "Low-vol head alone", "one regime head used everywhere", POSTHOC),
    ("head_mid_only", "v2_holdout_posthoc_heads", "Mid-vol head alone", "one regime head used everywhere", POSTHOC),
    ("head_hi_only", "v2_holdout_posthoc_heads", "High-vol head alone", "one regime head used everywhere", POSTHOC),
    ("spike_gate", "v2_holdout", "Gate + CUSUM shrinkage", "H1b: regime gate, CUSUM shrinks confidence", POSTDEV),
    ("regime_gated", "v2_holdout", "Regime gate", "3 volatility-regime heads, gate on trailing 10-min vol", PRE2),
]
EDGE_POLICIES = ["static_snorm", "ks_refit", "static_enorm", "regime_gated", "spike_gate"]


def _dc(s: dict, ref: str) -> dict | None:
    v = s.get(f"vs_{ref}")
    if not v:
        return None
    d = v["day_cluster"]
    return {"mean": d["mean"], "ci97_5": d["ci97.5"], "days_better": d["days_better"], "n_days": d["n_days"]}


def main() -> None:
    J = {k: json.loads((ER / f"{k}.json").read_text())
         for k in ("v2_holdout", "v2_holdout_posthoc_ablation", "v2_holdout_posthoc_heads")}
    rows = []
    for pol, src, name, what, status in ROWS:
        s = J[src]["summary"][pol]
        rows.append({"policy": pol, "name": name, "what": what, "status": status, "source": f"eval/results/{src}.json",
                     "logloss": s["logloss"], "auc": s["auc"], "vs_static": _dc(s, "static_snorm"),
                     "vs_regime_gated": _dc(s, "regime_gated"), "alarms_per_day": s["alarms_per_day"],
                     "per_day": {d: r["logloss"] for d, r in J[src]["per_day"][pol].items()}})
    h2 = _dc(J["v2_holdout"]["summary"]["spike"], "ks_refit")
    m = re.search(r"\*\*all holdout days\*\*\s*\|\s*\*\*([\d.]+)%\*\*\s*\|\s*\*\*([\d.]+)%\*\*\s*\|\s*\*\*([\d.]+)%\*\*",
                  (ER / "head_usage.md").read_text())
    usage = {"low": float(m.group(1)), "mid": float(m.group(2)), "high": float(m.group(3)),
             "status": POSTHOC, "source": "eval/results/head_usage.md"}
    edge = {}
    for pol in EDGE_POLICIES:
        src = "v2_holdout" if pol in J["v2_holdout"]["summary"] else "v2_holdout_posthoc_ablation"
        edge[pol] = {dl: {k: v for k, v in e.items() if k != "top_decile_rule"}
                     for dl, e in J[src]["summary"][pol]["edge"].items()}
    regime = J["v2_holdout"]["regime_by_day"]
    by_rv = sorted(regime, key=lambda d: regime[d]["rv_600s_bps_mean"])
    replay = [{"day": "2024-05-01", "role": "dev day, illustrative (FOMC statement 18:00 UTC)"},
              {"day": by_rv[0], "role": "held-out, calmest (lowest mean rv_600s)"},
              {"day": by_rv[(len(by_rv) - 1) // 2], "role": "held-out, lower median mean rv_600s"},
              {"day": by_rv[-1], "role": "held-out, most volatile (highest mean rv_600s)"}]
    out = {"status_note": "Committed held-out results (22 first-of-month days 2025-01 … 2026-10; trained on 2023, "
                          "tuned on 2024). Δ = per-step log-loss difference, paired day-cluster bootstrap 97.5% CI.",
           "rows": rows, "h2": {"spike_vs_ks_refit": h2, "status": PRE1}, "head_usage": usage,
           "edge": {"status": PRE2, "source": "eval/results/v2_holdout.json, v2_holdout_posthoc_ablation.json",
                    "fees_bps": J["v2_holdout"]["meta"]["cfg"]["fees_bps"], "policies": edge},
           "regime_by_day": {d: regime[d]["rv_600s_bps_mean"] for d in by_rv},
           "replay_days": replay,
           "replay_rule": "dev FOMC day (illustrative) + held-out days with the lowest, lower-median and highest mean "
                          "rv_600s in the committed regime_by_day"}
    (DEMO / "results").mkdir(exist_ok=True)
    (DEMO / "results" / "scoreboard.json").write_text(json.dumps(out, indent=1))
    print("wrote demo/results/scoreboard.json;", "replay days:", [r["day"] for r in replay])


if __name__ == "__main__":
    main()
