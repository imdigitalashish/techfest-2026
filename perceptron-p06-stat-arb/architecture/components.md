# Components and contracts — P6 cross-asset stat arb with latency budgets

Owner: project lead. Typed contracts: [`contracts/models.py`](contracts/models.py) (pydantic v2, row level) and [`contracts/frames.py`](contracts/frames.py) (columnar polars schemas used on the batch path). JSON Schemas are exported to `contracts/*.schema.json` by `python -m architecture.contracts.export`.
All SLOs below are **design targets**, not measurements, unless a results file is linked.

## Key idea in one line
An opportunity's value is `EV = S(L | x) · (edge − cost) − (1 − S(L | x)) · λ`. Here `S(L | x)` is the survival probability that the mispricing is still executable when our order lands L µs later, and `λ` is the expected loss of a failed (legged) attempt. Confidence and latency are traded inside a single quantity. Waiting Δ for confirmation changes the terms to `S(Δ+L)` and `(S(Δ) − S(Δ+L))·λ`, which gives an explicit act-now-vs-wait rule ([ADR 001](adr/001-spike.md)).

## Dependency graph
```mermaid
flowchart LR
  subgraph Data
    F[C1 feed<br/>adapters] --> B[C3 book<br/>consolidated as-of state]
    F --> LAT[C2 latency<br/>feed/order latency model]
  end
  B --> FV[C4 fair_value<br/>basis + lead–lag]
  B --> D[C6 detector<br/>executable edges]
  FV --> D
  CO[C5 costs<br/>fees, spread, size] --> D
  D --> DEC[C7 decay<br/>survival S(L|x)]
  LAT --> DEC
  D --> POL[C8 decision<br/>EV rank, act/wait]
  DEC --> POL
  CO --> POL
  LAT --> POL
  POL --> SIM[C9 sim<br/>latency-injected fills]
  B --> SIM
  LAT --> SIM
  SIM --> EV[C11 eval<br/>frontier + metrics]
  POL --> PT[C10 paper<br/>live paper trading]
  F --> PT
```

## Component table
| # | Component | Input → Output | Baseline (existing practice) | Spike? | Isolated scalar metric |
|---|---|---|---|---|---|
| C1 | `feed` | Tardis CSV / raw websocket frames → `QuoteFrame` | Tardis normalised `quotes`; cryptofeed-style adapters | no | parse coverage (% frames → valid quotes), monotonicity violations per 1M rows |
| C2 | `latency` | `QuoteFrame` (exch vs recv ts) + config → `LatencyModel` (per-venue quantiles, sampler) | constant latency | no | pinball loss of predicted latency quantiles on held-out hour |
| C3 | `book` | `QuoteFrame` (all venues) → `StateFrame` (as-of best bid/ask per venue on one clock, with quote ages) | as-of join | no | throughput (events/s); 0 look-ahead violations |
| C4 | `fair_value` | `StateFrame` → `BasisFrame` (rolling fair basis per pair) + `LeadLag` | rolling median basis | candidate | OOS RMSE (bps) of next-100 ms mid-difference forecast |
| C5 | `costs` | venue, product, tier, side, size → cost (bps) | official fee schedules, VIP0 | no | exact match to fee tables (unit tests) |
| C6 | `detector` | `StateFrame` + `BasisFrame` + costs → `OpportunityFrame` (episodes with edge, size, features) | naive cross `bid_A − ask_B > fees` | no | AUC-PR of "profitable at latency L" labels |
| C7 | `decay` | `OpportunityFrame` (durations, censoring, features) → `DecayModel` (S(t\|x), half-life) | Kaplan–Meier | **yes** | integrated Brier score / C-index on held-out day; calibration error of S(L) |
| C8 | `decision` | `Opportunity` + `DecayModel` + `LatencyModel` + costs → `OrderIntent` (or skip/wait) | trade every cross above fees | **yes** | net PnL per day at latency L and fee tier (simulated), capture ratio vs oracle |
| C9 | `sim` | `OrderIntent` stream + `QuoteFrame` (exchange-time truth) + `LatencyModel` → `FillFrame`, PnL | zero-latency backtest | no | determinism + fill-rule unit tests |
| C10 | `paper` | live frames → same C3–C8 path → simulated fills + dashboard | none | stretch | live-vs-sim slippage divergence (bps) |
| C11 | `eval` | everything → `results/*.json`, frontier plots, report | — | — | end-to-end: net PnL vs latency (frontier), capture ratio |

