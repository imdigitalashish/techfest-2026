# Round-1 abstract — Perceptron 2026 · Problem 6

**Arriving on time: ranking cross-venue crypto mispricings by their value when the order lands**

*Rendered from committed results in `perceptron-p06-stat-arb/eval/results/` by `deliverables/render.py`; `eval/check_docs.py` checks every number. Data: public Tardis.dev tick quotes. All P&L is simulated. [TEAM] lines await the team.*

**Problem and theme.** Theme 3 (Markets & Trading Intelligence), Problem 6: cross-asset statistical arbitrage with latency budgets. It isolates a question every trading system faces: is a signal still worth anything by the time we can act on it? [TEAM: why it matters to us.]

**Understanding of the challenge.** Detection is easy: on one held-out day our detector finds {{n_episodes}} gaps of at least 1 bp beyond each venue pair's fair basis, across nine BTC markets (Binance spot and perpetual, Coinbase, OKX spot and swap, Bybit, Kraken, Bitstamp, Deribit). What matters is a gap's value when our order arrives:
- it may be an artefact: a stale or asynchronous quote, USD vs USDT, or spot–perpetual basis;
- it may close first;
- fees and displayed size may consume it;
- waiting for confirmation spends lifetime.

Half of all gaps close within {{median_life_ms}} ms (95% CI {{median_ci_lo}}–{{median_ci_hi}}). Gap size ranks opportunities well at 0.5 ms (Spearman {{rho_edge_fast}} with realised P&L) but not at 50 ms ({{rho_edge_slow}}).

Public data limits what can be measured. In these samples, Binance and OKX publish quotes on a {{cad_bnf_ms}}–{{cad_grid_ms}} ms grid, while Coinbase updates every {{cad_cb_ms}} ms at the median. Lifetimes shorter than a venue's cadence cannot be resolved, and absolute P&L at the shortest latencies is optimistic. Comparisons between policies run on identical data.

**Proposed approach.** Separately tested components, each with its own metric:
1. Ingest Tardis.dev quotes (exchange and collector timestamps) and our 12-venue websocket recorder.
2. Keep an as-of book per venue and a 60 s EWMA fair basis per pair; Kalman and Hayashi–Yoshida lead–lag come next.
3. Detect executable crosses, bid_A − ask_B net of basis and fees, capped at top-of-book size.
4. Measure decay: Kaplan–Meier survival per venue pair.
5. **Decide (our spike):** rank by *latency-conditioned executable value*, LEV(x, L) = E[P&L | features, end-to-end latency L]. A gradient-boosted model learns it from simulator labels, and we act if LEV > 0. A survival-based expected value is kept as the interpretable baseline.
6. Simulate: decide on received state; fill both IOC legs against each venue's book at the moment each order arrives; unwind failed legs; charge fees.
7. Paper-trade the same code path on live feeds.

The decision step is compiled with Numba and matches scikit-learn exactly. It takes {{dec_p50_us}} µs at p50 and {{dec_p99_us}} µs at p99 per opportunity on a shared M5 laptop.

**Minimum Viable mapping.**
- *Detect mispricings with a threshold or statistical model:* running on real ticks.
- *Report how fast the opportunity typically decays:* a one-command survival report with confidence intervals. Median lifetimes are {{median_perp_perp}} ms for perpetual–perpetual pairs, {{median_spot_perp}} ms for spot–perpetual and {{median_spot_spot}} ms for spot–spot. Across {{n_pairs}} venue pairs they range from {{pair_median_min}} to {{pair_median_max}} ms; across {{n_months}} monthly samples, from {{month_median_min}} to {{month_median_max}} ms.

Both run live at the demo.

**Stretch goals.**
- *Simulated end-to-end latency budget:* L = feed + compute + order. Compute costs microseconds; distance costs milliseconds. Tardis collectors receive Binance perpetual quotes {{feed_fast_ms}} ms after the exchange timestamp at the median, and the slowest venue {{feed_slow_ms}} ms after. From our laptop in India, the fastest 5% of messages arrive {{mac_p05_min}}–{{mac_p05_max}} ms late. With 1 bp per-leg fees, the break-even one-way latency is {{be_naive}} ms for naive trading, {{be_thr}} ms for the tuned threshold and {{be_lev}} ms for LEV.
- *Paper trading:* the live recorder feeds the same pipeline with measured latency.

**Novelty.**
1. We rank by value at arrival, not by visible gap: at 50 ms the top decile by LEV earned {{top_decile_lev_slow}} bp per trade versus {{top_decile_edge_slow}} bp by gap size.
2. Decay is censored survival with hour-block bootstrap intervals, not a single half-life.
3. The evaluation is falsification-first: a pre-registered walk-forward, clock-skew and receive-time replays, and ablations, all published whatever the outcome.

**Evaluation plan.** We walk forward over Tardis first-of-month samples, fitting on one month's day and testing on the next. Baselines are naive trading, a tuned per-pair×latency threshold (the bar to beat) and survival EV. Metrics are simulated P&L by fee and latency, ranking quality, and decay calibration.

Results so far:
- *Pre-registered test over {{wf_n}} held-out months:* LEV beat the threshold in {{wf_pos}}/{{wf_n}}, by a mean of {{wf_mean}}/day ({{wf_rel}}); the 95% t-interval is {{wf_tci}}. Verdict: {{wf_verdict}}.
- *The {{unseen_n}} months never examined before registration:* {{unseen_pos}}/{{unseen_n}} positive, {{unseen_mean}}/day.
- *Baselines:* the threshold beats naive by {{thr_vs_naive}}/day; survival EV does not beat the threshold ({{ev_vs_thr}}/day).
- *Robustness:* under ±5 ms clock offsets and receive-time replay, the pair ranking holds (Spearman ≥ {{skew_rho_min}}) and LEV's uplift stays between {{skew_uplift_min}} and {{skew_uplift_max}}.

Next: more days, fills beyond top of book, and live paper trading.

**Feasibility and risks.** [TEAM: skills — systems/latency, ML, quant.] The MVP and both stretch simulators already run, so what remains is rigour and the demo.

*Milestones:* abstract by 31 Oct; Kalman basis and lead–lag 1–17 Nov; exams 19–25 Nov; midway report by 1 Dec; paper trading and demo 1–14 Dec.

*Risks:*
- Venue clocks differ; receive-time replay controls for this.
- Fees can erase every edge (Coinbase Exchange's lowest-volume taker fee is 60 bps), so we report fee-level frontiers.
- LEV may never beat a tuned threshold beyond noise; the pre-registered test decides, and we report it.
