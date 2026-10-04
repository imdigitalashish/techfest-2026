"""C5 early_warning — capacity-constrained 90-day risk of incident wasting (spike B, v0).

Scores every measured child-month; the action router takes the top-k per AWC per month
(k = the worker's spare home-visit capacity). Models here are deliberately simple and
interpretable; `eval.py` (frozen) compares them on held-out SYNTHETIC cohorts.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from components.credibility_engine import engine

ANTHRO = ["wlhz", "waz", "lhaz", "d_wlz1", "dw1", "dw2", "no_gain_2m", "age_m", "infant", "prior_wasted", "awc_cred"]
HEALTH = ["lbw", "bw_known", "recent_ill", "missed_vax_90d"]


def features(meas: pd.DataFrame, health: pd.DataFrame, month_of: pd.DataFrame) -> pd.DataFrame:
    """Per usable measurement: features visible to the system at that date (no look-ahead)."""
    mz, rec, units = engine.assess(meas)
    mz = mz.merge(rec[["event_id", "usable"]], on="event_id")
    df = mz[mz.usable].merge(month_of, on=["child_key", "measured_on"], how="inner")
    df = df.sort_values(["child_key", "month_index"]).reset_index(drop=True)
    g = df.groupby("child_key", sort=False)
    df["d_wlz1"] = g.wlhz.diff()
    df["dw1"] = g.weight_kg.diff()
    df["dw2"] = g.weight_kg.diff(2)
    df["no_gain_2m"] = ((df.dw1 <= 0) & (g.dw1.shift(1) <= 0)).astype(float)
    wasted_now = (df.wlhz < -2).astype(int)
    df["prior_wasted"] = wasted_now.groupby(df.child_key).cummax().groupby(df.child_key).shift(1).fillna(0)
    df["age_m"] = df.age_days / 30.4375
    df["infant"] = (df.age_m < 6).astype(float)
    df["awc_cred"] = df.awc_code.map(units.set_index("unit_id").credibility)

    bw = health[health.kind == "birth_weight"].drop_duplicates("child_key").set_index("child_key").value
    df["bw_known"] = df.child_key.map(bw).notna().astype(float)
    df["lbw"] = (df.child_key.map(bw) < 2.5).astype(float)

    def recent(kind: str, days: int) -> pd.Series:
        ev = health[health.kind == kind][["child_key", "occurred_on"]].sort_values("occurred_on")
        left = df[["child_key", "measured_on"]].reset_index().sort_values("measured_on")
        m = pd.merge_asof(left, ev.rename(columns={"occurred_on": "last"}), left_on="measured_on",
                          right_on="last", by="child_key", direction="backward")
        hit = (m.measured_on - m["last"]).dt.days.le(days)
        return pd.Series(hit.to_numpy(dtype=float), index=m["index"]).reindex(df.index).fillna(0)

    df["recent_ill"] = recent("illness_diarrhoea", 45)
    df["missed_vax_90d"] = recent("immunisation_missed", 90)
    return df


def fill(X: pd.DataFrame) -> pd.DataFrame:
    return X.fillna({"d_wlz1": 0, "dw1": 0.2, "dw2": 0.4, "awc_cred": 0.5}).fillna(0)


def fit_logistic(train: pd.DataFrame, cols: list[str], y: str = "label"):
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=0.5))
    model.fit(fill(train[cols]), train[y])
    return model


def score_rule_no_gain(df: pd.DataFrame) -> np.ndarray:
    """Programme rule: no weight gain in 2 consecutive months; ties broken by lower WHZ."""
    return df.no_gain_2m.to_numpy() * 10 - df.wlhz.fillna(0).to_numpy()


def score_lowest_whz(df: pd.DataFrame) -> np.ndarray:
    """Point-in-time status quo: closest to the MAM line first."""
    return -df.wlhz.fillna(0).to_numpy()
