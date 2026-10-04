"""Baseline gap analysis on REAL data (walking skeleton v0).

Joins (1) VAHAN cumulative registrations till today by state x fuel (BEV = ELECTRIC(BOV) + PURE EV),
(2) VAHAN CY2025 registrations, (3) official state-wise public charging stations (PIB 2151390, as on 01 Aug 2025),
(4) OSM amenity=charging_station features for India (Overpass), and (5) VAHAN Maharashtra RTO-level x vehicle class.
Reproduce (from ev-c1-infra-map-india/):
  .venv/bin/python components/vahan_ingest/fetch_vahan.py --national --rto-state MH --states
  .venv/bin/python components/charger_ingest/fetch_osm.py
  python3 components/charger_ingest/fetch_sources.py components/charger_ingest/source_urls.txt && python3 components/charger_ingest/official_pcs.py
  .venv/bin/python -W ignore eval/baseline_state_gap.py
"""
import json, os, re
import pandas as pd
from rapidfuzz import process, fuzz
R = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(R, ".data", "vahan", "raw")
OUT = os.path.join(R, "eval", "results"); os.makedirs(OUT, exist_ok=True)
BEV = ["ELECTRIC(BOV)", "PURE EV"]
def bev(df): return sum(df[c] for c in BEV if c in df)
norm = lambda s: re.sub(r"[^A-Z]", "", s.upper().replace("&", "AND"))
till = pd.read_csv(f"{RAW}/nat_state_fuel_A.csv"); y25 = pd.read_csv(f"{RAW}/nat_state_fuel_2025.csv")
st = pd.DataFrame({"vahan_state": till.row_label, "bev_cum": bev(till), "all_cum": till.TOTAL})
st = st.merge(pd.DataFrame({"vahan_state": y25.row_label, "bev_2025": bev(y25), "all_2025": y25.TOTAL}), on="vahan_state")
pcs = pd.read_csv(os.path.join(R, "components/charger_ingest/data/official_pcs_statewise.csv"))
pcs = pcs[pcs.source == "pib2151390"]
alias = {"UTTARPRADESH": "UP", "UTOFDNHANDDD": "UTOFDANDNHANDDANDD", "JAMMUANDKASHMIR": "JAMMUANDKASHMIR"}
choices = {norm(s): s for s in pcs.state}
def match(v):
    k = norm(v); k = alias.get(k, k)
    m = process.extractOne(k, list(choices), scorer=fuzz.ratio)
    return choices[m[0]] if m and m[1] >= 80 else None
st["pib_state"] = st.vahan_state.map(match)
st = st.merge(pcs[["state", "pcs_total"]], left_on="pib_state", right_on="state", how="left").drop(columns="state")
# Date-aligned variant: BEV registered up to Jul 2025 (end of the month before the official snapshot of 1 Aug 2025)
MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
later = pd.Series(0.0, index=st.vahan_state.values)
for y in (2025, 2026):
    mm = pd.read_csv(f"{RAW}/nat_state_month_bev_{y}.csv").set_index("row_label")
    for i, m in enumerate(MONTHS):
        if (y, i + 1) > (2025, 7) and m in mm.columns:
            later = later.add(mm[m].reindex(later.index).fillna(0), fill_value=0)
