# Perceptron P10 · Trusting a signal extracted from messy, manipulated text — Thought Node

> Journal for `perceptron-p10-trusted-text-signal/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 0 — Brief (not started)
- **Plan:** _(lead fills)_
- **Doing:** _(what, and which agents/sessions)_
- **Next:** _(ordered)_
- **Needs from user:** Register by 15 Oct (after the 12 Oct selection). Teammates' names and skills for the team-fit section.
- **Risks:** _(lead fills)_

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** Perceptron Hackathon 2026 — IITB-Optiver AI Innovation Lab, Techfest IIT Bombay. Prize pool ₹2,00,000 for the top 3 teams overall.
- **Official statement:** [`_briefs/perceptron.pdf`](../_briefs/perceptron.pdf) (text: [`_briefs/perceptron.txt`](../_briefs/perceptron.txt)).
- **Rounds:** register by **15 Oct** → Round 1 abstract (600–900 words + optional 1-page architecture diagram, submitted once by the team leader) due **31 Oct** → shortlist **10 Nov** (25–30 teams across all 10 problems) → midway check **1 Dec** (1-page progress report, unscored) → finals **15–18 Dec** at IIT Bombay: a working build demonstrating the Minimum Viable scope (plus any stretch goals attempted), judged by Optiver and IIT Bombay professors; top 3 overall win.
- **Round 1 judging:** problem understanding & relevance 20% · technical soundness & feasibility 25% · innovation/novelty beyond the starter-resource baseline 20% · clarity & structure 10% · impact & rigor of the evaluation plan 15% · team fit & readiness (skill mix, week-by-week milestones) 10%.
- **The abstract must cover:** the problem and why · the core technical difficulty in our own words · a concrete approach naming techniques, models, datasets and tools · an explicit mapping to the Minimum Viable bullets · stretch goals · novelty vs the obvious baseline · the evaluation plan (metrics, baselines, datasets/simulators) · feasibility and risks.
- **Hard constraints:** students only, team ≤3; **one problem per team**; original work (not protected by patents or publications); queries only via the Techfest portal.
- **Round-1 deliverable for the morning package:** `deliverables/round1-abstract.md` (600–900 words) + `deliverables/architecture.md` (mermaid diagram).

**Problem 10 — Trusting a Signal Extracted from Messy, Manipulated Text** (Theme 6: AI You Can Actually Trust — teams choose Problem 9 or 10)
- **Context:** Decisions increasingly lean on signals from unstructured text alongside numeric data, but that text is noisy and sometimes manipulated.
- **Challenge:** Fuse text and time-series data into one signal and report a confidence bound on each prediction that's meaningful.
- **Starter resources:** A public financial news + price dataset (widely available on Kaggle), plus an existing conformal prediction library (e.g. MAPIE) instead of building calibration machinery from scratch.
- **Minimum Viable:** build a fusion model combining text sentiment and time-series signal; wrap predictions with an off-the-shelf conformal prediction method for confidence bounds.
- **Stretch goals:** test robustness under one adversarial or noisy-label scenario; check whether the confidence bounds are actually well-calibrated, not just present.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Data: FNSPID (financial news + stock prices), Kaggle "Daily News for Stock Market Prediction".
- Text models: FinBERT, FinGPT, LLM embeddings; fusion via late fusion or temporal models (e.g. TFT).
- Conformal under distribution shift: MAPIE, EnbPI, adaptive conformal inference (ACI / AgACI), conformal PID control.
- Manipulation and noise: adversarial text perturbations (TextAttack), bot/pump text, source-credibility weighting; calibration diagnostics (coverage, interval width, conditional coverage by regime).
- What companies ship: alternative-data and news-signal products from data vendors and quant funds (public material).

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
