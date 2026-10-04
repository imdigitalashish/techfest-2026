"""C14 Simulator — SYNTHETIC persons, accounts, 24-month histories and potential outcomes.

Everything this module produces is synthetic. Parameters come from calibration.json, where each
value is marked VERIFIED (cited public source), PENDING (public source, not yet verified here)
or ASSUMPTION (modelling choice). The simulator exists so that targeting (C6), measurement (C9)
and accountability (C10) can be evaluated against KNOWN ground truth, which no public dataset
offers at account level.

Generative story (per person i):
  district d -> base usage u_d; person covariates (gender, age, rural, literacy, phone, distance
  to BC, migration, death, DBT scheme); latent engagement z_i; 1-3 accounts (one "primary" that
  the person uses, one NPCI-mapped DBT account that may differ); 24 months of customer-induced
  transactions by channel; DBT credits; usage state.
  Potential outcome Y_i(a) = sustained use over the next 6 months under arm a, with
  P(Y=1 | a) = sigmoid(base_i + tau_a(i)); tau_a is heterogeneous and is ZERO for persons
  who are deceased and for village-based arms when the person has migrated.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
CHANNELS = ["n_branch", "n_bc_aeps", "n_atm", "n_pos", "n_upi"]
ARMS = ["none", "sms_ivr", "bc_visit", "upi_onboard", "incentive"]
AGE_BANDS = ["18-25", "26-40", "41-60", "60+"]
BANKS = ["PSB_A", "PSB_B", "PSB_C", "RRB_D", "PVT_E", "PB_F"]
BANK_P = [0.32, 0.18, 0.12, 0.18, 0.08, 0.12]


def load_calibration(path: pathlib.Path | None = None) -> dict:
    raw = json.loads((path or HERE / "calibration.json").read_text())
    return {k: v["value"] for k, v in raw["params"].items()}


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


@dataclass
class SimConfig:
    n_persons: int = 40_000
    n_districts: int = 30
    bcs_per_district: int = 20
    months: int = 24
    seed: int = 0
    pilot_fraction: float = 0.2
    calibration: dict = field(default_factory=load_calibration)
    district_use_rates: np.ndarray | None = None  # optional real NFHS-5 district rates (0-1)


def _persons(cfg: SimConfig, rng: np.random.Generator) -> tuple[pd.DataFrame, pd.DataFrame]:
    c = cfg.calibration
    n, D = cfg.n_persons, cfg.n_districts
    if cfg.district_use_rates is not None:
        u = rng.choice(np.asarray(cfg.district_use_rates), size=D, replace=True)
    else:
        u = np.clip(rng.normal(c["district_use_mean"], c["district_use_sd"], D), 0.35, 0.97)
    districts = pd.DataFrame({
        "district_code": np.arange(1, D + 1),
        "base_use": u,
        "women_ct": rng.random(D) < c["women_ct_district_share"],
        "bc_sakhi_present": rng.random(D) < c["bc_sakhi_district_share"],
    })
    d = rng.integers(0, D, n)
    female = rng.random(n) < c["women_share"]
    age_idx = rng.choice(4, size=n, p=c["age_probs"])
    rural = rng.random(n) < c["rural_share"]
    lit_p = np.where(rural, np.where(female, 0.60, 0.78), np.where(female, 0.80, 0.90))
    lit_p = np.where(age_idx == 3, lit_p - 0.2, lit_p)
    literate = rng.random(n) < lit_p
    phone_p = np.where(female, c["women_phone_own"], c["men_phone_own"]) - 0.08 * rural - 0.2 * (age_idx == 3)
    has_phone = rng.random(n) < np.clip(phone_p, 0.05, 0.98)
    smart_p = np.where(age_idx <= 1, 0.62, 0.38) - 0.10 * rural
    smartphone = has_phone & (rng.random(n) < smart_p)
    dist_bc_km = np.round(rng.lognormal(np.where(rural, 0.7, -0.6), 0.6), 2)
    mig_mult = np.where(rural & ~female & (age_idx <= 1), 2.0, 0.55)
    migrated = rng.random(n) < c["migrated_share"] * mig_mult
    deceased = (age_idx == 3) & (rng.random(n) < c["deceased_share_60p"])
    women_ct = districts["women_ct"].to_numpy()[d]
    dbt_type = np.full(n, "none", dtype=object)
    r = rng.random(n)
    dbt_type[female & women_ct & (age_idx <= 2) & (r < 0.7)] = "women_ct_monthly"
    rest = dbt_type == "none"
    dbt_type[rest & rural & (age_idx >= 1) & (age_idx <= 2) & (r < 0.22)] = "pmkisan_quarterly"
    rest = dbt_type == "none"
    dbt_type[rest & rural & (age_idx <= 2) & (rng.random(n) < 0.15)] = "wages_irregular"
    rest = dbt_type == "none"
    dbt_type[rest & (age_idx == 3) & (rng.random(n) < 0.45)] = "pension_monthly"
    z = (
        logit(districts["base_use"].to_numpy()[d])
        + 0.6 * literate + 0.5 * smartphone + 0.25 * has_phone
        - 0.25 * np.log1p(dist_bc_km) + 0.2 * (~rural) - 0.2 * female
        + np.array([-0.1, 0.15, 0.05, -0.3])[age_idx]
        + rng.normal(0, 1.5, n)
    )
    n_acc = rng.choice([1, 2, 3], size=n, p=c["accounts_per_person_probs"])
    n_acc = np.where(smartphone & (rng.random(n) < 0.15), np.minimum(n_acc + 1, 3), n_acc)
    bc_local = rng.integers(0, cfg.bcs_per_district, n)
    persons = pd.DataFrame({
        "person_id": np.arange(n),
        "district_code": d + 1,
        "gender": np.where(female, "F", "M"),
        "age_band": np.array(AGE_BANDS)[age_idx],
        "rural": rural, "literate": literate, "has_phone": has_phone, "smartphone": smartphone,
        "dist_bc_km": dist_bc_km, "migrated": migrated, "deceased": deceased,
        "dbt_type": dbt_type, "z": z, "n_accounts": n_acc,
        "bc_id": [f"BC{dd + 1:03d}_{b:02d}" for dd, b in zip(d, bc_local)],
        "bc_sakhi_present": districts["bc_sakhi_present"].to_numpy()[d],
    })
    return persons, districts


def _accounts(persons: pd.DataFrame, rng: np.random.Generator, cfg: SimConfig) -> pd.DataFrame:
    c = cfg.calibration
    rep = persons.loc[persons.index.repeat(persons["n_accounts"])].reset_index(drop=True)
    rep["acc_idx"] = rep.groupby("person_id").cumcount()
    n = len(rep)
    primary_idx = rng.integers(0, persons["n_accounts"].to_numpy())
    dbt_same = rng.random(len(persons)) < 0.7
    dbt_idx = np.where(dbt_same, primary_idx, rng.integers(0, persons["n_accounts"].to_numpy()))
    rep["is_primary"] = rep["acc_idx"].to_numpy() == primary_idx[rep["person_id"].to_numpy()]
    has_dbt = (persons["dbt_type"] != "none").to_numpy()
    rep["is_dbt_account"] = (rep["acc_idx"].to_numpy() == dbt_idx[rep["person_id"].to_numpy()]) & has_dbt[rep["person_id"].to_numpy()]
    opened = rng.choice(np.arange(2014, 2025), size=n, p=_open_year_p())
    rep["opened_year"] = opened
    rep["is_pmjdy"] = rng.random(n) < np.where(opened <= 2016, 0.9, 0.6)
    rep["kyc_due"] = (opened <= 2016) & (rng.random(n) < c["kyc_due_share_old"])
    rep["bank_id"] = rng.choice(BANKS, size=n, p=BANK_P)
    rep["account_token"] = [f"A{i:07d}" for i in range(n)]
    return rep


def _open_year_p():
    w = np.array([30, 14, 10, 6, 5, 5, 6, 6, 6, 6, 6], dtype=float)  # PMJDY-heavy 2014-16 (ASSUMPTION)
    return w / w.sum()


def _activity_probs(acc: pd.DataFrame, offset: float) -> np.ndarray:
    z = acc["z"].to_numpy()
    p = np.where(acc["is_primary"], sigmoid(z + offset), 0.02)
    p = np.where(acc["migrated"], p * np.where(acc["smartphone"], 0.6, 0.15), p)
    p = np.where(acc["deceased"], 0.0, p)
    p = np.where(acc["kyc_due"] & (acc["opened_year"] <= 2015), p * 0.6, p)  # partial freezes
    return p


def _dbt_schedule(dbt_type: np.ndarray, months: int, rng) -> np.ndarray:
    n = len(dbt_type)
    s = np.zeros((n, months), dtype=bool)
    s[dbt_type == "women_ct_monthly"] = True
    s[dbt_type == "pension_monthly"] = True
    q = dbt_type == "pmkisan_quarterly"
    s[np.ix_(q, np.arange(months) % 4 == 0)] = True
    w = dbt_type == "wages_irregular"
    s[w] = rng.random((w.sum(), months)) < 0.3
    return s


DBT_AMOUNT = {"women_ct_monthly": 1250.0, "pension_monthly": 1000.0, "pmkisan_quarterly": 2000.0,
              "wages_irregular": 2500.0, "none": 0.0}  # Rs, ASSUMPTION


def _calibrate_offset(acc, cfg, rng, months) -> float:
    target = cfg.calibration["inoperative_target"]
    lo, hi = -6.0, 6.0
    sub = acc.sample(min(len(acc), 30_000), random_state=0)
    dbt_any = _dbt_schedule(sub["dbt_type"].to_numpy(), months, rng).any(axis=1) & sub["is_dbt_account"].to_numpy()
    for _ in range(30):
        mid = (lo + hi) / 2
        p = _activity_probs(sub, mid)
        p_inop = (1 - p) ** months
        alive = ~sub["deceased"].to_numpy()
        p_inop = np.where(dbt_any & alive & ~sub["migrated"].to_numpy(), p_inop * 0.15, p_inop)
        if p_inop.mean() > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def simulate(cfg: SimConfig | None = None) -> dict:
    """Return a dict of DataFrames: persons, districts, accounts, account_month (last 12 months),
    potential (person x arm probabilities), pilot (randomised pilot with observed outcomes)."""
    cfg = cfg or SimConfig()
    rng = np.random.default_rng(cfg.seed)
    persons, districts = _persons(cfg, rng)
    acc = _accounts(persons, rng, cfg)
    T = cfg.months
    offset = _calibrate_offset(acc, cfg, np.random.default_rng(cfg.seed + 7), T)
    p = _activity_probs(acc, offset)
    n = len(acc)
    active = rng.random((n, T)) < p[:, None]
    dbt = _dbt_schedule(acc["dbt_type"].to_numpy(), T, rng) & acc["is_dbt_account"].to_numpy()[:, None]
    alive_present = (~acc["deceased"].to_numpy()) & (~acc["migrated"].to_numpy() | acc["smartphone"].to_numpy())
    dbt_withdraw = dbt & alive_present[:, None] & (rng.random((n, T)) < 0.85)
    any_txn = active | dbt_withdraw
    n_txn = np.where(active, 1 + rng.poisson(2.0 * sigmoid(acc["z"].to_numpy())[:, None], (n, T)), 0) + dbt_withdraw.astype(int)
    last = np.where(any_txn.any(axis=1), T - 1 - np.argmax(any_txn[:, ::-1], axis=1), -1)
    months_since = np.where(last >= 0, T - 1 - last, T)
    # channel mix per account
    w = np.tile(np.array([0.15, 0.45, 0.2, 0.05, 0.15]), (n, 1))
    w[:, 4] *= np.where(acc["smartphone"], 4.0, np.where(acc["has_phone"], 0.6, 0.05))
    lit = acc["literate"].to_numpy()
    w[:, 0] *= np.where(lit, 1.0, 1.5)
    w[:, 1] *= np.where(lit, 1.0, 1.5) * np.where(acc["rural"], 1.5, 1.0)
    w[:, 2] *= np.where(acc["rural"], 0.5, 1.0)
    w[:, 3] *= np.where(acc["rural"], 0.3, 1.0)
    w /= w.sum(axis=1, keepdims=True)
    retain = np.clip(rng.beta(np.where(lit & acc["smartphone"], 2, 8), np.where(lit & acc["smartphone"], 3, 2)), 0, 1)
    protect = sigmoid(acc["z"].to_numpy() - 1.6)
    has_pmjjby = rng.random(n) < protect * 0.6
    has_pmsby = rng.random(n) < protect * 0.9
    has_apy = rng.random(n) < protect * 0.3
    flip = rng.random(n) < cfg.calibration["data_quality_flip"]
    months_lbl = pd.period_range(end="2026-09", periods=T, freq="M").strftime("%Y-%m").to_numpy()
    rows = []
    amount = np.vectorize(DBT_AMOUNT.get)(acc["dbt_type"].to_numpy())
    for t in range(T - 12, T):
        cnt = n_txn[:, t]
        alloc = rng.multinomial(cnt, w)
        seen = any_txn[:, : t + 1]
        # months since last customer-induced txn as of month t; accounts silent for the whole window
        # are treated as silent since before it (>= 24 months)
        ms = np.where(seen.any(axis=1), np.argmax(seen[:, ::-1], axis=1), T)
        inop_t = ms >= 24
        recent = any_txn[:, max(0, t - 2): t + 1]
        rows.append(pd.DataFrame({
            "account_token": acc["account_token"], "bank_id": acc["bank_id"], "month": months_lbl[t],
            "district_code": acc["district_code"], "is_pmjdy": acc["is_pmjdy"], "gender": acc["gender"],
            "age_band": acc["age_band"], "rural": acc["rural"],
            "n_branch": alloc[:, 0], "n_bc_aeps": alloc[:, 1], "n_atm": alloc[:, 2], "n_pos": alloc[:, 3], "n_upi": alloc[:, 4],
            "n_customer_txn": cnt, "dbt_credit_count": dbt[:, t].astype(int), "dbt_credit_amount": dbt[:, t] * amount,
            "share_dbt_withdrawn_7d": np.where(dbt_withdraw[:, t], retain, 0.0),
            "eom_balance": np.round(np.where(active[:, t], rng.lognormal(6.5, 1.2, n) * (1 - retain), rng.lognormal(3.0, 1.0, n)), 2),
            "months_since_last_customer_txn": ms.astype(int),
            "kyc_due": acc["kyc_due"], "official_inoperative": np.where(flip, ~inop_t, inop_t),
            "rupay_active_90d": (alloc[:, 2] + alloc[:, 3] > 0) | (recent.sum(axis=1) > 1) & (w[:, 2] + w[:, 3] > 0.3),
            "has_pmjjby": has_pmjjby, "has_pmsby": has_pmsby, "has_apy": has_apy,
            "token_credit_count": np.zeros(n, dtype=int), "last_bc_id": acc["bc_id"],
        }))
    account_month = pd.concat(rows, ignore_index=True)
    acc["months_since_last_customer_txn"] = months_since
    acc["inoperative_true"] = months_since >= 24
    acc["active_months_12"] = any_txn[:, -12:].sum(axis=1)
    acc["p_active_month"] = p
    potential = _potential_outcomes(persons, acc, offset)
    pilot = _pilot(persons, potential, cfg, rng)
    return {"persons": persons, "districts": districts, "accounts": acc, "account_month": account_month,
            "potential": potential, "pilot": pilot, "offset": offset, "config": cfg}


def person_state_true(acc: pd.DataFrame) -> pd.Series:
    """Ground-truth-ish best state per person from the 24-month ledger (used only for eval)."""
    s = np.select(
        [acc["months_since_last_customer_txn"] >= 24, acc["months_since_last_customer_txn"] >= 12,
         acc["active_months_12"] >= 6],
        [0, 1, 3], default=2)
    return pd.Series(s, index=acc.index).groupby(acc["person_id"]).max()


def _potential_outcomes(persons: pd.DataFrame, acc: pd.DataFrame, offset: float) -> pd.DataFrame:
    """Ground truth: P(meaningful use over the next 6 months) for each person under each arm.

    Meaningful use = voluntary customer-induced activity (not just DBT cash-out) in >= 3 of the
    next 6 months on any of the person's accounts. Without intervention the monthly probability
    is the person's simulated voluntary activity rate; an arm shifts the logit of the 6-month
    outcome by a heterogeneous tau (ASSUMPTION; magnitudes chosen to sit in the low single-digit
    to ~10 percentage-point range reported for nudges and doorstep services — see research/).
    """
    pm = 1 - (1 - acc["p_active_month"]).groupby(acc["person_id"]).prod().reindex(persons["person_id"]).to_numpy()
    q = np.clip(pm, 0, 1)
    p_y0 = 1 - ((1 - q) ** 6 + 6 * q * (1 - q) ** 5 + 15 * q ** 2 * (1 - q) ** 4)
    best = person_state_true(acc).reindex(persons["person_id"]).to_numpy()  # 0 inop,1 dormant,2 low,3 regular
    kyc_due_any = acc.groupby("person_id")["kyc_due"].max().reindex(persons["person_id"]).to_numpy()
    has_dbt = (persons["dbt_type"] != "none").to_numpy()
    present = ~persons["migrated"].to_numpy()
    alive = ~persons["deceased"].to_numpy()
    female = (persons["gender"] == "F").to_numpy()
    age = persons["age_band"].map({b: i for i, b in enumerate(AGE_BANDS)}).to_numpy()
    lit = persons["literate"].to_numpy()
    phone = persons["has_phone"].to_numpy()
    smart = persons["smartphone"].to_numpy()
    far = persons["dist_bc_km"].to_numpy() > 3
    sakhi = persons["bc_sakhi_present"].to_numpy()
    base = logit(np.clip(p_y0, 0.002, 0.995))
    stuck = np.where(kyc_due_any & (best <= 1), 0.3, 1.0)  # blocked/stale-KYC accounts need a KYC touch first
    regular = np.where(best == 3, 0.3, 1.0)
    tau = {
        "none": np.zeros(len(base)),
        "sms_ivr": phone * (0.10 + 0.20 * lit) * stuck * regular,
        "bc_visit": present * (0.45 + 0.35 * kyc_due_any + 0.25 * (best <= 1) + 0.25 * (female & sakhi) + 0.15 * far + 0.15 * (age == 3)) * regular,
        "upi_onboard": present * phone * (0.25 + 0.45 * smart) * np.array([1.0, 1.0, 0.6, 0.2])[age] * np.where(lit, 1.0, 0.5) * stuck * regular,
        "incentive": present * (0.15 + 0.35 * (has_dbt & (best == 2)) + 0.10 * female) * np.where(best <= 1, 0.4, 1.0) * regular,
    }
    out = pd.DataFrame({"person_id": persons["person_id"]})
    for a in ARMS:
        out[f"p_{a}"] = np.where(alive, sigmoid(base + tau[a]), 0.0)
    out["best_state_true"] = best
    return out


def _pilot(persons, potential, cfg: SimConfig, rng) -> pd.DataFrame:
    """Randomised pilot: a random fraction of persons, arms assigned uniformly; observed binary Y."""
    n = len(persons)
    in_pilot = rng.random(n) < cfg.pilot_fraction
    arm = rng.choice(ARMS, size=n)
    p = potential[[f"p_{a}" for a in ARMS]].to_numpy()
    p_obs = p[np.arange(n), [ARMS.index(a) for a in arm]]
    y = rng.random(n) < p_obs
    return pd.DataFrame({"person_id": persons["person_id"], "in_pilot": in_pilot, "arm": arm, "y": y.astype(int)})
