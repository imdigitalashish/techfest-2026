"""Fetch Tardis.dev free first-of-month tick samples (no API key needed).

Tardis serves the first day of every month for free at
  https://datasets.tardis.dev/v1/{exchange}/{data_type}/{YYYY}/{MM}/{DD}/{symbol}.csv.gz
Do NOT send Range headers (the CDN answers 403). Files land in .data/tardis/ (gitignored).

Usage:
  .venv/bin/python components/feed/fetch_tardis.py --dates 2026-09-01 2026-10-01
"""
from __future__ import annotations

import argparse
import os
import sys
import time
import urllib.request

# (tardis exchange id, symbol) — BTC on every venue; ETH perp on two venues for the cross-asset tier.
DEFAULT = [
    ("binance", "BTCUSDT"),
    ("binance-futures", "BTCUSDT"),
    ("coinbase", "BTC-USD"),
    ("okex", "BTC-USDT"),
    ("okex-swap", "BTC-USDT-SWAP"),
    ("bybit", "BTCUSDT"),
    ("kraken", "BTC-USD"),
    ("bitstamp", "BTCUSD"),
    ("deribit", "BTC-PERPETUAL"),
    ("okex-swap", "ETH-USDT-SWAP"),
    ("bybit", "ETHUSDT"),
]


def fetch(exchange: str, symbol: str, date: str, data_type: str, out: str) -> str:
    y, m, d = date.split("-")
    url = f"https://datasets.tardis.dev/v1/{exchange}/{data_type}/{y}/{m}/{d}/{symbol}.csv.gz"
    dst = os.path.join(out, data_type, date, f"{exchange}_{symbol}.csv.gz")
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        return f"cached {dst}"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    tmp = dst + ".part"
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "p06-stat-arb/0.1"})
    with urllib.request.urlopen(req, timeout=600) as r, open(tmp, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    os.replace(tmp, dst)
    return f"ok {dst} {os.path.getsize(dst)/1e6:.1f}MB {time.time()-t0:.0f}s"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dates", nargs="+", default=["2026-09-01", "2026-10-01"])
    ap.add_argument("--type", default="quotes")
    ap.add_argument("--out", default=".data/tardis")
    a = ap.parse_args()
    for date in a.dates:
        for ex, sym in DEFAULT:
            for attempt in range(3):
                try:
                    print(fetch(ex, sym, date, a.type, a.out), flush=True)
                    break
                except Exception as e:  # noqa: BLE001
                    print(f"retry {attempt} {ex} {sym} {date}: {e}", file=sys.stderr, flush=True)
                    time.sleep(5)


if __name__ == "__main__":
    main()
