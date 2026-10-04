# Perceptron P5 · Market-impact-aware execution — Thought Node

> Journal for `perceptron-p05-impact-execution/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 0 done → 1 (research) + 4 (skeleton), in Supervisor LEAN MODE (05:51 IST): no sub-agents, small requests, no downloads > 200 MB.
- **Plan:** Morning package in the order a→g: thought node → `research/landscape.md` → `architecture/components.md` + contracts → ADR 001 → selection memo → `deliverables/round1-abstract.md` + `deliverables/architecture.md` → ABIDES skeleton + paired-seed eval (TWAP/VWAP vs impact-aware agent), if the Python env installs.
- **Doing:** Lead alone, sequentially.
- **Next:** Install the minimal ABIDES runtime (numpy/pandas/scipy plus a local `pomegranate` shim), then write the landscape from primary sources while sims run.
- **Needs from user:** Register by 15 Oct (after the 12 Oct selection). Teammates' names and skills for the team-fit section.
- **Risks:** (1) Network saturation: all 6 research sub-agents died at 0 turns with 408s and the first pip install timed out. (2) ABIDES pins 2021-era deps (numpy 1.22, pandas 1.2.4, pomegranate 0.14.5, gym 0.18, ray 1.7), so installing on Python 3.11/arm64 is risky; mitigation: skip gym/ray, shim pomegranate. (3) RL agents that "beat TWAP" often win only by capturing the spread, which Optiver judges will spot. So we report the decomposition: spread vs impact vs timing.

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
- _(none yet)_

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|

## Selection memo
_First version due in the morning package (08:30 IST, 4 Oct); final by 12 Oct (a team can submit only one of the 10 Perceptron problems; the Supervisor ranks all 10 from these memos). Score each 1–5 with one line of evidence._
- **Winnability:**
- **Innovation headroom** (the spike, and why it beats the obvious baseline):
- **Feasibility by the deadline** on an M5 Mac (+ Azure), around the 19–25 Nov exams:
- **Demo strength** at the finals:
- **Fit with the user's strengths** (large-scale systems, frontier models):
- **Biggest risk:**
- **One-line pitch:**

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
