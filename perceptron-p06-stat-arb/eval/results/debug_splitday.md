# Baseline results — train 2026-09-01 → test 2026-09-01 12-24h (train 0-12h)

Legs: binance-futures:BTCUSDT, binance:BTCUSDT, coinbase:BTC-USD, okex:BTC-USDT. Detection threshold 1.0 bps over the fair basis. Fees verified: False. Size cap 0.05 BTC.

Assumptions: inventory pre-positioned on every venue (no transfers); order one-way latency = feed one-way latency = δ for every venue (colo-style sweep); IOC limit legs fill only if the exchange-time top of book is at/through our limit; size capped at top-of-book; unfilled-leg mismatch unwound on the same venue 2·δ later at top of book, paying taker fee; P&L marked against the EWMA fair basis observed at decision time; retail/vip fees are placeholders until research/notes/fees.md is verified; mm = 0 bps.

## Decay (MVP): episode lifetimes on the exchange clock, test day

| group | n | half-life (ms) | t at S=0.9 (ms) | t at S=0.1 (ms) | S(1ms) | S(10ms) | S(100ms) | mean edge0 (bps) |
|---|---|---|---|---|---|---|---|---|
| all | 41997 | 31.1 | 2.12 | 649 | 0.958 | 0.696 | 0.270 | 1.28 |
| spot-spot | 27390 | 22.7 | 1.98 | 794 | 0.953 | 0.643 | 0.305 | 1.28 |
| spot-perp | 14607 | 40.3 | 3 | 416 | 0.968 | 0.796 | 0.205 | 1.28 |
| same-ccy | 15780 | 45 | 8 | 949 | 0.993 | 0.807 | 0.318 | 1.38 |
| USD-vs-USDT | 26217 | 24.4 | 1.65 | 509 | 0.937 | 0.630 | 0.241 | 1.21 |
| 1-2bps | 40219 | 31 | 2.1 | 658 | 0.957 | 0.694 | 0.270 | 1.21 |
| 2-5bps | 1730 | 32.5 | 4.46 | 509 | 0.973 | 0.740 | 0.272 | 2.56 |
| 5-10bps | 43 | 100 | 17.6 | 269 | 1.000 | 1.000 | 0.535 | 6.22 |
| coinbase:BTC-USD > binance:BTCUSDT | 6936 | 24 | 1.73 | 716 | 0.944 | 0.608 | 0.283 | 1.16 |
| binance:BTCUSDT > coinbase:BTC-USD | 6471 | 30.2 | 1.75 | 820 | 0.939 | 0.661 | 0.306 | 1.18 |
| okex:BTC-USDT > coinbase:BTC-USD | 4212 | 19.3 | 1.53 | 263 | 0.930 | 0.610 | 0.185 | 1.26 |
| coinbase:BTC-USD > okex:BTC-USDT | 3383 | 20.7 | 1.67 | 400 | 0.938 | 0.609 | 0.213 | 1.26 |
| binance:BTCUSDT > okex:BTC-USDT | 3281 | 12.5 | 8.29 | 1.41e+03 | 1.000 | 0.689 | 0.440 | 1.52 |
| okex:BTC-USDT > binance:BTCUSDT | 3107 | 13.3 | 8.24 | 1.5e+03 | 1.000 | 0.715 | 0.469 | 1.49 |
| binance-futures:BTCUSDT > coinbase:BTC-USD | 3025 | 24.5 | 1.44 | 210 | 0.927 | 0.632 | 0.162 | 1.23 |
| binance:BTCUSDT > binance-futures:BTCUSDT | 2891 | 54.4 | 10.4 | 638 | 0.984 | 0.906 | 0.245 | 1.29 |
| binance-futures:BTCUSDT > binance:BTCUSDT | 2791 | 56.5 | 10.4 | 825 | 0.984 | 0.906 | 0.280 | 1.26 |
| coinbase:BTC-USD > binance-futures:BTCUSDT | 2190 | 28.1 | 1.67 | 312 | 0.939 | 0.667 | 0.174 | 1.26 |
| okex:BTC-USDT > binance-futures:BTCUSDT | 1870 | 37 | 6 | 260 | 0.993 | 0.845 | 0.166 | 1.34 |
| binance-futures:BTCUSDT > okex:BTC-USDT | 1840 | 37 | 5 | 291 | 0.993 | 0.827 | 0.175 | 1.30 |

