# Round 1 abstract — Perceptron 2026, Problem 3

> Rendered by `deliverables/render.py` from `eval/results/headline.json`; every number traces to a committed result (`eval/check_docs.py`). Edit `round1-abstract.tmpl.md`, never this file. The submission text is everything below the title line.

**Did-It-Work: attributing a before/after change to the policy — with error bars, and an honest "can't tell"**

**Problem & theme.** Theme 2 (Cause and Effect in AI Decisions), Problem 3. Teams shipping a recommender, pricing rule or quoting strategy judge it with a before/after dashboard that mixes the policy's effect with everything else that changed. Like P&L attribution, we separate the policy's contrast on observed traffic from changes in traffic and response, and say when logs cannot tell.

**Understanding of the challenge.** Ȳ_after − Ȳ_before = policy contrast + environment change (season, user mix, novelty, feedback on who arrives). The counterfactual "old policy during the after period" is never observed. Off-policy evaluation (OPE) identifies it only with logged propensities, action support, and no unlogged confounding. What is hard:
- Near-greedy new policies leave the old policy's actions rare: weights turn heavy-tailed, intervals under-cover, unsupported actions are unidentified.
- The target is a *difference* of policy values, needing its own uncertainty.
- No-confounding is untestable.
- Audience feedback makes the total effect unidentified from one period's logs.

**Proposed approach.** CPU-only components:
- A policy adapter, a cross-fitted reward model, and IPW, SNIPW, DM, doubly robust (DR; Dudík et al. 2011) and Switch-DR estimators returning paired per-round scores.
- **Spike 1 — Decomposer.**
  - Primary estimand: the after-period policy contrast on the observed traffic.
  - Secondary: a 2×2 Shapley attribution over {policy, environment} with interaction; OPE fills the two never-observed cells, playing the control arm a difference-in-differences would need.
  - Separately, the old-policy-ordered environment change is split into user-mix shift (doubly robust density ratio) and response drift.
- **Spike 2 — Certificate.**
  - (a) An exploratory *overlap gate* (ESS/n, mean-weight test): if the primary contrast's cell fails it, the verdict is "can't tell from these logs"; secondary attributions never replace it.
  - (b) Intervals: Wald and hour-block bootstrap.
  - (c) Marginal-sensitivity-model (MSM) bounds (Kallus & Zhou 2018; Zhao et al. 2017) for the after-period contrast, with tipping point Γ\*.
- A verdict: worked / hurt / inconclusive / can't tell.

**Minimum Viable mapping.**
1. *Standard OPE, Open Bandit Dataset (ZOZOTOWN), pre-registered.* From {{obd_rows_random}} uniform-random impressions and an hourly reconstruction of the adaptive Thompson-sampling policy, DR estimates {{a2_hourly_dr_k3}} clicks per 1,000 vs that arm's {{obd_ctr_bts_k3}} ({{a2_hourly_dr_relerr}} discrepancy). An approximate-target comparison, not verified accuracy; obp's static prior (a different policy) gives {{a2_static_dr_relerr2}}.
2. *Estimate vs naive before/after.* OBD's two policies ran concurrently as an A/B test.
   - **Re-enacted switch** (Random logs, then Thompson-sampling logs): the dashboard reads {{a3A_naive_k}} per 1,000 against a concurrent arm difference of {{a3A_truth_k}}: {{a3A_overstate}} larger, because the old policy's own rate rose. DR gives {{a3A_dr_k}} (row-level interval {{a3A_dr_lo}} to {{a3A_dr_hi}}; post-hoc hour-block {{bb_A_lo}} to {{bb_A_hi}}). Both contain the reference and the dashboard number; the gate withholds the primary decision.
   - **Reverse switch:** naive matches ({{a3B_naive_k}} vs {{a3B_truth_k}}); DR is noisier ({{a3B_dr_k}}).
   - **Whole-day pairs** (disclosed deviation): DR's pre-registered consistency test fails in deploy cases with ESS/n down to {{dayA_min_ess_pct}}. Across {{gate_obd_unique}} distinct, overlapping OBD instances, the post-hoc gate answers {{gate_obd_u_answered}}; {{gate_obd_u_ref_in_ci}} intervals hold the reference. It refuses both distinct consistency failures ({{gate_obd_u_s1rej_abst}}), and {{gate_obd_u_wrongsign}} answered policy contrasts are confidently wrong-signed.
   - **Simulator** (known model, Monte-Carlo reference, {{bank_seeds}} seeds): a seasonal drop makes the dashboard read {{s1_naive_pp}} percentage points while the switch added {{s1_truth_pp}}. DR gives {{s1_dr_pp}}; naive has the wrong sign in {{s1_naive_wrong}} seeds.

