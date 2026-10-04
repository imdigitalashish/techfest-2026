"""End-to-end run: held-out policy comparison (Monte Carlo) + dashboard bundle part.

Reproduce:  cd innovatex-t3-coastal-plastic/components && python -m twin_sim.run
Writes twin_sim/results/metrics.json and twin_sim/results/bundle_part.json (validated with contracts.py)."""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timedelta, timezone

import numpy as np

from . import dispatch as DP
from . import forcing as FO
from . import interceptor as IC
from . import params as PR
from . import risk_forecaster as RF
from . import sim
from ._paths import DATA, RESULTS, C
from .sites import get_sites

N_DRAWS = 40
SEED = 20261004
REPRO = "cd innovatex-t3-coastal-plastic/components && python -m twin_sim.run"
POLICIES = ["P0", "P1", "P2"]
TELE_STEP_H = 6          # simulated telemetry every 6 h keeps bundle_part.json under 5 MB


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def q(x, p):
    return float(np.percentile(x, p))


def compare(years: list[int], n_draws: int = N_DRAWS) -> dict:
    res = {p: sim.evaluate(p, years, n_draws, SEED) for p in POLICIES}
    out = {}
    for p in POLICIES:
        r = res[p]
        red = 1.0 - r["escaped"] / res["P0"]["escaped"]
        out[p] = {
            "escaped_kg_median": round(q(r["escaped"], 50), 0),
            "escaped_kg_p05": round(q(r["escaped"], 5), 0), "escaped_kg_p95": round(q(r["escaped"], 95), 0),
            "reduction_vs_P0_median": round(q(red, 50), 4),
            "reduction_vs_P0_p05": round(q(red, 5), 4), "reduction_vs_P0_p95": round(q(red, 95), 4),
            "draws_better_than_P0": int((red > 0).sum()),
            "captured_fraction_median": round(q(1 - r["escaped"] / r["load"], 50), 4),
            "cleared_kg_median": round(q(r["cleared"], 50), 0),
            "overflow_site_hours_median": round(q(r["overflow_h"], 50), 1),
            "bypass_site_hours_median": round(q(r["bypass_h"], 50), 1),
            "crew_hours": float(r["crew_h"][0]),
            "load_kg_median": round(q(r["load"], 50), 0),
        }
        assert np.allclose(r["crew_h"], res["P0"]["crew_h"]), "crew-hours differ between policies"
    return out


def nominal_2025(policy: str = "P2"):
    P = sim.param_arrays([PR.nominal()])
    phys = sim.physics(2025, P)
    fc = RF.season_forecast(2025)
    r = sim.run_season(phys, P, DP.make_policy(policy, fc), fc, sensor_seed=SEED, record=True)
    return P, phys, fc, r


WINDOW_DAYS = 7


