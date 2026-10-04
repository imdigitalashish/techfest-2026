"""Fetch hourly CPCB/DPCC monitor data for Delhi from the public OpenAQ S3 archive (no API key).

Archive layout (verified 2026-10-04): records/csv.gz/locationid={id}/year={yyyy}/month={mm}/location-{id}-{yyyymmdd}.csv.gz
Columns: location_id, sensors_id, location, datetime (local ISO with offset), lat, lon, parameter, units, value.

Writes one parquet per station to <out>/station_<id>.parquet with hourly means (IST, hour-beginning),
plus <out>/manifest.json (files fetched, rows, failures). Raw files are not kept.

Usage:
  python fetch_openaq_archive.py --stations stations_delhi.csv --start 2023-10-01 --end 2026-09-30 \
      --out ../../.data/openaq --params pm25 pm10 wd ws temperature relativehumidity
"""
import argparse, csv, gzip, io, json, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import date
import pandas as pd
import requests

BUCKET = "https://openaq-data-archive.s3.amazonaws.com"


def month_iter(start: date, end: date):
    y, m = start.year, start.month
    while (y, m) <= (end.year, end.month):
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def list_keys(session, loc_id, y, m):
    prefix = f"records/csv.gz/locationid={loc_id}/year={y}/month={m:02d}/"
    for attempt in range(4):
        try:
            r = session.get(f"{BUCKET}/?list-type=2&prefix={prefix}&max-keys=1000", timeout=30)
            r.raise_for_status()
            return re.findall(r"<Key>([^<]+)</Key>", r.text)
        except Exception:
            time.sleep(2 ** attempt)
    return None


def fetch_day(session, key, params):
    for attempt in range(4):
        try:
            r = session.get(f"{BUCKET}/{key}", timeout=60)
            r.raise_for_status()
            df = pd.read_csv(io.BytesIO(gzip.decompress(r.content)))
            return df[df["parameter"].isin(params)][["location_id", "datetime", "parameter", "units", "value"]]
        except Exception:
            time.sleep(2 ** attempt)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stations", default="stations_delhi.csv")
    ap.add_argument("--ids", nargs="*", type=int, help="override: explicit location ids")
    ap.add_argument("--start", default="2023-10-01")
    ap.add_argument("--end", default="2026-09-30")
    ap.add_argument("--params", nargs="+", default=["pm25", "pm10", "wd", "ws", "temperature", "relativehumidity"])
    ap.add_argument("--out", default="../../.data/openaq")
    ap.add_argument("--workers", type=int, default=24)
    a = ap.parse_args()

    import os
    os.makedirs(a.out, exist_ok=True)
    start, end = date.fromisoformat(a.start), date.fromisoformat(a.end)
    if a.ids:
        ids = a.ids
    else:
        with open(a.stations) as fh:
            ids = [int(r["location_id"]) for r in csv.DictReader(fh)]
    s = requests.Session()
    manifest = {"source": BUCKET, "start": a.start, "end": a.end, "params": a.params, "stations": {}}

    for loc in ids:
        out_path = os.path.join(a.out, f"station_{loc}.parquet")
        if os.path.exists(out_path):
            print(f"skip {loc} (exists)", file=sys.stderr)
            continue
        t0 = time.time()
        with ThreadPoolExecutor(a.workers) as ex:
            key_lists = list(ex.map(lambda ym: list_keys(s, loc, *ym), month_iter(start, end)))
        keys = [k for kl in key_lists if kl for k in kl
                if a.start.replace("-", "") <= re.search(r"-(\d{8})\.csv\.gz$", k).group(1) <= a.end.replace("-", "")]
        with ThreadPoolExecutor(a.workers) as ex:
            parts = list(ex.map(lambda k: fetch_day(s, k, a.params), keys))
        failed = sum(p is None for p in parts)
        parts = [p for p in parts if p is not None and len(p)]
        if not parts:
            manifest["stations"][loc] = {"files": len(keys), "failed": failed, "rows": 0}
            print(f"{loc}: no data", file=sys.stderr)
            continue
        df = pd.concat(parts, ignore_index=True)
        # Timestamps carry +05:30; convert to naive IST and floor to the hour (hour-beginning convention).
        ts = pd.to_datetime(df["datetime"], utc=True).dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
        df["hour"] = ts.dt.floor("h")
        df = df[pd.to_numeric(df["value"], errors="coerce").notna()]
        df["value"] = df["value"].astype(float)
        units = df.groupby("parameter")["units"].agg(lambda u: "|".join(sorted(set(map(str, u))))).to_dict()
        hourly = df.pivot_table(index="hour", columns="parameter", values="value", aggfunc="mean").sort_index()
        hourly.columns.name = None
        hourly.to_parquet(out_path)
        manifest["stations"][loc] = {"files": len(keys), "failed": failed, "rows": int(len(hourly)),
                                     "first": str(hourly.index.min()), "last": str(hourly.index.max()), "units": units,
                                     "seconds": round(time.time() - t0, 1)}
        print(f"{loc}: {len(keys)} files, {failed} failed, {len(hourly)} hourly rows, {time.time()-t0:.0f}s", file=sys.stderr)
        with open(os.path.join(a.out, "manifest.json"), "w") as fh:
            json.dump(manifest, fh, indent=1)


if __name__ == "__main__":
    main()
