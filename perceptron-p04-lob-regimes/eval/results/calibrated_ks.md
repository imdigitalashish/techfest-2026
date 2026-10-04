# Results: `calibrated_ks`

- Command: `python eval/run_baseline.py --policies static_snorm ks_refit ksc_refit regime_gated fixed_share fs_ksc_boost --tag calibrated_ks` (from `perceptron-p04-lob-regimes/`)
- Commit: `a97aa4b` · 2026-10-04T02:13:48+00:00 · arm64 macOS-26.2-arm64-arm-64bit · runtime 2688.6 s
- Data: Tardis.dev binance-futures BTCUSDT `book_snapshot_5` (free first-of-month days; MD5s in data/manifest.csv)
- Grid 1 s, horizon 10 steps; label = sign of mid change (ties excluded); prequential, label delay enforced

## In-sample (train days, static model) — the reference the model was fit on

| day | n | logloss | acc | AUC |
|---|---|---|---|---|
| 2023-02-01 | 71711 | 0.6465 | 0.6350 | 0.6779 |
| 2023-08-01 | 58248 | 0.6101 | 0.6823 | 0.7336 |

## dev: 2023-09-01, 2023-11-01, 2023-12-01

| policy | logloss | Δ vs static (95% block-bootstrap CI) | acc | AUC | edge bps/signal | alarms |
|---|---|---|---|---|---|---|
| static_snorm | 0.6473 | +0.0000 [+0.0000, +0.0000] | 0.6307 | 0.6739 | +0.385 | 0 |
| ks_refit | 0.6641 | +0.0167 [+0.0115, +0.0220] | 0.6090 | 0.6557 | +0.302 | 144 |
| ksc_refit | 0.6648 | +0.0175 [+0.0132, +0.0220] | 0.6116 | 0.6581 | +0.323 | 113 |
| regime_gated | 0.6340 | -0.0133 [-0.0156, -0.0113] | 0.6314 | 0.6872 | +0.393 | 0 |
| fixed_share | 0.6412 | -0.0061 [-0.0086, -0.0038] | 0.6273 | 0.6798 | +0.357 | 0 |
| fs_ksc_boost | 0.6410 | -0.0064 [-0.0089, -0.0041] | 0.6278 | 0.6802 | +0.357 | 113 |

## holdout: 2024-05-01, 2024-11-01, 2025-08-01

| policy | logloss | Δ vs static (95% block-bootstrap CI) | acc | AUC | edge bps/signal | alarms |
|---|---|---|---|---|---|---|
| static_snorm | 0.6808 | +0.0000 [+0.0000, +0.0000] | 0.5872 | 0.6180 | +0.412 | 0 |
| ks_refit | 0.7010 | +0.0202 [+0.0157, +0.0247] | 0.5623 | 0.5894 | +0.263 | 144 |
| ksc_refit | 0.6960 | +0.0152 [+0.0113, +0.0196] | 0.5653 | 0.5945 | +0.278 | 93 |
| regime_gated | 0.6676 | -0.0132 [-0.0148, -0.0115] | 0.5874 | 0.6247 | +0.420 | 0 |
| fixed_share | 0.6738 | -0.0070 [-0.0087, -0.0051] | 0.5834 | 0.6197 | +0.387 | 0 |
| fs_ksc_boost | 0.6741 | -0.0066 [-0.0084, -0.0047] | 0.5835 | 0.6195 | +0.389 | 93 |

## Per day (logloss · AUC · alarms)

| policy | 2023-09-01 | 2023-11-01 | 2023-12-01 | 2024-05-01 | 2024-11-01 | 2025-08-01 |
|---|---|---|---|---|---|---|
| static_snorm | 0.6213 · 0.716 · 0 | 0.6428 · 0.682 · 0 | 0.6729 · 0.632 · 0 | 0.7082 · 0.571 · 0 | 0.6680 · 0.638 · 0 | 0.6635 · 0.648 · 0 |
| ks_refit | 0.6329 · 0.696 · 48 | 0.6612 · 0.667 · 48 | 0.6924 · 0.607 · 48 | 0.7164 · 0.543 · 48 | 0.7002 · 0.602 · 48 | 0.6849 · 0.623 · 48 |
| ksc_refit | 0.6330 · 0.705 · 37 | 0.6592 · 0.666 · 39 | 0.6962 · 0.604 · 37 | 0.7140 · 0.543 · 47 | 0.6960 · 0.609 · 31 | 0.6764 · 0.630 · 15 |
| regime_gated | 0.6030 · 0.732 · 0 | 0.6272 · 0.698 · 0 | 0.6659 · 0.636 · 0 | 0.6870 · 0.573 · 0 | 0.6596 · 0.645 · 0 | 0.6544 · 0.654 · 0 |
| fixed_share | 0.6076 · 0.725 · 0 | 0.6354 · 0.691 · 0 | 0.6742 · 0.626 · 0 | 0.6925 · 0.567 · 0 | 0.6663 · 0.638 · 0 | 0.6609 · 0.650 · 0 |
| fs_ksc_boost | 0.6073 · 0.725 · 37 | 0.6351 · 0.691 · 39 | 0.6741 · 0.627 · 37 | 0.6928 · 0.567 · 47 | 0.6668 · 0.638 · 31 | 0.6610 · 0.650 · 15 |

## Scheduled-event windows (event −30 min … +60 min), logloss

| policy | 2023-11-01 (fomc-2023-11-01) | 2024-05-01 (fomc-2024-05-01) |
|---|---|---|
| static_snorm | 0.7194 | 0.7329 |
| ks_refit | 0.7564 | 0.7369 |
| ksc_refit | 0.7723 | 0.7467 |
| regime_gated | 0.6941 | 0.7010 |
| fixed_share | 0.7025 | 0.7060 |
| fs_ksc_boost | 0.7015 | 0.7049 |

## Latency of the online step (Python reference implementation, single core)

| policy | predict p50 µs | predict p99 µs | full step p50 µs | full step p99 µs |
|---|---|---|---|---|
| static_snorm | 5.9 | 167.7 | 7.0 | 213.6 |
| ks_refit | 5.9 | 1367.4 | 7.2 | 237485.9 |
| ksc_refit | 5.8 | 2452.7 | 7.2 | 282456.3 |
| regime_gated | 7.4 | 344.0 | 8.6 | 436.4 |
| fixed_share | 37.9 | 4191.4 | 64.9 | 9124.3 |
| fs_ksc_boost | 37.2 | 7825.2 | 64.6 | 297811.8 |
