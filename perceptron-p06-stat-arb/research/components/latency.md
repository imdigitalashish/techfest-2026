# C2 latency — feed and order latency model

## 1) Responsibility + contract summary

C2 estimates how stale each venue's data is when we receive it and how long an order would take to reach each venue. Input is `QuoteFrame`, a vantage label such as `tardis-collector`, `mac-india`, or `azure-<region>`, and optional measured order-latency overrides. Output is `LatencyModel`: per-venue/leg feed-latency quantiles and empirical sampler plus one-way order latency `L_order[v]`. Negative latencies are reported as clock-skew evidence, not clipped. Default assumption: one-way order latency equals median feed latency from the same vantage until measured order data exist.

## 2) State of the art / best existing practice

- **Latency Models · hftbacktest · https://github.com/nkaz001/hftbacktest/blob/v1.8.4/docs/latency_models.rst · claim:** hftbacktest separates feed latency, order entry latency, and order response latency. This is the correct taxonomy for P6; feed freshness and executable arrival are different random variables.
- **Latency Models · hftbacktest · https://github.com/nkaz001/hftbacktest/blob/v1.8.4/docs/latency_models.rst · claim:** feed latency is handled through `local_timestamp` and `exch_timestamp`, with `feed_latency = local_timestamp - exch_timestamp` in the feed-derived models. That is exactly our `ts_recv_us - ts_exch_us` baseline.
- **Latency Models · hftbacktest · https://github.com/nkaz001/hftbacktest/blob/v1.8.4/docs/latency_models.rst · claim:** hftbacktest provides `ConstantLatency`, `BackwardFeedLatency`, `ForwardFeedLatency`, `FeedLatency`, and `IntpOrderLatency`. We should ship constant/empirical baselines first and explicitly mark forward-looking models as unsuitable for online policy evaluation.
- **Latency Models · hftbacktest · https://github.com/nkaz001/hftbacktest/blob/v1.8.4/docs/latency_models.rst · claim:** `IntpOrderLatency` interpolates actual order latency data and suggests collecting it by regularly submitting unexecutable orders with local request timestamp, exchange timestamp, and local response timestamp. This is the best stretch measurement plan for paper trading.
- **Backtest Execution Flow · NautilusTrader · https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/execution-flow.md · claim:** NautilusTrader's `LatencyModel` places each command in a venue inflight queue with an arrival timestamp, then releases due commands at settlement points. This is better practice than simply shifting fills after the fact.
- **Backtest Execution Flow · NautilusTrader · https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/execution-flow.md · claim:** sandbox `StaticLatencyModel(base_latency_nanos=...)` covers inbound submit/modify/cancel legs; venue-generated accepts/fills/cancels are not delayed. This clarifies what our C9 baseline models and what it does not.
- **Historical Data Details — Overview · Tardis.dev · https://docs.tardis.dev/historical-data-details/overview · claim:** Tardis records arrival timestamps with synchronized clocks, making feed-latency estimation a first-class dataset property.
- **NTPv4 page · RFC Editor/IETF · https://www.rfc-editor.org/info/rfc5905/ · claim:** the opened RFC page only exposed metadata, not protocol accuracy details; precise NTP/PTP clock-sync performance claims remain **UNVERIFIED** here.

## 3) Baseline we ship now

`components/latency/model.py::feed_latency_table` excludes rows with imputed exchange timestamps, computes `lat_us = ts_recv_us - ts_exch_us`, groups by `venue:instrument`, and returns n, p05, p50, p95, p99, and negative-latency fraction. `pinball_loss` exists for quantile evaluation. Order latency is not directly measured; use `L_order[leg] = feed_p50_us[leg]` as a labelled symmetric-path assumption and sweep multipliers in C11.

## 4) Innovation candidates

| Candidate | Description | Impact | Novelty | Feasibility by Dec | Measurability | Demoability |
|---|---|---:|---:|---:|---:|---:|
| Empirical conditional sampler | Sample feed latency by venue, hour, burstiness, and recent latency decile instead of constant p50. | 5 | 3 | 4 | 5 | 4 |
| Clock-skew estimator | Track negative-latency tail and live `sntp` offsets to separate network latency from local clock error. | 4 | 3 | 4 | 4 | 4 |
| Unexecutable-order probe plan | In paper mode, optionally submit/post-only far-away orders on sandbox/testnet or small venues to measure request/exchange/response triplets. | 4 | 4 | 2 | 5 | 4 |
| Actuation-latency stress grid | Treat `L_order = a + b*feed_latency_quantile` and evaluate EV sensitivity over `a,b` rather than claiming one true latency. | 5 | 3 | 5 | 5 | 5 |

Best near-term candidate: **actuation-latency stress grid**; it is honest under missing order-latency data and maps directly to the judging criterion.

## 5) Isolated scalar metric

**Quantile pinball loss on a held-out hour:** for each leg and quantile `tau`, predict `q_tau` from the training window, then score held-out feed latencies `y` as:

`mean(max(tau*(y-q_tau), (tau-1)*(y-q_tau)))`

Average over `tau in {0.05,0.50,0.95,0.99}` and venue legs, weighted by held-out row count. Also report negative-latency fraction separately because low pinball loss can hide clock skew.

## 6) Risks

- `ts_exch_us` may be exchange gateway time, matching-engine time, or message-generation time depending on venue; exact per-venue semantics are **UNVERIFIED**.
- Feed latency is not order latency; assuming symmetry can overstate achievable PnL.
- Forward-looking feed-latency models are useful diagnostic bounds but invalid for online decisions.
- Clock sync on a Mac in India is weaker than colocated capture; label all live-vantage results accordingly.
- Heavy-tailed latency bursts make mean latency misleading; use quantiles and stress grids.
