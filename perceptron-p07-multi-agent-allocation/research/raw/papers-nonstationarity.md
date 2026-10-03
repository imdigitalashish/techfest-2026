# Non-Stationarity: Detect → Forecast → Plan — Research Notes

**Scope:** Perceptron P07 (multi-agent resource reallocation under shifting demand).
**Access date for all sources below: 2026-10-04.** Status: IN PROGRESS (being written incrementally).

---

## TL;DR

_(to be filled in after sources are gathered)_

---

## Sources table

| # | Title | Year | Venue | Link | Maturity (opened/skimmed/unverified) |
|---|-------|------|-------|------|----------------------------------------|
| 1 | Bayesian Online Changepoint Detection (Adams & MacKay) | 2007 | arXiv preprint | arxiv.org/abs/0710.3742 | opened (abstract via og:description; full text not yet read) |
| 2 | Adaptive Conformal Inference Under Distribution Shift (Gibbs & Candès) | 2021 | NeurIPS 2021 / arXiv 2106.00170 | arxiv.org/abs/2106.00170 | opened (abstract) |
| 3 | Conformal Inference for Online Prediction with Arbitrary Distribution Shifts, i.e. "DtACI" (Gibbs & Candès) | 2022 | arXiv 2208.08401 | arxiv.org/abs/2208.08401 | opened (abstract) |
| 4 | Conformal PID Control for Time Series Prediction (Angelopoulos, Candès, Tibshirani, et al.) | 2023 | NeurIPS 2023 / arXiv 2307.16895 | arxiv.org/abs/2307.16895 | opened (abstract) |
| 5 | Conformal Decision Theory: Safe Autonomous Decisions from Imperfect Predictions (Lekeufack, Angelopoulos, Bajcsy, et al.) | 2023/2024 | ICRA 2024 / arXiv 2310.05921 | arxiv.org/abs/2310.05921 | opened (abstract) |
| 6 | Robust and Scalable Bayesian Online Changepoint Detection (Altamirano, Briol, Knoblauch) | 2023 | ICML 2023 (PMLR 202:642–663) / arXiv 2302.04759 | arxiv.org/abs/2302.04759 | opened (abstract); code at github.com/maltamiranomontero/DSM-bocd (found via web_search, not yet opened) |

---

## Notes per source

### 1. Adams & MacKay 2007 — Bayesian Online Changepoint Detection (BOCPD)
- **URL:** https://arxiv.org/abs/0710.3742 (accessed 2026-10-04, via raw HTML meta tag — arxiv.org's markdown render is template-only / JS-gated, had to use `raw=true` to recover `og:description`)
- **Maturity:** Abstract opened and read verbatim. Full PDF/body not yet fetched this session (network constraints) — algorithmic details below are from the abstract only, flagged accordingly.
- **Key facts (exact wording from abstract):**
  1. "Changepoints are abrupt variations in the generative parameters of a data sequence."
  2. "we examine the case where the model parameters before and after the changepoint are independent and we derive an online algorithm for exact inference of the most recent changepoint."
  3. "We compute the probability distribution of the length of the current ``run,'' or time since the last changepoint, using a simple message-passing algorithm... highly modular so that the algorithm may be applied to a variety of types of data."
- **Inference (not yet verified against full text — standard knowledge of BOCPD, to confirm when PDF is read):** the message-passing recursion is the forward algorithm over run-length $r_t$, requires a conjugate exponential-family predictive distribution (Gamma-Poisson is the natural fit for Poisson zone-demand counts) and a hazard function $H(r)$ (constant hazard = geometric changepoint prior). This directly motivates our Poisson-count use case since Gamma is conjugate to Poisson.

### 2. Gibbs & Candès 2021 — Adaptive Conformal Inference (ACI)
- **URL:** https://arxiv.org/abs/2106.00170 (accessed 2026-10-04, raw HTML og:description)
- **Maturity:** Abstract opened and read verbatim; NeurIPS 2021 (per user prompt — not independently re-verified on this fetch, venue taken from prior knowledge/prompt).
- **Key facts (exact wording from abstract):**
  1. "We develop methods for forming prediction sets in an online setting where the data generating distribution is allowed to vary over time in an unknown fashion."
  2. "While previous conformal inference methods rely on the assumption that the data points are exchangeable, our adaptive approach provably achieves the desired coverage frequency over long-time intervals irrespective of the true data generating process."
  3. "We accomplish this by modelling the distribution shift as a learning problem in a single parameter whose optimal value is varying over time and must be continuously re-estimated." Tested on "two real world datasets" with "visible and significant distribution shifts."
