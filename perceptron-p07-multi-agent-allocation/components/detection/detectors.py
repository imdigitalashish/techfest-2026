"""C4 — Change detection on per-zone Poisson count streams.

PoissonCusum: two-sided CUSUM (Page 1954) for a multiplicative change of the rate by (1+delta)
up or 1/(1+delta) down, against a moving baseline expectation lam0 supplied by the forecaster.
Per step and zone, the log-likelihood ratio of a count k is
    up:   k*log(1+d) - lam0*d
    down: -k*log(1+d) + lam0*(1 - 1/(1+d))
S = max(0, S + llr); alarm when S > h. The onset estimate is the last step S was 0, and the
post-change rate MLE is (sum of counts since onset) / (sum of baseline shape since onset).
Cost: O(Z) per step. Hyper-parameters: delta (smallest change worth reacting to), h (threshold,
controls false-alarm rate ~ exp(h) steps per zone; UNVERIFIED rule of thumb, measured in eval).
"""
from __future__ import annotations

import numpy as np

from architecture.contracts.contracts import DetectorOutput


class PoissonCusum:
    def __init__(self, n_zones: int, delta: float = 1.0, h: float = 8.0):
        self.Z, self.delta, self.h = n_zones, float(delta), float(h)
        self.lg = np.log1p(self.delta)
        self.reset()

    def reset(self) -> None:
        Z = self.Z
        self.S_up, self.S_dn = np.zeros(Z), np.zeros(Z)
        self.start_up, self.start_dn = np.zeros(Z, dtype=np.int64), np.zeros(Z, dtype=np.int64)
        self.k_up, self.e_up = np.zeros(Z), np.zeros(Z)
        self.k_dn, self.e_dn = np.zeros(Z), np.zeros(Z)

    def update(self, t: int, k: np.ndarray, lam0: np.ndarray, shape: float | np.ndarray):
        """k: counts (Z,), lam0: expected counts under current level (Z,), shape: seasonal multiplier.
        Returns (DetectorOutput, post_change_level (Z,) — valid where alarm)."""
        lam0 = np.maximum(lam0, 1e-6)
        d, lg = self.delta, self.lg
        for side in ("up", "dn"):
            S = getattr(self, f"S_{side}")
            fresh = S <= 0
            getattr(self, f"k_{side}")[fresh] = 0.0
            getattr(self, f"e_{side}")[fresh] = 0.0
            getattr(self, f"start_{side}")[fresh] = t
            getattr(self, f"k_{side}")[:] += k
            getattr(self, f"e_{side}")[:] += shape
        self.S_up = np.maximum(0.0, self.S_up + k * lg - lam0 * d)
        self.S_dn = np.maximum(0.0, self.S_dn - k * lg + lam0 * (1 - 1 / (1 + d)))
        a_up, a_dn = self.S_up > self.h, self.S_dn > self.h
        alarm = a_up | a_dn
        level = np.where(a_up, self.k_up / np.maximum(self.e_up, 1e-9), self.k_dn / np.maximum(self.e_dn, 1e-9))
        start = np.where(a_up, self.start_up, np.where(a_dn, self.start_dn, -1))
        stat = np.maximum(self.S_up, self.S_dn)
        if alarm.any():
            for side in ("up", "dn"):
                getattr(self, f"S_{side}")[alarm] = 0.0
        return DetectorOutput(alarm=alarm, stat=stat, change_start=start), level
