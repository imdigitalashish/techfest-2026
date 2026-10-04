# Eval results (commit d5df843, n=10000, seed=20261004)

Reproduce: `python3 eval/eval.py` from `ev-c2-green-auto-lca/`. Units: g CO2e per vehicle-km.

## Replication of ICCT (2021) Table 1 — Indian scooters

| Scenario | ICE ours / published | BEV ours / published | MAPE % | Reduction ours / published |
|---|---|---|---|---|
| icct2021_implied | 60.90 / 60.9 | 37.54 / 37.5 | 0.06 | 38.4% / 38.4% |
| icct2021_stated | 66.52 / 60.9 | 34.25 / 37.5 | 8.955 | 48.5% / 38.4% |

## India 2026 case study (paired Monte Carlo, 90% intervals)

| Scenario | ICE total [90%] | BEV total [90%] | Reduction [90%] | P(BEV<ICE) | DQI ICE / BEV |
|---|---|---|---|---|---|
| in2026_cea_average | 62.95 [57.59–68.99] | 39.71 [36.9–42.84] | 36.9% [29.2–43.8%] | 1.0 | 2.2 / 1.62 |
| in2026_cea_operating_margin | 62.95 [57.59–68.99] | 54.15 [50.18–58.54] | 14.0% [3.3–23.5%] | 0.984 | 2.2 / 1.58 |
| in2026_cea_build_margin | 62.95 [57.59–68.99] | 28.23 [26.3–30.4] | 55.2% [49.8–60.0%] | 1.0 | 2.2 / 1.66 |

DQI = elasticity-weighted mean pedigree score (1 best … 5 worst).

## Top variance drivers of the reduction (in2026_cea_average)

- `vehicle.2w.scooter_ice.fuel_l_per_100km.icct2021_table_implied` — 34.9% of rank-variance
- `vehicle.2w.scooter_ev.elec_kwh_per_100km.icct2021_table_implied` — 29.9% of rank-variance
- `fuels.petrol.density.unsd2020` — 16.7% of rank-variance
- `energy.electricity.in.grid_wavg_generation.fy2025_26` — 8.5% of rank-variance
- `fuels.petrol.co2_per_energy.ipcc2006` — 4.1% of rank-variance
