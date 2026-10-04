"""C6 v0.3 — fixes code-review issues 1, 3, 4 and 5 of v0.2 (reviews/2026-10-04-code-gpt-6-sol.md).

DEFAULT RULE (transparent): a 10% randomised holdout is drawn first and gets standard service only. Stage 1: the arm
  with the highest pilot effect per rupee (among arms with a positive effect) goes to every remaining eligible person,
  or to a women-floor-stratified lottery if the budget cannot cover everyone. Stage 2 (only if stage 1 covers everyone):
  the leftover budget upgrades a women-floor-stratified lottery to the arm with the best extra effect per extra rupee.
CHALLENGER (learned): an exact copy of the rule's plan — same holdout, same stage-1 recipients, same upgrade arm, same
  number of upgrades — except that the model chooses WHOM to upgrade (top predicted extra uplift, women-floor
  stratified). If the rule makes no upgrades, the challenger equals the rule.
GATE: the pilot is split once into train (70%) and validation (30%). Arm effects and the model are fitted on train;
  the gate compares rule vs challenger on validation by IPW (one-sided 90% bootstrap bound > 0). Deployment uses the
  SAME train-fitted effects and model that the gate evaluated.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from components.targeting import engine

ARMS = engine.ARMS


def arm_ate(arm, y) -> dict:
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


def stage1_arm(ate: dict, costs: dict):
    pos = [a for a in ARMS if ate[a][0] > 0]
    return max(pos, key=lambda a: ate[a][0] / costs[a]) if pos else None


def upgrade_arm(ate: dict, costs: dict, s1: str):
    c1, e1 = costs[s1], ate[s1][0]
    cands = [a for a in ARMS if costs[a] > c1 and ate[a][0] > e1]
    return max(cands, key=lambda a: (ate[a][0] - e1) / (costs[a] - c1)) if cands else None


def stratified_pick(pool: np.ndarray, k: int, female: np.ndarray, floor: float, rng=None, score=None) -> np.ndarray:
    """Pick k indices from pool with at least ceil(floor*k) women (if available): by lottery (rng) or by score (desc)."""
    pool = np.asarray(pool)
    k = min(k, len(pool))
    if k <= 0:
        return pool[:0]
    order = rng.permutation(len(pool)) if score is None else np.argsort(-np.asarray(score)[pool], kind="stable")
    ranked = pool[order]
    women, men = ranked[female[ranked]], ranked[~female[ranked]]
    need_w = min(len(women), math.ceil(floor * k))
    first = women[:need_w]
    rest = np.concatenate([women[need_w:], men])
    if score is None:
        rest = rest[rng.permutation(len(rest))]
    else:
        rest = rest[np.argsort(-np.asarray(score)[rest], kind="stable")]
    return np.concatenate([first, rest[: k - need_w]])


def rule_plan(n: int, ate: dict, costs: dict, budget: float, female: np.ndarray, floor: float,
              rng: np.random.Generator, holdout_frac: float = 0.10) -> dict:
    arms = np.full(n, "none", dtype=object)
    holdout = np.zeros(n, dtype=bool)
    holdout[rng.permutation(n)[: int(round(holdout_frac * n))]] = True
    elig = np.flatnonzero(~holdout)
    info = {"stage1": None, "upgrade": None, "k1": 0, "k2": 0}
    s1 = stage1_arm(ate, costs)
    if s1 is None:
        return {"arms": arms, "holdout": holdout, "info": info}
    k1 = min(len(elig), int(budget // costs[s1]))
    rec1 = elig if k1 == len(elig) else stratified_pick(elig, k1, female, floor, rng=rng)
    arms[rec1] = s1
    info.update(stage1=s1, k1=int(len(rec1)))
    up = upgrade_arm(ate, costs, s1)
    if up is not None and k1 == len(elig):
        k2 = min(len(elig), int((budget - k1 * costs[s1]) // (costs[up] - costs[s1])))
        rec2 = stratified_pick(elig, k2, female, floor, rng=rng)
        arms[rec2] = up
        info.update(upgrade=up, k2=int(len(rec2)))
    return {"arms": arms, "holdout": holdout, "info": info}


def challenger_plan(rule: dict, U: pd.DataFrame, female: np.ndarray, floor: float) -> np.ndarray:
    """Same plan as the rule except that the model chooses whom to upgrade (same arm, same count)."""
    arms = rule["arms"].copy()
    info = rule["info"]
    if not info["upgrade"] or info["k2"] == 0:
        return arms
    s1, up, k2 = info["stage1"], info["upgrade"], info["k2"]
    arms[arms == up] = s1
    pool = np.flatnonzero(arms == s1)
    score = (U[up] - U[s1]).to_numpy()
    arms[stratified_pick(pool, k2, female, floor, score=score)] = up
    return arms


def floor_ok(arms: np.ndarray, female: np.ndarray, floor: float, tol: float = 1e-9) -> bool:
    """Women's share >= floor among stage-1 recipients and among upgrades (where feasible)."""
    treated = arms != "none"
    if not treated.any():
        return True
    groups = [treated]
    vals = [a for a in set(arms[treated])]
    if len(vals) > 1:
        groups = [arms == v for v in vals]
    for g in groups:
        k, w_avail = int(g.sum()), int(female.sum())
        need = min(math.ceil(floor * k), w_avail) / k if k else 0
        if female[g].mean() + tol < min(floor, need):
            return False
    return True


def ipw(arm_obs, y, pi, prop) -> np.ndarray:
    w = np.array([1.0 / prop[a] for a in arm_obs])
    return y * (arm_obs == pi) * w


def fit_and_gate(pilot: pd.DataFrame, costs: dict, bpe: float, seed: int, val_frac: float = 0.3,
                 alpha: float = 0.10, n_boot: int = 500) -> dict:
    """Split the eligible pilot once; fit effects + model on train; gate on validation. Returns the deployable objects."""
    rng = np.random.default_rng(seed + 77)
    idx = rng.permutation(len(pilot))
    nv = int(len(pilot) * val_frac)
    va, tr = pilot.iloc[idx[:nv]], pilot.iloc[idx[nv:]]
    ate = arm_ate(tr["arm"], tr["y"])
    model = engine.fit(tr, tr["arm"], tr["y"], seed=seed)
    fem = va["female"].to_numpy()
    floor = float(fem.mean())
    rp = rule_plan(len(va), ate, costs, bpe * len(va), fem, floor, np.random.default_rng(seed + 78), holdout_frac=0.0)
    cp = challenger_plan(rp, engine.predict_uplift(model, va), fem, floor)
    prop = pilot["arm"].value_counts(normalize=True).to_dict()
    a_obs, y = va["arm"].to_numpy(), va["y"].to_numpy().astype(float)
    d = ipw(a_obs, y, cp, prop) - ipw(a_obs, y, rp["arms"], prop)
    bs = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(n_boot)])
    lb = float(np.quantile(bs, alpha))
    return {"ate": ate, "model": model, "gate": {"pass": bool(lb > 0), "ipw_diff": float(d.mean()), "lower_bound_90": lb,
                                                 "n_validation": int(nv), "n_train": int(len(tr))}}
