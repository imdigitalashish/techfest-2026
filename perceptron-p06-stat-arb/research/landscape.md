# Compiled 2026-10-04 from research/notes/ (sources accessed 2026-10-04)

## 1. Summary: the frontier and where P6 sits

The frontier in cross-asset statistical arbitrage is no longer “find a spread” but “decide whether a stale, noisy, fee-adjusted, size-constrained spread will still exist after the system can act.” The notes point to three overlapping regimes: centralized-exchange latency races measured in milliseconds or less, crypto price-discovery and lead-lag effects across venues, and DeFi/cross-chain arbitrage whose opportunity lives are bounded by block production, settlement and inventory placement. Problem 6 sits at the applied intersection: it does not need to beat Optiver-style production infrastructure, but it can be state-of-the-art for a hackathon by turning each mispricing into a ranked decision with confidence, decay and explicit latency budget. The strongest MVP is therefore not a generic pairs-trading dashboard; it is a receive-time, no-look-ahead system that estimates fair value, subtracts executable costs, models survival over a latency grid, and reports both “trade now” EV and “wait for confirmation” opportunity cost.

## 2. Empirical facts that bound the problem

**Cross-chain and rollup opportunities decay on block/settlement timescales.** Öz et al. study nine blockchains from September 2023 to August 2024 and report 242,535 executed cross-chain arbitrages with $868.64M volume. The notes distinguish pre-positioned inventory arbitrage, settling in about **9 s**, from bridge-based arbitrage, taking about **242 s**. Activity grew **5.5×**; the top five addresses executed over **50%** of trades, and one address reached about **40%** of post-Dencun daily volume. Source: https://arxiv.org/abs/2501.17335. Cross-rollup MEV notes say opportunities persisted on average **10–20 blocks**, captured value was **0.03–0.05%** of trading volume on Arbitrum/Base/Optimism and about **0.25%** on zkSync Era. Source: https://arxiv.org/abs/2406.02172. A zkSync Era study of SyncSwap versus Binance from July to September 2023 finds cumulative Maximal Arbitrage Value of **$104.96k**, or **0.24%** of trading volume, using liquidity-aware MAV instead of a simple mid-price gap. Source: https://arxiv.org/abs/2403.16083.

**Centralized crypto arbitrage is constrained by settlement, counterparty risk and geography.** Bitcoin price differences coincide with high blockchain settlement latency; gaps are smaller between exchange pairs with lower counterparty/default risk (Hautsch, Scheuch & Voigt, "Building Trust Takes Time"). Source: https://arxiv.org/abs/1812.00595. Makarov and Schoar find larger deviations across countries than within countries, smaller deviations between cryptocurrencies, and a common volume factor explaining **80%** of BTC returns across exchanges. Sources: https://researchonline.lse.ac.uk/id/eprint/100409/ and DOI `10.1016/j.jfineco.2019.07.001`. These facts justify P6 separating executable same-asset CEX-CEX spreads from slower transfer/settlement arbitrage.

**Price discovery is venue- and regime-dependent.** Binance generally leads ETH price discovery versus Uniswap v2; CME futures generally lead BTC spot, but leadership becomes mixed during high-volatility periods. The notes cite Hasbrouck Information Share, Gonzalo–Granger Permanent-Transitory decomposition and Hayashi–Yoshida methods. Source: https://arxiv.org/abs/2506.08718. Hoffmann, Rosenbaum and Yoshida estimate lead-lag parameters from nonsynchronous data using contrast optimization with modified Hayashi–Yoshida covariation. Source: https://arxiv.org/abs/1303.4871. A caution: Huth and Abergel report about **60%** directional accuracy for predicting a lagger’s next midquote move, but naïve market-order strategies were not profitable after the bid/ask spread. Source: https://arxiv.org/abs/1111.7103.

