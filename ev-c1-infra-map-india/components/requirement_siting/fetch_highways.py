"""Maharashtra motorway + trunk ways with geometry from OpenStreetMap (Overpass). ODbL 1.0, © OpenStreetMap contributors.
Usage (from ev-c1-infra-map-india/): .venv/bin/python components/requirement_siting/fetch_highways.py
Writes .data/roads/mh_motorway_trunk.json (Overpass JSON with geometry).
"""
import datetime as dt, json, os
import requests
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, ".data", "roads"); os.makedirs(OUT, exist_ok=True)
Q = """[out:json][timeout:600];
area["ISO3166-2"="IN-MH"][admin_level=4]->.mh;
way["highway"~"^(motorway|trunk)$"](area.mh);
out tags geom;"""
for ep in ("https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"):
    try:
        r = requests.post(ep, data={"data": Q}, timeout=700, headers={"User-Agent": "EV-Infra-Map-India research (Techfest 2026)"})
        r.raise_for_status(); d = r.json(); d["_fetched_at"] = dt.datetime.now().isoformat(timespec="seconds"); d["_endpoint"] = ep
        json.dump(d, open(os.path.join(OUT, "mh_motorway_trunk.json"), "w"))
        print(f"ways={len(d['elements'])} osm_base={d.get('osm3s', {}).get('timestamp_osm_base')} endpoint={ep}")
        break
    except Exception as e:
        print("fail", ep, repr(e)[:120])
