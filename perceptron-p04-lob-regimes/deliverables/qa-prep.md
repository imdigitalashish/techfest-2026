# Q&A prep — hostile judge questions with evidence (draft v1, 2026-10-04)

> Every number traces to a committed results file; `python eval/check_numbers.py` checks this page too. Held-out numbers come from [`eval/results/v2_holdout.md`](../eval/results/v2_holdout.md): 22 days, 2025-01 … 2026-10, models trained on 2023 only, 97.5% paired day-cluster bootstrap CIs.

**1. "A regime-switching model is decades old. What is new?"**
Conditioning on volatility is classical, and we say so. Our contribution is the evidence: under a pre-registered protocol, *conditioning* beats *refitting*.
- Regime gate vs static: −0.0099 log-loss, better on 22/22 days.
- Textbook KS→retrain vs static: +0.0268, worse on 21/22 days.
- Daily retraining vs static: −0.0009, CI spans 0.

On top of that we add a monitor that knows when *not* to trust the model. It has two parts: a calibrated KS audit and a harm gate.

**2. "Is any of this tradable?"**
Not as a taker.
- Gross edge is 0.297 bps per signal and the spread is 0.013 bps.
- After crossing the spread 100 ms late, the break-even fee is 0.132 bps per side.
- Binance's published taker fees are 5.0 bps (Regular) and 1.7 bps (VIP 9).
- Even the top-decile confidence rule (+0.414 bps taker) does not clear fees.

The maker upper bound is positive only at a 0% maker fee, and it ignores queue position and adverse selection. The value is as an input to quoting: skew, size, and abstain when the harm gate fires.

**3. "Where could look-ahead hide?"**
- **Clock.** All as-of joins use receive time, the only clock a live system has.
- **Features.** A test perturbs the future and checks that past features are unchanged.
- **Labels.** A test corrupts labels after step s and checks that predictions up to s + 10 s are unchanged. It covers the abstain expert, the harm gate and the shrink path.
- **Fitting.** Regime edges, scalers and the KS null come from 2023 only. Walk-forward refits use days strictly before the evaluated day.

**4. "Latency?"**
- Python reference, `spike_gate`: 3.3 µs per prediction and 4.8 µs per full online step (p50, median over held-out days).
- Budget for the compiled step: ≤50 µs p99.
- Context: the median exchange-to-receive delay on the same feed is 2.9 ms (measured on 2023-11-01).

**5. "Why log-loss and not accuracy or F1?"**
Log-loss is a proper scoring rule, so it rewards calibration. That matters for quoting, where p sets the skew size. AUC and accuracy are reported alongside it.

**6. "Why only first-of-month days?"**
Those are the only free tick-level days on Tardis.dev; every other day returns 401. We use all 46, so there is no day selection. Because the days are non-contiguous, between-day shifts dominate the evaluation. More event days are available: Binance's continuous `bookTicker` archive covers 2023-05 … 2024-03, including CPI and FOMC days.

**7. "Your harm gate adds nothing on the holdout."**
That is correct on average: +0.0006 vs the regime gate alone, which Amendment 1 predicted from dev. The gate targets rare windows in which the model is worse than a coin flip. No verified scheduled event falls on a free holdout day, so its value is unproven. Getting event days is the next step.

**8. "Why does the textbook KS fire 48 times a day?"**
Its p-value assumes i.i.d. samples. Our windows are autocorrelated, the reference has tens of thousands of points, and activity levels (message rate, depth) drift from month to month. Calibrating against an empirical leave-one-day-out null and monitoring only level-comparable features brings it down to 0.7 alarms/day on the holdout. Refitting on 30-minute windows overfits noise.

**9. "Why BTCUSDT, a 1 s grid and a 10 s horizon?"**
- BTCUSDT: free tick data with both exchange and receive timestamps, and a liquid market that sits at a one-tick spread almost all the time.
- 10 s horizon: labels become observable quickly, so online adaptation is possible, and tie rates stay manageable (per-day tie rates are in the results' regime table).
- Equities next: LOBSTER samples.

**10. "Why not an HMM or BOCPD for regimes?"**
We will compare them. The volatility gate is the transparent, O(1) baseline that any latent-regime model must beat on the same pre-registered protocol.
