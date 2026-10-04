"""C10 SPIKE — certified manipulation-robust conformal intervals (CR-CQR).

Threat model: an adversary may inject up to k documents (any text, any metadata) into a ticker-day.
Prices are not manipulable. Defender sees only the observed (possibly attacked) set D'.
Because the clean set D is D' minus at most k documents, the clean feature vector lies in
  B_k(D') = { features(D' \\ S) : |S| <= k }.
We over-approximate B_k by a per-feature box (exact per-feature ranges; see `deletion_box`), bound
each LightGBM quantile model over that box by interval propagation through every tree (sound:
min of a sum >= sum of per-tree minima), and return [LB - Q, UB + Q], where Q is the clean
split-CQR correction. Guarantee: whenever the clean CQR interval would cover y, the certified
interval covers y, for every attack within budget k; so coverage >= 1 - alpha under exchangeability
of clean calibration/test data. Width is the price of robustness and is what the ratchet loop shrinks.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from components.fusion.lgbm_quantile import TEXT_COLS, QuantileFusion

TRIM = 0.2  # must match components/aggregator/aggregate.py
U = np.finfo(float).eps / 2  # unit round-off, 2**-53
ABS_EPS = 1e-12  # covers the aggregator's own rounding (pairwise sums; < 1e-14 for n <= MAX_DOCS)
MAX_DOCS = 1_000_000  # the round-off budget below is derived for n <= MAX_DOCS documents per ticker-day


def _trim_sorted(s: np.ndarray) -> float:
    n = len(s)
    if n == 0:
        return 0.0
    c = int(TRIM * n)
    return float(s[c:n - c].mean())


def features_from_docs(s: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Text features in TEXT_COLS order from per-doc sentiment s and trust w (same rules as the aggregator)."""
    n = len(s)
    if n == 0:
        return np.zeros(len(TEXT_COLS))
    ss = np.sort(s)
    return np.array([np.log1p(n), ss.mean(), _trim_sorted(ss), ss.std() if n > 1 else 0.0, np.mean(w)])


