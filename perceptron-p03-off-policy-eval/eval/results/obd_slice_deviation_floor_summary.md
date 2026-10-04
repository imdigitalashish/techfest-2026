# Real OBD check on large slices — results (REAL data; campaign All)

Implements [`preregistration_obd.md`](../preregistration_obd.md) (registered 2026-10-04 13:06:47 IST, before these results). Reproduce: see the header of `eval/run_obd_slice.py`.

**DEVIATION RUN (`--floor_start_to_hour`, decided after seeing the pre-registered results):** the pre-registered W started at the first BTS row, 47 ms after midnight, so 2019-11-24 was not a whole day and the secondary analysis had one day pair. Here W starts at 00:00, which adds the 2019-11-24 pairs. Everything else is identical.

Window W: 2019-11-24T00:00:00.000000000 → 2019-11-27T12:00:00.000000000 UTC (84 hours; 0 dropped for < 1,000 BTS rows). Rows in W: Random 660,907 · BTS 5,956,296. Items: 80.

## Analysis 1 — did the deployed BTS change during W?

**Pre-registered decision:** CHANGED (20/20 top cells have max/min 6-hour median propensity ≥ 1.5; median ratio 16.06; median |Spearman ρ| with time 0.18; 14 buckets).
Distinct logged propensity values per cell-hour (top-5 cells, up to 48 hours each): median 24. Correlation of the W-average empirical (item, position) frequency with the static-prior Monte Carlo: 0.631.

| item | position | BTS rows | min 6h-median ps | max 6h-median ps | max/min | Spearman ρ vs time |
|---|---|---|---|---|---|---|
| 51 | 2 | 304,984 | 0.0314 | 0.3541 | 11.26 | +0.20 |
| 51 | 3 | 258,770 | 0.0532 | 0.2602 | 4.90 | +0.28 |
| 51 | 1 | 251,235 | 0.0111 | 0.3596 | 32.50 | +0.29 |
| 61 | 3 | 228,225 | 0.0148 | 0.2560 | 17.33 | -0.56 |
| 61 | 2 | 196,852 | 0.0147 | 0.1967 | 13.41 | -0.50 |
| 7 | 1 | 149,728 | 0.0065 | 0.6351 | 97.93 | -0.14 |
| 7 | 3 | 137,857 | 0.0187 | 0.1682 | 9.01 | -0.03 |
| 7 | 2 | 136,674 | 0.0116 | 0.2387 | 20.62 | -0.03 |
| 59 | 3 | 134,013 | 0.0092 | 0.1893 | 20.46 | +0.48 |
| 59 | 2 | 133,214 | 0.0048 | 0.2404 | 49.61 | +0.43 |
| 59 | 1 | 123,544 | 0.0078 | 0.3832 | 49.41 | +0.27 |
| 61 | 1 | 117,186 | 0.0051 | 0.3193 | 62.18 | -0.48 |
| 39 | 3 | 114,215 | 0.0193 | 0.1707 | 8.83 | +0.10 |
| 39 | 2 | 106,599 | 0.0115 | 0.1703 | 14.79 | +0.11 |
| 63 | 2 | 106,419 | 0.0195 | 0.2271 | 11.62 | +0.05 |
| 49 | 1 | 106,052 | 0.0036 | 0.7929 | 219.04 | +0.15 |
| 63 | 1 | 101,855 | 0.0202 | 0.2833 | 13.99 | +0.05 |
| 63 | 3 | 101,689 | 0.0170 | 0.1627 | 9.54 | +0.05 |
| 39 | 1 | 94,073 | 0.0069 | 0.2399 | 34.54 | +0.13 |
| 35 | 3 | 89,156 | 0.0153 | 0.1460 | 9.51 | -0.42 |

## Analysis 2 — standard protocol: V(BTS) from Random logs vs BTS on-policy CTR (same window)

**Truth (BTS on-policy CTR in W):** 0.00489 ± 0.00006 (95%). Random's own CTR in W: 0.00344.

| evaluation policy | estimator | V̂(BTS) | 95% CI (bootstrap SE) | relative error | 95% CI of V̂ − truth | consistent? | ESS / n |
|---|---|---|---|---|---|---|---|
| P-static | IPW | 0.00494 | 0.00449–0.00540 | 1.1% | -0.00040…+0.00051 | yes | 106,990 / 660,907 |
| P-static | SNIPW | 0.00491 | 0.00447–0.00536 | 0.5% | -0.00043…+0.00048 | yes | 106,990 / 660,907 |
| P-static | DM | 0.00471 | 0.00471–0.00471 | 3.7% | -0.00024…-0.00013 | NO | 106,990 / 660,907 |
| P-static | DR | 0.00490 | 0.00445–0.00535 | 0.2% | -0.00045…+0.00046 | yes | 106,990 / 660,907 |
| P-hourly | IPW | 0.00497 | 0.00450–0.00544 | 1.6% | -0.00039…+0.00055 | yes | 75,316 / 660,907 |
| P-hourly | SNIPW | 0.00495 | 0.00448–0.00541 | 1.1% | -0.00041…+0.00052 | yes | 75,316 / 660,907 |
| P-hourly | DM | 0.00463 | 0.00463–0.00463 | 5.4% | -0.00032…-0.00021 | NO | 75,316 / 660,907 |
| P-hourly | DR | 0.00495 | 0.00449–0.00542 | 1.3% | -0.00040…+0.00053 | yes | 75,316 / 660,907 |

