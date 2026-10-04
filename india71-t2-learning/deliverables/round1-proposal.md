# Ek Tasveer — one trusted picture of every child's foundational learning
### A NIPUN Bharat decision-support layer built on UDISE+, PARAKH, ASER and state assessments
*India @ 71/100 Challenge · Theme 2: Foundational Learning Outcomes · Round 1 proposal — draft v0.3 (4 Oct 2026)*

**Team:** ⟦Team name⟧ · **Team ID:** ⟦Team ID⟧ · **Institution(s):** ⟦…⟧ · **Contact:** ⟦email, phone⟧

---

## 1. Problem identification

**The scorecard.** India scores 71/100 on the SDG India Index 2023-24 and 61 on SDG 4 (Quality Education); the adjusted net enrolment rate in elementary education is 96.5 % [1]. NIPUN Bharat (launched 5 July 2021) commits to "universal FLN in primary schools by 2026-27": every child reads with meaning at **≥ 60 words a minute** and handles numbers to 9,999 by the end of Grade 3 [2]. **2026-27 is this school year.**

**The lived reality.** In rural **government** schools, **23.4 %** of Std III children can read a Std II-level text and **27.6 %** can do at least subtraction (ASER 2024) [3]. Both rose sharply from 2022 (16.3 % and 20.2 %), so the system *can* move — but three in four Grade 3 children in government schools still cannot read a Grade 2 text. In private schools the reading figure is 35.5 % [3].

**The measurable gap.** *Share of Grade 3 children in government schools who meet the Grade 3 reading and numeracy goals*: mission target 100 % in 2026-27 [2]; independently measured ≈ 23 % (reading) and ≈ 28 % (subtraction) [3].

**The underserved group.** Children in Grades 1–3 of rural government schools — 68.9 % of India's 14.71 lakh schools are government schools [4] — and, within them, those the data system sees least well: children in **1,04,125 single-teacher schools (33.8 lakh enrolled)** [4], Scheduled Tribe children — the lowest-scoring social group in PARAKH 2024 Grade 3 (maths 57 % vs 61 % for others) [7] — Scheduled Caste children, and children whose home language is not the language of instruction.

**The implementation gap — five breaks.** Data is not missing: UDISE+ has held student-wise records ("more than 60 fields for each student") since 2022-23 [4]; states run census-style FLN tests; Vidya Samiksha Kendras (VSKs) run dashboards. Yet the chain *recorded → believed → acted on → rechecked* breaks at five points:

| Break | Today | Consequence |
|---|---|---|
| **Commensurability** | PARAKH 2024 reports Grade 3 children answering ~64 % of language items correctly [7]; ASER 2024 reports 23.4 % of government-school Std III children reading a Std II text [3]. Both are right — they measure different things — but no system links them | Teacher, block and state see different pictures |
| **Trust** | Census-style tests are often "proctored and graded by teachers in the same school"; Madhya Pradesh's Pratibha Parv (~6–7 million students) was shown to "mislead inferences about learning levels" [5] | Officials cannot tell progress from reporting pressure |
| **Granularity** | Trustworthy surveys (ASER, PARAKH) are samples | Silent about a block, a school, a child |
| **Actionability** | Outputs are averages and "% NIPUN" | Nobody is told *which children, which skill, which activity, this week* |
| **Closed loop** | Actions are not logged or rechecked | Nobody learns what worked |

## 2. Evidence and context

| Evidence | Finding | Source |
|---|---|---|
| ASER 2024 (rural, household, one-on-one oral test) | Std III govt: reading Std II text 20.9 % (2018) → 16.3 % (2022) → 23.4 % (2024); subtraction 20.2 % (2022) → 27.6 % (2024) | [3] |
| Foundational Learning Study 2022 (NCERT; ~86,000 Grade 3 students, 10,000 schools, 20 languages) | Numeracy: 37 % limited, 42 % sufficient, 10 % superior skills | [6] |
| PARAKH Rashtriya Sarvekshan 2024 (21,15,022 children, 74,229 schools, 781 districts; Grade 3: 5,99,026 students) | Grade 3 average score, language / maths: rural 64 % / 60 %; **ST children lowest at 61 % / 57 %** vs 66 % / 61 % for others; weakest maths competencies (shapes, money) at 50 % | [7] |
| **Official-data audit, Madhya Pradesh** (re-test in 283 schools) | Official census scores inflated by **+38.9 pp (maths)** and **+33.8 pp (Hindi)** over independent re-test levels of 25.1 % and 37.9 %; in Andhra Pradesh, paper tests inflated by 16–20 pp, while tablet-based tests (≈ US$0.50 per test) mostly removed the distortion | [5] |
| Diagnostic feedback to teachers, Andhra Pradesh (RCT) | Reports on their pupils' results alone: no detectable learning gain | [13] |
| School-governance reform, Madhya Pradesh (RCT, 1,774 schools) | High compliance with ratings and improvement plans; learning effects null (maths +0.031 SD, Hindi +0.004 SD) | [14] |
| Teaching at the Right Level (six RCTs, seven states) | Haryana +0.15 SD (language); Uttar Pradesh learning camps +0.6–0.7 SD; scaled to "over 60 million students" | [8], [15] |
| Phone + SMS targeted instruction, Botswana (RCT) | +0.121 SD numeracy; SMS alone +0.024 SD (not significant) | [16] |
| Global Education Evidence Advisory Panel (2023) | "Targeting teaching instruction by learning level, not grade" is a *Great Buy* | [17] |

