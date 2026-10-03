"""Live multi-venue top-of-book + trade recorder.

Writes every raw websocket text frame, prefixed with the local receive time
(time.time_ns()), to  <out>/<venue>/<venue>-<UTC hour>.tsv.gz  as
"recv_ns<TAB>raw_json". Parsing/normalisation happens offline (normalize.py),
so this process does as little as possible between socket and disk.

Also logs NTP clock offset every 10 minutes (sntp) to <out>/_clock/offsets.tsv,
because feed latency = recv_ns - exchange_ts is only meaningful up to clock error.

Usage:
  .venv/bin/python components/feed/live_recorder.py --out .data/live --hours 6
"""
from __future__ import annotations

import argparse
import asyncio
import gzip
import json
import os
import random
import subprocess
import sys
import time
from dataclasses import dataclass, field

import websockets


@dataclass
class VenueSpec:
    name: str
    url: str
    subscribe: list[str]
    ping: str | None = None          # application-level ping payload
    ping_every_s: float = 20.0
    extra: dict = field(default_factory=dict)


def specs() -> list[VenueSpec]:
    """BBO-only, bandwidth-light configuration (the link is shared and slow).

    BTC on every venue; ETH on a few liquid venues for the cross-asset (BTC/ETH) tier.
    """
    return [
        VenueSpec("binance", "wss://stream.binance.com:9443/stream?streams=btcusdt@bookTicker/ethusdt@bookTicker", []),
        VenueSpec("binance-futures", "wss://fstream.binance.com/stream?streams=btcusdt@bookTicker/ethusdt@bookTicker", []),
        VenueSpec(
            "coinbase",
            "wss://ws-feed.exchange.coinbase.com",
            [json.dumps({"type": "subscribe", "product_ids": ["BTC-USD", "ETH-USD", "USDT-USD"], "channels": ["ticker"]})],
        ),
        VenueSpec(
            "kraken",
            "wss://ws.kraken.com/v2",
            [json.dumps({"method": "subscribe", "params": {"channel": "book", "symbol": ["BTC/USD", "USDT/USD"], "depth": 10}})],
            ping=json.dumps({"method": "ping"}), ping_every_s=20,
        ),
        VenueSpec(
            "okx",
            "wss://ws.okx.com:8443/ws/v5/public",
            [json.dumps({"op": "subscribe", "args": [
                {"channel": "bbo-tbt", "instId": i} for i in ("BTC-USDT", "BTC-USDT-SWAP", "ETH-USDT-SWAP")]})],
            ping="ping", ping_every_s=20,
        ),
        VenueSpec(
            "bybit-spot",
            "wss://stream.bybit.com/v5/public/spot",
            [json.dumps({"op": "subscribe", "args": ["orderbook.1.BTCUSDT"]})],
            ping=json.dumps({"op": "ping"}), ping_every_s=20,
        ),
        VenueSpec(
            "bybit",
            "wss://stream.bybit.com/v5/public/linear",
            [json.dumps({"op": "subscribe", "args": ["orderbook.1.BTCUSDT", "orderbook.1.ETHUSDT"]})],
            ping=json.dumps({"op": "ping"}), ping_every_s=20,
        ),
        VenueSpec(
            "bitstamp",
            "wss://ws.bitstamp.net",
            [json.dumps({"event": "bts:subscribe", "data": {"channel": "live_trades_btcusd"}})],
        ),
        VenueSpec(
            "deribit",
            "wss://www.deribit.com/ws/api/v2",
            [json.dumps({"jsonrpc": "2.0", "id": 1, "method": "public/subscribe",
                         "params": {"channels": ["quote.BTC-PERPETUAL"]}})],
            ping=json.dumps({"jsonrpc": "2.0", "id": 9, "method": "public/test", "params": {}}), ping_every_s=20,
        ),
        VenueSpec(
            "hyperliquid",
            "wss://api.hyperliquid.xyz/ws",
            [json.dumps({"method": "subscribe", "subscription": {"type": "bbo", "coin": "BTC"}})],
            ping=json.dumps({"method": "ping"}), ping_every_s=30,
        ),
        VenueSpec(
            "gateio",
            "wss://api.gateio.ws/ws/v4/",
            [json.dumps({"time": 0, "channel": "spot.book_ticker", "event": "subscribe", "payload": ["BTC_USDT"]})],
            ping=json.dumps({"time": 0, "channel": "spot.ping"}), ping_every_s=20,
        ),
        VenueSpec(
            "bitget",
            "wss://ws.bitget.com/v2/ws/public",
            [json.dumps({"op": "subscribe", "args": [
                {"instType": "SPOT", "channel": "books1", "instId": "BTCUSDT"}]})],
            ping="ping", ping_every_s=25,
        ),
    ]


