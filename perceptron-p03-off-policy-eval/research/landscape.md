# Landscape — off-policy evaluation (OPE) for "did the policy actually work?"

> Perceptron 2026 · Problem 3. Lead-written on 2026-10-04 in lean mode (all research sub-agents failed on network 408s).
> **Evidence rule:** every paper below was opened through the official arXiv API. The full abstracts as read, with authors, dates and journal refs, are committed in [`sources/arxiv_classics.md`](sources/arxiv_classics.md) and [`sources/arxiv_newest.md`](sources/arxiv_newest.md); regenerate them with `research/tools/arxiv_fetch.py`. Repo facts come from the GitHub REST API ([`sources/github_repos.md`](sources/github_repos.md)). Company facts come from first-party pages opened on 2026-10-04 and are quoted. Venue labels come from the arXiv comment or journal-ref field; where that field is empty, only the year is given. Anything not opened is marked **UNVERIFIED**.

## 1. The problem in one paragraph

A deployed policy π₀ (a recommender, an ad ranker, a quoting rule) generates the logs later used to judge any replacement π₁. Two different questions get confused:
- **(Q1) Off-policy value:** what would π₁ have earned on the same traffic? The standard tools answer this, provided the logs record the behaviour policy's propensities and every action π₁ takes had non-zero probability under π₀ (overlap).
- **(Q2) The question the brief actually asks:** after we switched from π₀ to π₁, did the change cause the observed difference? A before/after number, Ȳ_after − Ȳ_before, mixes the policy's effect with everything else that changed between the periods: seasonality, a different user mix, novelty effects, and the feedback loop by which a policy shapes its own future data (Chaney et al., arXiv:1710.11214; Perdomo et al., *Performative Prediction*, ICML 2020, arXiv:2002.06673).

Our framing: answer Q2 with Q1 tools. Use OPE to build the counterfactual "the old policy, run during the after period", then attribute the naive gap to policy effect versus environment drift.

## 2. Estimators — the established core

| Estimator | Idea | Bias / variance | Needs | Source | obp |
|---|---|---|---|---|---|
| Replay / rejection sampling | Keep only rounds where the logged action matches π₁ (uniform logging) | Unbiased under uniform logging; discards data | uniform random logs | Li, Chu, Langford, Wang 2010, arXiv:1003.5956 | — |
| IPW / IPS | Reweight rewards by π₁/π₀ | Unbiased with true propensities; high variance when weights are large | propensities | (classic; see obp README) | `InverseProbabilityWeighting` |
| SNIPW | IPW normalised by the mean weight | Small bias, lower variance; bounded by the reward range | propensities | obp README → Swaminathan & Joachims NeurIPS 2015 | `SelfNormalizedInverseProbabilityWeighting` |
| DM | Regress reward q̂(x,a), average q̂ under π₁ | Low variance, biased if q̂ is misspecified | reward model | obp README | `DirectMethod` |
| DR | DM plus an IPW correction on the residual | Unbiased if either the propensities or q̂ is correct ("doubly robust") | both | Dudík, Langford, Li, ICML 2011, arXiv:1103.4601 | `DoublyRobust` |
| Switch-DR | IPW where weights are small, DM where they are large | Trades bias for variance with a threshold τ | both | Wang, Agarwal, Dudík, ICML 2017, arXiv:1612.01205 | `SwitchDoublyRobust` |
| DRos | Shrinks the weights optimistically | Minimax-motivated shrinkage | both | Su, Dimakopoulou, Krishnamurthy, Dudík, ICML 2020, arXiv:1907.09623 | `DoublyRobustWithShrinkage` |
| MRDR | Learns DR's reward model for DR itself. The abstract notes prior DR work improved the IS part and said "not much on how to learn the model" | Targets lower DR variance | both | Farajtabar, Chow, Ghavamzadeh 2018, arXiv:1802.03493 | listed in the obp README |
| Sub-Gaussian IPW/DR | Corrected importance weights with sub-Gaussian concentration (mechanism details **UNVERIFIED** tonight; paper not opened) | — | both | NeurIPS 2021 (linked from the obp README) | listed in the obp README |
| MIPS / OffCEM | Weight on action *embeddings* or clusters, not actions | Big variance cut for large action spaces | embeddings | Saito & Joachims, ICML 2022, arXiv:2202.06317; Saito, Ren, Joachims, ICML 2023, arXiv:2305.08062 | MIPS in obp |
| Cascade-DR | DR for rankings under a cascade click model | Ranking-specific | both | Kiyohara et al., WSDM 2022, arXiv:2202.01562 | `Cascade-DR` |
| Logarithmic smoothing | Pessimism: build upper bounds on worst-case performance; the LS estimator "logarithmically smooths large importance weights" | Biased on purpose; tightest bound in its class | propensities | Sakhi, Aouali, Alquier et al., NeurIPS 2024 spotlight, arXiv:2405.14335 | — |
| Baseline corrections (unified) | Additive control variates (baselines, DR) and multiplicative ones (self-normalisation) unified as "an equivalent baseline correction" | Variance reduction | propensities | Gupta, Jeunen, Oosterhuis et al. 2024, arXiv:2405.05736 | — |
| **Δ-OPE** | "The difference between policy values can often be estimated with significantly reduced variance, if said policies have positive covariance" | Less variance on the *difference* | propensities | Jeunen & Ustimenko, RecSys 2024 short paper, arXiv:2405.10024 | — |

