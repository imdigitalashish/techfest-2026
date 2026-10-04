"""Factor database: loads cited records from data/factors/*.yaml and data/sources/*.yaml, validates them,
and turns each record's stated range or pedigree scores into a lognormal sampling distribution."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Literal, Optional

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

PROJECT = Path(__file__).resolve().parents[3]  # ev-c2-green-auto-lca/
DATA = PROJECT / "data"

# Uncertainty factors per pedigree score 1..5 (brightway-lca/pedigree_matrix data.py, version_1).
PEDIGREE_V1 = {
    "reliability": (1.0, 1.05, 1.1, 1.2, 1.5),
    "completeness": (1.0, 1.02, 1.05, 1.1, 1.2),
    "temporal": (1.0, 1.03, 1.1, 1.2, 1.5),
    "geographical": (1.0, 1.01, 1.02, 1.02, 1.1),
    "technological": (1.0, 1.0, 1.2, 1.5, 2.0),
}
# Basic uncertainty factor for CO2 / energy demand (same file, commented basic_uncertainty table: 1.05).
BASIC_UNCERTAINTY = 1.05


class Pedigree(BaseModel):
    reliability: int = Field(ge=1, le=5)
    completeness: int = Field(ge=1, le=5)
    temporal: int = Field(ge=1, le=5)
    geographical: int = Field(ge=1, le=5)
    technological: int = Field(ge=1, le=5)

    def sigma(self, basic: float = BASIC_UNCERTAINTY) -> float:
        """Lognormal sigma (of ln X): sqrt(sum ln(U_i)^2)/2, U_i incl. basic factor (pedigree_matrix pm.py)."""
        factors = [basic] + [PEDIGREE_V1[k][getattr(self, k) - 1] for k in PEDIGREE_V1]
        return math.sqrt(sum(math.log(u) ** 2 for u in factors)) / 2

    def mean_score(self) -> float:
        return sum(getattr(self, k) for k in PEDIGREE_V1) / len(PEDIGREE_V1)


class Uncertainty(BaseModel):
    distribution: Literal["none", "range", "range95", "normal", "lognormal", "triangular", "uniform"] = "none"
    low: Optional[float] = None
    high: Optional[float] = None
    note: str = ""


class Record(BaseModel):
    id: str
    layer: str
    name: str
    value: Any
    unit: str
    quantity: str
    gas_basis: str
    boundary: str = ""
    geography: str
    reference_year: str
    technology: str = ""
    uncertainty: Uncertainty = Uncertainty()
    source_id: str
    locator: str
    quote: str = ""
    accessed: Any = None
    pedigree: Pedigree
    status: Literal["verified", "derived", "assumption", "synthetic", "UNVERIFIED"]
    derivation: str = ""
    notes: str = ""

    @field_validator("id")
    @classmethod
    def _id_lower(cls, v: str) -> str:
        if v != v.lower() or " " in v:
            raise ValueError(f"record id must be lowercase without spaces: {v}")
        return v

    @model_validator(mode="after")
    def _evidence(self) -> "Record":
        if self.status == "verified" and not self.quote:
            raise ValueError(f"{self.id}: verified records need a verbatim quote")
        if self.status == "derived" and not self.derivation:
            raise ValueError(f"{self.id}: derived records need a derivation")
        return self

    @property
    def is_scalar(self) -> bool:
        return isinstance(self.value, (int, float))

    def log_sigma(self) -> float:
        u = self.uncertainty
        if u.distribution == "range95" and u.low and u.high:
            return math.log(u.high / u.low) / (2 * 1.96)
        return self.pedigree.sigma()


class Source(BaseModel):
    id: str
    title: str
    publisher: str
    year: int
    url: str
    type: str
    accessed: Any = None
    license: str = ""
    local_copy: str = ""
    notes: str = ""


class FactorDB:
    def __init__(self, records: dict[str, Record], sources: dict[str, Source]):
        self.records = records
        self.sources = sources
        missing = {r.source_id for r in records.values()} - set(sources)
        if missing:
            raise ValueError(f"records cite unknown sources: {sorted(missing)}")

    @classmethod
    def load(cls, data_dir: Path = DATA) -> "FactorDB":
        records: dict[str, Record] = {}
        for f in sorted((data_dir / "factors").glob("*.yaml")):
            for raw in yaml.safe_load(f.read_text()) or []:
                rec = Record(**raw)
                if rec.id in records:
                    raise ValueError(f"duplicate record id {rec.id} in {f.name}")
                records[rec.id] = rec
        sources = {}
        for f in sorted((data_dir / "sources").glob("*.yaml")):
            for raw in yaml.safe_load(f.read_text()) or []:
                s = Source(**raw)
                sources[s.id] = s
        return cls(records, sources)

    def __getitem__(self, rid: str) -> Record:
        return self.records[rid]

    def summary(self) -> dict[str, Any]:
        by_status: dict[str, int] = {}
        by_layer: dict[str, int] = {}
        for r in self.records.values():
            by_status[r.status] = by_status.get(r.status, 0) + 1
            by_layer[r.layer] = by_layer.get(r.layer, 0) + 1
        return {"records": len(self.records), "sources": len(self.sources), "by_status": by_status,
                "by_layer": by_layer}