class RotatingGzWriter:
    def __init__(self, root: str, venue: str):
        self.dir = os.path.join(root, venue)
        os.makedirs(self.dir, exist_ok=True)
        self.venue = venue
        self.hour = None
        self.fh = None
        self.n = 0

    def write(self, recv_ns: int, raw: str) -> None:
        hour = time.strftime("%Y%m%dT%H", time.gmtime(recv_ns / 1e9))
        if hour != self.hour:
            if self.fh:
                self.fh.close()
            self.fh = gzip.open(os.path.join(self.dir, f"{self.venue}-{hour}.tsv.gz"), "at", compresslevel=3)
            self.hour = hour
        self.fh.write(f"{recv_ns}\t{raw}\n")
        self.n += 1

    def flush(self) -> None:
        if self.fh:
            self.fh.flush()

    def close(self) -> None:
        if self.fh:
            self.fh.close()


async def run_venue(spec: VenueSpec, root: str, stop_at: float, stats: dict) -> None:
    w = RotatingGzWriter(root, spec.name)
    log = open(os.path.join(root, "_logs", f"{spec.name}.log"), "a")
    backoff = 1.0
    while time.time() < stop_at:
        try:
            async with websockets.connect(spec.url, max_size=2**24, ping_interval=20, ping_timeout=60,
                                          open_timeout=15, close_timeout=5) as ws:
                for m in spec.subscribe:
                    await ws.send(m)
                log.write(f"{time.time_ns()}\tCONNECTED\n"); log.flush()
                backoff = 1.0
                last_ping = time.time()
                last_flush = time.time()
                while time.time() < stop_at:
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=5)
                    except asyncio.TimeoutError:
                        raw = None
                    now = time.time()
                    if raw is not None:
                        recv_ns = time.time_ns()
                        if isinstance(raw, bytes):
                            raw = raw.decode("utf-8", "replace")
                        w.write(recv_ns, raw.replace("\n", " "))
                        stats[spec.name] = stats.get(spec.name, 0) + 1
                    if spec.ping and now - last_ping > spec.ping_every_s:
                        p = spec.ping
                        if spec.name == "gateio":
                            p = json.dumps({"time": int(now), "channel": "spot.ping"})
                        await ws.send(p)
                        last_ping = now
                    if now - last_flush > 5:
                        w.flush(); last_flush = now
        except Exception as e:  # noqa: BLE001 - recorder must survive anything
            log.write(f"{time.time_ns()}\tERROR\t{type(e).__name__}: {e}\n"); log.flush()
            await asyncio.sleep(backoff + random.random())
            backoff = min(backoff * 2, 60)
    w.close()
    log.close()


async def clock_logger(root: str, stop_at: float) -> None:
    path = os.path.join(root, "_clock", "offsets.tsv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    while time.time() < stop_at:
        try:
            proc = await asyncio.create_subprocess_exec(
                "sntp", "time.apple.com", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
            out, _ = await asyncio.wait_for(proc.communicate(), timeout=20)
            text = out.decode().strip()
            line = text.splitlines()[-1] if text else ""
            with open(path, "a") as f:
                f.write(f"{time.time_ns()}\t{line}\n")
        except Exception as e:  # noqa: BLE001
            with open(path, "a") as f:
                f.write(f"{time.time_ns()}\tERROR {e}\n")
        await asyncio.sleep(600)


async def reporter(stats: dict, stop_at: float, root: str) -> None:
    while time.time() < stop_at:
        await asyncio.sleep(60)
        with open(os.path.join(root, "_logs", "counts.tsv"), "a") as f:
            f.write(f"{time.time_ns()}\t{json.dumps(stats, sort_keys=True)}\n")


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=".data/live")
    ap.add_argument("--hours", type=float, default=6.0)
    ap.add_argument("--only", default="", help="comma-separated venue names")
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "_logs"), exist_ok=True)
    stop_at = time.time() + a.hours * 3600
    chosen = [s for s in specs() if not a.only or s.name in a.only.split(",")]
    stats: dict = {}
    tasks = [run_venue(s, a.out, stop_at, stats) for s in chosen]
    tasks += [clock_logger(a.out, stop_at), reporter(stats, stop_at, a.out)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
