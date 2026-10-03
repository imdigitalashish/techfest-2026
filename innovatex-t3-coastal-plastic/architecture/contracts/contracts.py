"""Typed contracts for every component of the coastal-plastic system (pydantic v2).

Single source of truth for component inputs/outputs. Owned by the project lead; components
import from here and must not edit it (message the lead to change a contract).

Conventions
- Time: timezone-aware UTC datetimes; hourly series aligned on the hour. UIs display IST.
- Units are in field names (kg, m, m3s = m^3/s, ms = m/s, mm_h = mm/hour, inr).
- Every number that is not measured carries a Provenance whose `kind` says so
  (simulated / synthetic / assumption). Nothing simulated may be presented as observed.
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator

SCHEMA_VERSION = "0.1.0"

ProvenanceKind = Literal[
    "observed",             # measured in the field or by an agency gauge
    "reanalysis",           # e.g. ERA5
    "forecast",             # NWP / tide forecast issued before the fact
    "harmonic_prediction",  # tide predicted from fitted constituents
    "model_output",         # output of one of our components
    "simulated",            # simulated sensor / simulated process (digital twin)
    "synthetic",            # synthetic data generated for testing
    "assumption",           # a chosen parameter, documented in a parameter table
]


class Provenance(BaseModel):
    kind: ProvenanceKind
    source: str = Field(description="URL, dataset id, or 'component:<name>@<git-sha>'")
    retrieved_at: Optional[datetime] = None
    notes: str = ""


# ------------------------------------------------------------------ sites ----
class CatchmentDescriptor(BaseModel):
    area_km2: float = Field(gt=0)
    population: int = Field(ge=0)
    informal_settlement_fraction: float = Field(ge=0, le=1)
    waste_collection_coverage: float = Field(ge=0, le=1)
    runoff_coefficient: float = Field(ge=0, le=1)
    wards: list[str] = []
    provenance: dict[str, Provenance] = Field(default_factory=dict, description="per-field provenance")


class Site(BaseModel):
    site_id: str
    name: str
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    waterbody: str
    outfall_type: Literal["nullah_outfall", "river_mouth", "creek", "beach"]
    tidal: bool
    channel_width_m: float = Field(gt=0)
    boom_length_m: float = Field(ge=0)
    boom_capacity_m3: float = Field(ge=0)
    catchment: CatchmentDescriptor
    provenance: dict[str, Provenance] = Field(default_factory=dict)


# ------------------------------------------------- C1 forcing (tide + rain) ----
class ForcingSeries(BaseModel):
    """C1 output: hourly environmental forcing at a site (real data, labelled)."""
    site_id: str
    t: list[datetime]
    rain_mm_h: list[float]
    tide_m: list[float]
    tide_datum: Literal["CD", "MSL"]
    rain_provenance: Provenance
    tide_provenance: Provenance

    @model_validator(mode="after")
    def _aligned(self):
        if not (len(self.t) == len(self.rain_mm_h) == len(self.tide_m)):
            raise ValueError("t, rain_mm_h and tide_m must have equal length")
        return self


# ------------------------------------------------ C2 catchment plastic load ----
class LoadSeries(BaseModel):
    """C2 output: plastic arriving at the outfall per hour (before interception)."""
    site_id: str
    t: list[datetime]
    items_per_h: list[float]
    kg_per_h: list[float]
    provenance: Provenance


# ----------------------------------------------------- C3 outfall hydraulics ----
class HydraulicSeries(BaseModel):
    """C3 output: flow state at the boom line."""
    site_id: str
    t: list[datetime]
    discharge_m3s: list[float]
    surface_velocity_ms: list[float] = Field(description="signed: + seaward (ebb/outflow), - landward (flood tide)")
    water_level_m: list[float]
    provenance: Provenance


# ------------------------------------------------------- C4 interceptor model ----
class InterceptorSeries(BaseModel):
    """C4 output: hourly mass balance at the barrier (kg).
    Invariant: arrived = captured + escaped_entrainment + escaped_overtopping + escaped_bypass;
    stored(t) = stored(t-1) + captured - refloated - cleared >= 0."""
    site_id: str
    t: list[datetime]
    arrived_kg: list[float]
    captured_kg: list[float]
    escaped_entrainment_kg: list[float]
    escaped_overtopping_kg: list[float]
    escaped_bypass_kg: list[float]
    refloated_kg: list[float]
    cleared_kg: list[float]
    stored_kg: list[float]
    fill_fraction: list[float]
    provenance: Provenance


# ------------------------------------------------------ C5 vision detector -----
class Detection(BaseModel):
    bbox_xyxy: tuple[float, float, float, float] = Field(description="pixels, image coordinates")
    label: str
    score: float = Field(ge=0, le=1)


class FrameDetections(BaseModel):
    """C5 output for one frame."""
    frame_id: str
    t: Optional[datetime] = None
    image_wh: tuple[int, int]
    detections: list[Detection]
    model_id: str = Field(description="weights name + git sha / file hash")
    latency_ms: Optional[float] = None


# --------------------------------------------------------- C6 flux counter -----
class FluxEstimate(BaseModel):
    """C6 output: items crossing the counting line in a window, converted to mass."""
    site_id: str
    t_start: datetime
    t_end: datetime
    items_crossed: int = Field(ge=0)
    items_per_min: float = Field(ge=0)
    by_label: dict[str, int] = {}
    est_kg: float = Field(ge=0)
    est_kg_ci90: tuple[float, float]
    method: str
    provenance: Provenance


# --------------------------------------------------------- C7 fill estimator ----
class FillEstimate(BaseModel):
    site_id: str
    t: datetime
    fill_fraction: float = Field(ge=0, le=1)
    covered_area_m2: Optional[float] = None
    method: Literal["camera_segmentation", "range_sensor", "fused", "simulated"]
    confidence: float = Field(ge=0, le=1)
    provenance: Provenance


# ------------------------------------------------ C8 edge telemetry message -----
class SiteTelemetry(BaseModel):
    """C8: message from an edge node (MQTT/HTTPS JSON). Twin output must set simulated=True."""
    schema_version: str = SCHEMA_VERSION
    site_id: str
    t: datetime
    simulated: bool
    battery_v: Optional[float] = None
    solar_w: Optional[float] = None
    water_level_m: Optional[float] = None
    rain_mm_last_h: Optional[float] = None
    fill: Optional[FillEstimate] = None
    flux: Optional[FluxEstimate] = None
    health: list[str] = Field(default_factory=list, description="e.g. lens_dirty, low_battery, tamper")


# ----------------------------------------------------- C9 risk forecaster -------
class SiteForecast(BaseModel):
    site_id: str
    issued_at: datetime
    horizon_h: int = Field(gt=0)
    p_overflow: float = Field(ge=0, le=1, description="P(barrier overflows or must release within horizon)")
    expected_arrival_kg: float = Field(ge=0)
    expected_fill_fraction: float = Field(ge=0)
    drivers: dict[str, float] = Field(default_factory=dict, description="e.g. rain_mm_next_24h, max_tide_m")
    provenance: Provenance


# ----------------------------------------------------- C10 dispatch planner -----
class Crew(BaseModel):
    crew_id: str
    base_site_id: str
    shift_start_h: int = Field(ge=0, le=23, description="local IST hour")
    shift_hours: float = Field(gt=0)
    clear_rate_kg_per_h: float = Field(gt=0)


class Assignment(BaseModel):
    crew_id: str
    site_id: str
    start: datetime
    end: datetime
    expected_cleared_kg: float = Field(ge=0)
    reason: str = ""


class DispatchPlan(BaseModel):
    plan_id: str
    issued_at: datetime
    policy_id: str
    assignments: list[Assignment]
    objective: dict[str, float] = Field(default_factory=dict)


# --------------------------------------------------------- C11 MRV ledger -------
class ClearanceRecord(BaseModel):
    site_id: str
    crew_id: str
    t_start: datetime
    t_end: datetime
    claimed_wet_kg: float = Field(ge=0, description="what the contractor/crew reports")
    weighbridge_wet_kg: Optional[float] = None
    pre_fill_fraction: Optional[float] = None
    post_fill_fraction: Optional[float] = None
    photo_sha256: list[str] = []
    gps_track_sha256: Optional[str] = None


class Reconciliation(BaseModel):
    sensor_estimated_kg: float
    claimed_kg: float
    ratio: float
    flag: Literal["ok", "review", "reject"]
    reasons: list[str] = []


class LedgerEntry(BaseModel):
    seq: int = Field(ge=0)
    record: ClearanceRecord
    reconciliation: Reconciliation
    prev_hash: str
    hash: str = Field(description="sha256 over canonical JSON of (seq, record, reconciliation, prev_hash)")


# ----------------------------------------------- C13 recovery & upcycling -------
class CatchComposition(BaseModel):
    site_id: str
    period_start: datetime
    period_end: datetime
    wet_kg: float = Field(ge=0)
    fractions: dict[str, float] = Field(description="category -> mass fraction, sums to 1")
    provenance: Provenance


class RecoveryRoute(BaseModel):
    category: str
    route: Literal["mechanical_recycling", "co_processing", "waste_to_energy", "landfill", "organic_compost"]
    kg: float = Field(ge=0)
    epr_category: Optional[Literal["I", "II", "III", "IV"]] = None
    value_inr: Optional[float] = None
    value_provenance: Optional[Provenance] = None


# ------------------------------------------------ C14 source attribution --------
class WardHotspot(BaseModel):
    ward: str
    share_of_load: float = Field(ge=0, le=1)
    rank: int = Field(ge=1)
    evidence: str
    provenance: Provenance


# ------------------------------------------------- C12 dashboard bundle ---------
class DashboardBundle(BaseModel):
    """Everything the static dashboard reads (one JSON file)."""
    schema_version: str = SCHEMA_VERSION
    generated_at: datetime
    git_sha: str
    sites: list[Site]
    forcing: list[ForcingSeries] = []
    interceptor: list[InterceptorSeries] = []
    forecasts: list[SiteForecast] = []
    plans: list[DispatchPlan] = []
    telemetry: list[SiteTelemetry] = []
    ledger: list[LedgerEntry] = []
    metrics: dict[str, dict[str, Union[float, str]]] = Field(
        default_factory=dict, description="component -> {metric: value, 'reproduce': command}")
    disclaimers: list[str] = Field(default_factory=lambda: [
        "Values marked SIMULATED come from the digital twin, not from field hardware.",
    ])
