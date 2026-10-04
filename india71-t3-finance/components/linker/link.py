"""C3 Tokeniser + Person Linker (runs only inside the regulated clean room).

Pseudonyms are HMAC-SHA256(key_purpose, identity_reference): the key is held by the token
authority and differs per purpose, so tokens issued for 'targeting' cannot be joined with tokens
issued for 'accountability'. The identity reference stands in for an Aadhaar Data Vault
reference key / NPCI-mapper reference (never the Aadhaar number itself). Accounts without a
seeded reference cannot be linked and stay singleton "persons" (this inflates person counts and is
reported as a linkage error).
"""
from __future__ import annotations

import hashlib
import hmac

import numpy as np
import pandas as pd

STATE_RANK = {"inoperative": 0, "dormant_risk": 1, "pass_through": 2, "basic": 3, "meaningful": 4}
RANK_STATE = {v: k for k, v in STATE_RANK.items()}


def token(key: bytes, ref: str) -> str:
    return hmac.new(key, ref.encode(), hashlib.sha256).hexdigest()[:20]


def link(account_refs: pd.DataFrame, key: bytes) -> pd.DataFrame:
    """account_refs: account_token, bank_id, identity_ref (None if unseeded) -> AccountPersonLink."""
    refs = account_refs["identity_ref"]
    seeded = refs.notna()
    person = np.where(seeded, [token(key, str(r)) if s else "" for r, s in zip(refs, seeded)],
                      [token(key, "unlinked:" + a) for a in account_refs["account_token"]])
    return pd.DataFrame({"account_token": account_refs["account_token"], "bank_id": account_refs["bank_id"],
                         "person_token": person})


def person_usage(links: pd.DataFrame, usage: pd.DataFrame, attrs: pd.DataFrame, dbt_accounts: pd.Series) -> pd.DataFrame:
    """Aggregate AccountUsage to PersonUsage. attrs: account_token -> district_code, gender, age_band, rural."""
    m = links.merge(usage[["account_token", "state"]], on="account_token").merge(attrs, on="account_token")
    m["rank"] = m["state"].map(STATE_RANK)
    m["is_dbt"] = m["account_token"].isin(set(dbt_accounts))
    g = m.groupby("person_token", sort=False)
    out = g.agg(n_accounts=("account_token", "size"), best_rank=("rank", "max"), district_code=("district_code", "first"),
                gender=("gender", "first"), age_band=("age_band", "first"), rural=("rural", "first")).reset_index()
    dbt_tok = m[m["is_dbt"]].groupby("person_token")["account_token"].first()
    out["dbt_account_token"] = out["person_token"].map(dbt_tok)
    out["best_state"] = out["best_rank"].map(RANK_STATE)
    out["any_meaningful"] = out["best_rank"] == STATE_RANK["meaningful"]
    return out[["person_token", "n_accounts", "best_state", "dbt_account_token", "any_meaningful", "district_code", "gender", "age_band", "rural"]]


def pairwise_f1(true_person: pd.Series, pred_person: pd.Series) -> float:
    """Pairwise linkage F1 over account pairs (computed via cluster sizes; O(n))."""
    df = pd.DataFrame({"t": true_person.to_numpy(), "p": pred_person.to_numpy()})
    pairs = lambda s: (s * (s - 1) / 2).sum()
    tp = pairs(df.groupby(["t", "p"]).size())
    pred = pairs(df.groupby("p").size())
    true = pairs(df.groupby("t").size())
    if pred == 0 or true == 0:
        return 1.0 if pred == true else 0.0
    prec, rec = tp / pred, tp / true
    return float(2 * prec * rec / (prec + rec)) if prec + rec else 0.0