**Design lesson.** Reports and ratings produced compliance, not learning [13], [14]; unverified official numbers were off by over 30 points [5]; diagnosis that becomes a grouped, level-appropriate action works [8], [15], [16]. So the layer must make numbers trustworthy and end every diagnosis in an action.

## 3. Existing ecosystem — why the gap persists

| System (deployed) | What it does | What it leaves undone |
|---|---|---|
| **UDISE+** [4] | School census + student-wise records since 2022-23 | No learning levels |
| **VSKs** (Gujarat: 54,000 schools, 1.15 crore students, per officials [9]) | Command-centre dashboards: attendance, assessments | Monitoring, not a classroom action; no causal evaluation found |
| **State FLN assessments + verification** — Haryana *Saksham Ghoshna*: a block is "Saksham" if > 80 % of students score > 50 %, checked by a third-party test in all 119 blocks [10]; Gujarat *Gunotsav*: 3,000 senior officials assess "25% schools from all the blocks" [19]; UP: NIPUN app with external verification [20] | Census data + verification | Verification grades schools or blocks; it is not used to *calibrate* the data, so it must be huge |
| **AI oral reading** — Wadhwani AI Vaachan Samiksha, ~30,000 Gujarat schools (developer figures) [11] | Tamper-resistant fluency scores | No independent accuracy check found; no remediation plan |
| **TaRL** (Pratham) [8]; chatbots such as SwiftChat in 14 states (vendor figures) [12] | Assess → group → activities; delivery channels to teachers | Needs a light, recurring diagnostic and follow-up at scale |

**Why the gap persists.** Data pipes scaled; verified impact did not. Teacher-graded data is fragile, so states verify by brute force, and verification samples are not used as measurement. Dashboards monitor; few systems turn a diagnosis into next week's activity.

## 4. Proposed solution — "one picture, two loops"

Ek Tasveer is **not a new app**. It is a thin decision layer that plugs into what states run — UDISE+ for master data, the state assessment app for capture, the VSK for dashboards, DIKSHA for content, WhatsApp/SMS/IVR for delivery — and adds the five missing links through 12 components with typed, open contracts (JSON Schema), so a state can adopt one component at a time.

```mermaid
flowchart LR
  U[UDISE+ codes, enrolment,<br/>student-wise records] --> C2
  S[State assessment app] --> C2
  K[Classroom checks<br/>WhatsApp / IVR / ORF] --> C2
  P[PARAKH / ASER] --> C6
  C2[Canonical model<br/>+ pseudonyms] --> C4[Adaptive diagnostic]
  C3[NIPUN competency<br/>crosswalk] --> C4
  C4 --> C7[Monday plan<br/>WhatsApp / SMS / IVR]
  C7 --> C11[Action ledger<br/>+ 6-week recheck]
  C2 --> C5[Measurement assurance<br/>rotating re-tests]
  C5 --> C6[Block estimates<br/>+ intervals]
  C6 --> C9[Allocation + SMC page]
  C6 --> V[VSK dashboard]
  C11 --> C9
```

**Loop 1 — the classroom, weekly.** A teacher runs a few-minute oral check per child on the NIPUN-aligned ladder (letter → word → Grade 1 text → Grade 2 text; numbers → subtraction → division). An adaptive engine stops as soon as it is ≥ 90 % sure of the child's level and returns a **Monday plan**: TaRL groups, one activity per group from the state's own content, and the competency to recheck in four weeks — as one WhatsApp message, ≤ 3 SMS, or an IVR call in the local language. Names stay on the teacher's phone; the system holds only pseudonyms.

