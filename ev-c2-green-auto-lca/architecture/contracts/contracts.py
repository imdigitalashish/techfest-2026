"""Typed I/O contracts for every component (pydantic v2). The record/source schema itself lives in
components/lca_engine/greenauto/db.py (Record, Source, Pedigree, Uncertainty) and is re-exported here.
Each component's isolated metric is in architecture/components.md."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

# --- C1 Source registry -------------------------------------------------------------------------------
class SourceSpec(BaseModel):
    id: str
    url: str
    title: str
    publisher: str
    year: int
    type: Literal["government-dataset", "government-report", "company-disclosure", "peer-reviewed",
                  "grey-literature", "standard", "dataset", "software", "news"]
    local_copy: Optional[str] = None          # path under .data/raw/


# --- C3 Ingestion (spike A) ---------------------------------------------------------------------------
class Document(BaseModel):
    source_id: str
    path: str                                  # local PDF/XLSX/HTML
    media_type: Literal["pdf", "xlsx", "html", "csv"]


class CandidateRecord(BaseModel):
    """Extractor output; becomes a C2 Record only after automatic checks + human/agent review."""
    source_id: str
    name: str
    value: float
    unit: str
    reference_year: str
    geography: str
    locator: str                               # page/table/sheet!cell
    quote: str                                 # verbatim snippet containing the number
    quote_found_in_document: bool              # set by the verifier, never by the extractor
    unit_normalised: Optional[str] = None
    confidence: float = Field(ge=0, le=1)


# --- C4 Grid-factor service (spike B) -----------------------------------------------------------------
class GridFactorQuery(BaseModel):
    region: str = "IN"                         # IN or IN-<state>
    period: str = "2025-26"                    # FY, or a range for lifetime averages "2026-2035"
    method: Literal["average", "operating_margin", "build_margin", "combined_margin", "prospective"] = "average"
    delivery: Literal["busbar", "consumer_meter"] = "consumer_meter"
    gas_basis: Literal["CO2", "CO2e"] = "CO2"


class GridFactor(BaseModel):
    value: float                               # kg per kWh
    unit: str = "kg CO2/kWh"
    query: GridFactorQuery
    record_ids: list[str]                      # every record used (EF, T&D, upstream, ...)
    derivation: str


# --- C5 Product-system builder ------------------------------------------------------------------------
class VehicleSpec(BaseModel):
    id: str
    segment: Literal["2W", "3W", "car", "bus", "truck"]
    powertrain: Literal["ICE", "CNG", "HEV", "BEV", "FCEV"]
    label: str


class ProductSystem(BaseModel):
    id: str
    label: str
    powertrain: str
    functional_unit: str = "1 vehicle-km"
    params: dict[str, str]                     # local name -> record id (no free constants)
    stages: dict[str, str]                     # stage -> expression in kg CO2e per functional unit


# --- C6 Calculation engine ----------------------------------------------------------------------------
class StageResult(BaseModel):
    product_id: str
    unit: str = "g CO2e per vehicle-km"
    stages: dict[str, float]
    total: float


# --- C7 Uncertainty / sensitivity / DQI / data gaps --------------------------------------------------
class Interval(BaseModel):
    mean: float
    p05: float
    p50: float
    p95: float


class UncertaintyResult(BaseModel):
    product_id: str
    n_iterations: int
    seed: int
    total: Interval
    stages: dict[str, Interval]
    elasticity: dict[str, float]               # record id -> d ln(total) / d ln(value)
    dqi: float = Field(ge=1, le=5)             # elasticity-weighted mean pedigree score
    india_weighted_share: float = Field(ge=0, le=1)
    variance_share: dict[str, float]           # record id -> share of rank-variance (data-gap ranking)


class Comparison(BaseModel):
    ice: str
    bev: str
    reduction_central: float
    reduction_mc: Interval
    p_bev_lower: float = Field(ge=0, le=1)
    variance_share_of_reduction: dict[str, float]


# --- C8 Benchmark harness -----------------------------------------------------------------------------
class ReplicationResult(BaseModel):
    benchmark_id: str
    scenario_id: str
    mape_pct: float
    reduction_abs_error_pp: float
    published_inside_our_90pct: dict[str, bool]


class EvalReport(BaseModel):
    commit: str
    n: int
    seed: int
    headline: dict[str, float]                 # {"replication_mape_pct": ...}
    replication: dict[str, dict]
    india_2026: dict[str, dict]
