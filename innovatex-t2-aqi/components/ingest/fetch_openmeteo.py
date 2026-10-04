"""Fetch hourly meteorology (ERA5 via Open-Meteo archive API) and CAMS air-quality fields (Open-Meteo
air-quality API) for a point in Delhi. No API key needed. Times are requested in Asia/Kolkata (IST).

Usage:
  python fetch_openmeteo.py --lat 28.61 --lon 77.21 --start 2023-10-01 --end 2026-09-30 --out ../../.data/openmeteo
"""
import argparse, json, os, sys, time
from datetime import date, timedelta
import pandas as pd
import requests

ERA5_URL = "https://archive-api.open-meteo.com/v1/archive"
AQ_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
MET_VARS = ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "surface_pressure", "precipitation",
            "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m", "boundary_layer_height", "cloud_cover",
            "shortwave_radiation"]
AQ_VARS = ["pm10", "pm2_5", "dust", "carbon_monoxide", "nitrogen_dioxide", "aerosol_optical_depth"]


def get(url, params, tries=5):
    for i in range(tries):
        try:
            r = requests.get(url, params=params, timeout=120)
            if r.status_code == 200:
                return r.json()
            print(f"HTTP {r.status_code}: {r.text[:200]}", file=sys.stderr)
        except Exception as e:
            print(f"warn: {e}", file=sys.stderr)
        time.sleep(2 ** i)
    raise RuntimeError(f"failed: {url} {params}")


def chunks(start, end, days=180):
    s = start
    while s <= end:
        e = min(end, s + timedelta(days=days - 1))
        yield s, e
        s = e + timedelta(days=1)


def fetch(url, variables, lat, lon, start, end):
    frames = []
    for s, e in chunks(start, end):
        j = get(url, {"latitude": lat, "longitude": lon, "start_date": s.isoformat(), "end_date": e.isoformat(),
                      "hourly": ",".join(variables), "timezone": "Asia/Kolkata"})
        h = j["hourly"]
        df = pd.DataFrame(h)
        df["time"] = pd.to_datetime(df["time"])
        frames.append(df.set_index("time"))
    out = pd.concat(frames).sort_index()
    return out[~out.index.duplicated()], {k: v for k, v in j.items() if k not in ("hourly",)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lat", type=float, default=28.61)
    ap.add_argument("--lon", type=float, default=77.21)
    ap.add_argument("--start", default="2023-10-01")
    ap.add_argument("--end", default="2026-09-30")
    ap.add_argument("--out", default="../../.data/openmeteo")
    ap.add_argument("--skip-aq", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    start, end = date.fromisoformat(a.start), date.fromisoformat(a.end)
    tag = f"{a.lat:.2f}_{a.lon:.2f}"
    met, meta = fetch(ERA5_URL, MET_VARS, a.lat, a.lon, start, end)
    met.to_parquet(os.path.join(a.out, f"era5_{tag}.parquet"))
    info = {"era5": {"url": ERA5_URL, "rows": len(met), "first": str(met.index.min()), "last": str(met.index.max()), "meta": meta}}
    print(f"era5 rows={len(met)}", file=sys.stderr)
    if not a.skip_aq:
        try:
            aq, meta2 = fetch(AQ_URL, AQ_VARS, a.lat, a.lon, start, end)
            aq.to_parquet(os.path.join(a.out, f"cams_{tag}.parquet"))
            info["cams"] = {"url": AQ_URL, "rows": len(aq), "first": str(aq.index.min()), "last": str(aq.index.max()),
                            "non_null_pm2_5": int(aq["pm2_5"].notna().sum()), "meta": meta2}
            print(f"cams rows={len(aq)} non-null pm2_5={aq['pm2_5'].notna().sum()}", file=sys.stderr)
        except Exception as e:
            info["cams_error"] = str(e)
    with open(os.path.join(a.out, f"manifest_{tag}.json"), "w") as fh:
        json.dump(info, fh, indent=1, default=str)


if __name__ == "__main__":
    main()
