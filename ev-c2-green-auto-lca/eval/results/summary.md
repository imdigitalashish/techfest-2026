# Eval results (harness v2, code commit 8d71b2a, n=10000, seed=20261004)

Reproduce: `python3 eval/eval.py` from `ev-c2-green-auto-lca/`. Unit: g per vehicle-km (GHG indicator; see gas-basis flags).
Database: 88 records ({'verified': 73, 'derived': 15}), 9 sources.

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

**in2026_cea_average** [decision] — India 2026-grid, attributional — CEA FY2025-26 average (legacy 2021 ICCT vehicle data) — _NOT harmonized (CO2-only, GWP100, GWP20(CH4), unspecified)_

| Vehicle | Total [90 %] | vs reference: reduction [90 %] | P(lower) | Pedigree score |
|---|---|---|---|---|
| Petrol scooter 110 cc class | 64.3 [60.0 – 68.9] | reference |  | 2.1 |
| Electric scooter 2.9 kWh | 38.9 [36.7 – 41.3] | 39.5 % [33.8 – 44.5 %] | 1.000 | 1.78 |

**in2026_cea_operating_margin** [sensitivity] — Sensitivity — EV charging at CEA operating margin (fossil-dominated proxy, upper bound) — _NOT harmonized (CO2-only, GWP100, GWP20(CH4), unspecified)_

| Vehicle | Total [90 %] | vs reference: reduction [90 %] | P(lower) | Pedigree score |
|---|---|---|---|---|
| Petrol scooter 110 cc class | 64.3 [60.0 – 68.9] | reference |  | 2.1 |
| Electric scooter 2.9 kWh | 52.6 [49.6 – 55.8] | 18.2 % [10.5 – 25.1 %] | 1.000 | 1.75 |

**in2026_cea_build_margin** [sensitivity] — Sensitivity — EV charging at CEA build margin (recent-capacity proxy) — _NOT harmonized (CO2-only, GWP100, GWP20(CH4), unspecified)_

| Vehicle | Total [90 %] | vs reference: reduction [90 %] | P(lower) | Pedigree score |
|---|---|---|---|---|
| Petrol scooter 110 cc class | 64.3 [60.0 – 68.9] | reference |  | 2.1 |
| Electric scooter 2.9 kWh | 28.0 [26.5 – 29.7] | 56.4 % [52.4 – 60.0 %] | 1.000 | 1.82 |

**in2026_petrol_e0** [sensitivity] — Sensitivity — petrol tailpipe as E0 fossil CO2 (IPCC 2006 defaults, no ethanol credit) — _NOT harmonized (CO2-only, GWP100, GWP20(CH4), unspecified)_

| Vehicle | Total [90 %] | vs reference: reduction [90 %] | P(lower) | Pedigree score |
|---|---|---|---|---|
| Petrol scooter 110 cc class | 66.9 [62.4 – 71.8] | reference |  | 2.31 |
| Electric scooter 2.9 kWh | 38.9 [36.7 – 41.3] | 41.8 % [36.4 – 46.9 %] | 1.000 | 1.78 |


## Car — sedan: petrol vs diesel vs CNG vs electric — decision and sensitivity scenarios (paired Monte Carlo, 90 % intervals)

**car_in2026_cea_average** [decision] — India 2026-grid, attributional — CEA FY2025-26 average (legacy 2021 ICCT vehicle data) — _NOT harmonized (CO2-only, GWP100)_

| Vehicle | Total [90 %] | vs reference: reduction [90 %] | P(lower) | Pedigree score |
|---|---|---|---|---|
| Petrol sedan (6.8 L/100 km real-world) | 226.2 [201.9 – 253.7] | reference |  | 2.06 |
| Diesel sedan (6.0 L/100 km real-world) | 239.4 [214.2 – 269.3] | -5.9 % [-24.5 – 9.8 %] | 0.273 | 2.06 |
| CNG sedan (5.0 kg/100 km real-world) | 224.1 [210.9 – 269.4] | 0.9 % [-24.8 – 11.1 %] | 0.297 | 2.22 |
| Battery-electric sedan (23 kWh, 19.2 kWh/100 km at the plug) | 199.2 [170.6 – 234.4] | 11.9 % [-7.7 – 27.3 %] | 0.853 | 1.9 |

**car_in2026_cea_operating_margin** [sensitivity] — Sensitivity — BEV charging at CEA operating margin (fossil-dominated proxy) — _NOT harmonized (CO2-only, GWP100)_

| Vehicle | Total [90 %] | vs reference: reduction [90 %] | P(lower) | Pedigree score |
|---|---|---|---|---|
| Petrol sedan (6.8 L/100 km real-world) | 226.2 [201.9 – 253.7] | reference |  | 2.06 |
| Diesel sedan (6.0 L/100 km real-world) | 239.4 [214.2 – 269.3] | -5.9 % [-24.5 – 9.8 %] | 0.273 | 2.06 |
| CNG sedan (5.0 kg/100 km real-world) | 224.1 [210.9 – 269.4] | 0.9 % [-24.8 – 11.1 %] | 0.297 | 2.22 |
| Battery-electric sedan (23 kWh, 19.2 kWh/100 km at the plug) | 266.4 [225.9 – 316.2] | -17.8 % [-45.0 – 3.6 %] | 0.091 | 1.86 |

**car_in2026_cea_build_margin** [sensitivity] — Sensitivity — BEV charging at CEA build margin (recent-capacity proxy) — _NOT harmonized (CO2-only, GWP100)_

| Vehicle | Total [90 %] | vs reference: reduction [90 %] | P(lower) | Pedigree score |
|---|---|---|---|---|
| Petrol sedan (6.8 L/100 km real-world) | 226.2 [201.9 – 253.7] | reference |  | 2.06 |
| Diesel sedan (6.0 L/100 km real-world) | 239.4 [214.2 – 269.3] | -5.9 % [-24.5 – 9.8 %] | 0.273 | 2.06 |
| CNG sedan (5.0 kg/100 km real-world) | 224.1 [210.9 – 269.4] | 0.9 % [-24.8 – 11.1 %] | 0.297 | 2.22 |
| Battery-electric sedan (23 kWh, 19.2 kWh/100 km at the plug) | 145.9 [126.6 – 169.9] | 35.5 % [22.0 – 46.1 %] | 1.000 | 1.94 |

Pedigree score = elasticity-weighted mean pedigree score (1 best … 5 worst), a screening indicator.
Importance = normalized squared Spearman rank correlation (screening, not a variance decomposition) — see latest.json.
