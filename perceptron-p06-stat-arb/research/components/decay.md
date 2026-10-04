# C7 decay — opportunity survival model

## 1) Contract summary

C7 consumes `OpportunityFrame` episodes from C6: `duration_us`, `censored`, venue pair, edge, quote ages, spreads, short-term volatility, and related features. It emits a `DecayModel` with:

- `survival(t_grid, X) -> [n, len(t_grid)]`, i.e. `S(t | x)` on a microsecond/millisecond grid;
- `half_life_us(X)` for operational summaries;
- an MVP report: Kaplan-Meier curves by pair and edge bucket, median/p90 lifetimes, and `E[edge(t)] / edge(0)` decay curves.

The architecture baseline is Kaplan-Meier per pair; the spike target is covariate-conditioned survival. The isolated metric is integrated Brier score on a held-out day, with C-index and calibration of `S(L)` as secondary checks.

## 2) State of the art with opened sources

- **Kaplan-Meier is the right nonparametric MVP for censored lifetimes.** The lifelines survival-analysis page defines the Kaplan-Meier estimator as a product over event times with `d_i` events and `n_i` subjects at risk, and demonstrates censoring-aware fitting with `KaplanMeierFitter` ([lifelines KM tutorial](https://lifelines.readthedocs.io/en/latest/Survival%20analysis%20with%20lifelines.html)). This supports our per-pair and edge-bucket decay curves without assuming a lifetime distribution.
- **Cox models add covariates but impose proportional hazards unless extended/stratified.** lifelines documents `CoxPHFitter` as fitting `h(t|x)=h_0(t) exp((x - mean(x))' beta)`, with Breslow nonparametric baseline by default, spline/piecewise alternatives, Efron tie handling, and stratification for categorical covariates that do not satisfy proportional hazards ([lifelines CoxPHFitter](https://lifelines.readthedocs.io/en/latest/fitters/regression/CoxPHFitter.html)).
- **Gradient-boosted survival is a practical nonlinear upgrade.** scikit-survival documents gradient boosting with regression-tree base learners and a Cox partial-likelihood loss, replacing the linear Cox score with an additive model and allowing nonlinear feature effects ([scikit-survival gradient boosting](https://scikit-survival.readthedocs.io/en/stable/user_guide/boosting.html)). This is a good fit for edge size, quote ages, spread, volatility, and venue-pair interactions.
- **Neural Cox/non-proportional methods exist, but are probably not Round-1 default.** Kvamme, Borgan, and Scheel propose neural extensions of Cox regression, scalable loss approximations for large data sets, and report competitive performance in Brier score and binomial log-likelihood; the JMLR page also points to `pycox` ([JMLR 2019](https://jmlr.org/papers/v20/18-424.html)). DeepSurv is a feed-forward neural network version of Cox proportional hazards intended to learn nonlinear risk functions and treatment interactions ([DeepSurv PMC article](https://pmc.ncbi.nlm.nih.gov/articles/PMC5828433/)).
- **Evaluation should separate discrimination, probability accuracy, and calibration.** Haider et al. motivate individual survival distributions and evaluate them with concordance, 1-calibration, integrated Brier score, L1 losses, and D-calibration; they emphasize that risk scores and single-time probabilities are not full survival curves ([JMLR 2020](https://jmlr.org/papers/v21/18-772.html)). This maps directly to our need to evaluate `S(L|x)` and the full `S(t|x)` curve.
- **Finance precedent: limit-order fill-time survival is very close to our label geometry.** The research worker opened Arroyo et al., “Deep Attentive Survival Analysis in Limit Order Books: Estimating Fill Probabilities with Convolutional-Transformers,” and verified that it estimates fill probabilities/survival from LOB time series with a causal convolution/Transformer encoder ([arXiv page](https://arxiv.org/abs/2306.05479)). Treat this as the closest opened precedent, but note our event is “cross-asset opportunity remains executable,” not “one limit order fills.”
- **Conformal survival is a possible uncertainty wrapper, but details are not yet verified.** The opened arXiv page for “Conformalized Survival Analysis” only exposed the title in this session ([arXiv page](https://arxiv.org/abs/2103.09763)). Any finite-sample coverage or right-censoring claims must remain **UNVERIFIED** until the paper text is opened.
- **UNVERIFIED gaps:** DeepHit specifics, log-normal/Weibull AFT implementation details, D-calibration formula details, and classical limit-order Cox-fill papers were not opened sufficiently here. Do not cite them as facts in the submission without a follow-up source pass.

## 3) Baseline we ship now

Ship a two-layer baseline:

1. **Report baseline: stratified Kaplan-Meier.**
   - Fit separate KM curves by `(sell_venue, buy_venue, instrument/pair)` and coarse `edge0_bps` buckets.
   - Use receive-time episode durations only; mark right-censored episodes at file/session end and any episode whose termination cannot be observed because one venue stream ends early.
   - Produce median lifetime, p90 lifetime, survival at latency grid points, and `edge(t)/edge(0)` curves for the MVP “how fast does it decay?” requirement.
2. **Policy baseline: discrete-time hazard table.**
   - Bucket time logarithmically: e.g. 0-1 ms, 1-2 ms, 2-5 ms, 5-10 ms, 10-25 ms, 25-50 ms, 50-100 ms, then wider bins.
   - Estimate per-bin hazards with shrinkage by venue pair and edge bucket.
   - Convert hazards to `S(t|x)` for C8.

If data volume supports it, add a first covariate model: gradient-boosted survival / discrete-time hazard with features `{edge0_bps, net0_bps, age_sell_us, age_buy_us, spread_sell_bps, spread_buy_bps, vol_1s_bps, venue_pair}`. Keep KM as the calibration and explanation fallback.

## 4) Innovation candidates

Scores: 1 = weak, 5 = strong.

| Candidate | Description | Impact | Novelty | Feasibility by Dec | Measurability | Demoability | Critical read |
|---|---|---:|---:|---:|---:|---:|---|
| Covariate-conditioned discrete hazard GBM | Predict per-bin survival with nonlinear effects from edge, quote ages, spreads, volatility, and venue pair. | 5 | 3 | 4 | 5 | 4 | Strong but not novel generally; novelty is applying it to cross-asset opportunity decay and C8 EV. |
| Infant-mortality fake-cross detector | Explicitly model early hazard shape; opportunities with very high 0-Δ hazard are delayed/confirmed, while low early hazard acts now. | 5 | 4 | 4 | 5 | 5 | This is the most aligned with the spike; survival/hazard is standard, but the fake-cross interpretation is demo-friendly. |
| Survival calibration dashboard | Reliability plot for `S(L|x)`, D-calibration-style histogram, and pair/edge KM overlays. | 4 | 2 | 5 | 5 | 5 | Not novel in literature, but likely judges trust it because it proves probabilities are not arbitrary scores. |
| Conformal lower-bound survival | Wrap `S(t|x)` with conservative prediction sets/lower survival bounds for risk-sensitive act/skip. | 3 | 4 | 2 | 3 | 3 | Potentially innovative, but source details are UNVERIFIED and implementation may exceed Round-1 time. |
| Deep LOB survival encoder | Encode short LOB/state history with causal convolutions/Transformer before survival head. | 4 | 3 | 2 | 4 | 4 | Exists for fill probabilities; likely too heavy unless baseline is already stable. |

Best C7 candidate: **infant-mortality fake-cross detector** implemented through a discrete hazard GBM, because it directly explains when waiting is rational.

## 5) Isolated scalar metric

**Integrated Brier score (IBS) on held-out days, lower is better.**

Implementation rule:

- Train on earlier days; freeze model and binning.
- Score each held-out opportunity episode on a fixed latency/time grid using censoring-aware Brier scoring.
- Report IBS overall and by venue pair; also report C-index and calibration of `S(L)` at the operating latency.

Operational tie-breaker: if two models have similar IBS, choose the one with lower calibration error at the C8 latency `L`, because C8 consumes `S(L|x)` directly.

## 6) Failure modes and tests

- **Survivorship/label bias:** episodes still open at file end can look long-lived. Test by truncating training windows artificially and confirming censoring-aware estimates remain stable.
- **Clock skew and wrong duration origin:** exchange-time and receive-time duration labels can diverge. Test with synthetic two-venue streams where the true opportunity lifetime is known and venue timestamps are offset.
- **Look-ahead leakage:** features such as `edge_max_bps` can accidentally use future episode information. Test by enforcing feature timestamps `<= t_start_us` for online models and running a leakage audit.
- **Heavy ties at millisecond bins:** many events may share rounded durations. Test Cox/GBM stability under microsecond vs millisecond bucketing and tie handling.
- **Regime shift:** volatility/news periods can change hazards. Test rolling-day backtests and report IBS by volatility tercile.
- **Overfitting thresholds/bins:** choosing time bins on the test day inflates results. Test with predeclared bins and a train/validation/test split.
- **Dependent overlapping episodes:** simultaneous venue-pair opportunities are not independent. Test clustered bootstrap by time block/instrument, not IID rows.
- **Class imbalance in long survivors:** few opportunities survive to large `t`. Test confidence intervals or minimum-at-risk thresholds before reporting tail survival.
