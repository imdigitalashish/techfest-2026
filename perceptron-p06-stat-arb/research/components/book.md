# C3 book — consolidated as-of state

## 1) Responsibility + contract summary

C3 builds the trader's believed top-of-book state at every received event, on the trader receive clock, without look-ahead. Input is multi-venue `QuoteFrame`. Output is `StateFrame`: `ts_us` plus each venue's best bid/ask prices/sizes and `age_us_v`, the time since that venue's last update was received. Venues never seen are NaN; venues older than `max_age_us` are masked. Metric targets: high events/s throughput and zero look-ahead violations.

## 2) State of the art / best existing practice

- **Cryptocurrency Exchange Feed Handler README · cryptofeed · https://github.com/bmoscon/cryptofeed/blob/master/README.md · claim:** cryptofeed includes a synthetic NBBO feed aggregating best bids and asks across user-specified feeds. This validates C3's role as a normal consolidated top-of-book layer.
- **Cryptocurrency Exchange Feed Handler README · cryptofeed · https://github.com/bmoscon/cryptofeed/blob/master/README.md · claim:** cryptofeed supports L1_BOOK, L2_BOOK, and L3_BOOK. Our MVP is intentionally L1/top-of-book, but queue/fill realism can consume deeper books later.
- **Fill Prices and Matching · NautilusTrader · https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/fill-prices-and-matching.md · claim:** NautilusTrader treats recorded order-book and trade data as immutable; simulated fills do not edit the historical book. That separation should also apply to C3: state reconstruction is market-data truth, not a mutable simulator.
- **Fill Prices and Matching · NautilusTrader · https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/fill-prices-and-matching.md · claim:** with `liquidity_consumption=True`, NautilusTrader tracks original and consumed displayed size, and a fresh book update resets displayed size. This is a C9 fill concern, but C3 should expose sizes cleanly enough for that approximation.
- **Fill Prices and Matching · NautilusTrader · https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/fill-prices-and-matching.md · claim:** consumption tracking estimates available size, not order priority; queue-position tracking or probabilistic fill approximations are separate. Therefore C3 should not pretend top-of-book size gives FIFO priority.
- **Order Fill docs snippets · hftbacktest · https://github.com/nkaz001/hftbacktest/blob/master/docs/order_fill.rst · claim:** hftbacktest documents queue-model extension points including `QueueModel`/`L3QueueModel`, plus `RiskAverseQueueModel` and probability queue-model families. Exact formulas were not opened; mark queue-model details **UNVERIFIED** until that page is fetched fully.

## 3) Baseline we ship now

There is no C3 implementation beyond `components/book/__init__.py`. Ship a Polars as-of state builder:

1. Sort quotes by `ts_recv_us`.
2. For every event timestamp, update only the emitting leg's last BBO.
3. Emit one row per event with all configured venue/instrument legs, forward-filled only from rows whose `ts_recv_us <= current ts_us`.
4. Compute `age_us_v = ts_us - last_ts_recv_us_v`; mask price/size columns when age exceeds `max_age_us`.
5. Keep `source_ts_exch_us_v` for audits but never join on future exchange time.

## 4) Innovation candidates

| Candidate | Description | Impact | Novelty | Feasibility by Dec | Measurability | Demoability |
|---|---|---:|---:|---:|---:|---:|
| Receive-clock as-of engine | Explicit invariant that every state cell is sourced from `ts_recv_us <= ts_us`, with property tests. | 5 | 2 | 5 | 5 | 5 |
| Age-aware masking | Carry quote ages into C6/C7 and mask stale venues, so stale quotes become features or exclusions instead of hidden alpha. | 5 | 3 | 5 | 5 | 5 |
| Gap-aware state timeline | Use C1 feed-health gaps to invalidate affected venues until next snapshot/fresh BBO. | 4 | 3 | 4 | 5 | 4 |
| Optional NBBO/leader board | Maintain cross-venue best bid/ask and venue leadership changes as columns for demos and C6. | 4 | 2 | 4 | 4 | 5 |

Best near-term candidate: **age-aware receive-clock as-of engine**, because quote age is both a safety guard and a powerful decay feature.

## 5) Isolated scalar metric

**Look-ahead violations:**

For each emitted state row and venue column, store the source row's `source_ts_recv_us_v`. Assert:

`max(source_ts_recv_us_v - ts_us) <= 0`

The scalar metric is `lookahead_violations = count(source_ts_recv_us_v > ts_us)`, target 0. Throughput companion metric is `events_per_second = emitted_state_rows / wall_clock_seconds` on the fixed benchmark day.

## 6) Risks

- Joining by `ts_exch_us` would leak unavailable quotes; all online state must be receive-clock as-of.
- Forward-filling through feed gaps can create false stale mispricings; integrate C1 gap masks.
- Wide `StateFrame` columns can become memory-heavy as venues/instruments grow; start with selected legs and lazy Polars scans.
- L1 size is not guaranteed executable after latency; C9 must own fill realism.
- Symbol normalization across spot/perp/USD/USDT variants can silently pair the wrong instruments; keep explicit pair config.
