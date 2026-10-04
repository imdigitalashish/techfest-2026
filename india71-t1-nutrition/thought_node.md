# India @71/100 · Theme 1: Maternal & early-childhood nutrition — Thought Node

> Journal for `india71-t1-nutrition/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** ✅ Round-1 package complete (11:00 IST, 4 Oct). Supervisor definition of done met (see Log 11:00). Slot freed.
- **Deliverables:**
  - [`deliverables/India71_100_[TeamID].pdf`](deliverables/): 6 A4 pages, 1-inch margins, Arial ≥11 pt; source `round1-proposal.md` v0.3.
  - [`deliverables/architecture.md`](deliverables/architecture.md).
  - Selection memo final (below).
  - Reviews in [`reviews/`](reviews/).
  - Demo: `eval/run_pipeline.py` (SYNTHETIC).
- **Next (after the 12 Oct selection, if this theme is picked):**
  1. Fill the team header and Team ID; re-render (`deliverables/build_pdf.py` + Chromium print) and re-run `eval/check_docs.py`.
  2. Optionally, a cross-model re-review of v0.3 via a session (v0.3 hasn't been re-reviewed; it applies the v0.2 review).
  3. Spike A evaluator v2 (audit PPV at fixed re-measurement budget; remote-AWC false-positive rate) + ratchet.
  4. Spike B ratchet against `eval_v1` (the model must beat the lowest-WHZ rule); repeated-alert burden metric.
  5. Implement the three-clock fields in the `Task` contract (currently design only).
  6. Finals deck and demo script (16–18 Dec).
- **Needs from user:**
  - (a) Register by 15 Oct for one India@71 theme. This memo recommends T1 at 4.2/5; compare with the T2 and T3 memos.
  - (b) Teammates (≤4): names, institution, contacts, for the PDF header.
  - (c) Any state WCD department or district contact for a read-only pilot extract.
  - (d) An introduction to an Anganwadi workers' union or worker-rights NGO for co-design (a pilot prerequisite under ADR 002).
- **Risks:**
  1. All model metrics are SYNTHETIC.
  2. The children's-data regime commences 13 May 2027, so pilot timing straddles it; the legal go/no-go gate stays.
  3. Worker and union acceptance.
  4. The ML worklist model loses to the transparent rule (handled: rule ships, ML gated).
  5. Page budget: 6/6, with about 200 words of slack on page 6.

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
- 2026-10-04 — **ADR 003:** spike B ships a transparent lowest-WHZ ranking; ML is gated on beating it prospectively (leakage-free eval: 0.429 vs 0.384). [ADR 003](architecture/adr/003-transparent-ranking-first.md)
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
| C5 | early_warning → weekly ranked worklist (ADR 003) | z, velocity, observed status → ranked top-K per AWC | 2-month no-gain rule | **B** | v1 eval (leakage-free) | episode recall@5: transparent lowest-WHZ rule **0.429** (CI 0.420–0.443) > logistic 0.384 ≈ +health 0.384 > no-gain rule 0.365 > random 0.269 — SYNTHETIC; v0 (0.33/0.25) retracted |
| C6 | action_router | Alert → Task (+ escalation) | monthly review | | built; protocol v0.2.0 (CMAM 2023 verified) | demo: 482 escalated after 8 days (70% on time assumed); ops SIMULATION 83.6% vs 15.6% within SLA |
| C7 | frontline_worklist | Task → Worklist | PT home-visit scheduler | | built | payload bytes, % SMS ≤160 |
| C8 | aggregate_publisher | events → AggregateCell | static dashboards | | contract | relative error at ε |
| C9 | policy_gate | AccessRequest → AccessDecision | RBAC | | built; verified legal basis (v0.2.0); hardened | 39/39 red-team (incl. spoofed scope, fake consent, employment use), 0 false allows |
| C10 | audit_ledger | event → AuditEntry | DB audit | | built + checkpoint | tamper detection 100/100; truncation detected with checkpoint |

## Selection memo (FINAL, 4 Oct 2026 11:00 IST; theme decision 12 Oct, registration by 15 Oct)
- **Winnability — 4/5.** The evidence is unusually strong, with every core number and legal anchor verified at primary sources:
  - Poshan Tracker 5.46% wasting (June 2025, Rajya Sabha USQ 477) against NFHS-5 19.3% (PIB 1988614);
  - NFSA 2013 s.6, DPDP Act s.7(c)/s.8(3)/s.9 + Rules 2025 Fourth Schedule (commencement G.S.R. 843(E));
  - CMAM Protocol 2023 timelines.
  Two independent cross-model reviews were run and their fixes applied.
- **Innovation headroom — 4/5.** Measurement-system diagnostics per AWC × device × month: support before scrutiny, no worker scores, the s.8(3) accuracy duty made operational. Capacity-capped weekly worklists with a three-clock escalation tied to verified protocol steps. Purpose-bound policy-as-code (39/39 red-team). Privacy-preserving ICDS↔health linkage (SYNTHETIC F1 0.97).
- **Feasibility by the deadline — 5/5.** The proposal PDF is done (6 pages) on 4 Oct; due 1 Nov, well before the 19–25 Nov exams. Finals need only a deck and the demo, which already runs end to end in seconds.
- **Demo strength at finals — 4/5.** WHO-validated z-scores (real tables, 0.003 z) → diagnostics → ranked worklists (SMS ≤80 chars) → escalation (482 after 8 days) → verified audit chain. The honest twist that judges will remember: once leakage was removed, a transparent WHZ rule (43%) beat our ML model (38%), so the explainable rule ships. Weakness: synthetic data only.
- **Fit with the user's strengths — 4/5.** Large-scale data systems, privacy engineering, applied ML, and government-cloud deployment (Microsoft/Azure experience).
- **Biggest risk:** judges discount synthetic evaluation, or read diagnostics as surveillance of AWWs. Mitigated by ADR 002 (no worker scores, equipment first, appeal, employment-use deny), the honest evaluation story, and a pilot whose first study is blinded re-measurement.
- **Overall: 4.2/5.** Recommend T1 unless the T2/T3 memos are clearly stronger.
- **One-line pitch:** "Poshan Tracker says 5% of children are wasted; the national survey says 19%. Poshan Setu shows each district which measurements to trust and which children to see this week, through the apps workers already use, with every access lawful and logged."

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
- (RETRACTED 10:35: v0 evaluator had look-ahead and an oracle pool; see the 10:35 log entry and ADR 003) recall@5: programme rule "no weight gain in 2 months" **0.253**; lowest current WHZ **0.318**; logistic on anthropometry **0.326**; plus linked health events **0.325**.
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

### 2026-10-04 09:30–09:55 IST — legal layer verified; paused
- **Agent V1 verified the DPDP texts at primary sources** ([`research/sources/V1-dpdp-verified.md`](research/sources/V1-dpdp-verified.md)):
  - s.2(f): every ICDS beneficiary is a "child".
  - s.7(b) is *conditional* (prior consent, or a Centre-notified database), so supervisory and monitoring uses move to s.7(c), State function under law.
  - s.8(3): accuracy duty when data drive decisions or are shared. This is now the legal rationale for spike A.
  - s.17(2)(b): research only with no individual decisions.
  - DPDP Rules 2025 (G.S.R. 846(E), 13 Nov 2025): Rules 3 and 5–16 commence on 13 May 2027. Rule 12 + Fourth Schedule exempt from s.9(1),(3): Part A(1) health services by clinical establishments; Part B(1) functions "in the interests of a child, under any law"; Part B(2) State benefits to children.
- **Applied.** `policy.yaml` → v0.2.0: all 14 legal-basis strings replaced with verified citations; 0 "(VERIFY)" left on DPDP items (ABDM consent details and the NFSA statutory anchor still UNVERIFIED); tests pass. Also updated the proposal §4.3 privacy paragraph and landscape §4.
- **NFSA 2013 s.5(2)** ("identified through the local anganwadi"): primary text not reachable (India Code timeouts; dfpd/PRS URLs returned HTML/404), so it stays UNVERIFIED.
- **Agent V2** (CMAM protocol timelines) was still running at pause; its output file is the first resume step.
- **Paused** on Supervisor instruction at 09:55.

### 2026-10-04 ~10:20 IST — (paused) agent V2 result saved, not yet applied
[`research/sources/V2-cmam-timelines.md`](research/sources/V2-cmam-timelines.md), from 4 primary sources (CMAM Protocol 2023, Poshan 2.0 guidelines 2022, HBYC handbook, NRC guidelines 2011).

Against our `protocol.yaml` assumptions:
- SAM medical appraisal is **3–5 days**, not 7.
- The AWW 2-day step is confirmed, but as information-sharing with ASHA/ANM.
- The day-7 LS and day-14 CDPO/MO triggers are **UNVERIFIED**; confirmed are only monthly LS/CDPO oversight and a monthly DM-led SAM review.
- MAM fortnightly re-measure is confirmed; the 30-day LS rule is unverified (official triggers: 2 weeks / 3 months).
- Growth faltering: HBYC says **5 days** for severe (downward-curve) cases.
- NRC: discharge at 15% weight gain; stay 10–15 days; follow-up at 2 weeks, then monthly.

Apply at resume step 2.

### 2026-10-04 10:08–11:00 IST — resumed; definition of done completed
- **Legal layer verified at primary texts:**
  - CMAM Protocol 2023 (wcd.gov.in, 24 pp): 2-day SAM list sharing p.20; 3–5-day medical appraisal p.8; fortnightly MAM visits p.11; monthly district review p.22. `protocol.yaml` v0.2.0 cites pages; our own rules are labelled DESIGN.
  - NFSA 2013 **s.6** (Gazette copy; secondary sources wrongly say s.5(2)).
  - ABDM HIP/HIU Guidelines 24 Oct 2022 p.19 (consent artefact = purpose + duration) and p.5 (RCH as HIP).
  - DPDP commencement G.S.R. 843(E): ss.3–17 from 13 May 2027.
  - 0 "(VERIFY)" left in code, docs or deliverables. Notes in [`research/sources/V3-lead-verified-nfsa-abdm-cmam.md`](research/sources/V3-lead-verified-nfsa-abdm-cmam.md).
- **Cross-model reviews** (sub-agents launched before the 10:15 sessions directive; recorded in [`reviews/`](reviews/), ledger.tsv):
  - GPT-6 Sol code review: 14 issues, all accepted. Policy-gate bypasses fixed (39/39), ledger truncation checkpoint, MUAC rule, demo classification, no-look-ahead test, `fetch_who.py`, `requirements.txt`.
  - GPT-6 Astra proposal review: 17 issues, 16 accepted; 1 rejected (inventing a pilot costing).
- **Biggest finding.** The v0 early-warning eval had look-ahead and an oracle pool. The leakage-free `eval_v1.py` (episode recall, AWC bootstrap, SYNTHETIC) gives:
  - transparent lowest-WHZ rule **0.429** (0.420–0.443) beats the logistic model **0.384**;
  - linked health adds nothing;
  - programme rule 0.365, random 0.269.
  → [ADR 003](architecture/adr/003-transparent-ranking-first.md): the rule ships, ML is gated. v0 numbers retracted everywhere.
- **Supervisor alignment (10:38): agreed.** v0.3 reports v1 as a strength. Added `eval/check_docs.py` (17 quoted numbers checked against `eval/results`, also a pytest).
- **Demo now covers the whole chain:** z-scores → diagnostics → ranking → tasks → worklists → **escalation** (fixed a scope bug: escalated tasks now go to the sector/project owner; 482 escalated after 8 days at an assumed 70% on time) → audit (2,171 entries, verified). SYNTHETIC; runs in about 4 s.
- **Proposal v0.3 → PDF:** `India71_100_[TeamID].pdf`, 6 A4 pages, 1-inch margins, Arial (body 11 pt, diagram 11.25 pt unscaled), all 6 required sections + architecture diagram. 29 tests pass.

