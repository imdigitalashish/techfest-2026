"""C1 ingest — StockNet raw tweets + Yahoo prices → DOCS, BARS (see architecture/contracts/contracts.py).

Data: Xu & Cohen (ACL 2018) StockNet dataset, MIT licence, https://github.com/yumoxu/stocknet-dataset
Fetch: `bash eval/fetch_data.sh` (clones into .data/stocknet-dataset; gitignored).
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd

from architecture.contracts.contracts import BARS, DOCS, validate

TWITTER_TS = "%a %b %d %H:%M:%S %z %Y"


def _parse_line(ticker: str, line: str) -> dict | None:
    try:
        d = json.loads(line)
    except json.JSONDecodeError:
        return None
    u = d.get("user") or {}
    ent = d.get("entities") or {}
    return {
        "ticker": ticker,
        "doc_id": str(d.get("id_str") or d.get("id")),
        "ts": d.get("created_at"),
        "text": d.get("text") or "",
        "user_id": str(u.get("id_str") or u.get("id") or ""),
        "user_followers": int(u.get("followers_count") or 0),
        "user_created": u.get("created_at"),
        "user_verified": bool(u.get("verified") or False),
        "user_statuses": int(u.get("statuses_count") or 0),
        "is_retweet": "retweeted_status" in d,
        "n_cashtags": len(ent.get("symbols") or []),
        "has_url": len(ent.get("urls") or []) > 0,
    }


def load_tweets(root: str | os.PathLike) -> pd.DataFrame:
    """Parse every raw tweet JSON line under <root>/tweet/raw/<TICKER>/<YYYY-MM-DD>."""
    raw = Path(root) / "tweet" / "raw"
    rows = []
    for tdir in sorted(p for p in raw.iterdir() if p.is_dir()):
        for f in sorted(tdir.iterdir()):
            with open(f, encoding="utf-8") as fh:
                for line in fh:
                    r = _parse_line(tdir.name, line)
                    if r is not None:
                        rows.append(r)
    df = pd.DataFrame(rows)
    df["ts_utc"] = pd.to_datetime(df.pop("ts"), format=TWITTER_TS, utc=True)
    uc = pd.to_datetime(df.pop("user_created"), format=TWITTER_TS, utc=True, errors="coerce")
    df["user_age_days"] = ((df["ts_utc"] - uc).dt.total_seconds() / 86400).fillna(0).clip(lower=0)
    df["source"] = "real"
    df = df.drop_duplicates(["ticker", "doc_id"]).reset_index(drop=True)
    return validate(df[list(DOCS.columns)], DOCS)


def load_prices(root: str | os.PathLike) -> pd.DataFrame:
    """Read <root>/price/raw/<TICKER>.csv (Yahoo daily OHLC, adjusted close, volume)."""
    frames = []
    for f in sorted((Path(root) / "price" / "raw").glob("*.csv")):
        p = pd.read_csv(f)
        p = p.rename(columns={"Date": "date", "Open": "open", "High": "high", "Low": "low",
                              "Close": "close", "Adj Close": "adj_close", "Volume": "volume"})
        p["ticker"] = f.stem
        frames.append(p)
    df = pd.concat(frames, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    for c in ["open", "high", "low", "close", "adj_close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype(float)
    df = df.dropna(subset=["open", "high", "low", "close", "adj_close"])
    df = df[(df[["open", "high", "low", "close", "adj_close"]] > 0).all(axis=1) & (df["high"] >= df["low"])]
    df = df.drop_duplicates(["ticker", "date"]).sort_values(["ticker", "date"]).reset_index(drop=True)
    return validate(df[list(BARS.columns)], BARS)
