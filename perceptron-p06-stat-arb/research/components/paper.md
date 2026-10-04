# C10 paper — live paper trading

## 1) Responsibility + contract summary

C10 runs the same C3-C8 path on the live recorder stream and applies C9 fill rules with measured live latency. It is a stretch component: no real orders required for MVP. Output is a paper-trading log/dashboard containing live quotes, detected opportunities, decisions, simulated fills, PnL, latency, and divergence from replay. Metric: live-vs-replayed simulation slippage divergence in bps.

## 2) State of the art / best existing practice

- **Backtest Execution Flow · NautilusTrader · https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/execution-flow.md · claim:** NautilusTrader uses a common event-driven execution flow where strategy callbacks submit commands and venues settle them with latency semantics. C10 should maximize live/backtest code-path parity rather than writing a separate demo loop.
- **Backtest Execution Flow · NautilusTrader · https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/execution-flow.md · claim:** deterministic trade IDs make replayed data produce the same fill identifiers every time. Our paper logs should include deterministic IDs/config hashes so live periods can be replayed exactly.
- **Fill Prices and Matching · NautilusTrader · https://github.com/nautechsystems/nautilus_trader/blob/develop/docs/concepts/backtesting/fill-prices-and-matching.md · claim:** fixed fill-model seeds make probabilistic fill decisions repeatable, while recorded books remain immutable. If C10 adds stochastic slippage, it must record seeds.
- **Cryptocurrency Exchange Feed Handler README · cryptofeed · https://github.com/bmoscon/cryptofeed/blob/master/README.md · claim:** cryptofeed records data to pcap and supports replay. Best practice is to make every live demo produce replayable raw input, not just screenshots.
- **Latency Models · hftbacktest · https://github.com/nkaz001/hftbacktest/blob/v1.8.4/docs/latency_models.rst · claim:** actual order-latency interpolation is most accurate when measured triplets are available and can be collected by submitting unexecutable orders regularly. For our non-trading paper demo, this becomes an optional stretch/testnet measurement, not a default.
- **DBN README · Databento · https://github.com/databento/dbn · claim:** Databento Binary Encoding is the default encoding for Databento APIs and enforces standardized normalized market-data structs. This is a reference for durable paper-trading logs: use explicit schema/version metadata.
- **record/methods.rs search result · Databento · https://github.com/databento/dbn/blob/master/rust/dbn/src/record/methods.rs · claim:** the opened GitHub search fragment says `ts_recv` parses a capture-server-received timestamp and timestamp fields include `ts_event`/`ts_recv` for several record types. Full Databento docs pages were JS-only through `web_fetch`, so exact Databento timestamp semantics remain **UNVERIFIED** beyond these source-code comments/fragments.

## 3) Baseline we ship now

No C10 implementation exists beyond `components/paper/__init__.py`. The usable baseline is the existing live recorder plus offline replay:

1. Run `components/feed/live_recorder.py` to persist raw websocket frames with local `recv_ns` and periodic `sntp` offset logs.
2. Normalize raw frames through C1 `load_live`.
3. Build C3 state, C6 opportunities, C7 survival, C8 decisions, and C9 paper fills offline over the recorded period.
4. Present terminal tables: current best cross, feed-latency quantiles, opportunity half-life, decisions, fill outcome, cumulative PnL, and live-vs-replay divergence.

This satisfies a safe paper demo without real exchange credentials or order placement.

## 4) Innovation candidates

| Candidate | Description | Impact | Novelty | Feasibility by Dec | Measurability | Demoability |
|---|---|---:|---:|---:|---:|---:|
| Same-code-path live/replay | Run live frames through exactly the same C3-C9 functions and persist raw inputs/config hashes for replay. | 5 | 3 | 4 | 5 | 5 |
| Terminal latency budget tape | Live dashboard showing feed p50/p95, chosen `L_order`, `S(L)`, EV, act/skip/wait, and decay half-life. | 5 | 3 | 4 | 5 | 5 |
| Paper-vs-replay divergence | Replay the just-recorded session and compare fills/PnL to online paper decisions. | 4 | 4 | 4 | 5 | 5 |
| Optional measured order probes | Testnet or far-away unexecutable order pings to estimate request/exchange/response triplets. | 4 | 4 | 2 | 5 | 4 |

Best near-term candidate: **terminal latency budget tape**, because finals judges can see confidence-vs-latency decisions in real time.

## 5) Isolated scalar metric

**Live-vs-replay slippage divergence (bps):**

For every paper decision made online, replay the same raw frames offline with the saved config and compute the C9 fill PnL. Then:

`divergence_bps = mean(abs(pnl_bps_live_paper - pnl_bps_replay))`

If the online and replay paths are identical and deterministic, target near 0. Nonzero divergence indicates nondeterministic ordering, clock/config drift, dropped frames, or a live-only code path.

## 6) Risks

- Paper fills are not real fills; avoid language implying executable production PnL.
- Local Mac/India clock and network path differ materially from exchange colocated paths; use vantage labels everywhere.
- Live websocket outages can create demo artifacts; dashboard must display feed-health and stale masks.
- Any real-order probe requires credentials, testnet/sandbox or tiny risk controls, and explicit human approval; keep it optional.
- Databento timestamp semantics requested by the brief could not be fully verified from JS-rendered docs in this session; keep Databento claims limited to opened GitHub source facts.