**Loop 2 — the system, termly ("measurement assurance").** We borrow the idea of *moderation* — checking a sample of school-assessed results against an independent assessment — and use the sample to *calibrate*, not to grade. Each term a small, rotating sample of schools — chosen by statistical uncertainty and decision value, always with a random component, so every school has a known inclusion probability — is re-tested by the cluster coordinator during the regular academic-support visit, who then coaches that group. A model-assisted estimator calibrates every school's reported results; small-area estimation with UDISE+ covariates then gives **block numbers with intervals that add up to the PARAKH/ASER anchor**. No school-level "trust label" is published: the aim is a true picture, not blame.

**Decisions it feeds.** CRC weekly visit plans; block/district allocation of remedial camps and training, ranked by expected children helped and weighted for single-teacher schools and SC/ST share; a one-page pictorial summary for each School Management Committee; interval-backed evidence for district Samagra Shiksha plans.

**Governance and standards.** Keys: UDISE+ school code, LGD codes, a salted pseudonym of the student ID; competency codes from the NIPUN Lakshya Soochi. Role- and purpose-bound access: child-level data only on the teacher's device; cells with < 10 children suppressed; school-level moderation data only for the moderation team. The DPDP Act 2023 requires verifiable parental consent for children's data and bars "tracking or behavioural monitoring of children" unless rules exempt a class of processing (s. 9) [18]; the design holds either way, with pseudonymised, purpose-bound server records and consent captured at enrolment where required. NIPUN asks for "IT based solutions … field level child wise monitoring" built on DIKSHA, UDISE+ and NDEAR standards [2] — this is that layer.

**Working demo (real runs; synthetic children — no real child data used).** A simulated district (6 blocks, ~600 government primary schools) in which ~30 % of schools inflate teacher-reported results; code, seeds and commands in the repository (`eval/run_eval.py`, `components/*/evaluate.py`).

| Result (first runs, 4 Oct 2026) | Value |
|---|---|
| Adaptive check capped at 8 of 16 items: exact level accuracy (5 levels, both subjects, seeds 101–105) | 0.551 — baseline for the auto-research loop |
| Monday plan for a class of 60, Hindi WhatsApp | 659 bytes; SMS version 3 segments; IVR script |
| Block error of "% meeting goal", teacher-reported vs moderated (10 % of schools re-tested; 5 seeds) | 4.09 ± 0.32 pp → 2.34 ± 1.09 pp |
| Detecting inflating schools (AUC) from public signals only | 0.77 |
| Governance policy tests (`components/governance/evaluate.py`) | 36 / 36 pass |

**Honest limits.** In a small district (120 schools, 12 re-tested; one seed) moderation *increased* block error (5.4 → 7.7 pp) and intervals under-covered, so the minimum effective sample and calibrated intervals are our next targets; allocation gains are not yet shown. The 5-seed figures used the simulator's default calibration (25 % / 30 %); the ASER-calibrated re-run (23.4 % / 27.6 %) is pending.

## 5. Feasibility and implementation roadmap

| Phase | Scope | What happens | Exit criterion |
|---|---|---|---|
| 0 (3 months) | 1 district, 2 blocks, clusters staggered | Loop 1 in Grades 1–3; Loop 2 at a 10 % rotating sample; staggered start gives a causal comparison | Teachers use the plan weekly; moderated vs reported gap measured |
| 1 (1 year) | 1 state via its VSK | Connectors to the state assessment app and UDISE+; SMC pages; AWP&B evidence | Block estimates with intervals in the state's planning cycle |
| 2 (2–3 years) | Multi-state | Open contracts and components offered as digital public goods | Adopted component-by-component |

**People and time (design estimates).** Teacher: one short oral check per child per term and one message a week. CRC: at a 10 % rotating sample, a block of 100 schools needs 10 school re-tests per term — about 12 children each, inside visits the CRC already makes. Block/district: the existing monthly review uses the moderated numbers. **Costs:** no new devices; SMS/IVR as fallback; tablet-based re-testing was costed at about US$0.50 per test in the Andhra Pradesh study [5]. **Risks → mitigations:** teacher workload → short adaptive checks; language → per-language validation of items and AI scoring; connectivity → offline-first, SMS/IVR; gaming → rotation, random component, no published labels; privacy → pseudonyms, suppression, purpose limits.

