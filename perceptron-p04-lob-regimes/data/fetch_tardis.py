"""Download free Tardis.dev CSV datasets (first day of each month) into .data/raw/tardis/.

Tardis serves the first day of every month without an API key; other days return 401
(verified 2026-10-04). Each response carries an `x-md5` header, which we record in
data/manifest.csv so every downstream number can be traced to exact bytes.

Usage:
    python data/fetch_tardis.py --days 2024-05-01 2023-11-01 --types book_snapshot_5 trades
    python data/fetch_tardis.py --preset core
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / ".data" / "raw" / "tardis"
MANIFEST = ROOT / "data" / "manifest.csv"
BASE = "https://datasets.tardis.dev/v1"

# First-of-month days for Binance USD-M BTCUSDT. Event annotations live in
# data/events.csv (verified against official sources); this list only picks bytes.
PRESETS = {
    "core": [
        "2023-02-01", "2023-03-01", "2023-06-01", "2023-08-01", "2023-09-01",
        "2023-10-01", "2023-11-01", "2023-12-01", "2024-01-01", "2024-02-01",
        "2024-03-01", "2024-04-01", "2024-05-01", "2024-06-01", "2024-08-01",
        "2024-09-01", "2024-10-01", "2024-11-01", "2024-12-01", "2025-01-01",
        "2025-03-01", "2025-04-01", "2025-05-01", "2025-08-01",
    ],
}


def url_for(exchange: str, dtype: str, day: str, symbol: str) -> str:
    y, m, d = day.split("-")
    return f"{BASE}/{exchange}/{dtype}/{y}/{m}/{d}/{symbol}.csv.gz"


def path_for(exchange: str, dtype: str, day: str, symbol: str) -> Path:
    return RAW / exchange / dtype / f"{day}_{symbol}.csv.gz"


def md5_of(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(exchange: str, dtype: str, day: str, symbol: str, retries: int = 4) -> dict:
    url = url_for(exchange, dtype, day, symbol)
    out = path_for(exchange, dtype, day, symbol)
    out.parent.mkdir(parents=True, exist_ok=True)
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "techfest-p04/0.1"})
            with urllib.request.urlopen(req, timeout=120) as r:
                expected_md5 = (r.headers.get("x-md5") or "").strip('"')
                size = int(r.headers.get("content-length") or 0)
                if out.exists() and out.stat().st_size == size and expected_md5 and md5_of(out) == expected_md5:
                    return dict(exchange=exchange, dtype=dtype, day=day, symbol=symbol, url=url,
                                bytes=size, md5=expected_md5, status="cached")
                tmp = out.with_suffix(".part")
                with tmp.open("wb") as f:
                    while True:
                        chunk = r.read(1 << 20)
                        if not chunk:
                            break
                        f.write(chunk)
            got = md5_of(tmp)
            if expected_md5 and got != expected_md5:
                raise IOError(f"md5 mismatch {got} != {expected_md5}")
            tmp.replace(out)
            return dict(exchange=exchange, dtype=dtype, day=day, symbol=symbol, url=url,
                        bytes=out.stat().st_size, md5=got, status="downloaded")
        except Exception as e:  # network flakiness: retry with backoff
            last_err = e
            time.sleep(2 ** attempt)
    return dict(exchange=exchange, dtype=dtype, day=day, symbol=symbol, url=url,
                bytes=0, md5="", status=f"failed: {last_err}")


def write_manifest(rows: list[dict]) -> None:
    existing: dict[tuple, dict] = {}
    if MANIFEST.exists():
        with MANIFEST.open() as f:
            for r in csv.DictReader(f):
                existing[(r["exchange"], r["dtype"], r["day"], r["symbol"])] = r
    for r in rows:
        if r["status"] in ("downloaded", "cached"):
            existing[(r["exchange"], r["dtype"], r["day"], r["symbol"])] = {
                k: r[k] for k in ("exchange", "dtype", "day", "symbol", "url", "bytes", "md5")}
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["exchange", "dtype", "day", "symbol", "url", "bytes", "md5"])
        w.writeheader()
        for k in sorted(existing):
            w.writerow(existing[k])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exchange", default="binance-futures")
    ap.add_argument("--symbol", default="BTCUSDT")
    ap.add_argument("--types", nargs="+", default=["book_snapshot_5", "trades"])
    ap.add_argument("--days", nargs="*", default=[])
    ap.add_argument("--preset", choices=sorted(PRESETS), default=None)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    days = list(a.days) + (PRESETS[a.preset] if a.preset else [])
    if not days:
        ap.error("give --days or --preset")
    jobs = [(a.exchange, t, d, a.symbol) for d in days for t in a.types]
    rows = []
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(fetch, *j): j for j in jobs}
        for fu in as_completed(futs):
            r = fu.result()
            rows.append(r)
            print(f"{r['status']:>10}  {r['dtype']:<16} {r['day']}  {r['bytes']/1e6:8.1f} MB", flush=True)
            write_manifest(rows)
    failed = [r for r in rows if r["status"].startswith("failed")]
    print(f"done: {len(rows) - len(failed)} ok, {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
