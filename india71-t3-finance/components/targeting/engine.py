"""C6 Targeting & Prioritisation Engine (SPIKE A).

fit(train) -> model; predict_uplift(model, X) -> per-arm uplift; allocate(...) -> plan.
The autoresearch loop may edit ONLY this file (learner, features, hyper-parameters); the
evaluator in autoresearch/eval.py is frozen.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

ARMS = ["sms_ivr", "bc_visit", "upi_onboard", "incentive"]
CONFIG = {"learner": "t", "max_iter": 200, "learning_rate": 0.05, "max_leaf_nodes": 15, "min_samples_leaf": 40, "l2": 1.0,
          "shrink": 0.5}
# shrink: weight on per-person deviation from the arm's pilot ATE (1.0 = no shrinkage); a float applies to all arms

NUM = ["mus", "n_accounts", "months_since_last_customer_txn", "share_dbt_withdrawn_7d", "dist_bc_km"]
BOOL = ["female", "rural", "kyc_due", "is_dbt_account", "dbt_monthly", "has_phone", "smartphone", "literate", "bc_sakhi_present"]
CAT = {"state": ["no_use_24m", "dormant_risk", "pass_through", "basic"], "age_band": ["18-25", "26-40", "41-60", "60+"]}


def design(X: pd.DataFrame) -> np.ndarray:
    cols = [X[c].astype(float).to_numpy() for c in NUM] + [X[c].astype(float).to_numpy() for c in BOOL]
    for c, levels in CAT.items():
        cols += [(X[c] == v).astype(float).to_numpy() for v in levels]
    return np.column_stack(cols)


def _clf(seed: int):
    return HistGradientBoostingClassifier(max_iter=CONFIG["max_iter"], learning_rate=CONFIG["learning_rate"],
                                          max_leaf_nodes=CONFIG["max_leaf_nodes"], min_samples_leaf=CONFIG["min_samples_leaf"],
                                          l2_regularization=CONFIG["l2"], random_state=seed)


def fit(X: pd.DataFrame, arm: pd.Series, y: pd.Series, seed: int = 0) -> dict:
    D = design(X)
    models = {}
    for a in ["none"] + ARMS:
        m = (arm == a).to_numpy()
        models[a] = _clf(seed).fit(D[m], y.to_numpy()[m])
    yv, av = y.to_numpy(), arm.to_numpy()
    base = yv[av == "none"].mean() if (av == "none").any() else 0.0
    ate = {a: (yv[av == a].mean() - base) if (av == a).any() else 0.0 for a in ARMS}
    return {"kind": "t", "models": models, "ate": ate}


def predict_uplift(model: dict, X: pd.DataFrame) -> pd.DataFrame:
    D = design(X)
    p0 = model["models"]["none"].predict_proba(D)[:, 1]
    sh = CONFIG.get("shrink", 1.0)
    out = {}
    for a in ARMS:
        k = sh.get(a, 1.0) if isinstance(sh, dict) else sh
        u = model["models"][a].predict_proba(D)[:, 1] - p0
        out[a] = model["ate"][a] + k * (u - model["ate"][a])
    return pd.DataFrame(out, index=X.index)


def allocate(uplift: pd.DataFrame, costs: dict, budget: float, female: np.ndarray | None = None,
             min_share_women: float = 0.0, iters: int = 40) -> pd.Series:
    """Multiple-choice knapsack via Lagrangian relaxation: person i gets argmax_a (u_ia - lam*c_a) if > 0.
    The share constraint sum_i t_i (f_i - s) >= 0 enters as mu * (f_i - s) on every treated row, so raising mu
    favours women AND drops marginal men until the women's share of treated persons >= s = min_share_women."""
    U = uplift[ARMS].to_numpy()
    C = np.array([costs[a] for a in ARMS], dtype=float)
    fem = np.zeros(len(U), bool) if female is None else np.asarray(female, bool)

    def solve(lam, mu):
        score = U + mu * (fem.astype(float) - min_share_women)[:, None] - lam * C[None, :]
        best = score.argmax(axis=1)
        take = score[np.arange(len(U)), best] > 0
        return best, take

    def fit_lam(mu):
        lo, hi = 0.0, max(1e-9, float(np.nanmax(U)) + mu) / max(C.min(), 1e-9) * 2
        for _ in range(iters):
            lam = (lo + hi) / 2
            best, take = solve(lam, mu)
            spend = C[best[take]].sum()
            lo, hi = (lam, hi) if spend > budget else (lo, lam)
        best, take = solve(hi, mu)
        return best, take

    best, take = fit_lam(0.0)
    if min_share_women > 0 and take.any() and fem[take].mean() < min_share_women:
        # smallest mu that satisfies the share constraint (binary search; keep the feasible end)
        lo, hi = 0.0, 2.0
        best, take = fit_lam(hi)
        for _ in range(30):
            mid = (lo + hi) / 2
            b, t = fit_lam(mid)
            if t.any() and fem[t].mean() >= min_share_women:
                hi, best, take = mid, b, t
            else:
                lo = mid
    arms = np.where(take, np.array(ARMS, dtype=object)[best], "none")
    return pd.Series(arms, index=uplift.index, name="arm")
