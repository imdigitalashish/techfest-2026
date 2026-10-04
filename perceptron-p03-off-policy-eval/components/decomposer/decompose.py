"""C9 Decomposer (spike): attribute the naive before/after gap.

v0 (environment-first ordering), kept for the frozen bank:
  naive          = mean(R_after) - mean(R_before)
  policy_effect  = mean(R_after) - V_after(old)                [OPE on after-period logs; CI from C7]
  env_change     = V_after(old) - mean(R_before)               [= naive - policy_effect]
  mix_shift      = V_mix(old) - V_before(old), V_mix(old) = E_after-users[sum_a pi_old(a|x) mu_before(x, a)]
  response_drift = env_change - mix_shift
  mix_method "DM": both mix terms from a reward model fitted on before logs (model-dependent).
  mix_method "DR": V_mix(old) = plug-in + a density-ratio correction on before logs, rho(x) = p_after(x) / p_before(x)
                   from a cross-fitted classifier; V_before(old) is observed on-policy. Consistent if either the reward
                   model or rho is right. The before logs are on-policy for pi_old, so no action weight is needed.
v1 review fix: shapley() gives the 2x2 Shapley attribution with the interaction term (see ShapleyDecomposition).
Identification caveat: with policy-induced audience change (feedback), the policy term is the DIRECT effect on the
users who actually arrived; the audience change lands in mix_shift. The total effect is not identified from these logs.
"""
from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression

from architecture.contracts.contracts import ActionDist, BanditLog, Decomposition, Interval, ShapleyDecomposition
from components.estimators.ope import RewardModel, crossfit_q, delta_vs_onpolicy, estimate
from components.intervals.ci import wald

Z = 1.959963984540054


def _density_ratio(X_before: np.ndarray, X_after: np.ndarray, n_folds: int = 2, seed: int = 0) -> np.ndarray:
    """Cross-fitted rho(x_i) = p_after(x_i) / p_before(x_i) at the before-period contexts."""
    folds = np.random.default_rng(seed).integers(0, n_folds, len(X_before))
    rho = np.zeros(len(X_before))
    for f in range(n_folds):
        tr, te = folds != f, folds == f
        Xtr = np.vstack([X_before[tr], X_after])
        ytr = np.r_[np.zeros(tr.sum()), np.ones(len(X_after))]
        p = LogisticRegression(max_iter=1000).fit(Xtr, ytr).predict_proba(X_before[te])[:, 1]
        rho[te] = (tr.sum() / len(X_after)) * p / (1 - p)
    return rho


def v_mix_old(before: BanditLog, after: BanditLog, pi_old_after: ActionDist, method: str = "DM") -> float:
    qb = RewardModel(before.n_actions).fit(before.X, before.A, before.R)
    plug_in = float((pi_old_after.probs * qb.predict(after.X)).sum(1).mean())
    if method == "DM":
        return plug_in
    rho = _density_ratio(before.X, after.X)
    resid = before.R - qb.predict(before.X)[np.arange(len(before.A)), before.A]
    return plug_in + float((rho * resid).mean())


def decompose(before: BanditLog, after: BanditLog, pi_old_after: ActionDist, pi_old_before: ActionDist,
              estimator: str = "DR", pscore_after: np.ndarray | None = None, q_after=None,
              mix_method: str = "DM") -> Decomposition:
    q_after = q_after if q_after is not None else crossfit_q(after)
    d = delta_vs_onpolicy(estimator, after, pi_old_after, q_after, pscore_after)
    naive = float(after.R.mean() - before.R.mean())
    env = naive - d.delta
    if mix_method == "DM":  # v0 definition (frozen bank)
        qb = RewardModel(before.n_actions).fit(before.X, before.A, before.R)
        mix = float((pi_old_after.probs * qb.predict(after.X)).sum(1).mean()
                    - (pi_old_before.probs * qb.predict(before.X)).sum(1).mean())
    else:
        mix = v_mix_old(before, after, pi_old_after, "DR") - float(before.R.mean())
    return Decomposition(naive=naive, policy_effect=wald(d.influence), env_change=env, mix_shift=mix,
                         response_drift=env - mix, mix_method=mix_method)


def _iv(point: float, se: float, method: str) -> Interval:
    return Interval(method=method, level=0.95, point=point, lo=point - Z * se, hi=point + Z * se)


def shapley(before: BanditLog, after: BanditLog, pi_new_before: ActionDist, pi_old_after: ActionDist,
            estimator: str = "DR", q_before=None, q_after=None) -> ShapleyDecomposition:
    """OPE fills V(before, new) from the before logs and V(after, old) from the after logs (independent samples)."""
    q_before = q_before if q_before is not None else crossfit_q(before)
    q_after = q_after if q_after is not None else crossfit_q(after)
    phi_b = estimate(estimator, before, pi_new_before, q_before).influence - before.R  # V(b,new) - V(b,old), same rows
    phi_a = after.R - estimate(estimator, after, pi_old_after, q_after).influence  # V(a,new) - V(a,old), same rows
    eb, sb = float(phi_b.mean()), float(phi_b.std(ddof=1) / np.sqrt(len(phi_b)))
    ea, sa = float(phi_a.mean()), float(phi_a.std(ddof=1) / np.sqrt(len(phi_a)))
    naive = float(after.R.mean() - before.R.mean())
    pol, pol_se = 0.5 * (eb + ea), 0.5 * float(np.hypot(sb, sa))
    return ShapleyDecomposition(naive=naive, policy=_iv(pol, pol_se, "wald-shapley"), env=naive - pol,
                                interaction=_iv(ea - eb, float(np.hypot(sb, sa)), "wald"),
                                effect_after=_iv(ea, sa, "wald"), effect_before=_iv(eb, sb, "wald"))
