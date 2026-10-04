"""C8 Sensitivity (spike, v0): marginal sensitivity model (MSM) bounds for a Hajek-IPW policy value.

MSM with parameter Gamma >= 1 (Tan 2006; used for IPW by Zhao, Small & Bhattacharya, arXiv:1711.11286, and for
policies by Kallus & Zhou, arXiv:1805.08593): the true propensity e* of each logged action satisfies
1/Gamma <= odds(e*)/odds(e) <= Gamma, where e is the logged (nominal) propensity. Equivalently, the inverse weight
1/e* lies in [1 + (1/e - 1)/Gamma, 1 + Gamma*(1/e - 1)]. The extreme Hajek values over that box are attained
at a threshold in the reward order (linear-fractional programme), found with cumulative sums in O(n log n).
Joint sampling + confounding uncertainty: percentile bootstrap of the bounds (Zhao et al.).
"""
from __future__ import annotations

import numpy as np

from architecture.contracts.contracts import SensitivityCurve


def _extreme(c, lo_w, hi_w, R, upper: bool) -> float:
    order = np.argsort(-R if upper else R, kind="stable")
    c, lo_w, hi_w, R = c[order], lo_w[order], hi_w[order], R[order]
    a, b = c * lo_w, c * hi_w  # the first k rounds in the order get the high weight
    num = np.concatenate([[0.0], np.cumsum(b * R)]) + ((a * R).sum() - np.concatenate([[0.0], np.cumsum(a * R)]))
    den = np.concatenate([[0.0], np.cumsum(b)]) + (a.sum() - np.concatenate([[0.0], np.cumsum(a)]))
    vals = num / den
    return float(vals.max() if upper else vals.min())


def hajek_bounds(target_prob_logged: np.ndarray, pscore: np.ndarray, R: np.ndarray, gamma: float):
    inv = 1.0 / pscore
    lo_w, hi_w = 1 + (inv - 1) / gamma, 1 + gamma * (inv - 1)
    c = target_prob_logged
    return _extreme(c, lo_w, hi_w, R, upper=False), _extreme(c, lo_w, hi_w, R, upper=True)


def delta_curve(target_prob_logged, pscore, R, gammas, level=0.95, B=200, seed=0) -> SensitivityCurve:
    """Bounds on Delta = mean(R) [observed deployed policy] - V(target) [off-policy], jointly with sampling error."""
    rng = np.random.default_rng(seed)
    n = len(R)
    a = (1 - level) / 2
    lo, hi = [], []
    boots = [rng.integers(0, n, n) for _ in range(B)]
    for g in gammas:
        bl, bh = [], []
        for idx in boots:
            vlo, vhi = hajek_bounds(target_prob_logged[idx], pscore[idx], R[idx], g)
            m = R[idx].mean()
            bl.append(m - vhi)
            bh.append(m - vlo)
        lo.append(float(np.quantile(bl, a)))
        hi.append(float(np.quantile(bh, 1 - a)))
    gstar = next((g for g, l, h in zip(gammas, lo, hi) if l <= 0 <= h), None)
    return SensitivityCurve(gammas=list(map(float, gammas)), lo=lo, hi=hi, joint=True, gamma_star=gstar)
