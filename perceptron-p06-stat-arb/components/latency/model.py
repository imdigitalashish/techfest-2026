"""C2 latency — per-venue feed-latency quantiles and the vantage latency profile.

feed latency = ts_recv_us - ts_exch_us (rows with an imputed exchange timestamp are excluded).
Order latency is NOT observable from market data; by default we assume one-way order latency
equals the median feed latency of that venue from the same vantage (symmetric path). This is a
labelled assumption, swept in the evaluation.
"""
from __future__ import annotations

import numpy as np
import polars as pl


def feed_latency_table(q: pl.DataFrame, vantage: str) -> pl.DataFrame:
    lat = q.filter(~pl.col("exch_ts_imputed")).with_columns(
        (pl.col("ts_recv_us") - pl.col("ts_exch_us")).alias("lat_us"),
        (pl.col("venue") + ":" + pl.col("instrument")).alias("leg"),
    )
    return (
        lat.group_by("leg")
        .agg(
            pl.len().alias("n"),
            pl.col("lat_us").quantile(0.05).alias("feed_p05_us"),
            pl.col("lat_us").quantile(0.50).alias("feed_p50_us"),
            pl.col("lat_us").quantile(0.95).alias("feed_p95_us"),
            pl.col("lat_us").quantile(0.99).alias("feed_p99_us"),
            (pl.col("lat_us") < 0).mean().alias("negative_frac"),
        )
        .with_columns(pl.lit(vantage).alias("vantage"))
        .sort("leg")
    )


def pinball_loss(y: np.ndarray, q_pred: float, tau: float) -> float:
    d = y - q_pred
    return float(np.mean(np.maximum(tau * d, (tau - 1) * d)))
