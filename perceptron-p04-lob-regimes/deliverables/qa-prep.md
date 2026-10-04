# Q&A prep — hostile judge questions with evidence (draft v1, 2026-10-04)

> Every number traces to a committed results file; `python eval/check_numbers.py` checks this page too. Held-out numbers come from [`eval/results/v2_holdout.md`](../eval/results/v2_holdout.md): 22 days, 2025-01 … 2026-10, models trained on 2023 only, 97.5% paired day-cluster bootstrap CIs.

**1. "A regime-switching model is decades old. What is new?"**
Conditioning on volatility is classical, and we say so. Our contribution is the evidence: under a pre-registered protocol, *conditioning* beats *refitting*.
- Regime gate vs static: −0.0099 log-loss, better on 22/22 days.
- Textbook KS→retrain vs static: +0.0268, worse on 21/22 days.
- Daily retraining vs static: −0.0009, CI spans 0.

A post-hoc ablation confirms that the regime heads carry the gain: −0.0083 against one head on the same EWMA features, better on 22/22 days. The monitor (KS audit plus CUSUM shrinkage) adds no average gain.

**2. "Is any of this tradable?"**
Not as a taker.
- Gross edge is 0.297 bps per signal and the spread is 0.013 bps.
- After crossing the spread 100 ms late, the break-even fee is 0.132 bps per side.
- Binance's published taker fees are 5.0 bps (Regular) and 1.7 bps (VIP 9).
- Even the top-decile confidence rule (+0.414 bps taker) does not clear fees.

The maker upper bound is positive only at a 0% maker fee, and it ignores queue position and adverse selection. Its value for quoting (skew, size) is a hypothesis we have not tested; we make no claim of maker profitability.

**3. "Where could look-ahead hide?"**
- **Clock.** All as-of joins use receive time, the only clock a live system has.
- **Features.** A test perturbs the future and checks that past features are unchanged.
- **Labels.** A test corrupts labels after step s and checks that predictions up to s + 10 s are unchanged. It covers the abstain expert, the harm gate and the shrink path.
- **Fitting.** Regime edges, scalers and the KS null come from 2023 only. Walk-forward refits use days strictly before the evaluated day.

**4. "Latency?"**
- Python reference, `spike_gate`: prediction 3.3 µs p50; adapter step 4.8 µs p50 and 85.6 µs p99 (median over days, feature computation excluded).
- Budget for the compiled step: ≤50 µs p99. **Not yet met**, and end-to-end latency is not yet measured.
- Context: Tardis's exchange-to-receive feed delay has a 2.9 ms median over 46 days (`eval/results/feed_delay.md`).

**5. "Why log-loss and not accuracy or F1?"**
Log-loss is a proper scoring rule, so it rewards calibration. That matters for quoting, where p sets the skew size. AUC and accuracy are reported alongside it.

**6. "Why only first-of-month days?"**
Those are the only free tick-level days on Tardis.dev; every other day returns 401. We use all 46, so there is no day selection. Because the days are non-contiguous, between-day shifts dominate the evaluation. More event days are available: Binance's continuous `bookTicker` archive covers 2023-05 … 2024-03, including CPI and FOMC days.

**7. "Your harm gate adds nothing on the holdout."**
That is correct. It makes the average slightly worse (+0.0006, CI +0.0003 to +0.0009), as Amendment 1 predicted from dev. It is a heuristic, not a calibrated test. It targets rare windows in which the raw model does worse than a coin flip, and since no verified event falls on a holdout day, any benefit is unproven. It also only shrinks confidence: it does not change the trade direction.

**8. "Why does the textbook KS fire 48 times a day?"**
Its p-value assumes i.i.d. samples. Our windows are autocorrelated, the reference has tens of thousands of points, and activity levels (message rate, depth) drift from month to month. Using empirical leave-one-day-out thresholds and monitoring only level-comparable features brings it down to 0.7 alarms/day on the holdout. That is an alarm rate, not a verified false-alarm rate, and the thresholds come with no guarantee. Refitting on 30-minute windows overfits noise.

**9. "Why BTCUSDT, a 1 s grid and a 10 s horizon?"**
- BTCUSDT: free tick data with both exchange and receive timestamps, and a liquid market that sits at a one-tick spread almost all the time.
- 10 s horizon: labels become observable quickly, so online adaptation is possible, and tie rates stay manageable (per-day tie rates are in the results' regime table).
- Equities next: LOBSTER samples.

**10. "Why not an HMM or BOCPD for regimes?"**
We will compare them. The volatility gate is the transparent, O(1) baseline that any latent-regime model must beat on the same pre-registered protocol.

**11. "Was your holdout really unseen?"**
Not entirely, and we say so. The protocol was committed before evaluation, but one of the 22 held-out days (2025-08-01) had been read in an earlier exploratory run. Excluding it changes no conclusion (`eval/results/v2_holdout_sensitivity.md`). The registered method (Fixed-Share) failed H1. The regime gate with confidence shrinkage was added after dev and before the holdout run, so it is reported as secondary.

**12. "Your gate mostly picks the high-volatility head. Isn't it just one better model?"**
No; we tested this post hoc (exploratory). Every head alone does worse than the gate on the 22 held-out days:
- high-vol head alone: +0.0141 log-loss, better on only 1/22 days;
- mid-vol head alone: +0.0138;
- low-vol head alone: +0.0526.

On held-out days the gate selects the low/mid/high heads 20.7% / 33.2% / 46.0% of the time, and the mix swings by day: 2026-01-01 is 75.7% low-vol, 2026-03-01 is 93.7% high-vol. The gain comes from switching (`eval/results/v2_holdout_posthoc_heads.md`, `eval/results/head_usage.md`).