**Latency races require message-level thinking.** Aquilina, Budish and O’Neill show that full exchange message data are needed to observe both winners and losers of latency races; ordinary order-book data hide failed attempts. Source: https://www.bis.org/publ/work955.pdf. This is an equities result, but it bounds P6’s evaluation: a feed-only simulator can rank detectable opportunities, while true race participation needs richer execution observations.

**Fees can erase signals.** Coinbase Exchange spot base tier is **40 bps maker / 60 bps taker**; the $400M+ tier is **0 bps maker / 4 bps taker**. Source: https://help.coinbase.com/en/exchange/trading-and-funding/exchange-fees. Hyperliquid perpetuals list base **0.015% maker / 0.045% taker** and a best published taker of **0.0144%**; Hyperliquid spot lists base **0.040% maker / 0.070% taker** and a best taker of **0.0150%** (Tier 6 + Diamond staking). The top tier's maker fee is **0.0000%**; the **−0.002%** maker rebate comes from a *separate* maker-rebate table (for >1.5% maker volume share) — corrected after fact-check. Source: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees. P6 should therefore report retail, VIP and market-maker frontier scenarios separately.

## 3. Methods landscape

**Detection.** The baseline is an executable threshold: compare venue A bid with venue B ask after fair basis, two taker fees, spread, depth/slippage and quote age. A stronger statistical baseline uses rolling z-scores around a basis estimate, cointegration residuals or Ornstein–Uhlenbeck half-life estimates. A Kalman/local-level basis handles drifting venue premia without hard resets. The detector should keep lanes separate: same-asset CEX-CEX, spot-perp basis and BTC/ETH residual relationships do not share the same economics.

**Fair value and lead-lag.** The notes’ component plan uses rolling median basis over **60 s**, rolling MAD volatility, asynchronous lead-lag diagnostics, Kalman/local-level basis, microprice and Hayashi–Yoshida candidates. The key invariant is receive-time as-of state: do not join on future exchange timestamps. Track `ts_exch_us`, `ts_recv_us`, quote age and `max_age_us`; preserve gaps, reconnects, timestamp disorder, duplicates and crossed-book drops. A useful component metric is out-of-sample next-**100 ms** basis RMSE in bps.

**Decay and survival.** The natural target is not “was there a spread?” but “was it still profitable at latency L after costs?” Kaplan–Meier curves by venue pair and edge bucket can report median lifetime, P90 lifetime, survival at latency grid points and `edge(t)/edge(0)`. A discrete hazard model or gradient-boosted survival model can upgrade the same interface. The notes propose held-out integrated Brier score as a decay metric.

**Decisions under latency.** P6 can make the latency trade-off explicit with the notes’ decision rule: `EV_now = S(L|x) * (edge - cost) - (1 - S(L|x)) * lambda`. Compare acting now with confirmation delays such as `{0, 1, 2, 5, 10, 25, 50} ms`; rank by EV under inventory caps. This creates a clear story for the challenge statement: confidence is valuable only if the opportunity survives the extra delay.

**Simulation with latency.** Decisions should use receive-time state; fills should use exchange-time truth at `t_decide + L_order`. Model IOC fills, partial displayed size, one-leg fills and unwind latency/loss. Sweep latency `{0, 100 µs, 500 µs, 1, 5, 10, 50, 100, 500 ms, 1 s}` and fee tiers. Report net PnL/day, oracle capture ratio, calibration, regime slices and dependence-aware confidence intervals. hftbacktest is directly relevant because it models feed latency, order-entry latency, response latency, queue position, L2/L3 reconstruction and multi-asset/multi-exchange backtests. Sources: https://github.com/nkaz001/hftbacktest, https://hftbacktest.readthedocs.io/en/latest/, https://github.com/nkaz001/hftbacktest/blob/v1.8.4/docs/latency_models.rst. NautilusTrader contributes a production-style research/simulation/live architecture with nanosecond-resolution event-driven simulation and common research/live code paths. Sources: https://nautilustrader.io/docs/latest/, https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/execution-flow.md, https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/fill-prices-and-matching.md.

