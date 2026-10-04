"""C9 Decomposer (spike, v0): attribute the naive before/after gap.

naive          = mean(R_after) - mean(R_before)
policy_effect  = mean(R_after) - V_after(old)                [OPE on after-period logs; CI from C7]
env_change     = V_after(old) - mean(R_before)               [= naive - policy_effect]
mix_shift      = E_after-users[q_before(x, old)] - E_before-users[q_before(x, old)]   [reward model fitted on before logs]
response_drift = env_change - mix_shift
Only policy_effect carries a CI claim; the mix/drift split is model-based (DM) and labelled as such.
"""
from __future__ import annotations

import numpy as np

from architecture.contracts.contracts import ActionDist, BanditLog, Decomposition
from components.estimators.ope import RewardModel, crossfit_q, delta_vs_onpolicy
from components.intervals.ci import wald


def decompose(before: BanditLog, after: BanditLog, pi_old_after: ActionDist, pi_old_before: ActionDist,
              estimator: str = "DR", pscore_after: np.ndarray | None = None, q_after=None) -> Decomposition:
    q_after = q_after if q_after is not None else crossfit_q(after)
    d = delta_vs_onpolicy(estimator, after, pi_old_after, q_after, pscore_after)
    naive = float(after.R.mean() - before.R.mean())
    env = naive - d.delta
    qb = RewardModel(before.n_actions).fit(before.X, before.A, before.R)
    mix = float((pi_old_after.probs * qb.predict(after.X)).sum(1).mean()
                - (pi_old_before.probs * qb.predict(before.X)).sum(1).mean())
    return Decomposition(naive=naive, policy_effect=wald(d.influence), env_change=env, mix_shift=mix,
                         response_drift=env - mix)
