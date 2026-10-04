"""FROZEN allocator used only for the ORACLE in eval/targeting_eval.py (lead-owned; the C6 ratchet loop must not edit it).

Copy of the corrected components/targeting/engine.allocate as of 2026-10-04 08:20 IST, so that changes to the
engine cannot move the yardstick (the oracle) that normalises the loop's metric.
"""
import numpy as np
import pandas as pd

ARMS = ["sms_ivr", "bc_visit", "upi_onboard", "incentive"]


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
