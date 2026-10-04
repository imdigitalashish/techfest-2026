"""SIMULATED held-out analysis for the zonal package. No retuning: it uses the same 40 draws, seed, crew
budget, P2 knobs and held-out monsoons (Jun-Sep 2024+2025) as results/metrics.json.

1. Escape split by cause per policy: entrainment, overtopping, bypass/release. Re-floated flux is
   reported separately; it is a re-exposure flux, not an escape term.
2. Paired per-draw relative differences: P2 vs P1, P2 vs P0, P1 vs P0.
3. FWCE = (cleared + stored at season end) / catchment load. Each kg is counted once: re-arrivals
   of re-floated debris are not double-counted.
4. Fail-open fuse SENSITIVITY with P2. Assumption-driven, not evidence.

Reproduce: cd innovatex-t3-coastal-plastic/components && python -m twin_sim.analysis
"""
from __future__ import annotations

import json

import numpy as np

from . import dispatch as DP
from . import params as PR
from . import risk_forecaster as RF
from . import sim
from ._paths import RESULTS
from .run import N_DRAWS, SEED, git_sha

REPRO = "cd innovatex-t3-coastal-plastic/components && python -m twin_sim.analysis"
KEYS = ("arrived", "captured", "ent", "over", "byp", "refl", "rel", "cleared", "escaped", "load",
        "end_stored", "end_pool", "crew_h")
CAUSES = {"entrainment": "ent", "overtopping": "over", "bypass_release": "byp"}
VARIANTS = {
    "a_current_release": {},
    "b_fail_open_fuse": {"fail_open_fuse": True},
    "c_fuse_refloat_x0.5": {"fail_open_fuse": True, "refloat_mult": 0.5},
    "c_fuse_refloat_x0.2": {"fail_open_fuse": True, "refloat_mult": 0.2},
}


def run_heldout(n_draws: int = N_DRAWS, seed: int = SEED, years: list | None = None) -> dict:
    """Per-draw totals (D,) summed over sites and years, for P0, P1, P2 and the P2 hardware variants."""
    years = years or sim.HOLDOUT_YEARS
    P = sim.param_arrays(PR.draw(n_draws, seed))
    names = ["P0", "P1", "P2"] + [f"P2|{v}" for v in VARIANTS if VARIANTS[v]]
    runs: dict = {n: None for n in names}
    for y in years:
        phys = sim.physics(y, P)
        fc = RF.season_forecast(y)
        for name in names:
            pol, _, var = name.partition("|")
            r = sim.run_season(phys, dict(P, **VARIANTS[var]) if var else P, DP.make_policy(pol, fc), fc,
                               sensor_seed=seed + y)
            part = {k: (r[k].sum(axis=-1) if r[k].ndim == 2 else r[k]) for k in KEYS}
            runs[name] = part if runs[name] is None else {k: runs[name][k] + part[k] for k in KEYS}
    runs["P2|a_current_release"] = runs["P2"]
    return runs


def dist(x, nd: int = 4) -> dict:
    x = np.asarray(x, float)
    return {"median": round(float(np.median(x)), nd), "p05": round(float(np.percentile(x, 5)), nd),
            "p95": round(float(np.percentile(x, 95)), nd)}


