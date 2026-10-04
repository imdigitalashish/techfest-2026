# Feed latency from the Mac in India (live recorder)

Rows: 1,861,180 quotes over 1.31 h; venues without a venue timestamp are excluded. Latency = receive − venue timestamp (ms); includes Mac clock offset (sntp log below).

| leg | n | p05 | p50 | p95 | p99 | share < 0 |
|---|---|---|---|---|---|---|
| binance-futures:BTCUSDT | 721,037 | 90.2 | 3437.0 | 11934.9 | 16821.0 | 0.000 |
| binance-futures:ETHUSDT | 447,289 | 88.2 | 3647.8 | 14173.4 | 18308.2 | 0.000 |
| bitget:BTCUSDT | 13,941 | 74.9 | 3167.9 | 14259.7 | 20585.9 | 0.000 |
| bybit-spot:BTCUSDT | 27,440 | 17.5 | 1987.6 | 12501.9 | 19855.0 | 0.025 |
| bybit:BTCUSDT | 33,762 | -8.9 | 13.8 | 1886.6 | 3983.0 | 0.289 |
| bybit:ETHUSDT | 49,064 | -8.7 | 13.3 | 1727.9 | 3744.1 | 0.287 |
| coinbase:BTC-USD | 14,844 | 106.7 | 134.4 | 1119.5 | 3784.6 | 0.000 |
| coinbase:ETH-USD | 5,157 | 106.0 | 140.8 | 1214.0 | 3686.1 | 0.000 |
| coinbase:USDT-USD | 1,118 | 105.0 | 132.6 | 1252.2 | 3946.8 | 0.000 |
| deribit:BTC-PERPETUAL | 23,414 | 69.4 | 97.7 | 976.8 | 2834.1 | 0.000 |
| gateio:BTC_USDT | 7,258 | 90.3 | 2815.4 | 9645.6 | 12793.8 | 0.000 |
| hyperliquid:BTC | 17,196 | 209.4 | 262.5 | 979.0 | 2723.4 | 0.000 |
| kraken:BTC/USD | 71,866 | 78.5 | 112.5 | 1693.1 | 4400.2 | 0.000 |
| kraken:USDT/USD | 2,532 | 77.6 | 108.3 | 1711.2 | 4926.2 | 0.000 |
| okx:BTC-USDT | 22,455 | 25.0 | 49.1 | 2281.3 | 5683.3 | 0.000 |
| okx:BTC-USDT-SWAP | 108,288 | 23.8 | 52.3 | 2567.4 | 6226.9 | 0.000 |
| okx:ETH-USDT-SWAP | 90,528 | 23.4 | 51.8 | 2702.0 | 6788.2 | 0.000 |

sntp offset log (local − reference):

- `1791071635188423000	+0.022856 +/- 0.170171 time.apple.com 2a01:b740:a14:3000::22`
- `1791072240169617000	+0.010906 +/- 0.319658 time.apple.com 2a01:b740:a14:4000::22`
- `1791072845767179000	-0.114425 +/- 0.553879 time.apple.com 2403:300:a26:3000::31`
- `1791073450010459000	-0.008260 +/- 0.299181 time.apple.com 2a01:b740:a14:4000::22`
- `1791074059674693000	}`
- `1791074666683985000	}`

Command: `.venv/bin/python -m eval.live_latency`
