"""C2 Usage-State Classifier — transparent, gaming-resistant usage states and Meaningful Usage Score.

Input: AccountMonth rows (last 12 months per account). Output: AccountUsage rows (contract).
Rules v0 (every rule id is emitted in reason_codes):
  R1 no_use_24m    : months since last customer-induced txn >= 24. Behavioural only — the RBI legal status is passed
                     through separately as regulatory_inoperative (CBS flag; DBT/scholarship-purpose accounts exempt)
  R2 dormant_risk  : 12 <= months since last customer-induced txn < 24
  R3 pass_through  : DBT credited in >= 3 months, >= 80% of each credit withdrawn within 7 days,
                     and voluntary (non-DBT-cash-out) activity in < 3 months
  R4 meaningful    : voluntary activity in >= 6 of 12 months AND (>= 2 channels OR a protection
                     product OR >= 50% of DBT retained beyond 7 days)
  R5 basic         : everything else
  G1 gaming guard  : credits <= Rs 10 not initiated by the customer never count as activity
MUS = 100 * (0.40 frequency + 0.20 diversity + 0.25 retention + 0.15 protection).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

CH = ["n_branch", "n_bc_aeps", "n_atm", "n_pos", "n_upi"]


def classify(account_month: pd.DataFrame, as_of: str | None = None) -> pd.DataFrame:
    am = account_month
    as_of = as_of or am["month"].max()
    win = am[am["month"] <= as_of]
    months = sorted(win["month"].unique())[-12:]
    win = win[win["month"].isin(months)].copy()
    dbt_cashout = ((win["dbt_credit_count"] > 0) & (win["share_dbt_withdrawn_7d"] > 0)).astype(int)
    win["voluntary"] = (win["n_customer_txn"] - dbt_cashout).clip(lower=0)  # G1: token credits are not customer txns
    win["dbt_month"] = (win["dbt_credit_count"] > 0).astype(int)
    win["fast_out"] = ((win["dbt_credit_count"] > 0) & (win["share_dbt_withdrawn_7d"] >= 0.8)).astype(int)
    g = win.groupby(["account_token", "bank_id"], sort=False)
    agg = g.agg(
        vol_months=("voluntary", lambda s: int((s > 0).sum())),
        dbt_months=("dbt_month", "sum"),
        fast_out_months=("fast_out", "sum"),
        mean_withdrawn=("share_dbt_withdrawn_7d", lambda s: float(s[s > 0].mean()) if (s > 0).any() else 0.0),
        med_balance=("eom_balance", "median"),
        **{f"used_{c}": (c, lambda s: int(s.sum() > 0)) for c in CH},
    ).reset_index()
    last = win[win["month"] == months[-1]].set_index("account_token")
    agg["ms"] = agg["account_token"].map(last["months_since_last_customer_txn"])
    prot = last[["has_pmjjby", "has_pmsby", "has_apy"]].sum(axis=1) / 3.0
    agg["protection"] = agg["account_token"].map(prot).astype(float)
    agg["channels"] = agg[[f"used_{c}" for c in CH]].sum(axis=1)
    agg["frequency"] = agg["vol_months"] / 12.0
    agg["diversity"] = (agg["channels"] / 3.0).clip(upper=1.0)
    agg["retention"] = np.where(agg["dbt_months"] > 0, 1 - agg["mean_withdrawn"], (agg["med_balance"] / 1000.0).clip(upper=1.0))
    agg["retention"] = agg["retention"].clip(0, 1)
    agg["mus"] = (100 * (0.40 * agg["frequency"] + 0.20 * agg["diversity"] + 0.25 * agg["retention"] + 0.15 * agg["protection"])).round(2)
    inop = agg["ms"] >= 24
    dorm = (agg["ms"] >= 12) & ~inop
    pt = (agg["dbt_months"] >= 3) & (agg["fast_out_months"] >= agg["dbt_months"] * 0.8) & (agg["vol_months"] < 3) & ~inop & ~dorm
    meaningful = (agg["vol_months"] >= 6) & ((agg["channels"] >= 2) | (agg["protection"] > 0) | ((agg["dbt_months"] > 0) & (agg["retention"] >= 0.5))) & ~inop & ~dorm & ~pt
    state = np.select([inop, dorm, pt, meaningful], ["no_use_24m", "dormant_risk", "pass_through", "meaningful"], default="basic")
    reasons = np.select([inop, dorm, pt, meaningful], ["R1;G1", "R2;G1", "R3;G1", "R4;G1"], default="R5;G1")
    return pd.DataFrame({
        "account_token": agg["account_token"], "bank_id": agg["bank_id"], "as_of_month": as_of, "state": state,
        "mus": agg["mus"], "frequency": agg["frequency"].round(4), "diversity": agg["diversity"].round(4),
        "retention": agg["retention"].round(4), "protection": agg["protection"].round(4), "reason_codes": reasons,
        "regulatory_inoperative": agg["account_token"].map(last["official_inoperative"]).astype(bool).to_numpy(),
    })
