"""C1 feed — normalise Tardis `quotes` CSVs and raw live frames into a QuoteFrame.

QuoteFrame contract: architecture/contracts/frames.py::QUOTE_FRAME.
"""
from __future__ import annotations

import glob
import gzip
import os
from datetime import datetime

import orjson
import polars as pl

from architecture.contracts.frames import QUOTE_FRAME

# Amount → base-asset units. Deribit BTC-PERPETUAL amounts are USD (contract_size 10 USD,
# verified via public/get_instrument on 2026-10-04); everything else is left as published.
USD_AMOUNT_VENUES = {"deribit"}


def load_tardis_quotes(path: str) -> pl.DataFrame:
    df = pl.read_csv(
        path,
        schema_overrides={"timestamp": pl.Int64, "local_timestamp": pl.Int64, "ask_amount": pl.Float64,
                          "ask_price": pl.Float64, "bid_price": pl.Float64, "bid_amount": pl.Float64},
    )
    df = df.drop_nulls(["bid_price", "ask_price"]).filter(
        (pl.col("bid_price") > 0) & (pl.col("ask_price") > pl.col("bid_price"))
    )
    venue = df["exchange"][0]
    out = df.select(
        pl.col("timestamp").alias("ts_exch_us"),
        pl.col("local_timestamp").alias("ts_recv_us"),
        (pl.col("timestamp") == pl.col("local_timestamp")).alias("exch_ts_imputed"),
        pl.col("exchange").alias("venue"),
        pl.col("symbol").alias("instrument"),
        pl.col("bid_price").alias("bid_px"),
        pl.col("bid_amount").fill_null(0.0).alias("bid_sz"),
        pl.col("ask_price").alias("ask_px"),
        pl.col("ask_amount").fill_null(0.0).alias("ask_sz"),
    )
    if venue in USD_AMOUNT_VENUES:
        out = out.with_columns((pl.col("bid_sz") / pl.col("bid_px")), (pl.col("ask_sz") / pl.col("ask_px")))
    return out.sort("ts_recv_us").cast(QUOTE_FRAME)


def load_tardis_day(root: str, date: str, include: list[str] | None = None) -> pl.DataFrame:
    files = sorted(glob.glob(os.path.join(root, "quotes", date, "*.csv.gz")))
    frames = []
    for f in files:
        key = os.path.basename(f).removesuffix(".csv.gz")
        if include and key not in include:
            continue
        frames.append(load_tardis_quotes(f))
    return pl.concat(frames).sort("ts_recv_us")


# ---------------------------------------------------------------- live frames
def _iso_us(s: str) -> int:
    # '2026-10-04T00:00:00.123456Z' (Coinbase/Kraken). fromisoformat handles up to 6 decimals.
    s = s.rstrip("Z")
    if "." in s:
        head, frac = s.split(".")
        s = f"{head}.{(frac + '000000')[:6]}"
    return int(datetime.fromisoformat(s + "+00:00").timestamp() * 1_000_000)


class _L2:
    """Tiny price-level book for venues that only send depth (Kraken book)."""

    def __init__(self) -> None:
        self.b: dict[float, float] = {}
        self.a: dict[float, float] = {}

    def apply(self, side: dict, levels: list) -> None:
        for lv in levels:
            px, q = float(lv["price"]), float(lv["qty"])
            if q == 0:
                side.pop(px, None)
            else:
                side[px] = q

    def bbo(self):
        if not self.b or not self.a:
            return None
        bp = max(self.b); ap = min(self.a)
        return bp, self.b[bp], ap, self.a[ap]


def parse_live_file(path: str, venue: str) -> list[tuple]:
    """Return rows (ts_exch_us|None, ts_recv_us, venue, instrument, bid, bsz, ask, asz)."""
    rows: list[tuple] = []
    books: dict[str, _L2] = {}
    side_state: dict[str, list] = {}
    with gzip.open(path, "rt") as fh:
        for line in fh:
            try:
                recv_ns, raw = line.split("\t", 1)
                recv = int(recv_ns) // 1000
                if raw[0] != "{":
                    continue
                m = orjson.loads(raw)
                rows.extend(_parse_msg(venue, m, recv, books, side_state))
            except Exception:  # noqa: BLE001 — malformed/partial lines are counted by the caller
                continue
    return rows


