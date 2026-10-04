"""Maharashtra district EV demand from VAHAN RTO tables (walking skeleton, representative geography).

Crosswalk: components/admin_geo/data/rto_district_MH.csv (lead's manual town->district mapping; verify against the
Maharashtra Transport Department RTO jurisdiction list). Reproduce:
  .venv/bin/python components/vahan_ingest/fetch_vahan.py --rto-state MH && .venv/bin/python -W ignore eval/baseline_state_gap.py
  .venv/bin/python -W ignore eval/mh_district_demand.py
Benchmark requirement = stations needed for the district to match a reference density (BEV registrations per official
public charging station): national median of states (from state_gap_baseline.csv) and Karnataka (best large state).
This is a benchmark-equivalence figure, NOT a demand model (C8/C11 will replace it).
"""
import json, os
import pandas as pd
R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")); OUT = f"{R}/eval/results"
rto = pd.read_csv(f"{OUT}/mh_rto_bev.csv"); xw = pd.read_csv(f"{R}/components/admin_geo/data/rto_district_MH.csv")
rto = rto.merge(xw[["rto_code", "district", "method"]], on="rto_code", how="left")
a, y = rto[rto.year == "A"], rto[rto.year == "2025"]
seg = ["2W", "3W", "4W", "BUS", "GOODS", "OTHER"]
d = a.groupby("district", dropna=False)[["bev_total"] + [f"bev_{s}" for s in seg]].sum()
d = d.join(y.groupby("district", dropna=False)["bev_total"].sum().rename("bev_2025"))
d = d.join(a.groupby("district", dropna=False)["rto_code"].count().rename("n_rtos")).reset_index()
gap = pd.read_csv(f"{OUT}/state_gap_baseline.csv"); m = gap.dropna(subset=["pcs_total"])
nat_median = float(m.bev_per_pcs.median()); ka = float(m.loc[m.vahan_state.str.upper() == "KARNATAKA", "bev_per_pcs"].iloc[0])
d["stations_at_national_median_density"] = (d.bev_total / nat_median).round(0)
d["stations_at_karnataka_density"] = (d.bev_total / ka).round(0)
d["share_of_state_bev_pct"] = (100 * d.bev_total / d.bev_total.sum()).round(2)
d["bev_2025_share_of_stock_pct"] = (100 * d.bev_2025 / d.bev_total).round(1)
d = d.sort_values("bev_total", ascending=False)
d.to_csv(f"{OUT}/mh_district_demand.csv", index=False)
state_total = int(gap.loc[gap.vahan_state.str.upper() == "MAHARASHTRA", "bev_cum"].iloc[0])
rto_sum = int(a.bev_total.sum())
mh_pcs = int(gap.loc[gap.vahan_state.str.upper() == "MAHARASHTRA", "pcs_total"].iloc[0])
s = {"mh_rtos_with_data": int(a.rto_code.nunique()), "mh_rtos_mapped_to_district": int(a.district.notna().sum()),
     "c1_reconciliation_rel_err": round(abs(rto_sum - state_total) / state_total, 5), "sum_rto_bev": rto_sum, "state_table_bev": state_total,
     "unassigned_bev (TC office etc.)": int(a[a.district.isna()].bev_total.sum()), "districts": int(d.district.notna().sum()),
     "national_median_bev_per_station": nat_median, "karnataka_bev_per_station": ka, "mh_official_stations": mh_pcs,
     "mh_stations_at_national_median_density": round(state_total / nat_median), "mh_stations_at_karnataka_density": round(state_total / ka),
     "mh_segment_mix_pct": {s_: round(100 * float(a[f"bev_{s_}"].sum()) / rto_sum, 1) for s_ in seg}}
json.dump(s, open(f"{OUT}/mh_district_summary.json", "w"), indent=1)
print(json.dumps(s, indent=1))
print(d[["district", "n_rtos", "bev_total", "bev_2W", "bev_3W", "bev_4W", "bev_2025", "stations_at_national_median_density", "stations_at_karnataka_density"]].head(12).to_string(index=False))
