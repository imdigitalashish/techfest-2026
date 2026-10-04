# Round 1 abstract — Perceptron 2026, Problem 3

> Rendered by `deliverables/render.py` from `eval/results/headline.json`; every number traces to a committed result (`eval/check_docs.py`). Edit `round1-abstract.tmpl.md`, never this file.

**Did-It-Work: attributing a before/after change to the policy — with error bars, and an honest "can't tell"**

**Problem & theme.** Theme 2 (Cause and Effect in AI Decisions), Problem 3. Teams shipping a recommender, pricing rule or quoting strategy usually judge it with a before/after dashboard, which mixes the policy's effect with everything else that changed. We treat it like P&L attribution: separate what the decision caused from what the world did anyway, and say so when the logs cannot tell.

**Understanding of the challenge.** Ȳ_after − Ȳ_before = policy effect + environment change (season, user mix, novelty, and the policy's feedback on who shows up). The missing counterfactual, "old policy during the after period", is never observed. Off-policy evaluation (OPE) identifies it only with logged propensities, overlap, and no unlogged confounding. What is hard:
- When the new policy is greedy, the old policy's actions are rare in the new logs: importance weights turn heavy-tailed and standard intervals under-cover.
- The target is a *difference* of two policy values, needing its own uncertainty.
- No-confounding cannot be tested from the data.
- If the policy changes its audience, a single after-period log cannot identify the total effect.

**Proposed approach.** Typed components (Python, numpy, scikit-learn; CPU-only):
- A policy adapter (any policy as π(a|x) on logged contexts) and a cross-fitted reward model.
- Estimators — IPW, SNIPW, DM, doubly robust (DR; Dudík et al. 2011) and Switch-DR — each returning per-round influence terms, so any interval or sensitivity method plugs in.
- **Spike 1 — Decomposer.** A 2×2 Shapley attribution over {policy, environment}; OPE fills the two never-observed cells (new policy before the switch, old policy after), acting as the control arm a difference-in-differences would need. Output: policy effect, environment change (split into user-mix shift, via a doubly robust density-ratio estimate, and response drift) and their interaction.
- **Spike 2 — Certificate.**
  - (a) An *overlap gate* on ESS/n, effective number of rewarded rows, and a mean-weight test (E[w] = 1). It abstains ("can't tell from these logs") below thresholds calibrated only on simulated data.
  - (b) Intervals for the difference.
  - (c) Marginal-sensitivity-model bounds (Kallus & Zhou 2018; Zhao et al. 2017) with a tipping point Γ\*.
- A verdict: worked / hurt / can't tell, with a waterfall chart.

**Minimum Viable mapping.**
1. *Standard OPE.* Open Bandit Dataset (ZOZOTOWN), pre-registered: from 660,904 uniform-random impressions, DR estimates the Thompson-sampling policy's click rate within 0.1% of its on-policy truth (4.89 clicks per 1,000 impressions); IPW within 1.1%.
2. *Estimate vs naive before/after, on real logs with real truth.* Both policies ran concurrently, so all four period × policy cells are observed.
   - **Re-enacted switch** (Random's logs in the first half of the window, Thompson sampling's in the second): the dashboard reads +1.62 per 1,000 against a true effect of +1.26, overstating it by 29% because the old policy's own rate rose. DR gives +1.40 ± 0.27: its interval holds the truth, but is too wide to rule out the dashboard number.
   - **Reverse switch:** naive is right (−1.25 vs −1.26) and DR is noisier (−1.70).
   - **Whole-day pairs:** DR's interval missed the truth in 3/3 deploy cases (ESS/n down to 0.05%). Applied post hoc, the simulator-calibrated gate abstains on all of them and answers 6/10 cases with 0 wrong.
   - **Simulator** (synthetic, exact truth, 30 seeds): a seasonal drop makes the dashboard read −5.6 points while the switch added +7.5. DR gives +7.5 (RMSE 0.6); naive has the wrong sign in 30/30 seeds.

**Stretch ambitions.**
- **Uncertainty:** Shapley intervals cover 95% in simulation. Next: anytime-valid confidence sequences (Waudby-Smith et al.) for the difference.
- **Confounding:** in an unlogged-override scenario DR is biased by −6.9 points (coverage 0%). The MSM bounds contain the truth in 10/10 runs, and Γ\* = 1.25 flags the conclusion as fragile. Next: benchmark Γ\* against observed covariates.

**Novelty.** The baseline estimates V(π) with Open Bandit Pipeline. We instead:
- attribute the dashboard number, including the policy × season interaction;
- abstain when the logs cannot answer, with thresholds fixed on simulation before being checked on real truth;
- pre-register real-data tests in both switch directions.

We also found that the deployed Thompson-sampling policy drifted within the logged 84 hours (6-hour median propensities of top item-slots varied by a median factor of 16), whereas the standard OBD protocol evaluates one static prior. Closest prior art: Δ-OPE (Jeunen & Ustimenko, RecSys 2024) and distribution-shift attribution (Zhang et al., ICML 2023); our arXiv search found no switch attribution with abstention.

**Evaluation plan.**
- Pre-registered OBD analyses, plus disclosed deviations.
- A frozen simulator bank, and a 13-level drift sweep: naive has the right sign for drift ≥ −0.25 and the wrong sign at ≤ −0.75; DR's RMSE stays ≤ 0.6 points, while naive's reaches 26.2.
- A feedback test: DR recovers the direct effect (+9.1 vs +8.9), while the total effect (+14.6) is not identified, a stated limitation.
- A misspecification test: policy-term bias +0.09 for DR vs +1.58 for DM; doubly robust mix-term bias −0.01 vs +0.57.
- Gate calibration on 36 configurations: coverage among answered runs 0.96; worst ungated configuration 0.65.
- Metrics: RMSE, sign accuracy, coverage, abstention rate, confident-wrong count; baselines: naive, DM, IPW, Open Bandit Pipeline estimators.

**Feasibility and risks.** Everything above runs today on a laptop CPU, one command per result, with contract tests.
- *Team:* Ashish (ML systems, Microsoft; pipeline and evaluation) plus two teammates, TBD (statistics; demo).
- *Milestones:* October — full OBD (all campaigns), confidence sequences. 1–17 November — Γ\* benchmarking and the interactive demo. 19–25 November — exams, no planned work. 1 December — midway report. 15 December — finals.
- *Risks:* the gate may abstain often (it answers 47% of hard simulated cases); mitigation: recommend an exploration floor at logging time. Total effects under feedback stay unidentified. Click rewards are sparse.
