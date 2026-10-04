"""Collect every headline number from the committed result files into eval/results/latest.json.

Each entry: {"value": <raw>, "text": <display string used in documents>, "source": <result file>}.
Documents embed numbers as <!--n:KEY-->text<!--/n--> and eval/render_docs.py rewrites them from this file;
eval/check_docs.py fails on drift. Usage (from ev-c1-infra-map-india/): python3 eval/make_latest.py
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "eval" / "results"
L: dict[str, dict] = {}


def put(key, value, text=None, source=""):
    if text is None:
        text = f"{value:,}" if isinstance(value, int) else str(value)
    L[key] = {"value": value, "text": text, "source": source}


def j(name):
    return json.loads((RES / name).read_text())


def f1(x):
    return f"{x:,.1f}"


def f0(x):
    return f"{x:,.0f}"


def main():
    b = j("baseline_summary.json"); src = "eval/results/baseline_summary.json"
    put("nat_bev_cum", b["india_bev_registrations_till_today"], source=src)
    put("nat_bev_2025", b["india_bev_registrations_cy2025"], source=src)
    put("nat_bev_share_2025", b["india_bev_share_cy2025_pct"], f"{b['india_bev_share_cy2025_pct']:.2f}%", src)
    put("official_pcs_aug2025", b["official_pcs_sum_pib2151390"], source=src)
    put("nat_bev_per_pcs", b["national_bev_per_official_pcs"], f0(b["national_bev_per_official_pcs"]), src)
    put("nat_bev_jul2025", b["india_bev_registrations_to_jul2025"], source=src)
    put("nat_bev_jul2025_per_pcs", b["national_bev_jul2025_per_official_pcs"], f0(b["national_bev_jul2025_per_official_pcs"]), src)
    put("bev_since_2020_pct", b["bev_share_registered_since_2020_pct"], f"{b['bev_share_registered_since_2020_pct']:.1f}%", src)
    put("bev_since_2022_pct", b["bev_share_registered_since_2022_pct"], f"{b['bev_share_registered_since_2022_pct']:.1f}%", src)
    put("bev_before_2020", b["bev_registered_before_2020"], source=src)
    put("osm_n", b["osm_charging_features_india"], source=src)
    put("osm_pct_official", b["osm_coverage_vs_official_pct"], f"{b['osm_coverage_vs_official_pct']:.2f}%", src)
    put("osm_operator_pct", b["osm_with_operator_pct"], f"{b['osm_with_operator_pct']:.1f}%", src)
    put("osm_socket_pct", b["osm_with_any_socket_tag_pct"], f"{b['osm_with_any_socket_tag_pct']:.1f}%", src)
    put("mh_bev_cum", b["mh_state_bev_till_today"], source=src)
    put("mh_pcs", b["mh_pcs_pib2151390"], source=src)
    put("mh_bev_per_pcs", b["mh_bev_per_pcs"], f0(b["mh_bev_per_pcs"]), src)
    seg = b["mh_bev_by_segment_till_today"]; tot = sum(seg.values())
    for k in ("2W", "3W", "4W"):
        put(f"mh_share_{k}", round(100 * seg[k] / tot, 1), f"{100 * seg[k] / tot:.1f}%", src)
    rows = list(csv.DictReader((RES / "state_gap_baseline.csv").open()))
    for r in rows:
        k = r["vahan_state"].lower().replace(" ", "_").replace("&", "and")
        if r["bev_per_pcs"]:
            put(f"state_bev_per_pcs_{k}", float(r["bev_per_pcs"]), f0(float(r["bev_per_pcs"])), "eval/results/state_gap_baseline.csv")
            put(f"state_bev_cum_{k}", int(r["bev_cum"]), source="eval/results/state_gap_baseline.csv")
            put(f"state_pcs_{k}", int(float(r["pcs_total"])), source="eval/results/state_gap_baseline.csv")
            put(f"state_bev_jul2025_per_pcs_{k}", float(r["bev_jul2025_per_pcs"]), f0(float(r["bev_jul2025_per_pcs"])), "eval/results/state_gap_baseline.csv")
    m = j("mh_district_summary.json"); src = "eval/results/mh_district_summary.json"
    put("mh_rtos", m["mh_rtos_with_data"], source=src)
    put("mh_reconciliation_err", m["c1_reconciliation_rel_err"], f"{m['c1_reconciliation_rel_err']:.1f}", src)
    c5 = j("c5_mse_summary.json"); src = "eval/results/c5_mse_summary.json"
    rec = c5["records"]
    put("ocm_n_in_india", rec["ocm"], source=src); put("ovt_n_in_india", rec["ovt"], source=src); put("osm_n_in_india", rec["osm"], source=src)
    put("linked_records", sum(rec.values()), source=src)
    put("linked_sites", c5["sites_linked"], source=src)
    put("sites_in_all3", c5["national_cells"]["111"], source=src)
    put("open_coverage_pct", round(100 * c5["sites_linked"] / c5["official_national_aug2025"], 1),
        f"{100 * c5['sites_linked'] / c5['official_national_aug2025']:.1f}%", src)
    n = c5["national_mse"]
    put("mse_nat", n["N_hat"], f0(n["N_hat"]), src); put("mse_nat_lo", n["ci90_lo"], f0(n["ci90_lo"]), src); put("mse_nat_hi", n["ci90_hi"], f0(n["ci90_hi"]), src)
    put("mse_states", c5["states_evaluated"], source=src)
    put("mse_median_ratio", c5["median_mse_over_official"], f"{c5['median_mse_over_official']:.2f}", src)
    put("union_median_ratio", c5["median_union_over_official"], f"{c5['median_union_over_official']:.3f}", src)
    put("mse_median_abs_log", c5["median_abs_log_ratio_mse"], f"{c5['median_abs_log_ratio_mse']:.2f}", src)
    put("mse_ci_coverage", c5["ci90_coverage_of_official"], f"{100 * c5['ci90_coverage_of_official']:.0f}%", src)
    put("mse_passes", c5["passes_state_check"], "fails" if not c5["passes_state_check"] else "passes", src)
    sens = j("c5_mse_sensitivity.json"); src = "eval/results/c5_mse_sensitivity.json"
    nats = [r["national"] for r in sens]
    put("mse_nat_min_model", min(nats), source=src); put("mse_nat_max_model", max(nats), source=src)
    put("mse_sens_runs", len(sens), source=src); put("mse_sens_any_pass", any(r["passes"] for r in sens), "none" if not any(r["passes"] for r in sens) else "some", src)
    put("mse_sens_cov_max", max(r["ci_coverage"] for r in sens), f"{100 * max(r['ci_coverage'] for r in sens):.0f}%", src)
    sa = j("small_area_summary.json"); src = "eval/results/small_area_summary.json"
    cg = sa["chhattisgarh_validation"]
    put("cg_districts", cg["districts"], source=src); put("cg_official_total", cg["official_total_evaluated"], source=src)
    for k, v in cg["methods"].items():
        put(f"cg_wape_{k}", v["wape"], f"{v['wape']:.2f}", src); put(f"cg_spearman_{k}", v["spearman"], f"{v['spearman']:.2f}", src)
    put("cg_ci_coverage", cg["small_area_ci90_coverage"], f"{100 * cg['small_area_ci90_coverage']:.0f}%", src)
    put("sa_loo", sa["state_model_aug2025"]["loo_median_abs_log_err"], f"{sa['state_model_aug2025']['loo_median_abs_log_err']:.2f}", src)
    g = j("mh_district_gap_summary.json"); src = "eval/results/mh_district_gap_summary.json"
    put("mh_districts", g["districts"], source=src); put("mh_open_sites", g["open_sites_in_mh"], source=src)
    put("mh_zero_open_districts", g["districts_with_zero_open_sites"], source=src)
    put("mh_need_ka", g["mh_need_at_karnataka_density"], source=src); put("mh_shortfall_ka", g["mh_shortfall_vs_karnataka"], source=src)
    put("ka_bev_per_pcs", g["karnataka_bev_per_station"], f"{g['karnataka_bev_per_station']:.1f}", src)
    put("sa_b_mh", g["small_area_coef_excl_mh"][1], f"{g['small_area_coef_excl_mh'][1]:.2f}", src)
    put("sa_c_mh", g["small_area_coef_excl_mh"][2], f"{g['small_area_coef_excl_mh'][2]:.2f}", src)
    top = g["top5_bev_per_station"]
    for i, (dname, v, rng) in enumerate(top[:3], 1):
        put(f"mh_top{i}_name", dname, dname, src); put(f"mh_top{i}_bev_per_stn", v, f0(v), src); put(f"mh_top{i}_range", rng, rng, src)
    gd = list(csv.DictReader((RES / "mh_district_gap.csv").open()))
    ng = next(r for r in gd if r["district"] == "Nagpur")
    put("nagpur_bev", int(float(ng["bev_total"])), source="eval/results/mh_district_gap.csv")
    put("nagpur_open", int(float(ng["open_sites"])), source="eval/results/mh_district_gap.csv")
    put("nagpur_est", float(ng["est_stations"]), f0(float(ng["est_stations"])), "eval/results/mh_district_gap.csv")
    put("nagpur_lo", float(ng["est_lo"]), f0(float(ng["est_lo"])), "eval/results/mh_district_gap.csv")
    put("nagpur_hi", float(ng["est_hi"]), f0(float(ng["est_hi"])), "eval/results/mh_district_gap.csv")
    put("nagpur_3w_pct", round(100 * float(ng["bev_3W"]) / float(ng["bev_total"])), f"{100 * float(ng['bev_3W']) / float(ng['bev_total']):.0f}%", "eval/results/mh_district_gap.csv")
    c9 = j("c9_summary.json"); src = "eval/results/c9_summary.json"
    fc = c9["forecast_12m_dev_holdout"]
    for k, short in (("naive12", "naive"), ("pooled_growth_nat_0.5", "pooled"), ("share_logit_k2_0.5", "logit"), ("ensemble_pg+sl", "ensemble")):
        put(f"c9_dev_{short}", fc[k]["dev_wape"], f"{fc[k]['dev_wape']:.3f}", src); put(f"c9_hold_{short}", fc[k]["holdout_wape"], f"{fc[k]['holdout_wape']:.3f}", src)
    put("c9_hold_gain_vs_naive", round(100 * (1 - fc["share_logit_k2_0.5"]["holdout_wape"] / fc["naive12"]["holdout_wape"])),
        f"{100 * (1 - fc['share_logit_k2_0.5']['holdout_wape'] / fc['naive12']['holdout_wape']):.0f}%", src)
    bt = c9["nowcast_backtest_by_method"]["yoy"]
    put("nowcast_wape", bt["mean_wape"], f"{100 * bt['mean_wape']:.1f}%", src)
    put("nowcast_mean_nat_err", bt["mean_abs_nat_err"], f"{100 * bt['mean_abs_nat_err']:.1f}%", src)
    put("nowcast_max_nat_err", bt["max_abs_nat_err"], f"{100 * bt['max_abs_nat_err']:.1f}%", src)
    nc = c9["nowcast_2026_national"]
    put("nowcast_2026", nc["yoy"], source=src); put("nowcast_2026_m", round(nc["yoy"] / 1e6, 2), f"{nc['yoy'] / 1e6:.2f} million", src)
    put("nowcast_2026_lo_m", round(min(nc.values()) / 1e6, 2), f"{min(nc.values()) / 1e6:.2f}", src)
    put("nowcast_2026_hi_m", round(max(nc.values()) / 1e6, 2), f"{max(nc.values()) / 1e6:.2f}", src)
    put("ytd_2026", c9["ytd_jan_sep_2026_national"], source=src)
    put("nowcast_growth", round(100 * (nc["yoy"] / c9["actual_2025_national"] - 1)), f"{100 * (nc['yoy'] / c9['actual_2025_national'] - 1):.0f}%", src)
    (RES / "latest.json").write_text(json.dumps(L, indent=1, ensure_ascii=False))
    print(f"latest.json: {len(L)} keys")


if __name__ == "__main__":
    main()