def deletion_box(s: np.ndarray, w: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Per-feature [lo, hi] of TEXT_COLS containing every deletion of at most k documents.

    Exact in real arithmetic: mean / trimmed mean are monotone order-statistic functionals (extremes at the m
    smallest / largest); the min-variance m-subset is contiguous in sorted order and the max-variance m-subset is a
    prefix plus a suffix (exchange arguments in research/components/robust_conformal.md).
    Floating point (fix for gpt-6-sol review B2): sums are taken after centring at the median, so clustered values
    do not cancel, and each bound is widened by a round-off budget from the recursive-summation bound
    |fl(sum) - sum| <= (n-1) u sum|x_i| (Higham 2002, Thm 4.2 form): every combination uses <= 3 prefix sums, giving
    |delta var| <= (12 n^2/m + 8) u X^2 with X = max|x_i|, and the same factor times (1 + max|s|) for mean-like
    features; ABS_EPS covers the aggregator's own (pairwise) rounding. Valid for n <= MAX_DOCS.
    """
    n = len(s)
    if n > MAX_DOCS:
        raise ValueError(f"deletion_box: {n} documents exceeds MAX_DOCS={MAX_DOCS} (round-off budget not derived)")
    ss, ws = np.sort(np.asarray(s, float)), np.sort(np.asarray(w, float))
    c = float(ss[n // 2]) if n else 0.0
    x = ss - c
    X = float(np.max(np.abs(x))) if n else 0.0
    S = 1.0 + (float(np.max(np.abs(ss))) if n else 0.0)
    cs = np.concatenate([[0.0], np.cumsum(x)])
    cq = np.concatenate([[0.0], np.cumsum(x * x)])
    cw = np.concatenate([[0.0], np.cumsum(ws)])
    lo = np.full(len(TEXT_COLS), np.inf)
    hi = np.full(len(TEXT_COLS), -np.inf)
    for j in range(0, min(k, n) + 1):
        m = n - j
        if m == 0:
            f_lo = f_hi = np.zeros(len(TEXT_COLS))
        else:
            g = (12.0 * n * n / m + 8.0) * U
            e1 = g * S + ABS_EPS
            mean_lo, mean_hi = c + cs[m] / m, c + (cs[n] - cs[j]) / m
            trim_lo, trim_hi = _trim_sorted(ss[:m]), _trim_sorted(ss[j:])
            if m > 1:
                i = np.arange(j + 1)  # contiguous windows (min variance)
                v_min = (cq[i + m] - cq[i]) / m - ((cs[i + m] - cs[i]) / m) ** 2
                p = np.arange(m + 1)  # prefix + suffix (max variance)
                s2, q2 = cs[p] + cs[n] - cs[p + j], cq[p] + cq[n] - cq[p + j]
                v_max = q2 / m - (s2 / m) ** 2
                dv = g * X * X
                std_min = float(np.sqrt(max(v_min.min() - dv, 0.0))) - ABS_EPS
                std_max = float(np.sqrt(max(v_max.max(), 0.0) + dv)) + ABS_EPS
            else:
                std_min, std_max = -ABS_EPS, ABS_EPS
            tr_lo, tr_hi = cw[m] / m, (cw[n] - cw[j]) / m
            f_lo = np.array([np.log1p(m), mean_lo - e1, trim_lo - e1, std_min, tr_lo - e1])
            f_hi = np.array([np.log1p(m), mean_hi + e1, trim_hi + e1, std_max, tr_hi + e1])
        lo, hi = np.minimum(lo, f_lo), np.maximum(hi, f_hi)
    return lo, hi


def _tree_bounds(node: dict, lo: np.ndarray, hi: np.ndarray, reach: np.ndarray, out_min: np.ndarray, out_max: np.ndarray):
    if "leaf_value" in node:
        v = node["leaf_value"]
        np.minimum(out_min, np.where(reach, v, np.inf), out=out_min)
        np.maximum(out_max, np.where(reach, v, -np.inf), out=out_max)
        return
    assert node.get("decision_type", "<=") == "<=", "only numerical splits supported"
    # inputs are finite (enforced in CertifiedCQR.boxes), so LightGBM's missing-value routing never applies
    f, t = node["split_feature"], node["threshold"]
    left = reach & (lo[:, f] <= t)
    right = reach & (hi[:, f] > t)
    if left.any():
        _tree_bounds(node["left_child"], lo, hi, left, out_min, out_max)
    if right.any():
        _tree_bounds(node["right_child"], lo, hi, right, out_min, out_max)


def ensemble_bounds(booster_dump: dict, lo: np.ndarray, hi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Sound lower/upper bounds of a LightGBM regressor over axis-aligned boxes [lo, hi] (rows x features)."""
    n = lo.shape[0]
    tot_min, tot_max = np.zeros(n), np.zeros(n)
    for tree in booster_dump["tree_info"]:
        mn, mx = np.full(n, np.inf), np.full(n, -np.inf)
        _tree_bounds(tree["tree_structure"], lo, hi, np.ones(n, bool), mn, mx)
        tot_min += mn
        tot_max += mx
    return tot_min, tot_max


class CertifiedCQR:
    def __init__(self, model: QuantileFusion, q_offset: float, k: int):
        self.model, self.Q, self.k = model, q_offset, k
        self.dumps = [m.booster_.dump_model() for m in model.models]
        feats = [c for c in TEXT_COLS if c in model.cols]
        self.text_idx = [model.cols.index(c) for c in feats]
        self.text_sel = [TEXT_COLS.index(c) for c in feats]

    def boxes(self, X: np.ndarray, docs: list[tuple[np.ndarray, np.ndarray]]) -> tuple[np.ndarray, np.ndarray]:
        if not np.isfinite(X).all():
            raise ValueError("certificate requires finite features (no NaN/inf)")
        lo, hi = X.copy(), X.copy()
        if self.text_idx:
            for r, (s, w) in enumerate(docs):
                b_lo, b_hi = deletion_box(s, w, self.k)
                lo[r, self.text_idx], hi[r, self.text_idx] = b_lo[self.text_sel], b_hi[self.text_sel]
        return lo, hi

    def raw_bounds(self, X: np.ndarray, docs: list[tuple[np.ndarray, np.ndarray]]) -> tuple[np.ndarray, np.ndarray]:
        """[min over box of min(q_lo, q_hi), max over box of max(q_lo, q_hi)] before the conformal offset."""
        lo_box, hi_box = self.boxes(X, docs)
        (l_min, l_max), _, (h_min, h_max) = (ensemble_bounds(d, lo_box, hi_box) for d in self.dumps)
        return np.minimum(l_min, h_min), np.maximum(l_max, h_max)

    def intervals(self, X: np.ndarray, docs: list[tuple[np.ndarray, np.ndarray]]) -> tuple[np.ndarray, np.ndarray]:
        lb, ub = self.raw_bounds(X, docs)
        return lb - self.Q, ub + self.Q


def docs_lookup(docs_scored: pd.DataFrame, rows: pd.DataFrame) -> list[tuple[np.ndarray, np.ndarray]]:
    g = {key: (grp["sentiment"].to_numpy(float), grp["trust"].to_numpy(float))
         for key, grp in docs_scored.groupby(["ticker", "trade_date"], sort=False)}
    empty = (np.zeros(0), np.zeros(0))
    return [g.get((t, d), empty) for t, d in zip(rows["ticker"].values, pd.to_datetime(rows["trade_date"]).values)]
