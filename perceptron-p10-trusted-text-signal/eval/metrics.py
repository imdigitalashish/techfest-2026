"""FROZEN evaluator metrics (do not edit inside ratchet loops). Interval-forecast quality.

coverage, mean width, Winkler interval score (Gneiting & Raftery 2007), Kupiec (1995) POF test,
Christoffersen (1998) independence test (pooled first-order Markov transitions per ticker),
and coverage by group (regime). Pooled p-values ignore cross-sectional dependence of misses on
the same day, so they are optimistic; we therefore also report mean daily coverage with a 90%
day-block bootstrap CI (date-cluster inference; added 4 Oct 13:00 after the independent review).
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


def day_block_ci(x: np.ndarray, block: int = 5, b: int = 2000, seed: int = 0) -> list[float]:
    """90% percentile CI of the mean of a daily series via circular moving-block bootstrap over days."""
    n = len(x)
    if n < 2:
        return [float("nan"), float("nan")]
    rng = np.random.default_rng(seed)
    nb = int(np.ceil(n / block))
    idx = (rng.integers(0, n, size=(b, nb))[:, :, None] + np.arange(block)).reshape(b, -1)[:, :n] % n
    m = x[idx].mean(1)
    return [float(np.quantile(m, 0.05)), float(np.quantile(m, 0.95))]


def evaluate(iv: pd.DataFrame, truth: pd.DataFrame, alpha: float, groups: dict[str, pd.Series] | None = None) -> dict:
    """lo > hi is the empty interval (always a miss, width 0); infinite bounds are allowed (v1, 4 Oct 10:00).

    Width statistics are over finite-width rows; `frac_infinite` reports the rest."""
    d = iv.merge(truth[["ticker", "trade_date", "y"]], on=["ticker", "trade_date"], how="inner")
    y, lo, hi = d["y"].to_numpy(), d["lo"].to_numpy(), d["hi"].to_numpy()
    d["miss"] = (~((y >= lo) & (y <= hi))).astype(int)
    w = np.maximum(hi - lo, 0.0)
    fin = np.isfinite(w)
    lo_w, hi_w = np.where(fin, lo, 0.0), np.where(fin, np.maximum(hi, lo), 0.0)
    day_cov = 1 - d.groupby("trade_date")["miss"].mean()
    out = {"n": int(len(d)), "coverage": float(1 - d["miss"].mean()), "mean_width": float(np.mean(w[fin])),
           "median_width": float(np.median(w[fin])), "frac_infinite": float(1 - fin.mean()),
           "winkler": winkler(y[fin], lo_w[fin], hi_w[fin], alpha),
           "kupiec_p": kupiec_pof(d["miss"].to_numpy(), alpha), "christoffersen_p": christoffersen_ind(d),
           "worst_day_coverage": float(day_cov.min()), "day_coverage_p10": float(day_cov.quantile(0.10)),
           "n_days": int(len(day_cov)), "mean_day_coverage": float(day_cov.mean()),
           "mean_day_coverage_ci90": day_block_ci(day_cov.sort_index().to_numpy())}
    if groups:
        key = d.set_index(["ticker", "trade_date"]).index
        for gname, gser in groups.items():
            lab = gser.reindex(key).to_numpy()
            for v in pd.unique(lab[~pd.isna(lab)]):
                m = lab == v
                out[f"cov[{gname}={v}]"] = float(1 - d["miss"].to_numpy()[m].mean())
                out[f"width[{gname}={v}]"] = float(np.mean(w[m & fin]))
    return out
