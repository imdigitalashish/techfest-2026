# E6_confirm_sync: paired comparison vs TWAP

n = 200 seeds (1060–1259), source = CSV. IS = implementation shortfall vs the arrival mid, in bps (+ = cost). 1 bp = 10¢/share at $1,000. ΔIS = label − baseline on the same seed; 95% CI = bootstrap over seeds (10k resamples).

| policy | mean IS (bps) | 95% CI | std | CVaR95 | own impact (bps) | ΔIS vs TWAP (bps) | 95% CI | win rate |
|---|---|---|---|---|---|---|---|---|
| IA_full | -0.213 | [-0.609, 0.188] | 2.927 | 5.694 | 0.218 | -0.015 | [-0.044, +0.016] | 55% |
| IA_sched_only | -0.232 | [-0.634, 0.171] | 2.949 | 5.674 | 0.176 | -0.034 | [-0.056, -0.013] | 52% |
| TWAP | -0.198 | [-0.603, 0.210] | 2.975 | 5.784 | 0.217 | — | — | — |
| VWAP | -0.214 | [-0.622, 0.199] | 3.008 | 5.784 | 0.204 | -0.016 | [-0.040, +0.007] | 54% |

Decomposition means (bps): IA_full: drift -0.513, own +0.218, instant +0.081; IA_sched_only: drift -0.531, own +0.176, instant +0.123; TWAP: drift -0.539, own +0.217, instant +0.123; VWAP: drift -0.540, own +0.204, instant +0.122