def _parse_msg(venue: str, m: dict, recv: int, books: dict, st: dict) -> list[tuple]:
    out = []
    if venue in ("binance", "binance-futures"):
        d = m.get("data") or {}
        if "b" in d and "a" in d:
            ts = d.get("E")
            out.append((ts * 1000 if ts else None, recv, venue, d["s"], float(d["b"]), float(d["B"]), float(d["a"]), float(d["A"])))
    elif venue == "coinbase":
        if m.get("type") == "ticker" and m.get("best_bid"):
            out.append((_iso_us(m["time"]), recv, venue, m["product_id"], float(m["best_bid"]), float(m.get("best_bid_size") or 0),
                        float(m["best_ask"]), float(m.get("best_ask_size") or 0)))
    elif venue == "kraken":
        if m.get("channel") == "book":
            for d in m.get("data", []):
                sym = d["symbol"]
                bk = books.setdefault(sym, _L2())
                if m.get("type") == "snapshot":
                    bk.b.clear(); bk.a.clear()
                bk.apply(bk.b, d.get("bids", [])); bk.apply(bk.a, d.get("asks", []))
                # keep depth bounded like the venue does (depth=10)
                for side, rev in ((bk.b, True), (bk.a, False)):
                    if len(side) > 10:
                        for px in sorted(side, reverse=not rev)[: len(side) - 10]:
                            side.pop(px, None)
                q = bk.bbo()
                ts = d.get("timestamp")
                if q:
                    out.append((_iso_us(ts) if ts else None, recv, venue, sym, q[0], q[1], q[2], q[3]))
    elif venue == "okx":
        arg = m.get("arg") or {}
        for d in m.get("data", []) or []:
            if d.get("bids") and d.get("asks"):
                out.append((int(d["ts"]) * 1000, recv, venue, arg.get("instId"), float(d["bids"][0][0]), float(d["bids"][0][1]),
                            float(d["asks"][0][0]), float(d["asks"][0][1])))
    elif venue in ("bybit", "bybit-spot"):
        if str(m.get("topic", "")).startswith("orderbook.1."):
            d = m["data"]; sym = d["s"]
            s = st.setdefault(venue + sym, [None, 0.0, None, 0.0])
            if d.get("b"):
                s[0], s[1] = float(d["b"][0][0]), float(d["b"][0][1])
            if d.get("a"):
                s[2], s[3] = float(d["a"][0][0]), float(d["a"][0][1])
            if s[0] and s[2] and s[1] > 0 and s[3] > 0:
                ts = m.get("cts") or m.get("ts")
                out.append((int(ts) * 1000, recv, venue, sym, s[0], s[1], s[2], s[3]))
    elif venue == "deribit":
        p = m.get("params") or {}
        d = p.get("data") or {}
        if str(p.get("channel", "")).startswith("quote.") and d.get("best_bid_price"):
            bp, ap = float(d["best_bid_price"]), float(d["best_ask_price"])
            out.append((int(d["timestamp"]) * 1000, recv, venue, d["instrument_name"], bp, float(d["best_bid_amount"]) / bp,
                        ap, float(d["best_ask_amount"]) / ap))
    elif venue == "hyperliquid":
        if m.get("channel") == "bbo":
            d = m["data"]; b, a = d["bbo"][0], d["bbo"][1]
            if b and a:
                out.append((int(d["time"]) * 1000, recv, venue, d["coin"], float(b["px"]), float(b["sz"]), float(a["px"]), float(a["sz"])))
    elif venue == "gateio":
        r = m.get("result") or {}
        if m.get("channel") == "spot.book_ticker" and r.get("b"):
            out.append((int(r["t"]) * 1000, recv, venue, r["s"], float(r["b"]), float(r["B"]), float(r["a"]), float(r["A"])))
    elif venue == "bitget":
        arg = m.get("arg") or {}
        for d in m.get("data", []) or []:
            if d.get("bids") and d.get("asks"):
                out.append((int(d["ts"]) * 1000, recv, venue, arg.get("instId"), float(d["bids"][0][0]), float(d["bids"][0][1]),
                            float(d["asks"][0][0]), float(d["asks"][0][1])))
    return out


def load_live(root: str, venues: list[str] | None = None) -> pl.DataFrame:
    rows: list[tuple] = []
    for vdir in sorted(glob.glob(os.path.join(root, "*"))):
        venue = os.path.basename(vdir)
        if venue.startswith("_") or (venues and venue not in venues):
            continue
        for f in sorted(glob.glob(os.path.join(vdir, "*.tsv.gz"))):
            rows.extend(parse_live_file(f, venue))
    df = pl.DataFrame(rows, schema=["ts_exch_us", "ts_recv_us", "venue", "instrument", "bid_px", "bid_sz", "ask_px", "ask_sz"],
                      orient="row", schema_overrides={"ts_exch_us": pl.Int64, "ts_recv_us": pl.Int64})
    df = df.with_columns(pl.col("ts_exch_us").is_null().alias("exch_ts_imputed"))
    df = df.with_columns(pl.col("ts_exch_us").fill_null(pl.col("ts_recv_us")))
    df = df.filter((pl.col("bid_px") > 0) & (pl.col("ask_px") > pl.col("bid_px")))
    return df.select(list(QUOTE_FRAME)).cast(QUOTE_FRAME).sort("ts_recv_us")
