# Eval results (harness v2, inputs id d337af61e1, run at commit 5040fae, n=10000, seed=20261004)

The inputs id hashes the git trees of components/lca_engine/, data/ and eval/eval.py — stable across rebases.
Reproduce: `python3 eval/eval.py` from `ev-c2-green-auto-lca/`. Unit: g per vehicle-km (GHG indicator; see gas-basis flags).
Database: 127 records ({'verified': 107, 'derived': 20}), 20 sources.

## Arithmetic implementation verification (NOT validation: same source supplies inputs and targets)

| Scenario | Vehicle | Ours | Published | Error % |
|---|---|---|---|---|
| icct2021_implied | ice_scooter | 60.90 | 60.9 | +0.00 |
| icct2021_implied | ev_scooter | 37.54 | 37.5 | +0.12 |
| icct2021_implied | **MAPE** | | | **0.06** |
| icct2021_stated | ice_scooter | 66.52 | 60.9 | +9.23 |
| icct2021_stated | ev_scooter | 34.25 | 37.5 | -8.68 |
| icct2021_stated | **MAPE** | | | **8.955** |
| car_icct2021_replication | petrol | 226.17 | 228.0 | -0.80 |
| car_icct2021_replication | diesel | 239.45 | 245.0 | -2.26 |
| car_icct2021_replication | cng | 224.07 | 226.0 | -0.86 |
| car_icct2021_replication | bev | 185.14 | 185.0 | +0.07 |
| car_icct2021_replication | **MAPE** | | | **0.999** |
| car_icct2021_sds | petrol | 226.17 | 228.0 | -0.80 |
| car_icct2021_sds | diesel | 239.45 | 245.0 | -2.26 |
| car_icct2021_sds | cng | 224.07 | 226.0 | -0.86 |
| car_icct2021_sds | bev | 149.62 | 150.0 | -0.25 |
| car_icct2021_sds | **MAPE** | | | **1.044** |

## 2W — petrol vs electric scooter — decision and sensitivity scenarios (paired Monte Carlo, 90 % intervals)

**in2026_cea_average** [sensitivity] — Sensitivity — CO2-only grid (CEA FY2025-26 average, no CH4/N2O or upstream): understates grid emissions, so an upper bound on the EV saving — _NOT harmonized (CO2-only, GWP100-AR5, GWP20(CH4), unspecified)_

| Vehicle | Total [90 %] | vs reference: reduction [90 %] | P(lower) | Pedigree score |
|---|---|---|---|---|
| Petrol scooter 110 cc class | 64.3 [60.0 – 68.9] | reference |  | 2.1 |
| Electric scooter 2.9 kWh | 38.9 [36.7 – 41.3] | 39.5 % [33.8 – 44.5 %] | 1.000 | 1.78 |

**in2026_cea_operating_margin** [sensitivity] — Sensitivity — EV charging at CEA operating margin, CO2e (fossil-dominated proxy; not a guaranteed upper bound) — _NOT harmonized (GWP100-AR5, GWP20(CH4), unspecified)_

| Vehicle | Total [90 %] | vs reference: reduction [90 %] | P(lower) | Pedigree score |
|---|---|---|---|---|
| Petrol scooter 110 cc class | 64.3 [60.1 – 69.0] | reference |  | 2.1 |
| Electric scooter 2.9 kWh | 53.9 [51.0 – 57.5] | 16.2 % [7.8 – 23.2 %] | 0.999 | 1.76 |

**in2026_cea_build_margin** [sensitivity] — Sensitivity — EV charging at CEA build margin, CO2-only (recent-capacity proxy; no CO2e adder: BM fuel mix unknown) — _NOT harmonized (CO2-only, GWP100-AR5, GWP20(CH4), unspecified)_

| Vehicle | Total [90 %] | vs reference: reduction [90 %] | P(lower) | Pedigree score |
|---|---|---|---|---|
| Petrol scooter 110 cc class | 64.3 [60.0 – 68.9] | reference |  | 2.1 |
| Electric scooter 2.9 kWh | 28.0 [26.5 – 29.7] | 56.4 % [52.4 – 60.0 %] | 1.000 | 1.82 |

**in2026_petrol_e0** [sensitivity] — Sensitivity — petrol tailpipe as E0 fossil CO2 (IPCC 2006 defaults, no ethanol credit) — _NOT harmonized (CO2-only, GWP100-AR5, GWP20(CH4), unspecified)_

| Vehicle | Total [90 %] | vs reference: reduction [90 %] | P(lower) | Pedigree score |
|---|---|---|---|---|
| Petrol scooter 110 cc class | 66.9 [62.4 – 71.9] | reference |  | 2.31 |
| Electric scooter 2.9 kWh | 39.8 [37.7 – 42.4] | 40.5 % [34.5 – 45.5 %] | 1.000 | 1.78 |

**in2026_avg_co2e** [decision] — India 2026-grid, attributional — CEA FY2025-26 average on CO2e (AR5 GWP100, matching ICCT inputs), partial upstream (legacy 2021 ICCT vehicle data) — _NOT harmonized (GWP100-AR5, GWP20(CH4), unspecified)_

| Vehicle | Total [90 %] | vs reference: reduction [90 %] | P(lower) | Pedigree score |
|---|---|---|---|---|
| Petrol scooter 110 cc class | 64.3 [60.1 – 69.0] | reference |  | 2.1 |
| Electric scooter 2.9 kWh | 39.8 [37.7 – 42.5] | 38.1 % [32.0 – 43.2 %] | 1.000 | 1.78 |


