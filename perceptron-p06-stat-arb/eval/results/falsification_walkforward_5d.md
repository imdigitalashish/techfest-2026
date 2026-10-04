# Falsification test 1 — walk-forward (train on day i−1, test on day i)

Days: 2026-05-01, 2026-06-01, 2026-07-01, 2026-08-01, 2026-09-01, 2026-10-01. 5 BTC legs (binance_BTCUSDT, binance-futures_BTCUSDT, coinbase_BTC-USD, okex_BTC-USDT, okex-swap_BTC-USDT-SWAP). Cells: fee [1.0, 2.0] bps/leg × one-way latency [1.0, 5.0, 20.0] ms; P&L = simulated USD/day summed over the 6 cells (0.05 BTC cap). Policies are fitted on the previous day only.

| test day | naive | threshold_pair | ev_kmpair | gbm_clf | lev | lev_edge_only |
|---|---|---|---|---|---|---|
| 2026-06-01 | -1,910 | 1,287 | 1,271 | 1,345 | 1,483 | 1,273 |
| 2026-07-01 | -3,597 | 1,927 | 1,756 | 2,450 | 2,577 | 2,027 |
| 2026-08-01 | -256 | 282 | 283 | 296 | 326 | 293 |
| 2026-09-01 | -3,428 | 1,065 | 1,085 | 1,097 | 1,197 | 1,107 |
| 2026-10-01 | -2,488 | 1,175 | 1,169 | 1,274 | 1,342 | 1,181 |

Falsified = the lower bound of either 95% interval is ≤ 0. With few test days the percentile bootstrap is optimistic, so the t-interval and a one-sided sign test are also reported.

| comparison | mean USD/day | median | 95% bootstrap CI | 95% t-CI | days positive | sign p | Wilcoxon p | rel. uplift (totals) | falsified? |
|---|---|---|---|---|---|---|---|---|---|
| lev - threshold_pair | +237.5 | +166.4 | [+92.4, +449.6] | [-57.5, +532.5] | 5/5 | 0.0312 | 0.0312 | +20.7% | YES |
| gbm_clf - threshold_pair | +145.0 | +58.1 | [+29.8, +336.0] | [-119.9, +410.0] | 5/5 | 0.0312 | 0.0312 | +12.6% | YES |
| ev_kmpair - threshold_pair | -34.5 | -5.9 | [-105.2, +8.4] | [-130.9, +61.8] | 2/5 | 0.8125 | 0.7812 | -3.0% | YES |
| threshold_pair - naive | +3,483.4 | +3,663.0 | [+1,861.3, +4,739.9] | [+1,162.7, +5,804.1] | 5/5 | 0.0312 | 0.0312 | -149.1% | no |
| lev - lev_edge_only | +208.8 | +160.7 | [+79.5, +380.6] | [-42.9, +460.4] | 5/5 | 0.0312 | 0.0312 | +17.8% | YES |

LEV − threshold by cell (mean USD/day, 95% CI, days positive):

| cell | mean | CI | days + |
|---|---|---|---|
| f1_d1 | +9.1 | [-11.5, +29.2] | 4 |
| f1_d5 | +77.7 | [+12.7, +155.3] | 4 |
| f1_d20 | +88.0 | [+21.9, +165.4] | 5 |
| f2_d1 | +3.2 | [-2.0, +9.5] | 3 |
| f2_d5 | +25.3 | [+1.5, +51.6] | 5 |
| f2_d20 | +34.1 | [+1.9, +66.3] | 3 |

Runtime 41 s · commit `9cadff6` · `python -m eval.falsification walkforward --days 2026-05-01 2026-06-01 2026-07-01 2026-08-01 2026-09-01 2026-10-01 --out falsification_walkforward_5d`
