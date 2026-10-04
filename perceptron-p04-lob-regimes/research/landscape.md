# Landscape: short-horizon LOB forecasting under regime shifts

> Perceptron 2026 · Problem 4. Compiled 2026-10-04 by the project lead. Every source was opened on 2026-10-04 by the lead or by a research worker whose notes are in [`notes/`](notes/), which hold the per-source entries with quotes. Anything not opened is marked **UNVERIFIED**. Our own numbers come from [`../eval/results/baseline.md`](../eval/results/baseline.md).

## 1. Summary

1. **Models are commoditising; robustness is the gap.** Deep LOB forecasters (DeepLOB → TLOB) keep improving on benchmarks, yet TLOB reports that stock-price predictability has *declined* over time (−6.68 F1) and that redefining labels by the average spread hurts performance [TLOB]. The LOBCAST benchmark exists precisely because results did not carry over between datasets [LOBCAST].
2. **Order-flow imbalance is the strongest known short-horizon driver.** Its price-impact slope scales with 1/depth [CKS]. A liquidity shock therefore changes the *mapping* from features to outcomes, not just the feature scales. Multi-level OFI improves out-of-sample fit as levels are added [MLOFI].
3. **Shift detection in theory has moved past KS.** Recent work offers sequential, anytime-valid detectors with false-alarm control (e-detectors [E-DET]; conformal test martingales [CTM], with 2026 optimal constructions [CTM-OPT]) and tests for *harmful* shift (risk tracking) rather than any shift [HARM]. Most shift tests "detect arbitrary shifts (benign or harmful)" [HARM]. On our data, a naive rolling KS rejects all the time (§6).
4. **Adaptation research is rich, but little of it targets microsecond budgets.** Options range from normalisation (DAIN, RevIN, SAN) and online ensembling (OneNet) to proactive adaptation under label delay (Proceed, KDD 2025) and expert tracking with adaptive regret (Fixed-Share, AdaHedge, strongly adaptive learning). Most were built for minute-to-day forecasting, not a sub-millisecond loop.
5. **Industry practice: online learning and time-ordered validation win.** The Optiver *Trading at the Close* winner says online learning "play[s] an important role" [OPT-TATC-1]. The Jane Street competition warns that series "can be non-stationary" [JS]. Two Sigma models regimes with a Gaussian mixture [TS].
6. **The 2026 frontier sits next door to us but does not do our task.** UQ-LOB conditions forecasts on recently *realised* windows [UQ-LOB]. Jeon (2026) studies Binance BTCUSDT futures around macro events with event-clustered validation [JEON]. Latency-aware LOB architectures are appearing [ICF, LOBIN]. None of them combines **calibrated shift detection, harm-gated adaptation and a latency budget** in one online loop, which is our pitch.

## 2. Forecasting models and benchmarks (newest first)

