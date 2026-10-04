"""OSM public-charging features in India AS OF a past date (Overpass attic query), for point-in-time validation.
Usage: .venv/bin/python components/charger_ingest/fetch_osm_asof.py 2024-12-20 2025-08-01
Writes .data/chargers/osm_india_asof_<date>.csv (same columns as osm_india.csv). © OpenStreetMap contributors, ODbL 1.0.
"""
import datetime as dt, json, os, sys
import requests
sys.path.insert(0, os.path.dirname(__file__))
from fetch_osm import to_records, ENDPOINTS  # noqa: E402
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")); OUT = os.path.join(ROOT, ".data", "chargers")
for day in sys.argv[1:]:
    q = f"""[out:json][timeout:600][date:"{day}T00:00:00Z"];
area["ISO3166-1"="IN"][admin_level=2]->.in;
nwr["amenity"="charging_station"](area.in);
out center tags meta;"""
    for ep in ENDPOINTS:
        try:
            r = requests.post(ep, data={"data": q}, timeout=700, headers={"User-Agent": "EV-Infra-Map-India research (Techfest 2026)"})
            r.raise_for_status(); d = r.json()
            df = to_records(d); df.to_csv(os.path.join(OUT, f"osm_india_asof_{day}.csv"), index=False)
            json.dump({"as_of": day, "fetched_at": dt.datetime.now().isoformat(timespec="seconds"), "endpoint": ep, "n": len(df)},
                      open(os.path.join(OUT, f"osm_india_asof_{day}.json"), "w"))
            print(f"osm as of {day}: {len(df)} features ({ep})"); break
        except Exception as e:
            print("fail", day, ep, repr(e)[:120])
