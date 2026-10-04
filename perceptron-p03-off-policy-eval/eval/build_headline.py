"""Build eval/results/headline.json: every number the deliverables quote, computed from committed result files.

Reproduce: cd perceptron-p03-off-policy-eval && .venv/bin/python eval/build_headline.py
Sources: eval/results/sim_bank_runs.csv (SYNTHETIC bank v0) · obd_slice.json (REAL, pre-registered) ·
obd_slice_deviation_floor.json (REAL, disclosed deviation) · decomposer_review.json (SYNTHETIC) · ../components/delta_estimator/autoresearch/results.tsv
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "eval" / "results"


def sgn(x: float, nd: int) -> str:
    return f"{x:+.{nd}f}".replace("-", "−")


def main():
    disp, src = {}, {}

    def put(key, value, source):
        disp[key], src[key] = value, source

    # ---- simulator bank v0 (SYNTHETIC) ----
    df = pd.read_csv(RES / "sim_bank_runs.csv")
    for s, tag in (("S1_drift_masks_gain", "s1"), ("S2_drift_fakes_gain", "s2")):
        d = df[(df.scenario == s) & (df.estimator == "DR")]
        t = d.truth.iloc[0]
        put(f"{tag}_naive_pp", sgn(100 * d.naive.mean(), 1), f"sim_bank_runs.csv {s} mean naive ×100")
        put(f"{tag}_truth_pp", sgn(100 * t, 1), f"sim_bank_runs.csv {s} truth ×100")
        put(f"{tag}_dr_pp", sgn(100 * d.delta.mean(), 1), f"sim_bank_runs.csv {s} DR mean ×100")
        put(f"{tag}_dr_rmse_pp", f"{100 * np.sqrt(((d.delta - t) ** 2).mean()):.1f}", f"sim_bank_runs.csv {s} DR RMSE ×100")
        put(f"{tag}_dr_cover", f"{100 * d.covered.mean():.0f}%", f"sim_bank_runs.csv {s} DR Wald coverage")
        put(f"{tag}_naive_wrong", f"{int((np.sign(d.naive) != np.sign(t)).sum())}/{len(d)}", f"sim_bank_runs.csv {s} naive wrong-sign seeds")
    d4 = df[(df.scenario == "S4_hidden_override") & (df.estimator == "DR")]
    put("s4_dr_bias_pp", sgn(100 * (d4.delta.mean() - d4.truth.iloc[0]), 1), "sim_bank_runs.csv S4 DR bias ×100")
    put("s4_dr_cover", f"{100 * d4.covered.mean():.0f}%", "sim_bank_runs.csv S4 DR coverage")
    m4 = df[(df.scenario == "S4_hidden_override") & (df.estimator == "MSM_HAJEK")]
    put("s4_msm_valid", f"{int(m4.covered.sum())}/{len(m4)}", "sim_bank_runs.csv S4 MSM truth inside bounds at Γ ≥ Γ_true")
    put("s4_gamma_star", f"{m4.gamma_star.median():.2f}", "sim_bank_runs.csv S4 median Γ*")
    put("bank_seeds", str(df.seed.nunique()), "sim_bank_runs.csv seeds")

    # ---- real OBD, pre-registered ----
    o = json.loads((RES / "obd_slice.json").read_text())
    put("obd_rows_random", f"{o['window']['n_random']:,}", "obd_slice.json window.n_random")
    put("obd_rows_bts", f"{o['window']['n_bts']:,}", "obd_slice.json window.n_bts")
    put("obd_hours", str(o["window"]["hours"]), "obd_slice.json window.hours")
    put("obd_ctr_bts_k", f"{1000 * o['a2']['truth']:.2f}", "obd_slice.json a2.truth ×1000")
    put("obd_ctr_random_k", f"{1000 * o['a2']['random_ctr']:.2f}", "obd_slice.json a2.random_ctr ×1000")
    for pol, tag in (("P-static", "static"), ("P-hourly", "hourly")):
        for e in ("IPW", "SNIPW", "DR", "DM"):
            put(f"a2_{tag}_{e.lower()}_relerr", f"{100 * o['a2'][pol][e]['rel_err']:.1f}%", f"obd_slice.json a2.{pol}.{e}.rel_err")
    put("a1_changed", f"{o['a1']['cells_ratio_ge_1.5']}/20", "obd_slice.json a1.cells_ratio_ge_1.5")
    put("a1_median_ratio", f"{o['a1']['median_ratio']:.0f}", "obd_slice.json a1.median_ratio")
    A, Bd = o["a3_halves"]["A_deploy_BTS"], o["a3_halves"]["B_rollback_to_Random"]
    put("a3A_naive_k", sgn(1000 * A["naive"], 2), "obd_slice.json a3_halves.A.naive ×1000")
    put("a3A_truth_k", sgn(1000 * A["truth"], 2), "obd_slice.json a3_halves.A.truth ×1000")
    put("a3A_dr_k", sgn(1000 * A["DR"]["policy_effect_after"], 2), "obd_slice.json a3_halves.A.DR ×1000")
    put("a3A_overstate", f"{100 * (A['naive'] - A['truth']) / A['truth']:.0f}%", "obd_slice.json (naive − truth)/truth, direction A")
    put("a3A_naive_err_k", f"{1000 * abs(A['naive'] - A['truth']):.2f}", "obd_slice.json |naive − truth| ×1000")
    put("a3A_dr_err_k", f"{1000 * A['DR']['abs_err']:.2f}", "obd_slice.json |DR − truth| ×1000")
    put("a3B_naive_k", sgn(1000 * Bd["naive"], 2), "obd_slice.json a3_halves.B.naive ×1000")
    put("a3B_truth_k", sgn(1000 * Bd["truth"], 2), "obd_slice.json a3_halves.B.truth ×1000")
    put("a3B_dr_k", sgn(1000 * Bd["DR"]["policy_effect_after"], 2), "obd_slice.json a3_halves.B.DR ×1000")
    put("a3A_ess_pct", f"{100 * A['ess_after'] / A['n_after']:.1f}%", "obd_slice.json a3_halves.A ESS/n")

    # ---- real OBD, disclosed deviation (whole-day pairs) ----
    dv = json.loads((RES / "obd_slice_deviation_floor.json").read_text())
    pairs = dv["a3_daypairs"]
    a_fail = sum(not p["A_deploy_BTS"]["DR"]["S1_ci_contains_0"] for p in pairs.values())
    b_ok = sum(p["B_rollback_to_Random"]["DR"]["S1_ci_contains_0"] for p in pairs.values())
    min_ess = min(p["A_deploy_BTS"]["ess_after"] / p["A_deploy_BTS"]["n_after"] for p in pairs.values())
    put("day_pairs", str(len(pairs)), "obd_slice_deviation_floor.json a3_daypairs count")
    put("dayA_dr_fail", f"{a_fail}/{len(pairs)}", "obd_slice_deviation_floor.json day pairs, direction A, DR CI misses truth")
    put("dayB_dr_ok", f"{b_ok}/{len(pairs)}", "obd_slice_deviation_floor.json day pairs, direction B, DR CI contains truth")
    put("dayA_min_ess_pct", f"{100 * min_ess:.2f}%", "obd_slice_deviation_floor.json min ESS/n, direction A")

    # ---- decomposer review (SYNTHETIC) ----
    r = json.loads((RES / "decomposer_review.json").read_text())
    drift = {float(k[5:]): v for k, v in r.items() if v["kind"] == "drift"}
    wrong = sorted(x for x, v in drift.items() if v["naive_sign_ok"] == 0.0)
    right = sorted(x for x, v in drift.items() if v["naive_sign_ok"] == 1.0)
    put("sweep_wrong_from", sgn(max(wrong), 2) if wrong else "none", "decomposer_review.json: largest drift with naive wrong-sign in all seeds")
    put("sweep_right_from", sgn(min(right), 2) if right else "none", "decomposer_review.json: smallest drift with naive right-sign in all seeds")
    put("sweep_dr_rmse_max_pp", f"{100 * max(v['dr_rmse'] for v in drift.values()):.1f}", "decomposer_review.json drift sweep max DR RMSE ×100")
    put("sweep_naive_rmse_max_pp", f"{100 * max(v['naive_rmse'] for v in drift.values()):.1f}", "decomposer_review.json drift sweep max naive RMSE ×100")
    put("sweep_points", str(len(drift)), "decomposer_review.json drift points")
    fb = r["feedback1.00"]
    put("fb_direct_pp", sgn(100 * fb["truth"]["effect_after"], 1), "decomposer_review.json feedback1.00 direct ×100")
    put("fb_total_pp", sgn(100 * fb["truth"]["total_effect"], 1), "decomposer_review.json feedback1.00 total ×100")
    put("fb_dr_pp", sgn(100 * fb["dr_mean"], 1), "decomposer_review.json feedback1.00 DR mean ×100")
    ms = r["nonlinmix2.0"]
    put("ms_dr_bias_pp", sgn(100 * (ms["dr_mean"] - ms["truth"]["effect_after"]), 2), "decomposer_review.json nonlinmix2.0 DR bias ×100")
    put("ms_dm_bias_pp", sgn(100 * ms["dm_bias"], 2), "decomposer_review.json nonlinmix2.0 DM bias ×100")
    put("ms_mixdm_bias_pp", sgn(100 * ms["mix_dm_bias"], 2), "decomposer_review.json nonlinmix2.0 DM-mix bias ×100")
    put("ms_mixdr_bias_pp", sgn(100 * ms["mix_dr_bias"], 2), "decomposer_review.json nonlinmix2.0 DR-mix bias ×100")
    put("shap_cover", f"{100 * np.mean([v['shap_cover'] for v in r.values()]):.0f}%", "decomposer_review.json mean Shapley coverage")

    put("ms_true_mix_pp", sgn(100 * ms["truth"]["mix"], 2), "decomposer_review.json nonlinmix2.0 true mix ×100")
    put("ms_true_effect_pp", sgn(100 * ms["truth"]["effect_after"], 1), "decomposer_review.json nonlinmix2.0 true effect ×100")
    put("fb_gap_pp", f"{100 * (fb['truth']['total_effect'] - fb['truth']['effect_after']):.1f}", "decomposer_review.json feedback1.00 total − direct ×100")

    # ---- overlap gate: simulator calibration + post-hoc OBD ----
    g = json.loads((ROOT / "eval" / "gate_rule.json").read_text())
    put("gate_tau_ess", f"{100 * g['tau_ess']:.0f}%", "gate_rule.json tau_ess")
    put("gate_sim_answer", f"{100 * g['answer_rate']:.0f}%", "gate_rule.json answer_rate")
    put("gate_sim_cov", f"{g['pooled_coverage_answered']:.2f}", "gate_rule.json pooled_coverage_answered")
    put("gate_sim_ungated_worst", f"{g['ungated']['worst_cfg_cov']:.2f}", "gate_rule.json ungated.worst_cfg_cov")
    put("gate_sim_configs", "36", "eval/calibrate_gate.py CONFIGS (3 x 2 x 3 x 2)")
    go = json.loads((RES / "gate_obd_posthoc.json").read_text())["summary"]
    put("gate_obd_answered", f"{go['answered']}/{go['cases']}", "gate_obd_posthoc.json answered/cases")
    put("gate_obd_wrong", str(go["answered_wrong"]), "gate_obd_posthoc.json answered_wrong")
    put("gate_obd_caught", f"{go['failures_abstained']}/{go['failures_total']}", "gate_obd_posthoc.json failures abstained/total")
    put("gate_obd_cost", str(go["abstained_but_right"]), "gate_obd_posthoc.json abstained_but_right")

    # ---- C6 ratchet ----
    led = pd.read_csv(ROOT / "components" / "delta_estimator" / "autoresearch" / "results.tsv", sep="\t")
    put("ratchet_baseline", f"{led.iloc[0]['metric(nRMSE,dev)']:.3f}", "autoresearch/results.tsv baseline")

    (RES / "headline.json").write_text(json.dumps({"display": disp, "source": src}, indent=1, ensure_ascii=False))
    for k, v in disp.items():
        print(f"{k:28s} {v:>12s}   {src[k]}")


if __name__ == "__main__":
    main()
