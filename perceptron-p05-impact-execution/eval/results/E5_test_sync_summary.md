# E5_test_sync: paired comparison vs TWAP

n = 60 seeds (1000–1059), source = CSV. IS = implementation shortfall vs the arrival mid, in bps (+ = cost). 1 bp = 10¢/share at $1,000. ΔIS = label − baseline on the same seed; 95% CI = bootstrap over seeds (10k resamples).

| policy | mean IS (bps) | 95% CI | std | CVaR95 | own impact (bps) | ΔIS vs TWAP (bps) | 95% CI | win rate |
|---|---|---|---|---|---|---|---|---|
| IA_full | 0.502 | [-0.238, 1.258] | 2.996 | 7.258 | 0.279 | -0.017 | [-0.069, +0.035] | 53% |
| IA_sched_only | 0.469 | [-0.268, 1.225] | 2.997 | 7.131 | 0.230 | -0.050 | [-0.100, -0.002] | 58% |
| TWAP | 0.519 | [-0.243, 1.300] | 3.086 | 7.411 | 0.273 | — | — | — |
| TWAP_touch_limit | 0.493 | [-0.273, 1.273] | 3.087 | 7.378 | 0.268 | -0.026 | [-0.067, +0.014] | 60% |
| VWAP | 0.502 | [-0.255, 1.272] | 3.059 | 7.259 | 0.252 | -0.017 | [-0.053, +0.019] | 52% |

Decomposition means (bps): IA_full: drift +0.141, own +0.279, instant +0.082; IA_sched_only: drift +0.118, own +0.230, instant +0.122; TWAP: drift +0.124, own +0.273, instant +0.122; TWAP_touch_limit: drift +0.144, own +0.268, instant +0.082; VWAP: drift +0.125, own +0.252, instant +0.125
