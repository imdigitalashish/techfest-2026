# C9 sim — latency-injected event-driven simulator

## 1) Responsibility + contract summary

C9 tests `OrderIntent`s against exchange-time truth with injected latency. For each leg, simulate an IOC limit order at the observed price, arriving at venue exchange time `t_decide_us + L_order[v]`; fill only if the venue top of book at arrival is still executable. Output is `FillFrame` plus per-trade PnL. If one leg fills and the other does not, unwind the filled leg at a later top-of-book and charge fees again. Metric: deterministic bit-identical reruns and unit-tested fill rules.

## 2) State of the art / best existing practice

- **Backtest Execution Flow · NautilusTrader · https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/execution-flow.md · claim:** the backtest loop processes exchange market data first, then strategy callbacks, then settles venues. Resting orders see incoming market data before newly submitted orders. This is the sequencing discipline C9 should emulate.
- **Backtest Execution Flow · NautilusTrader · https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/execution-flow.md · claim:** latency-delayed commands are put in an inflight queue with arrival timestamps and released only at defined settlement points. This motivates modeling order arrival before fill, not only post-hoc PnL decay.
- **Backtest Execution Flow · NautilusTrader · https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/execution-flow.md · claim:** NautilusTrader emits deterministic `TradeId`s from an FNV-1a hash of venue, raw id, and `ts_init`. Deterministic IDs/golden outputs are a useful validation target for our simulator.
- **Fill Prices and Matching · NautilusTrader · https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/fill-prices-and-matching.md · claim:** the matching engine treats recorded order-book/trade data as immutable and simulated fills do not edit history. For our replay, market truth must remain untouched; fill assumptions are explicit overlays.
- **Fill Prices and Matching · NautilusTrader · https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/fill-prices-and-matching.md · claim:** L1 books expose only best bid/ask; market-style residual fills and price protection are modeled separately. Since our data are BBO quotes, C9 must be conservative about depth and partial fills.
- **Latency Models · hftbacktest · https://github.com/nkaz001/hftbacktest/blob/v1.8.4/docs/latency_models.rst · claim:** hftbacktest models feed latency, order-entry latency, and order-response latency separately. C9 consumes C2's order-entry latency; response latency matters for knowing one leg failed before unwinding.
- **Order Fill docs snippets · hftbacktest · https://github.com/nkaz001/hftbacktest/blob/master/docs/order_fill.rst · claim:** hftbacktest has queue-model abstractions and probability queue models; exact queue formulas are **UNVERIFIED** here, but the best-practice direction is to make fill assumptions modular.

## 3) Baseline we ship now

`components/sim/fills.py` implements the MVP:

- `truth_books(q)` groups quotes by `leg` and stores sorted exchange-time arrays.
- `LegBook.at(t)` returns latest BBO at or before arrival time via `np.searchsorted`.
- `simulate(...)` fills each IOC sell/buy leg if arrival BBO is at or better than the observed limit, caps size with top-of-book displayed size and `q_max`, charges taker fees, and classifies `both`, `sell_only`, `buy_only`, or `none`.
- Mismatched inventory is unwound after learning failure using a further latency delay; assumption: inventory is pre-positioned, no transfers.

Near-term hardening: add deterministic sort keys, explicit no-data outcomes, synthetic unit tests for both-fill/one-leg/miss cases, and golden hashes for replay outputs.

## 4) Innovation candidates

| Candidate | Description | Impact | Novelty | Feasibility by Dec | Measurability | Demoability |
|---|---|---:|---:|---:|---:|---:|
| Exchange-time truth with receive-time decisions | Prove every order decision uses receive-time state but fill truth is looked up at exchange-time arrival. | 5 | 4 | 5 | 5 | 5 |
| Legging-loss model | Explicitly simulate failed second leg and unwind delay/loss; estimate `lambda` for C8 EV. | 5 | 4 | 4 | 5 | 5 |
| Modular fill assumptions | Switch among BBO-only IOC, displayed-size consumption, and conservative no-partial modes. | 4 | 3 | 4 | 5 | 4 |
| Deterministic replay artifacts | Stable IDs, sorted outputs, fixed seeds, and golden result files for demos/regression tests. | 4 | 2 | 5 | 5 | 4 |

Best near-term candidate: **receive-time decisions + exchange-time truth**, because it is the core anti-look-ahead story for judges.

## 5) Isolated scalar metric

**Determinism failure count:**

Run the same simulator command twice on the same `OrderIntent`, `QuoteFrame`, latency, and fee inputs. Sort by stable keys and hash canonical output columns. Scalar:

`determinism_failures = 1 if hash_run_1 != hash_run_2 else 0`

Target 0 for every fixture. Companion unit-test metric: number of fill-rule fixtures passing, including stale/no-book, both legs, one-leg unwind, partial size, and fee accounting.

## 6) Risks

- Arrival lookup by `ts_exch_us` can still be biased if exchange timestamps are not matching-engine timestamps; semantics are venue-specific and partly **UNVERIFIED**.
- BBO data cannot model hidden liquidity, queue priority, or deeper-book walking; label fills as conservative BBO IOC approximations.
- Unwind timing is an assumption; sweep it in C11 and estimate from paper/live when possible.
- Using future feed latency to choose order latency would leak; C9 should accept only C2 online-safe `LatencyModel` samples.
- If quote streams have gaps, `LegBook.at` may use a stale quote unless C3/C9 enforce max age.
