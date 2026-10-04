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
    "det": "components/detection/results/metrics.json",
    "detzs": "components/detection/results/zeroshot_test_metrics.json",
    "gron": "components/detection/results/zeroshot_groningen_eval.json",
    "flux": "components/detection/results/flux_synthetic.json",
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
    gr = _load("gron")
    return (f"YOLO11n trained on public floating-litter images (TUD-GV): held-out test mAP50 {d['mAP50']:.3f} "
            f"(zero-shot: {zs['mAP50']:.3f}) on {n} images; precision {d['precision']:.3f}, recall {d['recall']:.3f} "
            f"at score {d['precision_recall_at_score']}.")


COMPUTED = {"det_line": _det_line}


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
