"""Typed contracts between P5 components (pydantic v2).

Prices are integer cents, quantities integer shares, times integer ns (simulation clock).
Positive cost/impact = adverse to the agent. See ../components.md for the component map.
"""
from __future__ import annotations

from typing import Dict, List, Literal, Optional, Tuple, Union

from pydantic import BaseModel, Field, model_validator

Side = Literal["BUY", "SELL"]


class ParentOrder(BaseModel):
    side: Side
    quantity: int = Field(gt=0)
    start: str = "09:35:00"
    end: str = "09:55:00"
    n_slots: int = Field(40, gt=1)


class WorldSpec(BaseModel):                       # C9/C2 -> C1
    seed: int = Field(ge=0)
    config: Literal["rmsc04"] = "rmsc04"
    end_time: str = "10:05:00"
    rng_sync: Literal["naive", "per_wakeup"] = "naive"   # C2 spike option


class BookSnapshot(BaseModel):                    # C1/C7 -> C3, C6
    t_ns: int
    bids: List[Tuple[int, int]]                   # [(price, qty)], best first
    asks: List[Tuple[int, int]]


class Fill(BaseModel):
    t_ns: int
    price: int
    qty: int = Field(gt=0)


class WorldResult(BaseModel):                     # C1 -> C2, C8, C10
    seed: int
    t_ns: List[int]
    best_bid: List[Optional[float]]
    best_ask: List[Optional[float]]
    trade_t_ns: List[int]
    trade_qty: List[float]
    holdings_by_type: Dict[str, int]
    fills: List[Fill] = []
    decision_t_ns: List[int] = []


class PolicySpec(BaseModel):                      # C9/C11 -> C7
    kind: Literal["TWAP", "VWAP", "PROBE", "IA"]
    label: str
    params: Dict[str, Union[float, int, bool, List[float]]] = {}


class TwinSpec(BaseModel):                        # C9 -> C2
    world: WorldSpec
    parent: ParentOrder
    policy: PolicySpec


class TwinIntegrity(BaseModel):
    pre_window_identical: bool                    # must be True
    arrival_mid_equal: bool                       # must be True


class TwinPair(BaseModel):                        # C2 -> C8, C10
    spec: TwinSpec
    treatment: WorldResult
    twin: WorldResult
    integrity: TwinIntegrity


class Features(BaseModel):                        # C3 -> C4, C5, C6
    t_ns: int
    spread_ticks: float
    touch_depth_opp: int
    depth5_opp: int
    imbalance: float = Field(ge=-1, le=1)
    remaining: int
    time_left_frac: float = Field(ge=0, le=1)


class ImpactParams(BaseModel):                    # C4b -> C4, C5
    g_perm: float                                 # cents per share, permanent
    g_tr: float                                   # cents per share, transient amplitude
    tau_s: float = Field(gt=0)                    # transient decay time
    inst_cost: float = Field(ge=0)                # cents per share^2 (book walking)


class ImpactEstimate(BaseModel):                  # C4 -> C5, C12
    t_ns: int
    own_impact_cents: float                       # I_hat(t), + = adverse
    ghost_mid: float                              # observed mid corrected for own impact


class VolumeProfile(BaseModel):                   # C4b -> C5 (VWAP)
    cum_fraction: List[float]

    @model_validator(mode="after")
    def _monotone(self):
        c = self.cum_fraction
        if not (all(b >= a for a, b in zip(c, c[1:])) and abs(c[-1] - 1) < 1e-6):
            raise ValueError("cum_fraction must be non-decreasing and end at 1")
        return self


class Schedule(BaseModel):                        # C5 -> C6
    cum_target_fraction: List[float]


class SlotTarget(BaseModel):                      # C5 -> C6
    slot: int
    child_qty: int = Field(ge=0)
    is_final: bool


class ChildOrder(BaseModel):                      # C6 -> C7
    kind: Literal["MKT", "LMT"]
    qty: int = Field(gt=0)
    price: Optional[int] = None

    @model_validator(mode="after")
    def _limit_has_price(self):
        if self.kind == "LMT" and self.price is None:
            raise ValueError("LMT orders need a price")
        return self


class EpisodeMetrics(BaseModel):                  # C8 -> C9
    seed: int
    label: str
    is_bps: float
    drift_bps: float
    own_impact_bps: float
    instant_bps: float
    impact_end_cents: float
    impact_post10_cents: float
    filled: int


class Attribution(BaseModel):                     # C10 -> C9, C12
    seed: int
    label: str
    dpos_by_type: Dict[str, int]                  # treatment minus twin end-of-day position
    conservation_residual: int                    # sum(dpos) incl. our agent; must be 0


class ComparisonResult(BaseModel):                # C9 output
    label: str
    baseline: str
    n_seeds: int
    mean_delta_is_bps: float                      # label minus baseline, paired
    ci95: Tuple[float, float]
    win_rate: float = Field(ge=0, le=1)
