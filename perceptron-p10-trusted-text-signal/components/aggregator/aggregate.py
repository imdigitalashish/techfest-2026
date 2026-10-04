"""C5 aggregator — per-document scores → one text-feature row per (ticker, trade_date).

`robust_agg` is the bounded-influence aggregator used by the certified spike (C10): a 20 %
trimmed mean, which is monotone non-decreasing in every input, so its range over any
"remove up to k documents" or "edit up to k documents" set is attained at order statistics.
Isolated metric: worst-case shift of the aggregate under k injected documents (lower is better)
at equal information coefficient with next-day returns.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import trim_mean

from architecture.contracts.contracts import TEXT_FEATURES, validate

TRIM = 0.2
ATTN_WIN = 20


def robust_agg(values: np.ndarray) -> float:
    v = np.asarray(values, dtype=float)
    return 0.0 if v.size == 0 else float(trim_mean(v, TRIM))


def _per_day(g: pd.DataFrame) -> pd.Series:
    s = g["sentiment"].to_numpy()
    w = g["trust"].to_numpy()
    return pd.Series({
        "n_docs": len(s), "sent_mean": s.mean(), "sent_median": float(np.median(s)), "sent_trim": robust_agg(s),
        "sent_std": s.std() if len(s) > 1 else 0.0, "sent_tw": float(np.sum(w * s) / max(np.sum(w), 1e-9)),
        "trust_mean": w.mean(),
    })


def attention_z(n_docs: pd.Series, hist_mean: pd.Series, hist_std: pd.Series) -> pd.Series:
    return ((np.log1p(n_docs) - hist_mean) / (hist_std + 0.25)).astype(float)


def aggregate(trusted: pd.DataFrame, panel: pd.DataFrame) -> pd.DataFrame:
    """`panel` has one row per (ticker, trade_date) to emit (days without documents get n_docs=0)."""
    g = trusted.groupby(["ticker", "trade_date"], sort=False)[["sentiment", "trust"]].apply(_per_day).reset_index()
    out = panel[["ticker", "trade_date"]].merge(g, on=["ticker", "trade_date"], how="left")
    out["n_docs"] = out["n_docs"].fillna(0).astype(int)
    out[["sent_mean", "sent_median", "sent_trim", "sent_std", "sent_tw"]] = out[
        ["sent_mean", "sent_median", "sent_trim", "sent_std", "sent_tw"]].fillna(0.0)
    out["trust_mean"] = out["trust_mean"].fillna(0.0)
    out = out.sort_values(["ticker", "trade_date"]).reset_index(drop=True)
    out["log_n_docs"] = np.log1p(out["n_docs"]).astype(float)
    lg = out.groupby("ticker")["log_n_docs"]
    out["attn_hist_mean"] = lg.transform(lambda x: x.shift(1).rolling(ATTN_WIN, min_periods=5).mean()).fillna(0.0)
    out["attn_hist_std"] = lg.transform(lambda x: x.shift(1).rolling(ATTN_WIN, min_periods=5).std()).fillna(0.0)
    out["attn_z"] = attention_z(out["n_docs"], out["attn_hist_mean"], out["attn_hist_std"])
    return validate(out, TEXT_FEATURES)
