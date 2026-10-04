"""C6 time-series features — daily bars → price/volatility features and the target.

y = 100 * log(adj_close[t+1] / adj_close[t]) (next-day close-to-close log return, percent).
All features use information up to and including the close of t. Isolated metric: pinball loss of
a price-only quantile model on the validation period.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from architecture.contracts.contracts import TS_FEATURES, validate


def build_ts_features(bars: pd.DataFrame) -> pd.DataFrame:
    b = bars.sort_values(["ticker", "date"]).copy()
    g = b.groupby("ticker")
    b["r0"] = 100 * np.log(b["adj_close"] / g["adj_close"].shift(1))
    for L in range(1, 5):
        b[f"r{L}"] = b.groupby("ticker")["r0"].shift(L)
    b["rv5"] = b.groupby("ticker")["r0"].transform(lambda x: x.rolling(5, min_periods=5).std())
    b["rv20"] = b.groupby("ticker")["r0"].transform(lambda x: x.rolling(20, min_periods=20).std())
    b["pk"] = 100 * np.sqrt(np.log(b["high"] / b["low"]) ** 2 / (4 * np.log(2)))
    lv = np.log1p(b["volume"])
    b["vol_z"] = (lv - lv.groupby(b["ticker"]).transform(lambda x: x.shift(1).rolling(20, min_periods=10).mean())) / (
        lv.groupby(b["ticker"]).transform(lambda x: x.shift(1).rolling(20, min_periods=10).std()) + 1e-6)
    mkt = b.groupby("date")["r0"].mean().rename("mkt_r")
    mkt_rv = mkt.rolling(20, min_periods=20).std().rename("mkt_rv20")
    b = b.merge(mkt, left_on="date", right_index=True).merge(mkt_rv, left_on="date", right_index=True)
    b["y"] = b.groupby("ticker")["r0"].shift(-1)
    b["dow"] = b["date"].dt.dayofweek.astype(int)
    b = b.rename(columns={"date": "trade_date"})
    cols = list(TS_FEATURES.columns)
    b = b.dropna(subset=cols).replace([np.inf, -np.inf], np.nan).dropna(subset=cols)
    return validate(b[cols].reset_index(drop=True), TS_FEATURES)
