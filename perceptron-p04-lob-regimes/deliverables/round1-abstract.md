# Round 1 abstract — final draft (v2, 2026-10-04)

**Title:** Knowing when the book has changed: calibrated shift detection and regime-conditioned heads for 10-second order-book forecasting

**Theme 3 · Problem 4 — Order Book Forecasting Under Regime Shifts**

## Problem & theme chosen
Market makers quote on short-horizon order-book forecasts that silently degrade around macro releases and liquidity shocks, exactly when errors cost most. It fits our team: streaming systems under latency budgets, and rigorous evaluation.

## Understanding of the challenge
At one-second resolution non-stationarity is the norm (volatility clusters; depth and message rates drift monthly), so a rolling KS test on autocorrelated windows rejects almost always. On real Binance data the textbook test fires at its cooldown cap (48 alarms a day), and "retrain on every alarm" makes forecasts worse on 21 of 22 held-out days.

The real difficulty has three parts:
1. Separate harmful shifts from benign ones at a controlled false-alarm rate, when labels arrive 10 s late.
2. Adapt without refitting on tiny, noisy windows.
3. Do both inside a latency budget, without look-ahead.

Why models break: order-flow imbalance moves prices with slope ∝ 1/depth (Cont, Kukanov & Stoikov 2014), so liquidity regimes change coefficients, not just input scales.

## Proposed approach
- **Data:** Binance USD-M BTCUSDT 5-level order books from Tardis.dev. We use all 46 free days (the first of each month, 2023-01 to 2026-10), aligned on receive time. FOMC days, with release times from federalreserve.gov, serve as natural experiments. LOBSTER equity samples will test generality.
- **Pipeline:** nine typed components, already built, with leakage tests:
  - causal features: depth-normalised single- and multi-level OFI over 1/5/30 s, queue and depth imbalance, micro-price, spread, realised volatility;
  - an EWMA normaliser;
  - one logistic head per volatility regime, selected by trailing 10-minute volatility;
  - a shift monitor;
  - a prequential evaluator and a latency bench.
- **Shift monitor (the spike):**
  - **Calibrated rolling KS.** The brief's rolling KS, run only on features whose levels are comparable across months. Its thresholds come from an empirical leave-one-day-out null, which contains real autocorrelation and seasonality.
  - **Harm gate.** A CUSUM on the deployed model's delayed log-loss in excess of ln 2, the loss of a coin flip. While the model is demonstrably worse than abstaining, the gate shrinks forecasts toward 0.5 (after Podkopaev & Ramdas, ICLR 2022).
- **Tools:** Python, polars, NumPy/Numba, scikit-learn; PyTorch for a planned small neural head.

## Minimum Viable
1. **Predict short-term direction from order-book features.** The 10-second mid-price direction forecaster runs today; held-out AUC is 0.6746.
2. **Detect a shift with a simple test and show the model reacting.** On a replayed FOMC day (2024-05-01):
   - the calibrated KS fired 9.5 minutes after the 18:00 UTC statement;
   - the harm gate fired 18 minutes after it and moved forecasts toward abstention;
   - the textbook KS fired every 30 minutes all day.

## Stretch ambitions
- **Multiple regime-adaptive heads:** implemented. They are the main source of the gain so far.
- **Latency:** budget ≤50 µs p99 per compiled (Numba/C++) online step, versus a measured 2.9 ms median exchange-to-receive delay; the Python reference already predicts in 3.3 µs (p50).
- **Next:** a spread-change head, calendar-aware detection priors, and LOBSTER transfer.

## Novelty / differentiation
1. We measure that the obvious baseline, KS → retrain, is harmful, and explain why.
2. Detection is calibrated on an empirical null and split into a label-free audit signal and a label-based harm test.
3. Adaptation conditions on the state variable that theory names (volatility) instead of refitting.
4. "Is it tradable?" is answered with official exchange fees.

Recent work calibrates forecasts (UQ-LOB, 2026) or classifies liquidity states around macro events (Jeon, 2026); neither closes the detect→adapt loop under a latency budget.

## Evaluation plan
**Protocol.** Pre-registered before any held-out number existed: train on 2023 (12 days), tune on 2024 (12), report 2025-01 to 2026-10 (22) once. Evaluation is prequential: labels are used only once observable, and contract tests catch look-ahead. The primary test compares per-step log-loss with a paired day-cluster bootstrap (97.5% CIs, Bonferroni for two hypotheses). We also report AUC, alarms per day, event-window loss, and trading edge after crossing the spread 100 ms late and paying Binance's published fees.

**Held-out results so far** (Δ log-loss, negative is better):

| Policy | vs static model | vs KS → retrain |
|---|---|---|
| Regime heads + harm gate | −0.0093 (CI −0.0129 to −0.0062; better on 22/22 days) | −0.0361 |
| Static GBDT | −0.0052 | — |
| Daily retraining | −0.0009 (CI spans zero) | — |
| Fixed-Share mixture of online experts | −0.0010 (CI spans zero) | — |

The harm gate adds no average gain over gating alone (+0.0006); its job is rare event windows.

**Edge.** Gross 0.297 bps per signal versus a 0.013 bps spread, but the break-even fee is 0.132 bps per side against 1.7–5.0 bps taker fees: not a standalone taker strategy; its value is in quoting (skew, abstain).

## Feasibility and risks
**Team:**
- [TEAM — member 1: name, skills]
- [TEAM — member 2: name, skills]
- [TEAM — member 3: name, skills]

Ashish: streaming/large-scale systems, ML engineering.

Everything runs on one laptop (22 held-out days in ~4 minutes).

**Milestones:**

| When | Work |
|---|---|
| Oct weeks 3–4 | Calendar-aware priors, spread head, LOBSTER |
| Nov weeks 1–2 | Compiled online step, live websocket replay |
| 17 Nov | Freeze, before the 19–25 Nov exams |
| December | Finals demo |

**Risks and mitigations:**

| Risk | Mitigation |
|---|---|
| Small effects | Pre-registration and day-level CIs |
| One instrument | LOBSTER transfer |
| Harm-gate value concentrated in rare events | More event days from official calendars |
| Edge not tradable after fees | Framed as risk control: knowing when the model is wrong |
