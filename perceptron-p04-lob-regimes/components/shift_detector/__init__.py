"""C6 Shift detectors.

RollingKS (the Minimum-Viable test): every `stride` steps, compare the last `window` steps of
each monitored raw feature (sub-sampled every `subsample` steps to weaken autocorrelation)
with a reference sample using the two-sample Kolmogorov-Smirnov test; Bonferroni across
features; an alarm needs `persist` consecutive rejections and is followed by a cooldown.
Label-free: it fires on *covariate* shift, whether or not the shift hurts the model.

PageHinkley on the deployed model's realised (delayed) log-loss: label-based, fires when
the *loss* drifts up — i.e. on harmful shift. Same recursion as River's PageHinkley
(mode='up'); see research/notes/shift-detection-sota.md.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import ks_2samp

from components.contracts import Alarm


class RollingKS:
    name = "rolling_ks"

    def __init__(self, ref: np.ndarray, feature_idx: list[int], feature_names: list[str],
                 window: int = 600, subsample: int = 10, stride: int = 30, alpha: float = 1e-3,
                 persist: int = 3, cooldown: int = 1800):
        self.ref = [np.sort(ref[:, k]) for k in range(ref.shape[1])]
        self.idx, self.names = feature_idx, feature_names
        self.window, self.subsample, self.stride = window, subsample, stride
        self.alpha, self.persist, self.cooldown = alpha, persist, cooldown
        self.hits, self.last_alarm = 0, -10**9
        self.last_p = np.ones(len(feature_idx))

    def update(self, t: int, X_raw: np.ndarray) -> Alarm | None:
        if t < self.window or t % self.stride:
            return None
        cur = X_raw[t - self.window + 1:t + 1:self.subsample][:, self.idx]
        p = np.array([ks_2samp(cur[:, k], self.ref[k], method="asymp").pvalue for k in range(len(self.idx))])
        self.last_p = p
        reject = p.min() * len(self.idx) < self.alpha
        self.hits = self.hits + 1 if reject else 0
        if self.hits >= self.persist and t - self.last_alarm >= self.cooldown:
            self.last_alarm, self.hits = t, 0
            k = int(p.argmin())
            return Alarm(t, self.name, float(p.min()), {"feature": self.names[k]})
        return None


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