def wettest_window(year: int = 2025, days: int = WINDOW_DAYS) -> tuple[int, float]:
    """Start day (00 UTC-aligned) of the `days`-day window with the most ERA5 rain, mean over the 4 sites."""
    s = FO.season(year)
    daily = s.rain.mean(axis=1)[: (len(s.t) // 24) * 24].reshape(-1, 24).sum(1)
    sums = np.convolve(daily, np.ones(days), "valid")
    d0 = int(np.argmax(sums))
    return d0, float(sums[d0])


def day2_forecast(t_index, sids, year: int = 2025) -> np.ndarray:
    import pandas as pd
    df = pd.read_csv(DATA / f"fc_day2_{year}.csv.gz")
    df["time"] = pd.to_datetime(df["time"], utc=True)
    return df.pivot(index="time", columns="site_id", values="fc2_rain_mm_h")[sids].reindex(t_index).fillna(0.0).to_numpy()


def bundle(metrics: dict) -> dict:
    sites = get_sites()
    sids = [s.site_id for s in sites]
    runs = {p: nominal_2025(p) for p in POLICIES}
    P, phys, fc, r = runs["P2"]
    rec = r["rec"]
    t = list(phys["t"].to_pydatetime())
    src = f"component:twin_sim@{git_sha()} nominal parameters, policy P2, monsoon 2025"
    forcing = [FO.forcing_series(2025, i) for i in range(len(sids))]
    inter = [IC.interceptor_series(sid, t, {k: rec[k][:, 0, i] for k in rec}, float(P["capacity_kg"][0, i]), src)
             for i, sid in enumerate(sids)]
    nd = len(t) // 24
    d0, wsum = wettest_window()
    window = range(d0, min(d0 + WINDOW_DAYS, nd))
    fc2 = day2_forecast(phys["t"], sids)
    forecasts, plans = [], []
    for d in range(nd):
        f = rec["fill_obs"][d * 24, 0]
        forecasts += RF.site_forecasts(fc, d, f, sids)
        if d in window:
            forecasts += RF.horizon_forecasts(fc, d, f, sids, 48, fc2)
        for p in POLICIES:
            rp = runs[p][3]
            plans.append(DP.dispatch_plan(p, d, rp["plans"][d][0], fc, sids, rp["rec"]["fill_obs"][d * 24, 0]))
    w_hours = set(range(window.start * 24, window.stop * 24))
    hours = sorted(set(range(0, len(t), TELE_STEP_H)) | w_hours)
    tele = []
    rng = np.random.default_rng(SEED)
    sim_prov = C.Provenance(kind="simulated", source=src, notes="SIMULATED sensor")
    used_prov = C.Provenance(kind="simulated", source=src,
                             notes="SIMULATED sensor; at 00 UTC this is the exact reading the P2 dispatcher used")
    for i, sid in enumerate(sids):
        prev = -TELE_STEP_H
        for h in hours:
            st = float(rec["stored"][h, 0, i])
            at_decision = h % 24 == 0
            fill = (float(rec["fill_obs"][h, 0, i]) if at_decision else
                    float(np.clip(st / P["capacity_kg"][0, i] + rng.normal(0, P["fill_noise_sd"][0, i]), 0, 1)))
            arr = float(rec["arrived"][max(prev + 1, 0):h + 1, 0, i].sum())
            step = h - prev
            prev = h
            items = int(round(arr / P["kg_per_item"][0, i]))
            tele.append(C.SiteTelemetry(
                site_id=sid, t=t[h], simulated=True,
                water_level_m=round(float(phys["level"][h, 0, i] + rng.normal(0, 0.02)), 3),
                rain_mm_last_h=round(float(phys["rain"][h, i]), 2),
                fill=C.FillEstimate(site_id=sid, t=t[h], fill_fraction=round(fill, 3), method="simulated",
                                    confidence=0.8, provenance=used_prov if at_decision else sim_prov),
                flux=C.FluxEstimate(site_id=sid, t_start=t[h] - timedelta(hours=step), t_end=t[h],
                                    items_crossed=items, items_per_min=round(items / (60 * step), 3), est_kg=round(arr, 2),
                                    est_kg_ci90=(round(arr * 0.6, 2), round(arr * 1.5, 2)), method="simulated",
                                    provenance=sim_prov)))
    ws, we = t[window.start * 24], t[window.stop * 24 - 1]
    metrics = dict(metrics, **{"twin_sim.window": {
        "label": "SIMULATED (window choice uses real ERA5 rain)",
        "start_utc": ws.strftime("%Y-%m-%dT%H:%MZ"), "end_utc": we.strftime("%Y-%m-%dT%H:%MZ"),
        "days": float(len(window)), "rain_mm_7d_mean_of_4_sites": round(wsum, 1),
        "selection": "held-out 2025 Jun-Sep: 00 UTC-aligned 7-day window with the most ERA5 rain (mean of 4 sites)",
        "forecasts": "horizon 24 h every day (P2 policy forecaster); plus 48 h on window days (day-1 + day-2 archived "
                     "JMA GSM, all issued before 00 UTC); issued 00 UTC",
        "plans": "P0, P1, P2 every day, issued 00 UTC, each from its own nominal-parameter run",
        "sensed_fill": "telemetry[].fill.fill_fraction: hourly in the window, 6-hourly elsewhere; at 00 UTC = the reading "
                       "the P2 dispatcher used",
        "true_fill": "interceptor[].fill_fraction (hourly, P2 nominal run)"}})
    b = C.DashboardBundle(generated_at=datetime.now(timezone.utc), git_sha=git_sha(), sites=sites, forcing=forcing,
                          interceptor=inter, forecasts=forecasts, plans=plans, telemetry=tele, metrics=metrics,
                          disclaimers=["Values marked SIMULATED come from the digital twin, not from field hardware.",
                                       "Rain: ERA5 reanalysis (real). Forecasts use archived real JMA GSM runs issued "
                                       "before each 00 UTC decision. Tide: harmonic prediction from a fit to Open-Meteo "
                                       "Marine model sea level 2022-11-23..2023-12-31 (model data, not a gauge).",
                                       "Interceptor and telemetry: twin with nominal ASSUMPTION parameters, policy P2, "
                                       "monsoon 2025 (held-out year). Plans: P0, P1, P2, each from its own nominal run."])
    return json.loads(b.model_dump_json())


def main():
    import sys
    RESULTS.mkdir(exist_ok=True)
    fit = json.loads((DATA / "tide_fit.json").read_text())
    if "--bundle-only" in sys.argv:          # rebuild the bundle from the committed metrics.json (no re-evaluation)
        held = json.loads((RESULTS / "metrics.json").read_text())["heldout_2024_2025"]
        write_bundle(held, fit)
        return
    held = compare(sim.HOLDOUT_YEARS)
    tune = compare(sim.TUNE_YEARS)
    knobs = DP.load_knobs()
    metrics_full = {
        "metric": "escaped_kg summed over 4 sites and the held-out monsoons (Jun-Sep 2024+2025); "
                  "relative reduction vs P0 per sampled parameter setting (Monte Carlo draw); median and central 90% "
                  "scenario range across sampled parameter settings (p05-p95; not a confidence interval)",
        "n_draws": N_DRAWS, "seed": SEED, "crew_budget": f"{DP.N_CREWS} crews x {DP.SHIFT_H} h/day, all policies",
        "heldout_2024_2025": held, "tuning_2019_2023": tune, "p2_knobs": knobs,
        "tide_fit": {k: {"fit_period": v["fit_period"],
                         "variance_explained": round(v["variance_explained"], 4), "rmse_m": round(v["rmse_m"], 3),
                         "flat_keys_are": "in-sample fit residual (fit window); see out_of_sample_2024_2025",
                         "in_sample": v["in_sample"], "out_of_sample_2024_2025": v["out_of_sample_2024_2025"],
                         "out_of_sample_jjas_2024_2025": v["out_of_sample_jjas_2024_2025"]}
                     for k, v in fit.items()},
        "tide_fit_note": "UTide fit on Open-Meteo Marine model sea level 2022-11-23..2023-12-31 only (no held-out-"
                         "year data); P2 knobs were tuned on 2019-2023 with the superseded fit (2022-11..2025-09) "
                         "and are kept unchanged",
        "reproduce": REPRO, "git_sha_at_run": git_sha(),
    }
    (RESULTS / "metrics.json").write_text(json.dumps(metrics_full, indent=1))
    write_bundle(held, fit)


def write_bundle(held: dict, fit: dict):
    flat = {"twin_sim.dispatch": {
        **{f"{p}_reduction_vs_P0_median": held[p]["reduction_vs_P0_median"] for p in ("P1", "P2")},
        **{f"{p}_reduction_vs_P0_p05": held[p]["reduction_vs_P0_p05"] for p in ("P1", "P2")},
        **{f"{p}_reduction_vs_P0_p95": held[p]["reduction_vs_P0_p95"] for p in ("P1", "P2")},
        **{f"{p}_escaped_kg_median": held[p]["escaped_kg_median"] for p in POLICIES},
        **{f"{p}_captured_fraction_median": held[p]["captured_fraction_median"] for p in POLICIES},
        **{f"{p}_overflow_site_hours_median": held[p]["overflow_site_hours_median"] for p in POLICIES},
        "n_draws": float(N_DRAWS), "heldout": "Jun-Sep 2024+2025 (SIMULATED twin, real forcing)", "reproduce": REPRO},
        "twin_sim.forcing": {**{f"tide_fit_var_expl_{k}": round(v["variance_explained"], 4) for k, v in fit.items()},
                             **{f"tide_oos_var_expl_{k}": v["out_of_sample_2024_2025"]["variance_explained"]
                                for k, v in fit.items()},
                             **{f"tide_oos_rmse_m_{k}": v["out_of_sample_2024_2025"]["rmse_m"] for k, v in fit.items()},
                             "tide_fit_window": "2022-11-23..2023-12-31 (out-of-sample = 2024-01..2025-09)",
                             "reproduce": "cd innovatex-t3-coastal-plastic/components && python -m twin_sim.fetch_forcing"}}
    b = bundle(flat)
    path = RESULTS / "bundle_part.json"
    path.write_text(json.dumps(b, separators=(",", ":")))
    print(json.dumps({p: {k: held[p][k] for k in ("escaped_kg_median", "reduction_vs_P0_median",
                                                     "reduction_vs_P0_p05", "reduction_vs_P0_p95",
                                                     "captured_fraction_median", "overflow_site_hours_median")}
                      for p in POLICIES}))
    print("bundle MB %.2f" % (path.stat().st_size / 1e6))


if __name__ == "__main__":
    main()
