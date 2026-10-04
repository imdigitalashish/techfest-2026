# Perceptron P3 · Did the policy actually work? (off-policy evaluation) — Thought Node

> Journal for `perceptron-p03-off-policy-eval/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** ⏸ **PAUSED** (2026-10-04 23:37 IST; user directive via the Supervisor, 23:36). Demo phase: **the demo is built and verified; DEMO DONE has not been sent yet** (no DEMO DONE tonight, per the directive).
- **Resume point (exact):**
  1. Re-verify: `git fetch origin && bash perceptron-p03-off-policy-eval/eval/verify_demo_clean.sh` (expected: run.sh ≤ 1 s, smoke 30/30 PASS).
  2. A quick browser look at the D1/D2 fixes: sheet 3 at Nov 26 α 0.33, cluster mode, should show "E1 inside; E2 still rejects".
  3. Message the Supervisor "DEMO DONE".
  4. Optional: a short gpt-6-astra re-check of the fixed demo (86540241), with a ledger row.
- **Demo state at pause** (main 86540241, verified from a clean checkout at 23:36:15 IST: no .data; run.sh 0.2 s; smoke 30/30 PASS):
  - The builder applied all 12 demo-review fixes. Spoken script 375 words; measured rehearsal 2:52 with clicks. E1 and E2 are shown side by side, with the BTS-primary counts 75/12/403/116 (69/81 at α>0).
  - The builder ("P3 demo builder") was told to stop and stay idle. No servers or jobs of mine are running.
- **Definition of done (Supervisor 13:05):**
  1. **Real OBD check**, with the analysis pre-registered before results: the BTS time-window slice; a drift test of the deployed BTS's logged propensities; a real before/after with real truth, in both directions.
  2. **Decomposer review fixes:** (a) a feedback/mix-shift knob; (b) the 2×2 Shapley decomposition plus the interaction term; (c) a misspecification test; (d) a drift sweep that shows where naive is right and where it is wrong.
  3. **Final abstract** rendered from committed results, plus a doc-drift check script and the architecture diagram.
  4. **Cross-model reviews** as child sessions: gpt-6-astra (max) as hostile judge; gpt-6-sol (max) on code/eval, including reproducing the headline numbers. Recorded in `reviews/` and `reviews/ledger.tsv`.
  5. **Final selection memo** (an honest case versus P7, P9, P1 and P4), thought node current, pushed, then "DONE — slot free".
- **Rules in force:** child sessions only (at most 2 at a time); never `git stash` or `--autostash`; start heavy jobs only when `kern.memorystatus_level` ≥ 30, under `nice -n 10`, one at a time, pausing below 25; keep network requests small.
- **Doing (2026-10-04 14:33 IST):** Nothing running. Final abstract v4: 897 words, 0 untraced numbers, `check_docs` PASS, 14 tests pass. Hostile re-score 69/100. Final memo recommends P7 over P3, narrowly.
- **Next (after DONE; dated):**
  1. By 10 Oct: the 2×2 nuisance-correctness test for the DR mix term (A9); the OBD environment interval (C8) on the next OBD run; a paired DR + ordinary-diagnostics baseline (A12).
  2. 15 Oct: protocol freeze (estimands, gate, metrics).
  3. By 24 Oct: held-out OBD campaigns (Men/Women, unseen).
  4. 28 Oct: final submission.
- **Needs from user:** Register by 15 Oct if P3 is chosen. Teammates' names and skills for the team-fit section.
- **Risks:**
  - On real data the BTS−Random difference may be too small, or IPW too noisy, to be conclusive. We report it either way, as pre-registered.
  - The network is congested.
- **Morning package (done 08:05 IST; accepted by the Supervisor):** landscape, components + contracts, ADR 001, selection memo v1, abstract + architecture, skeleton + simulator bank v0 + OBD sample check, C6 ratchet (baseline + 1 iteration). Details are in the Log.

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** Perceptron Hackathon 2026 — IITB-Optiver AI Innovation Lab, Techfest IIT Bombay. Prize pool ₹2,00,000 for the top 3 teams overall.
- **Official statement:** [`_briefs/perceptron.pdf`](../_briefs/perceptron.pdf) (text: [`_briefs/perceptron.txt`](../_briefs/perceptron.txt)).
- **Rounds:** register by **15 Oct** → Round 1 abstract (600–900 words + optional 1-page architecture diagram, submitted once by the team leader) due **31 Oct** → shortlist **10 Nov** (25–30 teams across all 10 problems) → midway check **1 Dec** (1-page progress report, unscored) → finals **15–18 Dec** at IIT Bombay: a working build demonstrating the Minimum Viable scope (plus any stretch goals attempted), judged by Optiver and IIT Bombay professors; top 3 overall win.
- **Round 1 judging:** problem understanding & relevance 20% · technical soundness & feasibility 25% · innovation/novelty beyond the starter-resource baseline 20% · clarity & structure 10% · impact & rigor of the evaluation plan 15% · team fit & readiness (skill mix, week-by-week milestones) 10%.
- **The abstract must cover:** the problem and why · the core technical difficulty in our own words · a concrete approach naming techniques, models, datasets and tools · an explicit mapping to the Minimum Viable bullets · stretch goals · novelty vs the obvious baseline · the evaluation plan (metrics, baselines, datasets/simulators) · feasibility and risks.
- **Hard constraints:** students only, team ≤3; **one problem per team**; original work (not protected by patents or publications); queries only via the Techfest portal.
- **Round-1 deliverable for the morning package:** `deliverables/round1-abstract.md` (600–900 words) + `deliverables/architecture.md` (mermaid diagram).

**Problem 3 — Did the Policy Actually Work, or Did It Just Look Like It Did?** (Theme 2: Cause and Effect in AI Decisions — the theme's only problem)
- **Context:** A deployed decision system shapes the very outcomes later used to judge it, so simple before/after metrics can mislead.
- **Challenge:** Estimate what would have happened under a different policy, using only logged data from the current one.
- **Starter resources:** A public bandit-feedback or off-policy evaluation dataset (e.g. Open Bandit Dataset), or a synthetic dataset with known ground-truth counterfactuals.
- **Minimum Viable:** apply a standard off-policy evaluation method (e.g. inverse propensity weighting or a doubly robust estimator); show a concrete case where this estimate differs from a naive before/after number.
- **Stretch goals:** quantify uncertainty on the counterfactual estimate; a basic sensitivity analysis for unobserved confounding.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Data and tooling: Open Bandit Dataset + Open Bandit Pipeline (`obp`: IPW, SNIPW, DM, DR, SNDR, Switch-DR, DRos, MRDR), SCOPE-RL.
- Uncertainty: bootstrap and concentration-bound intervals, high-confidence OPE. Confounding: marginal sensitivity model, Rosenbaum bounds, E-values.
- Large action spaces: MIPS, OffCEM; simulators with known counterfactuals for ground truth.
- What companies ship: experimentation and counterfactual-evaluation platforms at large recommender, ads and marketplace companies — check their engineering blogs.

## Key decisions
- 2026-10-04 — **Framing:** answer "did the switch cause the change?" (the policy effect in the after period) rather than only "what is V(π)?". Use OPE to build the counterfactual "old policy during the after period", and attribute the naive gap to it.
- 2026-10-04 — **Spikes:** the C9 Decomposer and the C8+C7 Robustness Certificate (see [ADR 001](architecture/adr/001-spike.md)). The auto-research ratchet targets C6 (Δ-RMSE on the frozen bank). It is process, not pitch, because GrowthHacker (arXiv:2511.00802) is prior art.
- 2026-10-04 — **Own numpy implementations behind contracts**, cross-checkable against obp later. Reason: obp's last release was 0.5.5 in June 2022 (GitHub API), and tonight's stack is pandas 3, numpy 2.4 and scikit-learn 1.9.
- 2026-10-04 — **Assumption (no user input):** the team is Ashish plus two TBD teammates; the abstract says so.
- 2026-10-04 13:06 — **Real-data analysis pre-registered** (`eval/preregistration_obd.md`, commit f88de64) before any BTS-slice result. DR was fixed as the primary estimator.
- 2026-10-04 13:20 — **Disclosed deviation:** the pre-registered window started 47 ms after midnight, so day 2019-11-24 was excluded. A flagged deviation run adds it (`*_deviation_floor*`); both versions are reported.
- 2026-10-04 13:39 — **Overlap gate (C10) adopted as a product feature** (Supervisor's suggestion; refined by the lead: multi-diagnostic, simulator-only calibration).
  - Rule: abstain if ESS/n < 0.05, effective rewards < 0 or |mean-weight z| > 3; frozen in `eval/gate_rule.json` (commit b4e95ae) before being applied to OBD.
  - The OBD check is labelled POST-HOC because its outcomes had been seen.
- 2026-10-04 13:36 — **Decomposer v1:** a 2×2 Shapley attribution with an interaction term replaces the environment-first ordering as the headline. The mix term gets a doubly robust (density-ratio) option. v0 is kept for the frozen bank.
- 2026-10-04 — **Identification limit stated:** with policy-induced audience change (feedback), the logs identify the direct effect only. The total effect is reported as not identified.
- 2026-10-04 14:20 — **After the cross-model reviews** (astra 59/100 pre-fix; sol 44/44 numbers reproduced):
  - Primary estimand = the after-period contrast on observed traffic; the Shapley attribution is secondary. The ordered mix split is labelled as belonging to the old-policy ordering.
  - "0.1% accuracy" is withdrawn (approximate target). "Truth" is renamed "concurrent arm difference / reference".
  - The gate is labelled exploratory, with a pre-registered held-out validation (criteria met).
  - The novelty claim is reframed as integration.

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | LogIngest | raw → `BanditLog` | obp loader | | contract done | validation pass rate |
| C2 | PolicyAdapter | policy → `ActionDist` | obp BTS action dist | | sim policies done; BTS MC pending | MC error |
| C3 | PropensityModel | log → `Propensity` | logged / logistic | | logged only | held-out log-loss |
| C4 | RewardModel | log → `RewardModelOut` | cross-fitted logistic | | done (`components/estimators/ope.py`) | held-out log-loss |
| C5 | ValueEstimator | → `ValueEstimate` | IPW/SNIPW/DM/DR/Switch-DR | | done | rel. error (OBD), RMSE (bank) |
| C6 | DeltaEstimator | → `DeltaEstimate` | V̂(new) − V̂(old) | ratchet target | DR baseline; ratchet live (`components/delta_estimator/autoresearch/`) | Δ-nRMSE on the mini bank (baseline 0.21823) |
| C7 | Interval | influence → `Interval` | Wald, bootstrap | ★ (with C8) | baseline done | coverage + width |
| C8 | Sensitivity | → `SensitivityCurve` | MSM Hajek bounds + bootstrap | ★ | v0 done (`components/sensitivity/msm.py`) | validity at Γ_true + width |
| C9 | Decomposer | before/after → `Decomposition`, `ShapleyDecomposition` | naive gap | ★ | v1: 2×2 Shapley + interaction, DR mix term | RMSE + sign of the policy term; Shapley coverage 0.95 (sim) |
| C10 | Report + overlap gate | → `Verdict` (worked / hurt / can't tell) | dashboard number | ★ (gate) | gate v1 calibrated on sim (`components/report/gate.py`) | confident-wrong count; abstention rate |
| C11 | Simulator | config → logs + `GroundTruth` | obp synthetic | | + feedback, nonlinearity, sparse rewards, MC propensity noise (v0 worlds unchanged, tested) | truth MC precision |
| C12 | EvalHarness | bank × seeds → metrics | obp evaluate | | v0 running | — |

## Selection memo
_**Final for the 12 Oct pick**, rendered from `deliverables/selection-memo.tmpl.md` + `eval/results/headline.json` by `deliverables/render.py`. Every number traces to committed results, to `reviews/scores.json`, or to another project's cited memo (`eval/check_docs.py`). Supersedes v1 (07:35)._

**Scores (1–5), each with its evidence:**
- **Winnability — 3/5.**
  - The hostile cross-model judge (gpt-6-astra, max) scored the abstract **59/100** before fixes and **69/100** after them: "borderline, still lean no", with no blockers left (`reviews/`).
  - Strengths a judge can verify: real data with a concurrent-arm reference, pre-registration, disclosed deviations, and all 44 abstract numbers reproduced by an independent reviewer.
  - Weakness: the headline real-data improvement is modest, and on the flagship case the gate rightly withholds the decision.
- **Innovation headroom — 3/5.** This is an integration, not a new estimator: Δ-OPE, Shapley shift attribution, diagnostic protocols and non-stationary OPE are prior art. The defensible additions:
  - an auditable switch-attribution protocol that says "can't tell";
  - the finding that the deployed Thompson-sampling policy drifted (median 16-fold) while the standard OBD protocol evaluates one static prior.
- **Feasibility — 5/5.** Everything runs on the M5 CPU, one command per result; contract tests pass. The full OBD can be read by HTTP range requests (no 413 MB download). Nothing is gated on the user or a GPU, and the 19–25 Nov exams are kept free.
- **Demo strength — 4/5.**
  - A waterfall ("the dashboard said −5.6 points; the season did it; the policy added +7.5").
  - A verdict that can say "can't tell from these logs".
  - A Γ slider for hidden confounding.
  - Less visual than the agent or market-simulation demos.
- **Fit with the user's strengths — 3/5.** Statistics and causal inference more than large-scale systems or frontier models. Bridges: range-read data engineering on the 26M-row OBD, and streaming (anytime-valid) monitoring as next work.

**Overall: 3.6/5** (unweighted mean of the five scores).

**Honest comparison with the finished candidates** (their own final memos, read on main 4 Oct):
- **P7** (hostile judge 71/100; fit 5) scores slightly higher and fits the user better.
- **P1** (hostile judge 3.40/5; fit 5) and **P9** (hostile judge 3.10/5, 62/100; fit 5) fit the user better.
- **P4** (hostile judge 2.65/5 before fixes) is weaker.
- **P3's edge:** the closest match to its brief (MVP and both stretch goals are working), with real concurrent-arm references and a pre-registered, falsifiable evaluation.
- **P3's weakness:** lower fit, and a nuanced real-data story. OPE fails when the new policy is greedy, so the tool often abstains.
- **Recommendation:** **P7 over P3**, narrowly: P7's hostile score is a little higher (71 vs 69) and its fit with the user's strengths is better (5 vs 3). P3 is the credible runner-up. Pick it only if the team values real-data causal evidence over fit.

**Biggest risk:** a judge reads "known parts" and "abstains often" as weak. Mitigation: lead with the real-reference evaluation and with the gate preventing confident wrong answers, then show the protocol finding.

**One-line pitch:** "The dashboard said the new policy lifted clicks 29% more than the concurrent A/B showed. Our tool separates what the policy did from what the week did, and says 'can't tell' when the logs can't support an answer."

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 02:05 IST — Phase 0 done; research fan-out launched
- Read `PLAYBOOK.md`, this brief and `_briefs/perceptron.txt` (verified: problem text, MVP and stretch bullets, rounds, judging weights and dates match the seeded brief).
- What we must be able to show, from the judging weights: (1) the crux in our own words: the policy changes the data and the world drifts, so a before/after number confounds the policy's effect with trend, mix shift and selection (20%); (2) a valid estimator with stated assumptions — overlap, logged propensities, no unmeasured confounding — plus a feasible plan (25%); (3) something beyond "run IPW/DR from obp" (20%); (4) an evaluation that proves the claim — ground truth from a simulator and the OBD Random→BTS protocol, coverage of intervals, bias of the naive number (15%).
- Created the folder layout and a uv venv (`.venv`, Python 3.11; numpy 2.4.6, scipy 1.17.1, pandas 3.0.6, scikit-learn 1.9.1, pydantic 2.13.5; installed offline from the uv cache because PyPI downloads timed out).
- Spawned 8 research sub-agents (R1 estimators, R2 uncertainty, R3 confounding, R4 code and datasets, R5 companies, R6 feedback loops, R7 social signal, R8 trading and competition intel).

### 2026-10-04 05:55 IST — All 8 research agents failed; switching to lean mode
- Every sub-agent failed at 0 turns with `408 Timed out reading request body`, so no research files were produced. The network is saturated across the portfolio.
- Supervisor's lean-mode directive (05:50) received: no sub-agents, small requests, nothing over 200 MB, push every 30 minutes. Plan reordered to match. Research is now done directly: arXiv API and GitHub API records saved under `research/sources/`.

### 2026-10-04 07:35 IST — Morning package mostly on main; skeleton running
- **Research (lead, lean mode):**
  - 50 arXiv records fetched through the official API, abstracts saved under `research/sources/`.
  - Newest work found includes: GrowthHacker (2511.00802, prior art for our ratchet); Adyen's production OPE (2501.10470); OPE under non-stationarity (2506.20417); "When offline evaluation misleads" (2608.11560, closest framing); Jeunen's A/B acceleration (2607.14604) and additive control variates (2602.14914).
  - Company facts verified first-party: Azure Personalizer was retired on 25 Aug 2026 (Microsoft Learn); ReAgent is archived in favour of Pearl (README); obp's last release was 0.5.5 in June 2022 (GitHub API).
- **Architecture:** 12 components with executable pydantic contracts; ADR 001 picks the C9 Decomposer and the C8+C7 Certificate as spikes.
- **Deliverables:** abstract v1 (894 words) and a mermaid architecture diagram.
- **OBD sample** (10k rows per policy, "All" campaign, fetched by `eval/fetch_obd_sample.sh`): Random CTR 0.00380 (38 clicks), BTS CTR 0.00420 (42 clicks); Random propensity is 0.0125 (= 1/80); both logs span 2019-11-24 to 2019-11-30, so the two policies ran concurrently. Our pandas run.
- **Smoke run** (4 seeds; not committed, superseded by the 30-seed run):
  - DR recovered the policy effect with RMSE about 0.003 in the stationary and drift scenarios.
  - With an unlogged override (S4), every estimator was biased by about −0.07 with 0% coverage; MSM bounds held the truth at Γ_true and flagged fragility (Γ\* about 1.25).
  - S1/S2 drift was too weak to flip the naive sign, so before freezing bank v0 the drifts were set to ±1.0 logit, chosen from ground-truth-only checks: S1 truth +0.075 vs naive −0.054; S2 truth −0.084 vs naive +0.090.
- **Supervisor 07:22:** alignment check answered (the abstract was already on main; order agreed).

### 2026-10-04 07:45 IST — Real numbers committed; abstract updated
- **Sim bank v0** (SYNTHETIC; 30 seeds; 10k rows per period; `eval/run_sim_bank.py --seeds 30`; results in `eval/results/`):
  - Naive before/after has the wrong sign in 30/30 seeds in both S1 (drift masks a gain) and S2 (drift fakes a gain).
  - DR is within RMSE ≤ 0.006 of the truth, with 93% Wald coverage in S1–S3.
  - S5 (low overlap, ESS 79/10k): IPW and DR coverage 0.90 with wide CIs; Switch-DR is narrow but covers only 0.63. This shows the classic variance–coverage trade-off and is a target for the C7 ratchet.
  - S4 (hidden override): OPE fails (DR bias −0.069; coverage 0) while naive keeps the right sign, so OPE is not magic when propensities are wrong. The MSM joint bounds contain the truth at Γ_true (6.94) in 10/10 seeds, and Γ\* (median 1.25) flags the conclusion as fragile. This is exactly the stretch-2 story.
- **OBD sample** (REAL; 10k rows per policy): every estimator's interval contains the on-policy BTS CTR (0.00420); inconclusive at this size.
  - Finding: the BTS logs' own propensities do not match obp's static BTS prior. Correlation 0.074 at (item, position); logged median propensity 0.064 vs 0.019 from the prior; empirical item frequencies correlate 0.595 with the prior.
  - Hypothesis (UNVERIFIED): the deployed BTS updated its posterior during the week. So we added a week-average empirical-BTS evaluation policy (ESS 2,639 vs 1,644 for the prior).
- **Abstract:** MVP bullets now carry these numbers, labelled as simulator vs the real OBD sample (863 words).
- **Tests:** 8/8 contract tests pass.

### 2026-10-04 07:57 IST — First auto-research ratchet; morning package complete
- **C6 ratchet** (`components/delta_estimator/autoresearch/`):
  - `program.md` sets the goal, constraints and an 8-idea backlog from the landscape. `eval.py` is FROZEN: a mini bank of 4 synthetic scenarios × 12 seeds, 5k rows each, plus a `--holdout` world seed.
  - Baseline DR: dev nRMSE **0.21823**.
  - Iteration 1, SNDR: 0.21944 (+0.00121, within noise). Not kept; reverted. Ledger in `results.tsv`.
  - Lesson: at 12 seeds, coverage is noisy (the baseline's minimum is 0.83 against a 0.90 guard). Next iterations double the seeds before any keep decision.
- **Per-component research index:** `research/components/README.md` (mapped to landscape sections, as lean mode allows).
- **Morning package (PLAYBOOK §9) status:**
  1. landscape ✅
  2. components + contracts ✅
  3. per-component research ✅ (index; dedicated spike files next)
  4. ADR 001 ✅
  5. selection memo v1 ✅
  6. Round-1 abstract + architecture ✅
  7. skeleton + eval with real numbers ✅ (simulator bank v0 + OBD sample)
  8. first ratchet loop ✅ (baseline + 1 iteration)
  9. thought node current ✅

### 2026-10-04 08:03 IST — Demo asset
- Waterfall charts for S1 and S2 in `deliverables/figures/`, rendered by `eval/plot_waterfall.py` from the committed `sim_bank_runs.csv` (SYNTHETIC). S1: the dashboard shows −0.056; the estimated split is policy +0.075, mix +0.016, season −0.146, each matching the truth to 3 decimals. Linked from `deliverables/architecture.md`.

### 2026-10-04 09:58 IST — Resumed in lean mode, then PAUSED by the Supervisor
- 09:40 Supervisor: lean mode again; next tasks are a larger real OBD slice and a hostile review of the decomposer.
- **The OBD zip supports HTTP range requests** (`accept-ranges: bytes`; 412,931,917 bytes; last modified 20 Aug 2020). New tool `eval/obd_zip_slice.py` reads the central directory and streams one member, so no full download is needed.
  - Member sizes, compressed (uncompressed): random/all 22.1 MB (695.5 MB); bts/all 203.6 MB (6,321 MB); random/men 6.4; random/women 12.4; bts/men 57.5; bts/women 110.9.
- **Fetched the full Random log for the All campaign:** 1,374,327 rows, time-sorted, compact npz in gitignored `.data/obd_slice/`.
- 09:55 Supervisor: **PAUSE** (only 3 projects run at a time). No jobs were running; the exact resume point is in *Now*. Going idle.

### 2026-10-04 13:45 IST — Resumed: real OBD pre-registered and run; decomposer review; overlap gate; abstract rendered; reviews spawned
- **13:05** Resumed by the Supervisor; Now rewritten. Definition of done: see *Now*.
- **13:06:47 Pre-registration committed** (f88de64) before any BTS-slice result. Then the BTS slice was range-read: 100 of 203.6 MB compressed, 6,058,425 rows, up to 2019-11-27 12:43 UTC.
- **Bug found and fixed before the results run:** pandas 3 infers microsecond timestamps; the slicer now casts to ns, and the loader auto-detects old files.
- **Real OBD results (pre-registered; `eval/results/obd_slice_summary.md`):**
  - Window: 84 h; 660,904 Random rows and 5,956,296 BTS rows.
  - (A1) The deployed BTS changed: 20/20 top cells moved ≥1.5× between 6-hour windows (median 16×).
  - (A2) Random→V(BTS): DR is within 0.1% (static prior) or 0.9% (hourly reconstruction) of the on-policy CTR, IPW within 1.1–1.6%. All intervals contain the truth. DM is off by 3.5–5.2% with an overconfident interval.
  - (A3, halves) Re-enacted deployment of BTS: the naive before/after is +1.62 per 1,000 vs a truth of +1.26 (+29%; naive's CI excludes the truth). DR gives +1.40 (consistent).
  - Rollback direction: naive is exactly right, DR is noisier.
- **Disclosed deviation** (whole days including 11-24): DR's interval missed the truth in 3/3 deploy-direction day pairs (2 distinct after-days; ESS/n down to 0.05%). Rollback direction 3/3 consistent.
- **Pre-registered balance check** flagged TVD ≈ 0.36. A POST-HOC diagnostic shows a labelling artefact: one category has a different hash in each file; the label-free TVD is ≤ 0.0044.
- **Verified first-party:** obp's OBD example evaluates the static ZOZOTOWN prior (`examples/obd/evaluate_off_policy_estimators.py`: `is_zozotown_prior=True`, single-round `compute_batch_action_dist`; `obp/policy/contextfree.py` line 18: "replicate the Bernoulli Thompson Sampling policy used in ZOZOTOWN production").
- **Decomposer review (`eval/results/decomposer_review.md`, SYNTHETIC):**
  - Drift sweep (13 levels): naive has the right sign for drift ≥ −0.25 and the wrong sign at ≤ −0.75. DR RMSE stays ≤ 0.006, while naive's reaches 0.262.
  - Feedback: DR tracks the direct effect, but the total effect is not identified (gap 5.7 points at feedback 1.0).
  - Misspecification along the mix axis: DM policy-term bias +1.58 points vs DR +0.09; DM-mix bias +0.57 vs DR-mix −0.01.
  - Shapley coverage 0.95.
- **Overlap gate** (`eval/gate_rule.json`, SIMULATOR ONLY; Supervisor's idea, refined):
  - Calibration bank: 36 configs × 20 seeds. The chosen rule (abstain if ESS/n < 5%) answers 47% of cases with 0.96 coverage; the worst config without the gate covers 0.65.
  - POST-HOC on OBD: 6/10 cases answered, 0 wrong; 3/3 DR failures abstained; 1 unnecessary abstention.
- **Abstract** rendered from `eval/results/headline.json` (885 words). `eval/check_docs.py` shows 0 untraced numbers in the abstract; the memo is pending. Architecture diagram v2 includes Shapley and the gate.
- **Child sessions spawned (2, the cap):** "P3 hostile judge (gpt-6-astra, max)" and "P3 code/eval reviewer (gpt-6-sol, max; reproduces the headline numbers)".

### 2026-10-04 13:52 IST — Product layer while the reviews run
- **C10 verdict** (`components/report/verdict.py`): worked / hurt / inconclusive / **can't tell**. Each off-policy cell is gated on the logs it comes from.
  - Both cells pass: decide on the Shapley term and report the interaction.
  - One passes: decide on that period's effect and say the interaction is not estimable.
  - Neither passes: can't tell.
  - Insight: on OBD every 2×2 needs one cell estimated from Thompson-sampling logs, which are greedy and fail the gate. So the Shapley term is never estimable there, while the single-ordering effect from the Random logs is.
- **Abstract wording fixed before review:** DR's interval in the deploy case (+1.40 ± 0.27 per 1,000) holds the truth, but also still contains the dashboard number (+1.62); the abstract now says so. Framing added: OPE supplies the control arm a difference-in-differences would need.
- **Added:** `deliverables/evidence-map.md` (criteria → evidence); `eval/demo_verdicts.py` (will run once the reviewer's OBD job finishes; one heavy job at a time). Tests: 13 pass.

### 2026-10-04 14:20 IST — Cross-model reviews processed; fixes applied; abstract v3
- **gpt-6-astra (hostile, max):** 59/100 (2.95/5), "would not shortlist this version". 14 issues (2 blockers). **gpt-6-sol (code, max):** all 44 abstract numbers reproduced byte-identically; 9 issues (2 blockers). All 23 items were accepted; some are partly done or deferred (`reviews/2026-10-04-dispositions.md`; `reviews/ledger.tsv`).
- **Fixes:**
  - Gate endpoints separated: S1 non-rejection vs reference-in-CI vs confident wrong sign; distinct instances counted. The 25 Nov rollback row now shows S1 passing while the CI misses the reference.
  - "0.1% accuracy" withdrawn.
  - Raw-label evidence for the balance flag: one category per feature carries a different raw label in each file with matching shares. Left UNRESOLVED; the OBD README calls the data an A/B test.
  - True ungated baseline. Fixed gate guards (zero rewards, non-finite diagnostics). Hidden-override V(before, new) truth fixed. Shapley environment interval added. DR mix residuals cross-fitted (decomposer review re-run; DR-mix bias −0.02 vs DM +0.57 points).
  - Hour-block bootstrap and DM refit, both post hoc: block intervals are wider, e.g. ±0.42 vs ±0.27 per 1,000 for the deploy case, and all references stay inside. DM consistency becomes yes once the model is refitted.
- **Pre-registered held-out gate validation** (commit d9de82e at 14:10:45, before results; 1,536 runs on unseen worlds 101/202 with positive, near-null and harmful effects, 10/40 actions, 5k/20k rows):
  - The gate answers 53%; coverage among answered 0.943 vs 0.914 ungated; coverage on abstained runs 0.882.
  - Confident wrong-sign answers: 0 with or without the gate, so the gate's decision benefit is not shown on these worlds.
  - Pre-registered criteria: met.
- **Abstract v3** (890 whitespace words; check_docs 0 untraced): separate estimands, approximate-target wording, gate endpoints and abstention on the flagship case, held-out result, explicit units, integration framing (Lee 2026 and OPEN cited after opening their arXiv records), dated milestones.
- **Re-score of v3 requested** from the same gpt-6-astra session.

### 2026-10-04 14:33 IST — Re-score 69/100; abstract v4; final memo; DONE
- **gpt-6-astra re-scored v3: 69/100** (3.45/5, up from 59). A1 and A2 are fixed, the original blockers are retired, and there are no new blockers. Two new major issues: A15 ("near-null" was a scorer-quality label) and A16 (the wrong-sign denominator included value rows).
- **Abstract v4** applies the judge's safe rewrites (897 words, 0 untraced numbers):
  - an approximate-target OBD comparison (4.936 vs 4.890 per 1,000);
  - the flagship deploy case shown with row-level and hour-block intervals, and the gate withholding the primary decision;
  - distinct-instance gate counts (5/8 answered, 4/5 hold the reference, 0/3 confident wrong signs);
  - the gate's design chronology;
  - holdout counts (818/1,536 answered; 771/818 vs 1,404/1,536 coverage).
- **Verdict contract** (`components/report/verdict.py`): one primary decision on the after-period contrast, otherwise "can't tell"; Shapley is secondary. Demo verdicts re-run: OBD deploy → cant_tell; rollback → hurt (reference inside the interval). The diagram uses "Monte-Carlo reference" and "noisy concurrent-arm reference" wording.
- **Final selection memo:** win 3, innovation 3, feasibility 5, demo 4, fit 3; mean 3.6. **Recommendation: P7 over P3, narrowly** (P7's hostile score 71 vs 69, fit 5 vs 3); P3 is the credible runner-up. `eval/check_docs.py`: PASS.
- **Deferred, with dates in Next:** A9 nuisance matrix; C8 OBD environment interval; A12 paired-DR baseline; A15 frozen near-zero test; held-out OBD campaigns.

### 2026-10-04 20:33 IST — Demo phase started (Supervisor 20:29)
- Read PLAYBOOK §11.
- **Licence check:** the GitHub repo st-tech/zr-obp is Apache-2.0 (code). The README inside the official dataset zip (read by HTTP range request) says "This dataset is licensed under CC BY 4.0". The zip's VERSION file reads "08/18/2020 Open Bandit Dataset 1.0". So a small aggregated extract can be committed, with attribution and a change notice.
- Spawned child session **"P3 demo builder"** (plan mode, notify always). Its kickoff has the full context, the crazy-element refinement (an exact real reference line for the α-mixture, plus a day selector), a pre-registration requirement for the knob analysis, the extract design (< 20 MB, a NOTICE file), the §11 deliverables and the honesty rules.

### 2026-10-04 21:03 IST — Demo plan approved
- **Builder's plan** (approved, with refinements): "the evaluator that says I don't know".
  - The α-knob runs on BTS logs with exact weights and a real A/B reference line, across 6 periods (W, W1, W2, Nov 24–26).
  - A Random-logs mirror uses the hourly reconstruction (approximate target).
  - IPW and SNIPW only; DR is left out because the full BTS action distribution isn't logged.
  - Extract: about 1 MB, CC BY 4.0, exact propensities, a manifest with checks against committed numbers.
  - Four panels: REAL ×3 (dashboard vs A/B; when logs can tell; the knob), then SYNTHETIC.
- **Pre-registered predictions** (from committed numbers, made before any knob computation). The z-test is α-invariant, so the gate refuses at every α>0 on Nov 25 and W1. On Nov 26 the gate answers up to α≈0.39 while IPW's interval misses the reference above α≈0.27 (honest "answered-miss" cells). On W2 the gate is conservative.
- **Refinements sent:** mirror reference labelled approximate; neutral explanation of z-test refusals; Nov 26 misses made prominent; Panel 1 rendered from headline.json; SCRIPT.md opens on real data; deterministic HTML; report P1–P5 outcomes.

### 2026-10-04 21:48 IST — Demo built; lead verification; review requested
- **Builder commits:** pre-registration 10209ca (21:07:33, before any knob computation) → extract aecbfa4 (0.76 MB, CC BY 4.0, exact propensities, NOTICE, manifest) → knob results 3919858 → page and tooling 228a683.
- **Knob results** (REAL, pre-registered; `demo/results/knob_summary.md`):
  - 31 of 33 predictions hit.
  - BTS logs: the gate's first abstention is at α 0.43 on W2 and 0.40 on Nov 26. On W, W1, Nov 24 and Nov 25 it refuses at every α>0, because the α-invariant mean-weight z is 4.5–6.1.
  - IPS answered with the reference outside its interval at 12 of 1,212 grid points, all on Nov 26 between α 0.28 and 0.39; the largest miss is 0.036 per 1,000. With hour-cluster intervals there are none.
  - Random logs: answered, with the reference inside, at all 606 points.
  - 403 refusals were unnecessary. The gate is conservative on greedy logs.
- **Lead verification from a clean checkout** (`eval/verify_demo_clean.sh`: a worktree at origin/main with no .data):
  - run.sh shows the first visual in 0.2 s; smoke.sh passes 23/23.
  - Rebuilding with a numpy-free python3.13 from a git archive (no .git) gives a byte-identical page.
  - Browser check (Playwright, served over localhost): no console errors.
- **Sent back to the builder:** at 1200 px the sheet-3 title block is cramped; check 1280/1440/1920.
- **Demo review requested:** the gpt-6-astra session was reused for the PLAYBOOK §11.7 "judge watching the demo" review.

### 2026-10-04 22:39 IST — Demo review (gpt-6-astra) and fixes in progress
- **Layout fix** a6f0c52, verified from a clean checkout: smoke 23/23; first visual in 0.1 s.
- **gpt-6-astra demo review** (bf9230b; pinned f58966c): wow 7, clarity 4, technical credibility 6, honesty 5 (out of 10). Verdict: "working real-data MVP: yes; top-three finals demo: no, as presented".
  - Blockers: D1, the A/B line called "true value"; D2, endpoints merged (Nov 26's paired E2 test still rejects after hour clustering; BTS-primary counts are 75/87 answered holding E1, 519/606 refused).
  - Majors: chronology overstated; "31/33" sold as fresh evidence; the 403 refusals over-read; a 500-word script for 3 minutes; script/screen state mismatches; ESS and z over-interpreted; simulator called "exact".
  - Minors: dynamic numbers lack hover sources; replay vs independent recompute conflated; one inconsistent fallback.
- All 12 accepted (`reviews/2026-10-04-dispositions.md`; ledger row). The fix list went to the builder: copy contract, E1/E2 side by side, BTS-primary counts, a 350–400-word script with presets and a timed rehearsal, source keys, re-captured fallbacks.

### 2026-10-04 23:37 IST — Demo fixes verified; PAUSED for the night
- The builder pushed 86540241 ("apply the gpt-6-astra review (D1–D12)"): 375-word script, rehearsal 2:52 with clicks, E1/E2 side by side, BTS-primary counts with an α>0 disclosure (69/81), fallbacks re-captured with states.json.
- Lead clean-checkout verification (`eval/verify_demo_clean.sh`, 23:36:10–23:36:15): run.sh 0.2 s; smoke **30/30 PASS**, including the new E2 assert at Nov 26 α 0.33 (difference CI −0.290 … −0.008), the fallback-state checks and the rehearsal check.
- **PAUSE (user directive, 23:36):** builder told to stop; temporary files cleaned; no DEMO DONE tonight. The resume point is in *Now*.
