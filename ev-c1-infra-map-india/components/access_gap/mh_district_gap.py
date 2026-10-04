"""C10 access_gap — Maharashtra district gap table (representative geography), all inputs real and committed.

Supply: the official Maharashtra total (4,155 public charging stations, PIB 2151390, as of 1 Aug 2025) is allocated
to districts with the small-area model in small_area.py (weights BEV^b·(open+1)^c, b and c fitted across the other 35
states; 90% predictive interval). Chosen because the three-source capture–recapture estimate failed the state-level
validation (eval/results/c5_mse_summary.json) and the model beat open-share, BEV-share and 50:50-blend allocations on
Chhattisgarh's official district counts (eval/results/small_area_summary.json).
Demand: VAHAN BEV registrations by district (eval/results/mh_district_demand.csv).
Benchmarks: Maharashtra average density; Karnataka density (best large state, BEV per station, state_gap_baseline.csv).
Boundaries: geoBoundaries IND ADM2 2021 (Pathways Data / LGD, ODbL; 36 districts incl. Palghar; Mumbai City +
Mumbai Suburban merged to match the RTO crosswalk).
Usage: .venv/bin/python -W ignore components/access_gap/mh_district_gap.py
"""
import json, os, re
import geopandas as gpd, numpy as np, pandas as pd
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")); OUT = f"{R}/eval/results"
ADM2_ALIAS = {"Ahmadnagar": "Ahilyanagar", "Aurangabad": "Chhatrapati Sambhajinagar", "Bid": "Beed", "Osmanabad": "Dharashiv",
              "Raigarh": "Raigad", "Gondiya": "Gondia", "Buldana": "Buldhana", "Mumbai Suburban": "Mumbai"}
adm1 = gpd.read_file(f"{R}/.data/geo/ind_adm1.geojson"); mh_poly = adm1[adm1.shapeName.str.startswith("Mah")].geometry.iloc[0]
adm2 = gpd.read_file(f"{R}/.data/geo/ind_adm2.geojson")
mh = adm2[adm2.representative_point().within(mh_poly)].copy()
mh["district"] = mh.shapeName.replace(ADM2_ALIAS)
mh = mh.dissolve(by="district", as_index=False)[["district", "geometry"]]
sites = pd.read_csv(f"{OUT}/c5_linked_records.csv")
sites = sites[sites.state_key == "maharashtra"].groupby("site").agg(lat=("lat", "mean"), lon=("lon", "mean"),
          srcs=("src", lambda s: ",".join(sorted(set(s))))).reset_index()
g = gpd.GeoDataFrame(sites, geometry=gpd.points_from_xy(sites.lon, sites.lat), crs="EPSG:4326")
j = gpd.sjoin(g, mh[["district", "geometry"]], how="left", predicate="within")
obs = j.groupby("district").size().rename("open_sites")
dem = pd.read_csv(f"{OUT}/mh_district_demand.csv")
gap = pd.read_csv(f"{OUT}/state_gap_baseline.csv"); gm = gap.dropna(subset=["pcs_total"])
OFFICIAL = int(gm.loc[gm.vahan_state.str.upper() == "MAHARASHTRA", "pcs_total"].iloc[0])
KA = float(gm.loc[gm.vahan_state.str.upper() == "KARNATAKA", "bev_per_pcs"].iloc[0])
d = mh[["district"]].merge(dem, on="district", how="left").merge(obs, on="district", how="left").fillna({"open_sites": 0})
missing = d[d.bev_total.isna()].district.tolist()
import sys
sys.path.insert(0, os.path.dirname(__file__))
import small_area as SA  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402
Y, BEVS, OPENS = SA.official("pib2151390"), SA.bev_cum_at(2025, 7), SA.open_by_state()
dd = d.set_index("district")
# Primary: BEV-only small-area allocation (the variant that passed the point-in-time Chhattisgarh check)
est, lo, hi, coef = SA.small_area(float(OFFICIAL), dd.bev_total, 0 * dd.open_sites, Y, BEVS, 0 * OPENS, exclude="maharashtra")
# Sensitivity: with the open-data term (current covariates; not testable point-in-time)
est2, lo2, hi2, coef2 = SA.small_area(float(OFFICIAL), dd.bev_total, dd.open_sites, Y, BEVS, OPENS, exclude="maharashtra")
d["est_stations"] = d.district.map(est); d["est_lo"] = d.district.map(lo); d["est_hi"] = d.district.map(hi)
d["est_stations_open_model"] = d.district.map(est2)
d["bev_per_station"] = d.bev_total / d.est_stations
d["bev_per_station_range"] = [f"{b / h:.0f}–{b / l:.0f}" if l > 0 else f"≥{b / h:.0f}" for b, l, h in zip(d.bev_total, d.est_lo, d.est_hi)]
d["open_coverage"] = d.open_sites / d.est_stations
d["open_per_10k_bev"] = 1e4 * d.open_sites / d.bev_total
rank_sens = float(spearmanr(d.bev_total / d.est_stations, d.bev_total / d.est_stations_open_model)[0])
state_avg = d.bev_total.sum() / OFFICIAL
d["need_at_karnataka_density"] = (d.bev_total / KA).round(0)
d["shortfall_vs_karnataka"] = (d.need_at_karnataka_density - d.est_stations).round(0)
d["growth_2025_share_pct"] = d.bev_2025_share_of_stock_pct
hi_pressure = d.bev_total >= d.bev_total.quantile(2 / 3)
state_open_density = 1e4 * d.open_sites.sum() / d.bev_total.sum()
thin = d.open_per_10k_bev < 0.5 * state_open_density  # less than half the state's visible density
d["verify_first"] = hi_pressure & thin
def drivers(r):
    out = [f"registration pressure: {r.bev_total:,.0f} BEV ({r.growth_2025_share_pct:.0f}% registered in 2025)"]
    if r.open_sites == 0: out.append("data-thin: no site in any open source")
    else: out.append(f"{r.open_sites:.0f} visible sites ({r.open_per_10k_bev:.1f} per 10,000 BEV)")
    if r.bev_3W / max(r.bev_total, 1) > 0.15: out.append(f"3W-heavy ({100 * r.bev_3W / r.bev_total:.0f}%): depot/swap needs")
    if r.bev_4W / max(r.bev_total, 1) > 0.20: out.append(f"car-heavy ({100 * r.bev_4W / r.bev_total:.0f}% 4W): DC fast-charging needs")
    if r.verify_first: out.append("VERIFY FIRST: high pressure, thin visible supply")
    return "; ".join(out)
