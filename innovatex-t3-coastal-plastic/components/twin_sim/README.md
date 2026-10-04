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
```

## Outputs (read by the dashboard)
- `results/bundle_part.json` (3.3 MB). It has the keys `sites`, `forcing`, `interceptor`, `forecasts`, `plans` (P2 and P0, daily), `telemetry` (every 6 h, `simulated=true`) and `metrics`. Coverage is monsoon 2025, hourly, all 4 sites, from a nominal-parameter P2 run. The whole file validates as `contracts.DashboardBundle`.
- `results/metrics.json`: held-out and tuning comparisons, P2 knobs, tide-fit skill and the reproduce command.

## Headline (SIMULATED, held-out Jun–Sep 2024+2025, 40 draws)
Each figure is escaped kg vs P0: median reduction, then the 90% interval.

| policy | median reduction | 90% interval | draws better than P0 |
|---|---|---|---|
| P1 (fill-threshold) | −3.1% | [−6.0%, −0.01%] | 2/40 |
| P2 (forecast + tide-aware) | +2.1% | [−1.5%, +12.5%] | 28/40 |

Captured fraction: P0 0.461, P1 0.444, P2 0.492. These are the corrected numbers after the causal-forecast fix; the first held-out run is disclosed in twin.md §4. Tide-aware shift timing is the main lever: ablating it raises the tuning metric by 3.7%. Forecast terms add 0.5% or less.

## Modules → contracts
`sites.py` (Site) · `forcing.py` (C1 ForcingSeries) · `catchment_load.py` (C2 LoadSeries) · `hydraulics.py` (C3 HydraulicSeries) · `interceptor.py` (C4 InterceptorSeries) · `risk_forecaster.py` (C9 SiteForecast) · `dispatch.py` (C10 DispatchPlan) · `sim.py` (season simulator) · `params.py` (parameter table) · `run.py` (bundle + metrics).

## Assumptions recorded during the overnight run (no user input)
- Sites:
  - Mithi mouth, Oshiwara→Malad Creek and Dahisar use OSM downstream nodes.
  - Trombay uses an approximate OSM node: no "Mahul Creek" object was found.
  - Catchment areas, boom sizes and channel widths are ASSUMPTIONS.
- Rain is ERA5 at 0.25°, so site pairs share cells. The forecast is JMA GSM `previous_day1`, the only probed model that is archived for both 2019 and 2024.
- Tide is a UTide fit to Open-Meteo Marine sea level from 2022-11 onward (the marine series is empty earlier), predicted back to 2019.
- Crew budget is 2 crews × 8 h/day for 4 sites, in daylight shifts. P0 is an area-weighted fixed rotation, which is our proxy for the status quo.
- `results/metrics.json` records `git_sha_at_run`, which is HEAD at run time. The final numbers come from the causal-forecast fix that is committed together with them.
- The ratchet's pass 2 repeated pass 1 deterministically. It was aborted after 3 runs; the duplicate rows were removed and a note left in `results.tsv`.
