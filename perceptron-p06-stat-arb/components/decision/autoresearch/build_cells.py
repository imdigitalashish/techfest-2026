"""Build the labelled cells used by the FROZEN autoresearch eval (run once; cached in .cache/).

For each cell (fee bps per leg f, one-way latency δ) and each detected opportunity whose net edge
beats fees, simulate acting immediately (t_decide = t_obs + compute) and record the realised P&L.
Usage: .venv/bin/python -m components.decision.autoresearch.build_cells
"""
from __future__ import annotations

import os

import numpy as np
import polars as pl

from components.decay.survival import add_features
from components.decision import policies as P
from components.decision.lev import add_lev_columns
from components.detector.cross import detect
from components.sim.fills import simulate, truth_books
from eval.run_baseline import load, pair_group

LEGS_FILES = "binance_BTCUSDT,binance-futures_BTCUSDT,coinbase_BTC-USD,okex_BTC-USDT,okex-swap_BTC-USDT-SWAP".split(",")
FEES = [1.0, 2.0]
DELTAS_MS = [1.0, 5.0, 20.0]
COMPUTE_US = 7.0   # measured EV cost (~6.4 µs/opportunity on the M5), rounded up
OUT = ".cache/autoresearch"


def cells_for(q: pl.DataFrame, legs: list[str], part: str) -> pl.DataFrame:
    opp = add_lev_columns(pair_group(add_features(detect(q, legs, "ts_exch_us", theta_bps=1.0))), legs)
    books = truth_books(q)
    out = []
    for f in FEES:
        tier = f"f{f:g}"
        o = P.with_net(opp, tier).filter(pl.col("net0_bps") > 0)
        for d_ms in DELTAS_MS:
            d = d_ms * 1000.0
            c = o.with_columns((pl.col("t_start_us") + int(d)).alias("t_obs_us"), pl.col("duration_us").alias("duration_obs_us"))
            it = P.intents(c, np.ones(c.height, bool), c["t_obs_us"].to_numpy() + COMPUTE_US, c["net0_bps"].to_numpy(), "all")
            r = simulate(it, books, {l: d for l in legs}, {l: f for l in legs}, 0.05)
            out.append(it.join(r.select("opp_id", "outcome", "pnl_usd", "pnl_bps"), on="opp_id").with_columns(
                pl.lit(f).alias("fee_bps"), pl.lit(d_ms).alias("delta_ms"),
                pl.lit(float(2 * d_ms + COMPUTE_US / 1000)).alias("L_ms"), pl.lit(part).alias("part"),
                (pl.col("t_start_us") // 3_600_000_000).alias("hour")))
    return pl.concat(out, how="diagonal_relaxed")


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    q = load(".data/tardis", "2026-09-01", LEGS_FILES)
    legs = sorted(q["leg"].unique().to_list())
    cut = q["ts_exch_us"].min() + 12 * 3600 * 1_000_000
    tr = cells_for(q.filter(pl.col("ts_exch_us") < cut), legs, "train")
    va = cells_for(q.filter(pl.col("ts_exch_us") >= cut), legs, "val")
    pl.concat([tr, va], how="diagonal_relaxed").write_parquet(f"{OUT}/cells_0901.parquet")
    full = cells_for(q, legs, "train_full")
    q2 = load(".data/tardis", "2026-10-01", LEGS_FILES)
    ho = cells_for(q2, legs, "holdout")
    pl.concat([full, ho], how="diagonal_relaxed").write_parquet(f"{OUT}/cells_holdout.parquet")
    print("rows", tr.height, va.height, full.height, ho.height)


if __name__ == "__main__":
    main()