Edge-magnitude decay E[edge(t0+Δ)/edge(t0)]:

| Δ (ms) | mean | median | share still > 0 |
|---|---|---|---|
| 0.1 | 0.998 | 1.000 | 0.999 |
| 0.5 | 0.994 | 1.000 | 0.997 |
| 1 | 0.983 | 1.000 | 0.995 |
| 2 | 0.966 | 1.000 | 0.992 |
| 5 | 0.926 | 1.000 | 0.978 |
| 10 | 0.872 | 1.000 | 0.966 |
| 20 | 0.798 | 1.000 | 0.940 |
| 50 | 0.666 | 0.817 | 0.889 |
| 100 | 0.579 | 0.688 | 0.856 |
| 250 | 0.477 | 0.535 | 0.821 |
| 500 | 0.424 | 0.471 | 0.795 |
| 1000 | 0.348 | 0.379 | 0.759 |

## Survival models (train → test)

| model | IBS (log-t, lower better) | C-index |
|---|---|---|
| Kaplan–Meier | 0.1252 | 0.500 |
| Weibull AFT (covariates) | 0.1308 | 0.510 |

Weibull shape ρ = 0.445 (ρ < 1 ⇒ decreasing hazard: young crosses die fastest). EV evaluation cost: 26.84 µs per opportunity (numpy, M5).

## Policy frontier (test day, simulated fills)