| Source | Claim (as stated in the source) | Maturity | Use for us |
|---|---|---|---|
| [UQ-LOB] Manoharan et al., *UQ-LOB: Uncertainty-Aware LOB Mid-Price Forecasting*, arXiv 2609.31491 (2026-09-25), https://arxiv.org/abs/2609.31491 | Lightweight, encoder-agnostic UQ module. It "conditions each forecast on a context set of recently completed windows whose outcomes are already realised" and gives a calibrated Gaussian or categorical output. | paper (code UNVERIFIED) | Closest idea to our label-delayed adaptation, but it targets calibration, not detection. Cite as related work. |
| [ICF] Hedges, *The Inference-Compute Frontier and a Latency-Efficient Architecture for LOB Prediction*, arXiv 2606.25986 (2026-06-24), https://arxiv.org/abs/2606.25986 | Loss against compute follows a power law on FI-2010 (R²=0.941 extrapolating to MLPLOB). The fit in *latency* space is "substantially weaker", so latency must be measured, not inferred from FLOPs. | paper | Supports our measured-latency protocol (C9). |
| [LOBIN] Hong et al., *In-Network Market Prediction Using ML and LOBs*, arXiv 2608.02424 (2026-08-03), https://arxiv.org/abs/2608.02424 | LOBIN builds the LOB and runs inference inside programmable switches. | paper | Frontier reference for the latency stretch goal: our tiny linear heads suit such hardware. |
| [JEON] Jeon, *When Does Order Flow Matter? State-Dependent L2 Liquidity-State Transitions in Crypto Futures*, arXiv 2607.09230 (2026-07-10), https://arxiv.org/abs/2607.09230 | Binance BTCUSDT/ETHUSDT futures 2023–2026, top-20 L2, macro-event windows, rolling monthly out-of-sample folds, event-clustered validation, blocked permutation tests. | paper | Closest prior art on data and protocol. We differ: forecasting plus online detection and adaptation, not liquidity-state classification. |
| [XEVT] Zaman et al., *Volatility-Aware Extreme Event Detection in HF Financial Markets*, arXiv 2607.17555 (2026-07-20), https://arxiv.org/abs/2607.17555 | Bitcoin LOB. Non-stationarity, heavy tails and imbalance; the target combines large returns with high-volatility regimes. | paper | Supports volatility-regime heads. |
| [CRUMBLE] Xu et al., *When Quotes Crumble*, arXiv 2604.21993 (2026-04-23), https://arxiv.org/abs/2604.21993 | Uses ABIDES with stochastic market-maker regime switches to get time-resolved ground truth that real data lack. | paper | Supports our semi-synthetic ground-truth changepoints for detector evaluation. |
| [TLOB] Berti & Kasneci, *TLOB*, arXiv 2502.15757 (2025), https://arxiv.org/abs/2502.15757 · code https://github.com/LeonardoBerti00/TLOB (stars/commit UNVERIFIED) | Dual-attention transformer, best on FI-2010, NASDAQ and BTC. A simple MLP beats earlier SoTA. New labelling "removes horizon bias". Predictability declined (−6.68 F1). Spread-based labels deteriorate performance. | maintained code | Stronger head candidate later. Our label is raw point-to-point (no smoothing). We report edge net of spread. |
| [LOB-Bench] Nagy et al., *LOB-Bench*, arXiv 2502.09172 (2025-02-13), https://arxiv.org/abs/2502.09172 | Benchmark for generative LOB models. | paper + code (UNVERIFIED) | A generator could create controlled regime shifts. Stretch only. |
| [LOBCAST] Prata et al., *LOB-Based Deep Learning Models for Stock Price Trend Prediction: A Benchmark Study*, arXiv 2308.01915 (2023), https://arxiv.org/abs/2308.01915 | Benchmark of deep LOB models. Robustness/generalisation numbers UNVERIFIED (not opened beyond the title). | code (UNVERIFIED) | Motivation only. |
| [DeepLOB] Zhang, Zohren & Roberts, arXiv 1808.03668 (IEEE TSP 2019), https://arxiv.org/abs/1808.03668 | CNN+LSTM on raw 10-level snapshots. Validated out of sample on a year of LSE data. | code | Head option behind the C5 contract. |
| [FI-2010] Ntakaris et al., arXiv 1705.03233 (J. Forecasting 2018), https://arxiv.org/abs/1705.03233 | First public LOB benchmark: 5 Nasdaq Nordic stocks, 10 days, pre-normalised, smoothed labels, anchored day-based CV. | dataset | Not used. It is pre-normalised and has no calendar time, so we cannot place events. |

Not opened tonight: *Deep LOB forecasting: a microstructural guide* (Briola et al.) — the arXiv title search returned no hit; Kolm, Turiel & Westray *Deep order flow imbalance*; Lucchese et al. 2024; MarS (Microsoft). Leads only, all UNVERIFIED.

## 3. Microstructure features