## Analysis 3 — real before/after with real truth (W split at its midpoint)

W1 = before (2019-11-24T00:00 → 2019-11-25T18:00 UTC), W2 = after. Direction A: old = Random → new = BTS. Direction B: old = BTS → new = Random.
All four cells V(period, policy) are observed on-policy because both arms ran concurrently; that is the truth. ± = 95% half-width.

| split | direction | naive before/after | truth (concurrent A/B in W2) | DR policy effect | IPW | SNIPW | S1: DR CI(est − truth) ∋ 0 | abs err naive vs DR | naive CI ∋ truth | ESS/n (after logs) |
|---|---|---|---|---|---|---|---|---|---|---|
| halves | A_deploy_BTS | +0.00162 ± 0.00021 | **+0.00126** ± 0.00023 | +0.00140 ± 0.00027 | +0.00139 | +0.00137 | yes | 0.00036 vs 0.00014 | no | 25,395/2,769,425 |
| halves | B_rollback_to_Random | -0.00125 ± 0.00023 | **-0.00126** ± 0.00023 | -0.00170 ± 0.00065 | -0.00170 | -0.00172 | yes | 0.00000 vs 0.00045 | yes | 42,386/308,605 |

**2×2 Shapley decomposition (DR fills the two unobserved cells) vs all-on-policy truth:**

| direction | policy (Shapley) est vs truth | env (Shapley) est vs truth | interaction est vs truth |
|---|---|---|---|
| A_deploy_BTS | +0.00136 ± 0.00033 vs +0.00144 ± 0.00015 | +0.00025 vs +0.00018 | +0.00007 ± 0.00066 vs -0.00036 ± 0.00031 |
| B_rollback_to_Random | -0.00199 ± 0.00040 vs -0.00144 ± 0.00015 | +0.00073 vs +0.00018 | +0.00057 ± 0.00080 vs +0.00036 ± 0.00031 |

### Secondary — every ordered pair of whole UTC days inside W (all reported)

| split | direction | naive before/after | truth (concurrent A/B in W2) | DR policy effect | IPW | SNIPW | S1: DR CI(est − truth) ∋ 0 | abs err naive vs DR | naive CI ∋ truth | ESS/n (after logs) |
|---|---|---|---|---|---|---|---|---|---|---|
| 2019-11-24→2019-11-25 | A_deploy_BTS | +0.00154 ± 0.00027 | **+0.00171** ± 0.00030 | +0.00270 ± 0.00035 | +0.00203 | +0.00250 | NO | 0.00017 vs 0.00098 | yes | 799/1,479,442 |
| 2019-11-24→2019-11-25 | B_rollback_to_Random | -0.00159 ± 0.00029 | **-0.00171** ± 0.00030 | -0.00088 ± 0.00080 | -0.00093 | -0.00084 | yes | 0.00012 vs 0.00083 | yes | 16,149/163,989 |
| 2019-11-24→2019-11-26 | A_deploy_BTS | +0.00149 ± 0.00027 | **+0.00106** ± 0.00030 | +0.00148 ± 0.00028 | +0.00151 | +0.00146 | NO | 0.00043 vs 0.00042 | no | 12,822/1,611,904 |
| 2019-11-24→2019-11-26 | B_rollback_to_Random | -0.00100 ± 0.00030 | **-0.00106** ± 0.00030 | -0.00181 ± 0.00092 | -0.00181 | -0.00181 | yes | 0.00007 vs 0.00075 | yes | 25,583/179,290 |
| 2019-11-25→2019-11-26 | A_deploy_BTS | +0.00166 ± 0.00029 | **+0.00106** ± 0.00030 | +0.00148 ± 0.00028 | +0.00151 | +0.00146 | NO | 0.00060 vs 0.00042 | no | 12,822/1,611,904 |
| 2019-11-25→2019-11-26 | B_rollback_to_Random | -0.00112 ± 0.00031 | **-0.00106** ± 0.00030 | -0.00181 ± 0.00092 | -0.00181 | -0.00181 | yes | 0.00005 vs 0.00075 | yes | 25,583/179,290 |

## Balance check (W2): total-variation distance between arms, per user feature (top 50 categories + other)

user_feature_0: 0.3611 · user_feature_1: 0.3622 · user_feature_2: 0.3623 · user_feature_3: 0.3639 — **CAVEAT: arm assignment may not be randomised by user**

