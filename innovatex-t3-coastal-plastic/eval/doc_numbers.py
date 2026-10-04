"""Registry of every number the deliverables quote from our own committed runs.

Templates in deliverables/src/ write {{r:alias}}; eval/render_docs.py replaces it with the formatted value read from the
committed results file below. Each alias names the file, the JSON path and the format, so any number in the deck can be
traced back to its run (each results file carries its own `reproduce` command).
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = {
    "twin": "components/twin_sim/results/metrics.json",
    "an": "components/twin_sim/results/analysis.json",
    "mrv": "components/mrv_ledger/results/metrics.json",
    "mrvd": "components/mrv_ledger/results/eval_detail.json",
    "det": "components/detection/results/metrics.json",
    "detzs": "components/detection/results/metrics_zeroshot.json",
    "gron": "components/detection/results/zeroshot_groningen_eval.json",
    "flux": "components/detection/results/flux_synthetic.json",
    "imp": "eval/impact_estimate.json",
}

_PAIR = "paired_escaped_rel_diff"
_ES = "escape_split.P2.by_cause"
_FS = "fuse_sensitivity_P2"

# alias: (file key, dotted JSON path, format)
ALIASES: dict[str, tuple[str, str, str]] = {
    # --- twin: paired policy comparisons (held-out 2024+2025, SIMULATED) ---
    "n_draws": ("an", "n_draws", "int"),
    "crew_budget": ("an", "crew_budget", "raw"),
    "p2p0_med": ("an", f"{_PAIR}.P2_vs_P0.median", "spct1"),
    "p2p0_lo": ("an", f"{_PAIR}.P2_vs_P0.p05", "spct1"),
    "p2p0_hi": ("an", f"{_PAIR}.P2_vs_P0.p95", "spct1"),
    "p2p0_n": ("an", f"{_PAIR}.P2_vs_P0.draws_a_lower", "int"),
    "p2p1_med": ("an", f"{_PAIR}.P2_vs_P1.median", "spct1"),
    "p2p1_lo": ("an", f"{_PAIR}.P2_vs_P1.p05", "spct1"),
    "p2p1_hi": ("an", f"{_PAIR}.P2_vs_P1.p95", "spct1"),
    "p2p1_n": ("an", f"{_PAIR}.P2_vs_P1.draws_a_lower", "int"),
    "p1p0_med": ("an", f"{_PAIR}.P1_vs_P0.median", "spct1"),
    "p1p0_lo": ("an", f"{_PAIR}.P1_vs_P0.p05", "spct1"),
    "p1p0_hi": ("an", f"{_PAIR}.P1_vs_P0.p95", "spct1"),
    # --- twin: flux-weighted capture efficiency ---
    "fwce_p0": ("an", "fwce.P0.fwce.median", "pct1"),
    "fwce_p1": ("an", "fwce.P1.fwce.median", "pct1"),
    "fwce_p2": ("an", "fwce.P2.fwce.median", "pct1"),
    "fwce_p2_lo": ("an", "fwce.P2.fwce.p05", "pct1"),
    "fwce_p2_hi": ("an", "fwce.P2.fwce.p95", "pct1"),
    # --- twin: why plastic escapes (P2) ---
    "ent_esc": ("an", f"{_ES}.entrainment.share_of_escaped.median", "pct1"),
    "ent_esc_lo": ("an", f"{_ES}.entrainment.share_of_escaped.p05", "pct1"),
    "ent_esc_hi": ("an", f"{_ES}.entrainment.share_of_escaped.p95", "pct1"),
    "ent_arr": ("an", f"{_ES}.entrainment.share_of_arrived.median", "pct1"),
    "over_esc": ("an", f"{_ES}.overtopping.share_of_escaped.median", "pct1"),
    "byp_esc": ("an", f"{_ES}.bypass_release.share_of_escaped.median", "pct1"),
    "refloat_arr": ("an", "escape_split.P2.refloated_kg.tidal_refloat_share_of_arrived.median", "pct1"),
    # --- twin: fail-open fuse and one-way pocket SENSITIVITY (P2) ---
    "fuse_med": ("an", f"{_FS}.b_fail_open_fuse.escaped_rel_vs_a.median", "spct1"),
    "fuse_lo": ("an", f"{_FS}.b_fail_open_fuse.escaped_rel_vs_a.p05", "spct1"),
    "pk5_med": ("an", f"{_FS}.c_fuse_refloat_x0.5.escaped_rel_vs_a.median", "spct1"),
    "pk5_lo": ("an", f"{_FS}.c_fuse_refloat_x0.5.escaped_rel_vs_a.p05", "spct1"),
    "pk5_hi": ("an", f"{_FS}.c_fuse_refloat_x0.5.escaped_rel_vs_a.p95", "spct1"),
    "pk5_fwce": ("an", f"{_FS}.c_fuse_refloat_x0.5.fwce_delta_pp_vs_a.median", "pp1"),
    "pk2_med": ("an", f"{_FS}.c_fuse_refloat_x0.2.escaped_rel_vs_a.median", "spct1"),
    "pk2_lo": ("an", f"{_FS}.c_fuse_refloat_x0.2.escaped_rel_vs_a.p05", "spct1"),
    "pk2_hi": ("an", f"{_FS}.c_fuse_refloat_x0.2.escaped_rel_vs_a.p95", "spct1"),
    "pk2_fwce": ("an", f"{_FS}.c_fuse_refloat_x0.2.fwce_delta_pp_vs_a.median", "pp1"),
    # --- twin: ablations (which ingredient matters), SIMULATED ---
    "abl_tide_med": ("an", "ablations.paired_escaped_rel_diff.P2_vs_P2_notide.median", "spct1"),
    "abl_tide_lo": ("an", "ablations.paired_escaped_rel_diff.P2_vs_P2_notide.p05", "spct1"),
    "abl_tide_hi": ("an", "ablations.paired_escaped_rel_diff.P2_vs_P2_notide.p95", "spct1"),
    "abl_tide_n": ("an", "ablations.paired_escaped_rel_diff.P2_vs_P2_notide.draws_a_lower", "int"),
    "abl_fc_med": ("an", "ablations.paired_escaped_rel_diff.P2_vs_P2_nofc.median", "spct1"),
    "abl_mass_med": ("an", "ablations.paired_escaped_rel_diff.P1m_vs_P1.median", "spct1"),
    "abl_mass_lo": ("an", "ablations.paired_escaped_rel_diff.P1m_vs_P1.p05", "spct1"),
    "abl_mass_hi": ("an", "ablations.paired_escaped_rel_diff.P1m_vs_P1.p95", "spct1"),
    "p2p1m_med": ("an", "ablations.paired_escaped_rel_diff.P2_vs_P1m.median", "spct1"),
    "p2p1m_lo": ("an", "ablations.paired_escaped_rel_diff.P2_vs_P1m.p05", "spct1"),
    "p2p1m_hi": ("an", "ablations.paired_escaped_rel_diff.P2_vs_P1m.p95", "spct1"),
    # --- twin: what 'under the boom' is made of; how often flow is fast (SIMULATED) ---
    "ent_floor_esc": ("an", "entrainment_split.P2.floor_1_minus_emax.share_of_escaped.median", "pct0"),
    "ent_vel_esc": ("an", "entrainment_split.P2.velocity_driven.share_of_escaped.median", "pct0"),
    "expo_kg": ("an", "exposure_P2_nominal.theta90.share_of_arrived_kg", "pct1"),
    "expo_h": ("an", "exposure_P2_nominal.theta90.share_of_hours", "pct1"),
    # --- twin: boom-angle SENSITIVITY (follows from the assumed capture curve) ---
    "ang45_med": ("an", "boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_theta90.median", "spct1"),
    "ang30_med": ("an", "boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_theta90.median", "spct1"),
    "ang20_med": ("an", "boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_theta90.median", "spct1"),
    "ang20_lo": ("an", "boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_theta90.p05", "spct1"),
    "ang20_hi": ("an", "boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_theta90.p95", "spct1"),
    "ang20_len": ("an", "boom_angle_sensitivity_P2.a_current_release.theta20.boom_length_factor_1_over_sin_theta", "f1"),
    "combo20_med": ("an", "boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_current_a_theta90.median", "spct1"),
    # --- twin: boom overtopping and bypass hours (SIMULATED; the twin does not model street flooding) ---
    "ovf_p0": ("twin", "heldout_2024_2025.P0.overflow_site_hours_median", "f1"),
    "ovf_p1": ("twin", "heldout_2024_2025.P1.overflow_site_hours_median", "f1"),
    "ovf_p2": ("twin", "heldout_2024_2025.P2.overflow_site_hours_median", "f1"),
    "byp_h": ("twin", "heldout_2024_2025.P2.bypass_site_hours_median", "int"),
    # --- ILLUSTRATIVE ESTIMATE per boom (eval/impact_estimate.py: reported catch x twin ratios) ---
    "imp_days": ("imp", "inputs.monsoon_days", "int"),
    # --- twin: forcing quality ---
    "tide_rmse_mithi": ("twin", "tide_fit.mithi_mahim.rmse_m", "f2"),
    "tide_var_mithi": ("twin", "tide_fit.mithi_mahim.variance_explained", "pct1"),
    # --- evidence ledger (SYNTHETIC records) ---
    "mrv_recall": ("mrv", "recall_fraud_at_5pct_false_flags", "pct1"),
    "mrv_ff": ("mrv", "false_flag_rate_test", "pct1"),
    "mrv_base": ("mrv", "baseline_ratio_recall_at_5pct", "pct1"),
    "mrv_slip": ("mrv", "status_quo_slip_check_recall", "pct0"),
    "mrv_prec5": ("mrv", "precision_at_5pct_prevalence", "pct1"),
    "mrv_prec10": ("mrv", "precision_at_10pct_prevalence", "pct1"),
    "mrv_tamper": ("mrv", "tamper_detection_rate_with_anchor", "pct0"),
    "mrv_small": ("mrv", "recall_inflated_x1.2-1.5", "pct1"),
    "mrv_phantom": ("mrv", "recall_phantom", "pct0"),
    "mrv_wet": ("mrv", "recall_wetted_or_silted", "pct0"),
    "mrv_infl": ("mrv", "recall_inflated_x1.2-3", "pct1"),
    "mrv_dens125": ("mrvd", "reconciliation.sensitivity.false_flag_rate_if_true_density_x1.25", "pct1"),
    "mrv_trunc_chain": ("mrvd", "tamper.truncate_tail.detected_chain_only", "pct0"),
    "mrv_trunc_anchor": ("mrvd", "tamper.truncate_tail.detected_with_anchor", "pct0"),
    # --- detector (BUILT; public TUD-GV floating-litter images, not Mumbai) ---
    "det_map50": ("det", "mAP50", "f3"),
    "det_map5095": ("det", "mAP50_95", "f3"),
    "det_p": ("det", "precision", "f3"),
    "det_r": ("det", "recall", "f3"),
    "det_n": ("det", "n_test_images", "int"),
    "det_val_map50": ("det", "other_splits.val.mAP50", "f3"),
    "det_gron_map50": ("det", "other_splits.groningen.mAP50", "f3"),
    "det_gron_r": ("det", "other_splits.groningen.recall", "f3"),
    "det_gron_n": ("det", "other_splits.groningen.n_images", "int"),
    "det_zs_map50": ("detzs", "mAP50", "f3"),
    "det_lat_mac": ("det", "latency_ms_mps.median", "int"),
    # SYNTHETIC line-crossing counter, pooled over clips (fixed tracker and direction, review gpt-6-sol #3)
    "flux_err": ("flux", "headline.signed_count_error_pct", "f1"),
    "flux_n_seq": ("flux", "headline.sequences", "int"),
    "flux_gt": ("flux", "headline.gt_crossings", "int"),
    "flux_false": ("flux", "headline.false", "int"),
    "flux_dup": ("flux", "headline.false_duplicate", "int"),
    "flux_missed": ("flux", "headline.missed", "int"),
}


@lru_cache(maxsize=None)
def _load(key: str) -> dict:
    return json.loads((ROOT / FILES[key]).read_text())


def _get(obj, path: str):
    """Walk a dotted path; keys may themselves contain dots (e.g. 'c_fuse_refloat_x0.5'), so match greedily."""
    parts = path.split(".")
    i = 0
    while i < len(parts):
        for j in range(len(parts), i, -1):
            k = ".".join(parts[i:j])
            if isinstance(obj, dict) and k in obj:
                obj = obj[k]
                i = j
                break
        else:
            raise KeyError(f"{path!r}: no key at {'.'.join(parts[i:])!r}")
    return obj


def fmt(v, kind: str) -> str:
    minus = "\u2212"
    if kind == "raw":
        return str(v)
    if kind == "int":
        return f"{int(round(v)):,}"
    if kind == "f1":
        return f"{v:.1f}"
    if kind == "f2":
        return f"{v:.2f}"
    if kind == "f3":
        return f"{v:.3f}"
    if kind == "pct0":
        return f"{100 * v:.0f}%"
    if kind == "pct1":
        return f"{100 * v:.1f}%"
    if kind == "spct1":  # signed percentage; a negative escaped-kg change means less plastic escaped
        s = f"{100 * v:+.1f}%"
        return s.replace("-", minus)
    if kind == "pp1":
        return f"{v:+.1f} pp".replace("-", minus)
    if kind == "tonnes":
        return f"{v / 1000:,.0f} t"
    raise ValueError(kind)


def _det_line() -> str:
    """One sentence about the detector, built only from committed detection results."""
    d = _load("det")
    kind = str(d.get("baseline_kind", ""))
    n = d.get("n_test_images")
    if kind.upper().startswith("ZERO"):
        return (f"off-the-shelf (COCO-pretrained, zero-shot) YOLO11n on {n} held-out floating-litter test images: "
                f"mAP50 {d['mAP50']:.3f}, but recall {d['recall']:.3f} at score {d['precision_recall_at_score']}. "
                "Off-the-shelf models miss most river litter; training on floating-litter data is required.")
    zs = _load("detzs")
    g = d["other_splits"]["groningen"]
    fm = d["frozen_matcher_test"]
    # like-for-like: trained vs off-the-shelf both scored by the same frozen matcher (review gpt-6-sol #6)
    assert abs(fm["zero_shot"]["mAP50"] - zs["mAP50"]) < 1e-4, "frozen-matcher zero-shot differs from metrics_zeroshot.json"
    return (f"YOLO11n trained on public floating-litter images (TUD-GV): on {n} held-out test images, mAP50 "
            f"{d['mAP50']:.3f}, precision {d['precision']:.3f}, recall {d['recall']:.3f} (Ultralytics evaluator). "
            f"Scored with one shared matcher, the trained model reaches mAP50 {fm['trained']['mAP50']:.3f} against "
            f"{fm['zero_shot']['mAP50']:.3f} off the shelf. "
            f"At another site's camera (Groningen, {g['n_images']} images) mAP50 falls to {g['mAP50']:.3f}: "
            "it does not yet transfer, and Mumbai nullah film is untested.")


def _flux_ci() -> str:
    lo, hi = _load("flux")["headline"]["signed_count_error_ci95_pct"]
    return f"{lo:+.1f}% to {hi:+.1f}%".replace("-", "\u2212")


def _rng(path: str, dp: int, unit: str):
    def f() -> str:
        lo, hi = _get(_load("imp"), path)
        return f"{lo:.{dp}f}–{hi:.{dp}f} {unit}"
    return f


def _imp_retro_span() -> str:
    r = _load("imp")["retrofit_avoided_t_per_monsoon"]
    return f"{min(r['p95']):.0f}–{max(r['p05']):.0f} t"


COMPUTED = {"det_line": _det_line, "flux_ci": _flux_ci,
            "imp_esc": _rng("escaping_t_per_day", 1, "t"),
            "imp_disp": _rng("dispatch_avoided_t_per_monsoon.median", 1, "t"),
            "imp_retro": _rng("retrofit_avoided_t_per_monsoon.median", 0, "t"),
            "imp_retro_span": _imp_retro_span}


def value(alias: str) -> str:
    if alias in COMPUTED:
        return COMPUTED[alias]()
    if alias not in ALIASES:
        raise KeyError(f"unknown alias {alias!r}")
    key, path, kind = ALIASES[alias]
    return fmt(_get(_load(key), path), kind)


def source_of(alias: str) -> str:
    if alias in COMPUTED:
        return "computed from " + ", ".join(FILES[k] for k in ("det", "detzs", "gron"))
    key, path, _ = ALIASES[alias]
    return f"{FILES[key]} :: {path}"


if __name__ == "__main__":
    for a in list(ALIASES) + list(COMPUTED):
        try:
            print(f"{a:18s} {value(a):>14s}   {source_of(a)}")
        except Exception as e:  # list unresolved aliases instead of failing
            print(f"{a:18s} {'UNRESOLVED':>14s}   {source_of(a)}  ({e})")
