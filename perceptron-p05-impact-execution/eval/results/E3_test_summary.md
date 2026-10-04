# E3_test: paired comparison vs TWAP

n = 60 seeds (1000–1059), source = CSV. IS = implementation shortfall vs the arrival mid, in bps (+ = cost). 1 bp = 10¢/share at $1,000. ΔIS = label − baseline on the same seed; 95% CI = bootstrap over seeds (10k resamples).

| policy | mean IS (bps) | 95% CI | std | CVaR95 | own impact (bps) | ΔIS vs TWAP (bps) | 95% CI | win rate |
|---|---|---|---|---|---|---|---|---|
| IA_full | 0.346 | [-0.408, 1.122] | 3.077 | 7.254 | 0.557 | -0.056 | [-0.441, +0.339] | 52% |
| IA_sched_only | 0.352 | [-0.364, 1.078] | 2.889 | 6.530 | 0.548 | -0.050 | [-0.407, +0.336] | 57% |
| TWAP | 0.402 | [-0.361, 1.183] | 3.084 | 6.530 | 0.589 | — | — | — |
| TWAP_touch_limit | 0.316 | [-0.390, 1.037] | 2.895 | 6.250 | 0.527 | -0.086 | [-0.447, +0.288] | 62% |
| VWAP | 0.223 | [-0.502, 0.969] | 2.938 | 5.372 | 0.412 | -0.180 | [-0.420, +0.081] | 63% |

Decomposition means (bps): IA_full: drift -0.292, own +0.557, instant +0.081; IA_sched_only: drift -0.312, own +0.548, instant +0.116; TWAP: drift -0.311, own +0.589, instant +0.124; TWAP_touch_limit: drift -0.294, own +0.527, instant +0.084; VWAP: drift -0.311, own +0.412, instant +0.121
