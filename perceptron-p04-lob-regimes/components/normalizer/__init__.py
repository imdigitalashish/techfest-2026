"""C4 Normalizer: raw features -> standardised features.

StaticNorm: z-score with statistics frozen on the training days (the classic deployment).
EWMANorm: label-free online standardisation (exponentially weighted mean/variance, causal:
z_t uses statistics up to t-1, then the statistics absorb x_t). It is the streaming analogue
of adaptive input normalisation (DAIN, RevIN) and removes slow scale drift (volatility,
depth) without any labels — the cheapest form of adaptation.
"""
from __future__ import annotations

import numba
import numpy as np

CLIP = 8.0


class StaticNorm:
    def __init__(self, mu: np.ndarray, sd: np.ndarray):
        self.mu, self.sd = mu, np.where(sd > 1e-12, sd, 1.0)

    @classmethod
    def fit(cls, X: np.ndarray) -> "StaticNorm":
        return cls(np.nanmean(X, 0), np.nanstd(X, 0))

    def transform(self, X: np.ndarray) -> np.ndarray:
        return np.clip((X - self.mu) / self.sd, -CLIP, CLIP)


@numba.njit(cache=True)
def _ewma_z(X, mu0, var0, a):
    T, d = X.shape
    Z = np.empty_like(X)
    mu = mu0.copy()
    var = var0.copy()
    for t in range(T):
        for k in range(d):
            x = X[t, k]
            s = np.sqrt(var[k]) if var[k] > 1e-24 else 1.0
            z = (x - mu[k]) / s
            Z[t, k] = min(max(z, -CLIP), CLIP)
            dlt = x - mu[k]
            mu[k] += a * dlt
            var[k] = (1.0 - a) * (var[k] + a * dlt * dlt)
    return Z


class EWMANorm:
    def __init__(self, mu0: np.ndarray, var0: np.ndarray, halflife_steps: float):
        self.mu0, self.var0 = mu0.astype(np.float64), var0.astype(np.float64)
        self.a = 1.0 - 0.5 ** (1.0 / halflife_steps)

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Causal pass over a day; every episode starts from the training statistics."""
        return _ewma_z(np.ascontiguousarray(X, dtype=np.float64), self.mu0, self.var0, self.a)
