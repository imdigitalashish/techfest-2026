# India @71/100 · Theme 2: Foundational learning outcomes — Thought Node

> Journal for `india71-t2-learning/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 2–4 overlapping — component map + contracts done; builders running; spike selection in progress.
- **Plan (to 08:30 IST):** builders A+B finish skeleton + eval harness → ADR 001 (six hats + antithesis + first principles) → landscape.md from research files → round-1 proposal + architecture.md → first autoresearch ratchet on C5 → fact-check → push.
- **Doing:** builder-a (simulator, C2 canonical, C3 competency, C4 diagnostics, C7 teacher view, C12 governance) · builder-b (C5 trust/audit spike candidate, C6 small-area estimation, C9 allocation, C10 dashboard, eval harness, autoresearch scaffold) · data-extractor (ASER 2024 + PARAKH 2024 tables → `data/public/`) · r2a national DPI (VSK, Sunbird, DIKSHA, APAAR) · r2b states & NGOs · r1n UDISE+/NIPUN targets · r3n causal evidence · r4n SAE/forensics/audit methods · antithesis (rubber-duck) + first-principles on the spike. Original r1/r3/r5/r8 still running since 02:50 (likely stuck in API retries).
- **Next:** ADR 001 → landscape.md → proposal → autoresearch loop → fact-check.
- **Needs from user:** Register by 15 Oct for one theme (after the 12 Oct selection). Teammates (≤4): names and skills.
- **Risks:** (1) **model API outage** 03:00–05:00 IST (408 "timed out reading request body" across sessions) killed r2, r4, r7 and stalled others; mitigated with narrow, append-as-you-go re-runs; (2) public data granularity — PARAKH state/district report pages returned 403 from this network; ASER 2024 district estimates exist as PDFs → demo uses labelled synthetic child data calibrated to published aggregates; (3) "policing teachers" framing risk for the audit spike — under adversarial review; (4) every number in deliverables must trace to `research/sources/*.md` or a committed run.

## Phase 0 extraction (from `_briefs/india71.txt`, verified 4 Oct 02:10 IST)
**Hard constraints**
- Round 1 (due **1 Nov**): proposal ≤ **6 pages**, A4, 1-inch margins, Arial ≥ 11 pt, single PDF `India71_100_[Team ID].pdf`, via the official Google Form (no email). Sections: Team info · Problem identification · Evidence & context · Existing ecosystem · Proposed solution · Expected impact.
- Expected: "a concrete technical architecture - a data pipeline, diagnostic or analytics engine, or decision-support platform - grounded in these existing datasets, and not a generic ed-tech pitch". Must engage with ≥ 1 of: (1) governance & standardisation, (2) point-of-use decision support, (3) policy-monitoring feedback loops.
- Team ≤ 4, cross-institute OK, **one theme per team, fixed at registration (closes 15 Oct)**. Solutions must be original, "not protected by patents, copyrights, or publications". Queries only via the Techfest portal *Doubt* section.
- Shortlist 8 Nov (top 10 per theme). Finals 16–18 Dec at IIT Bombay: 10-min presentation + 5-min jury Q&A covering problem validation & stakeholders, ecosystem, detailed solution, roadmap, feasibility, scalability, impact assessment.

**Judging criterion → what we must be able to show**
| Criterion | Evidence we must produce |
|---|---|
| Problem identification | One precise, *measurable* scorecard-vs-reality gap for a named underserved group, quantified from official + independent data (ASER 2024, PARAKH 2024, UDISE+). |
| Evidence & context | Cited numbers from primary reports; causal evidence on what converts data into learning (TaRL, diagnostic-feedback RCTs, data-inflation audits). |
| Existing-ecosystem analysis | Map of what is deployed (VSKs, UDISE+, DIKSHA/Sunbird, APAAR, state FLN apps, NGO tools) and *evidenced* reasons the gap persists. |
| Proposed solution | Architecture diagram + typed component contracts + a working demo with real numbers; name the dataset field each component consumes. |
| Feasibility & roadmap | Plugs into existing VSKs / Samagra Shiksha processes and staff (teacher, CRC, BRC, DIET, SMC); costed pilot → state → national path; risks. |
| Impact & scalability | Beneficiaries counted from UDISE+; impact range from cited effect sizes; simulation with stated assumptions; scale via DPGs and VSKs. |

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** The India @71/100 Challenge — Techfest IIT Bombay. Prize pool ₹1,00,000.
- **Official statement:** [`_briefs/india71.pdf`](../_briefs/india71.pdf) (text: [`_briefs/india71.txt`](../_briefs/india71.txt)).
- **Challenge question (verbatim):** "Identify one measurable gap between India's development scorecard and the lived reality of an underserved group (including socially marginalised groups) within one of the three competition themes, and design a solution that could be realistically implemented and scaled in the real world."
- **Round 1 — due 1 Nov:** a proposal of **at most 6 pages** (A4, 1-inch margins, Arial ≥11 pt, single PDF named `India71_100_[Team ID].pdf`, via the official Google Form): team info · problem identification (the gap and the underserved community) · evidence & context · existing-ecosystem analysis (why the gap persists) · proposed solution · expected impact. A **concrete technical architecture** (data pipeline, decision-support model or platform design) is expected — not a policy recommendation alone. No prototype required. Top 10 teams per theme shortlisted on **8 Nov**.
- **Round 2 — 16–18 Dec at IIT Bombay:** 10-min presentation + 5-min jury Q&A covering problem validation & stakeholders, ecosystem analysis, detailed solution, implementation roadmap, feasibility, scalability and impact assessment.
- **Judging:** problem identification · evidence & context · existing-ecosystem analysis · proposed solution · feasibility & implementation roadmap · impact & scalability.
- **Rules:** students, team ≤4 (cross-institute allowed); **one theme per team** (fixed at registration, by 15 Oct); original work.
- **Round-1 deliverable for the morning package:** `deliverables/round1-proposal.md` (fits 6 pages when rendered) + an architecture diagram. A small working demo of the architecture is a bonus that will strengthen the finals.

**Theme 2 — Foundational Learning Outcomes.** Problem (verbatim): "From a data governance and policy-implementation perspective, design a technologically robust intervention that converts India's existing school data ecosystem (UDISE+, ASER, PARAKH, state assessment systems) into a decision-support system aligned with the NIPUN Bharat/FLN policy mandate." Engage with at least one of:
1. **Data governance & standardisation** — how should attendance, assessment and learning-level data be standardised and made interoperable across UDISE+, state assessment platforms and classroom-level tools so a teacher, block official and state administrator see a consistent picture?
2. **Decision-support at point of use** — how can existing data be surfaced as an actionable, low-bandwidth tool for teachers to identify and remediate specific learning gaps, rather than remaining a compliance report?
3. **Policy-monitoring feedback loops** — how should PARAKH/ASER-style diagnostic data feed back into resource allocation, teacher training or School Management Committee decisions at block or district level?

The statement expects a concrete technical architecture grounded in these datasets — "not a generic ed-tech pitch". Suggested sources: ASER 2024, PARAKH Rashtriya Sarvekshan 2024, UDISE+, NEP 2020, NIPUN Bharat (2021), DIKSHA.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Vidya Samiksha Kendras (state education command centres); APAAR ID; Teaching at the Right Level (Pratham / J-PAL evidence).
- Item response theory for diagnostics; offline-first delivery to teachers (WhatsApp, IVR, SMS).
- What others ship: state FLN dashboards and ed-tech/NGO tools in use in government schools — find published evaluations.

## Key decisions
- _(none yet)_

## Components
Full specs: [architecture/components.md](architecture/components.md) · contracts: [architecture/contracts/fln_contracts.py](architecture/contracts/fln_contracts.py)

| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | Source connectors | sources → raw rows + Provenance | state ETL / VSK ingestion | no | spec | ingest validation pass rate |
| C2 | Canonical model & identity | raw → School/Student/Response | Ed-Fi/CEDS-style, UDISE+/LGD codes | no | building (A) | validation pass rate; linkage F1 |
| C3 | Competency framework & crosswalk | docs/items → Competency/Item (Q-matrix) | SCERT expert mapping | no | building (A) | κ vs expert Q-matrix |
| C4 | Diagnostic engine | Responses → ChildDiagnosis | ASER highest-level rule | candidate | building (A) | level accuracy; items to P≥0.9 |
| C5 | Trust & audit engine | reported results → TrustAssessment | ad hoc third-party checks | **proposed** | building (B) | block MAE (pp) at 10 % audit budget |
| C6 | Linking + small-area estimation | TrustAssessment + anchors → AreaEstimate | direct averages | candidate | building (B) | block RMSE; CI coverage |
| C7 | Teacher point-of-use | ChildDiagnosis → TeacherPlan | state apps / chatbots | no | building (A) | payload bytes; SMS segments |
| C8 | CRC visit planner | AreaEstimate + trust → VisitPlan | rota | no | spec | need-weighted coverage |
| C9 | Allocation & policy feedback | AreaEstimate → AllocationDecision | enrolment-proportional | candidate | building (B) | expected extra children vs oracle |
| C10 | Dashboards | estimates → HTML/JSON | VSK dashboards | no | building (B) | disclosure pass rate; KB |
| C11 | Action ledger & outcome loop | ActionRecord → effects | none | no | spec | % actions with outcome in 6 wks |
| C12 | Governance & access | AccessRequest → AccessDecision | role portals | no | building (A) | policy suite pass rate |

## Selection memo
_First version due in the morning package (08:30 IST, 4 Oct); final by 12 Oct (the team registers for one theme by 15 Oct). Score each 1–5 with one line of evidence._
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

### 2026-10-04 02:50 IST — Phase 0 done; Phase 1 fan-out
Read PLAYBOOK, the seeded brief and `_briefs/india71.txt`; extracted hard constraints and the criterion → evidence map (above). Toolchain checked: Python 3.11, uv, pdftotext, numpy/pandas/scipy/sklearn/pydantic; Azure subscription enabled (not needed yet). Launched 8 background research agents (r1–r8, see *Now*). Assumption (overnight, no user input): we engage all three engagement areas, with governance/standardisation as the spine, because it is what makes the other two trustworthy; to be confirmed by ADR 001.

### 2026-10-04 05:15 IST — Outage recovery; Phase 2 contracts + component map; builders launched
Model API timed out (HTTP 408) for ~2 h across many sessions: r2 (deployed today), r4 (methods) and r7 (datasets) failed, though r4 and r7 left usable files (`research/sources/methods-sota.md`, `datasets-agent-notes.md`) and r7 downloaded ASER 2024 (full report), PARAKH 2024 Grade 3 report and the PARAKH technical report into `.data/raw/`. Wrote typed contracts (`architecture/contracts/fln_contracts.py`, 19 JSON Schemas) and the 12-component map (`architecture/components.md`, five "breaks" between a recorded number and a changed outcome: commensurability, trust, granularity, actionability, closed loop). Launched builders A and B, a local-file data extractor, narrow re-runs (r1n, r2a, r2b, r3n, r4n) and the antithesis + first-principles agents on the spike. Assumption: proposed spike = C5 trust & audit engine pending ADR 001.
