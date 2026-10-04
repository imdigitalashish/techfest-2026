"""FROZEN evaluator for early_warning (spike B). Prints one JSON line.

Unit: a measured child-month t where the child is truly NOT wasted (SYNTHETIC truth).
Positive: truly wasted (true WLZ < -2) in any of months t+1..t+3 (needs all 3 months observed).
Capacity: each AWC can act on K children per month (assumption, K=5 ≈ 10% of an AWC's under-5s).
Primary scalar: recall@K = share of positives that were in their AWC's top-K list at t.
Train on seeds 21-22, test on held-out seed 23 (different children, AWCs, workers).
Run: .venv/bin/python -m components.early_warning.eval
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from components.cohort_simulator.simulate import SimConfig, simulate
from components.early_warning import model as ew

K = 5
TRAIN_SEEDS, TEST_SEED = (21, 22), 23


def labelled(seed: int) -> pd.DataFrame:
    out = simulate(SimConfig(seed=seed))
    t = out["truth_monthly"].sort_values(["child_key", "month_index"])
    g = t.groupby("child_key").true_wlz
    fut = pd.concat([g.shift(-1), g.shift(-2), g.shift(-3)], axis=1)
    t = t.assign(fut_min=fut.min(axis=1, skipna=False))
    month_of = t[["child_key", "measured_on", "month_index"]]
    df = ew.features(out["measurements"], out["health_events"], month_of)
    df = df.merge(t[["child_key", "month_index", "true_wlz", "fut_min"]], on=["child_key", "month_index"])
    df = df[(df.true_wlz >= -2) & df.fut_min.notna()].copy()
    df["label"] = (df.fut_min < -2).astype(int)
    df["seed"] = seed
    return df


def recall_at_k(df: pd.DataFrame, score: np.ndarray, k: int = K) -> tuple[float, float]:
    d = df.assign(score=score)
    d["rank"] = d.groupby(["awc_code", "month_index"]).score.rank(ascending=False, method="first")
    sel = d["rank"] <= k
    return float(d.label[sel].sum() / d.label.sum()), float(d.label[sel].mean())


def main() -> dict:
    train = pd.concat([labelled(s) for s in TRAIN_SEEDS], ignore_index=True)
    test = labelled(TEST_SEED)
    res = {"metric": f"recall_at_{K}_per_awc_month", "K": K, "n_test_rows": int(len(test)),
           "n_test_positives": int(test.label.sum()), "base_rate": round(float(test.label.mean()), 4)}
    m_anthro = ew.fit_logistic(train, ew.ANTHRO)
    m_full = ew.fit_logistic(train, ew.ANTHRO + ew.HEALTH)
    scores = {
        "rule_no_gain_2m": ew.score_rule_no_gain(test),
        "lowest_whz_now": ew.score_lowest_whz(test),
        "logistic_anthro": m_anthro.predict_proba(ew.fill(test[ew.ANTHRO]))[:, 1],
        "logistic_anthro_plus_linked_health": m_full.predict_proba(ew.fill(test[ew.ANTHRO + ew.HEALTH]))[:, 1],
    }
    for name, s in scores.items():
        r, p = recall_at_k(test, s)
        res[name] = {"recall_at_k": round(r, 4), "precision_at_k": round(p, 4)}
    res["value"] = res["logistic_anthro_plus_linked_health"]["recall_at_k"]
    res["synthetic"] = True
    print(json.dumps(res))
    return res


if __name__ == "__main__":
    main()