## 4. What companies ship today

| Company / product | What they ship | How, publicly documented | Latency scale | Source URL | What P6 borrows / where P6 beats or complements |
|---|---|---|---|---|---|
| **Optiver** | Market-making and trading expertise relevant to latency-aware pricing and arbitrage. | Notes did not verify public headline system numbers. | Exact ns/µs figures from an Optiver C++ latency talk are **UNVERIFIED**. | No verified primary URL in notes for headline numbers. | P6 borrows the framing: price dislocations must be ranked under latency and execution constraints. P6 complements by producing an open, explainable hackathon simulator and decay report rather than claiming production speed. |
| **Tardis.dev** | Tick-level historical crypto data: L2 updates, L2/L3 snapshots, trades, quotes, options, funding and liquidations. | Provides exchange `timestamp` and collector `local_timestamp` (column names confirmed in our downloaded CSV headers); preserves connection drops, publishing delays, duplicate trades and crossed books. | One Deribit sample implies about **14 ms** exchange-to-collector latency. | https://tardis.dev/; https://docs.tardis.dev/faq/data; https://docs.tardis.dev/faq/order-books; https://docs.tardis.dev/historical-data-details/overview | P6 borrows timestamp discipline and dirty-feed realism; P6 adds survival/EV ranking on top of recorded feeds. |
| **Databento** | Market data sourced from colocation sites, with real-time and historical APIs across equities, futures and options. | Public notes verify colocation-sourced data but not exact timestamp semantics beyond opened source fragments. | Pricing/precise timestamp semantics are **UNVERIFIED** in notes. | https://databento.com/about | P6 borrows the “data infrastructure first” lesson; P6 can beat a data-only story by showing decision quality under latency budgets. |
| **hftbacktest** | Open-source HFT backtesting with latency and queue modeling. | Feed latency, order-entry latency, response latency, queue position, L2/L3 reconstruction and multi-asset/multi-exchange backtests; same strategy code live on Binance Futures and Bybit. | Explicit feed/order/response latency models; user-specified scale. | https://github.com/nkaz001/hftbacktest; https://hftbacktest.readthedocs.io/en/latest/; https://github.com/nkaz001/hftbacktest/blob/v1.8.4/docs/latency_models.rst | P6 should borrow latency-model concepts; P6 complements by specializing in cross-asset mispricing ranking and decay explanation. |
| **NautilusTrader** | Multi-asset, multi-venue research, deterministic simulation and live execution engine. | Rust-native engine with common research/live code paths and documented fill/matching flow. | Nanosecond-resolution event-driven simulation. | https://nautilustrader.io/docs/latest/; https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/execution-flow.md; https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/fill-prices-and-matching.md | P6 borrows deterministic replay and live/replay parity; P6 beats on challenge-specific explainability and latency-budget visualizations. |
| **cryptofeed** | Normalized multi-exchange crypto market-data feeds. | Trades, L1/L2/L3 books, funding, liquidations, indices, candles; synthetic NBBO aggregation and zstd-compressed pcap recording/replay. | Feed latency not quantified in notes. | https://github.com/bmoscon/cryptofeed | P6 can use the same normalized-feed idea; P6 adds cost-aware detection and decay modeling. |
| **CCXT / CCXT Pro** | Unified REST/WebSocket exchange connectivity to **100+ exchanges**. | Docs and blog recommend inventory-based arbitrage with assets pre-positioned because transfers take minutes to hours. | Transfers: minutes to hours per CCXT guidance. | https://docs.ccxt.com/#/README; https://docs.ccxt.com/#/pro; https://docs.ccxt.com/blog/crypto-arbitrage-strategies | P6 borrows pre-positioned inventory assumptions and avoids pretending transfer arbitrage is millisecond arbitrage. |
| **Hummingbot** | Open-source trading bots and arbitrage executors. | ArbitrageExecutor trades interchangeable pairs across two markets, checks balances and transaction costs, and requires profitability above a threshold; AMM arbitrage covers CEX/DEX, gas, fees, slippage buffers and concurrent orders. | No precise latency number in notes. | https://hummingbot.org/strategies/v2-strategies/executors/arbitrage-executor/; https://hummingbot.org/strategies/v1-strategies/amm-arbitrage/ | P6 borrows the threshold-plus-cost baseline; P6 improves by estimating opportunity decay and ranking by latency-adjusted EV. |
| **Hyperliquid** | Venue APIs, latency guidance and fee schedules. | API-server, mempool and HyperBFT commit latency are part of execution; `split_client_blocks: true` may improve read latency by **70–150 ms**; maker protection prioritizes cancels and ALO orders over IOC/GTC orders sent at the same time. | Tens to hundreds of milliseconds for documented read-latency improvement. | https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/optimizing-latency; https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees | P6 borrows end-to-end latency decomposition and fee tiers; P6 can compare survival at those latency deltas. |
| **AWS / Avelacom** | Ultra-low-latency cross-region crypto trading network design. | Tokyo RTT measurements compare VPC peering with Direct Connect+Avelacom. | Singapore **68.0 vs 65.4 ms**; Virginia **150.2 vs 135.4 ms**; Frankfurt **224.3 vs 136.5 ms**; London **210.0 vs 139.6 ms**; Stockholm **245.3 vs 124.3 ms** (per-route figures from the original note; only the headline "up to 49%" was re-verified). P99 tracked P50; jitter below **90 µs**. | https://aws.amazon.com/blogs/industries/ultra-low-latency-cross-region-crypto-trading-with-avelacom-and-aws/ | P6 borrows realistic geography budgets and can show which opportunities survive retail cloud versus optimized routes. |
| **Glassnode Latency Monitor** | Public venue latency monitoring. | Measures WebSocket/FIX and validator/sequencer paths across Binance, Coinbase, Kraken, OKX, Bybit, Deribit and other venues; emphasizes geographic placement can cost tens to hundreds of milliseconds. | Tens to hundreds of milliseconds by placement. | https://latency.glassnode.com/; https://latency.glassnode.com/hyperliquid/fill-latency | P6 borrows latency observability and can integrate survival curves with measured path delays. |
| **Flashbots Protect** | Private transaction routing for Ethereum users. | Private mempool RPC `https://rpc.flashbots.net/fast`; hides transactions from frontrunning/sandwich bots, refunds gas on high priority fees and excludes reverting transactions without charging a fee. | No numeric latency in notes. | https://docs.flashbots.net/flashbots-protect/overview | P6 borrows private-routing awareness for DEX/MEV lanes; P6 remains focused on ranking mispricings rather than protecting arbitrary swaps. |

