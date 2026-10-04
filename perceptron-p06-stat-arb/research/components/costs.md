# C5 costs — execution-cost modelling for cross-venue arbitrage

## 1) Contract summary

C5 returns the cost in bps for `(venue, product, tier, side, liquidity='taker')`. In the architecture contract, C5's baseline is official fee schedules, with tiers `retail` = base tier, `vip` = top published tier, and `mm` = 0 bps as a zero-fee frontier; its isolated metric is exact unit-test agreement with the cited fee tables in `research/notes/fees.md`.

## 2) Opened-source facts

- Crypto venues use maker-taker schedules and fee tiers, so a cross that is profitable for a market maker or high-volume account may be untradeable at retail taker rates. Opened examples: Coinbase Exchange shows 40/60 bps maker/taker at $0K-$10K and 0/4 bps at $400M+; Deribit describes automated fee tiers and negative values as rebates; Hyperliquid publishes separate spot/perp tier tables plus maker rebates.
- Product matters. Hyperliquid's opened table has different base fees for perps (0.015% maker / 0.045% taker) and spot (0.040% maker / 0.070% taker), so C5 must key by `(venue, product)` rather than venue alone.
- Size matters. The architecture defines C3 top-of-book bid/ask sizes and C5 says size limits come from quote sizes; C9 then fills order intents at order-arrival exchange time and records legging loss for missed legs.
- Transfer costs are outside immediate execution but affect deployability: the opened Coinbase Exchange fee page lists fiat transfer charges and crypto miner/network fees, supporting the operational assumption that inventory should be pre-positioned.

## 3) State of the art cost stack for this problem

A practical cross-venue arbitrage cost model should evaluate the full executable stack, not just a raw mid-price difference:

1. **Two taker fees.** For the baseline problem statement, net edge is gross cross minus the buy-leg taker fee and sell-leg taker fee. Fee tier selection is often decisive.
2. **Half-spread / crossing cost.** Using `sell at bid_A` and `buy at ask_B` already pays the spread relative to each venue mid. The detector should therefore compute executable crosses from bid/ask, not mid/mid.
3. **Size-limited top-of-book.** The immediately executable notional is bounded by `min(bid_size_sell, ask_size_buy)` from C3. Larger notional must either be clipped or charged with deeper-book slippage.
4. **Slippage beyond top of book.** If order size exceeds top-of-book quantity, the marginal execution price walks the book. The current C3 contract has only top-of-book, so beyond-TOB slippage is not in the MVP unless deeper book data is added.
5. **Funding/carry for perps.** Spot-perp and perp-perp crosses need funding-rate/carry treatment when positions can remain open. Same-instant two-leg arbitrage can start with taker fees plus executable bid/ask, but any inventory-holding policy must accrue or forecast funding.
6. **Legging risk under latency.** C9 explicitly models arrival at `t_decide + L_order[v]`; if one IOC leg fills and the other misses, the simulator unwinds and charges the resulting loss. That loss should feed C8 as `lambda` and can dominate small fee-adjusted edges.

## 4) Baseline we use

For MVP C5:

- Store fee schedules from `research/notes/fees.md` with provenance, access date, product, tier, maker bps, taker bps, and verification status.
- Use `retail` = base-tier taker fees where verified; otherwise label the venue/product assumption and include it only in sweeps, not as a claimed fact.
- Use `vip` = best published tier from official pages where verified; otherwise leave `UNVERIFIED`.
- Use `mm` = 0 bps as the contract's upper-bound frontier, not as a claim about any venue.
- Compute same-asset cross net edge as `sell_bid - buy_ask - sell_taker_fee - buy_taker_fee`, capped at top-of-book size.
- Let C9, not C5, realize latency and legging losses; C5 provides deterministic per-leg cost inputs.

## 5) Innovation candidates

Scores: 1 = weak, 5 = strong.

| Candidate | Description | Impact | Novelty | Feasibility by Dec | Measurability | Demoability | Isolated metric |
|---|---|---:|---:|---:|---:|---:|---|
| Fee-tier frontier | Evaluate every opportunity under retail, verified VIP, and `mm=0` to show when fees erase the edge. | 5 | 2 | 5 | 5 | 5 | Difference in tradeable opportunity count and net PnL/day across fee tiers. |
| Depth-aware cost curve | Replace top-of-book clipping with a piecewise price-impact curve when L2 depth is available. | 4 | 3 | 3 | 5 | 4 | Slippage MAE in bps between predicted cost and replayed book-walk fill cost. |
| Latency-conditioned legging reserve | Add a pair/venue-specific reserve equal to predicted p90 missed-leg unwind loss. | 5 | 4 | 4 | 5 | 5 | Calibration error of predicted p90 legging loss and PnL drawdown reduction. |
| Funding-aware perp cost | Accrue expected funding/carry for opportunities that may remain open beyond immediate IOC arbitrage. | 3 | 3 | 3 | 4 | 3 | Funding-adjusted PnL error versus realized funding events for perp positions. |

Best near-term candidate: **fee-tier frontier**, because it directly answers the problem's fee-tier sensitivity requirement and is fully measurable once fee tables are verified. Best differentiator if data permits: **latency-conditioned legging reserve**, because it connects C5 costs to C7/C8 latency survival instead of treating cost as static.

## 6) Risks and tests

- **Unverified fee tables:** do not silently default to remembered fees. Unit tests should fail or skip with `UNVERIFIED` provenance until a source row is verified.
- **Double-counting spread:** if C6 uses bid/ask crosses, C5 should add explicit fees but not another half-spread penalty for the same top-of-book execution.
- **Fee units:** store bps internally; parse `%` and bps inputs with tests.
- **Product mismatch:** spot, USD-M futures, linear swaps, and BTC perpetuals can have different schedules even at the same venue.
- **Tier mismatch:** account-level VIP, staking, and maker rebates may be conditional. The `vip` tier should preserve the eligibility note from the source.
- **Latency/cost coupling:** legging reserves should be estimated by C9/C8 from simulated missed legs, not hard-coded in C5.
