# Round 1 abstract — Perceptron 2026, Problem 3 (DRAFT v1, 2026-10-04)

**Did-It-Work: counterfactual attribution of a policy switch, with error bars and a confounding tipping point**

**Problem & theme.** Theme 2 (Cause and Effect in AI Decisions), Problem 3. Teams that ship a recommender, pricing rule or quoting strategy ask "did the new policy work?" and answer with a before/after dashboard, a number that mixes the policy's effect with everything else that changed. It is P&L attribution for decision systems: separate what our decision caused from what the world did anyway.

**Understanding of the challenge.** The naive gap Ȳ_after − Ȳ_before equals the policy's effect *plus* the environment change: seasonality, a different user mix, novelty, and the policy's feedback on its own future data. The missing quantity is a counterfactual — the old policy's value during the after period — which is never observed. Off-policy evaluation (OPE) identifies it from logs if three conditions hold:
1. the deployed policy logged its action propensities;
2. every action the old policy would take had non-zero probability under the new one (overlap);
3. no unlogged factor drove both actions and outcomes.

The hard parts are the variance of large importance weights when overlap is poor, honest uncertainty on a *difference* of two policy values, and condition 3, which no data can verify.

**Proposed approach.** A pipeline of 12 components with typed contracts (Python/pydantic, numpy, scikit-learn; CPU-only):
1. **Ingestion** of logs into a validated schema: context, action, reward, propensity, period.
2. **Policy adapter**: expresses any policy as π(a|x) on the logged contexts — softmax scorers, ε-greedy, and Bernoulli Thompson Sampling via Monte Carlo from its priors.
3. **Cross-fitted reward model** (logistic regression, LightGBM).
4. **Estimators**: IPW, SNIPW, DM, doubly robust (Dudík et al., ICML 2011), Switch-DR and DR-shrinkage. Each returns per-round influence terms. A Δ-estimator targets V(new) − V(old) on the same traffic, sharing control variates (Δ-OPE, Jeunen & Ustimenko, RecSys 2024).
5. **Spike 1 — Decomposer.** Naive gap = policy effect (OPE: Ȳ_after − V̂_after(old)) + environment change. The environment term is split further into user-mix shift and response drift using period-specific reward models, an Oaxaca–Blinder-style accounting.
6. **Spike 2 — Robustness certificate.** Intervals for Δ: Wald, bootstrap and anytime-valid confidence sequences (Waudby-Smith et al., 2022). Marginal-sensitivity-model bounds with parameter Γ (Kallus & Zhou 2018; percentile bootstrap of Zhao, Small & Bhattacharya). A tipping point Γ\*: the smallest Γ at which the 95% interval for Δ contains zero. Γ\* is benchmarked against observed covariates, so it reads as "a hidden factor would need to be k× as strong as the strongest logged feature".
7. **Report**: a verdict (worked / hurt / inconclusive) with a waterfall chart, intervals and overlap diagnostics (effective sample size, maximum weight) that can force "inconclusive".

**Minimum Viable mapping.**
1. *"Apply a standard OPE method"*: IPW and DR on the **Open Bandit Dataset** (ZOZOTOWN fashion e-commerce; about 26M impressions with true propensities). The uniform-random logs estimate the Bernoulli-TS policy, whose on-policy CTR is real ground truth. Implemented in our walking skeleton.
2. *"A concrete case where the estimate differs from a naive before/after number"*: in our ground-truth simulator, a seasonal drop makes the dashboard show a decline although the new policy truly helped; in the mirror scenario a seasonal rise hides a harmful policy. A semi-synthetic version injects a drift of known size into real OBD clicks.

**Stretch ambitions.** Both official stretch goals are the core of Spike 2: coverage-tested uncertainty for Δ, and sensitivity to unobserved confounding (Γ-curves and Γ\*). A decision needs a sign, error bars and the assumption that could flip it. Further stretch: anytime-valid monitoring, and a trading-flavoured domain (a quote-skew policy with a markout reward).

**Novelty / differentiation.** The starter baseline estimates V(π). We answer the decision question — did the switch *cause* the change? — in three ways:
- we attribute the naive gap rather than replace it;
- we certify the sign of Δ under sampling error *and* hidden confounding jointly, with a calibrated tipping point;
- we validate every number against known counterfactuals.

Related work attributes *model*-performance changes to distribution shifts (Zhang et al., ICML 2023) or forecasts a policy's future value (Shimizu et al., 2025). We found no tool that attributes a policy switch this way.

**Evaluation plan.**
1. A **frozen scenario bank** (drift masking a gain, drift faking a gain, stationary control, hidden override, low overlap) × 100 seeds with exact ground truth. Metrics: RMSE and sign accuracy of Δ̂ versus the naive number; empirical coverage and width of 95% intervals; validity of sensitivity bounds at the true Γ.
2. The **OBD Random→BTS** relative estimation error, following the protocol of Saito et al. (NeurIPS 2021 Datasets & Benchmarks).
3. A **held-out scenario bank** to catch over-tuning.

Baselines: naive before/after, DM, IPW, and the Open Bandit Pipeline estimators. Improvements are kept only if they beat seed-to-seed noise.

**Feasibility and risks.** Everything runs on CPU. A walking skeleton already exists (simulator, five estimators, intervals, MSM bounds, decomposition).
- *Team:* Ashish (ML systems at Microsoft; pipeline and evaluation harness) plus two teammates, TBD (statistics/causal inference; visualisation and demo).
- *Milestones:* October — estimators, Δ-estimator, harness, full OBD. 1–17 Nov — certificate and semi-synthetic OBD. 19–25 Nov — exams, no planned work. 1 Dec — midway report. 15 Dec — interactive demo.
- *Risks:* the mix/drift split depends on the reward model (reported separately from the identified policy term); Γ can be misread (mitigation: covariate benchmarking); a simulator can look rigged (mitigation: a frozen bank that includes cases where the naive number is right).
