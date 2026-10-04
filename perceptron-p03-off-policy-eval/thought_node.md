# Perceptron P3 · Did the policy actually work? (off-policy evaluation) — Thought Node

> Journal for `perceptron-p03-off-policy-eval/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** ▶ **RESUMED** 13:05 IST (Supervisor; batch slot freed by P1). Working to the Supervisor's definition of done (13:05).
- **Definition of done (Supervisor 13:05):**
  1. **Real OBD check**, with the analysis pre-registered before results: the BTS time-window slice; a drift test of the deployed BTS's logged propensities; a real before/after with real truth, in both directions.
  2. **Decomposer review fixes:** (a) a feedback/mix-shift knob; (b) the 2×2 Shapley decomposition plus the interaction term; (c) a misspecification test; (d) a drift sweep that shows where naive is right and where it is wrong.
  3. **Final abstract** rendered from committed results, plus a doc-drift check script and the architecture diagram.
  4. **Cross-model reviews** as child sessions: gpt-6-astra (max) as hostile judge; gpt-6-sol (max) on code/eval, including reproducing the headline numbers. Recorded in `reviews/` and `reviews/ledger.tsv`.
  5. **Final selection memo** (an honest case versus P7, P9, P1 and P4), thought node current, pushed, then "DONE — slot free".
- **Rules in force:** child sessions only (at most 2 at a time); never `git stash` or `--autostash`; start heavy jobs only when `kern.memorystatus_level` ≥ 30, under `nice -n 10`, one at a time, pausing below 25; keep network requests small.
- **Doing:** Step 1. Pre-registration first (`eval/preregistration_obd.md`), then the 100 MB BTS range-read on its own.
- **Next:** steps 2 → 3 → 4 → 5.
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
| C9 | Decomposer | before/after → `Decomposition` | naive gap | ★ | v0 done | RMSE + sign of the policy term |
| C10 | Report | → `Verdict` | dashboard number | | contract only | decision accuracy |
| C11 | Simulator | config → logs + `GroundTruth` | obp synthetic | | done (`components/simulator/sim.py`) | truth MC precision |
| C12 | EvalHarness | bank × seeds → metrics | obp evaluate | | v0 running | — |

## Selection memo
_First version due in the morning package (08:30 IST, 4 Oct); final by 12 Oct (a team can submit only one of the 10 Perceptron problems; the Supervisor ranks all 10 from these memos). Score each 1–5 with one line of evidence._
**v1 — 2026-10-04 07:35 IST** (synthetic-simulator numbers are labelled; evidence: `eval/results/`)
- **Winnability — 4/5.** The MVP has a crisp, checkable answer: exact ground truth in our simulator, and real ground truth in OBD (BTS on-policy CTR). A rigorous team can show numbers judges cannot argue with. The theme has a single problem. That Optiver judges reward counterfactual rigour is our hypothesis (UNVERIFIED).
- **Innovation headroom — 4/5.** The spike is a before/after Decomposer plus a Robustness Certificate (CI + MSM bounds + tipping point Γ\* for Δ). The obvious baseline only estimates V(π) with obp. Every piece has prior art (Δ-OPE, MSM, confidence sequences), but our arXiv search found no tool that attributes a policy switch this way. Agentic OPE-code optimisation is already published (GrowthHacker, Nov 2025), so we do not pitch the ratchet as novel.
- **Feasibility — 5/5.** CPU-only (numpy, scikit-learn). Overnight, under lean mode, we built the simulator, 5 estimators, intervals, MSM bounds and the decomposer. Nothing depends on a GPU or on the 19–25 Nov exam window.
- **Demo strength — 4/5.** A waterfall chart ("the dashboard said it failed; the season did it; the policy helped") and an interactive Γ slider. Less visually flashy than LLM or agent demos.
- **Fit with the user's strengths — 3/5.** It leans on statistics and causal inference more than large-scale systems or frontier models. Bridges: full-scale OBD (26M rows), streaming anytime-valid monitoring, and optional evaluation of LLM-generated policies.
- **Biggest risk:** being read as "a tutorial re-run of obp" or "a rigged simulator". Mitigation: the frozen bank includes cases where naive is right and where OPE fails (the hidden override), plus OBD real truth and a semi-synthetic OBD before/after.
- **One-line pitch:** "Your dashboard says the new policy failed. We show the season did it, the policy actually helped, and how much hidden confounding it would take to overturn that."

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