- [CKS] Cont, Kukanov & Stoikov, *The Price Impact of Order Book Events*, arXiv 1011.6402 (J. Fin. Econometrics 2014), https://arxiv.org/abs/1011.6402. Over short intervals, price changes are mainly driven by order-flow imbalance. The relation is linear, with a slope inversely proportional to market depth. → **C2 computes depth-normalised OFI.** This is the first-principles reason a liquidity shock is a *concept* shift (see `notes/features-labels.md`).
- [MLOFI] Xu, Gould & Howison, arXiv 1907.06230, https://arxiv.org/abs/1907.06230. Multi-level OFI (one OFI per level). Out-of-sample fit improves as levels are added, on 6 Nasdaq stocks. → **C2 computes level-1 and 5-level OFI over 1/5/30 s.**
- Queue imbalance (Gould & Bonart 2016) and the micro-price (Stoikov 2018) are used as features. Their papers were **not opened tonight (UNVERIFIED)**, and the formulas are the standard ones in our code.

## 4. Shift detection (details and quotes: [`notes/shift-detection-sota.md`](notes/shift-detection-sota.md))

| Detector | Monitors | Guarantee | Per-update cost | Labels? | Source |
|---|---|---|---|---|---|
| Rolling two-sample KS / KSWIN | feature distribution | p-value assumes i.i.d. | O(w log w) per test | no | River KSWIN docs https://riverml.xyz/latest/api/drift/KSWIN/ |
| ADWIN | mean of a stream (e.g. loss) | false-positive bound | O(log w) | if fed loss | https://riverml.xyz/latest/api/drift/ADWIN/ |
| Page-Hinkley / CUSUM | mean shift | threshold set from α, β, δ (NIST V-mask) | O(1) | if fed loss | River source; NIST §6.3.2.3 https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm |
| BOCPD [BOCPD] | predictive model of a stream | Bayesian posterior over run length | O(run length) or pruned | no | Adams & MacKay, https://arxiv.org/abs/0710.3742 |
| Robust β-divergence BOCPD | same, outlier-robust | — | "linear time, constant space" | no | Knoblauch et al., https://arxiv.org/abs/1806.02261 |
| E-detectors [E-DET] | any e-process | non-asymptotic ARL control | O(1)–O(#bases) | either | Shin, Ramdas & Rinaldo, https://arxiv.org/abs/2203.03532 |
| Conformal test martingales [CTM] | conformal p-values of the model | exchangeability test, retrain-or-not | O(1) amortised | no | Vovk et al., https://arxiv.org/abs/2102.10439 |
| Optimal CTM [CTM-OPT] | same | proves existing constructions have Ω(T) delay; new ones reach Θ(log T) (per notes) | — | no | Bhattacharyya & Ramdas, arXiv 2609.27179 (2026-09-23), https://arxiv.org/abs/2609.27179 (title, date and authors verified by the lead) |
| Harmful-shift tracking [HARM] | model *risk* (loss) | sequential, time-uniform | O(1) | yes (delayed) | Podkopaev & Ramdas ICLR 2022, https://arxiv.org/abs/2110.06177 |
| Failing loudly [FL] | low-dim projection + two-sample test | — | — | no | Rabanser et al., https://arxiv.org/abs/1810.11953 — "using pre-trained classifiers for dimensionality reduction, performs best" |
| Evaluation | — | F1 with a tolerance margin, covering; annotators disagree | — | — | TCPDBench, van den Burg & Williams, https://arxiv.org/abs/2003.06222 |

**Pitfall (our own measurement, not a citation):** on 1-second LOB features, Bonferroni-corrected rolling KS at α=1e-3 alarmed at its cooldown cap — 48 alarms on every one of 6 evaluation days ([baseline.md](../eval/results/baseline.md)). The research worker could not find a primary source quantifying KS false alarms under autocorrelation. We therefore *measure* the null on calm training data instead of trusting asymptotic p-values.

## 5. Adaptation (details: [`notes/adaptation-sota.md`](notes/adaptation-sota.md))

| Family | Representative (opened) | Idea | Fit for a µs loop |
|---|---|---|---|
| Normalisation | DAIN https://arxiv.org/abs/1902.07892 · RevIN https://github.com/ts-kim/RevIN · SAN (NeurIPS 2023) https://proceedings.neurips.cc/paper_files/paper/2023/hash/2e19dab94882bc95ed094c4399cfda02-Abstract-Conference.html | remove shifting statistics from the inputs | ✔ — our C4 EWMA z-score is the streaming analogue |
| Online ensembling | OneNet https://arxiv.org/abs/2309.12659 · FSNet https://arxiv.org/abs/2202.11672 | combine fast and slow learners online | ✔ for linear heads |
| Proactive / label delay | Proceed (KDD 2025) https://arxiv.org/abs/2412.08435 | adapt *before* the delayed labels arrive, using estimated drift | ✔ idea: pre-emptively switch heads on label-free signals |
| Meta / data-distribution | DoubleAdapt https://arxiv.org/abs/2306.09862 · DDG-DA (Microsoft Qlib) https://arxiv.org/abs/2201.04038 · TAFAS https://arxiv.org/abs/2501.04970 | learn how to adapt | ✘ for the hot path (offline refits only) |
| Expert tracking | Fixed-Share (Herbster & Warmuth; not opened) · AdaHedge https://export.arxiv.org/abs/1301.0534 · strongly adaptive learning https://arxiv.org/abs/1502.07073 | regret against the best *switching* sequence of experts | ✔ O(K) per step — our C7 mixer |
| Calibrated sets under shift | ACI https://arxiv.org/abs/2106.00170 · conformal PID https://arxiv.org/abs/2307.16895 | keep coverage under arbitrary shift | ✔ stretch: abstain/size-down signal |

## 6. What our first baseline already shows (real data, committed run)

Command: `python eval/run_baseline.py` → [`eval/results/baseline.md`](../eval/results/baseline.md). Setup: Binance USD-M BTCUSDT, Tardis `book_snapshot_5`, 1 s grid, 10 s horizon, prequential, labels only after they would be observed. Train 2 days (2023), dev 3 days (2023), holdout 3 days (2024–25).
- **Silent degradation:** a static logistic model goes from log-loss 0.6473 / AUC 0.674 (dev, 2023) to 0.6808 / 0.618 (holdout, 2024–25).
- **Naive "rolling KS → refit" is worse than doing nothing:** Δlog-loss +0.0167 [+0.0115, +0.0220] dev and +0.0202 [+0.0157, +0.0247] holdout (95% moving-block bootstrap), with 48 alarms per day.
- **Regime-adaptive heads help most:** −0.0133 [−0.0156, −0.0113] dev and −0.0132 [−0.0148, −0.0115] holdout. They are also the best policy in both FOMC windows (event −30 min … +60 min). For example, on 2024-05-01 log-loss is 0.7010 against 0.7329 for the static model.

### 6b. Pre-registered v2 evaluation (46 days, holdout 2025-01 … 2026-10)
- **Setup.** Protocol: [`eval/PREREGISTRATION.md`](../eval/PREREGISTRATION.md). Results: [`eval/results/v2_holdout.md`](../eval/results/v2_holdout.md). Train on 2023 (12 days), tune on 2024 (12), report 22 held-out days once. CIs are 97.5% paired day-cluster bootstraps.
- **Textbook KS→retrain** is +0.0268 [+0.0220, +0.0317] log-loss vs static and worse on 21/22 days.
- **Volatility-regime heads plus a harm gate**: −0.0093 [−0.0129, −0.0062], better on 22/22 days. Plain regime gating gives −0.0099 [−0.0136, −0.0068].
- **Other adapters:** static GBDT −0.0052; daily walk-forward retraining −0.0009 (the CI spans zero); Fixed-Share over online experts −0.0010 (the CI spans zero).
- **Calibrated KS** on 5 level-comparable features: 0.7 alarms/day. This is an alarm rate, not a verified false-alarm rate.
- **Post-hoc ablation:** regime heads vs one EWMA head: −0.0083.
- **Exposure:** one holdout day (2025-08-01) was seen in v1; excluding it changes nothing (`eval/results/v2_holdout_sensitivity.md`).
- **Is it tradable?** No:
  - gross edge is 0.297 bps per signal against a 0.013 bps spread;
  - break-even fee is 0.132 bps per side;
  - Binance's published taker fees are 5.0 bps (Regular) and 1.7 bps (VIP 9);
  - even the top-decile confidence rule (+0.414 bps taker) does not clear fees.

The forecast's value is as an input to quoting, not as a standalone strategy.

## 7. What companies ship today (details: [`notes/industry-what-companies-ship.md`](notes/industry-what-companies-ship.md))

| Org | What they ship or say (opened source) | Where we borrow or beat |
|---|---|---|
| **Optiver** | Kaggle *Realized Volatility Prediction* (10-minute volatility for hundreds of stocks) and *Trading at the Close* (closing-auction moves from order-book data), both scored on data collected *after* submission: https://www.kaggle.com/competitions/optiver-realized-volatility-prediction/overview · https://www.kaggle.com/competitions/optiver-trading-at-the-close/overview | Borrow: forward-in-time evaluation. Ours is prequential with label delay. |
| Optiver TATC winner (hyd) | CatBoost+GRU+Transformer. "online learning(OL) and post-processing(PP) also play an important role": https://www.kaggle.com/competitions/optiver-trading-at-the-close/writeups/hyd-1st-place-solution | Borrow: online updates. Beat: we add *when* to adapt (calibrated, harm-gated) and measure latency. |
| Optiver RVP top solution (nyanp) | Recovered the hidden time order and used time-series CV and covariate-shift checks: https://www.kaggle.com/competitions/optiver-realized-volatility-prediction/writeups/nyanp-1st-place-solution-nearest-neighbors (page title says 1st, body says public 2nd — see notes) | Borrow: covariate-shift diagnostics as a first-class step. |
| **Jane Street** | *Real-Time Market Data Forecasting*: "time series can be non-stationary": https://www.kaggle.com/competitions/jane-street-real-time-market-data-forecasting/overview. Top community thread on online CatBoost training: …/discussion/556544 | Borrow: online training as the default. |
| **Two Sigma** | GMM on 17 factors gives four market regimes: https://www.twosigma.com/articles/a-machine-learning-approach-to-regime-modeling/ | Borrow: unsupervised regimes. Beat: our regimes are microstructural (volatility, depth) and switch in milliseconds, not months. |
| **Tardis.dev** | Tick-level crypto order-book archives. First day of each month downloadable without a key (verified by download; other days return HTTP 401) | Our data source. |
| **Binance (fee schedule)** | USDⓈ-M Futures fee table, Regular User USDT maker/taker 0.0200%/0.0500%, VIP 9 0.0000%/0.0170%: https://www.binance.com/en/fee/futureFee (opened in a rendered browser 2026-10-04); BTCUSDT tickSize 0.10 via https://fapi.binance.com/fapi/v1/exchangeInfo | The cost side of our edge table; decides "is it tradable?" |
| Exchanges (Nasdaq Dynamic M-ELO, LULD bands, CME velocity logic) | Production rule-based regime detectors — **UNVERIFIED** tonight (the worker died before opening them) | Planned citation. Exchanges already run "shift detectors" with fixed rules; ours is learned and calibrated. |

## 8. Gaps → our innovation room

1. **Empirical-threshold rolling KS:** take thresholds from the *empirical* leave-one-training-day-out distribution of the windowed statistic instead of trusting i.i.d. p-values. *(Implemented. These are marginal per-feature quantiles; they give no daily false-alarm guarantee, and the training days include FOMC days. Review A5.)* Metric: realised false alarms/day on calm dev hours against the budget, and detection delay at the FOMC timestamps.
2. **Harm gating:** adapt only when a sequential test on the deployed model's delayed loss (CUSUM/e-detector [HARM, E-DET]) agrees that the shift hurts. Metric: Δlog-loss vs static, and the fraction of alarms followed by a real loss increase.
3. **Regime-adaptive heads.** *Superseded wording: Fixed-Share mixing with alarm-boosted switching failed H1 on the holdout. Hard volatility gating is what worked (−0.0083 vs a single EWMA head, post-hoc ablation).* Metric: holdout Δlog-loss with a bootstrap CI.
4. **A calendar-aware prior:** scheduled FOMC/CPI times are known in advance, so raising the switch prior around them causes no leakage. Metric: event-window log-loss.
5. **Latency as a contract:** p50/p99 per online step against a stated budget; Numba/C++ port. Metric: p99 µs.
