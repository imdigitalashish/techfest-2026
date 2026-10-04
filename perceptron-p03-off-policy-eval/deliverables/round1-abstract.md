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
1. *Standard OPE, Open Bandit Dataset (ZOZOTOWN), pre-registered.* From 660,904 uniform-random impressions and an hourly reconstruction of the adaptive Thompson-sampling policy, DR estimates 4.936 clicks per 1,000 vs that arm's 4.890 (0.9% discrepancy). An approximate-target comparison, not verified accuracy; obp's static prior (a different policy) gives 0.07%.
2. *Estimate vs naive before/after.* OBD's two policies ran concurrently as an A/B test.
   - **Re-enacted switch** (Random logs, then Thompson-sampling logs): the dashboard reads +1.62 per 1,000 against a concurrent arm difference of +1.26: 29% larger, because the old policy's own rate rose. DR gives +1.40 (row-level interval +1.13 to +1.67; post-hoc hour-block +0.93 to +1.78). Both contain the reference and the dashboard number; the gate withholds the primary decision.
   - **Reverse switch:** naive matches (−1.25 vs −1.26); DR is noisier (−1.70).
   - **Whole-day pairs** (disclosed deviation): DR's pre-registered consistency test fails in deploy cases with ESS/n down to 0.05%. Across 8 distinct, overlapping OBD instances, the post-hoc gate answers 5/8; 4/5 intervals hold the reference. It refuses both distinct consistency failures (2/2), and 0/3 answered policy contrasts are confidently wrong-signed.
   - **Simulator** (known model, Monte-Carlo reference, 30 seeds): a seasonal drop makes the dashboard read −5.6 percentage points while the switch added +7.5. DR gives +7.5; naive has the wrong sign in 30/30 seeds.

**Stretch ambitions.**
- **Uncertainty:** Shapley policy intervals hold the reference in 419/440 simulated runs. Next: anytime-valid confidence sequences (Waudby-Smith et al.).
- **Confounding:** with an unlogged override, DR is biased by −6.9 points (coverage 0%). MSM bounds at Γ = 10 (above the simulator's proved bound) hold the reference in 10/10 runs, and the grid crossing Γ\* = 1.25 flags fragility.

**Novelty.** The pieces exist: pairwise OPE (Δ-OPE, Jeunen & Ustimenko 2024), Shapley attribution of shifts (Zhang et al. 2023), diagnostic protocols (Lee et al. 2026), and action-dependent non-stationarity (Chandak et al. 2022). We contribute an integration: an auditable switch-attribution protocol that abstains when logs cannot answer. Its base OPE analyses were pre-registered against concurrent-arm references. The gate was designed after inspecting OBD, applied there retrospectively, then assessed in a separately pre-registered simulator holdout. Finding: the deployed Thompson-sampling policy drifted (6-hour propensities moved a median 16-fold in 84 hours), yet the standard OBD protocol evaluates one static prior.

**Evaluation plan.**
- Pre-registered real-data analyses; deviations disclosed.
- A pre-registered held-out gate test: two new world seeds and 192 settings (positive and harmful effects plus a small scorer-quality-gap configuration). The gate answers 818/1,536 runs; 771/818 answered intervals hold the reference vs 1,404/1,536 overall.
- Simulator checks (one world):
  - Drift (13-level grid): naive's sign is right from −0.25 up, wrong at ≤ −0.75; DR's RMSE ≤ 0.6 points vs naive's 26.2.
  - Feedback: DR recovers the traffic-standardised contrast (+9.1 vs +8.9), not the total effect (+14.6).
  - Misspecification: bias +0.09 vs +1.58 points (DR vs DM contrast), −0.02 vs +0.57 (mix term).
- Metrics: RMSE, sign accuracy, coverage, abstention rate, confident-wrong count; baselines: naive, DM, IPW, paired DR with ordinary diagnostics.

**Feasibility and risks.** Committed estimators and evaluations run on a laptop CPU, one command each; confidence sequences and the interactive report are planned.
- *Team:* Ashish (ML systems, Microsoft) plus two teammates, TBD.
- *Milestones:* estimand fixes by 10 October; protocol freeze 15 October; held-out OBD campaigns by 24 October; submission 28 October; demo 1–17 November; exams 19–25 November; midway report 1 December; finals 15 December.
- *Risks:* frequent abstention (mitigation: recommend an exploration floor); unidentified total effects; sparse clicks; unresolved arm-balance labelling.
