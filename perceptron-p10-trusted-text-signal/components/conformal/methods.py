"""C8 conformal — calibrated intervals around the fusion model.

* split   : MAPIE SplitConformalRegressor (absolute residual around the median model), prefit.
* cqr     : MAPIE ConformalizedQuantileRegressor (Romano et al. 2019), prefit with the 3 quantile models.
* cqr_aci : our own ACI loop (Gibbs & Candes 2021; not MAPIE) on CQR scores, run online over test days;
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


def aci_from_bounds(cal_lb, cal_ub, y_cal, lb, ub, y, dates, alpha: float, gamma: float = 0.01,
                    stats: dict | None = None):
    """Adaptive Conformal Inference (Gibbs & Candes 2021) on CQR-type scores for any base bounds (lb, ub).

    One alpha_t per trading day, updated with that day's miss rate; scores of a day are revealed after the
    close. alpha_t is NOT clipped: alpha_t <= 0 gives the whole line, alpha_t >= 1 the empty set, so
    alpha_{T+1} = alpha_1 + gamma * sum_t (alpha - err_t) and alpha_t stays in [-gamma, 1 + gamma], which
    yields |mean_t err_t - alpha| <= (max(alpha_1, 1 - alpha_1) + gamma) / (gamma * T)  (tests/).
    Endpoints are never reordered: lo > hi means the empty interval (a miss). Returns (lo, hi).
    """
    pool = list(np.maximum(cal_lb - y_cal, y_cal - cal_ub))
    lo, hi = np.empty(len(y)), np.empty(len(y))
    a_t = alpha
    st = {"days": 0, "alpha_le0_days": 0, "alpha_ge1_days": 0, "neg_q_days": 0, "empty_rows": 0,
          "alpha_min": alpha, "alpha_max": alpha, "day_err": []}
    s_all = np.maximum(lb - y, y - ub)
    for d in np.unique(dates):
        idx = np.flatnonzero(dates == d)
        if a_t <= 0:
            q = np.inf
            st["alpha_le0_days"] += 1
        elif a_t >= 1:
            q = -np.inf
            st["alpha_ge1_days"] += 1
        else:
            q = conformal_quantile(np.asarray(pool), a_t)
        st["neg_q_days"] += int(q < 0)
        lo[idx], hi[idx] = lb[idx] - q, ub[idx] + q
        covered = (y[idx] >= lo[idx]) & (y[idx] <= hi[idx])
        st["empty_rows"] += int(np.sum(lo[idx] > hi[idx]))
        err = 1.0 - float(covered.mean())
        st["day_err"].append(err)
        a_t = a_t + gamma * (alpha - err)
        st["alpha_min"], st["alpha_max"] = min(st["alpha_min"], a_t), max(st["alpha_max"], a_t)
        st["days"] += 1
        pool.extend(s_all[idx].tolist())
    if stats is not None:
        stats.update({k: v for k, v in st.items() if k != "day_err"})
        stats["mean_day_err"] = float(np.mean(st["day_err"]))
        stats["aci_bound"] = float((max(alpha, 1 - alpha) + gamma) / (gamma * st["days"]))
    return lo, hi


def cqr_aci(model: QuantileFusion, cal: pd.DataFrame, test: pd.DataFrame, gamma: float = 0.01,
            stats: dict | None = None) -> pd.DataFrame:
    pc, pt = model.predict(cal), model.predict(test)
    lb_c, ub_c = np.minimum(pc.q_lo, pc.q_hi).to_numpy(), np.maximum(pc.q_lo, pc.q_hi).to_numpy()
    lb, ub = np.minimum(pt.q_lo, pt.q_hi).to_numpy(), np.maximum(pt.q_lo, pt.q_hi).to_numpy()
    lo, hi = aci_from_bounds(lb_c, ub_c, cal["y"].to_numpy(float), lb, ub, test["y"].to_numpy(float),
                             test["trade_date"].to_numpy(), model.alpha, gamma, stats)
    return _frame(test, lo, hi, pt["q_med"].to_numpy(), "cqr_aci")