st["bev_cum_jul2025"] = (st.bev_cum.values - later.reindex(st.vahan_state.values).values).astype(int)
st["bev_jul2025_per_pcs"] = (st.bev_cum_jul2025 / st.pcs_total).round(1)
st["bev_per_pcs"] = (st.bev_cum / st.pcs_total).round(1)
st["bev2025_per_pcs"] = (st.bev_2025 / st.pcs_total).round(1)
st["bev_share_2025_pct"] = (100 * st.bev_2025 / st.all_2025).round(2)
st = st.sort_values("bev_per_pcs", ascending=False)
st.to_csv(f"{OUT}/state_gap_baseline.csv", index=False)
osm = json.load(open(os.path.join(R, ".data/chargers/osm_india_raw.json")))
osm_n = len(osm["elements"]); tags = [e.get("tags", {}) for e in osm["elements"]]
nat_pcs = int(pcs.pcs_total.sum()); matched = st.dropna(subset=["pcs_total"])
summary = {
  "vahan_states": int(len(st)), "states_matched_to_pib": int(st.pib_state.notna().sum()),
  "unmatched_vahan_states": st[st.pib_state.isna()].vahan_state.tolist(),
  "india_bev_registrations_till_today": int(st.bev_cum.sum()), "india_all_registrations_till_today": int(st.all_cum.sum()),
  "india_bev_registrations_cy2025": int(st.bev_2025.sum()), "india_bev_share_cy2025_pct": round(100 * st.bev_2025.sum() / st.all_2025.sum(), 2),
  "official_pcs_sum_pib2151390": nat_pcs, "national_bev_per_official_pcs": round(st.bev_cum.sum() / nat_pcs, 1),
  "median_state_bev_per_pcs": float(matched.bev_per_pcs.median()),
  "india_bev_registrations_to_jul2025": int(st.bev_cum_jul2025.sum()),
  "national_bev_jul2025_per_official_pcs": round(st.bev_cum_jul2025.sum() / nat_pcs, 1),
  "osm_charging_features_india": osm_n, "osm_base_timestamp": osm.get("osm3s", {}).get("timestamp_osm_base"),
  "osm_coverage_vs_official_pct": round(100 * osm_n / nat_pcs, 2),
  "osm_with_operator_pct": round(100 * sum(1 for t in tags if t.get("operator")) / osm_n, 1),
  "osm_with_any_socket_tag_pct": round(100 * sum(1 for t in tags if any(k.startswith("socket:") for k in t)) / osm_n, 1),
}
# Maharashtra RTO level
seg = lambda c: ("2W" if re.search(r"M-CYCLE|MOTOR CYCLE|MOPED|MOTORISED CYCLE", c) else "3W" if re.search(r"RICKSHAW|THREE WHEELER", c)
       else "4W" if re.search(r"MOTOR CAR|MOTOR CAB|LUXURY CAB|MAXI CAB|QUADRICYCLE", c) else "BUS" if re.search(r"BUS", c)
       else "GOODS" if re.search(r"GOODS|TRUCK|CARRIER", c) else "OTHER")
rl = pd.read_csv(f"{RAW}/rto_list_MH.csv") if os.path.getsize(f"{RAW}/rto_list_MH.csv") > 5 else pd.DataFrame(columns=["rto_code", "rto_label"]); rows = []
for _, r in rl.iterrows():
    for y in ("A", "2025"):
        p = f"{RAW}/rto_MH_{r.rto_code}_class_fuel_{y}.csv"
        if not os.path.exists(p) or os.path.getsize(p) < 5: continue
        d = pd.read_csv(p); d["bev"] = bev(d); d["seg"] = d.row_label.map(seg)
        g = d.groupby("seg").bev.sum()
        rows.append({"rto_code": r.rto_code, "rto_label": r.rto_label, "year": y, "bev_total": int(d.bev.sum()), "all_total": int(d.TOTAL.sum()),
                     **{f"bev_{k}": int(g.get(k, 0)) for k in ["2W", "3W", "4W", "BUS", "GOODS", "OTHER"]}})
mh = pd.DataFrame(rows); mh.to_csv(f"{OUT}/mh_rto_bev.csv", index=False)
a = mh[mh.year == "A"]
summary.update({"mh_rtos_listed": int(len(rl)), "mh_rtos_fetched_till_today": int(len(a)), "mh_bev_till_today_sum_rtos": int(a.bev_total.sum()),
  "mh_bev_by_segment_till_today": {k: int(a[f"bev_{k}"].sum()) for k in ["2W", "3W", "4W", "BUS", "GOODS", "OTHER"]},
  "mh_top5_rtos_bev": a.nlargest(5, "bev_total")[["rto_label", "bev_total"]].values.tolist()})
mhs = st[st.vahan_state.str.upper().str.startswith("MAHARASHTRA")]
if len(mhs): summary["mh_state_bev_till_today"] = int(mhs.bev_cum.iloc[0]); summary["mh_pcs_pib2151390"] = int(mhs.pcs_total.iloc[0]); summary["mh_bev_per_pcs"] = float(mhs.bev_per_pcs.iloc[0])
json.dump(summary, open(f"{OUT}/baseline_summary.json", "w"), indent=1)
print(json.dumps(summary, indent=1)[:3000])
print(st[["vahan_state", "bev_cum", "bev_2025", "pcs_total", "bev_per_pcs", "bev_share_2025_pct"]].head(12).to_string(index=False))
print(st[["vahan_state", "bev_cum", "pcs_total", "bev_per_pcs"]].dropna().tail(5).to_string(index=False))
