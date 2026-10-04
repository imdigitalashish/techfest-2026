# Round 1 abstract — Perceptron 2026, Problem 10: Trusting a Signal Extracted from Messy, Manipulated Text

_Draft v0, 4 Oct 2026. Preliminary numbers come from our committed walking skeleton (`eval/results/baseline_v0.json`; reproduce with `eval/run_baselines.py`). Team section to be completed by the team._

**Problem & theme.** Theme 6 (AI You Can Actually Trust), Problem 10. Desks and apps act on sentiment from news and social posts, and one hacked tweet once moved the Dow 140 points. We want a text-plus-price signal whose error bar stays honest when some of the text is fake.

**Understanding of the challenge.** Three difficulties interact. (1) The text signal is weak: next-day direction is barely predictable from sentiment, and text may say more about *how much* a price moves than *which way*. (2) Daily returns are not exchangeable: volatility clusters and regimes shift, so a split-conformal interval that is valid "on average" under-covers exactly in stressed markets. (3) Manipulation acts on the test input: an attacker who injects posts moves the features after calibration, which no standard conformal guarantee covers. The bound can then be narrow, shifted and confidently wrong. "Meaningful" must therefore be measured, not asserted: valid on held-out time, valid within regimes, misses not clustered in time, as narrow as possible, and robust to a stated attack budget.

**Proposed approach.** A ten-component pipeline with typed contracts between stages:
1. *Ingest + align:* tweets/news and daily bars; every document is assigned to the trading day whose 16:00 New York close it precedes (look-ahead leakage is a unit-tested metric — 0 of 119,641 documents).
2. *Text scorer:* VADER with a finance lexicon (baseline), then FinBERT (`ProsusAI/finbert`, `yiyanghkust/finbert-tone`). LLM scorers only with a look-ahead test, because LLMs can recall pre-cutoff outcomes.
3. *Trust scorer:* account age, followers, verification, copy-paste clusters, cashtag spam.
4. *Bounded-influence aggregator:* count, mean, 20% trimmed mean, dispersion, trust.
5. *Fusion model:* LightGBM quantile regression (5%, 50%, 95%) on 12 price/volatility features plus the text features.
6. *Conformal layer (MAPIE 1.5):* split conformal, conformalized quantile regression (CQR), and Adaptive Conformal Inference (ACI) for drift.
7. *Spike — CR-ACI, certified manipulation-robust conformal:* if at most k documents of a ticker-day are injected, the clean feature vector lies in a "deletion box" whose per-feature ranges we compute exactly from order statistics. We propagate that box through every tree of each quantile model and widen by the ACI-tuned conformal correction. For every attack within budget k, the interval contains the clean model's interval. So coverage holds per prediction, not just on average, at a measurable width cost.

Data: StockNet (87 US stocks, 119,641 tweets with user metadata, 2014–2016; MIT licence); its StockNet model is a victim of the published tweet-concatenation attack (Xie et al., NAACL 2022). For the finals, FNSPID (KDD 2024; news for S&P 500 firms 1999–2023), so we can test across 2008, 2020 and 2022.

**Minimum Viable mapping.** MV1 "fusion model of text sentiment + time series": the LightGBM quantile fusion model, already running end-to-end. MV2 "off-the-shelf conformal bounds": MAPIE `SplitConformalRegressor` and `ConformalizedQuantileRegressor` around it, also running.

**Stretch ambitions.** (1) Adversarial scenario: a pump attack (k bullish bot posts per ticker-day) and an oracle attacker (worst of 12 injection variants within k = 3). Then a noisy-label scenario: flipped sentiment labels when fine-tuning FinBERT. (2) Calibration, not just presence: Kupiec unconditional-coverage and Christoffersen independence tests, coverage by volatility regime and tweet volume, and worst-day coverage. Both stretch goals use the same harness, so robustness is reported *as coverage*.

**Novelty.** Robust conformal methods (RSCP, VRCP, ICML 2024, NeurIPS 2025) certify bounded perturbations of a single input (ℓp balls, smoothing noise, sparse edits) or poisoned calibration data, mostly for classification. In our searches we found no method that certifies coverage against a budget of injected *documents* feeding a text + time-series regressor. We also report a price-of-robustness curve (width versus k): what the text channel is worth against the attack surface it opens.

**Evaluation plan.** Strict time order: train 2014, calibrate H1-2015, test Jul 2015–Mar 2016 (16,443 ticker-days, including the Aug-2015 and Jan-2016 sell-offs). Baselines: price-only, text-only and fusion models, each with split CP, CQR and CQR+ACI. Metrics: coverage at 90%, mean width, Winkler score, Kupiec/Christoffersen p-values, coverage by regime, and clean vs attacked coverage for k = 0…5. Preliminary results:
- Split CP is not meaningful here. The fusion model covers 81.3% (Kupiec p < 0.001) and only 76.5% in the high-volatility tercile.
- CQR reaches 86.3% (width 4.71 percentage points of return). ACI restores 89.4% (width 5.22).
- Text adds almost nothing to point accuracy (pinball loss 0.3518 fusion vs 0.3513 price-only), consistent with the literature.
- Under the oracle attack (k = 3), plain CQR falls from 86.3% to 84.4% coverage. The certified interval keeps 88.0%, at 4.5% extra width.
- Combined with ACI (CR-ACI), coverage is 89.5% clean and 89.7% under a pump attack, at 0.3% more width than plain ACI.

**Feasibility and risks.** Everything above runs on one Apple-silicon laptop. Risks:
- The threat model covers injection only; editing documents is next, and true-but-misleading news is out of scope.
- Box relaxations may loosen as features grow; a ratchet loop minimises certified width under a frozen evaluator.
- Weak text signal; mitigated by stronger scorers and FNSPID news.

Team: Ashish (ML systems; large-scale and frontier-model engineering) plus two teammates (roles: quantitative finance; NLP) — names and skills TBD. Milestones:

| Weeks | Milestone |
|---|---|
| 5–18 Oct | FinBERT scorers, FNSPID subset |
| 19 Oct–1 Nov | Edit-budget certificate, regime-conditional conformal, abstract |
| 2–15 Nov | Ratchet loops, noisy-label study, demo dashboard |
| 19–25 Nov | Exams; automated runs only |
| 1 Dec | Midway report |
| 15–18 Dec | Finals: live demo with an attack toggle and a k slider |
