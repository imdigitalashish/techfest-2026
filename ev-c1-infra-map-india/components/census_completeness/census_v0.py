"""Spike 1, v0: cross-source site matching (C4 baseline) + capture-recapture completeness per state (C5 baseline).

Sources: OSM (Overpass, ODbL) and Open Charge Map (export, India subset). States by point-in-polygon on
geoBoundaries IND ADM1 (DataMeet/ECI, CC BY 2.5 IN; analysis only, not for the public map).
Held-out ground truth: official state-wise public charging stations, PIB 2151390 (1 Aug 2025).
Reproduce: fetch_osm.py, fetch_ocm.py, official_pcs.py, then
  .venv/bin/python -W ignore components/census_completeness/census_v0.py
"""
import json, os, re, unicodedata
import numpy as np, pandas as pd, geopandas as gpd
from rapidfuzz import fuzz
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(R, "eval", "results"); os.makedirs(OUT, exist_ok=True)
osm = pd.read_csv(f"{R}/.data/chargers/osm_india.csv"); ocm = pd.read_csv(f"{R}/.data/chargers/ocm_india.csv")
osm = osm.dropna(subset=["lat", "lon"]); ocm = ocm.dropna(subset=["lat", "lon"])
adm = gpd.read_file(f"{R}/.data/geo/ind_adm1.geojson")[["shapeName", "geometry"]]
def assign(df):
    g = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326")
    j = gpd.sjoin(g, adm, how="left", predicate="within")
    return pd.DataFrame(j.drop(columns=["geometry", "index_right"]))
osm, ocm = assign(osm), assign(ocm)
def hav(lat1, lon1, lat2, lon2):
    p = np.pi / 180; a = np.sin((lat2 - lat1) * p / 2) ** 2 + np.cos(lat1 * p) * np.cos(lat2 * p) * np.sin((lon2 - lon1) * p / 2) ** 2
    return 2 * 6371000 * np.arcsin(np.sqrt(a))
A = osm[["lat", "lon"]].to_numpy(); B = ocm[["lat", "lon"]].to_numpy()
D = hav(A[:, None, 0], A[:, None, 1], B[None, :, 0], B[None, :, 1])  # 600 x 1872 metres
nnA = D.argmin(1); nnB = D.argmin(0)
results = {}
for radius in (50, 100, 150, 250, 500):
    mutual = [(i, j) for i, j in enumerate(nnA) if nnB[j] == i and D[i, j] <= radius]
    results[radius] = mutual
RADIUS = 150  # baseline choice; to be tuned against a hand-labelled pair set (pairwise F1)
pairs = results[RADIUS]
pm = pd.DataFrame([{"osm_id": osm.iloc[i].source_id, "ocm_id": ocm.iloc[j].source_id, "dist_m": round(float(D[i, j]), 1),
                    "osm_name": osm.iloc[i]["name"], "ocm_name": ocm.iloc[j]["name"], "state": osm.iloc[i].shapeName,
                    "name_sim": fuzz.token_set_ratio(str(osm.iloc[i]["name"]), str(ocm.iloc[j]["name"]))} for i, j in pairs])
pm.to_csv(f"{OUT}/osm_ocm_matches_r150.csv", index=False)
osm["matched"] = False; osm.iloc[[i for i, _ in pairs], osm.columns.get_loc("matched")] = True
pcs = pd.read_csv(f"{R}/components/charger_ingest/data/official_pcs_statewise.csv"); pcs = pcs[pcs.source == "pib2151390"]
norm = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().replace("&", "and"))
alias = {"up": "uttarpradesh", "utofdandnhanddandd": "dadraandnagarhavelianddamananddiu", "andamanandnicobar": "andamanandnicobarislands"}
pcs["key"] = pcs.state.map(lambda s: alias.get(norm(s), norm(s)))
rows = []
for st in sorted(set(adm.shapeName)):
    k = norm(st); n1 = int((osm.shapeName == st).sum()); n2 = int((ocm.shapeName == st).sum()); m = int(((osm.shapeName == st) & osm.matched).sum())
    chap = (n1 + 1) * (n2 + 1) / (m + 1) - 1
    var = (n1 + 1) * (n2 + 1) * (n1 - m) * (n2 - m) / ((m + 1) ** 2 * (m + 2))
    off = pcs.loc[pcs.key == k, "pcs_total"]
    rows.append({"state": st, "n_osm": n1, "n_ocm": n2, "matched": m, "union": n1 + n2 - m, "chapman": round(chap, 1),
                 "chapman_se": round(float(np.sqrt(var)), 1), "official_pcs": int(off.iloc[0]) if len(off) else None})
st = pd.DataFrame(rows)
st["union_rel_err"] = ((st.union - st.official_pcs) / st.official_pcs).round(3)
st["chapman_rel_err"] = ((st.chapman - st.official_pcs) / st.official_pcs).round(3)
st["coverage_union_vs_official"] = (st.union / st.official_pcs).round(3)
st.to_csv(f"{OUT}/census_v0_by_state.csv", index=False)
ok = st[(st.matched >= 3) & st.official_pcs.notna()]
summary = {"osm_sites": int(len(osm)), "ocm_sites": int(len(ocm)), "osm_unassigned_state": int(osm.shapeName.isna().sum()),
           "ocm_unassigned_state": int(ocm.shapeName.isna().sum()),
           "mutual_nn_matches_by_radius_m": {r: len(v) for r, v in results.items()}, "radius_used_m": RADIUS,
           "matches_name_sim_ge_60_pct": round(100 * float((pm.name_sim >= 60).mean()), 1) if len(pm) else None,
           "national_union": int(st.union.sum()), "national_official": int(st.official_pcs.sum()),
           "national_union_coverage_pct": round(100 * st.union.sum() / st.official_pcs.sum(), 2),
           "national_chapman_on_totals": round((len(osm) + 1) * (len(ocm) + 1) / (len(pairs) + 1) - 1, 1),
           "states_evaluated_m_ge_3": int(len(ok)),
           "median_abs_rel_err_union": float(ok.union_rel_err.abs().median()) if len(ok) else None,
           "median_abs_rel_err_chapman": float(ok.chapman_rel_err.abs().median()) if len(ok) else None,
           "ocm_state_text_disagrees_with_polygon": int(sum(1 for a, b in zip(ocm.state_text.fillna(""), ocm.shapeName.fillna(""))
                                                          if a and b and fuzz.partial_ratio(norm(a), norm(b)) < 80))}
json.dump(summary, open(f"{OUT}/census_v0_summary.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
print(ok[["state", "n_osm", "n_ocm", "matched", "union", "chapman", "chapman_se", "official_pcs", "union_rel_err", "chapman_rel_err"]].to_string(index=False))
