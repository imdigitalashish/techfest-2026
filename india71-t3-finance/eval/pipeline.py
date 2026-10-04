"""Shared eval pipeline: simulator world -> C2 usage states -> C3 person linkage -> C6 features.

Covariates. `observable=True` (default since v0.3, code-review issue 6) gives the policies only bank-observable
PROXIES with error, never the simulator's true covariates (which also drive treatment effects). Error rates are
ASSUMPTIONS: mobile number seeded (true phone owners, 10% missing); UPI/mobile-banking registration as smartphone
proxy (70% of true smartphone owners registered); thumb-impression flag as literacy proxy (15% misclassified);
geocoded BC distance (log-normal error, sd 0.3); BC Sakhi roster (exact); monthly DBT from the ledger (DBT credited
in >= 10 of the last 12 months on any of the person's accounts). `observable=False` reproduces v0.1/v0.2 behaviour.
All values are SYNTHETIC.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

import sakriya_paths  # noqa: F401
from components.linker.link import link, person_usage
from components.simulator.sim import SimConfig, simulate
from components.usage_state.classify import classify

KEY_TARGETING = b"demo-key-targeting-not-secret"


def build(seed: int = 0, n_persons: int = 40_000, seeded_share: float = 0.97, observable: bool = True) -> dict:
    w = simulate(SimConfig(n_persons=n_persons, seed=seed))
    acc, persons = w["accounts"], w["persons"]
    usage = classify(w["account_month"])
    rng = np.random.default_rng(seed + 101)
    seeded = rng.random(len(acc)) < seeded_share
    refs = pd.DataFrame({"account_token": acc["account_token"], "bank_id": acc["bank_id"],
                         "identity_ref": np.where(seeded, "UIDREF" + acc["person_id"].astype(str), None)})
    links = link(refs, KEY_TARGETING)
    attrs = acc[["account_token", "district_code", "gender", "age_band", "rural"]]
    pu = person_usage(links, usage, attrs, acc.loc[acc["is_dbt_account"], "account_token"])
    # truth map person_token -> person_id (eval only; never exists in production)
    tok2pid = links.assign(person_id=acc["person_id"].to_numpy()).groupby("person_token")["person_id"].first()
    pu["person_id"] = pu["person_token"].map(tok2pid)
    last = w["account_month"][w["account_month"]["month"] == w["account_month"]["month"].max()]
    acc2 = acc.merge(usage[["account_token", "state", "mus"]], on="account_token").merge(
        last[["account_token", "share_dbt_withdrawn_7d"]], on="account_token")
    acc2 = acc2.merge(links[["account_token", "person_token"]], on="account_token")
    g = acc2.groupby("person_token")
    feat = pd.DataFrame({
        "mus": g["mus"].max(), "months_since_last_customer_txn": g["months_since_last_customer_txn"].min(),
        "kyc_due": g["kyc_due"].max(), "is_dbt_account": g["is_dbt_account"].max(),
        "share_dbt_withdrawn_7d": g["share_dbt_withdrawn_7d"].max(),
    })
    pu = pu.merge(feat, left_on="person_token", right_index=True)
    P = persons.set_index("person_id")
    if observable:
        orng = np.random.default_rng(seed + 202)
        n = len(pu)
        pu["has_phone"] = pu["person_id"].map(P["has_phone"]).to_numpy() & (orng.random(n) < 0.9)
        pu["smartphone"] = pu["person_id"].map(P["smartphone"]).to_numpy() & (orng.random(n) < 0.7)
        pu["literate"] = pu["person_id"].map(P["literate"]).to_numpy() ^ (orng.random(n) < 0.15)
        pu["dist_bc_km"] = pu["person_id"].map(P["dist_bc_km"]).to_numpy() * orng.lognormal(0.0, 0.3, n)
        pu["bc_sakhi_present"] = pu["person_id"].map(P["bc_sakhi_present"])
        am = w["account_month"]
        dbt_m = am.assign(d=am["dbt_credit_count"] > 0).groupby("account_token")["d"].sum()
        acc_dbt = links[["account_token", "person_token"]].assign(m=lambda d: d["account_token"].map(dbt_m).fillna(0))
        pu["dbt_monthly"] = pu["person_token"].map(acc_dbt.groupby("person_token")["m"].max() >= 10).fillna(False)
    else:
        for c in ["has_phone", "smartphone", "literate", "dist_bc_km", "bc_sakhi_present"]:
            pu[c] = pu["person_id"].map(P[c])
        pu["dbt_monthly"] = pu["person_id"].map(P["dbt_type"].isin(["women_ct_monthly", "pension_monthly"]))
    pmjdy_tok = set(links.loc[acc["is_pmjdy"].to_numpy(), "person_token"])
    pu["has_pmjdy"] = pu["person_token"].isin(pmjdy_tok)
    pu["bc_id"] = pu["person_id"].map(P["bc_id"])
    pu["female"] = pu["gender"] == "F"
    pu["state"] = pu["best_state"]
    return {"world": w, "usage": usage, "links": links, "persons_usage": pu, "seeded": seeded}
