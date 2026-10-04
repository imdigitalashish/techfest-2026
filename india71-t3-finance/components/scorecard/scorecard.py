"""C10 Usage Scorecard & Attribution (SPIKE B).

Inputs per person: implementer (district/bank/branch/BC cluster), randomised holdout flag, person-level
meaningful-use outcome from C2 (token credits never count), account-level flags. Output: ScorecardRow-like
records with the implementer's *incremental* meaningful-usage (treated − holdout) and a 95% CI, plus
gaming flags. Empirical-Bayes shrinkage toward the district mean stabilises small units.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def incremental(df: pd.DataFrame, unit: str = "unit_id", y: str = "meaningful", hold: str = "holdout",
                min_n: int = 30) -> pd.DataFrame:
    """Treated-minus-holdout difference per unit with a 95% CI. Units with fewer than min_n treated or holdout persons
    get status 'insufficient_data' and no estimate (pool them or wait for more months) instead of a silent NaN."""
    g = df.groupby([unit, hold])[y].agg(["mean", "count", "var"]).unstack(hold)
    col = lambda stat, h: g[(stat, h)] if (stat, h) in g.columns else pd.Series(np.nan, index=g.index)
    t_m, c_m = col("mean", False), col("mean", True)
    t_n, c_n = col("count", False).fillna(0), col("count", True).fillna(0)
    t_v, c_v = col("var", False).fillna(0.25), col("var", True).fillna(0.25)
    ok = (t_n >= min_n) & (c_n >= min_n)
    est = (t_m - c_m).where(ok)
    se = np.sqrt(t_v / t_n.where(ok) + c_v / c_n.where(ok))
    return pd.DataFrame({"incremental": est, "se": se, "ci_low": est - 1.96 * se, "ci_high": est + 1.96 * se,
                         "persons": t_n + c_n, "mu_rate": (t_m.fillna(0) * t_n + c_m.fillna(0) * c_n) / (t_n + c_n),
                         "status": np.where(ok, "ok", "insufficient_data")})


def eb_shrink(inc: pd.DataFrame, group: pd.Series) -> pd.Series:
    """Empirical-Bayes shrinkage of unit estimates toward their group (district) mean."""
    out = inc["incremental"].copy()
    for _, idx in inc.groupby(group).groups.items():
        idx = [i for i in idx if inc.at[i, "status"] == "ok"]
        if not idx:
            continue
        e, s2 = inc.loc[idx, "incremental"], inc.loc[idx, "se"] ** 2
        tau2 = max(e.var(ddof=1) - s2.mean(), 1e-6) if len(e) > 2 else 1e-6
        w = tau2 / (tau2 + s2)
        out.loc[idx] = e.mean() + w * (e - e.mean())
    return out


def gaming_flags(df: pd.DataFrame, unit: str = "unit_id") -> pd.Series:
    """Flag units whose account-level 'operative' share exceeds their person-level meaningful share by > 15 pp
    (token credits / reactivate-then-lapse inflate the former but not the latter)."""
    g = df.groupby(unit)[["acct_operative", "meaningful"]].mean()
    return (g["acct_operative"] - g["meaningful"] > 0.15).map({True: "TOKEN_ACTIVITY_SUSPECTED", False: ""})
