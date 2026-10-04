"""Poshan Setu — canonical inter-component contracts (pydantic v2).

Every component consumes and emits only these types (record-level) or the frame
specs in `frames.py` (batch-level, same field names). Changing a contract needs an
ADR in `architecture/adr/`.

Design rules encoded here:
- Two planes. The *identity plane* (IdentityRecord, LinkDecision) never leaves the
  state identity vault. The *analytics plane* sees only the pseudonymous `child_key`.
  Names reappear only at the edge, inside the frontline worker's own app, via
  `WorklistItem.child_local_ref` (the beneficiary ID that app already holds).
- Every artefact carries `synthetic` so simulator output can never pass as real data.
- Every access to child data is an AccessRequest -> AccessDecision (policy_gate) and
  every decision/action is an AuditEntry (audit_ledger).
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

CONTRACT_VERSION = "0.2.0"


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


# --------------------------------------------------------------------------- enums
class Sex(str, Enum):
    MALE = "M"
    FEMALE = "F"


class SourceSystem(str, Enum):
    POSHAN_TRACKER = "poshan_tracker"  # MWCD ICDS app used by Anganwadi workers
    RCH = "rch"  # MoHFW RCH portal / ANMOL (ANM tablets)
    UWIN = "uwin"  # MoHFW U-WIN immunisation registry
    ABDM = "abdm"  # ABDM health-information exchange (FHIR bundles, consent-gated)
    NRC = "nrc"  # Nutrition Rehabilitation Centre records
    SIMULATOR = "simulator"  # synthetic data for evaluation only


class Role(str, Enum):
    AWW = "aww"  # Anganwadi worker (one AWC)
    ASHA = "asha"  # Accredited Social Health Activist (village)
    ANM = "anm"  # Auxiliary Nurse Midwife (sub-centre)
    LS = "ls"  # Lady Supervisor / Mukhya Sevika (sector of AWCs)
    CDPO = "cdpo"  # Child Development Project Officer (ICDS project ~ block)
    MO_PHC = "mo_phc"  # Medical Officer, PHC / block health
    DPO = "dpo"  # District Programme Officer (ICDS)
    DM = "dm"  # District Magistrate / Collector (district convergence)
    STATE = "state"
    PUBLIC = "public"
    RESEARCHER = "researcher"
    SYSTEM = "system"  # automated components


class Purpose(str, Enum):
    SERVICE_DELIVERY = "service_delivery"  # ICDS benefit/service to this child
    CARE_COORDINATION = "care_coordination"  # ICDS <-> health referral and follow-up
    SUPERVISION = "supervision"  # data quality and supportive supervision
    PROGRAMME_MONITORING = "programme_monitoring"  # aggregates for review meetings
    PUBLIC_REPORTING = "public_reporting"
    RESEARCH = "research"
    MODEL_TRAINING = "model_training"
    EMPLOYMENT_ACTION = "employment_action"  # HR, pay, transfer, disciplinary use of any data — always denied (ADR 002)
    OTHER = "other"  # always denied


class DataCategory(str, Enum):
    IDENTIFIED_CHILD = "identified_child"  # names, contact, address
    PSEUDONYMOUS_CHILD = "pseudonymous_child"  # child_key-level measurements/events
    RISK_SCORE = "risk_score"
    HEALTH_RECORD = "health_record"  # pulled from the health system (ABDM/RCH/U-WIN)
    AGGREGATE = "aggregate"


class ScopeLevel(str, Enum):
    AWC = "awc"
    VILLAGE = "village"
    SECTOR = "sector"
    PROJECT = "project"  # ICDS project ~ block
    DISTRICT = "district"
    STATE = "state"
    NATIONAL = "national"


# --------------------------------------------------------------------------- shared
class Provenance(Strict):
    source: SourceSystem
    source_record_id: str
    extracted_at: datetime
    synthetic: bool = Field(description="True for simulator-derived records; propagates to derived artefacts")


class GeoUnit(Strict):
    """ICDS administrative hierarchy (codes are opaque strings)."""

    state_code: str
    district_code: str
    project_code: str  # ICDS project (CDPO) ~ block
    sector_code: str  # Lady Supervisor's sector
    awc_code: str
    village_code: Optional[str] = None


# --------------------------------------------------------------- identity plane only
class IdentityRecord(Strict):
    """Quasi-identifiers of one child record in one source system. Identity vault only."""

    source: SourceSystem
    source_record_id: str
    child_name: Optional[str] = None
    mother_name: Optional[str] = None
    father_name: Optional[str] = None
    dob: Optional[date] = None
    sex: Optional[Sex] = None
    village_code: Optional[str] = None
    awc_code: Optional[str] = None
    facility_code: Optional[str] = None
    mobile_hash: Optional[str] = None
    shared_ids: dict[str, str] = Field(
        default_factory=dict,
        description="Tokens such as rch_id, uwin_id, abha_number_token, pt_beneficiary_id. Never raw Aadhaar.",
    )
    synthetic: bool


class LinkDecision(Strict):
    child_key: str = Field(description="Pseudonymous key: HMAC-SHA256(vault_key, cluster id); stable across sources")
    members: list[tuple[SourceSystem, str]]
    method: Literal["deterministic", "probabilistic", "clerical_review", "singleton"]
    match_probability: float = Field(ge=0, le=1)
    synthetic: bool


# ---------------------------------------------------------- analytics plane (pseudo)
class MeasurementEvent(Strict):
    event_id: str
    child_key: str
    geo: GeoUnit
    sex: Sex
    dob: date
    measured_on: date
    weight_kg: Optional[float] = Field(None, gt=0, lt=80)
    length_height_cm: Optional[float] = Field(None, gt=20, lt=200)
    measure_position: Optional[Literal["recumbent", "standing"]] = None
    muac_cm: Optional[float] = Field(None, gt=3, lt=40)
    oedema: Optional[bool] = None
    measured_by: str = Field(description="Pseudonymous worker id (for worker-level credibility)")
    provenance: Provenance


HealthEventKind = Literal[
    "birth_weight",  # value in kg
    "preterm_birth",
    "immunisation_given",
    "immunisation_missed",  # dose overdue beyond schedule window (U-WIN)
    "illness_diarrhoea",
    "illness_ari",
    "hospitalisation",
    "nrc_admission",
    "nrc_discharge",
    "maternal_anaemia",  # value = Hb g/dL
    "maternal_short_stature",  # value = height cm
    "maternal_low_bmi",  # value = BMI
    "asha_home_visit",
]


class HealthEvent(Strict):
    event_id: str
    child_key: str
    occurred_on: date
    kind: HealthEventKind
    value: Optional[float] = None
    unit: Optional[str] = None
    provenance: Provenance


ServiceEventKind = Literal[
    "thr_received",  # take-home ration
    "hcm_received",  # hot-cooked meal
    "home_visit",
    "counselling",
    "referral_made",
    "referral_completed",
]


class ServiceEvent(Strict):
    event_id: str
    child_key: str
    occurred_on: date
    kind: ServiceEventKind
    provenance: Provenance


ZName = Literal["waz", "lhaz", "wlhz", "baz", "muacz"]


class AnthroZ(Strict):
    """WHO 2006 Child Growth Standards z-scores for one MeasurementEvent."""

    event_id: str
    child_key: str
    age_days: int = Field(ge=0)
    waz: Optional[float] = None
    lhaz: Optional[float] = None
    wlhz: Optional[float] = None
    baz: Optional[float] = None
    muacz: Optional[float] = None
    flags: list[ZName] = Field(default_factory=list, description="WHO biologically-implausible flags")
    nutrition_status: Literal["sam", "mam", "normal", "unknown"]
    stunting: Literal["severe", "moderate", "none", "unknown"]
    underweight: Literal["severe", "moderate", "none", "unknown"]
    standard: Literal["WHO-2006"] = "WHO-2006"


class VelocityZ(Strict):
    """WHO 2009 growth-velocity z-score between two measurements of the same child."""

    child_key: str
    from_event_id: str
    to_event_id: str
    interval_months: int = Field(ge=1, le=6)
    weight_velocity_z: Optional[float] = None
    length_velocity_z: Optional[float] = None
    standard: Literal["WHO-2009-velocity"] = "WHO-2009-velocity"


class QualityFinding(Strict):
    code: str  # e.g. WHO_FLAG_WLHZ, HEIGHT_DECREASE, COPY_FORWARD, TERMINAL_DIGIT_0_5
    severity: Literal["info", "warn", "reject"]
    detail: str


class RecordQuality(Strict):
    event_id: str
    findings: list[QualityFinding] = Field(default_factory=list)
    usable: bool
    confidence: float = Field(ge=0, le=1, description="Probability the record reflects a true measurement")


class UnitCredibility(Strict):
    unit_type: Literal["awc", "worker", "sector", "project", "district"]
    unit_id: str
    period: str = Field(pattern=r"^\d{4}-\d{2}$")
    n_measurements: int = Field(ge=0)
    indices: dict[str, float] = Field(description="Named indices; definitions in components/credibility_engine/README.md")
    credibility: float = Field(ge=0, le=1)
    band: Literal["high", "medium", "low", "insufficient_data"]
    recommended_action: Literal["none", "remeasure_sample", "supportive_supervision", "equipment_check"]
    synthetic: bool


class ReasonCode(Strict):
    code: str  # e.g. WEIGHT_VELOCITY_LOW, NO_GAIN_2M, LBW, MISSED_VACCINE, PRIOR_WASTING
    text_en: str
    text_hi: str
    weight: float = Field(description="Signed contribution to the score (model-specific scale)")


class RiskScore(Strict):
    child_key: str
    awc_code: str
    as_of: date
    horizon_days: int = Field(gt=0)
    target: Literal["incident_wasting", "incident_sam"]
    probability: float = Field(ge=0, le=1)
    rank_in_awc: int = Field(ge=1)
    reasons: list[ReasonCode]
    data_confidence: float = Field(ge=0, le=1)
    model_version: str
    synthetic: bool


class AlertKind(str, Enum):
    SAM = "sam"
    MAM = "mam"
    RISK_HIGH = "risk_high"
    GROWTH_FALTERING = "growth_faltering"
    DATA_RECHECK = "data_recheck"
    HEALTH_SIGNAL = "health_signal"


class Alert(Strict):
    alert_id: str
    child_key: Optional[str] = None  # None for unit-level alerts (e.g. DATA_RECHECK on an AWC)
    geo: GeoUnit
    kind: AlertKind
    severity: int = Field(ge=1, le=4, description="4 = most urgent")
    created_on: date
    evidence: list[str] = Field(default_factory=list)
    recommended_action: str
    synthetic: bool


class TaskTransition(Strict):
    on: date
    from_status: str
    to_status: str
    by_role: Role
    note: str = ""


class Task(Strict):
    task_id: str
    alert_id: str
    owner_role: Role
    owner_scope_id: str  # awc / sector / project / facility code
    action: str
    due_on: date
    status: Literal["open", "done", "escalated", "closed"]
    escalation_level: int = Field(ge=0)
    protocol_ref: str = Field(description="Which protocol step this task implements (citation key)")
    history: list[TaskTransition] = Field(default_factory=list)


class AccessRequest(Strict):
    request_id: str
    actor_id: str
    actor_role: Role
    actor_scope_level: ScopeLevel
    actor_scope_id: str
    purpose: Purpose
    data_category: DataCategory
    subject_child_key: Optional[str] = None
    subject_scope_id: Optional[str] = None  # unit whose data is requested
    consent_artefact_id: Optional[str] = None
    requested_at: datetime


class AccessDecision(Strict):
    request_id: str
    decision: Literal["allow", "allow_transformed", "deny"]
    transform: Literal["none", "pseudonymise", "aggregate", "suppress_small_cells", "dp_noise"]
    legal_basis: Optional[str] = Field(None, description="Citation, e.g. 'DPDP Act 2023 s.7(b)'")
    rule_id: str
    reason: str
    policy_version: str


class AuditEntry(Strict):
    seq: int = Field(ge=0)
    ts: datetime
    actor_id: str
    action: str
    object_ref: str
    decision_ref: Optional[str] = None
    prev_hash: str
    hash: str


class AggregateCell(Strict):
    geo_level: ScopeLevel
    geo_id: str
    period: str
    indicator: str  # e.g. wasting_prev, stunting_prev, sam_open_tasks, sla_breach_rate
    numerator: Optional[int] = None
    denominator: Optional[int] = None
    value: Optional[float] = None
    suppressed: bool
    mechanism: Literal["exact", "small_cell_suppressed", "dp_laplace", "dp_gaussian"]
    epsilon: Optional[float] = None
    credibility_adjusted: bool = False
    synthetic: bool


class WorklistItem(Strict):
    child_local_ref: str = Field(description="Beneficiary id inside the worker's own app; resolved to a name on-device")
    task_id: str
    action: str
    due_on: date
    priority: int = Field(ge=1)
    reason_en: str
    reason_hi: str


class Worklist(Strict):
    worker_role: Role
    worker_id: str
    scope_id: str
    week_of: date
    capacity: int = Field(ge=0, description="Max items the worker can act on this week")
    items: list[WorklistItem]
    synthetic: bool
