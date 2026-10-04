"""Fetch NASA TechPort project records (public API, no key) into .data/techport/raw/<id>.json.gz.

Resumable and polite: shuffled order (fixed seed) so any partial snapshot is a random sample,
bounded concurrency, retries with exponential backoff. Stdlib only.

Usage:  python data/techport/fetch_techport.py [--workers 16] [--limit N]
Source: https://techport.nasa.gov/api/projects?updatedSince=YYYY-MM-DD and /api/projects/{id}
"""
from __future__ import annotations

import argparse
import gzip
import json
import random
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

API = "https://techport.nasa.gov/api"
ROOT = Path(__file__).resolve().parents[2] / ".data" / "techport"
RAW = ROOT / "raw"
UA = "techfest-2026-apctt-research/0.1 (academic hackathon; contact via github.com/imdigitalashish)"


def get_json(url: str, timeout: float = 90.0, tries: int = 6) -> dict | None:
    delay = 2.0
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code not in (429, 500, 502, 503, 504):
                raise
        except (urllib.error.URLError, TimeoutError, ConnectionError, json.JSONDecodeError):
            pass
        time.sleep(delay + random.random())
        delay = min(delay * 2, 60)
    return None


def list_ids() -> list[int]:
    idx = ROOT / "project_index.json"
    if idx.exists():
        data = json.loads(idx.read_text())
    else:
        data = get_json(f"{API}/projects?updatedSince=1990-01-01", timeout=180)
        idx.write_text(json.dumps(data))
    return [p["projectId"] for p in data["projects"]]


def fetch_one(pid: int) -> tuple[int, str]:
    out = RAW / f"{pid}.json.gz"
    if out.exists():
        return pid, "cached"
    data = get_json(f"{API}/projects/{pid}")
    if data is None:
        (RAW / f"{pid}.missing").touch()
        return pid, "missing"
    tmp = out.with_suffix(".tmp")
    with gzip.open(tmp, "wt", encoding="utf-8") as f:
        json.dump(data, f)
    tmp.rename(out)
    return pid, "ok"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    ids = list_ids()
    random.Random(20261004).shuffle(ids)
    if args.limit:
        ids = ids[: args.limit]
    todo = [i for i in ids if not (RAW / f"{i}.json.gz").exists() and not (RAW / f"{i}.missing").exists()]
    print(f"{len(ids)} ids, {len(todo)} to fetch", flush=True)
    t0, done = time.time(), 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(fetch_one, i) for i in todo]
        for fut in as_completed(futs):
            done += 1
            if done % 200 == 0 or done == len(todo):
                rate = done / (time.time() - t0)
                eta = (len(todo) - done) / max(rate, 1e-9) / 60
                print(f"{done}/{len(todo)}  {rate:.1f}/s  eta {eta:.0f} min", flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    sys.exit(main())