## Per-component contracts

### C1 `feed` — market-data adapters
- **Responsibility:** turn any source into one normalised top-of-book stream with two clocks.
- **Input:** Tardis `quotes` CSV (`exchange,symbol,timestamp,local_timestamp,ask_amount,ask_price,bid_price,bid_amount`, µs) or raw live frames (`recv_ns\tjson`).
- **Output:** `QuoteFrame`: `ts_exch_us:i64` (venue's own timestamp, imputed if absent; `exch_ts_imputed:bool`), `ts_recv_us:i64` (collector receive time), `venue:str`, `instrument:str`, `bid_px, bid_sz, ask_px, ask_sz: f64`. Sorted by `ts_recv_us`.
- **Errors:** crossed/locked own book (`bid ≥ ask`) dropped and counted; zero/NaN prices dropped; out-of-order exchange timestamps kept but counted.
- **SLO:** ≥ 2M rows/s parse on the M5 (polars); live adapter < 50 µs per frame.
- **Calls:** nothing. **Called by:** C2, C3, C10.

### C2 `latency` — latency model
- **Responsibility:** know how stale each venue's data is when it reaches us, and how long an order takes to reach the venue.
- **Input:** `QuoteFrame`; a vantage config (`tardis-collector`, `mac-india`, `azure-<region>`); optional order-latency overrides.
- **Output:** `LatencyModel`: per venue, feed-latency quantiles (p5…p99) and an empirical sampler; order latency `L_order[v]` (one-way). By default, order latency is assumed equal to the median feed latency; this is labelled as an assumption until we measure it.
- **Errors:** negative latencies (clock skew) are reported, not clipped silently; the clock offset is logged.
- **Metric:** pinball loss of the quantiles on a held-out hour.

### C3 `book` — consolidated as-of state
- **Responsibility:** what the trader *believes* each venue's top of book is, at every event, on the trader's receive clock — never using information not yet received.
- **Input:** `QuoteFrame` for N venues.
- **Output:** `StateFrame`: `ts_us` + for each venue `bid_px_v, ask_px_v, bid_sz_v, ask_sz_v, age_us_v` (time since that venue's last update was received).
- **Errors:** venue never seen → NaN; stale beyond `max_age_us` → masked.
- **Metric:** events/s; a look-ahead test (no value used before its `ts_recv_us`).

### C4 `fair_value` — fair basis and lead–lag
- **Responsibility:** for each pair (A, B), estimate the fair price difference (USD vs USDT, spot vs perp basis) and which venue leads.
- **Input:** `StateFrame`.
- **Output:** `BasisFrame` (`ts_us, pair, basis_bps, basis_sd_bps`); `LeadLag(pair, lag_us, xcorr)`.
- **Baseline:** rolling median of `(mid_A − mid_B)/mid` over 60 s. **Candidates:** Kalman/local-level basis; Hayashi–Yoshida lead–lag; micro-price fair value.
- **Metric:** OOS RMSE (bps) of the next-100 ms mid difference.

### C5 `costs` — fees and execution costs
- **Responsibility:** cost in bps to cross the spread on each leg, by venue, product and fee tier.
- **Input:** `(venue, product, tier, side, liquidity='taker')`.
- **Output:** `fee_bps: float`. Size limits come from the quote sizes.
- **Baseline:** official fee schedules (sources in `research/notes/fees.md` once verified). Tiers: `retail` (base tier), `vip` (top published tier), `mm` (0 bps — the zero-fee frontier as an upper bound). Until verified, all fee numbers are **labelled assumptions** and swept.
- **Metric:** unit tests against the cited fee tables.

### C6 `detector` — executable mispricings
- **Responsibility:** emit every episode in which selling at venue A's bid and buying at venue B's ask beats the fair basis plus a threshold.
- **Input:** `StateFrame`, `BasisFrame`, threshold θ (bps), fee tier.
- **Output:** `OpportunityFrame`: `opp_id, t_start_us, t_end_us, duration_us, censored:bool, sell_venue, buy_venue, edge0_bps` (at detection, net of basis), `net0_bps` (minus fees), `size` (min of the two top-of-book sizes), and features `age_sell_us, age_buy_us, spread_sell_bps, spread_buy_bps, vol_1s_bps, edge_max_bps`.
- **Baselines:** naive (θ = fees) and z-score (θ = k·σ_basis).
- **Metric:** AUC-PR for the label "still profitable after fees when the order arrives at latency L" (label computed by C9 against exchange-time truth).

### C7 `decay` — opportunity survival model (SPIKE)
- **Responsibility:** `S(t | x)`, the probability that the opportunity is still executable t µs after detection, from censored durations; plus half-life summaries for the MVP decay report.
- **Input:** `OpportunityFrame` (durations, censoring flags, features).
- **Output:** `DecayModel` with `survival(t_grid, X) → [n, len(t_grid)]`, `half_life_us(X)`, and a report: Kaplan–Meier curves by pair and edge bucket, median and p90 lifetimes, and an edge-magnitude decay curve E[edge(t)]/edge(0).
- **Baseline:** Kaplan–Meier per pair (no covariates). **Spike:** covariate-conditioned survival (Weibull/log-normal AFT → discrete-time hazard GBM), with quote ages and edge size as the key covariates.
- **Metric:** integrated Brier score on the held-out day (lower is better); C-index; calibration of S(L) at the operating latency.

### C8 `decision` — latency-aware ranking and act/wait (SPIKE)
- **Responsibility:** for each live opportunity, compute EV under our latency and either send both legs now, wait Δ, or skip; rank simultaneous opportunities by EV under inventory caps.
- **Input:** `Opportunity` features, `DecayModel`, `LatencyModel`, `costs`, the expected failed-attempt loss λ (estimated from the simulator).
- **Output:** `OrderIntent(t_decide_us, opp_id, sell_venue, buy_venue, size, limit_sell_px, limit_buy_px, ev_bps)`.
- **Baselines:** (a) naive — act on every cross above fees; (b) z-score — act when the deviation exceeds k·σ. **Spike:** EV rule with an optimal confirmation delay Δ*.
- **Metric:** simulated net PnL/day at (latency L, fee tier), and capture ratio = PnL / oracle PnL.

### C9 `sim` — latency-injected event-driven simulator
- **Responsibility:** fill each leg against the venue's book **at the exchange time our order arrives** (`t_decide + L_order[v]`), not at the time we saw it.
- **Input:** `OrderIntent`s, per-venue `QuoteFrame` indexed by `ts_exch_us`, `LatencyModel`, fee tier.
- **Output:** `FillFrame` (`opp_id, leg, venue, filled:bool, px, size, fee_bps`) and per-trade PnL (bps, USD). IOC limit legs; an unfilled leg is unwound at the venue's top of book at arrival plus one order latency (the legging loss).
- **Metric:** deterministic, bit-identical reruns; unit tests for fill rules.

### C10 `paper` — live paper trading (stretch)
- Same C3–C8 code path on the live recorder stream; fills by C9's rules with the measured live latency; terminal dashboard. Metric: divergence between live paper fills and replayed simulation of the same period (bps).

### C11 `eval` — harness
- Train on 2026-09-01, test on 2026-10-01 (held-out), plus the live recording. Outputs `eval/results/*.json` and `*.md`: decay report, policy table across a latency grid × fee tiers, latency–PnL frontier. Every number in a deliverable must come from a file here, with the command that reproduces it.
