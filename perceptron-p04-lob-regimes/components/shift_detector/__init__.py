"""C6 Shift detectors.

RollingKS (the Minimum-Viable test): every `stride` steps, compare the last `window` steps of
each monitored raw feature (sub-sampled every `subsample` steps to weaken autocorrelation)
with a reference sample using the two-sample Kolmogorov-Smirnov test; Bonferroni across
features; an alarm needs `persist` consecutive rejections and is followed by a cooldown.
Label-free: it fires on *covariate* shift, whether or not the shift hurts the model.

PageHinkley on the deployed model's realised (delayed) log-loss: label-based, fires when
the *loss* drifts up — i.e. on harmful shift. Same recursion as River's PageHinkley
(mode='up'); see research/notes/shift-detection-sota.md.

HarmCUSUM (the spike's harm gate): one-sided CUSUM on the deployed forecast's delayed log-loss
in excess of ln 2 — the loss of the coin-flip forecast p = 0.5. It accumulates evidence only
while the deployed model is doing *worse than abstaining*, the operational meaning of a
harmful shift (cf. Podkopaev & Ramdas 2022, risk tracking of a deployed model). O(1) per label.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import distributions, ks_2samp

from components.contracts import Alarm

LN2 = float(np.log(2.0))


def ks_stat_sorted(cur: np.ndarray, ref_sorted: np.ndarray) -> float:
    """Two-sample KS distance D between `cur` and an already-sorted reference, O(m log n).

    Equal to scipy.stats.ks_2samp(cur, ref).statistic (ties included): the supremum of
    |F_cur - F_ref| over the pooled sample is attained either at a value u of `cur` (right
    limits) or just below one (left limits), so only m unique points need evaluating.
    """
    c = np.sort(cur)
    u = np.unique(c)
    m, n = c.shape[0], ref_sorted.shape[0]
    fc_at = np.searchsorted(c, u, side="right") / m
    fc_bef = np.searchsorted(c, u, side="left") / m
    fr_at = np.searchsorted(ref_sorted, u, side="right") / n
    fr_bef = np.searchsorted(ref_sorted, u, side="left") / n
    return float(max(np.abs(fc_at - fr_at).max(), np.abs(fc_bef - fr_bef).max()))


def ks_pvalue_asymp(d: float, n1: int, n2: int) -> float:
    """Two-sided p-value exactly as scipy.stats.ks_2samp(method='asymp') computes it (SciPy 1.17)."""
    m, n = sorted([float(n1), float(n2)], reverse=True)
    return float(np.clip(distributions.kstwo.sf(d, np.round(m * n / (m + n))), 0, 1))


class RollingKS:
    name = "rolling_ks"

    def __init__(self, ref: np.ndarray, feature_idx: list[int], feature_names: list[str],
                 window: int = 600, subsample: int = 10, stride: int = 30, alpha: float = 1e-3,
                 persist: int = 3, cooldown: int = 1800, thresholds: np.ndarray | None = None):
        self.ref = [np.sort(ref[:, k]) for k in range(ref.shape[1])]
        self.idx, self.names = feature_idx, feature_names
        self.window, self.subsample, self.stride = window, subsample, stride
        self.alpha, self.persist, self.cooldown = alpha, persist, cooldown
        self.thresholds = thresholds  # per-feature critical D from an empirical null (calibrated mode)
        if thresholds is not None:
            self.name = "rolling_ks_calibrated"
        self.hits, self.last_alarm = 0, -10**9
        self.last_p = np.ones(len(feature_idx))

    def update(self, t: int, X_raw: np.ndarray) -> Alarm | None:
        if t < self.window or t % self.stride:
            return None
        cur = X_raw[t - self.window + 1:t + 1:self.subsample][:, self.idx]
        if self.thresholds is None:
            m = cur.shape[0]
            p = np.array([ks_pvalue_asymp(ks_stat_sorted(cur[:, k], self.ref[k]), m, self.ref[k].shape[0])
                          for k in range(len(self.idx))])
            self.last_p = p
            reject, k, stat = p.min() * len(self.idx) < self.alpha, int(p.argmin()), float(p.min())
        else:
            ratio = np.array([ks_stat_sorted(cur[:, k], self.ref[k]) for k in range(len(self.idx))]) / self.thresholds
            reject, k, stat = bool(ratio.max() > 1.0), int(ratio.argmax()), float(ratio.max())
        self.hits = self.hits + 1 if reject else 0
        if self.hits >= self.persist and t - self.last_alarm >= self.cooldown:
            self.last_alarm, self.hits = t, 0
            return Alarm(t, self.name, stat, {"feature": self.names[k]})
        return None


def calibrate_ks_null(days_X: list[np.ndarray], feature_idx: list[int], window: int, subsample: int,
                      stride: int, quantile: float) -> np.ndarray:
    """Empirical null for the windowed KS statistic, leave-one-day-out over training days.

    For each training day, windows of that day are compared with a reference built from the
    *other* training days, so the null contains real autocorrelation, intraday seasonality and
    day-to-day variation — everything the i.i.d. p-value ignores. Returns per-feature critical D.
    """
    D = [[] for _ in feature_idx]
    for i, Xi in enumerate(days_X):
        ref = np.vstack([Xj for j, Xj in enumerate(days_X) if j != i])[::subsample][:, feature_idx]
        ref = [np.sort(ref[:, k]) for k in range(len(feature_idx))]
        for t in range(window, Xi.shape[0], stride):
            cur = Xi[t - window + 1:t + 1:subsample][:, feature_idx]
            for k in range(len(feature_idx)):
                D[k].append(ks_stat_sorted(cur[:, k], ref[k]))
    return np.array([np.quantile(d, quantile) for d in D])


class PageHinkley:
    name = "page_hinkley_loss"

    def __init__(self, delta: float = 0.005, threshold: float = 25.0, min_n: int = 300, alpha: float = 1 - 1e-4):
        self.delta, self.threshold, self.min_n, self.alpha = delta, threshold, min_n, alpha
        self.reset()

    def reset(self) -> None:
        self.n, self.mean, self.m, self.m_min = 0, 0.0, 0.0, 0.0

    def update(self, t: int, x: float) -> Alarm | None:
        self.n += 1
        self.mean += (x - self.mean) / self.n
        self.m = self.alpha * self.m + (x - self.mean - self.delta)
        self.m_min = min(self.m_min, self.m)
        if self.n >= self.min_n and self.m - self.m_min > self.threshold:
            stat = self.m - self.m_min
            self.reset()
            return Alarm(t, self.name, float(stat))
        return None


class HarmCUSUM:
    """S_t = max(0, S_{t-1} + loss_t - ln2 - k); alarm when S_t > threshold (then reset + cooldown)."""

    name = "harm_cusum"

    def __init__(self, k: float = 0.0, threshold: float = 5.0, min_n: int = 60, cooldown: int = 600):
        self.k, self.threshold, self.min_n, self.cooldown = k, threshold, min_n, cooldown
        self.s, self.n, self.last_alarm = 0.0, 0, -10**9

    def update(self, t: int, loss: float) -> Alarm | None:
        self.n += 1
        self.s = max(0.0, self.s + loss - LN2 - self.k)
        if self.n >= self.min_n and self.s > self.threshold and t - self.last_alarm >= self.cooldown:
            stat, self.s, self.last_alarm = self.s, 0.0, t
            return Alarm(t, self.name, float(stat))
        return None