## Car — sedan: petrol vs diesel vs CNG vs electric — decision and sensitivity scenarios (paired Monte Carlo, 90 % intervals)

**car_in2026_cea_average** [sensitivity] — Sensitivity — CO2-only grid (CEA FY2025-26 average, no CH4/N2O or upstream): understates grid emissions, so an upper bound on the BEV saving — _NOT harmonized (CO2-only, GWP100-AR5)_

| Vehicle | Total [90 %] | vs reference: reduction [90 %] | P(lower) | Pedigree score |
|---|---|---|---|---|
| Petrol sedan (6.8 L/100 km real-world) | 226.2 [202.4 – 254.1] | reference |  | 2.06 |
| Diesel sedan (6.0 L/100 km real-world) | 239.4 [214.4 – 268.6] | -5.9 % [-23.6 – 9.8 %] | 0.282 | 2.06 |
| CNG sedan (5.0 kg/100 km real-world) | 224.1 [210.8 – 269.4] | 0.9 % [-23.9 – 11.0 %] | 0.312 | 2.22 |
| Battery-electric sedan (23 kWh, 19.2 kWh/100 km at the plug) | 199.2 [170.4 – 234.5] | 11.9 % [-7.4 – 27.5 %] | 0.861 | 1.9 |

**car_in2026_cea_operating_margin** [sensitivity] — Sensitivity — BEV charging at CEA operating margin, CO2e (fossil-dominated proxy) — _harmonized_

| Vehicle | Total [90 %] | vs reference: reduction [90 %] | P(lower) | Pedigree score |
|---|---|---|---|---|
| Petrol sedan (6.8 L/100 km real-world) | 226.2 [202.6 – 253.8] | reference |  | 2.06 |
| Diesel sedan (6.0 L/100 km real-world) | 239.4 [214.4 – 269.0] | -5.9 % [-24.1 – 9.7 %] | 0.282 | 2.06 |
| CNG sedan (5.0 kg/100 km real-world) | 224.1 [210.6 – 268.7] | 0.9 % [-24.1 – 11.0 %] | 0.306 | 2.22 |
| Battery-electric sedan (23 kWh, 19.2 kWh/100 km at the plug) | 272.6 [231.4 – 326.4] | -20.5 % [-48.7 – 1.1 %] | 0.061 | 1.86 |

**car_in2026_cea_build_margin** [sensitivity] — Sensitivity — BEV charging at CEA build margin, CO2-only (recent-capacity proxy) — _NOT harmonized (CO2-only, GWP100-AR5)_

| Vehicle | Total [90 %] | vs reference: reduction [90 %] | P(lower) | Pedigree score |
|---|---|---|---|---|
| Petrol sedan (6.8 L/100 km real-world) | 226.2 [202.4 – 254.1] | reference |  | 2.06 |
| Diesel sedan (6.0 L/100 km real-world) | 239.4 [214.4 – 268.6] | -5.9 % [-23.6 – 9.8 %] | 0.282 | 2.06 |
| CNG sedan (5.0 kg/100 km real-world) | 224.1 [210.8 – 269.4] | 0.9 % [-23.9 – 11.0 %] | 0.312 | 2.22 |
| Battery-electric sedan (23 kWh, 19.2 kWh/100 km at the plug) | 145.9 [126.4 – 169.6] | 35.5 % [22.2 – 46.3 %] | 1.000 | 1.94 |

**car_in2026_avg_co2e** [decision] — India 2026-grid, attributional — CEA FY2025-26 average on CO2e (AR5 GWP100, matching ICCT inputs), partial upstream (legacy 2021 ICCT sedan data) — _harmonized_

| Vehicle | Total [90 %] | vs reference: reduction [90 %] | P(lower) | Pedigree score |
|---|---|---|---|---|
| Petrol sedan (6.8 L/100 km real-world) | 226.2 [202.6 – 253.8] | reference |  | 2.06 |
| Diesel sedan (6.0 L/100 km real-world) | 239.4 [214.4 – 269.0] | -5.9 % [-24.1 – 9.7 %] | 0.282 | 2.06 |
| CNG sedan (5.0 kg/100 km real-world) | 224.1 [210.6 – 268.7] | 0.9 % [-24.1 – 11.0 %] | 0.306 | 2.22 |
| Battery-electric sedan (23 kWh, 19.2 kWh/100 km at the plug) | 203.5 [174.4 – 241.6] | 10.0 % [-10.1 – 25.6 %] | 0.808 | 1.89 |

## Independent plausibility check — Indian cars (NOT validation)

Our central sedan case (`car_in2026_avg_co2e`) against independent, non-ICCT Indian car LCAs (TERI 2026, IIT Guwahati 2025, IIT Kanpur 2023): different vehicles, lifetimes (150,000–200,000 km), boundaries and grid years.

| Powertrain | Ours [90 %] | Independent range (n) | Central inside? |
|---|---|---|---|
| petrol | 226.2 [202.6 – 253.8] | 183.6 – 247.0 (6) | yes |
| diesel | 239.5 [214.4 – 269.0] | 271.5 – 271.5 (1) | NO |
| cng | 224.1 [210.6 – 268.7] | 167.9 – 209.1 (2) | NO |
| bev | 203.5 [174.5 – 241.6] | 156.0 – 265.0 (7) | yes |

Pedigree score = elasticity-weighted mean pedigree score (1 best … 5 worst), a screening indicator.
Importance = normalized squared Spearman rank correlation (screening, not a variance decomposition) — see latest.json.
