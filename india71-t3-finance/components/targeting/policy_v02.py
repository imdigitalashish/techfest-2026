"""C6 v0.2 — transparent default rule, learned two-stage challenger, and the deployment gate.

DEFAULT (transparent; can be published and recomputed by anyone from the pilot table):
  Stage 1: the arm with the highest pilot effect per rupee, among arms with a positive pilot effect, goes to every
           eligible person (persons drawn by lottery if the budget cannot cover everyone).
  Stage 2: the remaining budget upgrades persons, drawn by lottery, to the arm with the highest *extra* pilot effect
           per *extra* rupee over the stage-1 arm.
CHALLENGERS (learned): same stage 1; stage 2 upgrades by the model's predicted extra uplift per extra rupee (shrunk
  T-learner in engine.py), with the women's-share floor — either choosing the arm too ('model') or only choosing whom to
  upgrade to the default rule's arm ('who-only').
GATE (tests the who-only challenger by default): the challenger is deployed only if, on a held-out share of the eligible pilot, its inverse-probability-weighted
  (IPW) value beats the default with a one-sided 90% bootstrap lower bound above zero; otherwise the default runs.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from components.targeting import engine

ARMS = engine.ARMS


def arm_ate(arm: pd.Series, y: pd.Series) -> dict:
    """Pilot difference in means vs 'none' for each arm: {arm: (effect, standard error)}."""
    yv, av = np.asarray(y, dtype=float), np.asarray(arm)
    y0 = yv[av == "none"]
    out = {}
    for a in ARMS:
        ya = yv[av == a]
        if len(ya) < 2 or len(y0) < 2:
            out[a] = (0.0, float("inf"))
            continue
        out[a] = (float(ya.mean() - y0.mean()), float(np.sqrt(ya.var(ddof=1) / len(ya) + y0.var(ddof=1) / len(y0))))
    return out


def stage1_arm(ate: dict, costs: dict) -> str | None:
    pos = [a for a in ARMS if ate[a][0] > 0]
    return max(pos, key=lambda a: ate[a][0] / costs[a]) if pos else None


def upgrade_arm(ate: dict, costs: dict, s1: str) -> str | None:
    c1, e1 = costs[s1], ate[s1][0]
    cands = [a for a in ARMS if costs[a] > c1 and ate[a][0] > e1]
    return max(cands, key=lambda a: (ate[a][0] - e1) / (costs[a] - c1)) if cands else None


def rule_policy(n: int, ate: dict, costs: dict, budget: float, rng: np.random.Generator) -> np.ndarray:
    arms = np.full(n, "none", dtype=object)
    s1 = stage1_arm(ate, costs)
    if s1 is None:
        return arms
    k1 = min(n, int(budget // costs[s1]))
    arms[rng.permutation(n)[:k1]] = s1
    up = upgrade_arm(ate, costs, s1)
    if up is None or k1 < n:
        return arms
    k2 = min(n, int((budget - n * costs[s1]) // (costs[up] - costs[s1])))
    arms[rng.permutation(n)[:k2]] = up
    return arms


def two_stage(U: pd.DataFrame, ate: dict, costs: dict, budget: float, female: np.ndarray, min_share_women: float,
              arm_choice: str = "model") -> np.ndarray:
    """arm_choice='model': the model picks whom to upgrade AND to which arm.
    arm_choice='rule' ("who-only"): the upgrade arm is the default rule's (pilot effect per rupee); the model only
    ranks whom to upgrade."""
    n = len(U)
    arms = np.full(n, "none", dtype=object)
    s1 = stage1_arm(ate, costs)
    if s1 is None:
        return arms
    k1 = min(n, int(budget // costs[s1]))
    if k1 < n:
        arms[np.argsort(-U[s1].to_numpy())[:k1]] = s1
        return arms
    arms[:] = s1
    allowed = [a for a in ARMS if costs[a] > costs[s1]]
    if arm_choice == "rule":
        up_rule = upgrade_arm(ate, costs, s1)
        allowed = [up_rule] if up_rule else []
    D, cd = pd.DataFrame(index=U.index), {}
    for a in ARMS:
        if a in allowed:
            D[a], cd[a] = U[a] - U[s1], costs[a] - costs[s1]
        else:
            D[a], cd[a] = -1.0, 1e9
    up = engine.allocate(D, cd, budget - n * costs[s1], female, min_share_women=min_share_women).to_numpy()
    sel = up != "none"
    arms[sel] = up[sel]
    return arms


def ipw(arm_obs: np.ndarray, y: np.ndarray, pi: np.ndarray, prop: dict) -> np.ndarray:
    """Per-person IPW contributions; their mean estimates the outcome rate under policy pi (arms randomised)."""
    w = np.array([1.0 / prop[a] for a in arm_obs])
    return y * (arm_obs == pi) * w


def gate(pilot: pd.DataFrame, costs: dict, budget_per_person: float, seed: int, val_frac: float = 0.3,
         alpha: float = 0.10, n_boot: int = 500, arm_choice: str = "rule") -> dict:
    """pilot: eligible pilot persons with features + 'arm' + 'y'. Returns the gate decision and its evidence."""
    rng = np.random.default_rng(seed + 77)
    idx = rng.permutation(len(pilot))
    nv = int(len(pilot) * val_frac)
    va, tr = pilot.iloc[idx[:nv]], pilot.iloc[idx[nv:]]
    ate = arm_ate(tr["arm"], tr["y"])
    U = engine.predict_uplift(engine.fit(tr, tr["arm"], tr["y"], seed=seed), va)
    fem = va["female"].to_numpy()
    budget = budget_per_person * len(va)
    p_rule = rule_policy(len(va), ate, costs, budget, np.random.default_rng(seed + 78))
    p_ch = two_stage(U, ate, costs, budget, fem, float(fem.mean()), arm_choice=arm_choice)
    prop = pilot["arm"].value_counts(normalize=True).to_dict()
    a_obs, y = va["arm"].to_numpy(), va["y"].to_numpy().astype(float)
    d = ipw(a_obs, y, p_ch, prop) - ipw(a_obs, y, p_rule, prop)
    bs = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(n_boot)])
    lb = float(np.quantile(bs, alpha))
    return {"pass": bool(lb > 0), "ipw_diff": float(d.mean()), "lower_bound_90": lb, "n_validation": int(nv)}
