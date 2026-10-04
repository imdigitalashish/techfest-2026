"""C8 conformal — calibrated intervals around the fusion model.

* split   : MAPIE SplitConformalRegressor (absolute residual around the median model), prefit.
* cqr     : MAPIE ConformalizedQuantileRegressor (Romano et al. 2019), prefit with the 3 quantile models.
* cqr_aci : CQR scores + Adaptive Conformal Inference (Gibbs & Candes 2021) run online over test days;
            panel version: one alpha_t per day, updated with that day's average miscoverage.
Isolated metric: |coverage - (1-alpha)| and mean width on the time-ordered test period.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from mapie.regression import ConformalizedQuantileRegressor, SplitConformalRegressor

from architecture.contracts.contracts import INTERVALS, validate
from components.fusion.lgbm_quantile import QuantileFusion


def _frame(df, lo, hi, point, method):
    out = pd.DataFrame({"ticker": df["ticker"].values, "trade_date": df["trade_date"].values,
                        "lo": np.asarray(lo, float), "hi": np.asarray(hi, float), "point": np.asarray(point, float),
                        "method": method})
    return validate(out, INTERVALS)


def split_cp(model: QuantileFusion, cal: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    scr = SplitConformalRegressor(estimator=model.models[1], confidence_level=1 - model.alpha, prefit=True)
    scr.conformalize(cal[model.cols].to_numpy(float), cal["y"].to_numpy(float))
    point, iv = scr.predict_interval(test[model.cols].to_numpy(float))
    return _frame(test, iv[:, 0, 0], iv[:, 1, 0], point, "split")


def cqr(model: QuantileFusion, cal: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    c = ConformalizedQuantileRegressor(estimator=model.mapie_estimators(), confidence_level=1 - model.alpha, prefit=True)
    c.conformalize(cal[model.cols].to_numpy(float), cal["y"].to_numpy(float))
    point, iv = c.predict_interval(test[model.cols].to_numpy(float))
    return _frame(test, iv[:, 0, 0], iv[:, 1, 0], point, "cqr")


def cqr_scores(pred: pd.DataFrame, y: np.ndarray) -> np.ndarray:
    return np.maximum(pred["q_lo"].to_numpy() - y, y - pred["q_hi"].to_numpy())


def conformal_quantile(scores: np.ndarray, alpha: float) -> float:
    n = len(scores)
    if alpha <= 0:
        return np.inf
    if alpha >= 1:
        return -np.inf
    k = int(np.ceil((n + 1) * (1 - alpha)))
    return np.inf if k > n else float(np.sort(scores)[k - 1])


def cqr_offset(model: QuantileFusion, cal: pd.DataFrame) -> float:
    """Split-CQR correction Q (same rule MAPIE uses), exposed for the certified spike."""
    return conformal_quantile(cqr_scores(model.predict(cal), cal["y"].to_numpy(float)), model.alpha)


def aci_from_bounds(cal_lb, cal_ub, y_cal, lb, ub, y, dates, alpha: float, gamma: float = 0.01):
    """ACI (Gibbs & Candes 2021) on CQR-type scores for any per-row base bounds (lb, ub).

    One alpha_t per trading day; scores of a day are revealed after it closes. Returns (lo, hi).
    """
    pool = list(np.maximum(cal_lb - y_cal, y_cal - cal_ub))
    s = np.maximum(lb - y, y - ub)
    lo, hi = np.empty(len(y)), np.empty(len(y))
    a_t = alpha
    for d in np.unique(dates):
        idx = np.flatnonzero(dates == d)
        ref = np.asarray(pool)
        q = conformal_quantile(ref, a_t)
        q = np.nanmax(ref) * 3 if not np.isfinite(q) and q > 0 else q
        lo[idx], hi[idx] = lb[idx] - q, ub[idx] + q
        a_t = float(np.clip(a_t + gamma * (alpha - np.mean(s[idx] > q)), 0.0, 1.0))
        pool.extend(s[idx].tolist())
    return np.minimum(lo, hi), np.maximum(lo, hi)


def cqr_aci(model: QuantileFusion, cal: pd.DataFrame, test: pd.DataFrame, gamma: float = 0.01,
            window: int | None = None) -> pd.DataFrame:
    alpha = model.alpha
    pool = list(cqr_scores(model.predict(cal), cal["y"].to_numpy(float)))
    pred = model.predict(test)
    y = test["y"].to_numpy(float)
    s_test = cqr_scores(pred, y)
    lo, hi = np.empty(len(test)), np.empty(len(test))
    a_t = alpha
    dates = test["trade_date"].to_numpy()
    for d in np.unique(dates):
        idx = np.flatnonzero(dates == d)
        ref = np.asarray(pool[-window:] if window else pool)
        q = conformal_quantile(ref, a_t)
        q = np.nanmax(ref) * 3 if not np.isfinite(q) and q > 0 else q
        lo[idx] = pred["q_lo"].to_numpy()[idx] - q
        hi[idx] = pred["q_hi"].to_numpy()[idx] + q
        err = np.mean(s_test[idx] > q)
        a_t = float(np.clip(a_t + gamma * (alpha - err), 0.0, 1.0))
        pool.extend(s_test[idx].tolist())  # revealed after the day closes
    lo, hi = np.minimum(lo, hi), np.maximum(lo, hi)
    return _frame(test, lo, hi, pred["q_med"].to_numpy(), "cqr_aci")