## 5. Gaps and P6 novelty claims

**Well-known, not novel.** Threshold arbitrage, z-scores, cointegration, OU mean reversion, Kalman fair value, lead-lag tests, maker/taker fee adjustment and event-driven backtesting are standard. Hummingbot already ships threshold-based arbitrage executors. hftbacktest and NautilusTrader already model latency and deterministic replay. Tardis.dev and cryptofeed already provide or normalize market data.

**Potentially novel for the hackathon.** P6’s novelty is packaging these ideas into a single mispricing-ranking surface: receive-time state, no-look-ahead joins, executable cost subtraction, survival probability by latency, and EV comparison between “act now” and “wait for confirmation.” The key differentiator is not claiming a new statistical arbitrage model; it is reporting how fast each opportunity decays and how much expected value is lost at 100 µs, 1 ms, 10 ms, 100 ms or 1 s.

**Critical gaps.** The notes did not verify a crypto CEX-CEX equivalent of the equities latency-race evidence where both winners and losers are observable. That means P6 should avoid overclaiming race win rates from order-book data alone. Fee schedules are incomplete: Binance, Coinbase Advanced Trade, Kraken, OKX, Bybit, Bitstamp, Deribit, Gate.io and Bitget numeric schedules remain **UNVERIFIED**. Optiver public production latency/headline metrics are also **UNVERIFIED**, so the write-up should not benchmark against unnamed internal systems.

