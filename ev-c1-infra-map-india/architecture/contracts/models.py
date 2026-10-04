"""Typed contracts between components (pydantic v2). JSON Schemas are generated into this folder by
`python architecture/contracts/models.py` (one <Model>.schema.json per model).

Units: power kW, energy kWh, distances km, times minutes. Coordinates WGS84 (EPSG:4326).
Every record that carries data from outside carries provenance (source, source_id, license, fetched_at).
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field, confloat, conint

Segment = Literal["2W", "3W", "4W", "BUS", "GOODS", "OTHER"]


class ConnectorType(str, Enum):
    CCS2 = "CCS2"; TYPE2 = "TYPE2"; CHADEMO = "CHADEMO"; GBT_DC = "GBT_DC"; BHARAT_AC001 = "BHARAT_AC001"
    BHARAT_DC001 = "BHARAT_DC001"; LECCS = "LECCS"; IND_15A = "IND_15A"; DOMESTIC = "DOMESTIC"; OTHER = "OTHER"


class Provenance(BaseModel):
    source: str = Field(description="connector id, e.g. osm, ocm, cpo:<name>, official:pib2151390")
    source_id: str
    license: str
    fetched_at: datetime
    url: Optional[str] = None


# ---- C1 vahan_ingest -> C7 ev_stock -------------------------------------------------------------
class RegistrationRecord(BaseModel):
    """One cell of a VAHAN pivot: registrations for (geography, vehicle class, fuel, period)."""
    state_code: str = Field(description="VAHAN state code, e.g. MH; '-1' = all India")
    rto_code: str = Field(description="VAHAN office code; '-1' = all offices in state")
    rto_label: Optional[str] = None
    vehicle_class: str = Field(description="VAHAN vehicle class label, e.g. 'M-CYCLE/SCOOTER', 'E-RICKSHAW(P)'")
    segment: Segment
    fuel: str = Field(description="VAHAN fuel label; BEV = 'ELECTRIC(BOV)' or 'PURE EV'")
    period: str = Field(description="'A' = till today, 'YYYY' = calendar year, 'YYYY-MM' = month")
    count: conint(ge=0)
    provenance: Provenance


# ---- C2 charger_ingest -> C3 normalize -> C4 resolve -------------------------------------------
class Connector(BaseModel):
    type: ConnectorType
    count: conint(ge=1) = 1
    power_kw: Optional[confloat(gt=0, le=1000)] = None


class ChargerRecord(BaseModel):
    """A charging location as ONE source describes it (pre-resolution)."""
    lat: confloat(ge=6.0, le=37.5)
    lon: confloat(ge=68.0, le=97.5)
    name: Optional[str] = None
    operator: Optional[str] = None
    operator_canonical: Optional[str] = None
    address: Optional[str] = None
    connectors: list[Connector] = []
    access: Optional[Literal["public", "customers", "private", "unknown"]] = "unknown"
    segments_served: list[Segment] = []
    status: Optional[Literal["operational", "planned", "removed", "unknown"]] = "unknown"
    last_verified: Optional[datetime] = None
    provenance: Provenance


class Site(BaseModel):
    """A resolved physical charging site (output of C4): one or more ChargerRecords from >=1 sources."""
    site_id: str
    lat: float
    lon: float
    operator_canonical: Optional[str] = None
    connectors: list[Connector] = []
    max_power_kw: Optional[float] = None
    n_sources: conint(ge=1)
    members: list[Provenance]
    match_confidence: confloat(ge=0, le=1)
    admin: dict[str, str] = Field(default_factory=dict, description="{'state_lgd':..,'district_lgd':..,'h3_r8':..}")


# ---- C5 census_completeness ----------------------------------------------------------------------
class CompletenessEstimate(BaseModel):
    region_id: str
    observed_sites: conint(ge=0)
    estimated_total: float
    ci90: tuple[float, float]
    coverage: confloat(ge=0, le=1) = Field(description="observed / estimated_total")
    method: Literal["lincoln_petersen", "chapman", "loglinear_mse", "official_benchmark"]
    benchmark_total: Optional[int] = Field(None, description="official count for validation, e.g. PIB 2151390")


# ---- C6 admin_geo ---------------------------------------------------------------------------------
class AdminUnit(BaseModel):
    unit_id: str = Field(description="LGD code where available")
    level: Literal["country", "state", "district", "rto", "h3"]
    name: str
    parent_id: Optional[str] = None
    population: Optional[int] = None
    geometry_ref: str = Field(description="path#feature-id of the boundary (GeoParquet)")


class RtoDistrictLink(BaseModel):
    state_code: str
    rto_code: str
    rto_label: str
    district_lgd: Optional[str]
    district_name: Optional[str]
    weight: confloat(ge=0, le=1) = 1.0
    method: Literal["name_match", "manual", "office_geocode"]


# ---- C7 ev_stock / C8 demand / C9 forecast --------------------------------------------------------
class StockEstimate(BaseModel):
    unit_id: str
    segment: Segment
    year: int
    registrations_cum: int
    stock_est: float = Field(description="on-road stock after survival curve")
    ci90: Optional[tuple[float, float]] = None


class DemandEstimate(BaseModel):
    unit_id: str
    segment: Segment
    year: int
    public_kwh_per_day: float
    public_sessions_per_day: float
    assumptions_ref: str = Field(description="id of the parameter set (research/india-ev-parameters)")


# ---- C10 access_gap -> C11 requirement_siting -> C12/C13 -----------------------------------------
class GapRecord(BaseModel):
    unit_id: str
    level: Literal["state", "district", "h3", "corridor_segment"]
    ev_stock: float
    public_sites: float
    public_kw: Optional[float] = None
    coverage_adjusted_sites: Optional[float] = Field(None, description="sites / completeness coverage")
    evs_per_site: Optional[float] = None
    access_index_e2sfca: Optional[float] = None
    norm_shortfall: Optional[float] = Field(None, description="sites missing vs a policy norm (e.g. MoP 2024 spacing)")
    gap_score: confloat(ge=0, le=1)
    drivers: list[str] = Field(default_factory=list, description="human-readable reasons, ranked")


class Recommendation(BaseModel):
    unit_id: str
    year: int
    scenario: Literal["bau", "policy_target", "high"]
    chargers_needed: dict[str, int] = Field(description="by charger class, e.g. {'LEV_AC':..,'AC_7kW':..,'DC_60kW':..}")
    candidate_sites: list[dict] = Field(default_factory=list, description="[{lat,lon,kind,score,grid_ok}]")
    coverage_gain: Optional[float] = None
    rationale: str


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for m in [RegistrationRecord, ChargerRecord, Site, CompletenessEstimate, AdminUnit, RtoDistrictLink,
              StockEstimate, DemandEstimate, GapRecord, Recommendation]:
        with open(os.path.join(here, f"{m.__name__}.schema.json"), "w") as f:
            json.dump(m.model_json_schema(), f, indent=1)
    print("schemas written")
