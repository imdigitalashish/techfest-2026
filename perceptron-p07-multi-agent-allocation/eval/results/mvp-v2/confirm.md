# Confirmatory analysis — `eval/results/mvp-v2` (pre-registered: eval/preregistration.md)

Seeds 200–229 (30 fresh test seeds) · 1440 episodes · horizon 1440 · K=40 · P=10 · planner backend ['highspy']

## Served fraction by policy (mean over seeds)

| scenario | greedy | mpc-cusum-v1 | mpc-ewma | mpc-myopic | mpc-queue | oracle | reactive | static |
|---|---|---|---|---|---|---|---|---|
| stationary | 0.9751 | 0.9987 | 0.9987 | 0.9975 | 0.9974 | 0.9987 | 0.9625 | 0.9528 |
| shock | 0.9057 | 0.9417 | 0.9430 | 0.9337 | 0.9549 | 0.9418 | 0.8996 | 0.8642 |
| drift | 0.7884 | 0.9940 | 0.9946 | 0.9758 | 0.9679 | 0.9949 | 0.9363 | 0.8216 |
| shock+drift | 0.7446 | 0.9300 | 0.9321 | 0.9092 | 0.9284 | 0.9317 | 0.8774 | 0.7573 |
| spikes | 0.9717 | 0.9969 | 0.9969 | 0.9945 | 0.9967 | 0.9972 | 0.9534 | 0.9396 |
| shock+drift+spikes | 0.7443 | 0.9234 | 0.9256 | 0.9046 | 0.9251 | 0.9254 | 0.8658 | 0.7452 |

## Primary family — `mpc-ewma` vs pre-registered reference rule (Holm over 6 scenarios)

| scenario | reference | Δ served (pp) [95% paired CI] | seeds won | Wilcoxon p | Holm p |
|---|---|---|---|---|---|
| stationary | greedy | +2.36 [+2.16, +2.57] | 30/30 | 1.9e-09 | 1.1e-08 |
| shock | greedy | +3.73 [+3.28, +4.20] | 30/30 | 1.9e-09 | 1.1e-08 |
| drift | reactive | +5.83 [+5.75, +5.92] | 30/30 | 1.9e-09 | 1.1e-08 |
| shock+drift | reactive | +5.47 [+5.36, +5.59] | 30/30 | 1.9e-09 | 1.1e-08 |
| spikes | greedy | +2.51 [+2.34, +2.71] | 30/30 | 1.9e-09 | 1.1e-08 |
| shock+drift+spikes | reactive | +5.99 [+5.82, +6.15] | 30/30 | 1.9e-09 | 1.1e-08 |

## Secondary family S1 — served_frac (Holm within family and endpoint)

| scenario | comparison | Δ served (pp) [95% paired CI] | seeds with increase | Wilcoxon p | Holm p |
|---|---|---|---|---|---|
| stationary | mpc-myopic − mpc-ewma | -0.12 [-0.14, -0.10] | 0/30 | 1.9e-09 | 2.2e-08 |
| stationary | mpc-queue − mpc-ewma | -0.13 [-0.16, -0.10] | 0/30 | 1.9e-09 | 2.2e-08 |
| shock | mpc-myopic − mpc-ewma | -0.93 [-1.05, -0.81] | 0/30 | 1.9e-09 | 2.2e-08 |
| shock | mpc-queue − mpc-ewma | +1.19 [+1.06, +1.32] | 30/30 | 1.9e-09 | 2.2e-08 |
| drift | mpc-myopic − mpc-ewma | -1.88 [-2.06, -1.70] | 0/30 | 1.9e-09 | 2.2e-08 |
| drift | mpc-queue − mpc-ewma | -2.68 [-2.76, -2.59] | 0/30 | 1.9e-09 | 2.2e-08 |
| shock+drift | mpc-myopic − mpc-ewma | -2.29 [-2.55, -2.03] | 0/30 | 1.9e-09 | 2.2e-08 |
| shock+drift | mpc-queue − mpc-ewma | -0.37 [-0.50, -0.23] | 5/30 | 7.3e-05 | 0.00022 |
| spikes | mpc-myopic − mpc-ewma | -0.24 [-0.28, -0.20] | 0/30 | 1.9e-09 | 2.2e-08 |
| spikes | mpc-queue − mpc-ewma | -0.02 [-0.06, +0.02] | 12/30 | 0.26 | 0.52 |
| shock+drift+spikes | mpc-myopic − mpc-ewma | -2.10 [-2.36, -1.87] | 0/30 | 1.9e-09 | 2.2e-08 |
| shock+drift+spikes | mpc-queue − mpc-ewma | -0.06 [-0.20, +0.08] | 17/30 | 0.58 | 0.58 |

