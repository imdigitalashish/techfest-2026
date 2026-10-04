# Perceptron P5 · Market-impact-aware execution — Thought Node

> Journal for `perceptron-p05-impact-execution/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** Morning package delivered (07:45 IST). Phases 1–4 v0 done; Phase 5 (ratchet) is next. Still in Supervisor LEAN MODE.
- **Plan:** Make the spike real: (1) RNG-synchronised twins (C2) with NSR measured before/after; (2) a ghost-book estimator (C4) scored by RMSE vs the twin; (3) the agent ratchet on val seeds; (4) n = 200 test seeds for the abstract.
- **Doing:** E3 done (60 test seeds). E4 running: naive vs RNG-synchronised twins (TWAP, val seeds 100–129) to measure NSR. Lead alone.
- **Next:** (1) E4 → `eval/nsr.py E4_nsr_naive E4_nsr_sync`: does synchronisation cut the NSR? (2) If yes, rerun E3 with synced twins and n = 200. (3) Size sweep (square-root check). (4) Re-verify the UNVERIFIED company sources (LOXM, Aiden, BestEx, Proof, SEC 605) and the classics (Almgren–Chriss, Obizhaeva–Wang, Perold). (5) Independent rubber-duck pass on ADR 001 once sub-agents work again.
- **Needs from user:** Register by 15 Oct (after the 12 Oct selection). Teammates' names and skills (the abstract has placeholders).
- **Risks:** (1) **Twin decorrelation:** naive same-seed twins diverge (Δmid std 33¢ at 20 min vs 3–5¢ mean impact). Impact claims are noise-limited until C2 is fixed. (2) The agent's win so far comes mostly from the touch-limit tactic, not from impact-aware scheduling. Report it honestly; the ratchet must show schedule/feedback value. (3) Machine load (load avg 40–98 tonight) makes sims ~10× slower than idle. (4) ABIDES realism of impact is untested (square-root exponent unknown).

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
| C2 | twin_runner | TwinSpec → TwinPair | naive same-seed twins | ★ | ✅ naive; sync next | NSR = std/\|mean\| of Δmid(T1) |
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
- **Winnability: 3/5 (was 4 on 18 seeds; corrected at 08:00).** On 60 held-out seeds the agent cuts instantaneous cost by 35% (−0.043 bps [−0.051, −0.036]), but its total-IS gain vs TWAP is **not significant** (−0.06 [−0.44, +0.34]); VWAP: −0.18 [−0.42, +0.08]. The MV "measurably beats" is not yet met on total slippage. The path to meeting it is clear: the noise is the twin own-impact term, which the spike targets. It sits in Optiver's home domain. Against: "agent beats TWAP in a sim" is crowded (Karpe 2020, Hafsi & Vittori 2024, Olby et al. ICAIF 2025).
- **Innovation headroom: 4/5.** Spike = synchronised counterfactual twins plus a deployable ghost-book estimator. Evidence of headroom: naive twins decorrelate (std 33¢ vs 3–5¢ signal, E1), and I found no prior work fixing this in tonight's arXiv searches (absence UNVERIFIED beyond those). The twin-exact IS decomposition (drift/own impact/instant) is a crisp evaluation novelty.
- **Feasibility by the deadline: 5/5.** ABIDES runs on the M5 (0.9 s/day idle) with no GPU. Skeleton, twins, TCA, calibration and 3 policies were built overnight. Week-by-week plan avoids 19–25 Nov.
- **Demo strength: 4/5.** Side-by-side real book vs ghost book, live IS decomposition bars, "who absorbed our order" chart. Sim-only (no live market), but the judges asked for a simulator.
- **Fit with the user's strengths: 4/5.** Large-scale simulation (10⁴–10⁵ paired runs), systems engineering, a rigorous eval harness. Frontier models are optional (PPO challenger; MarS on Azure).
- **Biggest risk:** the only significant gain so far is instantaneous cost (book-walking avoidance; the touch-limit tactic alone gives −0.040 bps [−0.049, −0.032]). Total-IS and own-impact differences are noise-limited (±0.4 bps CI at n = 60) until twins are synchronised or n grows a lot. If synchronisation doesn't cut the noise, the MV claim needs ~10× more seeds (feasible on an idle M5: ~1 s/run).
- **One-line pitch:** *"We run twin markets, one with our order and one without, to measure our own footprint exactly and see who absorbs it, then train an execution agent to shrink it."* (No headline number yet: the total-IS gain is not significant at n = 60.)

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
