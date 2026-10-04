"""C6 DeltaEstimator: the implementation the auto-research ratchet edits.

Contract: estimate_delta(log: BanditLog, pi_old: ActionDist, q: RewardModelOut) -> DeltaEstimate,
where Delta = V(deployed policy, on-policy in `log`) - V(old policy, off-policy).
Baseline (ratchet iteration 0): doubly robust (Dudik, Langford, Li, ICML 2011).
"""
from __future__ import annotations

import numpy as np

from architecture.contracts.contracts import ActionDist, BanditLog, DeltaEstimate, RewardModelOut


def estimate_delta(log: BanditLog, pi_old: ActionDist, q: RewardModelOut) -> DeltaEstimate:
    idx = np.arange(len(log.A))
    w = pi_old.probs[idx, log.A] / log.pscore
    v_old_terms = (pi_old.probs * q.q_hat).sum(1) + w * (log.R - q.q_hat[idx, log.A])
    phi = log.R - v_old_terms
    return DeltaEstimate(estimator="DR", delta=float(phi.mean()), v_new=float(log.R.mean()),
                         v_old=float(v_old_terms.mean()), influence=phi,
                         diagnostics={"ess": float(w.sum() ** 2 / (w ** 2).sum()), "max_weight": float(w.max())})
