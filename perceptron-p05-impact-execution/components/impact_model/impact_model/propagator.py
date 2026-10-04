"""Own-impact model: discrete propagator with an exponential transient part plus a permanent part.

    I(t) = sum_{t_i <= t} q_i * (g_perm + g_tr * exp(-(t - t_i)/tau))      [cents; q_i in shares]

Fitted on twin-measured impact paths (treatment mid minus null-twin mid, same seed), which
removes the exogenous price drift from the regression target. For fixed tau the model is
linear in (g_perm, g_tr); tau is chosen by grid search. Points are weighted by 1/var(t)
because twin divergence grows with time.
"""
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import numpy as np


def _features(fills_s: Sequence[Tuple[float, float]], grid_s: np.ndarray, tau: float) -> np.ndarray:
    X = np.zeros((len(grid_s), 2))
    for t, q in fills_s:
        lag = grid_s - t
        on = lag >= 0
        X[on, 0] += q
        X[on, 1] += q * np.exp(-lag[on] / tau)
    return X


def predict_own_impact(fills_s, grid_s, params: Dict) -> np.ndarray:
    X = _features(fills_s, np.asarray(grid_s, float), params["tau_s"])
    return X @ np.array([params["g_perm"], params["g_tr"]])


def fit_exp_propagator(episodes: List[Dict], taus=(15, 30, 60, 90, 120, 180, 240, 300, 450, 600, 900)) -> Dict:
    """episodes: [{fills_s: [(t_s, qty)], grid_s: array, path: array (cents, + = adverse)}]."""
    Y = np.array([e["path"] for e in episodes], dtype=float)
    var = np.nanvar(Y, axis=0) + 1.0
    best = None
    for tau in taus:
        XtX = np.zeros((2, 2))
        Xty = np.zeros(2)
        for e in episodes:
            X = _features(e["fills_s"], e["grid_s"], tau)
            y = np.asarray(e["path"], float)
            ok = ~np.isnan(y)
            w = 1.0 / var[ok]
            XtX += (X[ok] * w[:, None]).T @ X[ok]
            Xty += (X[ok] * w[:, None]).T @ y[ok]
        beta = np.linalg.solve(XtX + 1e-9 * np.eye(2), Xty)
        sse = 0.0
        for e in episodes:
            X = _features(e["fills_s"], e["grid_s"], tau)
            y = np.asarray(e["path"], float)
            ok = ~np.isnan(y)
            sse += float((((y[ok] - X[ok] @ beta) ** 2) / var[ok]).sum())
        if best is None or sse < best["wsse"]:
            best = dict(tau_s=float(tau), g_perm=float(beta[0]), g_tr=float(beta[1]), wsse=sse)
    return best


def r2_on(episodes: List[Dict], params: Dict, upto_s: float) -> Dict:
    """Out-of-sample fit of the mean impact path (seed-averaged) and of per-seed paths."""
    ys, ps = [], []
    for e in episodes:
        g = np.asarray(e["grid_s"], float)
        m = g <= upto_s
        ys.append(np.asarray(e["path"], float)[m])
        ps.append(predict_own_impact(e["fills_s"], g[m], params))
    Y, P = np.array(ys), np.array(ps)
    ym, pm = np.nanmean(Y, 0), P.mean(0)
    r2_mean = 1 - np.nansum((ym - pm) ** 2) / np.nansum((ym - np.nanmean(ym)) ** 2)
    r2_seed = 1 - np.nansum((Y - P) ** 2) / np.nansum((Y - np.nanmean(Y)) ** 2)
    return dict(r2_mean_path=float(r2_mean), r2_per_seed=float(r2_seed),
                rmse_per_seed_cents=float(np.sqrt(np.nanmean((Y - P) ** 2))))
