# Official fee schedules — accessed 2026-10-04

Scope: P6 C5 costs. Rows use only official exchange pages opened in this session. `UNVERIFIED` means the official page failed to open here, rendered no numeric table, or did not clearly match the requested product. Do not use unverified numbers as constants; sweep them as labelled assumptions.

| Venue | Product | Base-tier maker / taker | Best published tier maker / taker (or MM rebate) | URL | Accessed |
|---|---|---:|---:|---|---|
| Binance | Spot | UNVERIFIED | UNVERIFIED | https://www.binance.com/en/fee/trading | 2026-10-04 |
| Binance | USD-M futures | UNVERIFIED | UNVERIFIED | https://www.binance.com/en/fee/futureFee | 2026-10-04 |
| Coinbase Advanced Trade | Spot | UNVERIFIED | UNVERIFIED | https://www.coinbase.com/advanced-fees | 2026-10-04 |
| Coinbase Exchange (related official reference, not Advanced Trade) | Spot | 40 bps / 60 bps | 0 bps / 4 bps for $400M+ 30-day volume | https://help.coinbase.com/en/exchange/trading-and-funding/exchange-fees | 2026-10-04 |
| Kraken Pro | Spot | UNVERIFIED | UNVERIFIED | https://www.kraken.com/features/fee-schedule | 2026-10-04 |
| OKX | Spot | UNVERIFIED | UNVERIFIED | https://www.okx.com/fees | 2026-10-04 |
| OKX | Perpetual swap | UNVERIFIED | UNVERIFIED | https://www.okx.com/fees | 2026-10-04 |
| Bybit | Spot | UNVERIFIED | UNVERIFIED | https://www.bybit.com/en/help-center/article/Trading-Fee-Rates | 2026-10-04 |
| Bybit | Perpetual | UNVERIFIED | UNVERIFIED | https://www.bybit.com/en/help-center/article/Trading-Fee-Rates | 2026-10-04 |
| Bitstamp | Spot | UNVERIFIED | UNVERIFIED | https://www.bitstamp.net/fee-schedule/ | 2026-10-04 |
| Deribit | BTC perpetual | UNVERIFIED | UNVERIFIED | https://support.deribit.com/hc/en-us/articles/25944746248989-Fees | 2026-10-04 |
| Hyperliquid | Perpetual | 0.015% / 0.045% | 0.0000% maker at top tier (−0.002% only via the separate maker-rebate table, >1.5% maker volume share) / 0.0144% taker (Tier 6 + Diamond staking discount) | https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees | 2026-10-04 |
| Hyperliquid | Spot | 0.040% / 0.070% | 0.0000% maker at top tier (−0.002% only via the separate maker-rebate table, >1.5% maker volume share) / 0.0150% taker (Tier 6 + Diamond staking discount) | https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees | 2026-10-04 |
| Gate.io | Spot | UNVERIFIED | UNVERIFIED | https://www.gate.com/fee | 2026-10-04 |
| Gate.io | Futures | UNVERIFIED | UNVERIFIED | https://www.gate.com/fee | 2026-10-04 |
| Bitget | Spot | UNVERIFIED | UNVERIFIED | https://www.bitget.com/fee | 2026-10-04 |
| Bitget | USDT-M futures | UNVERIFIED | UNVERIFIED | https://www.bitget.com/fee | 2026-10-04 |

## Opened-source notes

- The Coinbase Advanced Trade page opened but exposed no numeric fee table in this session. The separate official Coinbase Exchange help page did expose a maker-taker table: $0K-$10K volume is 40 bps maker / 60 bps taker, and $400M+ is 0 bps maker / 4 bps taker. Because the requested product is Advanced Trade, the Advanced Trade row remains `UNVERIFIED`.
- Deribit's official fee page opened and verified the maker-taker model, automated fee tiers, and that negative numbers indicate rebates, but the BTC perpetual numeric table was not captured in the opened content.
- Hyperliquid's official GitBook fee page opened with numeric spot and perps tables. Base tier is Tier 0. The best published taker above uses Tier 6 plus Diamond staking discount as shown in the table; the maker entry uses the separate published maker-rebate table.

## Transfer frictions

Practitioners pre-position inventory on both venues because moving funds is not just a bookkeeping operation: the opened Coinbase Exchange fee page lists fiat deposit/withdrawal charges for wires/SEPA/SWIFT and says crypto withdrawals include a miner/network fee disclosed at transaction time. Those explicit transfer costs, plus the operational delay while funds settle on-chain or through banking rails, can overwhelm a short-lived cross-venue edge; the arbitrage system should therefore assume inventory is already resident on each venue rather than depend on just-in-time transfers.
