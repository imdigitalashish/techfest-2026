# Round 1 abstract — final draft (v2.1, after cross-model review, 2026-10-04)

**Title:** Knowing when the book has changed: shift audits and regime-conditioned heads for 10-second order-book forecasting

**Theme 3 · Problem 4 — Order Book Forecasting Under Regime Shifts**

## Problem & theme chosen
Market makers quote on short-horizon order-book forecasts, which degrade silently around macro releases and liquidity shocks, exactly when errors cost most. It fits our team: streaming systems under latency budgets, and rigorous evaluation.

## Understanding of the challenge
At one-second resolution non-stationarity is the norm, so a rolling KS test on autocorrelated windows rejects almost always. On real Binance data our tested "KS alarm → refit" configuration fired 48 times a day (its cap) and made forecasts worse on 21 of 22 held-out days.

The difficulty: separating harmful from benign shifts when labels arrive 10 s late, and adapting without refitting on tiny noisy windows, within a latency budget and without look-ahead.

Order-flow price impact scales inversely with depth (Cont, Kukanov & Stoikov 2014), so the feature-to-move mapping is state-dependent; trailing volatility is our cheap state proxy.

## Proposed approach
- **Data:** Binance USD-M BTCUSDT five-level books from Tardis.dev, aligned on receive time. We use all 46 available first-of-month days (2023-01 to 2026-10); this is a calendar-restricted convenience sample. A transfer test on LOBSTER equities is planned.
- **Pipeline:**
  - causal depth-normalised OFI over 1/5/30 s;
  - queue and depth imbalance, micro-price, spread and realised volatility;
  - EWMA normalisation;
  - three logistic heads, selected by training-defined terciles of trailing ten-minute volatility.
- **Monitor:**
  - **Covariate audit:** rolling KS with empirical leave-one-training-day-out thresholds; no action, no false-alarm guarantee.
  - **Shrinkage trigger:** a CUSUM heuristic on the raw gated model's delayed log-loss above ln 2 (a coin flip's loss) moves forecasts halfway to 0.5 for five minutes. This is confidence shrinkage, not a certified harm test or a no-trade rule.
- **Tools:** Python, polars, NumPy/Numba and scikit-learn.

## Minimum Viable
1. **Predict direction:** up versus down, conditional on a non-zero 10-s move (ties excluded from scores, not markouts); held-out AUC 0.6746.
2. **Detect a shift and react:** the CUSUM drives the reaction. In an illustrative development replay (2024-05-01) the KS audit fired within 10 minutes of the 18:00 UTC FOMC statement and the CUSUM within 20, shrinking forecasts. A labelled semi-synthetic splice of two real days adds a known changepoint for testing that reaction.

## Stretch ambitions
- **Multiple regime heads:** implemented. Against a single EWMA-normalised head they cut held-out log-loss by 0.0083 (post-hoc ablation, 22/22 days). Each head alone does worse than switching (+0.0138 to +0.0526).
- **Latency:** target ≤50 µs p99 per compiled step including features and detectors. The Python adapter step is 4.8 µs p50 but 85.6 µs p99 (excluding features): unmet; end-to-end latency is unmeasured. Feed delay (Tardis) has a 2.9 ms median.
- **Next:** a spread-change head.

## Novelty / differentiation
Our contribution is a reproducible, pre-registered evaluation of shift audits and adaptation actions on real order books, not a new detector. It separates covariate audits, model-loss alarms and confidence shrinkage, and keeps failed variants as ablations.

UQ-LOB's realised-outcome conditioning, Jeon's event-clustered liquidity states and Podkopaev–Ramdas risk monitoring are close foundations. We test our integration against a single EWMA head, plain gating, a GBDT and daily retraining.

## Evaluation plan
**Protocol.** Pre-registered (plus one amendment) before evaluation: train on 12 monthly days from 2023, tune on 12 from 2024, evaluate once on 22 from 2025-01 to 2026-10. One evaluation day (2025-08-01) was seen in an earlier exploratory run; excluding it changes no conclusion. Updates are prequential and respect the 10-s label delay. Primary measure: pooled non-tie log-loss, with paired day-cluster bootstrap 97.5% intervals (Bonferroni across the two registered hypotheses).

| Policy (Δ vs static model) | Δ log-loss [97.5% CI] | Days better |
|---|---|---|
| Registered Fixed-Share spike (H1) | −0.0010 [−0.0044, +0.0020] | 10/22 |
| Regime gate (secondary) | −0.0099 [−0.0136, −0.0068] | 22/22 |
| Regime gate + shrinkage (post-dev, pre-holdout) | −0.0093 [−0.0129, −0.0062] | 22/22 |
| Static GBDT | −0.0052 | 16/22 |
| Daily walk-forward retraining | −0.0009 | 12/22 |

- **H2 supported:** the registered spike beats KS→refit (−0.0278).
- **H1 not supported:** it does not beat the static model.
- **Shrinkage costs a little:** it worsens average loss by +0.0006 (CI +0.0003 to +0.0009). Its benefit around events is unproven: there is one development event and none on the evaluation days.
- **Next:** freeze event-window metrics before testing on event-rich continuous data.

**Edge.** Gross markout is 0.297 bps per signal. Executing on the visible book 100 ms later gives a break-even fee of 0.132 bps per side, below Binance's published taker fees of 1.7–5.0 bps. This is not a viable standalone taker strategy. Maker estimates assume passive fills at the touch, and quoting value, inventory risk and adverse selection remain untested.

## Feasibility and risks
**Team:**
- Ashish (confirmed): streaming/large-scale systems and ML engineering; owns the online pipeline.
- [TEAM — member 2: name; statistics and evaluation]
- [TEAM — member 3: name; data and demo integration]

**Timeline.** The 22-day evaluation runs in ~4 minutes on one laptop.

| When | Milestone |
|---|---|
| October, weeks 3–4 | Event-rich data, matched ablations, spread head |
| November, weeks 1–2 | Compiled timing, replay integration |
| 17 November | Freeze, before the 19–25 Nov exams |
| December | Recorded-replay demo with a no-change control (no live shock needed) |

**Risks:**
- calendar and instrument selection;
- the shrinkage's benefit is unproven;
- data access.

Independent event-rich data, negative controls and end-to-end latency are acceptance gates, not completed evidence.
