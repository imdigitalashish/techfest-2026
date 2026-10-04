# Publication cadence of our live recorder's channels (venue timestamps)

Live recording of 2026-10-04, 3.2 h. Compare with the Tardis `quotes` samples in `update_cadence.md`.

| leg (our channel) | rows | median gap (ms) | p10 gap (ms) | share < 10 ms |
|---|---|---|---|---|
| binance-futures:BTCUSDT | 1,424,023 | 2.0 | 1.0 | 0.698 |
| binance-futures:ETHUSDT | 1,063,371 | 3.0 | 1.0 | 0.649 |
| bybit:BTCUSDT | 81,015 | 50.0 | 10.0 | 0.095 |
| bybit:ETHUSDT | 113,820 | 41.0 | 10.0 | 0.061 |
| coinbase:BTC-USD | 31,291 | 327.5 | 24.5 | 0.061 |
| coinbase:ETH-USD | 11,972 | 845.4 | 5.6 | 0.117 |
| coinbase:USDT-USD | 2,925 | 2064.0 | 47.3 | 0.085 |
| deribit:BTC-PERPETUAL | 51,772 | 44.0 | 10.0 | 0.057 |
| kraken:BTC/USD | 156,755 | 3.3 | 0.1 | 0.579 |
| kraken:USDT/USD | 5,424 | 326.9 | 0.1 | 0.324 |
| okx:BTC-USDT | 43,019 | 30.0 | 10.0 | 0.000 |
| okx:BTC-USDT-SWAP | 230,183 | 20.0 | 10.0 | 0.000 |
| okx:ETH-USDT-SWAP | 244,815 | 20.0 | 10.0 | 0.000 |

Commit `1e3aa26` · `.venv/bin/python -m eval.live_cadence`