The list of estimators obp implements is taken from the obp README (opened via the GitHub API): DM, IPW, SNIPW, DR, Switch, MRDR, DRos, Sub-Gaussian IPW/DR, Cascade-DR, and kernelised IPW/SNIPW/DR.

**Why this matters for us.** The brief's question is a comparison. Jeunen & Ustimenko's Δ-OPE is the most direct prior art for estimating the *difference* (not the two values separately). Jeunen & Gupta, *Additive Control Variates Dominate Self-Normalisation in OPE* (SIGIR 2026, arXiv:2602.14914), argue that the additive baseline beats SNIPS. Both feed our Δ-estimator component.

## 3. Uncertainty — confidence intervals and sequences

| Method | Guarantee | Source |
|---|---|---|
| Wald CI from the influence function | Asymptotic; under-covers when weights are heavy-tailed or the effective sample is small | standard; see Taufiq thesis below |
| Bootstrap (percentile) | Asymptotic; implemented in obp's `estimate_interval` | obp README |
| Empirical likelihood | Estimator and CI posed "as simple convex optimization problems" | Karampatziakis, Langford, Mineiro, NeurIPS 2020, arXiv:1906.03323 |
| Off-policy confidence sequences | **Anytime-valid**: holds at every sample size, so you may peek as logs arrive | Karampatziakis, Mineiro, Ramdas 2021, arXiv:2102.09540 |
| Anytime-valid off-policy inference (betting) | Anytime-valid confidence sequences for contextual bandits, including adaptively collected data | Waudby-Smith, Wu, Ramdas, Karampatziakis, Mineiro 2022, arXiv:2210.10768 |
| Bayesian inference via empirical likelihood | Posterior for the policy value | Ouyang, Gong, Bondell, accepted at JMLR, arXiv:2602.10608 (Feb 2026) |
| Risk-return of OPE (SharpeRatio@k) | Evaluates *estimator selection* by risk and return, not just error | Kiyohara et al., ICLR 2024, arXiv:2311.18207 |
| PERRY | CIs that use auxiliary (for example, generated) data | Mandyam, Meng, Gao et al. 2025, arXiv:2507.20068 |
| Conformal, beyond the horizon | Distribution-free inference for policy evaluation | Gan, Lu, Zhang 2025, arXiv:2510.26026 |

Taufiq's PhD thesis, *Uncertainty Quantification and Causal Considerations for Off-Policy Decision Making* (Feb 2025, arXiv:2502.06011), treats both of our stretch goals (statistical uncertainty and causal considerations) as limitations of existing OPE. It is a useful single map of the area.

## 4. Unobserved confounding — sensitivity analysis

**When confounding enters OPE.** If the logging policy's propensities are logged exactly (randomised exploration, as in OBD), there is no unobserved confounding by construction. It enters when propensities must be *estimated*: deterministic legacy rules, human overrides, observational logs, or a before/after comparison with no logged randomisation. Jeunen & London make this point for recommenders (*Offline Recommender System Evaluation under Unobserved Confounding*, CONSEQUENCES'23 at RecSys, arXiv:2309.04222).

