"""Typed contracts between components (pydantic v2).

Tensors never travel inside these models: a component passes a contract object plus a
LayerState / payload dict of tensors. Export JSON Schemas with
``python -m components.contracts`` (writes ``architecture/contracts/*.schema.json``).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class DeviceProfile(BaseModel):
    """C2 → C3/C7: one simulated device and its budgets."""

    client_id: str
    device_class: str = Field(description="e.g. workstation, laptop, phone")
    domain: str = Field(description="dominant data domain held by the device")
    n_train_blocks: int = Field(gt=0, description="local training set size, in 128-token blocks")
    rank: int = Field(ge=1, description="LoRA rank the device can afford (memory budget)")
    local_steps: int = Field(ge=1, description="optimizer steps per round it can afford (compute budget)")
    p_offline: float = Field(0.0, ge=0, le=1, description="P(device unavailable for a whole round)")
    p_cutoff: float = Field(0.0, ge=0, le=1, description="P(round deadline cuts the device short)")
    outage_rounds: list[int] = Field(default_factory=list, description="rounds of a forced mid-run outage")


class ClientTask(BaseModel):
    """C7 → C4: the work one device does in one round."""

    round: int
    client_id: str
    rank: int = Field(ge=1)
    planned_steps: int = Field(ge=1)
    allowed_steps: int = Field(ge=0, description="< planned_steps when the deadline cuts the device off")
    batch_size: int = Field(ge=1)
    lr: float = Field(gt=0)
    train_A: bool = Field(description="False when A is the frozen shared anchor")
    seed: int


class ClientUpdate(BaseModel):
    """C4 → C6 metadata accompanying the uploaded tensors."""

    round: int
    client_id: str
    rank: int
    planned_steps: int
    steps_done: int
    n_examples: int
    train_loss: float
    upload_bytes: int
    wall_s: float
    status: Literal["ok", "partial", "late_discarded", "offline"]


class AggregationReport(BaseModel):
    """C6 output (returned with the new global LayerState)."""

    round: int
    strategy: str
    reporters: list[str]
    used_memory_for: list[str] = Field(default_factory=list)
    weights: dict[str, float]
    influence_share: dict[str, float] = Field(
        description="s_k = <c_k, P> / ||P||^2 in product (ΔW) space; sums to 1 when aggregation is exact"
    )
    aggregation_error: float = Field(description="||P - Σ c_k|| / ||Σ c_k||; 0 for exact aggregation")
    update_norm: float


class EvalReport(BaseModel):
    """C9 output for one global-model snapshot."""

    round: int
    per_domain_loss: dict[str, float]
    macro_loss: float
    worst_loss: float
    worst_domain: str


class RunSummary(BaseModel):
    """End-to-end metrics for one (strategy, scenario, seed) run."""

    strategy: str
    scenario: str
    seed: int
    rounds: int
    base_macro_loss: float
    final_macro_loss: float
    final_worst_loss: float
    final_min_rel_gain: float = Field(description="min over domains of (base - final) / base")
    final_per_domain_loss: dict[str, float]
    mean_macro_loss: float = Field(description="mean macro loss over evaluated rounds (area under the curve)")
    max_spike: float = Field(description="largest increase in macro loss between consecutive evaluations")
    dominance_c0: float = Field(description="mean influence share of the data-rich device c0")
    dominance_max: float = Field(description="mean over rounds of max_k influence share")
    weak_gain: float = Field(description="mean loss reduction vs base on the weak devices' domains")
    aggregation_error: float
    upload_mb: dict[str, float]
    wall_s: float


ALL_CONTRACTS = [DeviceProfile, ClientTask, ClientUpdate, AggregationReport, EvalReport, RunSummary]


def export_schemas(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for model in ALL_CONTRACTS:
        p = out_dir / f"{model.__name__}.schema.json"
        p.write_text(json.dumps(model.model_json_schema(), indent=2) + "\n")
        paths.append(p)
    return paths


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    for p in export_schemas(root / "architecture" / "contracts"):
        print(p.relative_to(root))
