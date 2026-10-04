# twin_sim — site-level digital twin + dispatch (C1–C4, C9, C10)

This package builds a digital twin of 4 real Mumbai outfall sites, driven by **real** hourly rain, **real** archived day-ahead forecasts and **real** tide data. The plastic load, hydraulics, booms, sensors and crews in the twin are **SIMULATED**. It compares three crew-dispatch policies at equal crew-hours, using Monte Carlo draws over every assumption.

**Full write-up:** [`research/components/twin.md`](../../research/components/twin.md) covers sources, equations, the parameter table, results and limitations.

## Reproduce
```bash
cd innovatex-t3-coastal-plastic/components
pip install utide                                   # numpy, pandas, pydantic, pytest assumed
python -m twin_sim.fetch_forcing                    # Open-Meteo ERA5 rain, JMA day-ahead fc, marine sea level -> data/
python -m pytest twin_sim/tests -q                  # contracts + mass balance + equal crew-hours (8 tests)
python twin_sim/autoresearch/eval.py                # FROZEN tuning metric (2019-2023) for current P2
python twin_sim/autoresearch/ratchet.py [--round2]  # keep-if-better loop over P2 knobs, logs results.tsv
python -m twin_sim.run                              # held-out 2024-2025 comparison + results/bundle_part.json
python -m twin_sim.run --bundle-only                # rebuild the bundle from committed metrics.json
python -m twin_sim.report                           # regenerate the numeric blocks in twin.md + this README (--check verifies)
python -m twin_sim.analysis                         # SIMULATED escape causes, paired comparisons, FWCE, ablations, fuse + boom-angle SENSITIVITY -> results/analysis.json
```

## Outputs (read by the dashboard)
- `results/bundle_part.json` (about 3.9 MB). It has the keys `sites`, `forcing`, `interceptor`, `forecasts`, `plans`, `telemetry` (`simulated=true`) and `metrics`, and validates as `contracts.DashboardBundle`. It covers monsoon 2025 hourly, all 4 sites, from the P2 nominal run:
  - Forecasts: 24 h every day, plus 48 h on the 7 window days.
  - Plans: P0, P1 and P2 every day, issued 00 UTC.
  - Telemetry: sensed fill hourly in the window, 6-hourly elsewhere.
  - Window: the wettest held-out week, 2025-08-14 → 08-20 UTC (`metrics["twin_sim.window"]`; see twin.md §9).
- `results/metrics.json`: held-out and tuning comparisons, P2 knobs, tide-fit skill and the reproduce command.
- `results/analysis.json` (about 20 KB, label SIMULATED): escape split by cause, paired per-draw differences (P2 vs P1: −5.2% [−15.9%, −0.8%], 39/40 draws, after the 17:25 IST leak-free tide refit), FWCE per policy, and the fail-open fuse / one-way pocket SENSITIVITY. See twin.md §6.

## Headline (SIMULATED, held-out Jun–Sep 2024+2025, 40 sampled parameter settings)
Each figure is escaped kg vs P0: the median reduction, then the central 90% scenario range across sampled parameter settings (p05–p95; not a confidence interval).

<!-- twin_sim.report:headline -->

| policy | median reduction | central 90% scenario range | parameter settings (of 40) better than P0 |
|---|---|---|---|
| P1 fill-fraction-ranked fixed-shift rule | −3.0% | [−5.7%, +0.1%] | 3/40 |
| P2 mass/risk-ranked, tide- and forecast-timed policy | +1.9% | [−1.3%, +12.5%] | 28/40 |

<!-- /twin_sim.report:headline -->

<!-- twin_sim.report:headline_note -->

Captured fraction: P0 0.459, P1 0.446, P2 0.491. Tide: frozen UTide fit on 2022-11-23..2023-12-31 only (no held-out-year sea level); see twin.md §1 and §4.

<!-- /twin_sim.report:headline_note -->

## Modules → contracts
`sites.py` (Site) · `forcing.py` (C1 ForcingSeries) · `catchment_load.py` (C2 LoadSeries) · `hydraulics.py` (C3 HydraulicSeries) · `interceptor.py` (C4 InterceptorSeries) · `risk_forecaster.py` (C9 SiteForecast) · `dispatch.py` (C10 DispatchPlan) · `sim.py` (season simulator) · `params.py` (parameter table) · `run.py` (bundle + metrics).

## Assumptions recorded during the overnight run (no user input)
- Sites:
  - Mithi mouth, Oshiwara→Malad Creek and Dahisar use OSM downstream nodes.
  - Trombay uses an approximate OSM node: no "Mahul Creek" object was found.
  - Catchment areas, boom sizes and channel widths are ASSUMPTIONS.
- Rain is ERA5 at 0.25°, so site pairs share cells. The forecast is JMA GSM `previous_day1`, the only probed model that is archived for both 2019 and 2024.
- Tide is a frozen UTide fit to Open-Meteo Marine model sea level, 2022-11-23 → 2023-12-31 only, so no held-out-year data enters it (the marine series is empty before 2022-11). It predicts 2019–2025. Out-of-sample skill against 2024–25 model sea level is RMSE 0.093–0.095 m (`data/tide_fit.json`). The P2 knobs were tuned with an earlier fit through 2025-09 and are kept unchanged.
- Crew budget is 2 crews × 8 h/day for 4 sites, in daylight shifts. P0 is an assumed area-weighted fixed roster, our proxy rather than BMC's actual roster.
- `results/metrics.json` records `git_sha_at_run`, which is HEAD at run time. The final numbers come from the causal-forecast fix that is committed together with them.
- The ratchet's pass 2 repeated pass 1 deterministically. It was aborted after 3 runs; the duplicate rows were removed and a note left in `results.tsv`.
