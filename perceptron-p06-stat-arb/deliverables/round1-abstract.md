# Round-1 abstract — Perceptron 2026 · Problem 6

**Arriving on time: ranking cross-venue crypto mispricings by their value when the order lands**

*Rendered from committed results in `perceptron-p06-stat-arb/eval/results/` by `deliverables/render.py`; `eval/check_docs.py` checks every number. Data: public Tardis.dev tick quotes. All results are simulated. [TEAM] lines await the team.*

**Problem and theme.** Theme 3 (Markets & Trading Intelligence), Problem 6. It isolates a question every trading system faces: is a signal still worth anything by the time we can act on it? [TEAM: why it matters to us.]

**Understanding of the challenge.** Detection is easy: on one held-out day our detector finds 345,890 gaps of at least 1 bp beyond each pair's fair basis, across nine BTC markets. The hard part is a gap's value when our order arrives:
- the gap may be a stale quote or a structural basis (USD vs USDT, spot vs perpetual);
- it may close first;
- fees and displayed size may consume it;
- waiting for confirmation spends its lifetime.

Gap size predicts outcomes well at 0.5 ms (Spearman 0.83) but not at 50 ms (0.05). Public data also limits what is measurable. In these samples Binance and OKX publish quotes on 26–100 ms grids, against 3.3 ms for Coinbase, so a lifetime is known only to within its venues' publication intervals.

**Proposed approach.** Separately tested components:
1. Ingest Tardis.dev quotes and our 12-venue websocket recorder.
2. Maintain an as-of book per venue and a 60 s EWMA fair basis per pair; Kalman and Hayashi–Yoshida lead–lag come next.
3. Detect executable crosses net of basis and fees, capped at top-of-book size.
4. Measure decay with survival analysis per venue pair.
5. **Decide (spike):** rank by *latency-conditioned executable value*, LEV(x, L): a gradient-boosted estimate of expected execution surplus, clipped at ±30 bp, given market-state features and end-to-end latency L. It is learned from simulator labels, and we act if LEV > 0.
6. Simulate: decide on received state; fill both IOC legs at each venue's book when each order arrives; unwind failed legs.
7. Paper-trade the same path live.

The compiled decision step (Numba, matching scikit-learn's predictions) takes 6.1 µs at p50 and 41.5 µs at p99 on a shared laptop.

**Minimum Viable mapping.**
- *Detect mispricings with a threshold or statistical model:* running on real ticks.
- *Report how fast the opportunity typically decays:* survival curves with confidence intervals. The median lifetime is 90.5 ms (95% CI 84.0–100.0); publication times bound it to 11.3–147.1 ms. By pair type it is 46 ms (perpetual–perpetual), 105 ms (spot–perpetual) and 95 ms (spot–spot). Across 13 monthly samples of five markets it ranges from 26 to 68 ms.

**Stretch goals.**
- *Latency budget:* L = feed + compute + order. Compute takes microseconds; distance takes milliseconds. Tardis collectors see Binance perpetual quotes 1.8 ms after the exchange timestamp (median), and the slowest venue 40 ms after. From our laptop in India, the fastest 5% of messages arrive 69–107 ms late. At 1 bp per-leg fees, naive trading stops paying at 4.6 ms one-way.
- *Paper trading:* the live recorder feeds the same pipeline.

**Novelty.** Our contribution is a falsification-first decision benchmark on public data, not a new learner:
1. We rank by value at arrival. At 50 ms, with the frozen simulator, the top decile by LEV earned +0.89 bp per trade, against +0.04 bp ranked by gap size.
2. Decay is reported together with its observability limits.
3. The walk-forward is pre-registered, the stricter simulators are registered amendments, and the ablations are published whatever they show.

**Evaluation plan.** We fit on one month's first day and test on the next. Baselines are naive trading, a tuned per-pair × fee × latency threshold (the bar to beat) and survival EV. The metric is simulated execution surplus (fills after fees, marked against the fair basis), summed over six fee/latency scenarios.
- *Pre-registered: 12 sampled months, 5 of them previously inspected.* LEV beat the threshold in 12/12 months, by a mean of +$299/day (+23%); 95% t-interval [+$130, +$468]. Verdict: supported (both 95% lower bounds are above zero). On the 7 months never inspected: 7/7, +$343/day ([+$70, +$616]).
- *Stricter simulators (registered amendment):* filling at the next published quote gives +$73/day ([+$10, +$135]); adding a mark-to-mid 1 s later gives +$70/day ([+$0.2, +$140]). Verdict: the registered rule passes, but the gain shrinks to 24% of its frozen-simulator value.
- *Fragility:* dropping intents that reuse a quote already hit (18% of LEV's trades) leaves +$40/day ([−$12, +$92]). A LEV trained on optimistic fills has no established advantage over the threshold under strict fills (−$7.8/day, [−$148, +$132]).
- *Attribution (exploratory):* with the frozen simulator, LEV beats a GBM classifier by +$98/day ([+$48, +$148]) and the same model without the latency input by +$477/day ([+$247, +$708]). With strict fills and markouts, these become −$0.3 and +$40/day (neither significant). Survival EV trails the threshold (−$77/day).

**Feasibility and risks.** [TEAM: skills — systems/latency, ML, quant.] The MVP and both stretch simulators run.

*Milestones:* abstract by 31 Oct; lead–lag and deeper-book fills 1–17 Nov; exams 19–25 Nov; midway report by 1 Dec; paper trading and demo 1–14 Dec.

*Risks:*
- Venue clocks differ; we re-test conclusions under receive-time replay.
- Publication grids hide sub-cadence dynamics; for the finals we will capture tick-by-tick feeds near the exchanges.
- Fees can erase every edge (Coinbase Exchange's lowest-volume taker fee is 60 bps).
- Public replay cannot pin down LEV's value; its gain ranges from within noise to +$299/day depending on execution assumptions. We will measure it with live paper fills.
