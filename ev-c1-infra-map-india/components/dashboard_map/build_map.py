"""Build the decision-support dashboard (C13 v1): dist/index.html (national) and dist/maharashtra.html (districts).

Every number shown comes from committed result files in eval/results/ (see each page's footer for sources and dates).
No third-party basemap: only our boundary layers are drawn (state outline: geoBoundaries ADM1 from DataMeet/ECI;
districts: geoBoundaries ADM2 2021 from Pathways Data/LGD) — consistent with India's official depiction, not SoI-certified.
Usage: .venv/bin/python -W ignore components/dashboard_map/build_map.py
"""
import json, os, re, unicodedata
import geopandas as gpd, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(os.path.join(HERE, "..", "..")); RES = f"{R}/eval/results"
norm = lambda s: re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().replace("&", "and"))  # noqa: E731
ALIAS = {"utofdnhanddd": "dadraandnagarhavelianddamananddiu", "andamanandnicobarisland": "andamanandnicobarislands",
         "andamanandnicobar": "andamanandnicobarislands", "utofdandnhanddandd": "dadraandnagarhavelianddamananddiu"}
key = lambda s: ALIAS.get(norm(s), norm(s))  # noqa: E731
J = lambda o: json.dumps(o, separators=(",", ":"))  # noqa: E731


def national():
    adm = gpd.read_file(f"{R}/.data/geo/ind_adm1.geojson")[["shapeName", "geometry"]]
    adm["geometry"] = adm.geometry.simplify(0.02, preserve_topology=True); adm["k"] = adm.shapeName.map(key)
    gap = pd.read_csv(f"{RES}/state_gap_baseline.csv"); gap["k"] = gap.vahan_state.map(key)
    mse = pd.read_csv(f"{RES}/c5_mse_by_state.csv").rename(columns={"state_key": "k"})
    now = pd.read_csv(f"{RES}/c9_nowcast_2026.csv"); now["k"] = now.state.map(key)
    st = adm.merge(gap[["k", "bev_cum", "bev_2025", "pcs_total", "bev_per_pcs", "bev_share_2025_pct", "bev_cum_jul2025", "bev_jul2025_per_pcs"]], on="k", how="left")
    st = st.merge(mse[["k", "n_osm", "n_ocm", "n_ovt", "n_obs", "N_hat", "ci90_lo", "ci90_hi"]], on="k", how="left")
    st = st.merge(now[["k", "yoy", "ytd_jan_sep_2026"]].rename(columns={"yoy": "nowcast_2026"}), on="k", how="left")
    for c in ("n_osm", "n_ocm", "n_ovt", "n_obs"):
        st[c] = st[c].fillna(0)  # states absent from every open source have 0 visible sites, not "no data"
    st["coverage_pct"] = (100 * st.n_obs / st.pcs_total).round(1)
    unmatched = st[st.bev_cum.isna()].shapeName.tolist()
    rec = pd.read_csv(f"{RES}/c5_linked_records.csv")
    sites = rec.groupby("site").agg(lat=("lat", "mean"), lon=("lon", "mean"), name=("name", "first"),
                                    srcs=("src", lambda s: ",".join(sorted(set(s))))).reset_index()
    feats = [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [round(r.lon, 5), round(r.lat, 5)]},
              "properties": {"n": len(r.srcs.split(",")), "s": r.srcs, "name": (r.name if isinstance(r.name, str) else "")[:60]}}
             for r in sites.itertuples()]
    return json.loads(st.drop(columns=["k"]).to_json()), {"type": "FeatureCollection", "features": feats}, unmatched


def maharashtra():
    g = gpd.read_file(f"{R}/.data/geo/mh_district_gap.geojson")
    g["geometry"] = g.geometry.simplify(0.005, preserve_topology=True)
    for c in ("est_stations", "est_lo", "est_hi", "bev_per_station", "open_coverage"):
        g[c] = g[c].astype(float).round(2)
    rec = pd.read_csv(f"{RES}/c5_linked_records.csv"); rec = rec[rec.state_key == "maharashtra"]
    sites = rec.groupby("site").agg(lat=("lat", "mean"), lon=("lon", "mean"), name=("name", "first"),
                                    srcs=("src", lambda s: ",".join(sorted(set(s))))).reset_index()
    feats = [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [round(r.lon, 5), round(r.lat, 5)]},
              "properties": {"n": len(r.srcs.split(",")), "s": r.srcs, "name": (r.name if isinstance(r.name, str) else "")[:60]}}
             for r in sites.itertuples()]
    summ = json.load(open(f"{RES}/mh_district_gap_summary.json"))
    return json.loads(g.to_json()), {"type": "FeatureCollection", "features": feats}, summ


def main():
    tpl = open(os.path.join(HERE, "template.html")).read()
    os.makedirs(os.path.join(HERE, "dist"), exist_ok=True)
    sts, sites, unmatched = national()
    mse = json.load(open(f"{RES}/c5_mse_summary.json")); c9 = json.load(open(f"{RES}/c9_summary.json"))
    html = (tpl.replace("__MODE__", "national").replace("__AREAS__", J(sts)).replace("__SITES__", J(sites))
               .replace("__META__", J({"mse": mse, "c9": {"nowcast_2026_national": c9["nowcast_2026_national"]["yoy"],
                                                           "actual_2025": c9["actual_2025_national"]}})))
    open(os.path.join(HERE, "dist", "index.html"), "w").write(html)
    mh, mh_sites, summ = maharashtra()
    html = (tpl.replace("__MODE__", "maharashtra").replace("__AREAS__", J(mh)).replace("__SITES__", J(mh_sites)).replace("__META__", J(summ)))
    open(os.path.join(HERE, "dist", "maharashtra.html"), "w").write(html)
    print(f"national: {len(sts['features'])} states (unmatched {unmatched}), {len(sites['features'])} sites; "
          f"maharashtra: {len(mh['features'])} districts, {len(mh_sites['features'])} sites; "
          f"sizes {os.path.getsize(os.path.join(HERE, 'dist', 'index.html')) / 1e6:.2f} / {os.path.getsize(os.path.join(HERE, 'dist', 'maharashtra.html')) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
