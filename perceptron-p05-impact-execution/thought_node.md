# Perceptron P5 · Market-impact-aware execution — Thought Node

> Journal for `perceptron-p05-impact-execution/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** ⏸ **PAUSED by the user's decision (Supervisor, 09:55 IST, 4 Oct).** Only 3 projects run at a time; P7 is the current Perceptron pick unless the user overrides. Morning package delivered. Pre-registered H1 confirmed (E6). No jobs running; everything is pushed.
- **Resume point:** start with step (1). Heavy jobs one at a time under `nice -n 10`, run from `perceptron-p05-impact-execution/`.
  1. **Ratchet iteration 1 / E8 attribution ablation** (val seeds 100–139, synced). It crashed at ~09:50 with 8× `BrokenPipeError` in pool workers, probably killed under memory/CPU pressure; cause not yet diagnosed. Before rerunning, try `--workers 4`. Restart: `nice -n 10 .venv/bin/python components/execution_agent/autoresearch/eval.py eval/policies/e8_ablation.json --seeds 100:140 --workers 4 > /tmp/p5_ar1.out`. Then append one ledger row per candidate to `components/execution_agent/autoresearch/results.tsv` (keep rule in `program.md`). Arms: QP_only / IA_sched_only (legacy feedback) / IA_sched_fixed (`ref_mode=pre_trade`) / TWAP_legacy_fb vs TWAP.
  2. **E9 synced calibration (C4 metric):** `nice -n 10 .venv/bin/python eval/run_experiment.py --exp E9_calib_sync --seeds 0:40 --qty 4000 --policies eval/policies/calib.json --workers 4 --rng-sync per_wakeup && .venv/bin/python eval/calibrate.py --exp E9_calib_sync --out calibration_sync.json`. Compare OOS R² with E1 (naive: < 0).
  3. **E7 realism scorecard:** `for q in 1000 2000 4000 8000 16000; do nice -n 10 .venv/bin/python eval/run_experiment.py --exp E7_size_q$q --seeds 100:130 --qty $q --policies eval/policies/twap_only.json --workers 4 --rng-sync per_wakeup; done && .venv/bin/python eval/realism.py --qs 1000 2000 4000 8000 16000`. Fitted δ vs 0.5.
  4. Feedback-loop test: an rmsc04 variant with `num_momentum_agents=0` (does front-loading's advantage vanish?).
  5. An independent rubber-duck pass on ADR 001; per-component files from `research/components/innovation-candidates.md`.
- **Needs from user:** Register by 15 Oct if P5 is chosen at the 12 Oct selection. Teammates' names and skills (the abstract has placeholders).
- **Risks:** (1) The effect is small (−0.034 bps ≈ 10% of TWAP's controllable cost) and its mechanism is unattributed (QP schedule vs ~1.2× front-loading); E8 resolves it. (2) ABIDES impact realism (square-root law) is untested; E7 resolves it. (3) "Beats TWAP in a sim" is crowded prior art; our differentiator is the synchronised-twin instrument (7.5× tighter CIs) plus pre-registration.

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
_v1, 4 Oct 07:45 IST (final by 12 Oct). Each item scored 1–5 with one line of evidence._
- **Winnability: 4/5 (09:50: pre-registered result confirmed).** On 200 fresh test seeds with synced twins (E6), the propagator-optimised schedule beats TWAP: ΔIS −0.034 bps [95% CI −0.056, −0.013], one-sided p ≈ 0.0006; own impact −0.041 [−0.063, −0.020] (−19%). It sits in Optiver's home domain. Against: "agent beats TWAP in a sim" is crowded (Karpe 2020, Hafsi & Vittori 2024, Olby et al. ICAIF 2025), and our effect is small.
- **Innovation headroom: 5/5 (was 4).** Evidence since 08:12: synchronised twins cut the own-impact noise ~6× and paired-CI width 7.5× (E4/E5). Spike = synchronised counterfactual twins plus a deployable ghost-book estimator. Evidence of headroom: naive twins decorrelate (std 33¢ vs 3–5¢ signal, E1), and I found no prior work fixing this in tonight's arXiv searches (absence UNVERIFIED beyond those). The twin-exact IS decomposition (drift/own impact/instant) is a crisp evaluation novelty.
- **Feasibility by the deadline: 5/5.** ABIDES runs on the M5 (0.9 s/day idle) with no GPU. Skeleton, twins, TCA, calibration and 3 policies were built overnight. Week-by-week plan avoids 19–25 Nov.
- **Demo strength: 4/5.** Side-by-side real book vs ghost book, live IS decomposition bars, "who absorbed our order" chart. Sim-only (no live market), but the judges asked for a simulator.
- **Fit with the user's strengths: 4/5.** Large-scale simulation (10⁴–10⁵ paired runs), systems engineering, a rigorous eval harness. Frontier models are optional (PPO challenger; MarS on Azure).
- **Biggest risk:** the effect is small, ≈10% of TWAP's controllable cost (own impact 0.217 + instant 0.123 = 0.34 bps), and its mechanism is not yet attributed. Code review found that the feedback term acts as a ~1.2× front-loading, not a brake. Hypothesis to test: finishing early beats the delayed amplification of our selling by momentum agents, a feedback loop. E8 and agent ablations will settle it. ABIDES' impact realism (square-root law) is also untested. The ABIDES impact realism (square-root exponent) is still untested, so a judge could ask "is the impact physics even right?". Mitigation: the realism scorecard and a size sweep next.
- **One-line pitch:** *"We run twin markets, one with our order and one without, synchronised so their only difference is our footprint; then we train an execution agent to shrink it. First result: −19% own impact vs TWAP, pre-registered and confirmed on 200 fresh seeds."*

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
