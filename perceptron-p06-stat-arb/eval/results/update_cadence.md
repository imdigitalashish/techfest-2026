# Quote update cadence in the Tardis samples (2026-10-01)

Gaps between consecutive distinct exchange timestamps. A venue on a 100 ms grid cannot show a mispricing closing faster than its next publication, so millisecond lifetimes are measured at this resolution.

| leg | rows | median gap (ms) | p10 gap (ms) | min gap (ms) | share on 100 ms grid | share < 10 ms |
|---|---|---|---|---|---|---|
| binance_BTCUSDT | 595,066 | 100.1 | 99.8 | 6.62 | 0.996 | 0.000 |
| binance-futures_BTCUSDT | 1,848,343 | 26.0 | 26.0 | 26.00 | 0.000 | 0.000 |
| coinbase_BTC-USD | 2,292,710 | 3.3 | 0.3 | 0.00 | 0.359 | 0.668 |
| okex_BTC-USDT | 366,406 | 100.0 | 100.0 | 20.00 | 1.000 | 0.000 |
| okex-swap_BTC-USDT-SWAP | 733,362 | 100.0 | 100.0 | 20.00 | 1.000 | 0.000 |
| bybit_BTCUSDT | 1,311,333 | 39.0 | 20.0 | 4.00 | 0.063 | 0.000 |
| kraken_BTC-USD | 887,213 | 12.8 | 0.3 | 0.00 | 0.309 | 0.476 |
| bitstamp_BTCUSD | 122,835 | 328.0 | 325.4 | 188.72 | 0.006 | 0.000 |
| deribit_BTC-PERPETUAL | 1,023,962 | 22.0 | 10.0 | 1.00 | 0.013 | 0.069 |

Commit `0ca23e8` · `.venv/bin/python -m eval.update_cadence --date 2026-10-01`
