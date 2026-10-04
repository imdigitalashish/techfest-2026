"""C8 decision — latency-conditioned executable value (LEV), spike v1.

Instead of S(L|x) × edge, learn E[PnL_bps | x, L] directly from simulator labels: on the training
day, every candidate is "executed" by the latency simulator at each latency in a grid (joint IOC
legs at venue arrival times, partial fills, fees, unwind loss), and a gradient-boosted regressor
maps (features, log L) → realised P&L in bps. The policy acts iff the predicted value at our
actual latency (including the model's own compute time) is positive, and ranks by it.
NOTE: the evaluated LEV (this module and the walk-forward's rules.LEARN_X) uses market-state features only —
edge, quote age, spreads, volatility, venue flags, size, pair, latency, fee. No survival-model output is a feature;
residual-survival features are future work (ADR 001), not part of any reported result.
"""
from __future__ import annotations

import numpy as np
import polars as pl
from sklearn.ensemble import HistGradientBoostingRegressor

from components.decay.survival import FEATURES

LEV_FEATURES = FEATURES + ["edge0_bps", "net0_bps", "log_size", "pair_id", "log_L_ms"]


def add_lev_columns(opp: pl.DataFrame, legs: list[str]) -> pl.DataFrame:
    idx = {l: i for i, l in enumerate(legs)}
    n = len(legs)
    return opp.with_columns(
        (pl.col("size").clip(1e-6).log()).alias("log_size"),
        (pl.col("sell_venue").replace_strict(idx, return_dtype=pl.Int64) * n
         + pl.col("buy_venue").replace_strict(idx, return_dtype=pl.Int64)).cast(pl.Float64).alias("pair_id"),
    )


class LEV:
    def __init__(self, seed: int = 0, max_iter: int = 300, lr: float = 0.05, leaves: int = 31, clip_bps: float = 50.0):
        self.kw = dict(max_iter=max_iter, learning_rate=lr, max_leaf_nodes=leaves, random_state=seed,
                       categorical_features=[LEV_FEATURES.index("pair_id")], early_stopping=False)
        self.clip = clip_bps
        self.m = None

    def fit(self, df: pl.DataFrame) -> "LEV":
        X = df.select(LEV_FEATURES).to_numpy()
        y = np.clip(df["pnl_bps"].to_numpy(), -self.clip, self.clip)
        self.m = HistGradientBoostingRegressor(**self.kw).fit(X, y)
        return self

    def predict(self, opp: pl.DataFrame, L_us: float) -> np.ndarray:
        X = opp.with_columns(pl.lit(float(np.log(max(L_us, 1.0) / 1000.0))).alias("log_L_ms")).select(LEV_FEATURES).to_numpy()
        return self.m.predict(X)