| Approach | Parameter | What it bounds | Source |
|---|---|---|---|
| Confounding-robust policy improvement | An uncertainty set around the nominal propensities (MSM-type, Γ) | Worst-case policy value and regret, which "may not be point-identifiable" under confounding | Kallus & Zhou 2018, arXiv:1805.08593 |
| Marginal sensitivity model + percentile bootstrap for IPW | Γ: "a natural extension of Rosenbaum's sensitivity model" | An interval valid under the MSM, combining sampling and confounding | Zhao, Small, Bhattacharya 2017, arXiv:1711.11286 |
| Sharp bounds via quantile balancing | Γ | Sharp (tightest) MSM bounds | Dorn & Guo, JASA 2022 (per the arXiv comment), arXiv:2102.04543 |
| Efficient and sharp off-policy learning under confounding | Γ-type sensitivity | A semiparametrically efficient estimator of the sharp bound, without unstable minimax | Hess, Frauen, Melnychuk et al. 2025, arXiv:2502.13022 |
| Human–AI teams | MSM | Confounding-robust policy improvement when humans override | Gao & Yin, arXiv:2310.08824 (comment: AAAI 25) |
| OVB for causal ML ("Long story short") | Partial R² of the confounder | Bias bounds for DML targets; benchmarking against observed covariates | Chernozhukov, Cinelli, Newey, Sharma, Syrgkanis, Review of Economics and Statistics 2026, arXiv:2112.13398 |
| Confounded sequential OPE | Various | OPE for sequential decisions | arXiv:2504.01211 (2025); Li, Zhang, Bareinboim, NeurIPS 2025, arXiv:2510.21110 |

**Gap we observed (search scope: the arXiv queries in `sources/arxiv_newest.md`, 2026-10-04).** We did not find a tool that reports, for the **difference** between two policies, an MSM sensitivity bound *jointly* with sampling uncertainty, a **tipping point Γ\*** (the smallest Γ that makes the 95% interval for Δ include 0), *and* a benchmark of Γ\* against observed covariates in the style of Cinelli & Hazlett. This is not proof of absence; deeper citation-trail checks are scheduled.

## 5. Why before/after misleads — mechanisms

| Mechanism | How it corrupts Ȳ_after − Ȳ_before | Does OPE fix it? | Simulator knob |
|---|---|---|---|
| Time trend or seasonality (response drift) | Everyone's reward shifts between the periods | **Yes**: compare π₁ and π₀ within the same period | `drift_response` |
| User-mix (covariate) shift | Different users arrive after the switch | **Yes** within the period; the decomposition separates it | `drift_mix` |
| Feedback loop / performativity | π₁ changes future contexts (Chaney et al. 2017; Perdomo et al. 2020) | **Partly**: single-step OPE values the policy on the current context distribution, not its long-run effect | `feedback` |
| Non-stationarity across periods | The value of a policy itself moves; "future OPE" (Shimizu et al. 2025, arXiv:2506.20417) targets the next period | Partly | `drift_effect` |
| Unobserved confounding (estimated propensities) | Selection on unobservables | **No**: bound it with sensitivity analysis (§4) | `confounding_gamma` |
| Low overlap | Rare actions under π₀ get huge weights | Variance explodes; use DR, Switch or clipping | `epsilon` |

Classic alternatives for before/after, and how OPE differs:
- **Bayesian structural time series (CausalImpact)** builds the counterfactual from control time series (Brodersen et al., *Annals of Applied Statistics* 2015, arXiv:1506.00356). It needs good untreated control series. OPE instead needs logged propensities and overlap.
- **Attributing performance changes to distribution shifts** (Zhang, Singh, Ghassemi et al., ICML 2023, arXiv:2210.10769) uses Shapley attribution for *model* performance. Our decomposition does the same kind of accounting for a *policy's* before/after gap, with the policy term estimated by OPE.

## 6. Newest work, 2025–2026 (newest first; from date-sorted arXiv queries)

