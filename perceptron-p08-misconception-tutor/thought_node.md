# Perceptron P8 · A tutor that finds the real reason you're stuck — Thought Node

> Journal for `perceptron-p08-misconception-tutor/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 4 — walking skeleton built (contract tests 8/8 pass); evals + morning-package docs in progress. LEAN MODE (Supervisor, 05:45): no new sub-agents, small requests.
- **Plan:** Misconceptions as **executable bug switches** on one exact interpreter → (1) exact-likelihood diagnosis, (2) SymPy-verified *discriminative* item generation, (3) Bayesian tracer over *sets* of misconceptions across sessions with EIG item selection; evaluate on real Eedi data + simulated learners (labelled synthetic).
- **Doing (lead, sequential):** eval scripts (generation validity, diagnosis, simulation A/B) → landscape.md → components.md → ADR 001 → selection memo → round-1 abstract + architecture.md.
- **Next:** independent adversarial review of the spike (rubber-duck) once the network recovers; LLM bug-compiler on the Eedi catalogue; Eedi option-level data for real multi-session tracking.
- **Needs from user:** Register by 15 Oct (after the 12 Oct selection). Teammates' names and skills for the team-fit section. A Kaggle account login to download the official Eedi 2024 competition files (we use a community HF mirror meanwhile; fidelity UNVERIFIED).
- **Risks:** (1) synthetic-learner results only show the policy works under our assumptions; (2) the executable pack covers 5 arithmetic misconceptions, not Eedi's long tail (LLM retrieval covers that); (3) Eedi 2024 data via an unofficial mirror; (4) GitHub Models rate limits for the LLM baselines.

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** Perceptron Hackathon 2026 — IITB-Optiver AI Innovation Lab, Techfest IIT Bombay. Prize pool ₹2,00,000 for the top 3 teams overall.
- **Official statement:** [`_briefs/perceptron.pdf`](../_briefs/perceptron.pdf) (text: [`_briefs/perceptron.txt`](../_briefs/perceptron.txt)).
- **Rounds:** register by **15 Oct** → Round 1 abstract (600–900 words + optional 1-page architecture diagram, submitted once by the team leader) due **31 Oct** → shortlist **10 Nov** (25–30 teams across all 10 problems) → midway check **1 Dec** (1-page progress report, unscored) → finals **15–18 Dec** at IIT Bombay: a working build demonstrating the Minimum Viable scope (plus any stretch goals attempted), judged by Optiver and IIT Bombay professors; top 3 overall win.
- **Round 1 judging:** problem understanding & relevance 20% · technical soundness & feasibility 25% · innovation/novelty beyond the starter-resource baseline 20% · clarity & structure 10% · impact & rigor of the evaluation plan 15% · team fit & readiness (skill mix, week-by-week milestones) 10%.
- **The abstract must cover:** the problem and why · the core technical difficulty in our own words · a concrete approach naming techniques, models, datasets and tools · an explicit mapping to the Minimum Viable bullets · stretch goals · novelty vs the obvious baseline · the evaluation plan (metrics, baselines, datasets/simulators) · feasibility and risks.
- **Hard constraints:** students only, team ≤3; **one problem per team**; original work (not protected by patents or publications); queries only via the Techfest portal.
- **Round-1 deliverable for the morning package:** `deliverables/round1-abstract.md` (600–900 words) + `deliverables/architecture.md` (mermaid diagram).

**Problem 8 — A Tutor That Finds the Real Reason You're Stuck** (Theme 5: AI That Teaches — the theme's only problem)
- **Context:** Struggling with quant reasoning, math, or code usually isn't about missing facts — it's one specific misunderstanding producing the same class of mistake repeatedly.
- **Challenge:** Build a tutoring system that traces a learner's wrong answers back to a likely root misunderstanding and generates targeted follow-up problems.
- **Starter resources:** A public dataset of student errors (e.g. ASSISTments, or a coding-error dataset), or a small hand-built taxonomy of 3–5 common misconceptions if no dataset fits.
- **Minimum Viable:** classify a wrong answer into one of 3–5 misconception categories; automatically generate a new practice problem targeted at that category.
- **Stretch goals:** track a learner's misconceptions across multiple sessions; show some evidence the targeted problems actually reduce that error type over time.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Data: Eedi "Mining Misconceptions in Mathematics" (Kaggle, 2024 — wrong-answer distractors labelled with misconceptions), ASSISTments, EdNet, student coding-error datasets.
- Learner models: knowledge tracing via `pyKT` (BKT, DKT, SAKT, AKT and newer).
- Methods: LLM retrieval + rerank for misconception classification (see the Eedi winning solutions); generated problems verified by SymPy or code execution; simulated learners to test the "reduces errors over time" stretch.
- What companies ship: AI tutors from ed-tech companies and labs — check their published evaluations.

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

### 2026-10-04 02:05 IST — Phase 0 done, Phase 1 launched
- Brief verified against `_briefs/perceptron.txt` (matches the seeded Brief). What we must show: MVP = (a) wrong answer → one of 3–5 misconception categories, (b) auto-generated practice problem targeted at that category; stretch = cross-session tracking + evidence the targeted problems reduce that error type. Round 1 is plan-only (600–900 words); finals need a working build.
- Env: Apple M5, 24 GB, 70 GB free disk; Python 3.11 + uv; no Kaggle credentials; HF token present; GitHub Models API works (gpt-4.1-mini); Azure VS Enterprise subscription active (not needed so far).
- Found official Eedi data on HF: `Eedi/Eedi-Misconceptions-Graph` v1.0 (CC BY 4.0; 8,117 misconceptions, 2,258 constructs, updated 2026-09-16) and `Eedi/Question-Anchored-Tutoring-Dialogues-2k` (CC BY-NC). Kaggle Eedi 2024 data via community mirror `cdtmc/eedi-ir` (4,370 labelled question–distractor pairs, 2,587 misconceptions, 5 folds; no licence stated → research use only, fidelity UNVERIFIED).
- 7 research sub-agents launched.

### 2026-10-04 03:35 IST — Outage
Model API returned "408 Timed out reading request body" for most agents (network saturated; Supervisor confirmed portfolio-wide). 5 of 7 research agents died with no output; relaunched narrower ones that write incrementally. Lost ~85 min.

### 2026-10-04 05:45 IST — Skeleton up
- Assumption (recorded, not asked): MVP domain = school arithmetic with 5 categories linked to exact Eedi misconception names: LTR (Kaggle-2024 id 1507), SQ_DOUBLE (2316; graph 15012), SUB_NEG (2566), FRAC_ADD (217), NEG_TIMES_NEG (1597; graph 14310). Chosen because each is executable, frequent in Eedi's catalogue, and they produce *distinct* wrong answers on shared problem families.
- Built: contracts v0.1.1 (`architecture/contracts/`), bug pack (`components/bugs/school_math.py`: one exact interpreter + 5 composable bug switches), normaliser, SymPy verifier, template-discriminative generator, Bayes diagnoser + LLM zero-shot baseline, set-Bayes tracer with EIG, policies, simulated learners. `pytest components/tests` → 8 passed.
- Supervisor LEAN MODE received 05:45: no new sub-agents; sequential work; push every 30 min.
