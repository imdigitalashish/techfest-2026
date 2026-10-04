# India @71/100 · Theme 2: Foundational learning outcomes — Thought Node

> Journal for `india71-t2-learning/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** ⏸ **PAUSED** by the Supervisor at 09:55 IST (user's decision: only 3 projects run at a time; T1 is the provisional India@71 pick unless the user overrides). Nothing is running; no background jobs.
- **State at pause:** morning package complete and pushed — [landscape](research/landscape.md) · [components + contracts](architecture/components.md) · [12 per-component notes](research/components/) · [ADR 001 v2](architecture/adr/001-spike.md) (incl. first-principles review + case-register synthesis) · selection memo v1 (below) · [round-1 proposal v0.3](deliverables/round1-proposal.md) (renders to exactly 6 A4 pages, Arial 11 pt) + [architecture](deliverables/architecture.md) · walking skeleton + eval harness with ASER-calibrated numbers (`eval/results/summary.md`) · real-data ASER × PARAKH × UDISE+ analysis (`eval/results/real_data_analysis.md`) · auto-research scaffolds with baseline rows (C5 `components/trust_audit/autoresearch/`, C4 `components/diagnostics/autoresearch/`).
- **Resume point (in order):**
  1. C5/C6 interval calibration — 90 % intervals cover only 27 % of true block values. Start: bootstrap over the moderation sample in `components/trust_audit/core.py::adjust` and propagate into `components/area_estimation/core.py::fay_herriot_benchmark`; target coverage ≥ 0.85 without raising block MAE. Then find the minimum effective moderation sample (the 120-school / 12-re-test case failed).
  2. Re-run: `cd india71-t2-learning && nice -n 10 python3 eval/run_eval.py` (~3.5 CPU-min; 15–35 min wall under contention) → update the proposal demo table.
  3. Implement the C11 learning-case register (ADR 001 synthesis v2: notify → owner → recheck → verified cure; case-finding rate = notified ÷ (C6 prevalence × UDISE+ enrolment)) + a simulator test where honest notification beats inflation.
  4. First auto-research iterations (C4: `python3 components/diagnostics/autoresearch/eval.py`, baseline 0.551; C5: `python3 components/trust_audit/autoresearch/eval.py`, baseline 2.335 at default calibration — re-baseline at ASER calibration first).
  5. Make the simulator's inflation need-correlated so C9 allocation can show (or fail to show) a targeting gain.
  6. Re-run failed research narrowly: DPDP Rules 2025 text, NDEAR/VSK architecture at a government source, Kenya Tusome/Ceará; verify the three agent-cited papers (Aiyar & Bhattacharya 2016; Berry et al. 2020; Johnson & Parrado 2021).
  7. Selection memo final by 12 Oct (compare with T1/T3 memos); proposal: team details only placeholders left.
- **Needs from user:** Register by 15 Oct for one India@71 theme (Supervisor: T1 provisional). Teammates (≤4): names and skills.
- **Risks:** interval under-coverage (resume step 1); allocation gain not shown; PARAKH and ASER disagree strongly by state (this is evidence *for* our crosswalk, but jury may ask which to trust — answer: neither alone; link with uncertainty).

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
| C2 | Canonical model & identity | raw → School/Student/Response | Ed-Fi/CEDS-style, UDISE+/LGD codes | no | built (first pass) | validation pass rate; linkage F1 |
| C3 | Competency framework & crosswalk | docs/items → Competency/Item (Q-matrix) | SCERT expert mapping | no | built (first pass) | κ vs expert Q-matrix |
| C4 | Diagnostic engine | Responses → ChildDiagnosis | ASER highest-level rule | **spike 1** | built; baseline 0.551 @8 items | level accuracy; items to P≥0.9 |
| C5 | Measurement assurance | reported results → TrustAssessment | Gunotsav / Saksham verification | **spike 2** | built; 4.09 → 2.34 pp @10 % | block MAE (pp) at 10 % audit budget |
| C6 | Linking + small-area estimation | TrustAssessment + anchors → AreaEstimate | direct averages | candidate | built (first pass) | block RMSE; CI coverage |
| C7 | Teacher point-of-use | ChildDiagnosis → TeacherPlan | state apps / chatbots | **spike 1** | built; 659 B, 3 SMS | payload bytes; SMS segments |
| C8 | CRC visit planner | AreaEstimate + trust → VisitPlan | rota | no | spec | need-weighted coverage |
| C9 | Allocation & policy feedback | AreaEstimate → AllocationDecision | enrolment-proportional | candidate | built (first pass) | expected extra children vs oracle |
| C10 | Dashboards | estimates → HTML/JSON | VSK dashboards | no | built (first pass) | disclosure pass rate; KB |
| C11 | Action ledger & outcome loop | ActionRecord → effects | none | no | spec | % actions with outcome in 6 wks |
| C12 | Governance & access | AccessRequest → AccessDecision | role portals | no | built; 36/36 | policy suite pass rate |

## Selection memo
_v1, 4 Oct 2026 06:00 IST (lead). Final by 12 Oct. Scores 1–5 with one line of evidence._
- **Winnability — 4/5.** Theme 2 has the richest public evidence base of the three (ASER 2024 full report and state tables on disk; PARAKH 2024 national reports public; UDISE+), and the brief explicitly penalises "a generic ed-tech pitch" — the trap most teams will fall into. Our entry is a decision layer with typed contracts and moderation, grounded field-by-field in these datasets.
- **Innovation headroom — 4/5.** Spike 2, *measurement assurance* (rotating sentinel re-tests during existing CRC visits → model-assisted calibration → small-area block estimates benchmarked to PARAKH/ASER): novelty check done (09:10) — each element has precedent (NESA/QCAA/KS2 moderation, IPA back-checks, RBF verification, validation-subsample correction, FH literacy SAE), but no opened source combines them for Indian FLN census data → claim adaptation/combination novelty (`research/sources/novelty-check-measurement-assurance.md`). Spike 1 (adaptive check → Monday plan in ≤ 3 SMS → 6-week recheck) is incremental alone, strong as a loop on a shared competency spine. See [ADR 001](architecture/adr/001-spike.md).
- **Feasibility by the deadline — 5/5.** Runs entirely on the Mac (numpy/scipy); no hardware, credentials or real child data needed for Round 1. User effort: team details, a read-through, PDF export (~2 h), outside the 19–25 Nov exams.
- **Demo strength — 4/5.** A Hindi WhatsApp/SMS/IVR "Monday plan" for a teacher (659 bytes / 3 SMS in the first run) plus a moderated block dashboard with intervals, on a synthetic district calibrated to ASER 2024 government-school Std III levels (23.4 % reading, 27.6 % subtraction).
- **Fit with the user's strengths — 4/5.** National-scale data architecture (contracts, DPI integration with UDISE+/VSK/DIKSHA/APAAR, privacy by design) and statistical ML (IRT, small-area estimation, sampling design).
- **Biggest risk.** A jury may read the simulation as self-validating; mitigations: real-data ASER/PARAKH analysis, sensitivity analysis across bias scenarios, and a pilot design with staggered roll-out. Second risk: "policing teachers" — addressed by the non-punitive moderation design (ADR 001).
- **One-line pitch.** *Ek Tasveer turns the data India's schools already collect into one trusted picture — a Monday plan for every Grade 1–3 teacher and moderated, interval-backed block numbers for every official — so the three in four Grade 3 children in rural government schools who cannot yet read a Grade 2 text get the right help this week.*

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 02:50 IST — Phase 0 done; Phase 1 fan-out
Read PLAYBOOK, the seeded brief and `_briefs/india71.txt`; extracted hard constraints and the criterion → evidence map (above). Toolchain checked: Python 3.11, uv, pdftotext, numpy/pandas/scipy/sklearn/pydantic; Azure subscription enabled (not needed yet). Launched 8 background research agents (r1–r8, see *Now*). Assumption (overnight, no user input): we engage all three engagement areas, with governance/standardisation as the spine, because it is what makes the other two trustworthy; to be confirmed by ADR 001.

### 2026-10-04 05:15 IST — Outage recovery; Phase 2 contracts + component map; builders launched
Model API timed out (HTTP 408) for ~2 h across many sessions: r2 (deployed today), r4 (methods) and r7 (datasets) failed, though r4 and r7 left usable files (`research/sources/methods-sota.md`, `datasets-agent-notes.md`) and r7 downloaded ASER 2024 (full report), PARAKH 2024 Grade 3 report and the PARAKH technical report into `.data/raw/`. Wrote typed contracts (`architecture/contracts/fln_contracts.py`, 19 JSON Schemas) and the 12-component map (`architecture/components.md`, five "breaks" between a recorded number and a changed outcome: commensurability, trust, granularity, actionability, closed loop). Launched builders A and B, a local-file data extractor, narrow re-runs (r1n, r2a, r2b, r3n, r4n) and the antithesis + first-principles agents on the spike. Assumption: proposed spike = C5 trust & audit engine pending ADR 001.

### 2026-10-04 06:00 IST — ADR 001, proposal skeleton, selection memo v1; lean mode
Antithesis (rubber-duck) argued the audit spike is asserted-not-demonstrated, reads as surveillance, costs 100,000+ visits at 10 % national scale, and misses the classroom payoff. Synthesis adopted in [ADR 001](architecture/adr/001-spike.md): **Spike 1 = classroom action loop (C4 → C7 → C11)**, **Spike 2 = non-punitive measurement assurance (C5 + C6)** with uncertainty/decision-value sampling, a random floor, no published school-level trust labels, re-tests riding on CRC visits, and results reported as a sensitivity analysis. Verified ASER 2024 headline in the report text (govt-school Std III reading at Std II level 16.3 % → 23.4 %, subtraction 20.2 % → 27.6 %); `data/public/aser2024_state_std3.csv` has 180 rows. Builder A: tests passing (count UNVERIFIED — agent record lost); see the 07:55 entry for verified metrics. First Monday plan: 659 bytes (Hindi WhatsApp), 3 SMS segments. Supervisor switched all leads to lean mode (network saturated: 405/408 errors are request-upload timeouts); r3 and r8 failed, narrow re-runs continue. Selection memo v1 written.

### 2026-10-04 08:05 IST — Morning package
- **Verified facts now in the proposal** (quotes/pages in `research/sources/`): ASER 2024 govt Std III reading 23.4 % (16.3 % in 2022), subtraction 27.6 % (20.2 %), private reading 35.5 %; UDISE+ 2024-25: 14,71,473 schools, 24.69 crore students, 1.01 crore teachers, 68.9 % government, 1,04,125 single-teacher schools (33.8 lakh enrolled), student-wise data since 2022-23; NIPUN: universal FLN by 2026-27, Grade 3 reads ≥ 60 wpm; SDG India Index 71, SDG 4 = 61; MP Pratibha Parv official scores inflated +38.9 pp (maths) / +33.8 pp (Hindi) vs re-tests (Singh, RISE WP 20/042); diagnostic feedback alone: no gain; MP governance reform: null (+0.031 SD); TaRL +0.15 SD (Haryana), +0.6–0.7 SD (UP camps); phone+SMS +0.121 SD (Botswana); Gunotsav external sample 25 % of schools per block; Haryana Saksham third-party test in all 119 blocks. Bounded novelty check: no prior combination of risk-scored census data + randomized re-tests + model-assisted correction + benchmarked SAE.
- **Real runs (synthetic children; commands in `eval/README.md`):** C5 at a 10 % budget, 5 seeds, simulator defaults: block MAE 4.09 ± 0.32 → 2.34 ± 1.09 pp; detection AUC 0.77; C4 baseline exact level accuracy 0.551 at 8 items; C7 Hindi WhatsApp plan 659 bytes, SMS 3 segments; C12 36/36. ASER calibration module added (`eval/sim/calibration.py`; simulator hits 0.234 / 0.276 exactly).
- **Honest negatives:** 120-school single-seed smoke test with 12 re-tests — moderation worsened block RMSE (5.4 → 7.7 pp) and 90 % intervals covered 0 %; C9 targeting showed no gain (441.2 vs 441.1 children, oracle 444) because simulated inflation barely reorders schools. C6 patched (precision-weighted benchmarking with anchor variance, 2 covariates) but not yet re-run at scale.
- **Corrections:** removed two figures written earlier from builder A's progress ("7.5 of 16 items", "26/26") because their provenance could not be re-checked after the agent record was lost; replaced with the verified ledger values above.
- **Process:** the API outage (02:50–05:00) and CPU saturation cost ~3 h. Agents that finished: r1n, r2b, r3n, r4n, data-extractor (ASER), builders A and B (B failed late but its code ran). The first-principles review had not returned by 08:05, so ADR 001 records it as pending.

### 2026-10-04 09:35 IST — Real-data analysis, novelty verdict, 6-page PDF check
- **Real data (27 states, ASER 2024 × PARAKH 2024 state reports):** reading/language ρ = 0.44, arithmetic/maths ρ = 0.26, mean rank gap ~7 places; Rajasthan 4th on PARAKH (70 %) vs 23rd on ASER (12.1 %) — both values verified at source. PARAKH → ASER leave-one-state-out MAE 9.21 vs 10.46 pp (reading), 7.55 vs 7.86 (maths). Reproduce: `python3 scripts/extract_parakh2024_state.py && python3 scripts/extract_udise2425_state.py && python3 scripts/real_data_analysis.py`. New tidy data: `data/public/parakh2024_grade3_state.csv` (70 rows), `udise2425_state.csv` (37 rows).
- **Novelty verdict:** all elements have precedent (exam-board moderation NESA/QCAA/KS2, IPA back-checks, RBF verification, validation-subsample correction, FH literacy SAE); the combination for Indian FLN census data is not found → claim adaptation/combination novelty only.
- **Proposal v0.3:** renders to exactly 6 A4 pages (Arial 11 pt, 1-inch margins; `scripts/render_proposal.py` + headless-browser print; check with pypdf), with the rendered architecture diagram. Removed one secondary source (Careers360) to fit. Placeholders left: team details only.

### 2026-10-04 10:05 IST — ASER-calibrated eval; case-register synthesis; PAUSE
- **Eval (seeds 1–5, synthetic, calibrated to ASER 2024 govt Std III 23.4 % / 27.6 %; `nice -n 10 python3 eval/run_eval.py`, completed 10:00):** block MAE teacher-reported 4.04 ± 0.32 pp → moderated (risk-PPS, 10 % budget) 2.46 ± 0.69 pp; detection AUC 0.767 ± 0.009; block RMSE raw 4.13 → audit-adjusted 2.71 → Fay–Herriot benchmarked 2.75 pp; 90 % CI coverage 0.00 / 0.30 / 0.27 (**under-covered**); |aggregate − anchor| 2.34 pp; allocation raw 444.3, moderated 443.5, oracle 447.5 children (**no targeting gain**). Proposal demo table updated.
- **First-principles review returned** (bottleneck = recorded → owned; prevalence targets punish honesty) → ADR 001 synthesis v2: a learning-case register (notify → owner → verified cure → missing cases), borrowing the TB programme's notification logic (NSP for TB Elimination 2017–25, p. 34, verified: incentives "to promote TB case notification, ensure treatment adherence and treatment completion"). Added to the proposal as "Accountability that rewards finding, not hiding"; removed the GEEAP row to stay within 6 pages.
- **Paused** per Supervisor 09:55. Resume point in *Now*.