## Secondary family S1 — shock_lost (Holm within family and endpoint)

| scenario | comparison | Δ lost per shock [95% paired CI] | seeds with increase | Wilcoxon p | Holm p |
|---|---|---|---|---|---|
| shock | mpc-myopic − mpc-ewma | +42.67 [+34.53, +51.13] | 30/30 | 1.7e-06 | 1e-05 |
| shock | mpc-queue − mpc-ewma | -62.30 [-70.47, -53.83] | 0/30 | 1.7e-06 | 1e-05 |
| shock+drift | mpc-myopic − mpc-ewma | +31.73 [+23.57, +39.77] | 26/30 | 8.1e-06 | 1.6e-05 |
| shock+drift | mpc-queue − mpc-ewma | -49.90 [-57.03, -43.10] | 0/30 | 1.7e-06 | 1e-05 |
| shock+drift+spikes | mpc-myopic − mpc-ewma | +25.27 [+16.83, +33.67] | 26/30 | 5.3e-05 | 5.3e-05 |
| shock+drift+spikes | mpc-queue − mpc-ewma | -58.93 [-67.63, -50.30] | 0/30 | 1.7e-06 | 1e-05 |

## Secondary family S2 — served_frac (Holm within family and endpoint)

| scenario | comparison | Δ served (pp) [95% paired CI] | seeds with increase | Wilcoxon p | Holm p |
|---|---|---|---|---|---|
| stationary | mpc-cusum-v1 − mpc-ewma | +0.00 [-0.01, +0.02] | 17/30 | 0.6 | 1 |
| shock | mpc-cusum-v1 − mpc-ewma | -0.13 [-0.17, -0.09] | 5/30 | 2.4e-05 | 7.1e-05 |
| drift | mpc-cusum-v1 − mpc-ewma | -0.07 [-0.09, -0.05] | 4/30 | 5.1e-06 | 2.1e-05 |
| shock+drift | mpc-cusum-v1 − mpc-ewma | -0.21 [-0.25, -0.17] | 0/30 | 1.9e-09 | 1.1e-08 |
| spikes | mpc-cusum-v1 − mpc-ewma | +0.00 [-0.02, +0.02] | 15/30 | 0.94 | 1 |
| shock+drift+spikes | mpc-cusum-v1 − mpc-ewma | -0.22 [-0.26, -0.18] | 2/30 | 9.3e-09 | 4.7e-08 |

## Secondary family S2 — shock_lost (Holm within family and endpoint)

| scenario | comparison | Δ lost per shock [95% paired CI] | seeds with increase | Wilcoxon p | Holm p |
|---|---|---|---|---|---|
| shock | mpc-cusum-v1 − mpc-ewma | +8.00 [+4.53, +11.47] | 23/30 | 0.00043 | 0.00043 |
| shock+drift | mpc-cusum-v1 − mpc-ewma | +14.40 [+10.83, +17.87] | 27/30 | 9.6e-06 | 2.9e-05 |
| shock+drift+spikes | mpc-cusum-v1 − mpc-ewma | +12.57 [+8.30, +16.63] | 25/30 | 4.2e-05 | 8.3e-05 |

## Secondary family S3 — served_frac (Holm within family and endpoint)

| scenario | comparison | Δ served (pp) [95% paired CI] | seeds with increase | Wilcoxon p | Holm p |
|---|---|---|---|---|---|
| stationary | oracle − mpc-ewma | -0.00 [-0.01, +0.01] | 14/30 | 0.72 | 0.83 |
| shock | oracle − mpc-ewma | -0.12 [-0.17, -0.07] | 5/30 | 4.4e-05 | 0.00026 |
| drift | oracle − mpc-ewma | +0.03 [+0.01, +0.04] | 20/30 | 0.041 | 0.16 |
| shock+drift | oracle − mpc-ewma | -0.04 [-0.08, -0.00] | 11/30 | 0.05 | 0.16 |
| spikes | oracle − mpc-ewma | +0.04 [+0.02, +0.05] | 25/30 | 6.3e-05 | 0.00031 |
| shock+drift+spikes | oracle − mpc-ewma | -0.02 [-0.07, +0.02] | 15/30 | 0.42 | 0.83 |

## Secondary family S3 — shock_lost (Holm within family and endpoint)

