# Round-1 abstract (draft v1, 2026-10-04) — Perceptron 2026 · Problem 6

**Arriving on time: latency-aware ranking of cross-venue crypto mispricings**

*Status: draft for the 31 Oct submission. Every number below comes from committed runs in `perceptron-p06-stat-arb/eval/results/` on public Tardis.dev tick data (train 1 Sep 2026, held-out 1 Oct 2026); P&L figures are simulated. Team lines marked [TEAM] await the user.*

**Problem and theme.** Theme 3 (Markets & Trading Intelligence), Problem 6: cross-asset statistical arbitrage with latency budgets. It is a clean test of a question every trading system faces: is a signal still worth anything by the time we can act on it? [TEAM: why it matters to us.]

**Understanding of the challenge.** Spotting a price gap is easy. Our detector finds 345,890 gaps of ≥1 bp (beyond each pair's fair basis) in one day across nine BTC markets. The hard part is what a gap is worth *when our order lands*. The gap may not be real (asynchronous or stale quotes, different clocks, USD-vs-USDT or spot-vs-perpetual basis). It may close before we arrive. Fees and displayed size may consume it. Waiting for confirmation raises confidence but spends the lifetime. On the held-out day the median gap lasted 90 ms, and 10% were gone within 3.9 ms. The hazard decreases with age (Weibull shape 0.43). Raw gap size ranks opportunities well at 0.5 ms (Spearman 0.83 with realised P&L), but at 50 ms it is uninformative (0.05).

**Proposed approach.** An event-driven pipeline of typed components, each with its own metric:
1. Ingestion of Tardis.dev quotes (exchange and collector timestamps) for Binance, Coinbase, OKX, Bybit, Kraken, Bitstamp and Deribit, plus our own 12-venue websocket recorder.
2. A consolidated as-of book on the receive clock.
3. A fair-basis and lead–lag estimator: EWMA, then Kalman, then Hayashi–Yoshida.
4. A detector of executable crosses, bid_A − ask_B, net of basis and fees and capped at top-of-book size.
5. A decay model: Kaplan–Meier by venue pair, extended to residual survival.
6. The decision layer, our spike, which ranks by *latency-conditioned executable value*: LEV(x, L) = E[P&L | features, end-to-end latency L]. It is learned with gradient boosting from simulator labels and decides act-now, wait or skip. Its interpretable counterpart is EV = S(L|x)·net − (1−S(L|x))·λ, where S is survival and λ the expected loss of a legged attempt.
7. A simulator that decides on receive-time state but fills both IOC legs against each venue's book at its own arrival time, including partial fills, fees and unwind loss.
8. A paper trader that runs the same code path on live feeds.

Tools: Python, polars, numba, lifelines, scikit-learn.

**Minimum Viable mapping.** *Detect mispricings with a threshold or statistical model:* threshold and basis-adjusted detector, already running on real ticks (a 9-venue day in ~5 minutes on a laptop). *Report how fast opportunities decay:* survival curves by venue pair and gap size. Median lifetime is 46 ms for perpetual–perpetual pairs, 95–105 ms for pairs involving spot, and 200–257 ms for Deribit pairs. The average gap keeps 74% of its size after 100 ms and 48% after 500 ms. Both come from one command and run live at the demo.

**Stretch goals.** *Simulated end-to-end latency budget:* L = feed + compute + order latency, swept to give a latency–P&L frontier per policy and fee level. Tardis collectors see Binance perpetual quotes 1.8 ms after the exchange stamp (median). Our laptop in India sees the fastest 5% of Binance-perpetual, Coinbase, Kraken and Deribit messages 75–110 ms late (medians: seconds, on a congested link). We will measure from cloud regions to choose a vantage point. *Paper trading:* live recorder → same pipeline → simulated fills with measured latency.

**Novelty.** (1) We rank by value at arrival, not by visible gap. At 50 ms with 1 bp per-leg fees, the top decile by LEV earned +0.89 bp per trade against +0.04 bp for the top decile by gap size. (2) Decay is treated as censored survival, with an explicit act-or-wait rule derived from the hazard shape. (3) Evaluation uses a latency–P&L frontier with exchange-time fills rather than a zero-latency backtest. (4) An auto-research ratchet keeps changes only beyond bootstrap noise; its first loop has *not* yet beaten a tuned per-pair threshold significantly (+14%, within one standard error).

**Evaluation plan.**
- *Data:* Tardis first-of-month days for walk-forward (≥12 days), plus our live recordings.
- *Baselines:* naive (trade every gap above fees), a tuned per-pair×latency threshold (the bar to beat) and EV with Kaplan–Meier.
- *Metrics:* simulated P&L and capture ratio per latency and fee level; ranking quality; integrated Brier score and C-index for decay; drawdown and tail loss.
- *Rigor:* paired block bootstrap across days, receive-time replay with ±5 ms clock-offset perturbation, and ablations.
- *Held-out numbers today (1 bp/leg; latencies are one-way, applied to feed and orders):*

| One-way latency | Naive | Tuned threshold | LEV |
|---|---|---|---|
| 1 ms | +$1,490 | +$1,977 | +$1,926 |
| 10 ms | −$1,570 | +$768 | +$802 |
| 100 ms | −$4,433 | +$30 | −$33 |

**Feasibility and risks.** [TEAM: skills — systems/latency, ML, quant.] The MVP already runs end to end; the remaining work is rigor and engineering.

*Milestones:* abstract and multi-day dataset by 31 Oct; walk-forward, residual survival and compiled LEV 1–17 Nov; exams 19–25 Nov (no planned work); midway report by 1 Dec; paper trading, cloud vantage and demo 1–14 Dec.

*Risks and mitigations:*
- Cross-venue clocks are not common: receive-time replay and offset perturbation.
- Some venues publish ~100 ms snapshots: interval censoring, excluded from millisecond claims.
- Fees can erase every edge (Coinbase Exchange's lowest-volume taker fee is 60 bps): we report fee-level frontiers, not one profit number.
- Our spike may not beat a well-tuned threshold: the frozen evaluator will tell us, and we will say so.
