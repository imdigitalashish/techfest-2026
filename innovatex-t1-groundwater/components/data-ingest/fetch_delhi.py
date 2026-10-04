"""Fetch REAL public data for the Delhi groundwater digital twin.

Sources (all public, no key):
  1. India-WRIS / NWIC ArcGIS REST - groundwater-level station metadata for state_name='Delhi'
     https://arc.indiawris.gov.in/server/rest/services/NWIC/GroundwaterLevel_Stations/MapServer/0
  2. India-WRIS dataset API (POST) - groundwater-level time series (manual + telemetric DWLR)
     https://indiawris.gov.in/Dataset/Ground%20Water%20Level?stateName=Delhi&districtName=..&agencyName=..
  3. Open-Meteo historical archive (ERA5 reanalysis) - Delhi daily rain/ET0/temperature and
     hourly rain + surface pressure. https://archive-api.open-meteo.com/v1/archive

Run (idempotent; raw responses cached in innovatex-t1-groundwater/.data/):
  innovatex-t1-groundwater/.venv/bin/python innovatex-t1-groundwater/components/data-ingest/fetch_delhi.py

Outputs (small, committed, with attribution in eval/data/README.md):
  eval/data/delhi_gw_stations.csv   station metadata (ArcGIS layer)
  eval/data/delhi_gw_levels.csv.gz  tidy time series: station_id, datetime_ist, value_m, depth_mbgl, mode, ...
  eval/data/delhi_weather_daily.csv daily ERA5 drivers for central Delhi
  .data/delhi_weather_hourly.csv    hourly rain + surface pressure (gitignored, regenerable)
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import pathlib
import sys
import time
import urllib.parse

import pandas as pd
import requests

ROOT = pathlib.Path(__file__).resolve().parents[2]          # innovatex-t1-groundwater/
RAW = ROOT / ".data" / "wris"
OUT = ROOT / "eval" / "data"
RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

ARC = "https://arc.indiawris.gov.in/server/rest/services/NWIC/GroundwaterLevel_Stations/MapServer/0/query"
WRIS = "https://indiawris.gov.in/Dataset/Ground%20Water%20Level"
START, END = "2015-01-01", "2026-10-03"
PAGE = 5000
UA = {"User-Agent": "techfest-2026-research (student project; contact via GitHub imdigitalashish)"}


def _get_json(method: str, url: str, cache: pathlib.Path, tries: int = 4, headers: dict | None = None) -> dict:
    if cache.exists() and cache.stat().st_size > 0:
        return json.loads(cache.read_text())
    last = None
    for i in range(tries):
        try:
            r = requests.request(method, url, timeout=180, headers=headers or UA)
            r.raise_for_status()
            d = r.json()
            cache.write_text(json.dumps(d))
            return d
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(5 * (i + 1))
    raise RuntimeError(f"failed {url}: {last}")


def stations() -> pd.DataFrame:
    rows, off = [], 0
    while True:
        q = {"where": "state_name='Delhi'", "outFields": "*", "returnGeometry": "false",
             "resultOffset": off, "resultRecordCount": 1000, "f": "json"}
        d = _get_json("GET", ARC + "?" + urllib.parse.urlencode(q), RAW / f"arc_stations_{off}.json")
        feats = d.get("features", [])
        rows += [f["attributes"] for f in feats]
        if not d.get("exceededTransferLimit") or not feats:
            break
        off += len(feats)
    df = pd.DataFrame(rows)
    keep = ["station_code", "station_name", "station_type", "lat", "long", "telemetry", "agency_name",
            "district_name", "block_name", "basin_name", "created_date"]
    df = df[[c for c in keep if c in df.columns]].rename(columns={"long": "lon", "station_code": "station_id"})
    df["source"] = "India-WRIS/NWIC ArcGIS NWIC/GroundwaterLevel_Stations layer 0"
    return df.drop_duplicates("station_id")


def _levels_page(district: str, agency: str, page: int) -> list[dict]:
    q = {"stateName": "Delhi", "districtName": district, "agencyName": agency, "startdate": START,
         "enddate": END, "download": "false", "page": page, "size": PAGE}
    tag = f"lvl_{district}_{agency}_{page}".replace(" ", "_").replace("/", "_")
    d = _get_json("POST", WRIS + "?" + urllib.parse.urlencode(q), RAW / f"{tag}.json",
                  headers={**UA, "Content-Type": "application/json"})
    return d.get("data") or []


def levels_for(district: str, agency: str) -> list[dict]:
    out, page = [], 0
    while True:
        rows = _levels_page(district, agency, page)
        out += rows
        print(f"  {district:>20} | {agency:<12} | page {page} -> {len(rows)} rows", flush=True)
        if len(rows) < PAGE:
            return out
        page += 1


def weather() -> None:
    base = "https://archive-api.open-meteo.com/v1/archive"
    lat, lon = 28.6139, 77.2090  # central New Delhi
    qd = {"latitude": lat, "longitude": lon, "start_date": "2010-01-01", "end_date": "2026-09-30",
          "daily": "precipitation_sum,et0_fao_evapotranspiration,temperature_2m_mean", "timezone": "Asia/Kolkata"}
    d = _get_json("GET", base + "?" + urllib.parse.urlencode(qd), ROOT / ".data" / "openmeteo_daily.json")
    df = pd.DataFrame(d["daily"]).rename(columns={"time": "date", "precipitation_sum": "precip_mm",
                                                  "et0_fao_evapotranspiration": "et0_mm",
                                                  "temperature_2m_mean": "temp_mean_c"})
    df["source"] = "Open-Meteo archive (ERA5 reanalysis), 28.6139N 77.2090E"
    df.to_csv(OUT / "delhi_weather_daily.csv", index=False)
    qh = {"latitude": lat, "longitude": lon, "start_date": "2022-01-01", "end_date": "2026-09-30",
          "hourly": "precipitation,surface_pressure,temperature_2m", "timezone": "Asia/Kolkata"}
    h = _get_json("GET", base + "?" + urllib.parse.urlencode(qh), ROOT / ".data" / "openmeteo_hourly.json")
    hf = pd.DataFrame(h["hourly"]).rename(columns={"time": "datetime_ist", "precipitation": "precip_mm",
                                                   "surface_pressure": "pressure_hpa", "temperature_2m": "temp_c"})
    hf.to_csv(ROOT / ".data" / "delhi_weather_hourly.csv", index=False)
    print(f"weather: daily {len(df)} rows, hourly {len(hf)} rows")


def main() -> int:
    weather()
    st = stations()
    st.to_csv(OUT / "delhi_gw_stations.csv", index=False)
    print(f"stations: {len(st)}; agencies: {st.agency_name.value_counts().to_dict()}")
    # district names come in case variants ("South"/"SOUTH"); the API is queried once per name
    seen: dict[str, str] = {}
    for d in sorted(st.district_name.dropna().unique()):
        seen.setdefault(d.strip().upper(), d.strip())
    districts = sorted(seen.values())
    agencies = sorted(st.agency_name.dropna().unique())
    jobs = [(d, a) for d in districts for a in agencies]
    rows: list[dict] = []
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for fut in cf.as_completed({ex.submit(levels_for, d, a): (d, a) for d, a in jobs}):
            try:
                rows += fut.result()
            except Exception as e:  # noqa: BLE001
                print("ERROR", e, file=sys.stderr)
    if not rows:
        print("no level rows fetched", file=sys.stderr)
        return 1
    lv = pd.DataFrame(rows)
    lv = lv.rename(columns={"stationCode": "station_id", "dataTime": "datetime_ist", "dataValue": "value_m",
                            "dataAcquisitionMode": "mode", "description": "series"})
    # WRIS reports groundwater level as a negative number of metres relative to ground (e.g. -23.4).
    lv["depth_mbgl"] = -lv["value_m"]
    keep = ["station_id", "stationName", "agencyName", "district", "latitude", "longitude", "mode", "series",
            "datatypeCode", "datetime_ist", "value_m", "depth_mbgl", "unit", "wellType", "wellDepth", "wellAquiferType"]
    lv = lv[[c for c in keep if c in lv.columns]].drop_duplicates(["station_id", "datetime_ist", "datatypeCode"])
    lv = lv.sort_values(["station_id", "datetime_ist"])
    lv.to_csv(OUT / "delhi_gw_levels.csv.gz", index=False, compression="gzip")
    summ = lv.groupby(["station_id", "mode"]).agg(n=("value_m", "size"), first=("datetime_ist", "min"),
                                                 last=("datetime_ist", "max"),
                                                 depth_med=("depth_mbgl", "median")).reset_index()
    summ.to_csv(OUT / "delhi_gw_levels_summary.csv", index=False)
    print(f"levels: {len(lv)} rows, {lv.station_id.nunique()} stations; modes {lv['mode'].value_counts().to_dict()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