- **Relevance:** This is the base ACI online gradient-descent update on the miscoverage-rate parameter $\alpha_t$ — exactly the "calibrated intervals under drift" layer our hypothesis needs, but note it needs a *known/fixed* step size (motivating DtACI next).

### 3. Gibbs & Candès 2022 — DtACI ("Conformal Inference for Online Prediction with Arbitrary Distribution Shifts")
- **URL:** https://arxiv.org/abs/2208.08401 (accessed 2026-10-04, raw HTML og:description)
- **Maturity:** Abstract opened and read verbatim.
- **Key facts (exact wording from abstract):**
  1. "Previous approaches to this problem suffer from over-weighting historical data and thus may fail to quickly react to the underlying dynamics."
  2. "we develop a novel procedure with provably small regret over all local time intervals of a given width" — by "modifying the adaptive conformal inference (ACI) algorithm of Gibbs and Candès (2021) to contain an additional step in which the step-size parameter of ACI's gradient descent update is tuned over time."
  3. "unlike ACI, which requires knowledge of the rate of change of the data-generating mechanism, our new procedure is adaptive to both the size and type of the distribution shift." Tested on "predicting stock market volatility and COVID-19 case counts" (i.e., **count data**, directly relevant to Poisson zone-demand).
- **Relevance:** DtACI runs an ensemble of ACI instances at different step sizes (candidate $\gamma$'s) and mixes them online (expert-aggregation style) — removes the need to hand-tune ACI's single step size, important since our drift magnitude is unknown a priori. Mechanism detail (multiplicative-weights mixing of experts) not yet confirmed from full text — INFERRED from title/abstract + general knowledge of the paper, to verify against body text if time allows.

### 4. Angelopoulos, Candès, Tibshirani et al. 2023 — Conformal PID Control for Time Series Prediction
- **URL:** https://arxiv.org/abs/2307.16895 (accessed 2026-10-04, raw HTML og:description). NeurIPS 2023 (per user prompt).
- **Maturity:** Abstract opened and read verbatim.
- **Key facts (exact wording from abstract):**
  1. "The algorithms we present build upon ideas from conformal prediction and control theory, are able to prospectively model conformal scores in an online setting, and adapt to the presence of systematic errors due to seasonality, trends, and general distribution shifts."
  2. "Our theory both simplifies and strengthens existing analyses in online conformal prediction" (i.e., positions itself as a generalization/simplification of ACI/DtACI — P term ≈ ACI's integral-style error-feedback, I term = integral of past coverage error, D/"scorecaster" term = learned model of the score sequence itself).
  3. "Experiments on 4-week-ahead forecasting of statewide COVID-19 **death counts**" (count data, directly analogous to Poisson zone-demand) "show an improvement in coverage over the ensemble forecaster used in official CDC communications." Also tested on electricity demand, market returns, temperature. "We provide an **extendable codebase**" → confirmed code availability.
- **Relevance:** This is likely the strongest off-the-shelf calibration layer for our pipeline: the "P" (proportional, ≈ACI feedback), "I" (integral, corrects long-run bias), "D" (a learned "scorecaster" that forecasts the conformal score itself, e.g. its own quantile/trend) decomposition is a natural match for "forecaster with calibrated intervals" in our hypothesis — the scorecaster piece literally **is** a forecaster over the nonconformity score sequence. Need to verify the exact coverage-guarantee statement (regret bound form) from body text — not yet done.

### 5. Lekeufack, Angelopoulos, Bajcsy, et al. 2023/2024 — Conformal Decision Theory
- **URL:** https://arxiv.org/abs/2310.05921 (accessed 2026-10-04, raw HTML og:description). ICRA 2024 (per user prompt).
- **Maturity:** Abstract opened and read verbatim.
- **Key facts (exact wording from abstract):**
  1. "a framework for producing safe autonomous decisions despite imperfect machine learning predictions... from robot planning algorithms that rely on pedestrian predictions, to calibrating autonomous manufacturing to exhibit high throughput and low error, to the choice of trusting a nominal policy versus switching to a safe backup policy at run-time."
  2. "The decisions produced by our algorithms are safe in the sense that they come with provable statistical guarantees of having low risk without any assumptions on the world model whatsoever; the observations need not be I.I.D. and can even be adversarial."
  3. "The theory extends results from conformal prediction to calibrate decisions directly, **without requiring the construction of prediction sets**." Experiments: "robot motion planning around humans, automated stock trading, and robot manufacturing."
- **Relevance:** This is architecturally important — it suggests we may not need to build explicit prediction-interval sets and then separately feed them into the planner; instead the *allocation decision itself* (e.g., how many units to commit to zone $i$) can be the conformalized object, directly calibrated to a risk target (e.g., P(unmet demand) ≤ α). This could replace or complement the "forecaster with calibrated intervals → planner" hand-off in our hypothesis with a tighter, decision-calibrated loop. Non-i.i.d./adversarial-robustness claim is notable for the "abrupt shock" stretch goal.

### 6. Altamirano, Briol, Knoblauch 2023 — Robust and Scalable Bayesian Online Changepoint Detection
- **URL:** https://arxiv.org/abs/2302.04759 (accessed 2026-10-04, raw HTML og:description). ICML 2023, PMLR 202:642–663 (confirmed via web_search result, not independently cross-checked against the PMLR page this session).
- **Maturity:** Abstract opened and read verbatim. Code repo located (github.com/maltamiranomontero/DSM-bocd) via `web_search` but **not opened this session** — flag as unverified-but-located.
- **Key facts (exact wording from abstract):**
  1. "This paper proposes an online, provably robust, and scalable Bayesian approach for changepoint detection."
  2. "it provides provable robustness by leveraging the generalised Bayesian perspective, and also addresses the scalability issues of previous attempts."
  3. "the proposed generalised Bayesian formalism leads to conjugate posteriors whose parameters are available in closed form by leveraging diffusion score matching. The resulting algorithm is exact, can be updated through simple algebra, and is **more than 10 times faster** than its closest competitor."
- **Relevance:** Direct successor to Adams & MacKay (2007) that (a) fixes BOCPD's known brittleness to outliers/model misspecification via generalized-Bayes (Gibbs-measure / β-divergence style loss, standard in "robust Bayes" literature — INFERRED, not confirmed from body text this session) and (b) removes the $O(t)$-per-step cost blowup of naive run-length posteriors via closed-form score-matching updates. This is the strongest 2023 candidate for "2024-2026 BOCPD advances" the prompt asks about — it is the most recent major BOCPD mechanism we found and the most natural fit for a real-time per-zone allocator (per-step cost matters for a rolling-horizon planner that must re-plan frequently).

### 7. Lindemann, Cleaveland, Shim, Pappas 2022/2023 — Safe Planning in Dynamic Environments using Conformal Prediction
- **URL (located via web_search, title/venue/arXiv ID confirmed, not yet independently opened this session — see caveat below):** arxiv.org/abs/2210.10254. Venue: IEEE Robotics and Automation Letters (RA-L), Vol. 8, No. 8, Aug 2023, pp. 5116–5123 — matches user's "Lindemann et al. RA-L 2023" exactly.
- **Maturity:** UNVERIFIED-BY-DIRECT-FETCH this turn (web_search summary only) — will attempt direct arXiv fetch next; treat the mechanism description below as web_search-reported, not self-verified quote.
- **Key facts (as reported by web_search, to be confirmed):**
  1. Framework = MPC that consumes (a) trajectory predictions of the dynamic environment and (b) conformal "prediction regions that quantify the uncertainty of those predictions," making the MPC "provably safe" at a "user-specified probability."
  2. "Compatibility with state-of-the-art trajectory predictors (like RNNs and LSTMs) and a lack of assumptions about the underlying trajectory-generating distribution."
  3. Claimed as "the first results to offer valid safety guarantees" for planning in such dynamic, uncertain environments; validated in CARLA self-driving simulator, pedestrian-filled intersections.
- **Relevance:** This is the closest published analogue to our hypothesized "conformal buffer inside rolling-horizon planner" pattern — but it is for trajectory/collision safety, not resource-count allocation, and (per the summary) uses an *offline-calibrated* conformal region, not an online/adaptive one layered on a change detector. This is a key data point for the KEY QUESTION below.

---

## Implications

_(pending — recommended detector + forecaster + calibration combo for Poisson counts per zone, with equations; novelty assessment)_

---

## UNVERIFIED leads

_(pending)_
