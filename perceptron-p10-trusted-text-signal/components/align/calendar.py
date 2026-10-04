"""C2 align — assign each document to the trading day whose 16:00 America/New_York close it precedes.

Information set at the close of day t = all documents with local time < 16:00 on t and after the
previous close. Documents at/after 16:00, on weekends or on holidays roll to the next trading day.
This is the component that prevents look-ahead leakage; its isolated metric is the number of
documents whose timestamp is not strictly before their assigned close (must be 0).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from architecture.contracts.contracts import ALIGNED_DOCS, validate

NY = "America/New_York"
CLOSE_HOUR = 16


def assign_trade_date(docs: pd.DataFrame, trading_days: pd.DatetimeIndex) -> pd.DataFrame:
    days = pd.DatetimeIndex(sorted(set(pd.DatetimeIndex(trading_days).normalize())))
    local = docs["ts_utc"].dt.tz_convert(NY)
    cand = local.dt.tz_localize(None).dt.normalize()
    after_close = local.dt.hour >= CLOSE_HOUR
    cand = cand + pd.to_timedelta(after_close.astype(int), unit="D")
    idx = days.searchsorted(cand.values, side="left")
    valid = idx < len(days)
    out = docs[valid].copy()
    out["trade_date"] = days[idx[valid]]
    return validate(out, ALIGNED_DOCS)


def leakage_count(aligned: pd.DataFrame) -> int:
    """Isolated metric: # docs not strictly before 16:00 ET on their trade_date (must be 0)."""
    close = (aligned["trade_date"] + pd.Timedelta(hours=CLOSE_HOUR)).dt.tz_localize(NY)
    return int(np.sum(aligned["ts_utc"].dt.tz_convert(NY).values >= close.dt.tz_convert("UTC").values))
