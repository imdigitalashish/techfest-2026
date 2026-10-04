"""C10 Usage Scorecard & Attribution (SPIKE B).

Inputs per person: implementer (district/bank/branch/BC cluster), randomised holdout flag, person-level
meaningful-use outcome from C2 (token credits never count), account-level flags. Output: ScorecardRow-like
records with the implementer's *incremental* meaningful-usage (treated − holdout) and a 95% CI, plus
gaming flags. Empirical-Bayes shrinkage toward the district mean stabilises small units.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def incremental(df: pd.DataFrame, unit: str = "unit_id", y: str = "meaningful", hold: str = "holdout") -> pd.DataFrame:
    g = df.groupby([unit, hold])[y].agg(["mean", "count", "var"]).unstack(hold)
    t_m, c_m = g[("mean", False)], g[("mean", True)]
    t_n, c_n = g[("count", False)], g[("count", True)]
    t_v, c_v = g[("var", False)].fillna(0.25), g[("var", True)].fillna(0.25)
    est = t_m - c_m
    se = np.sqrt(t_v / t_n + c_v / c_n)
    return pd.DataFrame({"incremental": est, "se": se, "ci_low": est - 1.96 * se, "ci_high": est + 1.96 * se,
                         "persons": t_n + c_n, "mu_rate": (t_m * t_n + c_m * c_n) / (t_n + c_n)})


def eb_shrink(inc: pd.DataFrame, group: pd.Series) -> pd.Series:
    """Empirical-Bayes shrinkage of unit estimates toward their group (district) mean."""
    out = inc["incremental"].copy()
    for _, idx in inc.groupby(group).groups.items():
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
