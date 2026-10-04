"""Typed DataFrame contracts between components (source of truth; see architecture/components.md).

Every component consumes and produces pandas DataFrames. A contract lists required columns,
their dtype kind, and value checks. `validate(df, CONTRACT)` raises ContractError on violation.
Dtype kinds: "str", "int", "float", "bool", "datetime_utc", "date".
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Tuple

import numpy as np
import pandas as pd


class ContractError(ValueError):
    pass


@dataclass(frozen=True)
class Contract:
    name: str
    columns: Dict[str, str]
    checks: Tuple[Tuple[str, Callable[[pd.DataFrame], bool]], ...] = field(default_factory=tuple)
    unique_key: Tuple[str, ...] = ()


def _kind_ok(s: pd.Series, kind: str) -> bool:
    if kind == "str":
        return pd.api.types.is_object_dtype(s) or pd.api.types.is_string_dtype(s)
    if kind == "int":
        return pd.api.types.is_integer_dtype(s)
    if kind == "float":
        return pd.api.types.is_float_dtype(s) or pd.api.types.is_integer_dtype(s)
    if kind == "bool":
        return pd.api.types.is_bool_dtype(s)
    if kind == "datetime_utc":
        return isinstance(s.dtype, pd.DatetimeTZDtype) and str(s.dt.tz) == "UTC"
    if kind == "date":  # tz-naive, normalised to midnight
        return pd.api.types.is_datetime64_dtype(s) and bool((s.dropna() == s.dropna().dt.normalize()).all())
    raise ValueError(kind)


def validate(df: pd.DataFrame, c: Contract) -> pd.DataFrame:
    missing = [k for k in c.columns if k not in df.columns]
    if missing:
        raise ContractError(f"{c.name}: missing columns {missing}")
    for col, kind in c.columns.items():
        if not _kind_ok(df[col], kind):
            raise ContractError(f"{c.name}: column {col!r} dtype {df[col].dtype} is not {kind}")
    for desc, fn in c.checks:
        if not fn(df):
            raise ContractError(f"{c.name}: check failed: {desc}")
    if c.unique_key and df.duplicated(list(c.unique_key)).any():
        raise ContractError(f"{c.name}: duplicate keys on {c.unique_key}")
    return df


def _in(col, lo, hi):
    return lambda d: bool(d[col].between(lo, hi).all())


# C1 ingest → raw documents (one row per (ticker, doc))
DOCS = Contract(
    "DOCS",
    {"ticker": "str", "doc_id": "str", "ts_utc": "datetime_utc", "text": "str", "user_id": "str",
     "user_followers": "int", "user_age_days": "float", "user_verified": "bool", "user_statuses": "int",
     "is_retweet": "bool", "n_cashtags": "int", "has_url": "bool", "source": "str"},
    (("source in {real, injected}", lambda d: bool(d["source"].isin(["real", "injected"]).all())),
     ("user_age_days >= 0", lambda d: bool((d["user_age_days"] >= 0).all()))),
    ("ticker", "doc_id"),
)

# C1 ingest → daily bars
BARS = Contract(
    "BARS",
    {"ticker": "str", "date": "date", "open": "float", "high": "float", "low": "float",
     "close": "float", "adj_close": "float", "volume": "float"},
    (("prices > 0", lambda d: bool((d[["open", "high", "low", "close", "adj_close"]] > 0).all().all())),
     ("high >= low", lambda d: bool((d["high"] >= d["low"]).all()))),
    ("ticker", "date"),
)

# C2 align → DOCS + the trading day whose 16:00 ET close the document precedes
ALIGNED_DOCS = Contract(
    "ALIGNED_DOCS", {**DOCS.columns, "trade_date": "date"}, DOCS.checks, DOCS.unique_key)

# C3 text scorer → per-document sentiment
SCORED_DOCS = Contract(
    "SCORED_DOCS",
    {**ALIGNED_DOCS.columns, "p_pos": "float", "p_neg": "float", "p_neu": "float", "sentiment": "float"},
    ALIGNED_DOCS.checks + (
        ("probabilities sum to 1", lambda d: bool(np.allclose(d[["p_pos", "p_neg", "p_neu"]].sum(1), 1, atol=1e-3))),
        ("sentiment in [-1, 1]", _in("sentiment", -1, 1))),
    DOCS.unique_key,
)

# C4 trust scorer → per-document trust weight
TRUSTED_DOCS = Contract(
    "TRUSTED_DOCS", {**SCORED_DOCS.columns, "trust": "float", "dup_cluster": "int"},
    SCORED_DOCS.checks + (("trust in [0, 1]", _in("trust", 0, 1)),), DOCS.unique_key)

# C5 aggregator → one row per (ticker, trade_date)
TEXT_FEATURES = Contract(
    "TEXT_FEATURES",
    {"ticker": "str", "trade_date": "date", "n_docs": "int", "log_n_docs": "float", "attn_z": "float",
     "sent_mean": "float", "sent_median": "float", "sent_trim": "float", "sent_std": "float",
     "sent_tw": "float", "trust_mean": "float"},
    (("n_docs >= 0", lambda d: bool((d["n_docs"] >= 0).all())),
     ("sentiments in [-1, 1]", lambda d: bool(d[["sent_mean", "sent_median", "sent_trim", "sent_tw"]].abs().le(1 + 1e-9).all().all()))),
    ("ticker", "trade_date"),
)

# C6 time-series features → one row per (ticker, trade_date); y = next-day log return in percent
TS_FEATURES = Contract(
    "TS_FEATURES",
    {"ticker": "str", "trade_date": "date", "r0": "float", "r1": "float", "r2": "float", "r3": "float",
     "r4": "float", "rv5": "float", "rv20": "float", "pk": "float", "vol_z": "float", "mkt_r": "float",
     "mkt_rv20": "float", "dow": "int", "y": "float"},
    (("rv20 >= 0", lambda d: bool((d["rv20"] >= 0).all())),),
    ("ticker", "trade_date"),
)

# C7 fusion → raw (uncalibrated) quantile predictions
PREDICTIONS = Contract(
    "PREDICTIONS", {"ticker": "str", "trade_date": "date", "q_lo": "float", "q_med": "float", "q_hi": "float"},
    (), ("ticker", "trade_date"))

# C8 conformal / C10 certified-robust conformal → calibrated intervals
INTERVALS = Contract(
    "INTERVALS",
    {"ticker": "str", "trade_date": "date", "lo": "float", "hi": "float", "point": "float", "method": "str"},
    (("lo <= hi", lambda d: bool((d["lo"] <= d["hi"] + 1e-12).all())),),
    ("ticker", "trade_date", "method"),
)
