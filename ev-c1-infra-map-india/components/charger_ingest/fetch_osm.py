"""Fetch every OpenStreetMap public-charging feature in India via the Overpass API.

Usage (from ev-c1-infra-map-india/):
    .venv/bin/python components/charger_ingest/fetch_osm.py
Writes .data/chargers/osm_india_raw.json (Overpass JSON, © OpenStreetMap contributors, ODbL 1.0)
and .data/chargers/osm_india.csv in the canonical ChargerRecord shape
(architecture/contracts/charger_record.schema.json).
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re

import pandas as pd
import requests

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, ".data", "chargers")
os.makedirs(OUT, exist_ok=True)
ENDPOINTS = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"]
QUERY = """[out:json][timeout:300];
area["ISO3166-1"="IN"][admin_level=2]->.in;
nwr["amenity"="charging_station"](area.in);
out center tags meta;"""

SOCKET_MAP = {  # OSM socket:* key -> canonical connector type
    "type2": "TYPE2", "type2_combo": "CCS2", "type2_cable": "TYPE2", "chademo": "CHADEMO", "gb_dc": "GBT_DC",
    "gb_ac": "GBT_AC", "type1": "TYPE1", "type1_combo": "CCS1", "tesla_supercharger": "TESLA",
    "schuko": "DOMESTIC", "bs1363": "DOMESTIC", "india_ac_15a": "IND_15A", "iec_60309": "IEC60309",
    "bharat_ac001": "BHARAT_AC001", "bharat_dc001": "BHARAT_DC001", "type3c": "TYPE3",
}


def _kw(val: str | None) -> float | None:
    if not val:
        return None
    m = re.search(r"([\d.]+)\s*(kw|w)?", val.lower())
    if not m:
        return None
    x = float(m.group(1))
    return x / 1000 if m.group(2) == "w" or x > 1000 else x


def to_records(osm: dict) -> pd.DataFrame:
    rows = []
    for e in osm["elements"]:
        t = e.get("tags", {})
        lat = e.get("lat", e.get("center", {}).get("lat"))
        lon = e.get("lon", e.get("center", {}).get("lon"))
        connectors = []
        for k, v in t.items():
            m = re.match(r"^socket:([a-z0-9_]+)$", k)
            if m:
                n = int(v) if str(v).isdigit() else (1 if v not in ("no", "0") else 0)
                if n:
                    connectors.append({"type": SOCKET_MAP.get(m.group(1), m.group(1).upper()), "count": n,
                                       "power_kw": _kw(t.get(f"socket:{m.group(1)}:output"))})
        rows.append({
            "source": "osm", "source_id": f"{e['type']}/{e['id']}", "lat": lat, "lon": lon,
            "name": t.get("name") or t.get("name:en"), "operator": t.get("operator"), "network": t.get("network"),
            "brand": t.get("brand"), "address": ", ".join(x for x in [t.get("addr:street"), t.get("addr:city"),
                                                                      t.get("addr:postcode")] if x) or None,
            "capacity": int(t["capacity"]) if str(t.get("capacity", "")).isdigit() else None,
            "connectors": json.dumps(connectors), "access": t.get("access"),
            "vehicle_motorcar": t.get("motorcar"), "vehicle_scooter": t.get("scooter") or t.get("motorcycle"),
            "fee": t.get("fee"), "opening_hours": t.get("opening_hours"),
            "last_edit": e.get("timestamp"), "license": "ODbL-1.0 (c) OpenStreetMap contributors",
        })
    return pd.DataFrame(rows)


def main() -> None:
    raw_path = os.path.join(OUT, "osm_india_raw.json")
    if not os.path.exists(raw_path):
        last = None
        for ep in ENDPOINTS:
            try:
                r = requests.post(ep, data={"data": QUERY}, timeout=400,
                                  headers={"User-Agent": "EV-Infra-Map-India research (Techfest 2026)"})
                r.raise_for_status()
                data = r.json()
                data["_fetched_at"] = dt.datetime.now().isoformat(timespec="seconds")
                data["_endpoint"] = ep
                json.dump(data, open(raw_path, "w"))
                break
            except Exception as e:  # try the mirror
                last = e
        else:
            raise SystemExit(f"Overpass failed: {last!r}")
    data = json.load(open(raw_path))
    df = to_records(data)
    df.to_csv(os.path.join(OUT, "osm_india.csv"), index=False)
    print(f"osm chargers: {len(df)} features; fetched_at={data.get('_fetched_at')} endpoint={data.get('_endpoint')}")


if __name__ == "__main__":
    main()
