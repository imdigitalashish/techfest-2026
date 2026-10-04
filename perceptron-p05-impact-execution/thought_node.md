# Perceptron P5 · Market-impact-aware execution — Thought Node

> Journal for `perceptron-p05-impact-execution/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** ▶ **DEMO phase** (Supervisor 21:47 IST, PLAYBOOK §11). Updated 2026-10-04 21:49 IST.
- **Plan:**
  1. Spawn one demo-builder child session. It proposes the "crazy" element; the lead approves it before it builds.
  2. Build to §11: `demo/run.sh`, baseline side by side with a judge knob, SIMULATED labels on every screen, numbers from committed results, `demo/SCRIPT.md`, `demo/fallback/`, `demo/smoke.sh`.
  3. One gpt-6-astra demo review, recorded in `reviews/`.
  4. The lead verifies from a clean checkout, then sends "DEMO DONE".
- **Doing:** the demo is built (ef608074) and verified by the lead from a clean worktree. The gpt-6-astra demo review (child session) is running. Updated 2026-10-04 22:26 IST. Updated 2026-10-04 21:54 IST.
- **Earlier phase (definition of done, met 14:08):** see the Log.
- **Delivered:**
  - E8, E7, E9, E10, E11 and E12, each pre-registered by commit time.
  - Final Round-1 abstract v1.1 (`deliverables/round1-abstract.md`, 895 words) and diagram (`deliverables/architecture.md`), both rendered from `eval/claims.py`. `eval/check_docs.py` OK; pytest 7/7.
  - Cross-model reviews in `reviews/`: gpt-6-astra 2.80 → 3.25 → **3.45/5**; gpt-6-sol reproduced H1 and H2 bit-for-bit; 34 issues, all accepted.
  - Selection memo (below): **recommend against P5**.
- **Resume plan (if P5 is picked or resumed):**
  1. Realism gate: calibrate the rmsc04 agent mix to external, pre-declared targets (square-root exponent, permanent fraction) with held-out checks; MarS as the fallback.
  2. Diagnose the 13% spread widening under the coupling (try per-message keying).
  3. A pre-registered total-IS test on untouched seeds.
  4. The counterfactual-mid estimator: state-dependent kernel; per-seed R².
  5. Implement the paired candidate-vs-incumbent search; then PPO.
- **Needs from user:**
  - Register by 15 Oct only if P5 is picked on 12 Oct (the memo recommends against it).
  - Teammates' names and skills. Without them, Round 1 must narrow to a solo scope (astra v1.1 note).
- **Risks:** sub-tick effects; the starter simulator's impact law; a coupling that alters spreads.

### Phase 0 — what we must be able to show (from the Round-1 rubric)
- Crux (20%): the agent's own trades move the price it later pays (transient + permanent impact, book resilience, other agents' reactions), so slippage is endogenous; a replay backtest can't see it.
- Soundness (25%): a named simulator (ABIDES rmsc04), named baselines (TWAP, VWAP, Almgren–Chriss), a named impact model, and a fully specified metric (implementation shortfall in bps vs the arrival mid, with forced completion).
- Novelty (20%): beyond "PPO beats TWAP": exact counterfactual twins (same seed, with vs without our order) used as ground truth for impact, and an impact estimate the agent can deploy.
- Evaluation (15%): paired seeds (common random numbers), disjoint train/val/test seed sets, 95% bootstrap CIs, risk metrics (std, CVaR), and an IS decomposition.
- Team fit (10%): week-by-week milestones that avoid 19–25 Nov.

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** Perceptron Hackathon 2026 — IITB-Optiver AI Innovation Lab, Techfest IIT Bombay. Prize pool ₹2,00,000 for the top 3 teams overall.
- **Official statement:** [`_briefs/perceptron.pdf`](../_briefs/perceptron.pdf) (text: [`_briefs/perceptron.txt`](../_briefs/perceptron.txt)).
- **Rounds:** register by **15 Oct** → Round 1 abstract (600–900 words + optional 1-page architecture diagram, submitted once by the team leader) due **31 Oct** → shortlist **10 Nov** (25–30 teams across all 10 problems) → midway check **1 Dec** (1-page progress report, unscored) → finals **15–18 Dec** at IIT Bombay: a working build demonstrating the Minimum Viable scope (plus any stretch goals attempted), judged by Optiver and IIT Bombay professors; top 3 overall win.
- **Round 1 judging:** problem understanding & relevance 20% · technical soundness & feasibility 25% · innovation/novelty beyond the starter-resource baseline 20% · clarity & structure 10% · impact & rigor of the evaluation plan 15% · team fit & readiness (skill mix, week-by-week milestones) 10%.
- **The abstract must cover:** the problem and why · the core technical difficulty in our own words · a concrete approach naming techniques, models, datasets and tools · an explicit mapping to the Minimum Viable bullets · stretch goals · novelty vs the obvious baseline · the evaluation plan (metrics, baselines, datasets/simulators) · feasibility and risks.
- **Hard constraints:** students only, team ≤3; **one problem per team**; original work (not protected by patents or publications); queries only via the Techfest portal.
- **Round-1 deliverable for the morning package:** `deliverables/round1-abstract.md` (600–900 words) + `deliverables/architecture.md` (mermaid diagram).

**Problem 5 — Market-Impact-Aware Execution Strategy** (Theme 3: Markets & Trading Intelligence — teams choose one of Problems 4, 5, 6)
- **Context:** A firm's own large orders move the market it's trying to trade in, so naive models overstate expected returns.
- **Challenge:** Build an execution agent that reduces slippage compared to a standard baseline by accounting for its own market impact.
- **Starter resources:** An open market simulator (e.g. ABIDES).
- **Minimum Viable:** implement a TWAP/VWAP baseline; build one agent (rule-based, heuristic, or simple RL) that measurably beats the baseline on slippage in the simulator.
- **Stretch goals:** explicit counterfactual modeling of "what the book would look like without our order"; multi-step feedback-loop analysis.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Simulators: ABIDES / ABIDES-Gym (JPMorgan), mbt_gym, and any newer open market simulators.
- Impact models: Almgren–Chriss, Obizhaeva–Wang, propagator / transient impact, the square-root law; implementation-shortfall metrics.
- Agents: RL execution (PPO/DQN) with impact-aware state; counterfactuals via paired simulations with and without our order on identical seeds (a natural route to the stretch goal).
- What practitioners ship: execution-algo research from brokers and trading firms (public papers and talks).

## Key decisions
- 2026-10-04 13:21 IST: **Time stamps come from `TZ=Asia/Kolkata date` / git commit times only** (Supervisor; PLAYBOOK §6). Earlier labels are corrected in `eval/preregistration.md`.
- 2026-10-04 13:21 IST: **Confirmatory claims rest on strictly pre-registered fixed-n blocks (E10/H2).** E6/H1 is "registered after launch, before inspection"; E3/E5 are exploratory; E8 is validation.
- 2026-10-04 13:21 IST: **Wording per the reviews:** "counterfactual-mid estimator (prototype)", not "ghost book"; "conditional simulator counterfactual / CRN coupling", not "exact"; "pre-trade mids match at 1-s sampling", not "bit-identical"; the E6 arm is "QP + front-loading, market orders".
- 2026-10-04 13:21 IST: **Docs are rendered from templates** (`eval/render_docs.py`); `eval/check_docs.py` must pass before DONE.
- 2026-10-04: **Simulator = ABIDES rmsc04** (`jpmorganchase/abides-jpmc-public` @ f9cbe51), run on Python 3.11 + numpy 2.2 + pandas 2.3 with a 40-line `pomegranate` shim (same mixture, the agent's own RNG). No gym/ray. Assumption: shim draws are not bit-identical to pomegranate 0.14.5; the distribution is the same.
- 2026-10-04: **Task:** SELL 4,000 shares, 09:35–09:55, 40×30-s slots, forced completion; ≈12% of window volume. Metric = IS bps vs the arrival mid; paired vs TWAP with a bootstrap CI. Seeds: train 0–99 / val 100–199 / test 1000–1199.
- 2026-10-04: **Counterfactual twins:** the null twin appends a zero-quantity copy of our agent, so the latency model and all background RNG streams are identical (verified bit-identical pre-trade, 80/80).
- 2026-10-04: **Spike = synchronised twins (C2) + ghost-book impact model (C4)**. See [ADR 001](architecture/adr/001-spike.md). MV agent = propagator-QP + own-impact feedback + touch-limit tactic.

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | sim_env | WorldSpec → WorldResult | ABIDES rmsc04 | | ✅ | realism scorecard (δ, decay) |
| C2 | twin_runner | TwinSpec → TwinPair | naive same-seed twins | ★ | ✅ naive + sync (NSR 4.7 → 1.4) | NSR = std/\|mean\| of Δmid(T1) |
| C3 | market_state | BookSnapshot+fills → Features | L1 quotes | | partial | R² → next-slot cost |
| C4 | impact_model | Features+fills → ImpactEstimate | exp. propagator | ★ | ✅ v0 (OOS R² < 0) | ghost-book RMSE vs twin |
| C5 | scheduler | ParentOrder+ImpactParams → Schedule | TWAP/VWAP/AC | | ✅ | model cost; ΔIS |
| C6 | child_order_tactics | SlotTarget+book → ChildOrder[] | market order | | ✅ | instant cost bps |
| C7 | execution_agent | PolicySpec → fills | ABIDES-Gym env | | ✅ | completion 100% |
| C8 | tca | TwinPair → EpisodeMetrics | Perold IS | | ✅ | identity error = 0 |
| C9 | eval_harness | ExperimentSpec → CSV/summary | unpaired mean | | ✅ v0 | CI half-width |
| C10 | feedback_attribution | TwinPair → Attribution | none | | ✅ v0 | conservation residual |
| C11 | learner | results.tsv → PolicySpec | grid | | ⏳ | val ΔIS |
| C12 | demo_ui | results → app | — | | ⏳ | — |

## Selection memo
<!-- memo:begin (rendered from deliverables/selection-memo.template.md; edit the template) -->
_v3 (final for the 12 Oct pick unless new evidence arrives). Rendered from `deliverables/selection-memo.template.md` by `eval/render_docs.py`. Numbers come from `eval/results/` and `reviews/ledger.tsv`; `eval/check_docs.py` checks them. Comparisons with other projects come from their own memos on `main`, read on 4 Oct._

**Bottom line: I recommend _against_ P5 as the team's single Perceptron problem**, unless the user specifically wants a trading-domain entry for the Optiver judges. P5 has an unusually rigorous evaluation (pre-registration with timestamps, replication, two cross-model reviews, independent reproduction) but no confirmed result:
- Its minimum viable claim ("an agent that measurably beats TWAP") failed its strictly pre-registered replication.
- The starter simulator's impact physics makes that claim hard to earn.

| Criterion | Score | Evidence |
|---|---|---|
| Winnability | **2/5** | E6 beat TWAP by 0.034 bps [0.013, 0.056] (n = 200). It did not reproduce on validation seeds (E8: +0.006). The strictly pre-registered replication was **not confirmed** (E10, n = 400: -0.013 [-0.029, +0.003]). Pooled over the fixed-size test blocks (n = 600, descriptive): -0.020 [-0.032, -0.007] bps, i.e. 0.20¢/share. The hostile judge (gpt-6-astra) scored the draft 2.80/5 and the latest final abstract 3.45/5. |
| Innovation headroom | **3/5** | Common random numbers are classical. Our part is an ABIDES evaluation discipline: synchronised twins (own-impact dispersion ÷6, paired-difference std ÷7.7, but spreads 13% wider under the coupling), a per-seed decomposition, a realism gate, and replication. The counterfactual-mid estimator failed its held-out test (seed-averaged R² 0.15 / -0.02; per seed 0.010 / -0.004). |
| Feasibility by the deadline | **4/5** | Everything runs on the M5 (CPU only). 4,450 treatment–twin pairs are committed. An independent model (gpt-6-sol) reproduced the headline rows bit-for-bit. What is still needed is research: a realistic-impact market or a better tactic, so the timeline risk sits in science, not engineering. |
| Demo strength | **3/5** | Twin markets side by side and net-inventory shifts by agent type (value agents' net inventory rises by 102% of our shares) are visual. But the pooled effect is 0.20¢ per share against a 1¢ tick, and the registered impact-vs-size slope is 1.01 [0.55, 1.76] rather than the square-root law's δ ≈ 0.5. |
| Fit with the user's strengths | **4/5** | Simulation at scale, reproducibility and systems engineering fit; RL and market-microstructure depth would have to come from teammates. |

- **Biggest risk:** sub-tick effects in a simulator whose impact law is unrealistic. Optiver judges will ask "so what?", and today the answer is the instrument rather than an agent.
- **What would change my mind:** a realism-gated market (square-root-like, partly permanent impact) in which the same pipeline shows a replicated gain over TWAP and VWAP. We estimate 2–3 weeks of work, with no guarantee.
- **Versus the other candidates** (their memos on `main`): P10, P7 and P1 self-score winnability 4, each reporting a measured win in its own memo (P10: coverage held under injected documents; P7: a pre-registered demand-shock comparison; P1: per-device loss reductions under federated LoRA). P9 and P4 self-score 3. On evidence, P5 belongs below P10, P7 and P1.
- **One-line pitch (if chosen anyway):** *"Before claiming to beat TWAP, measure your own footprint: twin markets show how much of our cost we caused, and a pre-registered replication shows that our scheduling gain is not yet distinguishable from zero."*
<!-- memo:end -->

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 02:05 IST — Phase 0 read; research fan-out; ABIDES cloned
- Read PLAYBOOK, the seeded brief and `_briefs/perceptron.txt`. The brief matches the official text for Problem 5 (MV: TWAP/VWAP baseline plus one agent that beats it on slippage; stretch: counterfactual book, feedback loops).
- Spawned 6 research sub-agents (papers · simulators · companies · social/competitions · data/empirics/eval · counterfactual/feedback). **All 6 failed at 0 turns** with "408 Timed out reading request body", so no output.
- Cloned `jpmorganchase/abides-jpmc-public` into the gitignored `.cache/` (HEAD `f9cbe51`, last commit 2023-12-13, BSD-3). Read `abides-markets/abides_markets/configs/rmsc04.py`: 1 exchange, 1000 noise, 102 value, 2 adaptive market makers, 12 momentum agents, 09:30–10:00. Each agent's `RandomState` seed is drawn in sequence from the global `np.random` after `np.random.seed(seed)`. At runtime only the oracle's megashock draws use the global RNG. So appending our agent *after* the background agents leaves every background agent's random stream unchanged, which allows exact paired counterfactuals. One caveat: `config_add_agents` re-draws the latency model, so both twins must add an agent (ours vs a null agent).
- The first `uv pip install` timed out (network).

### 2026-10-04 05:51 IST — Supervisor: LEAN MODE
No sub-agents until 08:30; small requests; push at least every 30 min. Proceeding sequentially in the order a→g.

### 2026-10-04 07:45 IST — Morning package (lean mode, solo)
- **Built** (`components/`, `eval/`, `tests/`): ABIDES adapter + pomegranate shim (`sim_env`), counterfactual twins (`sim_env/twins.py`), ABIDES `ExecutionAgent` + pure policies TWAP/VWAP/PROBE/IA (`execution_agent`), TCA with an exact twin decomposition (`tca`), exponential propagator fit (`impact_model`), experiment runner, calibration and a paired-CI summariser (`eval/`). Unit tests: 4 passed (`.venv/bin/python -m pytest -q tests`).
- **Env:** `.venv` = `python3.11 -m venv --system-site-packages` (numpy 2.2.6, pandas 2.3.3, scipy 1.17, pydantic 2.12); `scripts/fetch_abides.sh` pins ABIDES f9cbe51.
- **E1 calibration (train seeds 0–39; TWAP + PROBE; SELL 4,000):** `.venv/bin/python eval/run_experiment.py --exp E1_calib_train --seeds 0:40 --qty 4000 --policies eval/policies/calib.json --workers 8`, then `.venv/bin/python eval/calibrate.py --exp E1_calib_train`.
  - Twins are bit-identical pre-trade in 80/80 runs.
  - Mean Δmid(own impact) is +1.5¢ @60 s and +3.2¢ @300 s, but its std is 4.7 / 8.5 / 33 / 64¢ at 60 s / 5 / 20 / 30 min (decorrelation).
  - Kernel fit: τ = 60 s, g_tr = 0.0059¢/sh, g_perm = 0.0022¢/sh; OOS R² < 0 on 20 held-out train seeds.
  - TWAP IS −0.09 bps (drift −0.32, own +0.12, instant +0.11); E1 is for calibration, not claims.
- **E3 test (seeds 1000–1059, in progress):** `.venv/bin/python eval/run_experiment.py --exp E3_test --seeds 1000:1060 --qty 4000 --policies eval/policies/test.json --workers 9`. Preliminary summary on the 18 finished seeds: `.venv/bin/python eval/summarize.py --exp E3_test --from-pkl`.

  | policy | IS bps | paired ΔIS vs TWAP | win |
  |---|---|---|---|
  | TWAP | 1.376 | — | — |
  | VWAP | 1.035 | −0.34 [−0.83, +0.11] | 67% |
  | IA_full | 0.778 | **−0.60 [−1.12, −0.10]** | 67% |
  | IA_sched_only | 0.952 | −0.42 [−0.89, +0.10] | 72% |
  | TWAP_touch_limit | 0.757 | −0.62 [−1.11, −0.14] | 78% |

  Twin-measured own impact (approx.): TWAP 0.71 bps vs touch-limit 0.12 bps and IA 0.15 bps.
- **Docs:** `research/landscape.md` (≈33 arXiv abstracts opened via the API plus 5 web sources; companies I couldn't open are marked UNVERIFIED), `research/components/innovation-candidates.md`, `architecture/components.md` + `architecture/contracts/contracts.py`, `architecture/adr/001-spike.md`, `deliverables/round1-abstract.md` (899 words incl. headings), `deliverables/architecture.md`.
- **Assumptions:** ABIDES ExchangeAgent writes `./log/<dir>`; we give each run a unique dir (a parallel-run race crashed E3 once; fixed). `log/` is gitignored.

### 2026-10-04 08:00 IST — E3 final (60 test seeds): **the preliminary 18-seed claim does not hold** (correction)
- Command: `.venv/bin/python eval/run_experiment.py --exp E3_test --seeds 1000:1060 --qty 4000 --policies eval/policies/test.json --workers 9` (2,557 s under load ~90). Summary: `.venv/bin/python eval/summarize.py --exp E3_test` → `eval/results/E3_test_summary.md`. Feedback table → `eval/results/E3_test_feedback.md`.
- Integrity: pre-window identical in 300/300 runs; all policies filled 4,000/4,000; share-conservation residual 0.
- **Paired ΔIS vs TWAP (bps, 95% bootstrap CI):**
  - IA_full −0.056 [−0.441, +0.339], win 52%.
  - IA_sched_only −0.050 [−0.407, +0.336].
  - TWAP_touch_limit −0.086 [−0.447, +0.288].
  - VWAP −0.180 [−0.420, +0.081].
  - TWAP mean IS is 0.402 bps (std 3.08).
- **Significant component:** instantaneous cost. IA_full −0.043 bps [−0.051, −0.036] (−35% vs TWAP's 0.124); touch-limit −0.040 [−0.049, −0.032]. The own-impact component dominates the noise (Δ CIs ≈ ±0.4 bps).
- **Feedback (stretch 2, v0):** value agents absorb our selling, +5,314 shares [+3,502, +7,134] under TWAP. Momentum agents *tend* to amplify it (−1,302 [−3,185, +636] under TWAP vs −81 under touch-limit), but that is **not significant**.
- **Correction:** the 07:45 entry and the first Supervisor message quoted −0.60 bps [−1.12, −0.10] on 18 seeds. With 60 seeds that effect is not significant. Abstract and memo are updated, and the Supervisor is told.
- Started E4: naive vs `per_wakeup` twins (TWAP, val 100–129) → NSR. The sanity check passed on seed 5: synced null is bit-identical to itself, pre-trade identical to the treatment, and fill 4,000.

### 2026-10-04 08:12 IST — Spike C2 works: synchronised twins cut own-impact noise ~6× (variance ~35×)
- E4: TWAP, val seeds 100–129. Commands:
  - `.venv/bin/python eval/run_experiment.py --exp E4_nsr_naive --seeds 100:130 --qty 4000 --policies eval/policies/twap_only.json --workers 5 --rng-sync naive`
  - the same with `--exp E4_nsr_sync --rng-sync per_wakeup`
  - then `.venv/bin/python eval/nsr.py E4_nsr_naive E4_nsr_sync` → `eval/results/nsr_E4_nsr_naive_vs_E4_nsr_sync.md`.
- Twin gap Δmid (¢), mean / std, naive → synced:

  | time | naive | synced |
  |---|---|---|
  | 300 s | +3.03 / 6.34 | +0.93 / 4.87 |
  | 600 s | +0.00 / 14.29 | +2.30 / 4.13 |
  | 1,200 s | +4.83 / 22.94 | +3.67 / 5.29 |
  | 1,800 s | −7.25 / 46.37 | −2.08 / 16.26 |

  At 60 s the synced std is *higher* (4.77 vs 2.83); unexplained so far, to investigate.
- **NSR at the end of execution (1,200 s): 4.7 → 1.4.** Own-impact term in IS: std **0.971 → 0.164 bps** (≈5.9× smaller, ≈35× less variance).
- Instant cost (0.130 vs 0.129 bps) and window volume (34.4k vs 33.9k) are unchanged. That is a first check that re-keying doesn't change the market's marginal behaviour; the full realism scorecard is still to do.
- Pre-window identical in 30/30 (naive) and 30/30 (synced).
- Started E5: `.venv/bin/python eval/run_experiment.py --exp E5_test_sync --seeds 1000:1060 --qty 4000 --policies eval/policies/test.json --workers 9 --rng-sync per_wakeup`.

### 2026-10-04 08:30 IST — E5: synchronised twins on the same 60 test seeds (fixed policies, no tuning)
- Command: `.venv/bin/python eval/run_experiment.py --exp E5_test_sync --seeds 1000:1060 --qty 4000 --policies eval/policies/test.json --workers 9 --rng-sync per_wakeup` (689 s). Summary: `eval/results/E5_test_sync_summary.md`; component CIs: `eval/results/E5_test_sync_components.md`.
- Paired ΔIS vs TWAP: CI half-width ≈ ±0.05 bps (vs ±0.39 naive in E3, 7.5× tighter).
  - **IA_sched_only −0.050 [−0.100, −0.003]**; its own impact is −0.044 [−0.086, −0.002] (TWAP's own impact 0.273 bps → 0.230, −16%).
  - IA_full −0.017 [−0.069, +0.035]: instant −0.039 [−0.050, −0.030], drift +0.017 [+0.001, +0.032].
  - TWAP_touch_limit −0.026 [−0.067, +0.015]: instant −0.040, drift +0.020.
  - VWAP −0.017 [−0.053, +0.019].
- Reading: the impact-aware *schedule* (propagator QP + own-impact feedback) is what reduces own impact. The touch-limit tactic saves spread but resting orders delay fills (worse timing) and don't reduce own impact. **Caveat:** 4 comparisons; with Bonferroni (α = 0.0125) nothing is significant, and IA_sched_only was singled out after seeing E5.
- **Pre-registered H1** (written before E6 results): on fresh test seeds 1060–1259 (n = 200) with synced twins, IA_sched_only has mean paired ΔIS vs TWAP < 0 (one-sided α = 0.05, bootstrap). Secondary: own_impact Δ < 0. Policies are frozen as in `eval/policies/confirm.json`. Command: `.venv/bin/python eval/run_experiment.py --exp E6_confirm_sync --seeds 1060:1260 --qty 4000 --policies eval/policies/confirm.json --workers 9 --rng-sync per_wakeup` (reniced to 10).
- Supervisor 08:22 (Inbox via message): package and correction accepted; lean mode lifts at 08:30 with limits (≤ 2 sub-agents; heavy jobs one at a time under nice 10). E5 reported in the memo and abstract as asked.

### 2026-10-04 09:25 IST — Code review (sub-agent) and source verification (sub-agent)
- **Code review: one real bug.** In `ImpactAwarePolicy`, the feedback compared pre-trade own impact with the *post*-trade steady state. At average-rate trading, excess = e^{−dt/τ} − 1 ≈ −0.39, so the "slow down while displaced" rule almost never braked (0.02–0.04% of 4,560 decisions in E3/E5). In practice it was a ~1.2–1.3× systematic speed-up.
  - Consequence: E3/E5 numbers are valid measurements *of the code as written*, but the "impact-aware feedback" explanation was wrong. IA_sched_only = propagator-QP schedule + systematic front-loading. E6 (pre-registered) tests the same frozen policy, so it stays a valid test of that policy, but not of the feedback idea.
  - Fix: `ref_mode="pre_trade"` (steady-state excess = 0, unit-tested). The legacy `post_trade` stays the default so the E3–E6 configs reproduce exactly. E8 (val seeds) will separate the QP schedule, the legacy speed-up and the corrected feedback.
- **Checked correct by the review:**
  - Twins diverge only after our first order (global RNG use, deterministic latency, message/order-id ties).
  - `_synchronise_rng` closures and wrapper binding; no seed collisions in 1000–1259.
  - Fill attribution: no overfill, cancel processed before the query.
  - TCA identity to 1.2e-5 bps; sign conventions; paired bootstrap; train/test seed disjointness; no leakage.
- **Source verification:** all items are recorded in `research/raw/source-verification-2026-10-04.md`.
  - Almgren–Chriss (*J. Risk* 3(2)) and Obizhaeva–Wang (*JFM* 16(1)): verified at primary.
  - Gatheral 2010 and Gatheral–Schied–Slynko 2012: verified via Crossref (no arXiv versions).
  - Perold 1988 (*JPM* 14(3), 4–9): bibliographic record only.
  - BestEx "Pulse" futures impact model (Sep 2025) and Proof "Rejecting the Black Box" (Oct 2021): verified.
  - LOXM: press only (MIT Tech Review, 2017).
  - SEC Rule 605: adopted 6 Mar 2024; compliance extended to 1 Aug 2026.
  - `landscape.md` is updated accordingly.
- `inst_cost` = 0.005 ¢/share² (frozen) is checked by `eval/derive_inst_cost.py`: derived 0.00486 from E1.

### 2026-10-04 09:50 IST — E6: pre-registered H1 **confirmed** on 200 fresh test seeds
- Command: `.venv/bin/python eval/run_experiment.py --exp E6_confirm_sync --seeds 1060:1260 --qty 4000 --policies eval/policies/confirm.json --workers 9 --rng-sync per_wakeup` (4,453 s, nice 10). Verdict: `eval/results/E6_H1_verdict.md`; summary: `eval/results/E6_confirm_sync_summary.md`.
- Integrity: 200 seeds, pre-window identical in all runs, all filled.
- **IA_sched_only vs TWAP:**
  - ΔIS −0.0340 bps, two-sided 95% CI [−0.0563, −0.0127], one-sided upper bound −0.0160, P(boot ≥ 0) = 0.0006, win rate 52%.
  - Own impact −0.0414 [−0.0629, −0.0204]: TWAP 0.217 → 0.176 bps (−19%).
  - Instant ±0.004; drift +0.0075 [−0.0007, +0.0156].
- IA_full (+ touch-limit): ΔIS −0.015 [−0.044, +0.016]. Instant −0.042 [−0.047, −0.038], but drift +0.026 [+0.018, +0.035]: resting orders lose on timing.
- VWAP: −0.016 [−0.040, +0.008].
- The code-review report is saved verbatim at `eval/results/code-review-2026-10-04.md`. It confirms the twins, RNG sync, fills, TCA identity, statistics and leakage, and finds the feedback-reference bug. So the confirmed effect = **propagator-QP schedule + ~1.2× front-loading**, not "braking while displaced".
- New feedback-loop hypothesis (untested): front-loading wins because momentum agents amplify our selling with a lag (E3: momentum Δpos −1,302 under TWAP, not significant), so finishing earlier trades ahead of it. Test: E8 arms, plus an rmsc04 variant with momentum agents removed.

### 2026-10-04 09:58 IST — Paused (user's decision via Supervisor, 09:55)
- Ratchet iteration 1 (`components/execution_agent/autoresearch/eval.py`, frozen 09:55 before first use; synced twins; val seeds 100–139) **crashed**: 8× `BrokenPipeError` in multiprocessing workers, no results. `results.tsv` therefore has no rows yet. The exact restart commands (with `--workers 4`) are in *Now → Resume point*.
- Supervisor 09:40 (lean mode again) and 09:55 (pause) handled: no sub-agents were running (code review and source verification had finished; both outputs are saved). No background jobs remain. Everything is committed and pushed.

### 2026-10-04 13:00 IST — Resumed (Supervisor 12:52); 09:50 crash diagnosed; E7/E8/E9 pre-registered
- Supervisor resume message handled (definition of done, rules and machine limits are in *Now*). New PLAYBOOK rules read: §4 (child sessions only, ≤ 2), §6 (never `git stash` / `--autostash`), §10 (cross-model reviews + `reviews/ledger.tsv`).
- **Crash diagnosis** (ratchet iteration 1, 09:44–09:51):
  - The parent died **without a Python traceback** (`/tmp/p5_ar1.err` has 8 tracebacks, all `BrokenPipeError` from 4 pool workers failing to send results back). The output file is empty, so the parent was killed by a signal, not by an exception.
  - The system log for 09:43–09:53 shows no memory (jetsam) kill of any python process, and ~8 GB still available, so memory pressure is unlikely.
  - Likely cause: the parent was launched as a plain `&` child of a tool shell that was later torn down. E4–E6 were launched as `( … &)` orphans or with the tool's async mode, and all survived. A diagnostic pair of `sleep 1800` jobs (plain vs subshell) is running to test this.
  - Remedy either way: run via the tool's attached async mode with `--workers 4` under nice 10, through `run_experiment.py`, which writes per-seed pickles incrementally (the frozen ratchet `eval.py` prints only at the end).
- Pre-registered E8 (attribution: QP main effect, front-loading main effect, interaction, corrected-feedback increment; val seeds 100–199), E7 (δ vs 0.5 with a seed-bootstrap CI; decision rule) and E9 (synced kernel OOS R² > 0) in `eval/preregistration.md`. Committed before any run.

### 2026-10-04 13:07:19 IST — Timestamp correction (Supervisor 13:06)
The Supervisor spotted journal and registration times running ahead of git. Audit of every Log header against the commit that first contains it:

| Header label | Commit time |
|---|---|
| 07:45 | 07:42:37 |
| 08:12 | 08:11:15 |
| 08:30 | 08:26:53 |
| 09:50 | 09:43:35 |
| 09:58 | 09:52:27 |
| 13:00 | 12:53:49 |

Those labels were estimates, 1–7 min ahead of the clock. The other headers are earlier than their commits, as they should be.

**H1 caveat found during the audit:** the H1 registration was committed at 08:26:53, ≈ 3 min after E6 launched, and the first E6 seed file was written at 08:25:21. No E6 output was read before the run finished, but H1 is now classified as "registered after launch, before inspection". E10 (registered 13:01:50, first seed 13:05:11) is the strict confirmatory test. Correction table: `eval/preregistration.md` (end). From now on every time comes from `TZ=Asia/Kolkata date`.

### 2026-10-04 13:21 IST — E7/E8/E9 done; both cross-model reviews in; amendment A1; templates
- **E8** (pre-registered; val 100–199; synced): IA_sched_only vs TWAP is +0.0056 [−0.0284, +0.0393], so the E6 effect was not reproduced. All attribution contrasts are unresolved (`eval/results/E8_ablation_val_attribution.md`).
- **E7** realism: δ = 1.01 [0.55, 1.76] (75% of draws valid). The registered rule says "consistent", but only because it was too lenient. Post hoc, resolved-size δ = 0.87 [0.57, 1.35], with no detectable permanent impact (`eval/results/realism_scorecard.md`). So ABIDES rmsc04 impact is near-linear and fully transient, which is why schedules barely matter.
- **E9:** on the registered split (fixed after review sol #1), held-out R² is +0.15 (TWAP) and −0.02 (PROBE); RMSE 5.0¢ vs 19.7¢ for naive twins. Criterion not met.
- **Reviews** (`reviews/ledger.tsv`):
  - gpt-6-sol reproduced 12/12 rows bit-for-bit; 7 issues, all accepted.
  - gpt-6-astra scored the draft 2.80/5 (56/100); 16 issues, all accepted (#16 is blocked on the user's teammates).
- **Amendment A1** (commit 8b85e29, 13:13:18, before E10 results): signed attribution labels with a ±0.02 bps equivalence margin, an interaction rule, and descriptive pools E6∪E10 and E5∪E6∪E10.
- **E11/E12 pre-registered** (commit 50c5be6). Shell-substitution defects fixed twice (5744e5b and A1's dollar figures); doc text is now written only with quoted heredocs or the edit tools.
- **Crash root cause:** undetermined. Ruled out: a Python exception, a memory kill (no log entry), tool-shell teardown (plain-`&` sleeps survived 19 min).

### 2026-10-04 13:44 IST — E10/E11/E12 done; final abstract rendered (898 words)
- **E10** (strict replication, n = 400, fresh seeds 1260–1659): **H2 NOT confirmed.** ΔIS −0.0127 [−0.0283, +0.0027], one-sided upper bound +0.0004.
  - Under amendment A1, the QP schedule's own-impact effect is detected (−0.0136 [−0.0252, −0.0022]); its IS effect is unresolved.
  - Front-loading, the interaction and the corrected feedback are negligible (within ±0.02 bps).
  - Pooled over E6∪E10 (n = 600, descriptive): −0.020 [−0.032, −0.007] bps, ≈ 0.20¢/share.
  - Synced feedback: value agents absorb 102% of our shares; momentum agents end at +70 [−60, +204]. The naive-twin "momentum amplifies" story vanishes, so the momentum-ablation stretch is deferred.
- **E11:** the coupling preserves volume and trade counts (±10%) but **widens mean spreads 13%** [2%, 26%]. Return volatility and depth are unresolved. Disclosed in the abstract.
- **E12:** exact event-level pre-trade identity in 180/180 runs. The touch-cap saving is fill-price improvement (−0.041 [−0.046, −0.036]), not decision-to-fill movement; the delay term is small and adverse.
- **Deliverables:**
  - `deliverables/round1-abstract.md` is rendered from its template; MV item 2 says "not yet met on total slippage", per the registered rule.
  - `deliverables/architecture.md` is rendered and status-tagged.
  - The selection memo is templated: **recommendation against P5** as the single Perceptron pick (winnability 2/5).

### 2026-10-04 13:59 IST — Final reviews in; abstract v1.1; claims hardened
- **gpt-6-astra final re-score of v1.0: 3.25/5 (65/100)**, up from 2.80. Nine items, all accepted and fixed in v1.1:
  - removed the post hoc "near-linear ⇒ TWAP near-optimal" inference;
  - same-arm E12 accounting (touch arm net ΔIS +0.001 [−0.032, +0.033]);
  - descriptive attribution wording with the ±0.02 bps margin;
  - "top-of-book event logs" scope;
  - seed-averaged vs per-seed R²;
  - "no momentum amplification was detected";
  - incumbent search marked [planned];
  - model-conditional counterfactual and externally anchored calibration targets.
- **gpt-6-sol follow-up:**
  - Reproduced E10 H2 (−0.012651 [−0.028501, +0.002586]) and the E6∪E10 pool; 2 rerun seeds matched 10/10 rows.
  - Six items, all accepted:
    - atomic rendering;
    - claims recomputed from CSVs (attribution, E11; E7 cross-checked);
    - the registered 10k seed-sorted bootstrap everywhere (H2 upper bound +0.0002, still not confirmed);
    - count-like integers traced;
    - review scores wired from the ledger;
    - top-of-book wording.
- `eval/check_docs.py`: 237 claims, 86 placeholders, no drift, no untraced numbers. Pytest 7/7 (includes the docs-drift test).
- Selection memo (rendered): **recommend against P5** as the single Perceptron pick. Scores: winnability 2, innovation 3, feasibility 4, demo 3, fit 4.

### 2026-10-04 14:08 IST — DONE: definition of done met; slot released
- gpt-6-astra re-scored the final abstract v1.1 at **3.45/5**, with no remaining blocker or major overclaim (`reviews/2026-10-04-abstract-v1.1-gpt-6-astra.md`, 070287c). Its two disclosed gaps are accepted: one is in the resume plan, the other in *Needs from user*.
- Final gates: `eval/check_docs.py` OK (237 claims, 86 placeholders); pytest 7/7; no P5 jobs running.
- Reviewer child sessions are finished and their work is on `main`; they are being archived to free machine resources.

### 2026-10-04 21:49 IST — Demo phase started (Supervisor 21:47)
§11 read. Supervisor's suggestion: the "ghost market", same-seed twins with and without our order, with an order-size knob, the naive-vs-synchronised contrast, and an honest E6→E8→E10 ending. **Assumption:** P5 has no real market data, so every screen is labelled SIMULATED (ABIDES). The only real-world anchors are cited literature values (the square-root law, δ ≈ 0.5, from the Tokyo Stock Exchange survey), shown as labelled references, not as our results.

### 2026-10-04 21:54 IST — Demo design approved
- **Builder's proposal (child session):** one offline page, every screen stamped SIMULATED (ABIDES rmsc04).
  - Act 1, the ghost market: two same-seed books side by side; the ghost twin translucent; a pre-trade identity badge; the shaded gap is our footprint, with an order-size knob (E7) and a log-log impact panel against the real-world square-root reference.
  - Act 2: naive vs synced spaghetti (E4: 6×, 7.7×; the coupling's +13% spreads footnoted).
  - Act 3: TWAP | impact-aware | ghost on one seed, with the IS split.
  - Act 4: honest forest plot (E6 → E8 → E10; pooled marked descriptive).
  - Live lane: "bring your own seed" through a stdlib server under the memory guard. I timed a fresh synced twin pair at 3.9 s.
- **Approved with 8 amendments**, aligned with the hostile-judge fixes:
  - an exact identity-scope label;
  - no "fails" (say "roughly linear vs ≈0.5; realism gate needed");
  - "net inventory", not "who took the other side";
  - a single-seed noise caption;
  - E6/E8/E10 status labels;
  - "1 new seed (live)";
  - a headless `DEMO_NO_OPEN=1` READY line;
  - a source footnote on every panel.

### 2026-10-04 22:26 IST — Demo built (ef608074); lead verification from a clean worktree of origin/main
- **Without the setup step:** `DEMO_NO_OPEN=1 demo/run.sh` prints READY (http://127.0.0.1:8650/) about 1 s after launch. `demo/smoke.sh` passes in 1 s; the live lane is skipped with its reason ("ABIDES not fetched").
- **After the README setup** (venv + `scripts/fetch_abides.sh`), `demo/smoke.sh` passes in 4 s, including a live run: seed 101 in 3.4 s; pre-trade top-5 identity 304/304 (TWAP) and 304/304 (impact-aware); T1 gaps −8.0¢ / −7.0¢ equal the committed `E7_size_q4000.csv` / `E8_ablation_val.csv` rows.
- **Wording audit** (grep of index.html and SCRIPT.md): all 8 approval amendments present; no "took the other side", "vanish", "fails", "absorb", "bit-identical", "certified", "beats TWAP" or "ghost book".
- **Labelling:** SIMULATED stamped in the sticky header and on every chart canvas; 13 "source:" footnotes.
- **Fallback:** 8 screenshots in talk order.
- The verification server was stopped after use. The clean worktree is at `/tmp/p5_clean_demo_check` (to be removed after the review).
