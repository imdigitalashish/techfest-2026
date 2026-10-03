# AI for Technology Readiness · TRL assessor — Thought Node

> Journal for `apctt-trl-assessor/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

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
- **Needs from user:** Register by 9 Oct (closes 10 Oct) — team of 1–3, everyone ≤35 on 17 Dec 2026. Forward the 10 Oct training guide and data into this Inbox as soon as they arrive.
- **Risks:** _(lead fills)_

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** AI for Technology Readiness — 2nd APCTT Hackathon 2026, by Techfest IIT Bombay with the Asian and Pacific Centre for Transfer of Technology (APCTT) of UN ESCAP. Prizes USD 2,000 / 1,500 / 1,500 + invitations to the APCTT Regional Flagship Showcase (travel covered). Indian teams compete alongside teams from the Philippines and South Korea.
- **Official statement:** [`_briefs/apctt.pdf`](../_briefs/apctt.pdf) (text: [`_briefs/apctt.txt`](../_briefs/apctt.txt)).
- **Objective (verbatim):** "To develop functional AI-powered, AI-assisted, or hybrid assessment tools capable of evaluating Technology Readiness Levels (TRL 1–9) from unstructured technical documentation, streamlining technology transfer workflows, and providing transparent, auditable evidence for innovation ecosystems across developing nations."
- **Challenge question (verbatim):** "How can an AI pipeline accurately parse raw technology documentation (e.g., patents, research papers, R&D reports), predict its correct Technology Readiness Level (TRL 1–9), synthesize supporting evidence, and output an auditable, actionable gap analysis to guide technology progression?"
- **Round 1 (online):** develop the model using approved public data sources → strict code/model freeze → organisers run it on an undisclosed private evaluation set. Max **3 submissions**: the first two return diagnostic feedback (runs/fails + benchmark scores); the third is the final, immutable entry. Deadline **15 Nov, 23:59 IST**.
- **Round 1 scoring (100% performance):** model ordinal accuracy & precision on the hidden set (primary) + strict pass/fail compliance on output schema, execution speed and dependency checks.
- **Round 2 (IIT Bombay, 16–17 Dec):** integrate the frozen model into an end-to-end system; on Day 2 process undisclosed live-challenge technology files, demonstrate usability, pitch to an expert panel. Finalists announced 1 Dec; technical check & integration rehearsal 2–11 Dec.
- **Rules:** no retraining, fine-tuning or model replacement after the freeze; undisclosed private API keys, hardcoded output schemas or plagiarism → immediate disqualification; finalists release the Stage 2 package under Apache-2.0 (pre-existing code and weights stay ours); unauthorised external AI tools banned in live rounds; team 1–3, everyone ≤35 on 17 Dec 2026; one team per person.
- **Unknown until 10 Oct:** detailed instructions, dataset guidelines, the assessment-criteria checklist and development samples — released only to registered teams. Design so we can adapt within hours: self-contained (open weights, runs offline), fast, schema-exact, robust to unseen document types.
- **Round-1 deliverable for the morning package:** `deliverables/approach.md` (pipeline, public-data plan, eval plan, 3-submission plan, 10-Oct adaptation checklist) + a baseline model with real eval numbers on a public labelled set.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- TRL definitions and rubrics: NASA, EU Horizon (General Annex), US DoD and DOE technology-readiness-assessment guides, ISO 16290, the AFRL TRL Calculator.
- Labelled public text: NASA TechPort project records (which carry TRL fields), EU CORDIS project reports, SBIR/STTR awards, patents (Google Patents, Lens), papers (arXiv, OpenAlex, Semantic Scholar). Confirm which sources count as "approved public data" once the guide lands.
- Methods: ordinal classification (CORAL/CORN, cumulative-link models); open-weight LLMs that run offline (Qwen3, Phi-4, Gemma 3, Llama) fine-tuned with LoRA via MLX or PEFT; evidence extraction with citations; rubric-mapped gap analysis; calibration.
- What companies ship: technology-scouting and IP-analytics platforms, and published research on automated TRL estimation.

## Key decisions
- _(none yet)_

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|

## Selection memo
_First version due in the morning package (08:30 IST, 4 Oct); final by 12 Oct (portfolio prioritisation). Score each 1–5 with one line of evidence._
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