## 6. UNVERIFIED leads (carried over verbatim from the notes)

- “Gap: I could not locate a primary Optiver page with headline numbers like ‘10M trades/day across 100+ exchanges’ (this figure surfaced only via a secondary AI-search summary, not an opened primary page) — **UNVERIFIED, do not cite without opening an Optiver page that states it directly.**”

- “Block-latency figures (~70ms–200ms, ‘sub-second’ finality, one-block finality) surfaced only via secondary summaries in this pass — **UNVERIFIED against a primary Hyperliquid page**…”

- “Tardis.dev / Databento / Kaiko: none of the three pricing pages rendered usable fee/subscription numbers on this pass … — **all three UNVERIFIED**…”

- “MEV-Share order-flow-auction specifics remain **UNVERIFIED**, retry directly.”

- “Exact ns/µs figures” from the Optiver C++ latency talk are **UNVERIFIED** until the video is watched directly.

- Databento exact timestamp semantics beyond opened source-code comments/fragments remain **UNVERIFIED**.

- “SSRN 5262988 / arXiv (Dai, Li, Yang), ‘Arbitrage in Perpetual Contracts’ (2025) — found via search summary only … claims about model-free no-arbitrage bounds for perpetuals and Binance 2023–2025 evidence are unverified.”

- “`clawrxiv.io/abs/2604.01454`, cited in a search summary as ‘Latency Arbitrage Profits Decreased 73% After Exchange Speed Bump...’ — this domain does not correspond to a known, recognized preprint archive … **Flagged as a likely unreliable/fabricated-looking citation; excluded entirely from the cited findings above.**”

- “Hasbrouck (1995) ‘92.7% median information share for NYSE’ figure … should be treated as a secondary-source figure pending direct verification against the original tables…”

- “No equity-style message-level latency-race study for CEX-CEX crypto markets” was found in the opened primary literature.

- “No unified cross-regime decay model” spanning CEX-CEX, CEX-DEX and cross-chain arbitrage was found.

- Conformal survival finite-sample coverage claims are **UNVERIFIED**; the opened page exposed only the title: https://arxiv.org/abs/2103.09763

- Specific DeepHit, AFT, D-calibration-formula and classical limit-order Cox-fill claims are **UNVERIFIED**.

- Reddit endpoints redirected to login (`reason=lor2`); no Reddit claims are cited.

- Kaggle winner techniques were not sufficiently rendered and remain **UNVERIFIED**.

- X/Twitter searches were empty or rate-limited; no X claims are cited.


## Fact-check (independent agent, 2026-10-04 ~07:45 IST)
Eight load-bearing claims were re-opened at their sources. The fact-check agent was asked to treat arXiv 1812.00595 and Makarov & Schoar as one claim; this document already cites them as separate papers.

| Claim | Verdict | Action |
|---|---|---|
| Coinbase Exchange fees 40/60 bps base, 0/4 bps at $400M+ | PASS | — |
| Hyperliquid best-tier maker −0.002% | PARTIAL | Corrected above: the top tier is 0.0000% maker; −0.002% is a separate rebate table |
| Aquilina–Budish–O'Neill: message data reveal race winners and losers | PASS | URL added |
| arXiv 1812.00595 settlement-latency claim | PARTIAL (authorship) | Authors named above; Makarov & Schoar is cited separately |
| Tardis preserves drops/duplicates/crossed books; dual timestamps | PARTIAL | Column names confirmed from our CSVs |
| hftbacktest models feed/order/response latency | PASS | — |
| AWS/Avelacom cross-region RTT "up to 49%" | PARTIAL | Headline verified; per-route numbers marked as not re-verified |
| CME futures generally lead BTC spot; mixed in high volatility (arXiv 2506.08718) | PASS | — |
