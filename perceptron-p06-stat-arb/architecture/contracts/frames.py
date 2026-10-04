"""Columnar (polars) schemas for the batch path. One dict per frame contract."""
from __future__ import annotations

import polars as pl

QUOTE_FRAME = {
    "ts_exch_us": pl.Int64,
    "ts_recv_us": pl.Int64,
    "exch_ts_imputed": pl.Boolean,
    "venue": pl.Utf8,
    "instrument": pl.Utf8,
    "bid_px": pl.Float64,
    "bid_sz": pl.Float64,
    "ask_px": pl.Float64,
    "ask_sz": pl.Float64,
}

OPPORTUNITY_FRAME = {
    "opp_id": pl.Int64,
    "t_start_us": pl.Int64,
    "t_end_us": pl.Int64,
    "duration_us": pl.Int64,
    "censored": pl.Boolean,
    "sell_venue": pl.Utf8,
    "buy_venue": pl.Utf8,
    "edge0_bps": pl.Float64,
    "net0_bps": pl.Float64,
    "size": pl.Float64,
    "age_sell_us": pl.Int64,
    "age_buy_us": pl.Int64,
    "spread_sell_bps": pl.Float64,
    "spread_buy_bps": pl.Float64,
    "vol_1s_bps": pl.Float64,
    "edge_max_bps": pl.Float64,
}

TRADE_FRAME = {
    "opp_id": pl.Int64,
    "policy": pl.Utf8,
    "outcome": pl.Utf8,
    "pnl_bps": pl.Float64,
    "pnl_usd": pl.Float64,
}


def check(df: pl.DataFrame, schema: dict) -> None:
    """Raise if df is missing a column or has the wrong dtype."""
    missing = [c for c in schema if c not in df.columns]
    if missing:
        raise TypeError(f"missing columns {missing}")
    bad = {c: (df.schema[c], t) for c, t in schema.items() if df.schema[c] != t}
    if bad:
        raise TypeError(f"dtype mismatch {bad}")
