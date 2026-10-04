"""Post-hoc breakdown of the evaluator v2.1 holdout (machine-written source for every attribution number in the docs).

Imports the FROZEN evaluator (eval_v2.py) without modifying it and recomputes, for each method, on the holdout configuration
(TEST period Jan–Sep 2026, HOLDOUT_SEEDS, the three scenarios + the hidden 'hard-rect' geometry):
  mae_all        all-hour MAE vs the max-node exposure truth, abstentions scored as 0  (= eval_v2's holdout scalar)
  mae_work       the same, on work hours only (08–18 IST, Mon–Sat), where site dust is actually emitted
  mae_diff_cov   MAE vs the identifiable contrast (true downwind minus upwind contribution), covered hours only
  coverage, csi_gt50, pod_gt50, far_gt50 (events: exposure truth > 50 µg/m³; undefined ratios are null)
Caveats (gpt-6-sol review, 4 Oct): this holdout is fresh-seeded but NOT blind — TEST was seen during v0/v1 and the hidden
geometry is visible in the evaluator source. ring_refcal14 was added after the review as a stronger reference baseline.
Run (from this folder): OMP_NUM_THREADS=1 nice -n 10 python breakdown_v21.py  → breakdown_v21.json
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
import eval_v2 as ev  # noqa: E402
import methods  # noqa: E402

NAMES = ["pair_fixed", "ring", "ring_refcal", "ring_refcal14", "ring_selfcal"]


def stats(est, ab, tmax, tdiff, mask):
    ab = ab | ~np.isfinite(est)
    est = np.where(np.isfinite(est), est, 0.0)
    e = np.where(ab, 0.0, est)
    cov = mask & ~ab
    o, f = tmax[mask] > ev.EXCEED, e[mask] > ev.EXCEED
    h, m, fa = int((o & f).sum()), int((o & ~f).sum()), int((~o & f).sum())
    return {"mae": float(np.mean(np.abs(e[mask] - tmax[mask]))),
            "mae_diff_cov": float(np.mean(np.abs(est[cov] - tdiff[cov]))) if cov.any() else None,
            "coverage": float(cov.sum() / max(1, mask.sum())),
            "csi": h / (h + m + fa) if h + m + fa else None, "pod": h / (h + m) if h + m else None,
            "far": fa / (h + fa) if h + fa else None}


def main():
    df = ev.load()
    scen = dict(ev.SCENARIOS, **ev.HIDDEN)
    acc = {n: {"all": [], "work": [], "per_scenario": {s: [] for s in scen}} for n in NAMES}
    for sname, sc in scen.items():
        for seed in ev.HOLDOUT_SEEDS:
            obs, tmax, tdiff, geom = ev.simulate(df, np.random.default_rng(seed), sc)
            idx = obs.index
            test = (idx >= ev.TEST[0]) & (idx <= ev.TEST[1] + " 23:00")
            work = test & (idx.hour >= 8) & (idx.hour < 18) & (idx.dayofweek < 6)
            for n in NAMES:
                est, ab = methods.METHODS[n](obs, geom)
                est, ab = np.asarray(est, float), np.asarray(ab, bool)
                a, w = stats(est, ab, tmax, tdiff, test), stats(est, ab, tmax, tdiff, work)
                acc[n]["all"].append(a); acc[n]["work"].append(w); acc[n]["per_scenario"][sname].append(a["mae"])
    mean = lambda xs: float(np.mean([x for x in xs if x is not None])) if any(x is not None for x in xs) else None
    out = {"config": {"period": ev.TEST, "seeds": ev.HOLDOUT_SEEDS, "scenarios": list(scen), "exceed": ev.EXCEED,
                      "blind": False, "note": "fresh seeds, not blind (see docstring)"}, "methods": {}}
    for n in NAMES:
        A, W = acc[n]["all"], acc[n]["work"]
        out["methods"][n] = {
            "mae_all": round(mean([x["mae"] for x in A]), 2), "mae_work": round(mean([x["mae"] for x in W]), 2),
            "mae_diff_cov": round(mean([x["mae_diff_cov"] for x in A]), 2), "coverage": round(mean([x["coverage"] for x in A]), 3),
            "coverage_work": round(mean([x["coverage"] for x in W]), 3),
            "csi_gt50": round(mean([x["csi"] for x in A]), 3), "pod_gt50": round(mean([x["pod"] for x in A]), 3),
            "far_gt50": round(mean([x["far"] for x in A]), 3),
            "csi_gt50_work": round(mean([x["csi"] for x in W]), 3),
            "per_scenario_mae_all": {s: round(float(np.mean(v)), 2) for s, v in acc[n]["per_scenario"].items()}}
    with open(os.path.join(HERE, "breakdown_v21.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    for n, v in out["methods"].items():
        print(f"{n:14s} all {v['mae_all']:6.2f} work {v['mae_work']:6.2f} diff {v['mae_diff_cov']:6.2f} cov {v['coverage']:.3f} "
              f"CSI {v['csi_gt50']:.3f} POD {v['pod_gt50']:.3f} FAR {v['far_gt50']:.3f} | {v['per_scenario_mae_all']}")


if __name__ == "__main__":
    main()