d["drivers"] = d.apply(drivers, axis=1)
d = d.sort_values("bev_total", ascending=False)  # rank by observed registration pressure, not model-imputed supply
cor = pd.read_csv(f"{OUT}/mh_corridor_norm.csv").rename(columns={"norm_stations": "corridor_norm_stations", "coverage_pct_lower_bound": "corridor_cov_pct"})
d = d.merge(cor[["district", "corridor_norm_stations", "corridor_cov_pct"]], on="district", how="left")
d.to_csv(f"{OUT}/mh_district_gap.csv", index=False)
mh.merge(d[["district", "bev_total", "bev_2W", "bev_3W", "bev_4W", "bev_2025", "open_sites", "open_per_10k_bev", "est_stations", "est_lo", "est_hi",
            "est_stations_open_model", "open_coverage", "bev_per_station", "bev_per_station_range", "need_at_karnataka_density",
            "shortfall_vs_karnataka", "verify_first", "corridor_norm_stations", "corridor_cov_pct", "drivers"]],
         on="district").to_file(f"{R}/.data/geo/mh_district_gap.geojson", driver="GeoJSON")
state_need = d.bev_total.sum() / KA
summ = {"districts": int(len(d)), "districts_without_bev_mapping": missing, "official_mh_stations_aug2025": OFFICIAL,
        "small_area_coef_excl_mh": [round(float(x), 3) for x in coef], "small_area_coef_open_model": [round(float(x), 3) for x in coef2],
        "ranking_spearman_bev_only_vs_open_model": round(rank_sens, 3),
        "verify_first_districts": d[d.verify_first].district.tolist(), "state_open_per_10k_bev": round(state_open_density, 2),
        "mh_statewide_net_vs_karnataka": round(state_need - OFFICIAL),
        "open_sites_in_mh": int(d.open_sites.sum()), "open_sites_unassigned": int(j.district.isna().sum()),
        "districts_with_zero_open_sites": int((d.open_sites == 0).sum()), "mh_bev_per_station_avg": round(state_avg, 1),
        "karnataka_bev_per_station": KA, "mh_need_at_karnataka_density": int(d.need_at_karnataka_density.sum()),
        "mh_shortfall_vs_karnataka": int(d.shortfall_vs_karnataka.clip(lower=0).sum()),
        "top5_registration_pressure": d.head(5)[["district", "bev_total", "open_sites"]].values.tolist(),
        "nagpur": d[d.district == "Nagpur"][["bev_total", "open_sites", "est_stations", "est_lo", "est_hi"]].round(1).values.tolist()[0]}
json.dump(summ, open(f"{OUT}/mh_district_gap_summary.json", "w"), indent=1)
print(json.dumps(summ, indent=1))
print(d[["district", "bev_total", "open_sites", "open_per_10k_bev", "est_stations", "est_lo", "est_hi", "verify_first", "corridor_norm_stations"]].head(15).round(1).to_string(index=False))
