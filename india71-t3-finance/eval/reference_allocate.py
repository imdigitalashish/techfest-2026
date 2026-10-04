"""Reference allocation with TRUE effects (evaluation only): the frozen Lagrangian allocator plus a greedy fill of the
budget it leaves unspent (fixes the tie/tight-budget gap found in code review issue 10). It is a strong heuristic
reference, NOT a certified optimum, so normalised values are "share of the reference gain", not "share of the
achievable maximum"."""
import math

import numpy as np
import pandas as pd

from eval.frozen_allocate import ARMS, allocate as lagrangian


def reference_allocate(U: pd.DataFrame, costs: dict, budget: float, female: np.ndarray, min_share_women: float) -> np.ndarray:
    arms = lagrangian(U, costs, budget, female, min_share_women=min_share_women).to_numpy().astype(object)
    spend = sum(costs[a] for a in arms if a != "none")
    M = U[ARMS].to_numpy()
    C = np.array([costs[a] for a in ARMS], dtype=float)
    free = np.flatnonzero(arms == "none")
    best = M[free].argmax(axis=1)
    gain = M[free, best]
    order = np.argsort(-(gain / C[best]))
    for j in order:
        if gain[j] <= 0:
            break
        i, c = free[j], C[best[j]]
        if spend + c > budget:
            continue
        treated = arms != "none"
        k, w = treated.sum() + 1, female[treated].sum() + female[i]
        if not female[i] and w < math.ceil(min_share_women * k):
            continue
        arms[i], spend = ARMS[best[j]], spend + c
    return arms