| scenario | comparison | Δ lost per shock [95% paired CI] | seeds with increase | Wilcoxon p | Holm p |
|---|---|---|---|---|---|
| shock | oracle − mpc-ewma | +5.37 [+1.13, +9.83] | 20/30 | 0.037 | 0.11 |
| shock+drift | oracle − mpc-ewma | +3.30 [-0.90, +7.70] | 17/30 | 0.23 | 0.23 |
| shock+drift+spikes | oracle − mpc-ewma | +4.00 [+0.13, +7.70] | 21/30 | 0.046 | 0.11 |

## Movement cost and shock recovery (means over seeds)

| scenario | policy | empty hops / served | lost per shock (120 steps) | recovered ≤120 steps | recover steps (censored at 120) |
|---|---|---|---|---|---|
| stationary | greedy | 0.346 | — | — | — |
| stationary | mpc-cusum-v1 | 0.557 | — | — | — |
| stationary | mpc-ewma | 0.583 | — | — | — |
| stationary | mpc-myopic | 0.687 | — | — | — |
| stationary | mpc-queue | 0.385 | — | — | — |
| stationary | oracle | 0.550 | — | — | — |
| stationary | reactive | 0.568 | — | — | — |
| stationary | static | 0.518 | — | — | — |
| shock | greedy | 0.326 | 404.5 | 0.13 | 115.6 |
| shock | mpc-cusum-v1 | 0.489 | 305.3 | 0.40 | 101.7 |
| shock | mpc-ewma | 0.511 | 297.3 | 0.47 | 96.1 |
| shock | mpc-myopic | 0.603 | 339.9 | 0.17 | 113.1 |
| shock | mpc-queue | 0.381 | 235.0 | 0.87 | 67.2 |
| shock | oracle | 0.481 | 302.6 | 0.43 | 100.3 |
| shock | reactive | 0.585 | 426.2 | 0.10 | 116.0 |
| shock | static | 0.512 | 573.5 | 0.00 | 120.0 |
| drift | greedy | 0.325 | — | — | — |
| drift | mpc-cusum-v1 | 0.693 | — | — | — |
| drift | mpc-ewma | 0.717 | — | — | — |
| drift | mpc-myopic | 0.767 | — | — | — |
| drift | mpc-queue | 0.509 | — | — | — |
| drift | oracle | 0.686 | — | — | — |
| drift | reactive | 0.701 | — | — | — |
| drift | static | 0.601 | — | — | — |
| shock+drift | greedy | 0.312 | 584.4 | 0.13 | 111.3 |
| shock+drift | mpc-cusum-v1 | 0.616 | 341.2 | 0.20 | 106.0 |
| shock+drift | mpc-ewma | 0.636 | 326.8 | 0.20 | 105.6 |
| shock+drift | mpc-myopic | 0.679 | 358.6 | 0.20 | 107.6 |
| shock+drift | mpc-queue | 0.489 | 276.9 | 0.63 | 84.0 |
| shock+drift | oracle | 0.607 | 330.1 | 0.30 | 102.8 |
| shock+drift | reactive | 0.689 | 448.7 | 0.00 | 120.0 |
| shock+drift | static | 0.585 | 735.7 | 0.00 | 120.0 |
| spikes | greedy | 0.347 | — | — | — |
| spikes | mpc-cusum-v1 | 0.569 | — | — | — |
| spikes | mpc-ewma | 0.588 | — | — | — |
| spikes | mpc-myopic | 0.683 | — | — | — |
| spikes | mpc-queue | 0.395 | — | — | — |
| spikes | oracle | 0.554 | — | — | — |
| spikes | reactive | 0.569 | — | — | — |
| spikes | static | 0.513 | — | — | — |
| shock+drift+spikes | greedy | 0.321 | 595.7 | 0.13 | 112.5 |
| shock+drift+spikes | mpc-cusum-v1 | 0.629 | 373.8 | 0.20 | 109.6 |
| shock+drift+spikes | mpc-ewma | 0.645 | 361.3 | 0.30 | 101.8 |
| shock+drift+spikes | mpc-myopic | 0.683 | 386.5 | 0.20 | 114.9 |
| shock+drift+spikes | mpc-queue | 0.499 | 302.3 | 0.57 | 84.9 |
| shock+drift+spikes | oracle | 0.614 | 365.3 | 0.27 | 108.0 |
| shock+drift+spikes | reactive | 0.690 | 491.7 | 0.03 | 119.4 |
| shock+drift+spikes | static | 0.585 | 771.9 | 0.00 | 120.0 |
