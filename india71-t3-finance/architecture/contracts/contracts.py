"""Typed contracts for Sakriya components (pydantic v2).

Each *Row model describes one record of a batch table that components exchange as a
pandas DataFrame. `validate_frame(df, Model)` checks columns and validates rows.
Run `python architecture/contracts/export_schema.py` to regenerate JSON Schemas.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)


# ---------- shared enums ----------
class Gender(str, Enum):
    F = "F"
    M = "M"
    O = "O"


class AgeBand(str, Enum):
    A18_25 = "18-25"
    A26_40 = "26-40"
    A41_60 = "41-60"
    A60P = "60+"


class UsageState(str, Enum):
    NO_USE_24M = "no_use_24m"      # behavioural: no customer-induced txn for 24 months. NOT the RBI legal status
                                   # (see AccountUsage.regulatory_inoperative; DBT/scholarship-purpose accounts are exempt)
    DORMANT_RISK = "dormant_risk"  # no customer-induced txn for 12-23 months
    PASS_THROUGH = "pass_through"  # inflows (mostly DBT) cashed out fast; little other use
    BASIC = "basic"                # some customer-induced use, below "meaningful"
    MEANINGFUL = "meaningful"      # sustained, diverse, customer-induced use


STATE_ORDER = ["no_use_24m", "dormant_risk", "pass_through", "basic", "meaningful"]


class Arm(str, Enum):
    NONE = "none"
    SMS_IVR = "sms_ivr"            # voice/IVR or SMS nudge in local language
    BC_VISIT = "bc_visit"          # BC / BC Sakhi doorstep visit: re-KYC + first transaction
    UPI_ONBOARD = "upi_onboard"    # assisted UPI / UPI 123PAY onboarding by BC
    INCENTIVE = "incentive"        # small first-transactions incentive


ARMS = [a.value for a in Arm]


# ---------- C1 -> C2, C3 ----------
class AccountMonth(Strict):
    account_token: str
    bank_id: str
    month: str = Field(pattern=r"^\d{4}-\d{2}$")
    district_code: int
    is_pmjdy: bool
    gender: Gender
    age_band: AgeBand
    rural: bool
    n_branch: int = Field(ge=0)
    n_bc_aeps: int = Field(ge=0)
    n_atm: int = Field(ge=0)
    n_pos: int = Field(ge=0)
    n_upi: int = Field(ge=0)
    n_customer_txn: int = Field(ge=0)
    dbt_credit_count: int = Field(ge=0)
    dbt_credit_amount: float = Field(ge=0)
    share_dbt_withdrawn_7d: float = Field(ge=0, le=1)
    eom_balance: float
    months_since_last_customer_txn: int = Field(ge=0)
    kyc_due: bool
    official_inoperative: bool = Field(description="CBS flag set by the bank under RBI rules (DBT-purpose accounts exempt)")
    opened_for_dbt: bool = Field(description="account opened to receive DBT/scholarship credits (RBI/2023-24/105 Annex para 3)")
    rupay_active_90d: bool
    has_pmjjby: bool
    has_pmsby: bool
    has_apy: bool
    token_credit_count: int = Field(ge=0, description="credits <= Rs 10 not initiated by the customer")
    last_bc_id: Optional[str] = None


# ---------- C2 -> C3, C10 ----------
class AccountUsage(Strict):
    account_token: str
    bank_id: str
    as_of_month: str = Field(pattern=r"^\d{4}-\d{2}$")
    state: UsageState
    mus: float = Field(ge=0, le=100, description="Meaningful Usage Score")
    frequency: float = Field(ge=0, le=1)
    diversity: float = Field(ge=0, le=1)
    retention: float = Field(ge=0, le=1)
    protection: float = Field(ge=0, le=1)
    reason_codes: str = Field(description="semicolon-separated rule ids")
    regulatory_inoperative: bool = Field(description="RBI legal status as flagged in CBS; independent of the behavioural state")


# ---------- C3 -> C6, C10 (clean room only) ----------
class AccountPersonLink(Strict):
    account_token: str
    bank_id: str
    person_token: str


class PersonUsage(Strict):
    person_token: str
    n_accounts: int = Field(ge=1)
    best_state: UsageState
    dbt_account_token: Optional[str] = None
    any_meaningful: bool
    district_code: int
    gender: Gender
    age_band: AgeBand
    rural: bool


# ---------- C5 ----------
class Role(str, Enum):
    BANK = "bank"                  # account-holding bank (data fiduciary)
    BC = "bc"                      # business correspondent acting for that bank
    NPCI = "npci"
    DBT_MISSION = "dbt_mission"    # incl. scheme departments / PFMS
    DFS = "dfs"
    RBI = "rbi"
    SLBC = "slbc"
    LDM = "ldm"                    # lead district manager / DLCC
    STATE_GOVT = "state_govt"
    RESEARCHER = "researcher"
    PUBLIC = "public"


class Granularity(str, Enum):
    ACCOUNT = "account"
    PERSON = "person"
    BC_AREA = "bc_area"
    BRANCH = "branch"
    BLOCK = "block"
    DISTRICT = "district"
    STATE = "state"
    NATIONAL = "national"


class AccessRequest(Strict):
    request_id: str
    requester_role: Role
    requester_id: str
    purpose: str
    data_elements: list[str]
    granularity: Granularity
    legal_basis: str
    own_customers_only: bool = False  # caller's claim; the engine re-derives it from identity
    subject_bank_id: Optional[str] = None  # whose customers the data concern (bank/BC requests)


class Obligations(Strict):
    dp_epsilon: Optional[float] = None
    min_cell_size: Optional[int] = None
    retention_days: Optional[int] = None
    masked_fields: list[str] = []


class AccessDecision(Strict):
    request_id: str
    allow: bool
    obligations: Obligations
    rule_ids: list[str]
    reason: str


class AuditEntry(Strict):
    seq: int
    request_id: str
    decision: bool
    payload_sha256: str
    prev_hash: str
    entry_hash: str


# ---------- C6 ----------
class TargetingRequest(Strict):
    budget_inr: float = Field(gt=0)
    arm_costs_inr: dict[str, float]
    min_share_women: float = Field(default=0.0, ge=0, le=1)
    max_tasks_per_bc: Optional[int] = None
    holdout_fraction: float = Field(default=0.1, ge=0, lt=1)
    seed: int = 0


class TargetingFeatures(Strict):
    person_token: str
    account_token: str
    bank_id: str
    district_code: int
    gender: Gender
    age_band: AgeBand
    rural: bool
    state: UsageState
    mus: float
    n_accounts: int
    months_since_last_customer_txn: int
    kyc_due: bool
    is_dbt_account: bool
    dbt_monthly: bool
    share_dbt_withdrawn_7d: float
    has_phone: bool
    smartphone: bool
    literate: bool
    dist_bc_km: float
    bc_sakhi_present: bool


class InterventionPlanRow(Strict):
    person_token: str
    account_token: str
    bank_id: str
    arm: Arm
    expected_uplift: float
    cost_inr: float = Field(ge=0)
    priority_rank: int = Field(ge=1)
    in_holdout: bool
    reason_codes: str


# ---------- C7 ----------
class SafetyDecision(Strict):
    account_token: str
    decision: str = Field(pattern=r"^(allow|verify|hold)$")
    risk_score: float = Field(ge=0, le=1)
    reasons: str


# ---------- C8 ----------
class ChannelTask(Strict):
    task_id: str
    account_token: str
    arm: Arm
    channel: str
    assigned_bc_id: Optional[str] = None
    language: str
    due_date: str


class InterventionEvent(Strict):
    task_id: str
    account_token: str
    arm: Arm
    status: str = Field(pattern=r"^(delivered|contacted|completed|failed)$")
    timestamp: str
    cost_inr: float = Field(ge=0)


# ---------- C9 ----------
class EffectEstimate(Strict):
    arm: Arm
    segment: str
    implementer_id: Optional[str] = None
    ate: float
    se: float = Field(ge=0)
    ci_low: float
    ci_high: float
    n_treated: int = Field(ge=0)
    n_control: int = Field(ge=0)
    method: str


# ---------- C10 ----------
class ScorecardRow(Strict):
    unit_type: str = Field(pattern=r"^(district|bank|branch|bc)$")
    unit_id: str
    period: str
    persons: int = Field(ge=0)
    mu_rate: float = Field(ge=0, le=1)
    inactive_rate: float = Field(ge=0, le=1)
    gender_gap_pp: float
    enrolments: int = Field(ge=0)
    incremental_usage: float
    incremental_ci_low: float
    incremental_ci_high: float
    gaming_flags: str


# ---------- C11 ----------
class DPRelease(Strict):
    table: str
    epsilon: float = Field(gt=0)
    mechanism: str
    min_cell_size: int = Field(ge=0)
    rows: list[dict]
    budget_spent_total: float = Field(ge=0)


# ---------- C13 ----------
class DistrictGapRow(Strict):
    state: str
    district: str
    women_own_account_use_nfhs5: float = Field(ge=0, le=100)
    women_own_account_use_nfhs4: Optional[float] = Field(default=None, ge=0, le=100)
    change_pp: Optional[float] = None
    women_mobile_own_use_nfhs5: Optional[float] = None
    women_literate_nfhs5: Optional[float] = None
    gap_rank: int = Field(ge=1)


ROW_MODELS = [
    AccountMonth, AccountUsage, AccountPersonLink, PersonUsage, AccessRequest, AccessDecision,
    AuditEntry, TargetingRequest, TargetingFeatures, InterventionPlanRow, SafetyDecision,
    ChannelTask, InterventionEvent, EffectEstimate, ScorecardRow, DPRelease, DistrictGapRow,
]


def validate_frame(df, model: type[BaseModel], sample: int | None = 2000, seed: int = 0) -> int:
    """Check that df has exactly the model's required columns and that rows validate.

    Validates all rows if len(df) <= sample, else a random sample. Returns rows checked.
    Raises ValueError on the first violation.
    """
    fields = model.model_fields
    required = {k for k, f in fields.items() if f.is_required()}
    cols = set(df.columns)
    missing = required - cols
    extra = cols - set(fields)
    if missing or extra:
        raise ValueError(f"{model.__name__}: missing={sorted(missing)} extra={sorted(extra)}")
    rows = df if sample is None or len(df) <= sample else df.sample(sample, random_state=seed)
    for rec in rows.to_dict(orient="records"):
        clean = {k: (None if _isnan(v) else _py(v)) for k, v in rec.items()}
        model.model_validate(clean)
    return len(rows)


def _isnan(v) -> bool:
    try:
        return v != v  # NaN check without numpy
    except Exception:
        return False


def _py(v):
    if hasattr(v, "item"):
        return v.item()
    return v
