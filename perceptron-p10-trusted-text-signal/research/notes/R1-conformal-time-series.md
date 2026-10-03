# R1 — Conformal Prediction for Time Series / Under Shift, Conditional Coverage, MAPIE Specifics, Calibration Tests

Status: IN PROGRESS (incremental write-up; skeleton first, append after every 2-3 sources)
Scope: Techfest 2026 Perceptron P10 — "Trusting a Signal Extracted from Messy, Manipulated Text"
Accessed date for all sources: 2026-10-04 (IST) unless noted otherwise.

---

## 1. TL;DR (decision-relevant bullets)

_(to be filled in last, after all findings gathered)_

---

## 2. Findings by sub-topic

### 2.1 Online / time-series conformal prediction (ACI, AgACI, PID, EnbPI, SPCI, decaying step sizes, gradient equilibrium, 2025-2026 newcomers)

**Gibbs & Candès (2021), "Adaptive Conformal Inference Under Distribution Shift" — ACI.** arXiv:2106.00170 (submitted 2021/06/01; v3 is current version per `citation_date`/`og:url` tags). Authors: Isaac Gibbs, Emmanuel Candès. Verified via raw HTML fetch of the abs page (citation meta tags + og:description), accessed 2026-10-04.
- **Guarantee**: NOT exchangeability-dependent; "provably achieves the desired coverage frequency over **long-time intervals** irrespective of the true data generating process." This is a **long-run average (marginal-in-time) coverage** guarantee, not pointwise/conditional coverage — ACI models the miscoverage-rate target as a single scalar parameter α_t that is continuously re-estimated online (online gradient-descent-like update on the nonconformity quantile level).
- **Assumptions**: none on exchangeability or stationarity; works as a generic wrapper around any black-box point-predictor or quantile estimator. Tested on two real-world datasets reported as robust to visible/significant distribution shift (dataset identity not yet confirmed — need full-text or later section of abs page to name them).
- Quote (og:description, exact): "We develop methods for forming prediction sets in an online setting where the data generating distribution is allowed to vary over time in an unknown fashion. Our framework builds on ideas from conformal inference to provide a general wrapper that can be combined with any black box method... While previous conformal inference methods rely on the assumption that the data points are exchangeable, our adaptive approach provably achieves the desired coverage frequency over long-time intervals irrespective of the true data generating process."

_(remaining papers in this subtopic — AgACI, PID, EnbPI, SPCI, decaying-step-size, gradient equilibrium, 2025/2026 newcomers — pending; titles already confirmed via arXiv abs-page title fetch, full metadata fetch in progress)_

