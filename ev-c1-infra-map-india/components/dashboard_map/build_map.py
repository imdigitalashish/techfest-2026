"""Build a self-contained national map (walking skeleton v0): components/dashboard_map/dist/index.html

Layers: state choropleth of BEV registrations per official public charging station; OSM and OCM charging sites.
Inputs (all produced by committed scripts): eval/results/state_gap_baseline.csv, eval/results/census_v0_by_state.csv,
.data/chargers/{osm,ocm}_india.csv, .data/geo/ind_adm1.geojson (geoBoundaries IND ADM1; DataMeet/ECI; CC BY 2.5 IN).
Usage: .venv/bin/python -W ignore components/dashboard_map/build_map.py
"""
import json, os, re, unicodedata
import pandas as pd, geopandas as gpd
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
norm = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().replace("&", "and"))
ALIAS = {"utofdnhanddd": "dadraandnagarhavelianddamananddiu", "andamanandnicobarisland": "andamanandnicobarislands"}
key = lambda s: ALIAS.get(norm(s), norm(s))
adm = gpd.read_file(f"{R}/.data/geo/ind_adm1.geojson")[["shapeName", "geometry"]]
adm["geometry"] = adm.geometry.simplify(0.02, preserve_topology=True)
adm["k"] = adm.shapeName.map(key)
gap = pd.read_csv(f"{R}/eval/results/state_gap_baseline.csv"); gap["k"] = gap.vahan_state.map(key)
cen = pd.read_csv(f"{R}/eval/results/census_v0_by_state.csv"); cen["k"] = cen.state.map(key)
st = adm.merge(gap[["k", "vahan_state", "bev_cum", "bev_2025", "pcs_total", "bev_per_pcs", "bev_share_2025_pct"]], on="k", how="left")
st = st.merge(cen[["k", "n_osm", "n_ocm", "matched", "union"]], on="k", how="left")
st["open_coverage_pct"] = (100 * st["union"] / st.pcs_total).round(1)
unmatched = st[st.vahan_state.isna()].shapeName.tolist()
states_geojson = json.loads(st.drop(columns=["k"]).to_json())
pts = []
for src in ("osm", "ocm"):
    d = pd.read_csv(f"{R}/.data/chargers/{src}_india.csv").dropna(subset=["lat", "lon"])
    for r in d.itertuples():
        pts.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [round(r.lon, 5), round(r.lat, 5)]},
                    "properties": {"src": src, "name": str(r.name)[:80] if isinstance(r.name, str) else "", "id": r.source_id}})
sites_geojson = {"type": "FeatureCollection", "features": pts}
tpl = open(os.path.join(os.path.dirname(__file__), "template.html")).read()
html = tpl.replace("__STATES__", json.dumps(states_geojson, separators=(",", ":"))).replace("__SITES__", json.dumps(sites_geojson, separators=(",", ":")))
out = os.path.join(os.path.dirname(__file__), "dist", "index.html"); open(out, "w").write(html)
print(f"wrote {out} ({os.path.getsize(out)/1e6:.2f} MB); states={len(st)} unmatched_to_vahan={unmatched}; sites={len(pts)}")
