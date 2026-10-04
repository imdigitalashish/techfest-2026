"""Typed contracts between DustLedger components (pydantic v2). Units: µg/m³ for PM, m/s, degrees (wind FROM, 0 = N),
UTC timestamps. Every record carries site_id. Anything simulated carries provenance="SIMULATED".
Run `python contracts.py` to export JSON Schemas to ./schemas/.
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field, conlist

Provenance = Literal["MEASURED", "SIMULATED", "PUBLIC_REFERENCE"]


class QAFlag(str, Enum):
    ok = "ok"; out_of_range = "out_of_range"; stuck = "stuck"; fog_rh_gt_95 = "fog_rh_gt_95"
    low_flow = "low_flow"; gap_filled = "gap_filled"; suspected_spray = "suspected_spray"; clock_skew = "clock_skew"


# C1 fence-line node → C3 gateway
class NodeReading(BaseModel):
    site_id: str; node_id: str; ts: datetime; seq: int = Field(ge=0)
    pm1: float = Field(ge=0); pm25: float = Field(ge=0); pm10: float = Field(ge=0)
    bins: Optional[conlist(float, min_length=1, max_length=24)] = None  # number concentrations if the sensor exposes them
    t_c: float; rh_pct: float = Field(ge=0, le=100)
    fan_ok: bool = True; fw: str; provenance: Provenance = "MEASURED"
    sig: Optional[str] = None  # Ed25519 signature over the canonical JSON, base64


# C2 wind/met station → C3 gateway
class WindReading(BaseModel):
    site_id: str; ts: datetime; ws_ms: float = Field(ge=0); wd_deg: float = Field(ge=0, lt=360)
    gust_ms: Optional[float] = None; provenance: Provenance = "MEASURED"


# C4 ingest+QA → C5
class CleanReading(NodeReading):
    flags: list[QAFlag] = [QAFlag.ok]


# C5 calibration → C6
class CalibratedReading(BaseModel):
    site_id: str; node_id: str; ts: datetime; window_s: int = 60
    pm25_cal: float; pm10_cal: float; sigma_pm10: float = Field(ge=0)  # 1-sigma calibration uncertainty
    model_version: str; flags: list[QAFlag] = [QAFlag.ok]


# C6 attribution (SPIKE) → C8, C10, C12
class SiteIncrement(BaseModel):
    site_id: str; window_start: datetime; window_s: int = 900
    background_pm10: float = Field(description="upwind / ring-minimum estimate")
    increment_pm10: float = Field(description="site's own contribution at the downwind fence line, µg/m³")
    ci90: tuple[float, float]
    p_site_cause: float = Field(ge=0, le=1, description="P(increment > threshold)")
    wind_from_deg: float; ws_ms: float; upwind_nodes: list[str]; downwind_nodes: list[str]
    method: str = "ring-differential-v0"; provenance: Provenance = "MEASURED"


# C7 background forecast → C8, C11, C12
class BackgroundForecast(BaseModel):
    station_id: str; issue_time: datetime; valid_date: str; pollutant: Literal["pm25", "pm10"]
    q10: float; q50: float; q90: float; model_version: str


# C8 controller → C9 actuator
class ActuationCommand(BaseModel):
    site_id: str; zone: str; ts: datetime; on: bool; duration_s: int = Field(ge=0, le=3600)
    reason: Literal["site_increment", "forecast_risk", "manual", "test", "water_budget_stop"]
    increment_ref: Optional[str] = None


# C9 actuator → C10, C12
class ActuationLog(BaseModel):
    site_id: str; zone: str; ts_on: datetime; ts_off: datetime; litres: float = Field(ge=0)
    flow_meter_ok: bool = True


# C10 evidence ledger
class LedgerEntry(BaseModel):
    site_id: str; ts: datetime; kind: Literal["reading", "wind", "increment", "actuation", "calibration", "maintenance"]
    payload_sha256: str; prev_hash: str; entry_hash: str


class DailyComplianceReport(BaseModel):
    site_id: str; date: str; coverage_pct: float = Field(ge=0, le=100)
    exceedance_minutes: int; mean_increment_pm10: float; p95_increment_pm10: float
    water_litres: float; suspected_tamper_events: int; ledger_head: str


# C11 scheduler
class WorkWindowAdvice(BaseModel):
    site_id: str; date: str; windows: list[tuple[datetime, datetime]]; rationale: str


if __name__ == "__main__":
    import json, os
    os.makedirs(os.path.join(os.path.dirname(__file__), "schemas"), exist_ok=True)
    for m in [NodeReading, WindReading, CleanReading, CalibratedReading, SiteIncrement, BackgroundForecast,
              ActuationCommand, ActuationLog, LedgerEntry, DailyComplianceReport, WorkWindowAdvice]:
        with open(os.path.join(os.path.dirname(__file__), "schemas", f"{m.__name__}.json"), "w") as fh:
            json.dump(m.model_json_schema(), fh, indent=1)
    print("exported schemas")