- **Recommendation-ranking OPE under ranking-dependent examination** — Okamura & Sugawara, arXiv:2609.35034 (Sep 2026).
- **OTROPE: optimal-transport-robust OPE for LLMs** — Xiang, Zhang, Cai, NeurIPS 2026 (per the comment), arXiv:2609.36264.
- **OPE as decision support for designing adaptive experiments** — Alves et al., arXiv:2609.30273 (Aug 2026): uses data from fixed A/B tests to judge whether adaptive bandit policies would have won.
- **When offline evaluation misleads** — Lee, Loganathan, Dash, arXiv:2608.11560 (Aug 2026, workshop). With delayed conversions, "a batch off-policy estimate, a marginal arm-discrimination test, a confidence interval — can mislead systematically". They propose an ordered diagnostic protocol and validate it "where the truth is known — a public off-policy-evaluation benchmark and a controllable synthetic generator". This is the closest framing to ours.
- **OPE for semantic-ID recommenders** — Betlei, arXiv:2608.28905 (Aug 2026).
- **Cross-domain OPE/OPL** — Natsubori, Ushiku, Saito, arXiv:2607.22012 (Jul 2026).
- **Kernel-weighted importance sampling for contextual bandits** — Spear, Komorowski, Pope, arXiv:2607.15067 (Jul 2026).
- **Accelerating A/B tests with counterfactual estimation** — Jeunen, arXiv:2607.14604 (Jul 2026): variance reduction for online experiments using structure between policies.
- **Logging-policy design for OPE** — Douglas, Persson, Provost, arXiv:2605.15108 (May 2026).
- **Decision support for marketplace policies under incomplete evidence (RTB reserve prices)** — Shekhar & Howard, arXiv:2605.12840 (May 2026): "strong offline performance does not imply that a policy is safe to deploy".
- **Offline contextual bandits with new actions** — Kishimoto, Shimizu, Kawamura, arXiv:2605.18509 (May 2026).
- **From weighting to modeling: a nonparametric OPE estimator** — Zhu, TMLR (3/2026), arXiv:2603.09436.
- **Additive control variates dominate self-normalisation** — Jeunen & Gupta, SIGIR 2026, arXiv:2602.14914.
- **Breaking determinism: stochastic modelling for OPE in ad auctions** — Yeom, Shin, Min, arXiv:2512.03354 (Dec 2025). Deterministic production policies break IPW.
- **GrowthHacker: LLM agents that modify OPE code** — Wu, Herlihy, Mirza et al., arXiv:2511.00802 (Nov 2025). The agent "autonomously and iteratively modifies code, runs OPE, and uses the metrics to guide subsequent optimization", evaluated on OBP and SCOPE-RL. **This is prior art for our auto-research ratchet; we must differentiate** (§8).
- **Offline A/B testing of slate recommenders with LLMs** — Bonin, Heuillet, Durand, arXiv:2511.04541 (Nov 2025).
- **APRIL: LLM annotations for policy evaluation with reliable inference** — Mandyam, Limaye, Engelhardt, arXiv:2511.17818 (Nov 2025).
- **Safely exploring novel actions** — Kiyohara, Narita, Saito, arXiv:2510.07635 (Oct 2025).
- **Optimisation matters more than estimation (large action spaces)** — Aouali & Sakhi, ICML'26 (per the comment), arXiv:2509.03456.
- **Context-action embedding learning for OPE** — Chandak, Liu, Lee et al., arXiv:2509.00648 (Aug 2025).
- **Meta off-policy estimation** — Jeunen, RecSys 2025 (per the comment), arXiv:2508.07914.
- **OPE/OPL for matching markets** — Hayashi, Goda, Saito, RecSys'25, arXiv:2507.13608.
- **Log-sum-exponential estimator** — Behnamnia et al., ICML 2025 spotlight (per the comment), arXiv:2506.06873.
- **Future OPE under non-stationarity (OPFV)** — Shimizu, Kawamura, Muroi et al., arXiv:2506.20417 (Jun 2025): existing methods "assume stationarity or depend on restrictive reward-modeling assumptions, leading to significant bias".
- **DR estimation of counterfactual policy mean embeddings** — Zenati, Bozkurt, Gretton, arXiv:2506.02793 (Jun 2025).
- **DOLCE: lagged versus current effects** — Tamano, arXiv:2505.00961 (May 2025).
- **Clustering context in OPE** — Guzman-Olivares, Schmidt, Golebiowski, AISTATS 2025, arXiv:2502.21304.
- **OPE with missing-not-at-random rewards** — Takahashi, Maru, Shoji, arXiv:2502.08993 (Feb 2025).
- **OPE for payments at Adyen** — Egg, arXiv:2501.10470 (Jan 2025); see §7.