def paired(a, b) -> dict:
    """Per-draw relative difference (a - b) / b; negative = a lets less plastic escape."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    return {**dist((a - b) / b), "draws_a_lower": int((a < b).sum()), "n_draws": int(a.size)}


def fwce(R: dict) -> np.ndarray:
    return (R["cleared"] + R["end_stored"]) / R["load"]


def escape_split(R: dict) -> dict:
    return {
        "escaped_kg": dist(R["escaped"], 0), "arrived_at_boom_kg": dist(R["arrived"], 0),
        "catchment_load_kg": dist(R["load"], 0),
        "by_cause": {c: {"kg": dist(R[k], 0), "share_of_escaped": dist(R[k] / R["escaped"]),
                         "share_of_arrived": dist(R[k] / R["arrived"]), "share_of_load": dist(R[k] / R["load"])}
                     for c, k in CAUSES.items()},
        "refloated_kg": {"tidal_refloat": dist(R["refl"] - R["rel"], 0), "flood_release": dist(R["rel"], 0),
                         "tidal_refloat_share_of_arrived": dist((R["refl"] - R["rel"]) / R["arrived"])},
        "held_upstream_at_season_end_kg": dist(R["end_pool"], 0),
    }


def summarise(runs: dict, metrics: dict | None = None) -> dict:
    out = {"escape_split": {p: escape_split(runs[p]) for p in ("P0", "P1", "P2")},
           "paired_escaped_rel_diff": {"P2_vs_P1": paired(runs["P2"]["escaped"], runs["P1"]["escaped"]),
                                       "P2_vs_P0": paired(runs["P2"]["escaped"], runs["P0"]["escaped"]),
                                       "P1_vs_P0": paired(runs["P1"]["escaped"], runs["P0"]["escaped"])},
           "fwce": {p: {"fwce": dist(fwce(runs[p])), "gross_captured_over_arrived": dist(
               runs[p]["captured"] / runs[p]["arrived"])} for p in ("P0", "P1", "P2")}}
    Ea, Fa = runs["P2"]["escaped"], fwce(runs["P2"])
    out["fuse_sensitivity_P2"] = {
        v: {"escaped_kg": dist(runs[f"P2|{v}"]["escaped"], 0),
            "escaped_rel_vs_a": paired(runs[f"P2|{v}"]["escaped"], Ea),
            "fwce": dist(fwce(runs[f"P2|{v}"])),
            "fwce_delta_pp_vs_a": dist((fwce(runs[f"P2|{v}"]) - Fa) * 100, 2),
            "by_cause_kg": {c: dist(runs[f"P2|{v}"][k], 0) for c, k in CAUSES.items()},
            "flood_release_kg": dist(runs[f"P2|{v}"]["rel"], 0),
            "tidal_refloat_kg": dist(runs[f"P2|{v}"]["refl"] - runs[f"P2|{v}"]["rel"], 0)}
        for v in VARIANTS}
    bal = max(float(np.abs(R["load"] - R["escaped"] - R["cleared"] - R["end_stored"] - R["end_pool"]).max())
              for R in runs.values())
    out["checks"] = {"mass_balance_max_abs_err_kg": round(bal, 6),
                     "equal_crew_hours": bool(all(np.allclose(R["crew_h"], runs["P0"]["crew_h"])
                                                  for R in runs.values()))}
    if metrics:
        ours = {p: out["escape_split"][p]["escaped_kg"]["median"] for p in ("P0", "P1", "P2")}
        theirs = {p: metrics["heldout_2024_2025"][p]["escaped_kg_median"] for p in ("P0", "P1", "P2")}
        out["checks"]["escaped_median_matches_metrics_json"] = bool(all(abs(ours[p] - theirs[p]) <= 1 for p in ours))
        out["checks"]["metrics_json_escaped_median"] = theirs
    out["per_draw"] = {n: {"escaped_kg": np.round(R["escaped"], 0).tolist(), "fwce": np.round(fwce(R), 4).tolist()}
                       for n, R in sorted(runs.items())}
    return out


def main():
    metrics = json.loads((RESULTS / "metrics.json").read_text())
    res = summarise(run_heldout(), metrics)
    doc = {
        "label": "SIMULATED",
        "what": "digital-twin analysis, held-out monsoons Jun-Sep 2024+2025, 4 sites summed; real forcing "
                "(ERA5 rain, archived JMA day-ahead forecast, harmonic tide), ASSUMPTION process parameters",
        "reproduce": REPRO, "git_sha_at_run": git_sha(), "n_draws": N_DRAWS, "seed": SEED,
        "years": sim.HOLDOUT_YEARS, "crew_budget": f"{DP.N_CREWS} crews x {DP.SHIFT_H} h/day, all runs",
        "p2_knobs": DP.load_knobs(),
        "definitions": {
            "interval": "median and p05/p95 across the 40 Monte Carlo draws",
            "paired_rel_diff": "(a - b) / b per draw, same draw and sensor noise; negative = a lets less escape",
            "arrived_at_boom": "contract arrived_kg: includes re-arrivals of re-floated/released debris",
            "fwce": "(cleared + stored at 30 Sep) / catchment load; each kg counted once",
            "gross_captured_over_arrived": "captured_kg / arrived_kg (double-counts re-captures)",
            "tidal_refloat": "stored debris lifted on flood tide into the upstream pool; it re-arrives on the "
                             "ebb (re-exposure flux, not an escape term)",
            "flood_release": "stored debris released during bypass/high head (current hardware), into the pool",
            "fuse": "SENSITIVITY: at release only the arriving flux passes; the pocket keeps its catch",
            "refloat_mult": "SENSITIVITY: one-way pocket scales tidal re-float; x1 with the fuse equals variant b",
        },
        "caveats": [
            "SIMULATED: escaped_kg is computed by the same assumed process model that the policies act on, so "
            "results show relative value under stated assumptions, not field evidence; field calibration comes "
            "in Round 2.",
            "Fuse/pocket rows are SENSITIVITY runs (assumption-driven), not evidence about real hardware.",
            "No retuning: P2 knobs, draws, seeds and crew budget identical to results/metrics.json.",
        ],
        **res,
    }
    path = RESULTS / "analysis.json"
    path.write_text(json.dumps(doc, indent=1))
    s = res
    print(json.dumps({"P2_vs_P1": s["paired_escaped_rel_diff"]["P2_vs_P1"],
                      "P2_vs_P0": s["paired_escaped_rel_diff"]["P2_vs_P0"],
                      "checks": {k: v for k, v in s["checks"].items() if k != "metrics_json_escaped_median"}}))
    print("analysis.json KB %.1f" % (path.stat().st_size / 1e3))


if __name__ == "__main__":
    main()
