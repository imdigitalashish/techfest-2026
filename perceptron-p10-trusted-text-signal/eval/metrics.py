"""FROZEN evaluator metrics (do not edit inside ratchet loops). Interval-forecast quality.

coverage, mean width, Winkler interval score (Gneiting & Raftery 2007), Kupiec (1995) POF test,
Christoffersen (1998) independence test (pooled first-order Markov transitions per ticker),
and coverage by group (regime). Pooled p-values ignore cross-sectional dependence of misses on
the same day, so they are optimistic; we also report day-level coverage dispersion.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chi2


def winkler(y, lo, hi, alpha):
    w = hi - lo
    return float(np.mean(w + (2 / alpha) * (lo - y) * (y < lo) + (2 / alpha) * (y - hi) * (y > hi)))


def kupiec_pof(miss: np.ndarray, alpha: float) -> float:
    n, x = len(miss), int(miss.sum())
    p_hat = x / n
    if x in (0, n):
        ll1 = 0.0
    else:
        ll1 = (n - x) * np.log(1 - p_hat) + x * np.log(p_hat)
    ll0 = (n - x) * np.log(1 - alpha) + x * np.log(alpha)
    return float(chi2.sf(-2 * (ll0 - ll1), 1))


def christoffersen_ind(df: pd.DataFrame) -> float:
    n = np.zeros((2, 2))
    for _, g in df.sort_values("trade_date").groupby("ticker"):
        m = g["miss"].to_numpy(int)
        if len(m) > 1:
            np.add.at(n, (m[:-1], m[1:]), 1)
    n00, n01, n10, n11 = n[0, 0], n[0, 1], n[1, 0], n[1, 1]
    p01 = n01 / max(n00 + n01, 1)
    p11 = n11 / max(n10 + n11, 1)
    p = (n01 + n11) / max(n.sum(), 1)

    def ll(a, b, q):
        q = min(max(q, 1e-12), 1 - 1e-12)
        return a * np.log(1 - q) + b * np.log(q)

    lr = -2 * (ll(n00 + n10, n01 + n11, p) - ll(n00, n01, p01) - ll(n10, n11, p11))
    return float(chi2.sf(lr, 1))


def evaluate(iv: pd.DataFrame, truth: pd.DataFrame, alpha: float, groups: dict[str, pd.Series] | None = None) -> dict:
    d = iv.merge(truth[["ticker", "trade_date", "y"]], on=["ticker", "trade_date"], how="inner")
    y, lo, hi = d["y"].to_numpy(), d["lo"].to_numpy(), d["hi"].to_numpy()
    d["miss"] = ((y < lo) | (y > hi)).astype(int)
    day_cov = 1 - d.groupby("trade_date")["miss"].mean()
    out = {"n": int(len(d)), "coverage": float(1 - d["miss"].mean()), "mean_width": float(np.mean(hi - lo)),
           "median_width": float(np.median(hi - lo)), "winkler": winkler(y, lo, hi, alpha),
           "kupiec_p": kupiec_pof(d["miss"].to_numpy(), alpha), "christoffersen_p": christoffersen_ind(d),
           "worst_day_coverage": float(day_cov.min()), "day_coverage_p10": float(day_cov.quantile(0.10))}
    if groups:
        key = d.set_index(["ticker", "trade_date"]).index
        for gname, gser in groups.items():
            lab = gser.reindex(key).to_numpy()
            for v in pd.unique(lab[~pd.isna(lab)]):
                m = lab == v
                out[f"cov[{gname}={v}]"] = float(1 - d["miss"].to_numpy()[m].mean())
                out[f"width[{gname}={v}]"] = float(np.mean((hi - lo)[m]))
    return out