| tier | δ one-way (ms) | policy | trades | both-fill | PnL (USD) | mean bps | hit | capture |
|---|---|---|---|---|---|---|---|---|
| retail | 0 | oracle | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 0 | naive | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 0 | threshold | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 0 | ev_km | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 0 | ev_aft | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 0 | ev_wait_aft | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 1 | naive | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 1 | threshold | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 1 | ev_km | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 1 | ev_aft | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 1 | ev_wait_aft | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 10 | naive | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 10 | threshold | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 10 | ev_km | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 10 | ev_aft | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 10 | ev_wait_aft | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 100 | naive | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 100 | threshold | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 100 | ev_km | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 100 | ev_aft | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| retail | 100 | ev_wait_aft | 0 | 0.000 | 0.00 | 0.000 | 0.000 |  |
| vip | 0 | oracle | 394 | 1.000 | 105.04 | 0.882 | 1.000 |  |
| vip | 0 | naive | 394 | 1.000 | 105.04 | 0.882 | 1.000 | 1.000 |
| vip | 0 | threshold | 394 | 1.000 | 105.04 | 0.882 | 1.000 | 1.000 |
| vip | 0 | ev_km | 394 | 1.000 | 105.04 | 0.882 | 1.000 | 1.000 |
| vip | 0 | ev_aft | 394 | 1.000 | 105.04 | 0.882 | 1.000 | 1.000 |
| vip | 0 | ev_wait_aft | 394 | 1.000 | 105.04 | 0.882 | 1.000 | 1.000 |
| vip | 1 | naive | 394 | 0.980 | 95.10 | 0.799 | 0.980 | 0.905 |
| vip | 1 | threshold | 394 | 0.980 | 95.10 | 0.799 | 0.980 | 0.905 |
| vip | 1 | ev_km | 291 | 0.976 | 93.14 | 1.057 | 0.976 | 0.887 |
| vip | 1 | ev_aft | 168 | 0.988 | 84.62 | 1.652 | 0.988 | 0.806 |
| vip | 1 | ev_wait_aft | 239 | 0.908 | 76.91 | 0.992 | 0.908 | 0.732 |
| vip | 10 | naive | 394 | 0.343 | -179.20 | -1.553 | 0.343 | -1.706 |
| vip | 10 | threshold | 47 | 0.617 | 19.10 | 1.220 | 0.617 | 0.182 |
| vip | 10 | ev_km | 51 | 0.608 | 19.11 | 1.084 | 0.608 | 0.182 |
| vip | 10 | ev_aft | 53 | 0.623 | 16.99 | 1.217 | 0.623 | 0.162 |
| vip | 10 | ev_wait_aft | 65 | 0.477 | 1.05 | -0.280 | 0.492 | 0.010 |
| vip | 100 | naive | 394 | 0.005 | -261.93 | -2.168 | 0.018 | -2.494 |
| vip | 100 | threshold | 9 | 0.000 | -5.41 | -1.551 | 0.111 | -0.051 |
| vip | 100 | ev_km | 4 | 0.000 | -0.86 | -0.560 | 0.000 | -0.008 |
| vip | 100 | ev_aft | 5 | 0.000 | -3.86 | -1.990 | 0.000 | -0.037 |
| vip | 100 | ev_wait_aft | 7 | 0.000 | -5.82 | -4.071 | 0.143 | -0.055 |
| mm | 0 | oracle | 41997 | 0.999 | 11649.93 | 1.274 | 0.999 |  |
| mm | 0 | naive | 41997 | 0.998 | 11639.92 | 1.273 | 0.998 | 0.999 |
| mm | 0 | threshold | 41997 | 0.998 | 11639.92 | 1.273 | 0.998 | 0.999 |
| mm | 0 | ev_km | 41997 | 0.998 | 11639.92 | 1.273 | 0.998 | 0.999 |
| mm | 0 | ev_aft | 41997 | 0.998 | 11639.92 | 1.273 | 0.998 | 0.999 |
| mm | 0 | ev_wait_aft | 41971 | 0.999 | 11640.98 | 1.274 | 0.999 | 0.999 |
| mm | 1 | naive | 41997 | 0.906 | 10578.95 | 1.151 | 0.906 | 0.908 |
| mm | 1 | threshold | 41997 | 0.906 | 10578.95 | 1.151 | 0.906 | 0.908 |
| mm | 1 | ev_km | 41997 | 0.906 | 10578.95 | 1.151 | 0.906 | 0.908 |
| mm | 1 | ev_aft | 41990 | 0.906 | 10579.19 | 1.152 | 0.906 | 0.908 |
| mm | 1 | ev_wait_aft | 41970 | 0.906 | 10580.90 | 1.153 | 0.907 | 0.908 |
| mm | 10 | naive | 41997 | 0.576 | 5830.49 | 0.679 | 0.588 | 0.500 |
| mm | 10 | threshold | 41997 | 0.576 | 5830.49 | 0.679 | 0.588 | 0.500 |
| mm | 10 | ev_km | 41997 | 0.576 | 5830.49 | 0.679 | 0.588 | 0.500 |
| mm | 10 | ev_aft | 41969 | 0.576 | 5839.92 | 0.680 | 0.589 | 0.501 |
| mm | 10 | ev_wait_aft | 41385 | 0.577 | 5832.33 | 0.682 | 0.590 | 0.501 |
| mm | 100 | naive | 41997 | 0.167 | 796.33 | 0.097 | 0.239 | 0.068 |
| mm | 100 | threshold | 41997 | 0.167 | 796.33 | 0.097 | 0.239 | 0.068 |
| mm | 100 | ev_km | 41997 | 0.167 | 796.33 | 0.097 | 0.239 | 0.068 |
| mm | 100 | ev_aft | 41836 | 0.167 | 819.67 | 0.099 | 0.239 | 0.070 |
| mm | 100 | ev_wait_aft | 31621 | 0.188 | 871.52 | 0.127 | 0.251 | 0.075 |

Runtime 33 s. Commit `2d09756`. Command: `python -m eval.run_baseline --train 2026-09-01 --split-day --legs binance_BTCUSDT,binance-futures_BTCUSDT,coinbase_BTC-USD,okex_BTC-USDT --deltas 0 1 10 100 --out eval/results/debug_splitday`
