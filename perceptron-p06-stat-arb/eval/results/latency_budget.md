# Simulated end-to-end latency budget

L = feed (venue → us) + detector + decision + order (us → venue). Feed latency is measured; compute is measured on the M5; **order latency is an assumption** (= one-way feed latency) because sending orders needs exchange accounts.

## 1. Where the time goes

| term | value | source |
|---|---|---|
| detector, per market-data event (Numba, amortised, 5 legs) | 0.09 µs | decision_timing.json |
| decision step: features + LEV + act (Numba, in-kernel) | p50 6.08 µs · p99 41.46 µs | decision_timing.json |
| **our compute, total** | **p50 6.17 µs · p99 41.55 µs** | sum of the two rows above |

| venue (feed one-way) | Tardis collector p50 | p99 | this Mac in India, p05 (floor) |
|---|---|---|---|
| binance-futures:BTCUSDT | 1.83 ms | 4.1 ms | 90 ms |
| binance:BTCUSDT | 2.45 ms | 3.3 ms |  |
| okex:BTC-USDT | 4.45 ms | 12.0 ms | 25 ms |
| okex-swap:BTC-USDT-SWAP | 4.76 ms | 10.9 ms | 24 ms |
| kraken:BTC/USD | 7.51 ms | 33.0 ms | 78 ms |
| deribit:BTC-PERPETUAL | 8.73 ms | 201.1 ms | 69 ms |
| bitstamp:BTCUSD | 34.00 ms | 60.2 ms |  |
| bybit:BTCUSDT | 37.20 ms | 39.5 ms | -9 ms |
| coinbase:BTC-USD | 39.67 ms | 129.5 ms | 107 ms |

Our compute is 3–4 orders of magnitude below the network terms: the budget is spent on distance, not on the model.

## 2. What a budget buys — break-even one-way latency (ms) by fee level

Largest one-way latency δ (feed = order = δ, as in the frontier sweep) at which simulated P&L on the held-out day 2026-10-01 (9 legs) is still positive. Grid 0.5–100 ms; log-linear interpolation.

| fee per leg | naive | tuned per-pair threshold | EV (KM by pair) | LEV |
|---|---|---|---|---|
| 0 bp | > 100 | > 100 | > 100 | > 100 |
| 1 bp | 4.6 | > 100 | 53.7 | 92.9 |
| 2 bp | 7.8 | > 100 | > 100 | 96.5 |
| 5 bp | 69.2 | 10.6 | 89.3 | 93.4 |

Commit `9cadff6` · `.venv/bin/python -m eval.latency_budget`
