# India @71/100 · Theme 1: Maternal & early-childhood nutrition — Thought Node

> Journal for `india71-t1-nutrition/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 1–2 (SOTA research running in parallel with component map + contracts). Started 02:05 IST, 4 Oct.
- **Plan (to 08:30 IST):** (1) 8 research agents → `research/sources/R*.md` → `research/landscape.md`; (2) component map + typed contracts (`architecture/`); (3) per-component research + six hats / adversarial / first-principles → ADR 001; (4) walking skeleton on WHO standards + SYNTHETIC cohort, eval harness with real numbers; (5) round-1 proposal + architecture diagram; (6) first auto-research loop on a spike.
- **Doing:** research agents R1 gov systems · R2 law & standards · R3 evidence & numbers · R4a early-warning SOTA · R4b data quality / linkage / privacy SOTA · R5 deployed today · R6b social signal (retry) · R7b data sources (retry). Lead: Phase 0, WHO tables (done), components + contracts.
- **Next:** landscape.md → components.md + contracts → builders → ADR 001 → proposal draft.
- **Needs from user:** Register by 15 Oct for one theme (after the 12 Oct selection). Teammates (≤4): names and skills. (Probable) DHS Program account for NFHS-5 microdata — details to follow from R7b.
- **Risks:** no public Poshan Tracker microdata (demo relies on SYNTHETIC data; real-data validation becomes a pilot item) · research-agent timeouts (2 already failed; relaunched narrower) · proposal must fit 6 A4 pages.

## Phase 0 — what the judges must be able to see (from `_briefs/india71.txt`)
| Criterion (official) | What we must show | Evidence we will produce |
|---|---|---|
| Problem identification | One measurable gap + one named underserved group | Survey-vs-admin wasting gap (NFHS-5 vs Poshan Tracker) and who falls through it — numbers from R3 |
| Evidence & context | Credible numbers with primary sources | Verified numbers table (NFHS-5, PIB/Parliament answers, SDG India Index, cohort studies) |
| Existing-ecosystem analysis | Current schemes/systems and why the gap persists | Systems map (Poshan Tracker, RCH/ANMOL, U-WIN, ABDM, CMAM protocol 2023, NRCs, state campaigns) + cited root causes |
| Proposed solution | Concrete technical architecture, not policy alone | Component map with typed contracts, decision-rights matrix + escalation protocol, DPDP-mapped safeguards, working demo |
| Feasibility & roadmap | Stakeholders, resources, constraints | Plugs into existing apps (no new AWW app, no new data entry), phased district → state pilot, cost, risks |
| Impact & scalability | Beneficiaries, outcomes, scale path | Metrics: lead time, early-catch rate, time-to-action, data credibility; evaluation design; national scale-out |

Hard constraints: ≤6 pages A4, 1-inch margins, Arial ≥11 pt, single PDF `India71_100_[Team ID].pdf`, via Google Form, due 1 Nov · team ≤4, one theme per team, fixed at registration (15 Oct) · original work · finals 16–18 Dec: 10-min talk + 5-min Q&A (problem validation, ecosystem, solution, roadmap, feasibility, scalability, impact).

**Assumptions (overnight, recorded instead of asking):**
- A1. We build Theme 1 fully; the theme choice is made by the 12 Oct selection memo.
- A2. No public Poshan Tracker microdata exists; the demo uses official WHO growth-standard tables plus a clearly labelled SYNTHETIC cohort calibrated to published NFHS-5 and cohort-study parameters. Real-data validation becomes a pilot item.
- A3. WHO tables come from WHO's `anthro` repository (GPL-3.0, commit b776d8a, 30 Jan 2026), are kept in gitignored `.data/` with a fetch script, and our z-score code is our own implementation of the published WHO method (no GPL code copied).
- A4. Working name for the system: **Poshan Setu** ("bridge") — renameable.

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** The India @71/100 Challenge — Techfest IIT Bombay. Prize pool ₹1,00,000.
- **Official statement:** [`_briefs/india71.pdf`](../_briefs/india71.pdf) (text: [`_briefs/india71.txt`](../_briefs/india71.txt)).
- **Challenge question (verbatim):** "Identify one measurable gap between India's development scorecard and the lived reality of an underserved group (including socially marginalised groups) within one of the three competition themes, and design a solution that could be realistically implemented and scaled in the real world."
- **Round 1 — due 1 Nov:** a proposal of **at most 6 pages** (A4, 1-inch margins, Arial ≥11 pt, single PDF named `India71_100_[Team ID].pdf`, via the official Google Form): team info · problem identification (the gap and the underserved community) · evidence & context · existing-ecosystem analysis (why the gap persists) · proposed solution · expected impact. A **concrete technical architecture** (data pipeline, decision-support model or platform design) is expected — not a policy recommendation alone. No prototype required. Top 10 teams per theme shortlisted on **8 Nov**.
- **Round 2 — 16–18 Dec at IIT Bombay:** 10-min presentation + 5-min jury Q&A covering problem validation & stakeholders, ecosystem analysis, detailed solution, implementation roadmap, feasibility, scalability and impact assessment.
- **Judging:** problem identification · evidence & context · existing-ecosystem analysis · proposed solution · feasibility & implementation roadmap · impact & scalability.
- **Rules:** students, team ≤4 (cross-institute allowed); **one theme per team** (fixed at registration, by 15 Oct); original work.
- **Round-1 deliverable for the morning package:** `deliverables/round1-proposal.md` (fits 6 pages when rendered) + an architecture diagram. A small working demo of the architecture is a bonus that will strengthen the finals.

**Theme 1 — Maternal & Early Childhood Nutrition.** Problem (verbatim): "From a data governance and policy-implementation perspective, design a technologically robust solution that closes the gap between what Poshan Abhiyaan/Mission Poshan 2.0 already collects and what frontline systems actually act on." Engage with at least one of:
1. **Interoperability & data flow** — how should Anganwadi (ICDS-CAS/Poshan Tracker), ASHA/health-system and community-level records be linked or made interoperable so at-risk children are flagged before, not after, severe malnutrition develops?
2. **Decision rights & accountability** — who should see which data, at what frequency, and through what escalation protocol, so a block or district administrator can act on early-warning signals within existing service-delivery timelines?
3. **Data quality & governance safeguards** — how should data validation, consent and child-data privacy be built in from the outset, consistent with applicable data-protection and data-sharing norms?

Context from the statement: Poshan Tracker already tracks growth-monitoring and service-delivery indicators for close to 9 crore children; data sits in siloed dashboards used for retrospective reporting rather than early warning. Suggested sources: Poshan Tracker / ICDS-CAS dashboards (MWCD), NFHS-5 (2019–21), Mission Poshan 2.0 guidelines, Ayushman Bharat Digital Mission (interoperability standards), the Digital Personal Data Protection Act 2023, the National Data Governance Framework Policy 2022 (MeitY).

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- ABDM building blocks (ABHA IDs, consent manager, FHIR-based exchange); WHO child growth standards (z-scores for stunting, wasting, underweight) and growth-faltering early-warning models.
- The ASHA/ANM side: RCH portal, ANMOL. DPDP Act provisions on children's data (verifiable parental consent; limits on tracking and behavioural monitoring).
- Known data-quality problems in anthropometric data (age heaping, implausible measurements).
- What others ship: state-level nutrition dashboards and command centres, and NGO/tech-partner pilots — find the latest published evaluations.

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
