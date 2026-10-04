"""C4 RewardModel + C5 ValueEstimator + C6 DeltaEstimator: baseline implementations (obp-equivalent formulas).

Every estimator returns per-round influence terms phi_i with value = mean(phi) (SNIPW uses its linearisation),
so C7 intervals and C8 sensitivity work with any estimator.
"""
from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression

from architecture.contracts.contracts import ActionDist, BanditLog, DeltaEstimate, RewardModelOut, ValueEstimate


class RewardModel:
    """Logistic model with per-action intercepts and per-action linear terms in x (well specified for C11)."""

    def __init__(self, n_actions: int, C: float = 1.0):
        self.K, self.C = n_actions, C

    def _feats(self, X, a):
        n, d = X.shape
        oh = np.zeros((n, self.K))
        oh[np.arange(n), a] = 1.0
        return np.hstack([oh, (X[:, None, :] * oh[:, :, None]).reshape(n, self.K * d)])

    def fit(self, X, A, R):
        self.m = LogisticRegression(C=self.C, max_iter=500).fit(self._feats(X, A), R)
        return self

    def predict(self, X):
        return np.column_stack([self.m.predict_proba(self._feats(X, np.full(len(X), a)))[:, 1] for a in range(self.K)])


def crossfit_q(log: BanditLog, n_folds: int = 2, seed: int = 0) -> RewardModelOut:
    folds = np.random.default_rng(seed).integers(0, n_folds, len(log.A))
    q = np.zeros((len(log.A), log.n_actions))
    for f in range(n_folds):
        tr, te = folds != f, folds == f
        q[te] = RewardModel(log.n_actions).fit(log.X[tr], log.A[tr], log.R[tr]).predict(log.X[te])
    return RewardModelOut(q_hat=q, model=f"logreg-crossfit{n_folds}")


def _diag(w):
    return {"ess": float(w.sum() ** 2 / (w ** 2).sum()), "max_weight": float(w.max()), "mean_weight": float(w.mean())}


def estimate(name: str, log: BanditLog, pi: ActionDist, q: RewardModelOut | None = None,
             pscore: np.ndarray | None = None, tau: float = 10.0) -> ValueEstimate:
    n = len(log.A)
    idx = np.arange(n)
    ps = log.pscore if pscore is None else pscore
    w = pi.probs[idx, log.A] / ps
    R = log.R
    if name == "IPW":
        phi = w * R
    elif name == "SNIPW":
        v = (w * R).sum() / w.sum()
        phi = v + w * (R - v) / w.mean()
    else:
        assert q is not None, f"{name} needs a reward model"
        dm = (pi.probs * q.q_hat).sum(1)
        resid = R - q.q_hat[idx, log.A]
        if name == "DM":
            phi = dm
        elif name == "DR":
            phi = dm + w * resid
        elif name == "SNDR":
            phi = dm + w * resid / w.mean()
        elif name == "SwitchDR":
            phi = dm + w * resid * (w <= tau)
        else:
            raise ValueError(name)
    return ValueEstimate(estimator=name, value=float(phi.mean()), influence=phi, diagnostics=_diag(w))


def delta_vs_onpolicy(name: str, log: BanditLog, pi_old: ActionDist, q: RewardModelOut | None = None,
                      pscore: np.ndarray | None = None) -> DeltaEstimate:
    """Policy effect in the logged period: V(deployed policy, observed on-policy) - V(old policy, off-policy)."""
    old = estimate(name, log, pi_old, q, pscore)
    phi = log.R - old.influence
    return DeltaEstimate(estimator=name, delta=float(phi.mean()), v_new=float(log.R.mean()), v_old=old.value,
                         influence=phi, diagnostics=old.diagnostics)


def delta_offpolicy_vs_onpolicy(name: str, log: BanditLog, pi_new: ActionDist, q: RewardModelOut | None = None) -> DeltaEstimate:
    """Policy effect in the *before* period: V(new, off-policy) - V(old, observed on-policy)."""
    new = estimate(name, log, pi_new, q)
    phi = new.influence - log.R
    return DeltaEstimate(estimator=name, delta=float(phi.mean()), v_new=new.value, v_old=float(log.R.mean()),
                         influence=phi, diagnostics=new.diagnostics)
