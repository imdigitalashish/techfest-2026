# Perceptron P3 · Did the policy actually work? (off-policy evaluation) — Thought Node

> Journal for `perceptron-p03-off-policy-eval/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 1–4, compressed. LEAN MODE (Supervisor, 05:50 IST): no sub-agents or downloads over 200 MB before 08:30; the lead works alone.
- **Plan:** Morning package in the Supervisor's order: (a) this node → (b) `research/landscape.md` → (c) `architecture/components.md` + contracts → (d) ADR 001 → (e) selection memo → (f) `deliverables/round1-abstract.md` + `architecture.md` → (g) a walking skeleton on a ground-truth simulator, plus the small Open Bandit Dataset sample if it is reachable.
- **Doing:** Lead, alone: primary-source reads via the arXiv API and GitHub API (small requests), then writing.
- **Next:** landscape → components → ADR → memo → abstract → skeleton numbers.
- **Needs from user:** Register by 15 Oct (after the 12 Oct selection). Teammates' names and skills for the team-fit section.
- **Risks:** Saturated network (all 8 research sub-agents died at 0 turns on HTTP 408). Mitigation: sequential, small requests. The full Open Bandit Dataset is too big to download tonight, so tonight's real-data numbers use only the small sample bundled with obp.

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

### 2026-10-04 02:05 IST — Phase 0 done; research fan-out launched
- Read `PLAYBOOK.md`, this brief and `_briefs/perceptron.txt` (verified: problem text, MVP and stretch bullets, rounds, judging weights and dates match the seeded brief).
- What we must be able to show, from the judging weights: (1) the crux in our own words: the policy changes the data and the world drifts, so a before/after number confounds the policy's effect with trend, mix shift and selection (20%); (2) a valid estimator with stated assumptions — overlap, logged propensities, no unmeasured confounding — plus a feasible plan (25%); (3) something beyond "run IPW/DR from obp" (20%); (4) an evaluation that proves the claim — ground truth from a simulator and the OBD Random→BTS protocol, coverage of intervals, bias of the naive number (15%).
- Created the folder layout and a uv venv (`.venv`, Python 3.11; numpy 2.4.6, scipy 1.17.1, pandas 3.0.6, scikit-learn 1.9.1, pydantic 2.13.5; installed offline from the uv cache because PyPI downloads timed out).
- Spawned 8 research sub-agents (R1 estimators, R2 uncertainty, R3 confounding, R4 code and datasets, R5 companies, R6 feedback loops, R7 social signal, R8 trading and competition intel).

### 2026-10-04 05:55 IST — All 8 research agents failed; switching to lean mode
- Every sub-agent failed at 0 turns with `408 Timed out reading request body`, so no research files were produced. The network is saturated across the portfolio.
- Supervisor's lean-mode directive (05:50) received: no sub-agents, small requests, nothing over 200 MB, push every 30 minutes. Plan reordered to match. Research is now done directly: arXiv API and GitHub API records saved under `research/sources/`.
