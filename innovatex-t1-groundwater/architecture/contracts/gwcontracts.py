"""Typed contracts between components — the single source of truth.

Every component consumes and produces only these models. JSON Schemas in `schemas/`
are generated from this file (do not edit them by hand):

    innovatex-t1-groundwater/.venv/bin/python innovatex-t1-groundwater/architecture/contracts/export_schemas.py

Conventions
- Timestamps are timezone-aware UTC. (India-WRIS publishes IST wall-clock; ingest converts.)
- Depth to water is metres below ground level (mbgl, positive downwards).
  Drawdown is metres, positive = water level going DOWN.
- Every observation carries `provenance` (real / simulated / derived); the UI must show it.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

CONTRACTS_VERSION = "0.3.0"


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


def _utc(v: datetime) -> datetime:
    if v.tzinfo is None or v.utcoffset() is None or v.utcoffset().total_seconds() != 0:
        raise ValueError("timestamp must be timezone-aware UTC")
    return v


# ----------------------------------------------------------------------------- enums
class Provenance(str, Enum):
    real = "real"            # agency measurement (CGWB, Delhi GW/DJB, USGS) or reanalysis (ERA5)
    simulated = "simulated"  # sensor simulator output — always labelled SIMULATED in the UI
    derived = "derived"      # computed by a component from other observations


class Variable(str, Enum):
    depth_to_water_m = "depth_to_water_m"   # mbgl
    water_column_m = "water_column_m"       # water above the sensor (pit/shaft level)
    abs_pressure_hpa = "abs_pressure_hpa"   # non-vented transducer reading
    baro_pressure_hpa = "baro_pressure_hpa"
    water_temp_c = "water_temp_c"
    ec_us_cm = "ec_us_cm"                   # specific conductance at 25 °C
    pump_current_a = "pump_current_a"       # RMS current on the pump supply
    vibration_g_rms = "vibration_g_rms"     # casing-head vibration, band-limited RMS
    rain_mm = "rain_mm"
    et0_mm = "et0_mm"
    battery_v = "battery_v"


UNITS: dict[str, str] = {
    "depth_to_water_m": "m", "water_column_m": "m", "abs_pressure_hpa": "hPa",
    "baro_pressure_hpa": "hPa", "water_temp_c": "degC", "ec_us_cm": "uS/cm",
    "pump_current_a": "A", "vibration_g_rms": "g", "rain_mm": "mm", "et0_mm": "mm", "battery_v": "V",
}


class QCFlag(str, Enum):
    unchecked = "unchecked"
    good = "good"
    suspect = "suspect"
    bad = "bad"
    filled = "filled"


class QCReason(str, Enum):
    spike = "spike"
    flatline = "flatline"
    drift = "drift"
    out_of_range = "out_of_range"
    gap = "gap"
    step = "step"
    duplicate = "duplicate"


class DeviceRole(str, Enum):
    """One node design, three deployments (see architecture/components.md)."""
    sentinel = "sentinel"              # observation well / piezometer: level (+EC, temp)
    recharge_meter = "recharge_meter"  # RWH recharge pit/shaft: water column + rain
    seal_guard = "seal_guard"          # sealed (or metered) borewell: vibration + pump current + lid switch


class AquiferType(str, Enum):
    alluvium_unconfined = "alluvium_unconfined"
    alluvium_confined = "alluvium_confined"
    hard_rock_fractured = "hard_rock_fractured"
    unknown = "unknown"


# ----------------------------------------------------------------------------- metadata
class StationMeta(_Strict):
    station_id: str
    name: str
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    district: Optional[str] = None
    agency: Optional[str] = None
    telemetric: Optional[bool] = None
    role: Optional[DeviceRole] = None          # None = existing agency station (not our node)
    aquifer: AquiferType = AquiferType.unknown
    provenance: Provenance = Provenance.real
    source: str


class AquiferParams(_Strict):
    """Parameters for analytic (Theis/Hantush) drawdown models. Ranges with sources, not truths."""
    aquifer: AquiferType
    transmissivity_m2d: float = Field(gt=0)
    storativity: float = Field(gt=0, lt=1, description="S (confined) or Sy (unconfined)")
    leakage_factor_m: Optional[float] = Field(default=None, gt=0)
    source: str


# ----------------------------------------------------------------------------- observations
class Series(_Strict):
    """Columnar batch: one variable at one station. The unit of exchange between analytics."""
    station_id: str
    variable: Variable
    unit: str
    provenance: Provenance
    source: str
    ts: list[datetime]
    values: list[Optional[float]]
    qc_flags: Optional[list[QCFlag]] = None

    @model_validator(mode="after")
    def _check(self) -> "Series":
        if UNITS[self.variable.value] != self.unit:
            raise ValueError(f"unit {self.unit!r} != {UNITS[self.variable.value]!r} for {self.variable.value}")
        if len(self.ts) != len(self.values):
            raise ValueError("ts and values must have equal length")
        if self.qc_flags is not None and len(self.qc_flags) != len(self.ts):
            raise ValueError("qc_flags must match ts length")
        for t in self.ts:
            _utc(t)
        if any(b <= a for a, b in zip(self.ts, self.ts[1:])):
            raise ValueError("ts must be strictly increasing")
        return self


# ----------------------------------------------------------------------------- node -> edge -> link
class Channel(str, Enum):
    abs_pressure = "abs_pressure"   # hPa
    baro = "baro"                   # hPa
    water_temp = "water_temp"       # degC
    ec = "ec"                       # uS/cm
    pump_current = "pump_current"   # A rms
    vibration = "vibration"         # g rms
    lid = "lid"                     # 0 closed / 1 open
    battery = "battery"             # V


class RawSample(_Strict):
    """sensor front-end -> edge firmware: one raw reading."""
    device_id: str
    ts: datetime
    channel: Channel
    value: float
    _v = field_validator("ts")(_utc)


class EdgeEventKind(str, Enum):
    pump_on = "pump_on"
    pump_off = "pump_off"
    level_rise = "level_rise"       # recharge inflow started
    level_step = "level_step"
    lid_open = "lid_open"
    tamper = "tamper"               # cable cut / sensor out of water / enclosure opened
    low_battery = "low_battery"


class EdgeEvent(_Strict):
    kind: EdgeEventKind
    ts: datetime
    value: Optional[float] = None
    _v = field_validator("ts")(_utc)


class ChannelBlock(_Strict):
    """Fixed-interval block: value_i = offset + scale * (first + cumsum([0] + deltas))_i."""
    channel: Channel
    scale: float = Field(gt=0)
    offset: float
    first: int
    deltas: list[int]


class UplinkFrame(_Strict):
    """edge firmware -> telemetry link -> ingest. Mirrors a LoRaWAN / NB-IoT application payload."""
    device_id: str
    role: DeviceRole
    fcnt: int = Field(ge=0)
    t0: datetime
    period_s: int = Field(gt=0)
    blocks: list[ChannelBlock]
    events: list[EdgeEvent] = []
    battery_mv: int = Field(ge=0)
    payload_bytes: int = Field(ge=0)
    _v = field_validator("t0")(_utc)


class DeliveryReport(_Strict):
    """telemetry-link outcome for one frame (radio + network model, or real network logs)."""
    device_id: str
    fcnt: int
    delivered: bool
    attempts: int = Field(ge=1)
    latency_s: Optional[float] = None
    energy_mj: float = Field(ge=0)
    link: Literal["lorawan", "nbiot", "store_and_forward"]
    rssi_dbm: Optional[float] = None


# ----------------------------------------------------------------------------- QC
class QCIssue(_Strict):
    ts: datetime
    reason: QCReason
    flag: QCFlag
    detail: Optional[str] = None
    _v = field_validator("ts")(_utc)


class QCReport(_Strict):
    station_id: str
    variable: Variable
    n_obs: int
    issues: list[QCIssue]
    counts: dict[str, int]


# ----------------------------------------------------------------------------- hydro twin
class FitMetrics(_Strict):
    nse: float
    rmse_m: float
    n: int


class HeadModelFit(_Strict):
    """hydro-twin output: per-well response model of depth-to-water to rain/ET (+pumping)."""
    station_id: str
    model: str
    stresses: list[str]
    calib_start: datetime
    calib_end: datetime
    metrics_calib: FitMetrics
    metrics_valid: Optional[FitMetrics] = None
    params: dict[str, float]


class RechargeEstimate(_Strict):
    """aquifer-level recharge from the water-table-fluctuation (WTF) method at one station/season."""
    station_id: str
    season: str                        # e.g. "monsoon-2025"
    rise_m: float
    specific_yield: float = Field(gt=0, lt=1)
    recharge_mm: float
    method: str


# ----------------------------------------------------------------------------- extraction analytics
class ExtractionEventKind(str, Enum):
    periodic_pumping = "periodic_pumping"
    step_drawdown = "step_drawdown"
    sealed_well_running = "sealed_well_running"   # from a SealGuard node
    unexplained_decline = "unexplained_decline"


class ExtractionEvent(_Strict):
    """extraction-detector / seal-guard output for one station or device."""
    event_id: str
    station_id: str
    kind: ExtractionEventKind
    t_start: datetime
    t_end: datetime
    amplitude_m: Optional[float] = None
    period_h: Optional[float] = None
    score: float = Field(ge=0, le=1)
    evidence: dict[str, float] = {}


# ----------------------------------------------------------------------------- recharge verification
class RechargeEventVerdict(str, Enum):
    verified = "verified"            # rise consistent with rain x catchment, normal recession
    clogged = "clogged"              # inflow seen, recession far slower than as-built
    no_inflow = "no_inflow"          # rain fell, no rise (blocked inlet / disconnected)
    implausible = "implausible"      # rise without rain or volume >> catchment x rain (gaming)


class RechargeEvent(_Strict):
    """recharge-verifier output for one storm at one recharge structure."""
    structure_id: str
    t_start: datetime
    t_end: datetime
    rain_mm: float = Field(ge=0)
    inflow_m3: float = Field(ge=0)
    recharged_m3: float = Field(ge=0)
    overflow_m3: float = Field(ge=0)
    k_per_h: Optional[float] = Field(default=None, ge=0, description="recession constant of the pit")
    clogging_index: Optional[float] = Field(default=None, ge=0, description="k / k_as_built")
    verdict: RechargeEventVerdict


# ----------------------------------------------------------------------------- operations
class FindingKind(str, Enum):
    sealed_well_running = "sealed_well_running"
    hidden_pumping_zone = "hidden_pumping_zone"
    recharge_not_functional = "recharge_not_functional"
    recharge_clogging = "recharge_clogging"
    sensor_fault = "sensor_fault"


class TicketStatus(str, Enum):
    open = "open"
    assigned = "assigned"
    verified = "verified"
    false_alarm = "false_alarm"
    closed = "closed"


class InspectionTicket(_Strict):
    """alerts component output: one actionable item for DJB / SDM / DPCC / RWA field teams."""
    ticket_id: str
    created_at: datetime
    kind: FindingKind
    station_id: str
    lat: float
    lon: float
    priority: float = Field(ge=0, description="m3/month at stake x confidence")
    confidence: float = Field(ge=0, le=1)
    evidence: list[str]
    recommended_action: str
    status: TicketStatus = TicketStatus.open
    _v = field_validator("created_at")(_utc)


__all__ = [n for n in dir() if not n.startswith("_")]
