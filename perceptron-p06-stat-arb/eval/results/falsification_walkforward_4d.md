# Falsification test 1 — walk-forward (train on day i−1, test on day i)

Days: 2026-06-01, 2026-07-01, 2026-08-01, 2026-09-01, 2026-10-01. 5 BTC legs (binance_BTCUSDT, binance-futures_BTCUSDT, coinbase_BTC-USD, okex_BTC-USDT, okex-swap_BTC-USDT-SWAP). Cells: fee [1.0, 2.0] bps/leg × one-way latency [1.0, 5.0, 20.0] ms; P&L = simulated USD/day summed over the 6 cells (0.05 BTC cap). Policies are fitted on the previous day only.

| test day | naive | threshold_pair | ev_kmpair | gbm_clf | lev | lev_edge_only |
|---|---|---|---|---|---|---|
| 2026-07-01 | -3,597 | 1,927 | 1,756 | 2,450 | 2,577 | 2,027 |
| 2026-08-01 | -256 | 282 | 283 | 296 | 326 | 293 |
| 2026-09-01 | -3,428 | 1,065 | 1,085 | 1,097 | 1,197 | 1,107 |
| 2026-10-01 | -2,488 | 1,175 | 1,169 | 1,274 | 1,342 | 1,181 |

Falsified = the lower bound of either 95% interval is ≤ 0. With few test days the percentile bootstrap is optimistic, so the t-interval and a one-sided sign test are also reported.

| comparison | mean USD/day | 95% bootstrap CI | 95% t-CI | days positive | sign-test p | falsified? |
|---|---|---|---|---|---|---|
| lev - threshold_pair | +247.8 | [+73.9, +520.4] | [-186.6, +682.3] | 4/4 | 0.062 | YES |
| gbm_clf - threshold_pair | +166.8 | [+22.7, +399.7] | [-215.0, +548.5] | 4/4 | 0.062 | YES |
| ev_kmpair - threshold_pair | -39.2 | [-128.3, +13.1] | [-180.5, +102.0] | 2/4 | 0.688 | YES |
| threshold_pair - naive | +3,554.9 | [+1,527.3, +5,059.2] | [+133.4, +6,976.5] | 4/4 | 0.062 | no |
| lev - lev_edge_only | +208.6 | [+61.5, +435.6] | [-163.8, +581.0] | 4/4 | 0.062 | YES |

LEV − threshold by cell (mean USD/day, 95% CI, days positive):

| cell | mean | CI | days + |
|---|---|---|---|
| f1_d1 | +17.9 | [+4.6, +35.4] | 4 |
| f1_d5 | +99.4 | [+29.7, +177.1] | 4 |
| f1_d20 | +74.4 | [+17.0, +171.1] | 4 |
| f2_d1 | +4.7 | [-0.9, +11.5] | 3 |
| f2_d5 | +14.9 | [+0.7, +41.4] | 4 |
| f2_d20 | +36.5 | [-3.7, +76.8] | 2 |

Runtime 202 s · commit `f8cb48f` · `python -m eval.falsification walkforward --days 2026-06-01 2026-07-01 2026-08-01 2026-09-01 2026-10-01`
