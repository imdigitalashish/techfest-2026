"""Exactness test: the Numba-compiled LEV equals sklearn's prediction (synthetic data, categorical pair_id)."""
from __future__ import annotations

import numpy as np
import polars as pl

from components.decision.autoresearch.rules import LEARN_X, fit_gbm_reg
from components.decision.compiled import RAW_FIELDS, build


def _synthetic(n=6000, seed=0):
    rng = np.random.default_rng(seed)
    raw = {
        "edge0_bps": rng.gamma(2.0, 1.0, n) + 0.5, "age_sell_us": rng.integers(0, 200_000, n).astype(float),
        "age_buy_us": rng.integers(0, 200_000, n).astype(float), "updater_is_sell": rng.integers(0, 2, n).astype(float),
        "spread_sell_bps": rng.gamma(1.0, 0.3, n), "spread_buy_bps": rng.gamma(1.0, 0.3, n), "vol_1s_bps": rng.gamma(1.0, 0.5, n),
        "sell_is_perp": rng.integers(0, 2, n).astype(float), "buy_is_perp": rng.integers(0, 2, n).astype(float),
        "size": rng.gamma(1.0, 0.05, n) + 1e-4, "pair_id": rng.integers(0, 25, n).astype(float),
        "L_ms": rng.choice([2.007, 10.007, 40.007], n), "fee_bps": rng.choice([1.0, 2.0], n),
    }
    df = pl.DataFrame(raw)
    upd = pl.col("updater_is_sell") > 0.5
    df = df.with_columns(
        pl.col("edge0_bps").clip(1e-6).log().alias("log_edge"),
        (pl.when(upd).then(pl.col("age_buy_us")).otherwise(pl.col("age_sell_us")) / 1000.0).clip(0).log1p().alias("log_age_other_ms"),
        (pl.col("spread_sell_bps") + pl.col("spread_buy_bps")).alias("spread_sum_bps"),
        pl.col("vol_1s_bps").clip(0).log1p().alias("log_vol"),
        (pl.col("edge0_bps") - 2 * pl.col("fee_bps")).alias("net0_bps"),
        pl.col("size").clip(1e-6).log().alias("log_size"),
    )
    y = (df["net0_bps"] * 0.5 - (df["L_ms"] / 20) * (df["pair_id"] % 3) + rng.normal(0, 0.5, n)).to_numpy()
    return df.with_columns(pl.Series("pnl_bps", y))


def test_compiled_matches_sklearn():
    df = _synthetic()
    m = fit_gbm_reg(df, iters=60)
    predict_row, decide, raw_to_x, a = build(m["m"])
    X = df.select(LEARN_X).to_numpy()
    R = df.select(RAW_FIELDS).to_numpy()
    ref = m["m"].predict(X)
    x = np.empty(13); xi = np.empty(13)
    got = np.empty(len(ref)); feats = np.empty_like(X)
    for k in range(len(ref)):
        act, v = decide(R[k], x, xi)
        got[k] = v; feats[k] = x
    assert np.max(np.abs(feats - X)) < 1e-9          # raw → features identical to the batch path
    assert np.max(np.abs(got - ref)) < 1e-9          # tree traversal identical to sklearn
    assert a["iscat"].any()                           # categorical splits exercised
    unseen = R[0].copy(); unseen[10] = 77.0           # a pair_id never seen in training → treated as missing
    act, v = decide(unseen, x, xi)
    Xu = X[:1].copy(); Xu[0, LEARN_X.index("pair_id")] = 77.0
    assert abs(v - m["m"].predict(Xu)[0]) < 1e-9
