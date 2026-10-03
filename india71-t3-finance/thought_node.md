# India @71/100 · Theme 3: Financial inclusion & meaningful banking access — Thought Node

> Journal for `india71-t3-finance/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 1 (SOTA research, 8 agents) ∥ 2 (component map — lead). Phase 0 done 02:55 IST.
- **Plan (to 08:30 IST):** 03:00–04:00 research lands + component contracts → 04:00 per-component research + six-hats/antithesis/first-principles on spike candidates → 04:30–06:30 walking skeleton (simulator, usage-state, uplift targeting, DP accountability) + eval harness with real numbers, first ratchet loop → 06:30–08:00 landscape, ADR 001, selection memo, round-1 proposal (≤6 pp), architecture.md → 08:00 fact-check, push.
- **Doing:** research agents r1 evidence-numbers · r2 regulation-governance · r3 last-mile-deployed · r4 interventions-and-targeting · r5 privacy-tech · r6 social-signal · r7 accountability-nsfi · d1 public-data fetch (all background, write to `research/` and `eval/public_data/`). Lead: component map + contracts.
- **Next:** landscape.md synthesis → components.md + contracts → per-component research → ADR 001 → skeleton + eval → autoresearch → deliverables.
- **Needs from user:** Register by 15 Oct for one theme (after the 12 Oct selection). Teammates (≤4): names and skills. Nothing blocks tonight.
- **Risks:** (1) No account-level PMJDY/DBT data is public → targeting is evaluated on a clearly-labelled synthetic simulator calibrated to public aggregates, plus public uplift benchmarks; the real-data part of the demo is district/state level. (2) Policy-oriented jury → the ML must serve a governance story, not lead it. (3) Cross-bank person-level linkage touches Aadhaar Act s.29 / DPDP → keep person lists inside the account-holding bank; only tokenised linkage in a regulated clean room; government sees aggregates. (4) Reactivated dormant accounts are mule-fraud targets → reactivation needs a fraud gate.

## Brief → what we must be able to show (Phase 0, 02:55 IST)
Hard constraints: one theme per team, fixed at registration (15 Oct); team ≤4; Round 1 = ≤6 pages A4, 1-inch margins, Arial ≥11 pt, single PDF `India71_100_[Team ID].pdf` via Google Form by 1 Nov; must be a concrete technical architecture (targeting model / interoperable access layer / governance dashboard), not a financial product; original work. Round 2 (16–18 Dec): 10-min talk + 5-min Q&A.

| Judging criterion | What we must show |
|---|---|
| Problem identification | One named gap for one named community, stated as a measurable number (scorecard value vs lived-reality value). |
| Evidence & context | A cited numbers table (PMJDY, inoperative accounts from Parliament answers, FI-Index, Findex 2025, NFHS-5, DBT, NPCI) + our own analysis of real public data. |
| Existing ecosystem | Map of schemes and rails (PMJDY, DBT/APBS/NPCI mapper, BC/BC Sakhi/IPPB, AePS, UPI 123PAY, AA, re-KYC drives, UDGAM, NSFI/FI-Index/SLBC) + an evidenced root-cause tree of why the gap persists. |
| Proposed solution | Architecture diagram + component contracts + data-governance matrix (who sees what, at what granularity, on what legal basis) + working demo. |
| Feasibility & roadmap | Owners per component (DFS, RBI, NPCI, banks, SLBC/LDM, DBT Mission), legal basis, pilot design (randomised, 1 district), timeline, costs (labelled estimates), risk register. |
| Impact & scalability | Evidence-based effect sizes, simulated impact (labelled), KPIs, scale path over existing rails. |

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** The India @71/100 Challenge — Techfest IIT Bombay. Prize pool ₹1,00,000.
- **Official statement:** [`_briefs/india71.pdf`](../_briefs/india71.pdf) (text: [`_briefs/india71.txt`](../_briefs/india71.txt)).
- **Challenge question (verbatim):** "Identify one measurable gap between India's development scorecard and the lived reality of an underserved group (including socially marginalised groups) within one of the three competition themes, and design a solution that could be realistically implemented and scaled in the real world."
- **Round 1 — due 1 Nov:** a proposal of **at most 6 pages** (A4, 1-inch margins, Arial ≥11 pt, single PDF named `India71_100_[Team ID].pdf`, via the official Google Form): team info · problem identification (the gap and the underserved community) · evidence & context · existing-ecosystem analysis (why the gap persists) · proposed solution · expected impact. A **concrete technical architecture** (data pipeline, decision-support model or platform design) is expected — not a policy recommendation alone. No prototype required. Top 10 teams per theme shortlisted on **8 Nov**.
- **Round 2 — 16–18 Dec at IIT Bombay:** 10-min presentation + 5-min jury Q&A covering problem validation & stakeholders, ecosystem analysis, detailed solution, implementation roadmap, feasibility, scalability and impact assessment.
- **Judging:** problem identification · evidence & context · existing-ecosystem analysis · proposed solution · feasibility & implementation roadmap · impact & scalability.
- **Rules:** students, team ≤4 (cross-institute allowed); **one theme per team** (fixed at registration, by 15 Oct); original work.
- **Round-1 deliverable for the morning package:** `deliverables/round1-proposal.md` (fits 6 pages when rendered) + an architecture diagram. A small working demo of the architecture is a bonus that will strengthen the finals.

**Theme 3 — Financial Inclusion & Meaningful Banking Access.** Problem (verbatim): "From a data governance and policy-implementation perspective, design a technologically robust solution that uses existing financial-inclusion data - PMJDY account and transaction status, DBT Mission records, RBI FI-Index indicators - to move beneficiaries from merely holding a formal account to actively and meaningfully using financial services." Engage with at least one of:
1. **Data-driven targeting & governance** — how should dormancy, DBT-linkage and usage data be governed and shared, within applicable RBI/NPCI/DBT Mission data-protection norms, to identify and prioritise specific inactive-account segments for intervention?
2. **Interoperable last-mile infrastructure** — how can Aadhaar-enabled payment systems, UPI and Business Correspondent networks be better integrated with existing account data to reduce friction for low-literacy or rural users?
3. **Policy feedback & accountability** — how should account-activity data feed back into the National Strategy for Financial Inclusion targets so implementers can be held accountable for usage, not just enrolment?

Context from the statement: PMJDY brought over 56 crore people into the formal system, yet roughly a quarter of these accounts remain inactive. The statement expects a concrete technical architecture — "not a new financial product concept alone". Suggested sources: PMJDY dashboards (DFS, Ministry of Finance), the RBI FI-Index, RBI's National Strategy for Financial Inclusion, DBT Bharat dashboards, NPCI UPI/AePS data, the DPDP Act 2023.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Account Aggregator framework (Sahamati) for consented data flows; RBI rules on inoperative accounts and the UDGAM unclaimed-deposits portal.
- Low-literacy rails: UPI 123PAY, voice-based UPI ("Hello! UPI"), Business Correspondent network performance data.
- Uplift modelling for targeted nudges.
- What others ship: bank and fintech reactivation programmes and DPI case studies — find published results.

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

### 2026-10-04 02:55 IST — Phase 0 done; Phase 1 launched
Read PLAYBOOK, seeded brief and `_briefs/india71.txt`; brief verified against the official text (constraints and the judging→evidence map are in *Brief → what we must be able to show*). Launched 8 background agents: r1 evidence numbers, r2 regulation and governance, r3 last-mile and what is deployed today, r4 intervention evidence and uplift/targeting methods, r5 privacy-preserving computation, r6 practitioner/social signal, r7 NSFI and accountability metrics, d1 real public-data fetcher. Assumption (no user input tonight): the demo uses real public aggregates for the district/state layer and a labelled synthetic simulator for account-level targeting, because no account-level PMJDY/DBT data is public.
