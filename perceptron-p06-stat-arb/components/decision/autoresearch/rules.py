"""Library of decision rules the ratchet can select/compose in candidate.py.

Every rule: fit(train_rows_with_labels, **cfg) -> model; act(model, rows) -> bool mask.
Survival curves are fitted on *training* episodes only; test rows' durations are never used.
"""
from __future__ import annotations

import numpy as np
import polars as pl
from lifelines import KaplanMeierFitter
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor

from components.decay.survival import FEATURES

CELL = ["fee_bps", "delta_ms"]
THETAS = [0.0, 0.25, 0.5, 1, 1.5, 2, 3, 5, 10]


def _key(df: pl.DataFrame, cols: list[str]) -> list[tuple]:
    return list(zip(*[df[c].to_list() for c in cols]))


def fit_threshold(train: pl.DataFrame, by: list[str]) -> dict:
    th = {}
    for key, g in train.group_by(by):
        best = (np.inf, 0.0)
        for t in THETAS:
            p = float(g.filter(pl.col("net0_bps") > t)["pnl_usd"].sum())
            if p > best[1]:
                best = (t, p)
        th[key] = best[0]
    return {"by": by, "th": th}


def act_threshold(m: dict, rows: pl.DataFrame) -> np.ndarray:
    th = np.array([m["th"].get(k, np.inf) for k in _key(rows, m["by"])])
    return rows["net0_bps"].to_numpy() > th


def _edge_bucket(df: pl.DataFrame) -> pl.Series:
    return df["edge0_bps"].cut([2, 5], labels=["lo", "mid", "hi"]).cast(pl.Utf8)


def fit_ev(train: pl.DataFrame, strata: list[str], lam_mult: float = 1.0, min_n: int = 30) -> dict:
    ep = train.unique("opp_id")
    if "edge_bucket_s" in strata:
        ep = ep.with_columns(_edge_bucket(ep).alias("edge_bucket_s"))
    pooled = KaplanMeierFitter().fit(ep["T_ms"].to_numpy(), ep["E"].to_numpy()).survival_function_
    curves = {None: (pooled.index.to_numpy().astype(float), pooled.iloc[:, 0].to_numpy())}
    for key, g in ep.group_by(strata):
        if g.height >= min_n:
            sf = KaplanMeierFitter().fit(g["T_ms"].to_numpy(), g["E"].to_numpy()).survival_function_
            curves[key] = (sf.index.to_numpy().astype(float), sf.iloc[:, 0].to_numpy())
    lam = {}
    for key, g in train.group_by(CELL):
        f = g.filter(pl.col("outcome") != "both")
        lam[key] = max(0.0, -float(f["pnl_bps"].mean())) * lam_mult if f.height else 0.0
    return {"strata": strata, "curves": curves, "lam": lam}


def surv_rowwise(m: dict, rows: pl.DataFrame, t_ms: np.ndarray) -> np.ndarray:
    if "edge_bucket_s" in m["strata"]:
        rows = rows.with_columns(_edge_bucket(rows).alias("edge_bucket_s"))
    out = np.empty(rows.height)
    for i, (k, t) in enumerate(zip(_key(rows, m["strata"]), t_ms)):
        tt, ss = m["curves"].get(k, m["curves"][None])
        j = np.searchsorted(tt, t, side="right") - 1
        out[i] = ss[j] if j >= 0 else 1.0
    return out


def act_ev(m: dict, rows: pl.DataFrame) -> np.ndarray:
    S = surv_rowwise(m, rows, rows["L_ms"].to_numpy())
    lam = np.array([m["lam"].get(k, 0.0) for k in _key(rows, CELL)])
    return (S * rows["net0_bps"].to_numpy() - (1 - S) * lam) > 0


LEARN_X = FEATURES + ["edge0_bps", "net0_bps", "log_size", "pair_id", "L_ms", "fee_bps"]


EDGE_ONLY_X = ["edge0_bps", "net0_bps", "log_size", "pair_id", "L_ms", "fee_bps"]  # ablation: no ages/spreads/vol


def fit_gbm_reg(train: pl.DataFrame, seed: int = 0, iters: int = 200, clip: float = 30.0, x: list[str] | None = None) -> dict:
    x = x or LEARN_X
    X = train.select(x).to_numpy()
    y = np.clip(train["pnl_bps"].to_numpy(), -clip, clip)
    return {"x": x, "m": HistGradientBoostingRegressor(max_iter=iters, learning_rate=0.05, random_state=seed,
                                                       categorical_features=[x.index("pair_id")]).fit(X, y)}


def act_gbm_reg(m: dict, rows: pl.DataFrame, margin: float = 0.0) -> np.ndarray:
    return m["m"].predict(rows.select(m.get("x", LEARN_X)).to_numpy()) > margin


def fit_gbm_clf(train: pl.DataFrame, seed: int = 0, iters: int = 200) -> dict:
    X = train.select(LEARN_X).to_numpy()
    y = (train["pnl_usd"].to_numpy() > 0).astype(int)
    m = HistGradientBoostingClassifier(max_iter=iters, learning_rate=0.05, random_state=seed,
                                       categorical_features=[LEARN_X.index("pair_id")]).fit(X, y)
    win = {k: float(g.filter(pl.col("pnl_bps") > 0)["pnl_bps"].mean() or 0.0) for k, g in train.group_by(CELL)}
    loss = {k: float(-(g.filter(pl.col("pnl_bps") <= 0)["pnl_bps"].mean() or 0.0)) for k, g in train.group_by(CELL)}
    return {"m": m, "win": win, "loss": loss}


def act_gbm_clf(m: dict, rows: pl.DataFrame) -> np.ndarray:
    p = m["m"].predict_proba(rows.select(LEARN_X).to_numpy())[:, 1]
    keys = _key(rows, CELL)
    w = np.array([m["win"].get(k, 0.0) for k in keys]); l = np.array([m["loss"].get(k, 0.0) for k in keys])
    return p * w - (1 - p) * l > 0