**Zaffran, Féron, Goude, Josse, Dieuleveut (2022), "Adaptive Conformal Predictions for Time Series" — AgACI.** arXiv:2202.07282v1. Verified via raw HTML og:description fetch, accessed 2026-10-04. (ICML 2022, per main agent's framing — not independently re-verified against ICML proceedings page in this session, flagged.)
- **Guarantee**: Builds on ACI (Gibbs & Candès 2021) — explicitly says CP "requires exchangeable data, excluding time series," and argues ACI (designed for distribution-shift) is in fact "a good procedure for time series with general dependency." AgACI itself is a **parameter-free, learning-rate-free** method that adaptively aggregates multiple ACI instances (different learning rates) via **online expert aggregation** — so the coverage guarantee inherited is still the ACI-style long-run/running average coverage, now without needing to hand-pick ACI's step size γ.
- **Assumptions**: theoretically analyzes impact of learning rate on ACI's efficiency "in the exchangeable and auto-regressic case" (i.e., both exchangeable and AR-dependent regimes considered).
- **Financial relevance**: real case study is **electricity price day-ahead forecasting** (not equities/FX, but a volatile, regime-shifting financial-adjacent time series). Quote: "We conduct a real case study: electricity price forecasting. The proposed aggregation algorithm provides efficient prediction intervals for day-ahead forecasting." Code/data stated as publicly released ("All the code and data to reproduce the experiments is made available").

**Angelopoulos, Candès, Tibshirani (2023), "Conformal PID Control for Time Series Prediction."** arXiv:2307.16895v1. Verified via raw HTML og:description fetch, accessed 2026-10-04. (NeurIPS 2023 per main agent's framing, not independently re-verified against NeurIPS proceedings in this session.)
- **Guarantee**: Frames online conformal as a **control-theory problem** — tracks/adapts conformal quantile scores using PID-controller machinery; "simplifies and strengthens existing analyses in online conformal prediction" (i.e., unifies/generalizes ACI-style long-run coverage results under one control-theoretic lens, explicitly handling "systematic errors due to seasonality, trends, and general distribution shifts").
- **Financial relevance — DIRECT HIT**: Quote (og:description, exact): "We also run experiments on predicting electricity demand, **market returns**, and temperature using autoregressive, Theta, Prophet, and Transformer models." This is the paper's own stated experiment roster — market-returns prediction-interval coverage is explicitly evaluated, but the exact numbers (coverage %, interval width) are NOT yet extracted from this abs-page fetch — would require the PDF/HTML full text (out of scope per "never fetch PDFs" instruction) or the paper's companion repo (`aangelopoulos/conformal-time-series`, confirmed to exist above, frozen at 2023-11-30). Flagged for a non-PDF HTML full-text route if time permits (e.g. arxiv's /html/ mirror).
- Also: 4-week-ahead CDC COVID-19 death-count forecasting experiment reported to "show an improvement in coverage over the ensemble forecaster used in official CDC communications" — a concrete comparative claim, numbers not yet extracted.
- Code: "We provide an extendable codebase for testing our methods" — this is the `aangelopoulos/conformal-time-series` GitHub repo already catalogued in §2.3 (145 stars, MIT, frozen since 2023-11-30).

**Xu & Xie (2021), "Conformal prediction for time series" — EnbPI.** arXiv:2010.09107v15 (note: v15 — heavily revised over time, originally submitted 2020). Verified via raw HTML og:description fetch, accessed 2026-10-04.
- **Guarantee**: Establishes "explicit bounds on **conditional and marginal** coverage gaps of estimated prediction intervals, which asymptotically converge to zero under additional assumptions" — i.e., EnbPI gives asymptotic (not finite-sample exact) conditional coverage under extra assumptions, plus marginal coverage bounds. Also bounds the size of set differences between oracle and estimated intervals.
- **Assumptions**: Explicitly does **NOT require data exchangeability** — designed to wrap around ensemble predictors (bootstrap ensembles) without retraining, "avoids data-splitting," "computationally efficient... scalable to sequentially producing prediction intervals."
- No financial-data numbers found in abstract; would need full text.

**Xu & Xie (2023), "Sequential Predictive Conformal Inference for Time Series" — SPCI.** arXiv:2212.03463v3. Verified via raw HTML og:description fetch, accessed 2026-10-04.
- **Guarantee**: "establish asymptotic valid **conditional coverage** upon extending consistency analyses in quantile regression" — i.e., SPCI targets asymptotic conditional coverage (stronger target than ACI/EnbPI's marginal/long-run framing), by adaptively re-estimating the conditional quantile of non-conformity scores (residuals) exploiting temporal dependence.
- **Assumptions**: explicitly built for non-exchangeable sequential/time-series data; casts the interval-construction problem as "predicting the quantile of a future residual, given a user-specified point prediction algorithm."
- **Reported result**: "a significant reduction in interval width of SPCI compared to other existing methods under the desired empirical coverage" (simulation + real-data experiments) — comparative claim, specific numbers/datasets not yet extracted from abstract (would need full text).

**Angelopoulos, Barber, Bates (2024), "Online conformal prediction with decaying step sizes."** arXiv:2402.01139v2. Verified via raw HTML og:description fetch, accessed 2026-10-04.
- **Guarantee**: "possesses a **retrospective guarantee of coverage for arbitrary sequences**" (same style as prior ACI/PID methods — distribution-free, sequence-adversarial-robust), BUT additionally "unlike previous methods, we can simultaneously estimate a population quantile when it exists." Key practical win: "when the distribution is stable, the coverage is close to the desired level for **every time point, not just on average over the observed sequence**" — i.e., this addresses a specific known weakness of constant-step-size ACI (good long-run average but can have poor/oscillating coverage locally) by decaying the step size, recovering near-pointwise coverage when the underlying distribution is in fact stationary, while keeping the adversarial-sequence retrospective guarantee.

**Angelopoulos, Jordan, Tibshirani (2025), "Gradient Equilibrium in Online Learning: Theory and Applications."** arXiv:2501.08330v3 (per og:url). Verified via raw HTML og:description fetch, accessed 2026-10-04. (Main-text claim of "JMLR v26, paper 25-0356" surfaced via web_search, NOT independently opened/verified in this session — flagged as unverified sub-claim.)
- **Core idea**: defines "gradient equilibrium" — a sequence of iterates has it if the **average of gradients of losses along the sequence converges to zero**; explicitly NOT implied by, nor implying, sublinear regret (a conceptually distinct target from standard online-learning regret bounds, and by extension distinct from most ACI-style "coverage as a regret proxy" framings).
- **Key mechanism difference from ACI/PID/decaying-step-size lineage**: gradient equilibrium is achievable with **constant step sizes** via standard GD/mirror descent — i.e., unlike the Angelopoulos-Barber-Bates (2024) decaying-step-size result above, this does NOT need decay to get a meaningful per-time-point-style property.
- **Applications stated**: (1) a debiasing scheme for black-box predictions under arbitrary distribution shift via simple post-hoc online descent updates; (2) calibrating predicted quantiles under distribution shift (directly conformal-relevant — this is effectively a quantile-tracking recalibration method, same family problem as ACI); (3) unbiased Elo scores for pairwise preference prediction (not conformal/finance-relevant, noted for completeness only).
- Code repo referenced by web_search (NOT opened in this session): `github.com/aangelopoulos/gradient-equilibrium` — flagged UNVERIFIED pending direct check.

**[2025/2026 newcomer] "Online Conformal Prediction via Universal Portfolio Algorithms."** arXiv:2602.03168v1 (submission numbering implies Feb 2026). Verified via raw HTML og:description fetch, accessed 2026-10-04. Authors not yet extracted from this fetch (truncated before author meta tags) — flagged for follow-up.
- **Guarantee**: targets "long-run (1-α) coverage for arbitrary (possibly adversarial) data streams" (same OCP family as ACI/PID/decaying-step/gradient-equilibrium) but develops a **general regret-to-coverage theory** for interval-valued OCP based on the (1-α)-pinball loss; identifies "linearized regret" as the key sufficient condition (controlling it implies coverage bounds for ANY online algorithm, via a black-box reduction using the Fenchel conjugate of an upper bound on linearized regret).
- **Method — DIRECTLY FINANCE-FLAVORED**: proposes **UP-OCP**, a parameter-free OCP method obtained by **reducing online conformal prediction to a two-asset portfolio-selection problem** and then applying universal portfolio algorithms (a classical online-finance/sequential-investment tool, e.g. Cover's Universal Portfolio). This is a genuine conceptual bridge between quantitative-finance online algorithms and conformal prediction — likely to resonate well with Optiver-quant judges as a "self-aware" connection between the two domains the hackathon is fusing.
- **Reported result**: "strong finite-time bounds on the miscoverage of UP-OCP, even for polynomially growing predictions" and "Extensive experiments support that UP-OCP delivers consistently better size/coverage trade-offs than prior online conformal baselines" — comparative claim; specific benchmark datasets/numbers not yet extracted (would need full text; not opened further due to PDF restriction / time budget).
- **Caution**: arXiv ID `2602.03168` numerically implies a Feb-2026 submission, i.e., genuinely very new/recent (after the session's "today" of 2026-10-04 this is only ~8 months old) — treat as a bleeding-edge, not-yet-widely-vetted result; no citation count or community validation available via the tools used in this session.




### 2.2 Conditional coverage (Gibbs/Cherian/Candès, Mondrian, multivalid — Bastani et al.)

_(pending)_

### 2.3 MAPIE specifics (version, release date, v1 class names, gaps) + sibling libraries (crepes, TorchCP, puncc, conformal-time-series)

**MAPIE current state** (GitHub API via `gh api repos/scikit-learn-contrib/MAPIE`, accessed 2026-10-04):
- Latest release: **v1.5.0**, published 2026-08-05 (tag `v1.5.0`, target `master`). Repo: 1,600 stars, 158 forks, 28 open issues, BSD-3-Clause license, last push 2026-09-30 (actively maintained).
- v1.5.0 release notes (verbatim from GitHub Releases API) add: **Conditional conformal prediction** — `ConditionalSplitConformalRegressor` and `ConditionalSplitConformalClassifier` "following Gibbs et al. (2023)" (finite-dimensional classes only, requires `torch`); `CrossConformalizedQuantileRegressor` (cross-CQR); `ConditionalExpectedRiskController` (Automatically Adaptive Conformal Risk Control, PyTorch-based); `StdConformityScore` for estimators returning predicted std-dev (enabling J+GP-style methods); experimental multivariate standardized residual conformity scores; conditional-coverage metrics via `covmetrics` integration. Python 3.9 support dropped (3.10+ required).
- v1.4.1 (2026-06-08): adds `conformity_scores` attribute on any MAPIE object; `fit_conformalize`/`reset()` to refit cross-conformal & jackknife-after-bootstrap without re-instantiating; notes that "Kim et al. (2020) and Zaffran et al. (2022) example datasets now load from bundled backups" — confirms MAPIE ships worked examples directly citing Zaffran et al. 2022 (AgACI paper) for time-series conformal.
- v1.4.0 (2026-04-30): adds FWER control methods, **exchangeability testing (permutation tests + online martingale tests)** with a high-level API, risk monitoring, experimental module.
- v1.3.0 (2026-02-03): adds Venn-Abers calibration, risk control for multi-label & semantic segmentation, LLM risk control with abstention; "Fix bugs in CRC, RCPS (lambda computation), and **ACI updates for time series**" (confirms ACI is implemented pre-v1.3 and had bugfixes).
- **Class-name naming scheme observed from release notes** (v1 API, confirmed from the release bodies above — NOT yet cross-checked against full docs/source): `CrossConformalRegressor`, `JackknifeAfterBootstrapRegressor` (both with `aggregate_point_predictions`, formerly `aggregate_predictions`/`ensemble`), `BinaryClassificationController` (risk control), `VennAbersCalibrator`, `MultiLabelClassificationController`, `SemanticSegmentationController`, `ConditionalSplitConformalRegressor`/`Classifier`, `CrossConformalizedQuantileRegressor`, `ConditionalExpectedRiskController`. Time-series-specific class names (e.g., for EnbPI/ACI) not yet directly confirmed by source inspection — flagged for follow-up (see Leads).
- **Gap evidence**: No release note (v1.2.1 through v1.5.0) mentions "PID" anywhere — i.e., **conformal PID control (Angelopoulos/Candès/Tibshirani) does not appear to be implemented in MAPIE** as of v1.5.0, consistent with it living in the separate `aangelopoulos/conformal-time-series` repo. This is an absence-of-evidence inference from the release changelogs, not a confirmed statement from MAPIE docs — flagged for a direct docs/source check.
- Source: GitHub Releases API JSON, `https://api.github.com/repos/scikit-learn-contrib/MAPIE/releases?per_page=5`, and repo metadata JSON, accessed via `gh api` 2026-10-04.

**Sibling conformal-prediction libraries** (GitHub API metadata, accessed 2026-10-04):
| Library | Description | Stars | License | Last push |
|---|---|---|---|---|
| `henrikbostrom/crepes` | "Python package for conformal prediction" | 583 | BSD-3-Clause | 2026-07-08 |
| `ml-stat-Sustech/TorchCP` | "A Python toolbox for conformal prediction research on deep learning models, using PyTorch" | 479 | LGPL-3.0 | 2026-08-05 |
| `deel-ai/puncc` | "Puncc is a python library for predictive uncertainty quantification using conformal prediction" | 410 | **None detected via API** (needs manual check — deel-ai puncc is actually MIT per repo, API returned null, flagged) | 2026-10-01 |
| `aangelopoulos/conformal-time-series` | "Conformal prediction for time-series applications" (companion code to the PID-control paper) | 145 | MIT | 2023-11-30 (not updated since — static/archival relative to the others) |

Note: `aangelopoulos/conformal-time-series` has had **no commits since 2023-11-30**, i.e. it is a frozen paper-companion repo, not an actively maintained library — important caveat for anyone considering depending on it directly rather than reimplementing the core quantile-tracking update.



### 2.4 Calibration tests for interval forecasts in finance (Kupiec, Christoffersen, Engle-Manganelli, Winkler/pinball)

_(pending)_

### 2.5 Evidence of conformal under-coverage on financial returns in high-volatility regimes

_(pending)_

---

## 3. Implications / pitfalls

_(pending)_

---

## 4. Source table

| URL | Title | Date | Maturity | Claim used |
|---|---|---|---|---|

---

## 5. Leads not verified (UNVERIFIED)

_(pending)_
