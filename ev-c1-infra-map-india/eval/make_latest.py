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
    put("mse_n_aic", n["N_aic_weighted"], f0(n["N_aic_weighted"]), src)
    put("mse_n_min_model", n["N_min_model"], f0(n["N_min_model"]), src); put("mse_n_max_model", n["N_max_model"], f0(n["N_max_model"]), src)
    put("mse_states_ge100", c5["states_ge100"], source=src); put("mse_states_in_ci", c5["states_in_ci"], source=src)
    put("mse_bias", c5["bias_median_log_ratio_mse"], f"{c5['bias_median_log_ratio_mse']:.2f}", src)
    put("osm_private_excluded", c5["osm_excluded_access_private_or_no"], source=src)
    put("edges_removed", c5["edges_removed_for_one_record_per_source"], source=src)
    sens = j("c5_mse_sensitivity.json"); src = "eval/results/c5_mse_sensitivity.json"
    nats = [r["national"] for r in sens]
    put("mse_nat_min_model", min(nats), source=src); put("mse_nat_max_model", max(nats), source=src)
    put("mse_sens_runs", len(sens), source=src); put("mse_sens_any_pass", any(r["passes"] for r in sens), "none" if not any(r["passes"] for r in sens) else "one", src)
    put("mse_sens_cov_max", max(r["ci_coverage"] for r in sens), f"{100 * max(r['ci_coverage'] for r in sens):.0f}%", src)
    put("mse_sens_n_pass", sum(r["passes"] for r in sens), source=src)
    ps = [r for r in sens if r["passes"]]
    put("mse_sens_pass_radius", ps[0]["radius_m"] if ps else 0, f"{ps[0]['radius_m']} m" if ps else "none", src)
    sa = j("small_area_summary.json"); src = "eval/results/small_area_summary.json"
    pit = sa["chhattisgarh_point_in_time"]; rr = pit["results"]
    put("cg_total", int(pit["total_allocated"]), source=src)
    put("cg_labelled", pit["accounting"]["labelled_2021_districts"], source=src)
    put("cg_unlabelled", ", ".join(pit["accounting"]["unlabelled_2021_districts"]), ", ".join(pit["accounting"]["unlabelled_2021_districts"]), src)
    A = rr["A_bev_only_point_in_time"]
    put("cg_pit_wape", A["wape"], f"{A['wape']:.2f}", src); put("cg_pit_spearman", A["spearman"], f"{A['spearman']:.2f}", src)
    put("cg_pit_b", A["b"], f"{A['b']:.2f}", src); put("cg_pit_inside", A["pi90_inside"], A["pi90_inside"], src)
    put("cg_pit_bevshare_wape", rr["baseline_bev_share_point_in_time"]["wape"], f"{rr['baseline_bev_share_point_in_time']['wape']:.2f}", src)
    C = rr["C_current_covariates_sanity_check"]
    put("cg_cur_wape", C["wape"], f"{C['wape']:.2f}", src); put("cg_cur_inside", C["pi90_inside"], C["pi90_inside"], src)
    put("cg_open_asof", rr["B_bev_plus_open_asof_approx"]["open_sites_cg_asof"], source=src)
    v1 = sa["chhattisgarh_validation_v1_superseded"]["methods"]
    put("cg_v1_open_share_wape", v1["open_share"]["wape"], f"{v1['open_share']['wape']:.2f}", src)
    put("sa_loo", sa["state_model_aug2025"]["loo_median_abs_log_err"], f"{sa['state_model_aug2025']['loo_median_abs_log_err']:.2f}", src)
    g = j("mh_district_gap_summary.json"); src = "eval/results/mh_district_gap_summary.json"
    put("mh_districts", g["districts"], source=src); put("mh_open_sites", g["open_sites_in_mh"], source=src)
    put("mh_zero_open_districts", g["districts_with_zero_open_sites"], source=src)
    put("mh_need_ka", g["mh_need_at_karnataka_density"], source=src); put("mh_gross_add_ka", g["mh_shortfall_vs_karnataka"], source=src)
    put("mh_net_ka", g["mh_statewide_net_vs_karnataka"], source=src)
    put("ka_bev_per_pcs", g["karnataka_bev_per_station"], f"{g['karnataka_bev_per_station']:.1f}", src)
    put("sa_b_mh", g["small_area_coef_excl_mh"][1], f"{g['small_area_coef_excl_mh'][1]:.2f}", src)
    put("mh_rank_sens", g["ranking_spearman_bev_only_vs_open_model"], f"{g['ranking_spearman_bev_only_vs_open_model']:.2f}", src)
    put("mh_verify_first", ", ".join(g["verify_first_districts"]), ", ".join(g["verify_first_districts"]), src)
    put("mh_verify_first_n", len(g["verify_first_districts"]), source=src)
    put("mh_state_open_density", g["state_open_per_10k_bev"], f"{g['state_open_per_10k_bev']:.1f}", src)
    ng = g["nagpur"]
    put("nagpur_bev", int(ng[0]), source=src); put("nagpur_open", int(ng[1]), source=src)
    put("nagpur_est", ng[2], f0(ng[2]), src); put("nagpur_lo", ng[3], f0(ng[3]), src); put("nagpur_hi", ng[4], f0(ng[4]), src)
    gd = list(csv.DictReader((RES / "mh_district_gap.csv").open()))
    ngr = next(r for r in gd if r["district"] == "Nagpur")
    put("nagpur_3w_pct", round(100 * float(ngr["bev_3W"]) / float(ngr["bev_total"])), f"{100 * float(ngr['bev_3W']) / float(ngr['bev_total']):.0f}%", "eval/results/mh_district_gap.csv")
    put("nagpur_open_density", float(ngr["open_per_10k_bev"]), f"{float(ngr['open_per_10k_bev']):.1f}", "eval/results/mh_district_gap.csv")
    cr = j("mh_corridor_summary.json"); src = "eval/results/mh_corridor_summary.json"
    put("cor_side_km", cr["side_km"], source=src); put("cor_nh_ref_pct", cr["share_km_with_NH_ref_pct"], f"{cr['share_km_with_NH_ref_pct']:.1f}%", src)
    put("cor_norm_stations", cr["norm_stations_required"], source=src); put("cor_hw_sites", cr["hw_accessible_open_sites"], source=src)
    put("cor_cov_lb", cr["coverage_pct_lower_bound"], f"{cr['coverage_pct_lower_bound']:.1f}%", src)
    put("cor_gap_ub", cr["gap_stations_upper_bound"], source=src)
    td = cr["top_districts_by_norm"]
    put("cor_top1_name", td[0][0], td[0][0], src); put("cor_top1_need", td[0][1], f0(td[0][1]), src); put("cor_top1_cov", td[0][2], f"{td[0][2]:.1f}%", src)
    c9 = j("c9_summary.json"); src = "eval/results/c9_summary.json"
    fc = c9["forecast_12m_dev_holdout"]
    for k, short in (("naive12", "naive"), ("pooled_growth_nat_0.5", "pooled"), ("share_logit_k2_0.5", "logit"), ("ensemble_pg+sl", "ensemble")):
        put(f"c9_dev_{short}", fc[k]["dev_wape"], f"{fc[k]['dev_wape']:.3f}", src); put(f"c9_hold_{short}", fc[k]["holdout_wape"], f"{fc[k]['holdout_wape']:.3f}", src)
    put("c9_hold_gain_vs_naive", round(100 * (1 - fc["share_logit_k2_0.5"]["holdout_wape"] / fc["naive12"]["holdout_wape"]), 1),
        f"{100 * (1 - fc['share_logit_k2_0.5']['holdout_wape'] / fc['naive12']['holdout_wape']):.1f}%", src)
    f3 = c9["forecast_12m_v3_purged"]
    put("c9v3_dev_naive", f3["naive12"]["dev_wape"], f"{f3['naive12']['dev_wape']:.3f}", src)
    put("c9v3_dev_logit", f3["share_logit_k2_0.5"]["dev_wape"], f"{f3['share_logit_k2_0.5']['dev_wape']:.3f}", src)
    put("c9v3_dev_ensemble", f3["ensemble_pg+sl"]["dev_wape"], f"{f3['ensemble_pg+sl']['dev_wape']:.3f}", src)
    put("c9v3_dev_pooled", f3["pooled_growth_nat_0.5"]["dev_wape"], f"{f3['pooled_growth_nat_0.5']['dev_wape']:.3f}", src)
    put("c9v3_dev_gain", round(100 * (1 - f3["share_logit_k2_0.5"]["dev_wape"] / f3["naive12"]["dev_wape"])),
        f"{100 * (1 - f3['share_logit_k2_0.5']['dev_wape'] / f3['naive12']['dev_wape']):.0f}%", src)
    bt = c9["nowcast_backtest_by_method"]["yoy"]
    put("nowcast_q4_err", bt["mean_abs_q4_err"], f"{100 * bt['mean_abs_q4_err']:.0f}%", src)
    put("nowcast_wape", bt["mean_wape"], f"{100 * bt['mean_wape']:.1f}%", src)
    put("nowcast_mean_nat_err", bt["mean_abs_nat_err"], f"{100 * bt['mean_abs_nat_err']:.1f}%", src)
    put("nowcast_max_nat_err", bt["max_abs_nat_err"], f"{100 * bt['max_abs_nat_err']:.1f}%", src)
    nc = c9["nowcast_2026_national"]
    put("nowcast_2026", nc["yoy"], source=src); put("nowcast_2026_m", round(nc["yoy"] / 1e6, 1), f"about {nc['yoy'] / 1e6:.1f} million", src)
    put("nowcast_2026_lo_m", round(min(nc.values()) / 1e6, 2), f"{min(nc.values()) / 1e6:.2f}", src)
    put("nowcast_2026_hi_m", round(max(nc.values()) / 1e6, 2), f"{max(nc.values()) / 1e6:.2f}", src)
    put("ytd_2026", c9["ytd_jan_sep_2026_national"], source=src)
    put("nowcast_growth", round(100 * (nc["yoy"] / c9["actual_2025_national"] - 1)), f"{100 * (nc['yoy'] / c9['actual_2025_national'] - 1):.0f}%", src)
    (RES / "latest.json").write_text(json.dumps(L, indent=1, ensure_ascii=False))
    print(f"latest.json: {len(L)} keys")


if __name__ == "__main__":
    main()
