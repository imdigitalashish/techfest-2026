"""Post-hoc sensitivity of the v2 holdout conclusions (EXPLORATORY — added after the holdout was read,
in response to reviews S1/A1, A2, A13 in reviews/2026-10-04-*). Does not replace the pre-registered analysis.

    cd perceptron-p04-lob-regimes && python eval/sensitivity_v2.py

From the per-day summaries in eval/results/v2_holdout*.json (per-day mean log-loss and non-tie count n,
which share the same steps across policies), it recomputes paired day-cluster bootstrap CIs for:
  - the full 22-day holdout (reproduces the registered table);
  - the 21 days excluding 2025-08-01, the one holdout day already evaluated in v1 (overnight);
  - 99% CIs, i.e. Bonferroni over the five reported holdout hypotheses (H1, H2, H1b, H2b, H3);
  - equal-day weighting and the leave-one-day-out range of the pooled difference;
  - the post-hoc matched-normalisation ablation (regime heads vs a single EWMA head).
Writes eval/results/v2_holdout_sensitivity.{md,json}.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "eval" / "results"
EXPOSED = ["2025-08-01"]  # in the v1 holdout (eval/results/baseline.md), read before v2 was registered


def per_day(js: dict, policy: str) -> dict[str, tuple[float, int]]:
    return {d: (v["logloss"], v["n"]) for d, v in js["per_day"][policy].items()}


def cluster_ci(a: dict, b: dict, days: list[str], n_boot: int = 4000, seed: int = 0,
               levels=(95.0, 97.5, 99.0)) -> dict:
    sums = np.array([a[d][1] * (a[d][0] - b[d][0]) for d in days])
    ns = np.array([float(a[d][1]) for d in days])
    assert all(a[d][1] == b[d][1] for d in days), "paired policies must share the same scored steps"
    rng = np.random.default_rng(seed)
    pick = rng.integers(0, len(days), size=(n_boot, len(days)))
    means = sums[pick].sum(1) / ns[pick].sum(1)
    out = {"mean": float(sums.sum() / ns.sum()), "n_days": len(days), "days_better": int((sums < 0).sum()),
           "equal_day_mean": float(np.mean(sums / ns))}
    for lv in levels:
        lo, hi = np.percentile(means, [(100 - lv) / 2, 100 - (100 - lv) / 2])
        out[f"ci{lv:g}"] = [float(lo), float(hi)]
    loo = [(sums.sum() - sums[i]) / (ns.sum() - ns[i]) for i in range(len(days))]
    out["leave_one_day_out_range"] = [float(min(loo)), float(max(loo))]
    return out


def main() -> int:
    main_js = json.loads((RES / "v2_holdout.json").read_text())
    days = main_js["meta"]["eval_days"]
    clean = [d for d in days if d not in EXPOSED]
    comps = [("spike", "static_snorm", "H1"), ("spike", "ks_refit", "H2"), ("spike_gate", "static_snorm", "H1b"),
             ("spike_gate", "ks_refit", "H2b"), ("spike_gate", "regime_gated", "H3"),
             ("regime_gated", "static_snorm", "secondary"), ("static_gbdt", "static_snorm", "secondary"),
             ("static_wf", "static_snorm", "secondary")]
    out = {"note": "EXPLORATORY post-hoc sensitivity; see module docstring", "exposed_days": EXPOSED, "rows": []}
    for pol, ref, tag in comps:
        a, b = per_day(main_js, pol), per_day(main_js, ref)
        out["rows"].append({"policy": pol, "ref": ref, "hypothesis": tag,
                            "all22": cluster_ci(a, b, days), "clean21": cluster_ci(a, b, clean)})
    abl = RES / "v2_holdout_posthoc_ablation.json"
    if abl.exists():
        aj = json.loads(abl.read_text())
        for pol, ref in (("regime_gated", "static_enorm"), ("static_enorm", "static_snorm"), ("spike_gate", "static_enorm")):
            a, b = per_day(aj, pol), per_day(aj, ref)
            out["rows"].append({"policy": pol, "ref": ref, "hypothesis": "post-hoc ablation",
                                "all22": cluster_ci(a, b, days), "clean21": cluster_ci(a, b, clean)})
    (RES / "v2_holdout_sensitivity.json").write_text(json.dumps(out, indent=1))
    f = lambda c, k: f"{c['mean']:+.4f} [{c[k][0]:+.4f}, {c[k][1]:+.4f}]"
    L = ["# v2 holdout — post-hoc sensitivity (EXPLORATORY)", "",
         "- Command: `python eval/sensitivity_v2.py` (from `perceptron-p04-lob-regimes/`); inputs: `eval/results/v2_holdout.json`"
         + (", `eval/results/v2_holdout_posthoc_ablation.json`" if abl.exists() else ""),
         "- Added after the holdout was read, in response to the cross-model reviews (`reviews/`). The registered analysis is `v2_holdout.md`.",
         f"- `clean21` excludes {', '.join(EXPOSED)}, the one holdout day already evaluated in the v1 overnight run.",
         "- Paired day-cluster bootstrap (4,000 resamples of days). 99% CI = Bonferroni over the five reported holdout hypotheses.", "",
         "| comparison | role | 22 days: Δ [97.5% CI] | 22 days: 99% CI | days better | equal-day mean | leave-one-day-out range | 21 clean days: Δ [97.5% CI] | 21 clean: 99% CI |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in out["rows"]:
        A, C = r["all22"], r["clean21"]
        L.append(f"| {r['policy']} − {r['ref']} | {r['hypothesis']} | {f(A, 'ci97.5')} | [{A['ci99'][0]:+.4f}, {A['ci99'][1]:+.4f}] | "
                 f"{A['days_better']}/{A['n_days']} | {A['equal_day_mean']:+.4f} | [{A['leave_one_day_out_range'][0]:+.4f}, "
                 f"{A['leave_one_day_out_range'][1]:+.4f}] | {f(C, 'ci97.5')} | [{C['ci99'][0]:+.4f}, {C['ci99'][1]:+.4f}] |")
    (RES / "v2_holdout_sensitivity.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