## 7. What companies ship today (first-party sources, opened 2026-10-04)

| Company | What they ship or use | OPE method | Uncertainty? | Confounding sensitivity? | Status | Source |
|---|---|---|---|---|---|---|
| **Microsoft** | Decision Service, then Azure AI Personalizer with "Offline evaluation" (counterfactual evaluation on logged Rank/Reward data) | IPS-family, via Vowpal Wabbit | not stated in the pages read | not stated | **Retired.** Microsoft Learn: "Starting on the 20th of September, 2023 you won't be able to create new Personalizer resources. The Personalizer service is being retired on the 25th of August, 2026." | [Personalizer docs](https://learn.microsoft.com/en-us/azure/ai-services/personalizer/), [offline evaluation](https://learn.microsoft.com/en-us/azure/ai-services/personalizer/concepts-offline-evaluation); Agarwal et al. arXiv:1606.03966 |
| Microsoft / VW community | Vowpal Wabbit (cb, offline evaluation); `VowpalWabbit/estimators`; `coba` benchmarking | IPS, SNIPS and others | estimator intervals (README) | — | VW active (8,727★, last push 2026-09-28); estimators repo quiet (13★, last push 2024-09-03); coba active (53★, 2026-08-30) | `sources/github_repos.md` |
| **Meta** | ReAgent: "counter-factual policy evaluation (CPE)" | DM, IPS, DR-type CPE | — | — | README: "ReAgent is officially archived and no longer maintained"; it points to **Pearl** (3,033★, MIT, last push 2026-08-19) | GitHub README via API |
| **Google / YouTube** | Off-policy correction of a top-K REINFORCE recommender "at Youtube" | Importance weighting for *learning* | — | — | Paper, production | Chen, Beutel, Covington et al., arXiv:1812.02353 |
| **Spotify** | Counterfactual evaluation of slate recommendations with sequential reward interactions | Slate OPE | — | — | Paper | McInerney, Brost, Chandar et al., arXiv:2007.12986 (Spotify affiliation **UNVERIFIED** in the abstract text; confirm from the PDF) |
| **ZOZO** (ZOZOTOWN) | Open Bandit Dataset, "collected on a large-scale fashion e-commerce platform, ZOZOTOWN" (Uniform-Random and Bernoulli-TS logging); Open Bandit Pipeline | Full obp estimator suite; bootstrap intervals | Bootstrap | — | Dataset and library public; obp last push 2024-06-03, latest release 0.5.5 (2022-06-16), 711★ | arXiv:2008.07146; GitHub API |
| **Adyen** (payments) | OPE "to accelerate recommender system development"; billion-scale transactions; "a strong correlation between OPE estimates and online A/B test results"; uses exploration traffic and Spark | Benchmarked several estimators | Variance mitigation discussed | not stated in the abstract | Production (paper, Jan 2025) | arXiv:2501.10470 |
| **Hakuhodo Technologies** | SCOPE-RL (offline RL + OPE, risk-return metrics) | Sequential OPE | Distributional / risk metrics | — | 143★, last push 2024-03-18 | GitHub API |
| Causal-inference OSS used in industry | DoWhy (py-why, 8,335★), EconML (py-why, 4,803★), CausalML (Uber, 6,015★), DoubleML (792★): all pushed within the last 2 weeks | Policy evaluation and treatment effects; DoubleML/EconML-style sensitivity | Yes (CIs) | DML-style sensitivity (to verify module by module) | Active | `sources/github_repos.md` |
| Experimentation vendors (Eppo, Statsig, Optimizely, GrowthBook…) | Bandits and A/B testing | — | — | — | **Not checked tonight** (UNVERIFIED); next step | — |

**Production pattern (from the sources above).** Log propensities → offline counterfactual evaluation (IPS/DR) to screen candidates → online A/B test to confirm → monitor. Adyen and Microsoft describe exactly this loop.

**Gaps we can exploit:**
1. The productized option for teams outside Big Tech (Azure Personalizer's offline evaluation) is now **retired**, and the OSS reference (obp) has not shipped a release since 2022 (GitHub API).
2. None of the first-party product pages we read reports **confounding sensitivity** for a policy comparison.
3. Reported outputs are a *value per policy*, not a *decision about the switch*: no decomposition of the before/after gap that the business actually looked at.

## 8. Innovation room (feeds `architecture/adr/001-spike.md`)

1. **Before/after attribution ("counterfactual P&L attribution").** Decompose Ȳ_after − Ȳ_before = [policy effect, estimated by OPE as Ȳ_after − V̂_after(π₀)] + [environment change, V̂_after(π₀) − Ȳ_before]. Split the environment term further into *user-mix shift* and *response drift* using period-specific reward models, an Oaxaca–Blinder-style split. Validate every term against simulator ground truth. Closest prior art: distribution-shift attribution for model performance (arXiv:2210.10769) and future-OPE (arXiv:2506.20417); neither attributes a *policy's* before/after gap. *Scalar metric:* RMSE of the estimated policy-effect term against the truth across a frozen scenario bank, and sign accuracy.
2. **A robustness certificate for Δ.** Report Δ̂ with (a) an anytime-valid or bootstrap CI, (b) MSM bounds jointly with sampling error (percentile bootstrap, arXiv:1711.11286), (c) the tipping point Γ\*, and (d) a Γ benchmark against observed covariates (leave-one-covariate-out, after Cinelli & Hazlett / arXiv:2112.13398). *Scalar metrics:* coverage ≥ 95% at Γ ≥ Γ_true, and the mean bound width.
3. **A ratchet on the Δ-estimator with a frozen, ground-truth evaluator.** This differs from GrowthHacker (arXiv:2511.00802), which optimises against OPE metrics on OBP/SCOPE-RL: our evaluator scores against *known* counterfactuals across drift, overlap and confounding scenarios, with a held-out scenario bank to catch metric gaming.
4. *Parked:* large action spaces (MIPS/OffCEM) and slates. The OBD "All" campaign has 80 items and 3 positions, so plain IPW/DR suffice for the MVP.

## 9. Datasets and simulators we use

- **Open Bandit Dataset** (ZOZO): "about 26M rows, each one representing a user impression with some feature values, selected items as actions, true propensity scores, and click indicators" (obd/README.md). Logging policies: Uniform-Random and Bernoulli Thompson Sampling. Campaigns: All (items 0–79), Men (0–33), Women (0–45). The repo ships a small version: "10,000 records for each pair of campaign and behavior policy". **Tonight we use only that sample** (`eval/fetch_obd_sample.sh`), because the full data exceeds the lean-mode download cap. Standard protocol (arXiv:2008.07146): estimate the value of the Bernoulli-TS policy from the Random logs and compare it with its on-policy CTR.
- **Verified 2026-10-04 (first-party code):** the standard obp OBD protocol evaluates one *static* Bernoulli-TS action distribution built from the ZOZOTOWN prior.
  - `examples/obd/evaluate_off_policy_estimators.py` sets `is_zozotown_prior=True` and calls a single-round `compute_batch_action_dist`.
  - `obp/policy/contextfree.py` line 18: "configurations to replicate the Bernoulli Thompson Sampling policy used in ZOZOTOWN production".
  - Our pre-registered analysis of 5.96M BTS rows (`eval/results/obd_slice_summary.md`) shows the deployed policy's logged propensities drifting by a median factor of 16 between 6-hour windows. So the protocol evaluates an approximation of the deployed policy, not the policy itself.
  - On the "All" campaign, DR still lands within 0.1% of the on-policy CTR with the static prior, and within 0.9% with an hourly reconstruction.
- **Our ground-truth simulator** (`components/simulator/`): synthetic, labelled as such. It provides before/after periods with controllable response drift, mix shift, overlap, effect size and hidden confounding, and exact counterfactual values.

## References

All arXiv records: `sources/arxiv_classics.md`, `sources/arxiv_newest.md` (URL https://arxiv.org/abs/ID; accessed 2026-10-04 via the arXiv API). GitHub: `sources/github_repos.md` (accessed 2026-10-04). Web pages (accessed 2026-10-04): https://learn.microsoft.com/en-us/azure/ai-services/personalizer/ · https://learn.microsoft.com/en-us/azure/ai-services/personalizer/concepts-offline-evaluation · https://github.com/st-tech/zr-obp (README, obd/README.md) · https://github.com/facebookresearch/ReAgent (README). Not opened (blocked, HTTP 403): Netflix TechBlog "Artwork Personalization", so it is not cited.
