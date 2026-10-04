"""FROZEN evaluator for the credibility engine (the auto-research loop must not edit this file).

Prints one JSON line. Primary scalar: `auroc_fabricating` — AUROC of (1 - credibility) for
identifying SYNTHETIC Anganwadi centres whose worker copies measurements forward, averaged
over 3 simulator seeds. Secondary: AUROC for any non-good worker; record-level recall of
gross errors; prevalence bias (raw vs credibility-filtered vs truth).
Run: .venv/bin/python -m components.credibility_engine.eval
"""

from __future__ import annotations

import json
import sys

import numpy as np
from sklearn.metrics import roc_auc_score

from components.cohort_simulator.simulate import SimConfig, simulate
from components.credibility_engine import engine

SEEDS = (11, 12, 13)


def one(seed: int) -> dict:
    out = simulate(SimConfig(seed=seed))
    geo, meas, truth = out["geo"], out["measurements"], out["truth_monthly"]
    mz, rec, units = engine.assess(meas)
    u = units.merge(geo[["awc_code", "worker_type"]], left_on="unit_id", right_on="awc_code")
    susp = 1 - u.credibility
    fab = (u.worker_type == "fabricating").astype(int)
    bad = (u.worker_type != "good").astype(int)
    gross = (mz.weight_kg / mz.groupby("child_key").weight_kg.transform("median")) > 4
    rr = rec.set_index("event_id").loc[mz.event_id]
    # prevalence bias: observed WHZ<-2 among usable records vs true WLZ<-2 in the same months
    usable_ev = set(rec.event_id[rec.usable])
    obs = mz[mz.event_id.isin(usable_ev)]
    raw_prev = float((obs.wlhz < -2).mean())
    keep_awc = set(u.awc_code[u.band.isin(["high", "medium"])])
    adj_prev = float((obs[obs.awc_code.isin(keep_awc)].wlhz < -2).mean())
    true_prev = float((truth.true_wlz < -2).mean())
    return dict(
        auroc_fabricating=roc_auc_score(fab, susp), auroc_nongood=roc_auc_score(bad, susp),
        gross_error_recall=float((~rr.usable.to_numpy())[gross.to_numpy()].mean()) if gross.any() else np.nan,
        reject_rate=float((~rec.usable).mean()), prev_true=true_prev, prev_raw=raw_prev, prev_cred_filtered=adj_prev,
    )


def main() -> dict:
    rs = [one(s) for s in SEEDS]
    agg = {k: round(float(np.nanmean([r[k] for r in rs])), 4) for k in rs[0]}
    agg["auroc_fabricating_sd"] = round(float(np.std([r["auroc_fabricating"] for r in rs])), 4)
    res = {"metric": "auroc_fabricating", "value": agg["auroc_fabricating"], **agg, "seeds": list(SEEDS), "synthetic": True}
    print(json.dumps(res))
    return res


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
