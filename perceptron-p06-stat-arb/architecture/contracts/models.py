"""Row-level typed contracts (pydantic v2) for every component boundary.

The batch path uses the columnar equivalents in frames.py; tests assert both agree.
Times are integer microseconds since the Unix epoch (UTC). Prices are in the
instrument's quote currency; bps = 1e-4 of mid.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

Vantage = Literal["tardis-collector", "mac-india", "azure-japaneast", "azure-eastus", "synthetic"]
FeeTier = Literal["retail", "vip", "mm"]


class Quote(BaseModel):
    """C1 output row: one top-of-book update."""
    ts_exch_us: int = Field(description="venue timestamp (imputed if the venue sends none)")
    ts_recv_us: int = Field(description="receive time at the collector / our machine")
    exch_ts_imputed: bool = False
    venue: str
    instrument: str
    bid_px: float = Field(gt=0)
    bid_sz: float = Field(ge=0)
    ask_px: float = Field(gt=0)
    ask_sz: float = Field(ge=0)

    @model_validator(mode="after")
    def _not_crossed(self) -> "Quote":
        if self.bid_px >= self.ask_px:
            raise ValueError("own-venue book crossed/locked")
        return self


class LatencyQuantiles(BaseModel):
    """C2 output (per venue)."""
    venue: str
    vantage: Vantage
    n: int
    feed_p05_us: float
    feed_p50_us: float
    feed_p95_us: float
    feed_p99_us: float
    order_oneway_us: float = Field(description="assumed one-way order latency; labelled assumption until measured")
    negative_frac: float = Field(description="share of feed latencies < 0 (clock skew indicator)")


class Opportunity(BaseModel):
    """C6 output row: one mispricing episode (sell at A's bid, buy at B's ask)."""
    opp_id: int
    t_start_us: int
    t_end_us: int
    duration_us: int
    censored: bool
    sell_venue: str
    buy_venue: str
    edge0_bps: float = Field(description="(bid_A - ask_B)/mid - fair basis, at detection")
    net0_bps: float = Field(description="edge0_bps minus two taker fees at the evaluated tier")
    size: float
    age_sell_us: int
    age_buy_us: int
    spread_sell_bps: float
    spread_buy_bps: float
    vol_1s_bps: float
    edge_max_bps: float


class SurvivalQuery(BaseModel):
    """C7 input for a single prediction."""
    features: dict[str, float]
    t_us: list[int]


class SurvivalAnswer(BaseModel):
    """C7 output for a single prediction."""
    t_us: list[int]
    survival: list[float] = Field(description="P(still executable at t | features), non-increasing in t")
    half_life_us: float | None


class OrderIntent(BaseModel):
    """C8 output: a two-leg IOC arbitrage order (or a decision to skip)."""
    t_decide_us: int
    opp_id: int
    action: Literal["act", "wait", "skip"]
    sell_venue: str
    buy_venue: str
    size: float
    limit_sell_px: float
    limit_buy_px: float
    ev_bps: float
    wait_us: int = 0


class Fill(BaseModel):
    """C9 output row (one leg)."""
    opp_id: int
    leg: Literal["sell", "buy", "unwind_sell", "unwind_buy"]
    venue: str
    t_arrive_exch_us: int
    filled: bool
    px: float | None
    size: float
    fee_bps: float


class TradeResult(BaseModel):
    """C9 per-intent outcome."""
    opp_id: int
    outcome: Literal["both", "sell_only", "buy_only", "none"]
    pnl_bps: float
    pnl_usd: float
