"""C11 prototype — norm-based corridor requirement for Maharashtra (MoP Guidelines 2024, clause 11(1)(b)):
"Charging Stations will be located every 20 km on both sides of highways, expressways, and major roads."

Roads: OSM highway=motorway|trunk in Maharashtra (fetch_highways.py; ODbL). Sides: a one-way carriageway (oneway=yes, or
motorway) is one side; a two-way road counts as two sides. Requirement = side-km / 20.
Existing (lower bound): linked open-data sites (OSM ∪ OCM ∪ Overture) within 500 m of a corridor. Coverage: share of
side-km whose 1-km sample point has such a site within 10 km (straight line) — the 20 km spacing norm means no point
should be more than 10 km from a station. Open data sees ~11% of official stations, so coverage here is a LOWER bound
and the gap an UPPER bound.
Usage: .venv/bin/python -W ignore components/requirement_siting/corridor_norm.py
"""
import json, os
import geopandas as gpd, numpy as np, pandas as pd
from shapely.geometry import LineString
from shapely import STRtree

R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")); OUT = f"{R}/eval/results"
CRS = "EPSG:7755"  # WGS 84 / India NSF LCC (metres)
SPACING_KM, ACCESS_M, COVER_KM = 20.0, 500.0, 10.0
d = json.load(open(f"{R}/.data/roads/mh_motorway_trunk.json"))
rows = []
for e in d["elements"]:
    g = e.get("geometry") or []
    if len(g) < 2:
        continue
    t = e.get("tags", {})
    oneway = t.get("oneway") in ("yes", "1", "true") or (t.get("highway") == "motorway" and t.get("oneway") != "no")
    rows.append({"osm_id": e["id"], "highway": t.get("highway"), "ref": t.get("ref", ""), "oneway": oneway,
                 "geometry": LineString([(p["lon"], p["lat"]) for p in g])})
roads = gpd.GeoDataFrame(rows, crs="EPSG:4326").to_crs(CRS)
roads["km"] = roads.length / 1000
roads["sides"] = np.where(roads.oneway, 1, 2)
roads["side_km"] = roads.km * roads.sides
roads["is_nh_ref"] = roads.ref.str.contains(r"\bNH|\bNE\b|\bNE[- ]?\d", case=False, regex=True)
dist = gpd.read_file(f"{R}/.data/geo/mh_district_gap.geojson")[["district", "geometry"]].to_crs(CRS)
rec = pd.read_csv(f"{OUT}/c5_linked_records.csv"); rec = rec[rec.state_key == "maharashtra"]
sites = rec.groupby("site").agg(lat=("lat", "mean"), lon=("lon", "mean")).reset_index()
sites = gpd.GeoDataFrame(sites, geometry=gpd.points_from_xy(sites.lon, sites.lat), crs="EPSG:4326").to_crs(CRS)
tree_roads = STRtree(roads.geometry.values)
near = tree_roads.query(sites.geometry.values, predicate="dwithin", distance=ACCESS_M)
hw_idx = np.unique(near[0]); hw_sites = sites.iloc[hw_idx]
tree_hw = STRtree(hw_sites.geometry.values) if len(hw_sites) else None
pts = []
for r in roads.itertuples():
    n = max(1, int(np.ceil(r.km)))
    for i in range(n):
        seg_km = min(1.0, r.km - i) if r.km - i > 0 else 0
        p = r.geometry.interpolate(min((i + 0.5) * 1000, r.geometry.length))
        pts.append((p, seg_km * r.sides))
P = gpd.GeoDataFrame({"w_side_km": [w for _, w in pts]}, geometry=[p for p, _ in pts], crs=CRS)
if tree_hw is not None:
    hit = tree_hw.query(P.geometry.values, predicate="dwithin", distance=COVER_KM * 1000)
    covered = np.zeros(len(P), bool); covered[np.unique(hit[0])] = True
else:
    covered = np.zeros(len(P), bool)
P["covered"] = covered
P = gpd.sjoin(P, dist, how="left", predicate="within").drop(columns="index_right")
by = P.groupby("district").agg(side_km=("w_side_km", "sum"), covered_side_km=("w_side_km", lambda s: float(s[P.loc[s.index, "covered"]].sum())))
by["norm_stations"] = (by.side_km / SPACING_KM).round(1)
hw_d = gpd.sjoin(hw_sites, dist, how="left", predicate="within").groupby("district").size().rename("hw_open_sites")
by = by.join(hw_d).fillna({"hw_open_sites": 0})
by["coverage_pct_lower_bound"] = (100 * by.covered_side_km / by.side_km).round(1)
by["gap_stations_upper_bound"] = ((by.side_km - by.covered_side_km) / SPACING_KM).round(1)
by = by.sort_values("norm_stations", ascending=False)
by.to_csv(f"{OUT}/mh_corridor_norm.csv", index_label="district")
tot_side = float(P.w_side_km.sum()); cov_side = float(P.w_side_km[P.covered].sum())
summ = {"osm_base": d.get("osm3s", {}).get("timestamp_osm_base"), "ways": int(len(roads)),
        "road_km_motorway_trunk": round(float(roads.km.sum())), "side_km": round(tot_side),
        "share_km_with_NH_ref_pct": round(100 * float(roads.km[roads.is_nh_ref].sum() / roads.km.sum()), 1),
        "oneway_km_share_pct": round(100 * float(roads.km[roads.oneway].sum() / roads.km.sum()), 1),
        "norm_stations_required": round(tot_side / SPACING_KM), "hw_accessible_open_sites": int(len(hw_sites)),
        "coverage_pct_lower_bound": round(100 * cov_side / tot_side, 1),
        "gap_stations_upper_bound": round((tot_side - cov_side) / SPACING_KM),
        "params": {"spacing_km": SPACING_KM, "access_m": ACCESS_M, "cover_km": COVER_KM, "crs": CRS},
        "top_districts_by_norm": by.head(5)[["norm_stations", "coverage_pct_lower_bound"]].reset_index().values.tolist()}
json.dump(summ, open(f"{OUT}/mh_corridor_summary.json", "w"), indent=1)
P.to_crs("EPSG:4326").assign(lon=lambda g: g.geometry.x.round(5), lat=lambda g: g.geometry.y.round(5))[["lon", "lat", "covered", "district"]].to_csv(
    f"{R}/.data/roads/mh_corridor_points.csv", index=False)
print(json.dumps(summ, indent=1))