## 6. Expected impact and scalability

**Beneficiaries.** Grade 1–3 children in government schools of the pilot district, then the state (counted from UDISE+ grade-wise enrolment).
**Outcome indicators.** Share of Grade 3 children meeting the reading and numeracy goals at block level, with intervals, every term; teacher minutes per child; share of actions rechecked within six weeks; gap between reported and moderated figures.
**Expected effect and scale.** TaRL-style grouping has strong RCT support [8]; the staggered pilot measures our effect rather than assuming it. No new hardware or app: the layer runs on the state's VSK, uses UDISE+ identifiers and speaks WhatsApp/SMS/IVR.

## References
1. NITI Aayog, SDG India Index 2023-24 (PIB). https://pib.gov.in/PressReleaseIframePage.aspx?PRID=2032857 ; SDG 4 score: https://static.pib.gov.in/WriteReadData/userfiles/image/image010QARO.jpeg
2. Ministry of Education (2021). *NIPUN Bharat*, pp. 2, 5, 12, 29. https://static.pib.gov.in/WriteReadData/specificdocs/documents/2021/jul/doc20217531.pdf
3. ASER Centre (2025). *Annual Status of Education Report (Rural) 2024*. https://asercentre.org/wp-content/uploads/2022/12/ASER_2024_Final-Report_13_2_24-1.pdf
4. Ministry of Education. *UDISE+ 2024-25*, pp. 10, 28–32. https://dashboard.udiseplus.gov.in/report-new-v.11-demo2025/static/media/UDISE+2024_25_Booklet_existing.118ba29d4773e6372f72.pdf
5. Singh, A. (2020). *Myths of Official Measurement*. RISE WP 20/042, pp. 1–5. https://riseprogramme.org/sites/default/files/2020-11/RISE_WP-042-Singh.pdf
6. Rajya Sabha Unstarred Q. 3224 (Foundational Learning Study 2022). https://sansad.in/getFile/annex/259/AU3224.pdf?source=pqars
7. NCERT (2025). *PARAKH Rashtriya Sarvekshan 2024, National Report*, pp. 1–4. https://parakh.ncert.gov.in/sites/default/files/2025-07/REPORT_India_IND.pdf
8. J-PAL. *Teaching at the Right Level* (case study). https://www.povertyactionlab.org/case-study/teaching-right-level-improve-learning
9. Careers360 (citing Gujarat officials). https://news.careers360.com/focus-on-quality-learning-fund-allocation-have-transformed-gujarats-education-sector-officials
10. Govt. of Haryana. *The Saksham Haryana programme*. https://www.prharyana.gov.in/en/the-saksham-haryana-programme-an-initiative-of-haryana-school-education-department-which-has-been-0
11. Wadhwani AI. *Vaachan Samiksha*. https://www.wadhwaniai.org/vaachan-samiksha-leveraging-ai-to-bridge-the-literacy-divide/
12. AWS (2023), ConveGenius SwiftChat press release. https://press.aboutamazon.com/in/2023/9/convegenius-builds-swiftchat-conversational-ai-platform-on-aws-to-improve-education-for-100-million-students
13. Muralidharan & Sundararaman (2010). Diagnostic feedback to teachers. *Economic Journal* (J-PAL summary): https://www.povertyactionlab.org/print/pdf/node/702092
14. Muralidharan & Singh. *Improving Public Sector Management at Scale?* NBER WP 28129. https://www.nber.org/system/files/working_papers/w28129/w28129.pdf
15. Banerjee et al. (2016). *Mainstreaming an Effective Intervention: TaRL in India*. https://www.povertyactionlab.org/sites/default/files/research-paper/TaRL_Paper_August2016.pdf
16. Angrist, Bergman & Matsheng (2022). *Nature Human Behaviour*. https://www.nature.com/articles/s41562-022-01381-z.pdf
17. GEEAP (2023). *Smart Buys*. https://documents1.worldbank.org/curated/en/099008110232520373/pdf/IDU-9401bfdd-f4ff-486b-84b4-570be4f65543.pdf
18. *Digital Personal Data Protection Act, 2023*, s. 9.
19. Govt. of Gujarat. *Gunotsav — About*. https://gunotsav.gujarat.gov.in/aboutus.html
20. UP NIPUN external assessment RFP (GeM). https://bidplus.gem.gov.in/bidding/bid/downloadBuyerDoc/5579037/17001372817746.pdf

All sources accessed 4 Oct 2026; quotes and page numbers in `research/sources/`.
