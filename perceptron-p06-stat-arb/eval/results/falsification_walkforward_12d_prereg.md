# Falsification test 1 — walk-forward (train on day i−1, test on day i)

Days: 2025-10-01, 2025-11-01, 2025-12-01, 2026-01-01, 2026-02-01, 2026-03-01, 2026-04-01, 2026-05-01, 2026-06-01, 2026-07-01, 2026-08-01, 2026-09-01, 2026-10-01. 5 BTC legs (binance_BTCUSDT, binance-futures_BTCUSDT, coinbase_BTC-USD, okex_BTC-USDT, okex-swap_BTC-USDT-SWAP). Cells: fee [1.0, 2.0] bps/leg × one-way latency [1.0, 5.0, 20.0] ms; P&L = simulated USD/day summed over the 6 cells (0.05 BTC cap). Policies are fitted on the previous day only.

| test day | naive | threshold_pair | ev_kmpair | gbm_clf | lev | lev_edge_only |
|---|---|---|---|---|---|---|
| 2025-11-01 | -140 | 234 | 211 | 259 | 312 | 256 |
| 2025-12-01 | -1,547 | 1,782 | 1,446 | 1,913 | 2,208 | 1,828 |
| 2026-01-01 | -188 | 138 | 133 | 172 | 173 | 131 |
| 2026-02-01 | -2,286 | 1,976 | 1,891 | 2,357 | 2,479 | 1,978 |
| 2026-03-01 | -1,950 | 4,011 | 3,777 | 4,736 | 4,890 | 4,024 |
| 2026-04-01 | -652 | 1,260 | 1,226 | 1,544 | 1,593 | 1,287 |
| 2026-05-01 | -470 | 732 | 701 | 838 | 877 | 703 |
| 2026-06-01 | -1,910 | 1,287 | 1,271 | 1,345 | 1,483 | 1,273 |
| 2026-07-01 | -3,597 | 1,927 | 1,756 | 2,450 | 2,577 | 2,027 |
| 2026-08-01 | -256 | 282 | 283 | 296 | 326 | 293 |
| 2026-09-01 | -3,428 | 1,065 | 1,085 | 1,097 | 1,197 | 1,107 |
| 2026-10-01 | -2,488 | 1,175 | 1,169 | 1,274 | 1,342 | 1,181 |

Falsified = the lower bound of either 95% interval is ≤ 0. With few test days the percentile bootstrap is optimistic, so the t-interval and a one-sided sign test are also reported.

| comparison | mean USD/day | median | 95% bootstrap CI | 95% t-CI | days positive | sign p | Wilcoxon p | rel. uplift (totals) | falsified? |
|---|---|---|---|---|---|---|---|---|---|
| lev - threshold_pair | +298.9 | +181.2 | [+165.0, +450.9] | [+129.6, +468.3] | 12/12 | 0.0002 | 0.0002 | +22.6% | no |
| gbm_clf - threshold_pair | +201.0 | +102.8 | [+89.0, +335.2] | [+54.6, +347.4] | 12/12 | 0.0002 | 0.0002 | +15.2% | no |
| ev_kmpair - threshold_pair | -76.8 | -27.0 | [-141.5, -22.3] | [-147.7, -5.8] | 2/12 | 0.9968 | 0.9976 | -5.8% | YES |
| threshold_pair - naive | +2,898.5 | +3,262.9 | [+1,814.9, +3,974.2] | [+1,628.4, +4,168.5] | 12/12 | 0.0002 | 0.0002 | -183.9% | no |
| lev - lev_edge_only | +280.7 | +191.8 | [+154.0, +425.9] | [+119.3, +442.1] | 12/12 | 0.0002 | 0.0002 | +20.9% | no |

Subset `unseen7` (test days 2025-11-01, 2025-12-01, 2026-01-01, 2026-02-01, 2026-03-01, 2026-04-01, 2026-05-01):

| comparison | mean USD/day | median | 95% bootstrap CI | 95% t-CI | days positive | sign p | Wilcoxon p | rel. uplift (totals) | falsified? |
|---|---|---|---|---|---|---|---|---|---|
| lev - threshold_pair | +342.8 | +333.6 | [+155.6, +553.5] | [+69.7, +615.9] | 7/7 | 0.0078 | 0.0078 | +23.7% | no |
| lev - lev_edge_only | +332.1 | +305.7 | [+151.0, +542.6] | [+64.8, +599.4] | 7/7 | 0.0078 | 0.0078 | +22.8% | no |

LEV − threshold by cell (mean USD/day, 95% CI, days positive):

| cell | mean | CI | days + |
|---|---|---|---|
| f1_d1 | +39.1 | [+14.0, +68.1] | 11 |
| f1_d5 | +115.0 | [+57.2, +179.8] | 11 |
| f1_d20 | +86.3 | [+45.7, +131.3] | 12 |
| f2_d1 | +16.0 | [+6.0, +27.4] | 9 |
| f2_d5 | +27.8 | [+14.0, +43.4] | 12 |
| f2_d20 | +14.7 | [-5.3, +35.2] | 9 |

Runtime 260 s · commit `9cadff6` · `python -m eval.falsification walkforward --days 2025-10-01 2025-11-01 2025-12-01 2026-01-01 2026-02-01 2026-03-01 2026-04-01 2026-05-01 2026-06-01 2026-07-01 2026-08-01 2026-09-01 2026-10-01 --out falsification_walkforward_12d_prereg --subset unseen7:2025-11-01,2025-12-01,2026-01-01,2026-02-01,2026-03-01,2026-04-01,2026-05-01`
