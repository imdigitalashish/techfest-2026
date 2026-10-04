# India @71/100 · Theme 2: Foundational learning outcomes — Thought Node

> Journal for `india71-t2-learning/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** ✅ DONE for the Supervisor's definition of done (2026-10-04 16:42 IST). Round-1 deliverable final: [`deliverables/India71_100_[TeamID].pdf`](deliverables/India71_100_[TeamID].pdf) (source [`round1-proposal.md`](deliverables/round1-proposal.md) v1.1).
- **Evidence state:** two pre-registered held-out PASSes — v1 ([prereg](eval/preregistration/2026-10-04-coverage.md), seeds 101–130): coverage 96.7 % of nominal 90 %, ±6.0 pp, MAE 4.31 → 2.16 pp; v2 with code-review design fixes ([prereg](eval/preregistration/2026-10-04-coverage-v2.md), seeds 201–230): 96.7 %, MAE 4.17 → 2.10 pp. Honest negatives: camp targeting with moderated school figures — no gain (v1), worse (v2, 5 % budget); raw reports rank blocks as well as moderated ones (moderation fixes level, not ranking). All SYNTHETIC.
- **Reviews:** gpt-6-astra v0.3 (25 issues, 24 accepted), v1.0 re-review 6/7/5/6/5/5 = 34/60, no blocking (4 new majors fixed in v1.1); gpt-6-sol code + eval (12 issues, all accepted; blocking governance bypass fixed; numbers reproduced byte-identical). Ledger: [`reviews/ledger.tsv`](reviews/ledger.tsv).
- **Next (only if T2 is chosen on 12 Oct):** the 13 partly-resolved review items need pilot-state decisions (district, sponsor, procurement, power calculation, field precision targets, device security); a real pilot partner; first auto-research iterations on seeds 1–30 with confirmations on fresh seeds.
- **Needs from user:** Register by 15 Oct for one India@71 theme — memo below recommends **T1**. Teammates (≤ 4); team name, Team ID, institution and contact for the PDF header; rename the PDF to `India71_100_<TeamID>.pdf`.
- **Risks:** synthetic-only evidence; heavy institutional asks (state order for protected period + firewall, cross-cluster assessors, anchor survey); a policy jury may see measurement, not learning.

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
- 2026-10-04 — [ADR 001](architecture/adr/001-spike.md): two loops — Spike 1 classroom loop (C4 → C7 → C11), Spike 2 non-punitive measurement assurance (C5 + C6). Addendum v3 (16:0x): learning-support record replaces the case/cure register; dominant-strategy claim withdrawn; allocation demoted (pre-registered: no gain).
- 2026-10-04 — Interval method frozen and pre-registered before held-out data ([pre-registration](eval/preregistration/2026-10-04-coverage.md), author time 15:44:58 IST): misclassification correction from a double-assessed subsample, children-weighted HT stratum bias, Fay–Herriot model on the bias, precision-weighted same-construct anchor, full-pipeline parametric bootstrap.
- 2026-10-04 — Benchmark only to a same-construct, same-population, same-term survey; never to PARAKH scale scores or old ASER rounds (hostile-judge issue 6).
- 2026-10-04 — Simulator vectorised (1.6 s vs ~90 s per district; distributions matched to the loop version over 9 vs 40 seeds); all results regenerated.

## Components
Full specs: [architecture/components.md](architecture/components.md) · contracts: [architecture/contracts/fln_contracts.py](architecture/contracts/fln_contracts.py)

| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | Source connectors | sources → raw rows + Provenance | state ETL / VSK ingestion | no | spec | ingest validation pass rate |
| C2 | Canonical model & identity | raw → School/Student/Response | Ed-Fi/CEDS-style, UDISE+/LGD codes | no | built (first pass) | validation pass rate; linkage F1 |
| C3 | Competency framework & crosswalk | docs/items → Competency/Item (Q-matrix) | SCERT expert mapping | no | built (first pass) | κ vs expert Q-matrix |
| C4 | Diagnostic engine | Responses → ChildDiagnosis | ASER highest-level rule | **spike 1** | built; frozen dev cut-points: CAT@8 0.538 vs full 0.592 vs ASER rule 0.486 (seeds 101–105) | exact level accuracy at 8 items |
| C5 | Measurement assurance | reported results → block estimates + intervals | Gunotsav / Saksham verification | **spike 2** | **pre-registered PASS**: coverage 0.967 (nominal 0.90), MAE 2.16 vs 4.31 pp (held-out 101–130) | block MAE s.t. coverage ≥ 0.85 |
| C6 | Linking + small-area estimation | bias residuals + anchor → block estimates | direct averages | part of spike 2 | Fay–Herriot on the bias + precision-weighted benchmark | coverage; MAE |
| C7 | Teacher point-of-use | ChildDiagnosis → TeacherPlan | state apps / chatbots | **spike 1** | built; 801 B Hindi, 3 SMS, IVR; printed default | payload bytes; SMS segments |
| C8 | CRC visit planner | AreaEstimate + trust → VisitPlan | rota | no | spec | need-weighted coverage |
| C9 | Allocation & policy feedback | estimates → AllocationDecision | enrolment-proportional | demoted | **no gain shown** (pre-registered; worse at 5 % budget) | below-goal children reached vs raw / oracle |
| C10 | Dashboards | estimates → HTML/JSON | VSK dashboards | no | rebuilt: block estimates + intervals, no school labels | disclosure pass rate; KB |
| C11 | Action ledger & outcome loop | ActionRecord → effects | none | no | spec | % actions with outcome in 6 wks |
| C12 | Governance & access | AccessRequest + trusted server context → AccessDecision | role portals | no | fail-closed; 42/42 incl. 5 forged-request cases; wired into the dashboard | policy suite pass rate |

## Selection memo (FINAL — 2026-10-04 16:42 IST; theme decision 12 Oct, registration by 15 Oct)
_Honest case for or against T2 against T1 (✅, 4.2/5, the default pick) and T3 (✅, 3.9/5, recommends T1). Scores 1–5 with one line of evidence each._
- **Winnability — 3/5.** The evidence chain is verified at primary sources:
  - ASER 2024: 23.4 % of rural govt Std III children read a Std II text (a proxy, not NIPUN attainment);
  - teacher-graded census scores in MP were +38.9 pp above re-tests;
  - NAS state averages are "likely artificially high";
  - the MoE itself says its systems work "in silos".
  The same hostile judge scored our v1.0 at **34/60, equal to T3's v1.0** (T1 was not numerically scored). Theme 2 will draw many ed-tech pitches. Our distinctive asset is statistical, and that is harder to sell to a policy jury than T1's "children flagged before severe wasting".
- **Innovation headroom — 4/5.** Measurement assurance passed **two pre-registered held-out tests** (v1 and the code-review-corrected v2): conservative 90 % intervals (96.7 % coverage, ±6 pp) and block error roughly halved (SYNTHETIC). Novelty is adaptation/combination (moderation + back-checks + misclassification correction + Fay–Herriot on the bias), per a bounded search.
- **Feasibility by the deadline — 5/5.** The final-format PDF exists today: 6 pages, Arial embedded, ≥ 11 pt, `check_docs` 17/17. Round 1 needs only team details from the user, all outside the 19–25 Nov exams.
- **Demo strength at finals — 3.5/5.**
  - Have: block dashboard with intervals (no school labels, C12 suppression), Hindi WhatsApp/SMS/IVR plan, pre-registered results, real ASER × PARAKH × UDISE+ state analysis.
  - Missing: real child data. The main honest finding (moderation fixes the *level*, not the *ranking*) is subtle, and the adaptive check is modest (0.538 exact level at 8 items).
- **Fit with the user's strengths — 4/5.** Statistics, data systems, privacy engineering; Azure for a VSK-hosted pilot.
- **Overall — 3.9/5** (mean of the five) vs **T1 4.2**, **T3 3.9**.
- **Biggest risk:** the institutional ask is heavy — a state order for a protected period and a personnel-use firewall, cross-cluster assessors, and a same-construct anchor survey. Education juries are sensitive to anything that looks like policing teachers.
- **Recommendation: keep T1.** T2 is the stronger reserve on evidence quality: two pre-registered passes, a verified inflation literature and real-data analysis. Prefer it only if the user wants education and can find a state/SCERT partner for a phase-0 district before 1 Nov.
- **One-line pitch:** "Schools already test every Grade 3 child, but no one can trust or act on the numbers. Ek Tasveer gives each teacher a weekly group plan and gives officials moderated block numbers with honest intervals — in two pre-registered tests on simulated districts it halved block error without labelling a single school."

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

### 2026-10-04 09:54 IST — ASER-calibrated eval; case-register synthesis; PAUSE
- **Eval (seeds 1–5, synthetic, calibrated to ASER 2024 govt Std III 23.4 % / 27.6 %; `nice -n 10 python3 eval/run_eval.py`, completed before 09:52):** block MAE teacher-reported 4.04 ± 0.32 pp → moderated (risk-PPS, 10 % budget) 2.46 ± 0.69 pp; detection AUC 0.767 ± 0.009; block RMSE raw 4.13 → audit-adjusted 2.71 → Fay–Herriot benchmarked 2.75 pp; 90 % CI coverage 0.00 / 0.30 / 0.27 (**under-covered**); |aggregate − anchor| 2.34 pp; allocation raw 444.3, moderated 443.5, oracle 447.5 children (**no targeting gain**). Proposal demo table updated.
- **First-principles review returned** (bottleneck = recorded → owned; prevalence targets punish honesty) → ADR 001 synthesis v2: a learning-case register (notify → owner → verified cure → missing cases), borrowing the TB programme's notification logic (NSP for TB Elimination 2017–25, p. 34, verified: incentives "to promote TB case notification, ensure treatment adherence and treatment completion"). Added to the proposal as "Accountability that rewards finding, not hiding"; removed the GEEAP row to stay within 6 pages.
- **Paused** per Supervisor 09:55. Resume point in *Now*.

### 2026-10-04 16:06 IST — Resumed: pre-registered calibration PASS; proposal v1.0; reviews
- Simulator vectorised (1.6 s vs ~90 s per district); distribution check vs the loop version over 9 vs 40 seeds (inflation gap 0.1530 vs 0.1532; item p 0.445 vs 0.436).
- Interval work on dev seeds 1–30 only: legacy 0.27 coverage traced to (i) clipping of misclassification-corrected re-test shares at 0 (truncation bias in low strata), (ii) school- instead of children-weighted bias, (iii) block-level deviations of reporting bias (a district-wide model over-corrects honest high-performing blocks; errors up to −10 pp). Fix: Fay–Herriot model on the bias + full-pipeline parametric bootstrap with block effects (adjusted likelihood keeps τ² > 0). Dev 1–30: coverage 0.928, MAE 2.30 vs 4.08 pp.
- **Pre-registration** committed 15:44:58 IST (`eval/preregistration/2026-10-04-coverage.md`), pushed before any held-out run. Held-out 101–130 (180 blocks): **coverage 0.967** (Wilson 0.929–0.985), MAE 2.16 vs 4.31 pp, half-width 5.97 pp → PASS. Secondaries: numeracy 0.928; budget 5 % ±8.34 pp / 20 % ±4.24 pp; need-correlated inflation 0.967. Allocation (effect-free metric): **gain not shown** in any scenario; at 5 % budget moderated targeting is worse (−13.4 children, CI −20.8 to −6.0); even the oracle beats raw by only ~1.2–1.5 % because school size dominates the score.
- Exploratory (labelled): 55 % of blocks' intervals sit clearly above/below the district average, 100 % on the correct side; true within-district spread ≈ 25 pp — answers the Supervisor's "does ±6 pp separate blocks?".
- Hostile judge (gpt-6-astra, max) on v0.3: 25 issues (4 blocking), scores 4/6/4/4/3/3. Accepted 24 (rejected only invented rupee prices) → proposal v1.0: ASER as proxies not NIPUN attainment; same-construct anchoring only; learning-support record + firewall replaces case/cure; verified DPDP timeline and exemption; responsibility chain + phase-0 gates; cluster-randomised phase 1; allocation demoted.
- Verified at primary sources: DPDP G.S.R. 843(E) and Rules 2025 Rule 12/Fourth Schedule; VSK (AU349: "working in silos"); Johnson & Parrado; Berry et al. (via authors' VoxDev summary); Aiyar & Bhattacharya (publisher abstract). NDEAR: UNVERIFIED (hosts unreachable).
- Final PDF `deliverables/India71_100_[TeamID].pdf`: 6 pages, A4 595×842, Arial only, embedded, min glyph 11 pt (`python3 deliverables/build_pdf.py --check`); Chromium had been shrinking pages 2.5 % because of unbreakable URLs — fixed.

### 2026-10-04 16:42 IST — Reviews processed; v2 pre-registered PASS; proposal v1.1 final; DONE
- **gpt-6-sol (code + eval):** reproduced the headline byte-for-byte (174/180 = 0.967; MAE 2.157 vs 4.310). 12 findings, all accepted:
  - BLOCKING governance bypass via caller text → fail-closed `TrustedContext`, 42/42 incl. forged requests;
  - dashboard now routes cells through C12 suppression;
  - C4 cut-points no longer derived from held-out truth (frozen from dev worlds; C4 now 0.538 / 0.592 / 0.486);
  - incomplete audits raise instead of publishing;
  - `truth_block` children-weighted; contract and allocation-API wording.
  The registered v1 command re-run after the fixes gives identical JSON and CSV.
- **v2 pre-registration** committed 16:31 IST (exact-π systematic PPS, assessor-error variance, pooled 20 % double checks), pushed before running fresh seeds 201–230.
  - Language PASS: coverage 0.967, MAE 2.10 vs 4.17 pp, ±6.0 pp; numeracy 0.956.
  - Allocation with moderated school figures is **worse** than raw (−8.1, CI −13.5 to −2.8). So school figures are not used for targeting.
- **Post hoc (labelled):**
  - district-clustered CI for v1 coverage: 93.3–98.9 %;
  - with a child-weighted district average, 97/180 blocks are clearly above or below it, all on the correct side;
  - matched baseline: raw reports rank blocks as well (98 % vs 97 %), so moderation fixes level, not ranking.
- **gpt-6-astra re-review of v1.0:** 6/7/5/6/5/5 = 34/60, no blocking. N1–N4 and its top-3 fixes went into v1.1: the double-rater assumption plus an audio check, the clustered CI, an anchor supplier, the matched baseline, a pilot operating box, source-bounded ecosystem wording, the 2026-27 inference, and a phase-1 comparator. 13 partly-resolved items are deferred to Round 2 with reasons.
- **Final PDF:** 6 pages, A4, Arial embedded, min 11 pt; `check_docs` 17/17. Selection memo final: **recommend T1**; T2 is the reserve.
