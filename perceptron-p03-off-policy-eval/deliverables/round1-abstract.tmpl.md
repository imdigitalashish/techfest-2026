# Round 1 abstract — Perceptron 2026, Problem 3

> Rendered by `deliverables/render.py` from `eval/results/headline.json`; every number traces to a committed result (`eval/check_docs.py`). Edit `round1-abstract.tmpl.md`, never this file.

**Did-It-Work: attributing a before/after change to the policy — with error bars, and an honest "can't tell"**

**Problem & theme.** Theme 2 (Cause and Effect in AI Decisions), Problem 3. Teams that ship a recommender, pricing rule or quoting strategy usually judge it with a before/after dashboard. That number mixes the policy's effect with everything else that changed. We treat it like P&L attribution: separate what the decision caused from what the world did anyway, and say so when the logs cannot tell.

**Understanding of the challenge.** Ȳ_after − Ȳ_before = policy effect + environment change (season, user mix, novelty, and the policy's feedback on who shows up). The missing counterfactual, "old policy during the after period", is never observed. Off-policy evaluation (OPE) identifies it only with logged propensities, overlap, and no unlogged confounding. What is hard:
- When the new policy is greedy, the old policy's actions are rare in the new logs: importance weights turn heavy-tailed and standard intervals under-cover.
- The question concerns a *difference* of two policy values, needing its own honest uncertainty.
- No-confounding cannot be tested from the data.
- If the policy changes its audience, a single after-period log cannot identify the total effect.

**Proposed approach.** Typed components (Python, numpy, scikit-learn; CPU-only):
- A policy adapter (any policy as π(a|x) on logged contexts) and a cross-fitted reward model.
- Estimators — IPW, SNIPW, DM, doubly robust (DR; Dudík et al. 2011) and Switch-DR — each returning per-round influence terms, so any interval or sensitivity method plugs in.
- **Spike 1 — Decomposer.** A 2×2 Shapley attribution over {policy, environment}; OPE fills the two never-observed cells (new policy before the switch, old policy after). Output: policy effect, environment change (split into user-mix shift, via a doubly robust density-ratio estimate, and response drift) and their interaction.
- **Spike 2 — Certificate.**
  - (a) An *overlap gate* on ESS/n, effective number of rewarded rows, and a mean-weight test (E[w] = 1). It abstains ("can't tell from these logs") below thresholds calibrated only on simulated data.
  - (b) Intervals for the difference.
  - (c) Marginal-sensitivity-model bounds (Kallus & Zhou 2018; Zhao et al. 2017) with a tipping point Γ\*.
- A report: worked / hurt / can't tell, with a waterfall chart.

**Minimum Viable mapping.**
1. *Standard OPE.* Open Bandit Dataset (ZOZOTOWN), pre-registered: from {{obd_rows_random}} uniform-random impressions, DR estimates the Thompson-sampling policy's click rate within {{a2_static_dr_relerr}} of its on-policy truth ({{obd_ctr_bts_k}} clicks per 1,000 impressions); IPW within {{a2_static_ipw_relerr}}.
2. *Estimate vs naive before/after, on real logs with real truth.* Both policies ran concurrently, so all four period × policy cells are observed.
   - **Re-enacted switch** (Random's logs in the first half of the window, Thompson sampling's in the second): the dashboard reads {{a3A_naive_k}} per 1,000 against a true effect of {{a3A_truth_k}}, overstating it by {{a3A_overstate}} because the old policy's own rate rose. DR gives {{a3A_dr_k}}, and its interval contains the truth.
   - **Reverse switch:** naive is right ({{a3B_naive_k}} vs {{a3B_truth_k}}) and DR is noisier ({{a3B_dr_k}}).
   - **Whole-day pairs:** DR's interval missed the truth in {{dayA_dr_fail}} deploy cases (ESS/n down to {{dayA_min_ess_pct}}). Applied post hoc, the simulator-calibrated gate abstains on all of them and answers {{gate_obd_answered}} cases with {{gate_obd_wrong}} wrong.
   - **Simulator** (synthetic, exact truth, {{bank_seeds}} seeds): a seasonal drop makes the dashboard read {{s1_naive_pp}} points while the switch added {{s1_truth_pp}}. DR gives {{s1_dr_pp}} (RMSE {{s1_dr_rmse_pp}}); naive has the wrong sign in {{s1_naive_wrong}} seeds.

**Stretch ambitions.**
- **Uncertainty:** Shapley intervals cover {{shap_cover}} in simulation. Next: anytime-valid confidence sequences (Waudby-Smith et al.) for the difference.
- **Confounding:** in an unlogged-override scenario DR is biased by {{s4_dr_bias_pp}} points (coverage {{s4_dr_cover}}). The MSM bounds contain the truth in {{s4_msm_valid}} runs, and Γ\* = {{s4_gamma_star}} flags the conclusion as fragile. Next: benchmark Γ\* against observed covariates.

**Novelty.** The baseline estimates V(π) with Open Bandit Pipeline. We instead:
- attribute the dashboard number, including the policy × season interaction;
- abstain when the logs cannot answer, with thresholds fixed on simulation before being checked on real truth;
- pre-register real-data tests in both switch directions.

We also found that the deployed Thompson-sampling policy drifted within the logged {{obd_hours}} hours: for the top item-slots, the 6-hour median logged propensity varied by a median factor of {{a1_median_ratio}}. The standard OBD protocol (obp's example) evaluates one static prior instead. Closest prior art: Δ-OPE (Jeunen & Ustimenko, RecSys 2024) and distribution-shift attribution (Zhang et al., ICML 2023); our arXiv search found no switch attribution with abstention.

**Evaluation plan.**
- Pre-registered OBD analyses, plus disclosed deviations.
- A frozen simulator bank, and a {{sweep_points}}-level drift sweep: naive has the right sign for drift ≥ {{sweep_right_from}} and the wrong sign at ≤ {{sweep_wrong_from}}; DR's RMSE stays ≤ {{sweep_dr_rmse_max_pp}} points, while naive's reaches {{sweep_naive_rmse_max_pp}}.
- A feedback test: DR recovers the direct effect ({{fb_dr_pp}} vs {{fb_direct_pp}}), while the total effect ({{fb_total_pp}}) is not identified, a stated limitation.
- A misspecification test: policy-term bias {{ms_dr_bias_pp}} for DR vs {{ms_dm_bias_pp}} for DM; doubly robust mix-term bias {{ms_mixdr_bias_pp}} vs {{ms_mixdm_bias_pp}}.
- Gate calibration on {{gate_sim_configs}} configurations: coverage among answered runs {{gate_sim_cov}}; worst ungated configuration {{gate_sim_ungated_worst}}.
- Metrics: RMSE, sign accuracy, coverage, abstention rate, confident-wrong count. Baselines: naive, DM, IPW, and the Open Bandit Pipeline estimators.

**Feasibility and risks.** Everything above runs today on a laptop CPU, one command per result, with contract tests.
- *Team:* Ashish (ML systems, Microsoft; pipeline and evaluation) plus two teammates, TBD (statistics; demo).
- *Milestones:* October — full OBD (all campaigns), confidence sequences. 1–17 November — Γ\* benchmarking and the interactive demo. 19–25 November — exams, no planned work. 1 December — midway report. 15 December — finals.
- *Risks:* the gate may abstain often (it answers {{gate_sim_answer}} of hard simulated cases); mitigation: recommend an exploration floor at logging time. Total effects under feedback stay unidentified. Click rewards are sparse.
