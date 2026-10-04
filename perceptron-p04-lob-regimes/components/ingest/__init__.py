"""C1 Ingest: Tardis `book_snapshot_5` CSV.gz -> BookDay (cached as .npz in .data/cache)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl

from components.contracts import BookDay

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / ".data" / "raw" / "tardis" / "binance-futures" / "book_snapshot_5"
CACHE = ROOT / ".data" / "cache" / "book"
LEVELS = 5


def raw_path(day: str, symbol: str = "BTCUSDT") -> Path:
    return RAW / f"{day}_{symbol}.csv.gz"


def load_book_day(day: str, symbol: str = "BTCUSDT", use_cache: bool = True) -> BookDay:
    cache = CACHE / f"{day}_{symbol}.npz"
    if use_cache and cache.exists():
        z = np.load(cache)
        return BookDay(symbol, day, z["recv_us"], z["exch_us"], z["bid_px"], z["bid_sz"], z["ask_px"], z["ask_sz"])
    df = pl.read_csv(raw_path(day, symbol), infer_schema_length=10000)
    # Receive time is the clock a live system runs on; stable sort keeps message order on ties.
    df = df.with_row_index("_i").sort(["local_timestamp", "_i"])

    def arr(side: str, f: str) -> np.ndarray:
        return df.select([f"{side}[{i}].{f}" for i in range(LEVELS)]).to_numpy().astype(np.float64)

    book = BookDay(
        symbol=symbol, day=day,
        recv_us=df["local_timestamp"].to_numpy().astype(np.int64),
        exch_us=df["timestamp"].to_numpy().astype(np.int64),
        bid_px=arr("bids", "price"), bid_sz=arr("bids", "amount"),
        ask_px=arr("asks", "price"), ask_sz=arr("asks", "amount"),
    )
    CACHE.mkdir(parents=True, exist_ok=True)
    np.savez(cache, recv_us=book.recv_us, exch_us=book.exch_us, bid_px=book.bid_px,
             bid_sz=book.bid_sz, ask_px=book.ask_px, ask_sz=book.ask_sz)
    return book


def available_days(symbol: str = "BTCUSDT") -> list[str]:
    return sorted(p.name.split("_")[0] for p in RAW.glob(f"*_{symbol}.csv.gz"))
