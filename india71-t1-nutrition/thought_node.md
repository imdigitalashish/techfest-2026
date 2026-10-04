# India @71/100 · Theme 1: Maternal & early-childhood nutrition — Thought Node

> Journal for `india71-t1-nutrition/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 5–6. Morning package delivered (08:02, accepted by the Supervisor at 08:22). Since then: hostile-judge review → ADR 002 redesign of spike A; proposal v0.2; first auto-research iterations (1 rejected as overfit, 1 kept for design reasons); end-to-end walking skeleton.
- **Plan (next):**
  1. Fold in the DPDP verification (`V1`, running) and replace every (VERIFY) tag, or change the design.
  2. Verify ABDM consent-artefact details and the CMAM protocol timelines.
  3. Evaluator v2 for spike A (audit value of diagnostics: PPV at a fixed re-measurement budget; remote-AWC false-positive rate; robustness across simulator variants).
  4. Early-warning evaluator v1 (real-decline episodes) and a ratchet loop.
  6. Re-run the failed research threads one at a time (≤2 concurrent agents).
- **Doing:** lead + research agent V1 (DPDP Act/Rules verification).
- **Needs from user:** (a) register by 15 Oct for one India@71 theme (after the 12 Oct memo); (b) teammates (≤4): names, skills, contacts; (c) any state WCD / district contact for a read-only pilot extract (on the Supervisor's list); (d) later, ideally an introduction to an Anganwadi workers' union or worker-rights NGO for co-design (ADR 002 makes this a pilot prerequisite).
- **Risks:**
  1. All model metrics are SYNTHETIC.
  2. The legal basis for child-level scoring is unconfirmed (go/no-go gate in ADR 002).
  3. Worker and union acceptance.
  4. Metric gaming in the auto-research loops (anti-gaming holdout in place; it already caught one overfit).

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
- 2026-10-04 — Working name **Poshan Setu**; no new frontline app, no new data entry; two-plane design (identity vault vs pseudonymous analytics). [components.md](architecture/components.md)
- 2026-10-04 — Measurable gap = survey-vs-admin divergence on wasting (NFHS-5 19.3% vs Poshan Tracker 5.46%, June 2025) and the unknown share of under-detection behind it. [landscape §1](research/landscape.md)
- 2026-10-04 — Spikes: **A credibility engine** + **B capacity-constrained early warning**; rest best practice. [ADR 001](architecture/adr/001-spike.md)
- 2026-10-04 — Demo on WHO tables (real) + SYNTHETIC cohort calibrated to ki-consortium parameters; every artefact carries `synthetic=True`.
- 2026-10-04 — **ADR 002:**
  - spike A is measurement-system diagnostics per AWC × device × month: no worker scores, support before scrutiny, random plus targeted re-measurement;
  - employment use denied in code (contract v0.2.0) and in the data-sharing agreement;
  - child-level prediction sits behind a legal go/no-go;
  - a service-readiness gate comes before SLA clocks;
  - the 19.3 vs 5.46 figure is framed as an *unexplained discrepancy*.
  [ADR 002](architecture/adr/002-measurement-diagnostics.md) · [hostile-judge-01](research/hostile-judge-01.md)

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric (latest, committed) |
|---|---|---|---|---|---|---|
| C0 | cohort_simulator | SimConfig → events + truth | — | | built | calibration: wasting 17.2% (NFHS-5 19.3%), stunting 36.7% (35.5%), 90-day recovery 70.9% (ki 71.1%), at-birth wasting 22.8% (ki SA 18.9%) — SYNTHETIC |
| C1 | ingest_adapters | extracts/FHIR → canonical events | ETL | | contract | % schema-valid |
| C2 | identity_linkage | IdentityRecord → LinkDecision | ID join, Fellegi–Sunter | (C) | built | F1 ids 0.513 · prob 0.945 · PPRL 0.968 — SYNTHETIC |
| C3 | growth_standards | MeasurementEvent → AnthroZ | WHO Anthro | | built | max error 0.003 z on 87,408 WHO table points |
| C4 | credibility_engine → measurement diagnostics (ADR 002) | events+z → RecordQuality, AWC×device×month diagnostics | SMART / WHO-UNICEF survey checks | **A** | built; ratchet started | AUROC fabricating 0.694±0.041, any non-good 1.0 — SYNTHETIC; iteration 1 (0.950) rejected by anti-gaming holdout |
| C5 | early_warning | z, velocity, health events → RiskScore | 2-month no-gain rule | **B** | v0 built | recall@5/AWC-month 0.326 vs rule 0.253, lowest-WHZ 0.318; +health 0.325 — SYNTHETIC |
| C6 | action_router | RiskScore/Alert → Task | monthly review | | built | ops SIMULATION: 83.6% within SLA (ladder, alerts ≤ capacity) vs 15.6% (monthly review); 14.9% when alerts exceed capacity |
| C7 | frontline_worklist | Task → Worklist | PT home-visit scheduler | | built | payload bytes, % SMS ≤160 |
| C8 | aggregate_publisher | events → AggregateCell | static dashboards | | contract | relative error at ε |
| C9 | policy_gate | AccessRequest → AccessDecision | RBAC | | built | 31/31 red-team (incl. employment-use denial), 0 false allows |
| C10 | audit_ledger | event → AuditEntry | DB audit | | built | tamper detection 100/100 |

## Selection memo (v1, 4 Oct 2026 — final by 12 Oct)
- **Winnability — 4/5.** Few student teams will bring a verified admin-vs-survey gap (5.46% vs 19.3% wasting) *plus* a working, tested architecture. The judging rubric rewards evidence and ecosystem analysis, which we have with primary citations.
- **Innovation headroom — 4/5.** The credibility engine (AWC-level trust scores from routine data, used to correct prevalence and target re-measurement) has no deployed Indian equivalent we could find. Capacity-capped, reason-coded early warning on linked ICDS + health data is rare in the literature ([L6](research/sources/L6-ews-models.md)).
- **Feasibility by the deadline — 5/5.** Core components already run and are tested. The proposal (≤6 pages) is due 1 Nov, before the 19–25 Nov exams; finals prep is light.
- **Demo strength at finals — 4/5.** Live pipeline: WHO-validated z-scores → credibility map → weekly worklist → escalation → audit trail. Weakness: synthetic data unless a state shares an extract.
- **Fit with the user's strengths — 4/5.** Large-scale data systems, privacy engineering and ML; Microsoft/Azure experience is relevant to the government-cloud deployment story.
- **Biggest risk:** judges discount synthetic validation, or see credibility scoring as surveillance of AWWs. Mitigation: re-measurement protocol as ground truth; supportive-supervision framing; real-data pilot plan.
- **Overall: 4.2/5** (mean of the five scores above; evidence-backed, build already runs).
- **One-line pitch:** "India's child-growth data says 5% of children are wasted; the national survey says 19%. Poshan Setu tells each district which numbers to trust and which children to see this week, without a single new app."

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 02:05–03:35 IST — Phase 0 + research fan-out
Read PLAYBOOK, brief, official statement. Branch renamed. Wrote Phase 0 judging map and assumptions A1–A4 (see above). Launched 8 research agents (R1–R7); 7 of 8 died on model 408 timeouts (0 turns). Typed contracts written (pydantic → 23 JSON Schemas). WHO LMS tables fetched from WHO `anthro` (commit b776d8a).

### 2026-10-04 03:35–06:10 IST — narrow research retry, builders, z-score engine
Relaunched research as 12 narrow agents (L1–L12). Survivors with usable notes: L5 growth epidemiology (ki consortium, verified), L6 early-warning models, L7 deployed India (partial), L8 global (partial), L9 Poshan Tracker facts, L12 linkage/DP/audit tools, R6 social signal (partial), L4 state CSV. Failed: L1 DPDP, L2 ABDM/NDGFP, L3 NFHS-5, L10 CMAM protocol, L11 DQ methods → legal citations stay (VERIFY). Built `growth_standards` (validated against WHO's own expanded z-score tables: max error 0.003 z on 87,408 points), `cohort_simulator` (SYNTHETIC; calibrated), `credibility_engine` + frozen `eval.py`. Builder agents produced `identity_linkage` (F1 0.513/0.945/0.968) and most of policy_gate / audit_ledger / action_router / frontline_worklist before failing. Supervisor imposed lean mode at ~05:50.

### 2026-10-04 07:10–08:00 IST — resume after session crash; morning package
Pushed all component work (`31ccc35`; 19 tests pass). Verified the core gap at primary sources myself: Rajya Sabha USQ 477 Annexure I (Poshan Tracker June 2025: 37.07/5.46/15.93) and PIB PRID 1988614 (NFHS-5 35.5/19.3/32.1; Poshan Tracker Nov 2023 37.51/17.43/6). Wrote research/landscape.md, architecture/components.md, ADR 001, deliverables/round1-proposal.md + architecture.md, selection memo v1. Ran all component metrics into `eval/results/*.json`. Known issue: action-router ops simulation output invalid (median 999 days; queue overload under default assumptions), so it is excluded from all claims until fixed.

### 2026-10-04 08:00 IST — early-warning v0 (spike B) result
Frozen evaluator `components/early_warning/eval.py` (train seeds 21–22, held-out seed 23; capacity K=5 per AWC per month; target = truly wasted within 3 months among truly non-wasted child-months). SYNTHETIC result ([`eval/results/early_warning.json`](eval/results/early_warning.json)):
- recall@5: programme rule "no weight gain in 2 months" **0.253**; lowest current WHZ **0.318**; logistic on anthropometry **0.326**; plus linked health events **0.325**.
- Base rate 15.4%.

Learned: (1) the v0 model beats the programme rule by +7.3 pp at equal capacity but barely beats ranking by current WHZ. (2) Linked health events add nothing *in this simulator*. This is partly by construction (illness is weakly coupled to episode onset), so linkage value must not be claimed from it. (3) The high base rate suggests many "incident" cases are threshold-hovering. Next: an evaluator v1 that weights new episodes with a real decline (kept as a separate file; v0 stays frozen), a velocity-z feature, and a ratchet loop.

### 2026-10-04 08:05 IST — proposal length check
Rendered `deliverables/round1-proposal.md` to PDF (Playwright; A4, 1-inch margins, Arial 11 pt, 7.5 cm placeholder for the diagram): **5 pages**, so it fits the 6-page limit with a page of headroom (preview in gitignored `.cache/`). Still open: team header, final diagram rendering, (VERIFY) legal citations.

### 2026-10-04 08:15–09:05 IST — skeleton, ratchet, hostile judge, ADR 002
- **Walking skeleton.** `eval/run_pipeline.py` runs one weekly district end to end on SYNTHETIC data ([`eval/results/pipeline_demo.json`](eval/results/pipeline_demo.json)):
  - 5,307 children measured in the month across 120 AWCs; 4.22% of records rejected; 47 AWCs flagged.
  - Alerts: 123 SAM, 838 MAM, 600 risk, 47 data-recheck → 1,608 tasks → 140 worklists, 1,222 SMS (max 80 chars).
  - Access decisions as intended (AWW own AWC allow; DPO named deny; AWW other AWC deny; public aggregate transformed). Audit chain of 1,612 entries verified.
  - Risk-alert precision 41.5%; 25.8% of next-3-month incident cases flagged in that single month.
- **Auto-research on spike A.**
  - Iteration 1 (+weight-increment spread, +length-increment band) scored 0.950 on the frozen eval but **0.7287 = baseline** on a variant fabrication pattern. Its band feature copies the simulator's own band, so it was **rejected and reverted**.
  - Iteration 2 (drop `low_wasting_vs_peers`): no metric change, kept for design reasons. Ledger: `components/credibility_engine/autoresearch/results.tsv`.
- **Hostile judge.** An independent rubber-duck agent raised 8 blocking objections; the top 3 are accepted ([research/hostile-judge-01.md](research/hostile-judge-01.md)). Wrote ADR 002. Proposal → v0.2: no "6 lakh never flagged" claim, synthetic results labelled as engineering checks, union co-design + legal opinion + pre-registered validation as pilot prerequisites, service-readiness gate. Policy gate: explicit `employment_action` deny (31/31).

### 2026-10-04 09:20 IST — action-router simulation fixed; proposal at 6 pages
- **Bug.** The old ops simulation pooled capacity per *role* (20 tasks/week for all AWWs combined, against 60 alerts/week), so the backlog never cleared (median 999 days). It also scored first action instead of completion by the due date.
- **Fix.** `components/action_router/sim.py` now uses per-person capacity, per-sector supervisors and done-by-due timing.
- **Result** (ILLUSTRATIVE assumptions, [`eval/results/action_router_sim.json`](eval/results/action_router_sim.json)):
  - weekly ladder with alerts within capacity (3/AWC/week, capacity 4): **83.6%** done within the 7-day SLA, median 4 days;
  - monthly-review status quo: **15.6%**, median 18 days;
  - alerts above capacity (5/week, [`_overload.json`](eval/results/action_router_sim_overload.json)): **14.9%**, with 28% escalated.
- **Learned:** escalation ladders only help if alert volume is capped at capacity. This is the quantitative case for spike B's top-k-per-AWC design.
- **Proposal v0.2** renders to 6 A4 pages, with 29 words on page 6. Inside the limit, but trim before adding team details.

