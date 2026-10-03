# India @71/100 · Theme 2: Foundational learning outcomes — Thought Node

> Journal for `india71-t2-learning/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 1 — SOTA research (Phase 0 brief done; see *Phase 0 extraction* below).
- **Plan (to 08:30 IST):** research fan-out (8 agents) → component map + typed contracts → per-component innovation scan + six hats / adversarial / first-principles on spike candidates → ADR 001 → walking skeleton + eval harness on public data + labelled synthetic child data → first autoresearch ratchet on the spike → proposal draft + architecture diagram → fact-check → push.
- **Doing:** 8 background research agents: r1 official data (ASER/PARAKH/UDISE+/NIPUN/FLS) · r2 what is deployed today (VSK, Sunbird/cQube, state FLN apps, NGO/ed-tech) · r3 causal evidence (TaRL, diagnostic feedback, governance reform, data inflation) · r4 methods SOTA (IRT/CDM/CAT/linking/SAE/forensics/audits/ASR) · r5 governance & standards (NDEAR, APAAR, DPDP Rules, Ed-Fi/CASE) · r6 2025–26 news + X signal · r7 public datasets + fetch scripts · r8 international practice (Tusome/Tangerine, Ceará, Semáforo Escuela). Lead: drafting component map + contracts.
- **Next:** landscape.md synthesis → components.md → per-component research → ADR 001 → skeleton.
- **Needs from user:** Register by 15 Oct for one theme (after the 12 Oct selection). Teammates (≤4): names and skills.
- **Risks:** (1) public data granularity — PARAKH/ASER may not be downloadable below state/district level → mitigated by labelled synthetic child data calibrated to published aggregates; (2) "generic dashboard" trap — judges asked for a concrete architecture grounded in the datasets, so every component must name the dataset field it consumes; (3) hallucinated numbers — every number in deliverables must trace to `research/sources/*.md` or a committed run.

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
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|

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
