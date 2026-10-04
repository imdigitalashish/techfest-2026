# Reaction time: compiled decision step and detector (Apple M5, shared machine)

LEV: 200 trees / 12,200 nodes, trained on 2026-09-01 cells (15,870 rows); evaluated on all 12,780 candidates of 2026-10-01. Max |compiled − sklearn| = 0.0e+00 bps.

| decision step (features + LEV + act) | p50 | p90 | p99 | p99.9 |
|---|---|---|---|---|
| in-kernel, Numba (mach_absolute_time, 41.7 ns ticks; 63,900 calls) | 6.08 µs | 10.50 µs | 41.46 µs | 510.17 µs |
| one call from Python incl. dispatch (200,000 calls) | 8.08 µs | 16.04 µs | 62.33 µs | 637.71 µs |

| detector (Numba event loop, amortised) | events | wall (best of 3) | ns / event | events / s |
|---|---|---|---|---|
| 2026-10-01, 5 legs | 5,835,887 | 0.50 s | 87 | 11,559,089 |
| 2026-10-01, 9 legs | 9,181,230 | 0.76 s | 82 | 12,121,222 |

Machine shared with other jobs (load not controlled); figures are upper bounds for a dedicated core.

Commit `9cadff6` · `eval/run_guarded.sh .venv/bin/python -m eval.decision_timing`
