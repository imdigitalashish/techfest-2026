"""C7 Interval: CIs from per-round influence terms (baseline: Wald and percentile bootstrap)."""
from __future__ import annotations

import numpy as np
from scipy import stats

from architecture.contracts.contracts import Interval


def wald(phi: np.ndarray, level: float = 0.95) -> Interval:
    m, se = phi.mean(), phi.std(ddof=1) / np.sqrt(len(phi))
    z = stats.norm.ppf(0.5 + level / 2)
    return Interval(method="wald", level=level, point=float(m), lo=float(m - z * se), hi=float(m + z * se))


def bootstrap(phi: np.ndarray, level: float = 0.95, B: int = 1000, seed: int = 0) -> Interval:
    rng = np.random.default_rng(seed)
    n = len(phi)
    means = np.array([phi[rng.integers(0, n, n)].mean() for _ in range(B)])
    a = (1 - level) / 2
    return Interval(method="bootstrap-percentile", level=level, point=float(phi.mean()),
                    lo=float(np.quantile(means, a)), hi=float(np.quantile(means, 1 - a)))
