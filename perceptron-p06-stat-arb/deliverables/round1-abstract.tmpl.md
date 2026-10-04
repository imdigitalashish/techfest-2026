# Round-1 abstract — Perceptron 2026 · Problem 6

**Arriving on time: ranking cross-venue crypto mispricings by their value when the order lands**

*Rendered from committed results in `perceptron-p06-stat-arb/eval/results/` by `deliverables/render.py`; `eval/check_docs.py` checks every number. Data: public Tardis.dev tick quotes. All results are simulated. [TEAM] lines await the team.*

**Problem and theme.** Theme 3 (Markets & Trading Intelligence), Problem 6. It isolates a question every trading system faces: is a signal still worth anything by the time we can act on it? [TEAM: why it matters to us.]

**Understanding of the challenge.** Detection is easy: on one held-out day our detector finds {{n_episodes}} gaps of at least 1 bp beyond each pair's fair basis, across nine BTC markets. The hard part is a gap's value when our order arrives:
- the gap may be a stale quote or a structural basis (USD vs USDT, spot vs perpetual);
- it may close first;
- fees and displayed size may consume it;
- waiting for confirmation spends its lifetime.

On one test day (nine markets, 1 bp fees), gap size predicts realised surplus at 0.5 ms one-way latency (Spearman {{rho_edge_fast}}) but not at 50 ms ({{rho_edge_slow}}). In these samples Binance and OKX publish quotes on {{cad_bnf_ms}}–{{cad_grid_ms}} ms grids, against {{cad_cb_ms}} ms for Coinbase, so lifetimes shorter than a venue's publication interval are unobservable in this data.

**Proposed approach.** Separately tested components:
1. Ingest Tardis.dev quotes and our 12-venue websocket recorder.
2. Maintain an as-of book per venue and a 60 s EWMA fair basis per pair.
3. Detect executable crosses net of basis and fees, capped at top-of-book size.
4. Measure decay with survival analysis per venue pair.
5. **Decide (spike):** rank by *latency-conditioned executable value*, LEV(x, L): a gradient-boosted regressor trained on simulated execution-surplus labels clipped to ±30 bp, given market-state features and end-to-end latency L. We act if its prediction is positive.
6. Simulate: decide on received state; fill both IOC legs at each venue's book when each order arrives; unwind failed legs.
7. Paper-trade the same path live.

The compiled decision step (Numba, matching scikit-learn's predictions) takes, in-kernel, {{dec_p50_us}} µs at p50 and {{dec_p99_us}} µs at p99 on a shared laptop.

**Minimum Viable mapping.**
- *Detect mispricings with a threshold or statistical model:* running on real ticks.
- *Report how fast the opportunity typically decays:* survival curves with confidence intervals. The observed median lifetime is {{median_life_ms}} ms (hour-block 95% CI {{median_ci_lo}}–{{median_ci_hi}}). Shifting episode endpoints within the publication intervals gives an illustrative {{med_lo}}–{{med_hi}} ms sensitivity range, not a bound on executable lifetime. By pair type it is {{median_perp_perp}} ms (perpetual–perpetual), {{median_spot_perp}} ms (spot–perpetual) and {{median_spot_spot}} ms (spot–spot). Across {{n_months}} monthly samples of five markets it ranges from {{month_median_min}} to {{month_median_max}} ms.

**Stretch goals.**
- *Latency budget:* L = feed + compute + order. Compute takes microseconds; distance takes milliseconds. Tardis collectors see Binance perpetual quotes {{feed_fast_ms}} ms after the exchange timestamp (median), and the slowest venue {{feed_slow_ms}} ms after. At 1 bp per-leg fees, naive trading stops paying at {{be_naive}} ms one-way.
- *Paper trading:* planned for 1–14 Dec; the live recorder already captures 12 venues.

**Novelty.** Our contribution is a falsification-first decision benchmark on public data, not a new learner:
1. We rank by predicted value at arrival, conditioned on latency, and test that against a strong tuned baseline under several execution models.
2. Decay is reported together with its observability limits.
3. Registered tests, amendments and ablations are published whatever they show.

**Evaluation plan.** We fit on one month's first day and test on the next. Baselines are naive trading, a tuned per-pair × fee × latency threshold and survival EV. The metric is simulated execution surplus (fills after fees, marked against the fair basis), summed over six fee/latency scenarios.
- *Pre-registered: {{wf_n}} sampled months, {{wf_inspected}} of them previously inspected.* LEV beat the threshold in {{wf_pos}}/{{wf_n}} months, by a mean of {{wf_mean}}/day ({{wf_rel}}); 95% t-interval {{wf_tci}}. Verdict: {{wf_verdict}}. On the {{unseen_n}} months never inspected: {{unseen_pos}}/{{unseen_n}}, {{unseen_mean}}/day ({{unseen_tci}}).
- *Stricter simulators (registered amendment):* next-quote fills, a stress scenario, give {{v1_mean}}/day ({{v1_tci}}); adding a mark-to-mid 1 s later gives {{v2_mean}}/day ({{v2_tci}}). Verdict: {{sens_decision}} ({{v1_share}}, then {{v2_share}}).
- *Fragility:* dropping intents that reuse a quote already hit ({{collide_lev}} of LEV's selected intents) leaves {{s3_mean}}/day ({{s3_tci}}). A LEV trained on optimistic fills {{v4_phrase}} ({{v4_mean}}/day, {{v4_tci}}).
- *Attribution (exploratory):* with the frozen simulator, LEV beats a GBM classifier by {{x_gbm_mean}}/day ({{x_gbm_tci}}) and the same model without the latency input by {{x_noL_mean}}/day ({{x_noL_tci}}). With strict fills and markouts, these become {{x_gbm_v2_mean}} and {{x_noL_v2_mean}}/day ({{x_v2_sig}}). Survival EV trails the threshold ({{ev_vs_thr}}/day).

**Feasibility and risks.** [TEAM: skills — systems/latency, ML, quant.] Historical replay and the latency-budget analysis run; live recording works; paper trading is planned.

*Milestones:* abstract by 31 Oct; lead–lag and deeper-book fills 1–17 Nov; exams 19–25 Nov; midway report by 1 Dec; paper trading and demo 1–14 Dec.

*Risks:*
- Venue clocks differ; we re-test conclusions under receive-time replay.
- Publication grids hide sub-cadence dynamics. Our recorder's channels are finer (Binance perpetual {{live_bnf_ms}} ms median versus {{cad_bnf_ms}} ms in the samples; OKX {{live_okx_lo}}–{{live_okx_hi}} ms versus {{cad_grid_ms}} ms), so the finals rerun the benchmark on our own recordings.
- Fees can erase every edge (Coinbase Exchange's lowest-volume taker fee is 60 bps).
- Public replay cannot pin down LEV's value (from within noise to {{wf_mean}}/day, depending on execution assumptions), and simulated fills cannot establish real fillability, so LEV is a benchmark result, not a validated edge.
