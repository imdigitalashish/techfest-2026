# Round 1 abstract — draft v1 (2026-10-04)

**Title:** Knowing when the book has changed: calibrated shift detection and regime-adaptive heads for short-horizon order-book forecasting

**Theme 3 · Problem 4 — Order Book Forecasting Under Regime Shifts**

## Problem & theme chosen
Market makers quote against short-horizon order-book forecasts. Around a macro release, those forecasts silently degrade exactly when errors cost most. The problem suits our strengths: streaming systems with latency budgets, and careful statistical evaluation.

## Understanding of the challenge
At high frequency, non-stationarity is the norm (seasonality, volatility clustering, liquidity cycles), so a two-sample test on autocorrelated windows of thousands of points rejects almost always. On real Binance BTCUSDT data we measured exactly this: a Bonferroni-corrected rolling KS test (α = 10⁻³) fired at its cooldown cap, 48 times a day, on every evaluation day. Retraining on each alarm *raised* held-out log-loss by +0.020 (95% CI +0.016 to +0.025). "Detect a shift" is therefore easy and useless. The real problem has three parts:
1. Detect a **harmful** shift at a **controlled false-alarm rate**, knowing that labels arrive h seconds late.
2. Adapt without overfitting to tiny post-shift windows.
3. Do both inside a latency budget, without look-ahead.

Microstructure theory explains why the model breaks. Order-flow imbalance (OFI) moves prices with a slope inversely proportional to depth (Cont, Kukanov & Stoikov 2014), so a liquidity shock changes the model's coefficients, not just its input scales.

## Proposed approach
- **Data:** Binance USD-M BTCUSDT 5-level order books and trades from Tardis.dev's free monthly archives, aligned on *receive* timestamps. FOMC days give natural experiments with officially published release times (federalreserve.gov). We will add LOBSTER equity samples to check generality.
- **Pipeline (nine typed components, built and tested):** ingest → causal features (depth-normalised single- and multi-level OFI over 1/5/30 s, queue/depth imbalance, micro-price, spread, realised volatility) → labeler (10 s mid direction; spread change as a second head) → EWMA normaliser → heads (logistic; LightGBM and a small MLP behind the same interface) → **shift monitor** and **regime-adaptive mixer** (the spikes) → prequential evaluator and latency bench.
- **Shift monitor:** the rolling KS test required by the brief, with thresholds calibrated from an *empirical* null. That null is built from training days left out one at a time, so it contains real autocorrelation and seasonality. A sequential CUSUM / e-detector test on the deployed model's delayed loss (after Podkopaev & Ramdas, ICLR 2022) then confirms that a shift actually hurts before we act on it. A calendar prior raises sensitivity around scheduled releases, which are known in advance, so this causes no leakage.
- **Adapter:** offline heads per volatility/liquidity regime plus fast online heads, combined by a Fixed-Share expert mixer (O(K) per tick, tracking-regret guarantees). Confirmed alarms raise the mixer's switching rate rather than triggering blind refits.
- **Tools:** Python, polars, NumPy/Numba, scikit-learn, LightGBM, River, PyTorch/MLX.

## Minimum Viable mapping
1. *Predict short-term direction or spread from order-book features* → the 10 s direction forecaster on OFI features, scored by prequential log-loss and AUC. This runs today.
2. *Detect a distribution shift with a simple statistical test and show the model reacting* → the rolling KS test (as specified) and its calibrated version, replayed over an FOMC day. The demo shows the alarm timeline, mixer weights moving to the high-volatility head, and rolling log-loss against a frozen model.

## Stretch ambitions
- **Multiple regime-adaptive heads.** Already prototyped: on held-out 2024–25 days, volatility-regime heads cut log-loss by 0.013 (CI 0.012–0.015) against a static model, and were best in both FOMC windows.
- **Latency benchmarking.** Budget: ≤ 50 µs p99 for the whole online step, compiled. That is far below the 2.9 ms median exchange-to-receive delay we measured on the same feed. Our Python reference already predicts in 2–4 µs (p50).

## Novelty / differentiation
1. We show quantitatively that the obvious baseline hurts, and why.
2. Detection is calibrated and *harm-aware* instead of relying on i.i.d. p-values.
3. Alarms modulate expert switching instead of forcing refits.
4. Scheduled-event priors carry no leakage.
5. Detectors are judged by false alarms per calm day at a fixed detection delay against official event timestamps, not by anecdote.

Recent work (UQ-LOB, 2026; Jeon, 2026) calibrates forecasts or classifies liquidity states. Neither closes the detect → adapt loop under a latency budget.

## Evaluation plan
- **Data split and protocol:** split by date, frozen in code: train, dev (tuning only), holdout (reported only). Prequential test-then-train, with labels used only after they would be observable. Contract tests fail the build on any feature look-ahead.
- **Forecast metrics:** log-loss (primary), AUC, accuracy, and gross edge in basis points against the one-tick spread and exchange fees.
- **Detector metrics:** false alarms per calm day, detection delay after FOMC releases, and tolerance-window F1 on spliced streams with known change points.
- **Adaptation metric:** held-out Δlog-loss against the static model, with 95% moving-block-bootstrap intervals and Diebold–Mariano tests.
- **Latency:** p50/p99/p99.9 per step.
- **Baselines:** static model, periodic retraining, online SGD, naive KS→refit, Page-Hinkley→refit.
- **Ablations:** every component on and off.

## Feasibility and risks
- **Team:** *[Ashish — streaming/large-scale systems and ML engineering; teammates' names and skills to add]*.
- **Plan:**
  - Oct wk 2–3: grow data to 24+ days; harm gate.
  - Oct wk 4: GBDT/MLP heads; abstract.
  - Nov wk 1–2: compiled online step, live websocket replay, splice benchmark.
  - MVP and stretch frozen by 17 Nov, before exams.
  - Dec: finals demo polish.
- **Risks:**
  - Small effect sizes. Mitigated with more days and confidence intervals.
  - Crypto-to-equity transfer. Mitigated with LOBSTER samples.
  - Over-tuning on the dev split. Mitigated by the frozen holdout.
  - Edge too small to trade after costs. We frame the system as risk control: knowing when the model is wrong.
