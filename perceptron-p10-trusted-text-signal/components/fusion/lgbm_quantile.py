"""C7 fusion — LightGBM quantile regressors (alpha/2, 0.5, 1-alpha/2) over TS + text features.

Feature sets let the eval run the ablation: price-only, text-only, fusion. Fixed seed + deterministic.
Isolated metric: mean pinball loss over the three quantiles on the validation period.
"""
from __future__ import annotations

import lightgbm as lgb
import numpy as np
import pandas as pd

TS_COLS = ["r0", "r1", "r2", "r3", "r4", "rv5", "rv20", "pk", "vol_z", "mkt_r", "mkt_rv20", "dow"]
TEXT_COLS = ["log_n_docs", "sent_mean", "sent_trim", "sent_std", "trust_mean"]
FEATURE_SETS = {"price_only": TS_COLS, "text_only": TEXT_COLS, "fusion": TS_COLS + TEXT_COLS}

PARAMS = dict(n_estimators=300, learning_rate=0.03, num_leaves=15, min_child_samples=200, subsample=0.8,
              subsample_freq=1, colsample_bytree=0.8, reg_lambda=1.0, n_jobs=4, deterministic=True,
              force_row_wise=True, verbose=-1)


class QuantileFusion:
    def __init__(self, cols: list[str], alpha: float = 0.1, seed: int = 0, params: dict | None = None):
        self.cols, self.alpha, self.seed = list(cols), alpha, seed
        self.params = {**PARAMS, **(params or {})}
        self.levels = (alpha / 2, 0.5, 1 - alpha / 2)
        self.models: list[lgb.LGBMRegressor] = []

    def fit(self, df: pd.DataFrame) -> "QuantileFusion":
        X, y = df[self.cols].to_numpy(float), df["y"].to_numpy(float)
        self.models = [lgb.LGBMRegressor(objective="quantile", alpha=q, random_state=self.seed, **self.params).fit(X, y)
                       for q in self.levels]
        return self

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        X = df[self.cols].to_numpy(float)
        lo, med, hi = (m.predict(X) for m in self.models)
        lo, hi = np.minimum(lo, hi), np.maximum(lo, hi)
        return pd.DataFrame({"ticker": df["ticker"].values, "trade_date": df["trade_date"].values,
                             "q_lo": lo, "q_med": med, "q_hi": hi})

    # MAPIE prefit expects [lower, upper, median]
    def mapie_estimators(self):
        return [self.models[0], self.models[2], self.models[1]]


def pinball(y: np.ndarray, q: np.ndarray, level: float) -> float:
    d = y - q
    return float(np.mean(np.maximum(level * d, (level - 1) * d)))