**Stretch ambitions.**
- **Uncertainty:** Shapley policy intervals hold the reference in {{shap_counts}} simulated runs. Next: anytime-valid confidence sequences (Waudby-Smith et al.).
- **Confounding:** with an unlogged override, DR is biased by {{s4_dr_bias_pp}} points (coverage {{s4_dr_cover}}). MSM bounds at Γ = 10 (above the simulator's proved bound) hold the reference in {{s4_msm_valid}} runs, and the grid crossing Γ\* = {{s4_gamma_star}} flags fragility.

**Novelty.** The pieces exist: pairwise OPE (Δ-OPE, Jeunen & Ustimenko 2024), Shapley attribution of shifts (Zhang et al. 2023), diagnostic protocols (Lee et al. 2026), and action-dependent non-stationarity (Chandak et al. 2022). We contribute an integration: an auditable switch-attribution protocol that abstains when logs cannot answer. Its base OPE analyses were pre-registered against concurrent-arm references. The gate was designed after inspecting OBD, applied there retrospectively, then assessed in a separately pre-registered simulator holdout. Finding: the deployed Thompson-sampling policy drifted (6-hour propensities moved a median {{a1_median_ratio}}-fold in {{obd_hours}} hours), yet the standard OBD protocol evaluates one static prior.

**Evaluation plan.**
- Pre-registered real-data analyses; deviations disclosed.
- A pre-registered held-out gate test: two new world seeds and {{ho_settings}} settings (positive and harmful effects plus a small scorer-quality-gap configuration). The gate answers {{ho_answered_counts}} runs; {{ho_cov_ans_counts}} answered intervals hold the reference vs {{ho_cov_all_counts}} overall.
- Simulator checks (one world):
  - Drift ({{sweep_points}}-level grid): naive's sign is right from {{sweep_right_from}} up, wrong at ≤ {{sweep_wrong_from}}; DR's RMSE ≤ {{sweep_dr_rmse_max_pp}} points vs naive's {{sweep_naive_rmse_max_pp}}.
  - Feedback: DR recovers the traffic-standardised contrast ({{fb_dr_pp}} vs {{fb_direct_pp}}), not the total effect ({{fb_total_pp}}).
  - Misspecification: bias {{ms_dr_bias_pp}} vs {{ms_dm_bias_pp}} points (DR vs DM contrast), {{ms_mixdr_bias_pp}} vs {{ms_mixdm_bias_pp}} (mix term).
- Metrics: RMSE, sign accuracy, coverage, abstention rate, confident-wrong count; baselines: naive, DM, IPW, paired DR with ordinary diagnostics.

**Feasibility and risks.** Committed estimators and evaluations run on a laptop CPU, one command each; confidence sequences and the interactive report are planned.
- *Team:* Ashish (ML systems, Microsoft) plus two teammates, TBD.
- *Milestones:* estimand fixes by 10 October; protocol freeze 15 October; held-out OBD campaigns by 24 October; submission 28 October; demo 1–17 November; exams 19–25 November; midway report 1 December; finals 15 December.
- *Risks:* frequent abstention (mitigation: recommend an exploration floor); unidentified total effects; sparse clicks; unresolved arm-balance labelling.
