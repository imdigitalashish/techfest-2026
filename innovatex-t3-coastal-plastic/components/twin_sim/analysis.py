"""SIMULATED held-out analysis for the zonal package. No retuning: it uses the same 40 draws, seed, crew
budget, P2 knobs and held-out monsoons (Jun-Sep 2024+2025) as results/metrics.json.

1. Escape split by cause per policy: entrainment, overtopping, bypass/release. Re-floated flux is
   reported separately; it is a re-exposure flux, not an escape term.
2. Paired per-draw relative differences: P2 vs P1, P2 vs P0, P1 vs P0.
3. FWCE = (cleared + stored at season end) / catchment load. Each kg is counted once: re-arrivals
   of re-floated debris are not double-counted.
4. Fail-open fuse SENSITIVITY with P2. Assumption-driven, not evidence.
5. Boom-angle SENSITIVITY with P2: entrainment sees |v|*sin(theta). Entrainment is split into the
   (1 - e_max) slack-water floor and the velocity-driven part. Exposure is the share of hours and of
   arrived kg at |v| > v50 (P2, nominal parameters).
6. Ablations (review findings 3/4/11): P1m (sensor-only, mass-ranked, P1's fixed shift), P2_notide
   (timing off), P2_nofc (forecast terms off), with paired comparisons, plus a once-counted mass boundary.

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
        "end_stored", "end_pool", "crew_h", "ent_floor", "ent_vel")
CAUSES = {"entrainment": "ent", "overtopping": "over", "bypass_release": "byp"}
VARIANTS = {
    "a_current_release": {},
    "b_fail_open_fuse": {"fail_open_fuse": True},
    "c_fuse_refloat_x0.5": {"fail_open_fuse": True, "refloat_mult": 0.5},
    "c_fuse_refloat_x0.2": {"fail_open_fuse": True, "refloat_mult": 0.2},
}


ABLATIONS = ("P1m", "P2_notide", "P2_nofc")
ABLATION_PAIRS = [("P2", "P1m"), ("P2", "P2_notide"), ("P2", "P2_nofc"), ("P1m", "P1"), ("P1m", "P0"),
                  ("P2_notide", "P1m"), ("P2_nofc", "P1m"), ("P2", "P1")]
ANGLES = {90: 1.0, 45: float(np.sin(np.radians(45))), 30: 0.5, 20: float(np.sin(np.radians(20)))}
ANGLE_HARDWARE = ["a_current_release", "c_fuse_refloat_x0.5"]


def run_configs(configs: dict, n_draws: int = N_DRAWS, seed: int = SEED, years: list | None = None) -> dict:
    """configs: name -> (policy, extra P switches). Per-draw totals (D,) summed over sites and years."""
    years = years or sim.HOLDOUT_YEARS
    P = sim.param_arrays(PR.draw(n_draws, seed))
    runs: dict = {n: None for n in configs}
    for y in years:
        phys = sim.physics(y, P)
        fc = RF.season_forecast(y)
        for name, (pol, extra) in configs.items():
            r = sim.run_season(phys, dict(P, **extra) if extra else P, DP.make_policy(pol, fc), fc,
                               sensor_seed=seed + y)
            part = {k: (r[k].sum(axis=-1) if r[k].ndim == 2 else r[k]) for k in KEYS}
            runs[name] = part if runs[name] is None else {k: runs[name][k] + part[k] for k in KEYS}
    return runs


def run_heldout(n_draws: int = N_DRAWS, seed: int = SEED, years: list | None = None) -> dict:
    """P0, P1, P2, the P2 fuse variants and the P2 boom-angle variants (theta90 = aliases)."""
    configs = {p: (p, {}) for p in ("P0", "P1", "P2") + ABLATIONS}
    configs.update({f"P2|{v}": ("P2", VARIANTS[v]) for v in VARIANTS if VARIANTS[v]})
    configs.update({f"P2|{h}|theta{a}": ("P2", dict(VARIANTS[h], sin_theta=s))
                    for h in ANGLE_HARDWARE for a, s in ANGLES.items() if a != 90})
    runs = run_configs(configs, n_draws, seed, years)
    runs["P2|a_current_release"] = runs["P2"]
    for h in ANGLE_HARDWARE:
        runs[f"P2|{h}|theta90"] = runs[f"P2|{h}"]
    return runs


def exposure_nominal(years: list | None = None) -> dict:
    """SIMULATED exposure, P2 with nominal parameters: share of hours and of arrived kg at |v|*sin(theta) > v50."""
    from .sites import SITE_IDS
    years = years or sim.HOLDOUT_YEARS
    P = sim.param_arrays([PR.nominal()])
    v50 = float(P["v50_ms"][0, 0])
    hrs = {a: np.zeros(len(SITE_IDS)) for a in ANGLES}
    kg = {a: np.zeros(len(SITE_IDS)) for a in ANGLES}
    n_h, arr_tot = 0, np.zeros(len(SITE_IDS))
    for y in years:
        phys = sim.physics(y, P)
        fc = RF.season_forecast(y)
        r = sim.run_season(phys, P, DP.make_policy("P2", fc), fc, sensor_seed=SEED + y, record=True)
        v, arr = np.abs(phys["v"][:, 0, :]), r["rec"]["arrived"][:, 0, :]
        n_h += v.shape[0]
        arr_tot += arr.sum(0)
        for a, s in ANGLES.items():
            fast = v * s > v50
            hrs[a] += fast.sum(0)
            kg[a] += (arr * fast).sum(0)
    out = {"v50_ms_nominal": v50, "hours_per_site": n_h}
    for a in ANGLES:
        out[f"theta{a}"] = {"share_of_hours": round(float(hrs[a].sum() / (n_h * len(SITE_IDS))), 4),
                            "share_of_arrived_kg": round(float(kg[a].sum() / arr_tot.sum()), 4)}
    out["theta90"]["by_site"] = {sid: {"share_of_hours": round(float(hrs[90][i] / n_h), 4),
                                       "share_of_arrived_kg": round(float(kg[90][i] / arr_tot[i]), 4)}
                                 for i, sid in enumerate(SITE_IDS)}
    return out


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
    out["entrainment_split"] = {p: {
        part: {"kg": dist(runs[p][k], 0), "share_of_escaped": dist(runs[p][k] / runs[p]["escaped"]),
               "share_of_entrainment": dist(runs[p][k] / runs[p]["ent"])}
        for part, k in (("floor_1_minus_emax", "ent_floor"), ("velocity_driven", "ent_vel"))}
        for p in ("P0", "P1", "P2")}
    if all(f"P2|{h}|theta{a}" in runs for h in ANGLE_HARDWARE for a in ANGLES):
        E0, F0 = runs["P2"]["escaped"], fwce(runs["P2"])
        out["boom_angle_sensitivity_P2"] = {h: {f"theta{a}": {
            "sin_theta": round(s, 4), "boom_length_factor_1_over_sin_theta": round(1 / s, 3),
            "escaped_kg": dist(runs[f"P2|{h}|theta{a}"]["escaped"], 0),
            "escaped_rel_vs_theta90": paired(runs[f"P2|{h}|theta{a}"]["escaped"], runs[f"P2|{h}|theta90"]["escaped"]),
            "escaped_rel_vs_current_a_theta90": paired(runs[f"P2|{h}|theta{a}"]["escaped"], E0),
            "fwce": dist(fwce(runs[f"P2|{h}|theta{a}"])),
            "fwce_delta_pp_vs_theta90": dist((fwce(runs[f"P2|{h}|theta{a}"]) - fwce(runs[f"P2|{h}|theta90"])) * 100, 2),
            "fwce_delta_pp_vs_current_a_theta90": dist((fwce(runs[f"P2|{h}|theta{a}"]) - F0) * 100, 2),
            "velocity_entrainment_share_of_escaped": dist(runs[f"P2|{h}|theta{a}"]["ent_vel"]
                                                          / runs[f"P2|{h}|theta{a}"]["escaped"])}
            for a, s in ANGLES.items()} for h in ANGLE_HARDWARE}
    if all(a in runs for a in ABLATIONS):
        names = ("P0", "P1", "P1m", "P2_notide", "P2_nofc", "P2")
        out["ablations"] = {
            "paired_escaped_rel_diff": {f"{a}_vs_{b}": paired(runs[a]["escaped"], runs[b]["escaped"])
                                        for a, b in ABLATION_PAIRS},
            "escaped_kg": {n: dist(runs[n]["escaped"], 0) for n in names},
            "fwce": {n: dist(fwce(runs[n])) for n in names},
            "cleared_share_of_unique_input": {n: dist(runs[n]["cleared"] / runs[n]["load"]) for n in names}}
    out["mass_boundary"] = {p: {
        "unique_input_kg": dist(runs[p]["load"], 0),
        "cleared_kg": dist(runs[p]["cleared"], 0),
        "stored_at_season_end_kg": dist(runs[p]["end_stored"], 0),
        "held_upstream_at_season_end_kg": dist(runs[p]["end_pool"], 0),
        "escaped_kg": dist(runs[p]["escaped"], 0),
        "cleared_share": dist(runs[p]["cleared"] / runs[p]["load"]),
        "retained_share": dist(runs[p]["end_stored"] / runs[p]["load"]),
        "escaped_share": dist(runs[p]["escaped"] / runs[p]["load"])} for p in ("P0", "P1", "P2")}
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
                       for n, R in sorted(runs.items()) if not n.endswith("|theta90")}
    return out


def main():
    metrics = json.loads((RESULTS / "metrics.json").read_text())
    res = summarise(run_heldout(), metrics)
    res["exposure_P2_nominal"] = exposure_nominal()
    doc = {
        "label": "SIMULATED",
        "what": "digital-twin analysis, held-out monsoons Jun-Sep 2024+2025, 4 sites summed; real forcing "
                "(ERA5 rain, archived JMA day-ahead forecast, harmonic tide), ASSUMPTION process parameters",
        "reproduce": REPRO, "git_sha_at_run": git_sha(), "n_draws": N_DRAWS, "seed": SEED,
        "years": sim.HOLDOUT_YEARS, "crew_budget": f"{DP.N_CREWS} crews x {DP.SHIFT_H} h/day, all runs",
        "p2_knobs": DP.load_knobs(),
        "definitions": {
            "range": "median and p05/p95 = central 90% scenario range across 40 sampled parameter settings "
                     "(Monte Carlo draws of the ASSUMPTION ranges); not a confidence interval",
            "paired_rel_diff": "(a - b) / b per sampled parameter setting (same setting and sensor noise); negative = "
                               "a lets less escape; draws_a_lower = number of the 40 settings where a < b",
            "policies": {"P0": "assumed fixed roster (area-weighted rotation, fixed 08:30 IST shift; not BMC's roster)",
                         "P1": "fill-fraction-ranked fixed-shift rule",
                         "P2": "mass/risk-ranked, tide- and forecast-timed policy",
                         "P1m": "ablation: sensor-only mass-ranked fixed-shift rule (greedy on sensed kg, P1's shift)",
                         "P2_notide": "ablation: P2 with tide-aware timing off (fixed 08:30 IST start)",
                         "P2_nofc": "ablation: P2 with forecast terms off (sensed kg only; timing from tide-only access)"},
            "mass_boundary": "unique input = catchment wash-off reaching the outfall (re-arrivals excluded) = escaped + "
                             "cleared by crews (removal) + stored in boom at 30 Sep (temporary retention) + held "
                             "upstream at 30 Sep; generic floating debris, not flexible packaging specifically",
            "arrived_at_boom": "contract arrived_kg: includes re-arrivals of re-floated/released debris",
            "fwce": "(cleared + stored at 30 Sep) / unique input (catchment load); each kg counted once; stored "
                    "is temporary retention, cleared_share is removal",
            "gross_captured_over_arrived": "captured_kg / arrived_kg (double-counts re-captures)",
            "tidal_refloat": "stored debris lifted on flood tide into the upstream pool; it re-arrives on the "
                             "ebb (re-exposure flux, not an escape term)",
            "flood_release": "stored debris released during bypass/high head (current hardware), into the pool",
            "fuse": "SENSITIVITY: at release only the arriving flux passes; the pocket keeps its catch",
            "refloat_mult": "SENSITIVITY: one-way pocket scales tidal re-float; x1 with the fuse equals variant b",
            "sin_theta": "SENSITIVITY: boom at angle theta to the flow; e(v) uses the normal component |v|*sin(theta), "
                         "e_max unchanged; boom length (W/sin theta), capacity, cost and loads not modelled; P2's "
                         "forecaster still assumes theta=90 (policy unchanged)",
            "ent_floor": "(1 - e_max) * arrived outside bypass: leaks even at slack water (ASSUMPTION e_max 0.70-0.95)",
            "ent_vel": "(e_max - e(v)) * arrived outside bypass: velocity-driven entrainment",
            "exposure": "P2, nominal parameters, held-out years: share of site-hours and of arrived kg with "
                        "|v|*sin(theta) > v50 (0.45 m/s nominal)",
        },
        "caveats": [
            "SIMULATED: escaped_kg is computed by the same assumed process model that the policies act on, so "
            "results show relative value under stated assumptions, not field evidence; field calibration comes "
            "in Round 2.",
            "Fuse/pocket rows are SENSITIVITY runs (assumption-driven), not evidence about real hardware.",
            "Boom-angle rows are SENSITIVITY runs (assumption-driven): boom angle is not field evidence. Angle acts "
            "only through the assumed capture curve e(|v| sin theta), so it cannot independently confirm that "
            "mechanism; v50 is transferred from oil-boom practice (UNVERIFIED ASSUMPTION).",
            "Assumed capture losses dominate this twin; boom angle and retention are candidate field experiments.",
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
