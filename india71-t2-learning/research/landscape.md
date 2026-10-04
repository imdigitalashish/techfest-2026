# Landscape — India's FLN data ecosystem: state of the art and what is deployed today

> Theme 2, India @71/100 (Techfest 2026). Lead synthesis, 4 Oct 2026 07:10 IST. Every number below carries its source; the detailed evidence (quotes, page numbers) is in [`sources/`](sources/). **UNVERIFIED** marks anything we could not open at a primary source. Access date for all sources: 2026-10-04.

## 1. The scorecard vs. the lived reality

| Indicator | Value | Source |
|---|---|---|
| SDG India Index 2023-24, composite score | 71 | PIB, https://pib.gov.in/PressReleaseIframePage.aspx?PRID=2032857 ("Overall SDG score for the country is 71 for 2023-24") |
| SDG 4 (Quality Education) score 2023-24 | 61 | PIB infographic, https://static.pib.gov.in/WriteReadData/userfiles/image/image010QARO.jpeg |
| Adjusted net enrolment rate, elementary (SDG 4 indicator) | 96.5 % | PIB PRID=2032857 |
| NIPUN Bharat goal | "Achieving universal FLN in primary schools by 2026-27"; "every child achieves the desired learning competencies … at the end of Grade III and not later than Grade V" | NIPUN Bharat launch document, MoE (July 2021), pp. 2, 5: https://static.pib.gov.in/WriteReadData/specificdocs/documents/2021/jul/doc20217531.pdf |
| NIPUN Bharat goal as restated to Parliament | FLN "by Grade 2 by 2026-27" | Rajya Sabha Unstarred Q. 523, answered 7 Feb 2024 (local copy `.data/nipun_parliament_AU523.pdf`; URL to be recorded) |
| Grade 3 learning goals (Lakshya Soochi) | reads with meaning ≥ 60 words/min; reads and writes numbers to 9,999; simple multiplication | NIPUN launch document p. 12 |
| **Std III, rural government schools: can read a Std II text** | **23.4 % (2024)**; 16.3 % (2022); 20.9 % (2018) | ASER 2024 national report, p. 24 of text ("increased from 16.3% in 2022 to 23.4%"): https://asercentre.org/wp-content/uploads/2022/12/ASER_2024_Final-Report_13_2_24-1.pdf |
| **Std III, rural government schools: can do at least subtraction** | **27.6 % (2024)**; 20.2 % (2022) | ASER 2024, same page ("from 20.2% to 27.6% — in government schools") |
| Std III, rural private schools: can read a Std II text | 35.5 % (2024) | ASER 2024 ("from 33.1% to 35.5%") |
| Grade 3 numeracy, Foundational Learning Study 2022 | 37 % limited, 42 % sufficient, 10 % superior skills (~86,000 Grade 3 students, 10,000 schools, 20 languages) | Rajya Sabha AU3224: https://sansad.in/getFile/annex/259/AU3224.pdf?source=pqars |
| PARAKH Rashtriya Sarvekshan 2024, Grade 3 (21,15,022 children in 74,229 schools, 781 districts) | average score language / maths: boys 63/60, girls 65/60, rural 64/60, urban 63/59; SC 64/60, **ST 61/57**, OBC 63/60, others 66/61 | PARAKH national report pp. 1–4, https://parakh.ncert.gov.in/sites/default/files/2025-07/REPORT_India_IND.pdf (via `sources/official-data.md`) |

**Reading the gap.** The scorecard counts enrolment and inputs (ANER 96.5 %, PTR 18) and the mission sets a 2026-27 deadline; the independent measure says fewer than one in four Grade 3 children in rural government schools can read a Grade 2 text. 2026-27 is the current school year.

## 2. The data the system already holds (UDISE+ 2024-25)
Source: UDISE+ 2024-25 report, https://dashboard.udiseplus.gov.in/report-new-v.11-demo2025/static/media/UDISE+2024_25_Booklet_existing.118ba29d4773e6372f72.pdf (pp. 10–32).
- 1,471,473 schools; 246,932,680 enrolments; 10,122,420 teachers; 1,013,322 government schools (68.9 %).
- 104,125 single-teacher schools with 3,376,769 enrolments; 7,993 schools with zero enrolment (20,817 teachers in them); PTR at primary 20.
- Student-wise data since 2022-23: "more than 60 fields for each student" and "a separate unique educational ID (EID) for every student" (p. 10). The report itself names "attendance, learning outcomes" as things student-wise data enables monitoring of; in the fields we could see, **learning levels are not collected by UDISE+** (to be confirmed against the 2024-25 data capture format).

## 3. What is deployed today
Detail and quotes: [`sources/deployed-states-ngos.md`](sources/deployed-states-ngos.md), [`sources/methods-sae-audit.md`](sources/methods-sae-audit.md).

| System | What it does with FLN data | Scale (source) | Evidence of learning impact | Gap it leaves |
|---|---|---|---|---|
| Vidya Samiksha Kendras (state command centres; Gujarat first) | Attendance, assessment and scheme data on dashboards | Gujarat: 54,000 schools, 4 lakh teachers, 1.15 crore students (Careers360 citing officials — secondary); national VSK toolkit by ConveGenius: 9.5 M teachers, 1.5 M schools, 14 states (AWS press — vendor claim) | No causal evaluation found | Monitoring, not a classroom action; no independent check on teacher-entered data |
| Gujarat Gunotsav | School accountability incl. learning outcomes: self-evaluation of 100 % of schools, then external evaluation of ~9,000 schools by ~3,000 senior officials ("25% of schools in each block") | Official Gunotsav pages (methods-sae-audit.md) | None found | Large, costly external sample; used for grading schools |
| Haryana Saksham Ghoshna | A block is declared "Saksham" if "more than 80% students score over 50% marks"; third-party assessment in all 119 blocks; "mass cheating" can disqualify a block | Haryana PR page (methods-sae-audit.md) | None found | Threshold claims verified by a full third-party census — expensive |
| Uttar Pradesh NIPUN assessment | NIPUN Lakshya app; verification by DIET trainees; RFP for an "independent, high-quality external agency" with audit subsamples | DIET trainees: 8,000 (partner blog — secondary) | None causal found | Verification not linked to a statistical estimator |
| Madhya Pradesh Pratibha Parv (historic) | Census-style test, "proctored and graded by teachers in the same school" | "∼6-7 million students, across 110,000 schools"; audit: "official assessments thus mislead inferences about learning levels" (A. Singh, *Myths of Official Measurement*, RISE WP) | Negative for data validity | The cautionary tale our moderation layer is built around |
| Assam Gunotsav | Teacher marking with external evaluators who sample-check / re-evaluate; OMR scanning | Rounds 2017, 2018, 2022, 2023, 2024 | None found | Sample-check results not used to calibrate estimates |
| Wadhwani AI Vaachan Samiksha | AI oral-reading-fluency assessment (words per minute), geotagged and tamper-resistant | ~30,000 Gujarat schools, 120,000 teachers, 2.5 M students (developer claims) | No independent accuracy-vs-human validation found | Measures fluency; needs per-language validation; not a remediation plan |
| ConveGenius SwiftChat | WhatsApp-style bots and VSK dashboards for states | >100 M students, 14 states (AWS press) | None independent found | Delivery channel; diagnosis-to-action logic is the state's |
| Pratham Teaching at the Right Level | Simple oral assessment → group by level → targeted activities | "over 60 million students"; "six randomized evaluations in seven states"; UP learning camps "doubled the number of children who could read a paragraph or story" (J-PAL case study) | Strongest causal evidence | Works "when implemented systematically"; needs a light, recurring diagnostic |
| Microsoft Research Shiksha Copilot (Karnataka) | GenAI lesson-plan help for teachers | 789 of 1,043 registered teachers used it (75.6 %) | No learning outcome measured; Kannada quality gap | Generation in Indian languages needs human QA |

**Why the gap persists (evidenced patterns).**
1. *Scale is easier than verified impact:* production data pipes everywhere; independent learning-impact evaluations almost nowhere.
2. *Teacher-administered data is fragile:* the MP audit shows census tests graded in-school mislead; states respond with costly full third-party censuses (Haryana) or very large external samples (Gunotsav, 25 % of schools per block).
3. *Verification is not used as measurement:* sample checks decide pass/fail or grade schools; none we found feeds a statistical estimator that calibrates every school's reported data.
4. *Actionability is uneven:* TaRL ties diagnosis to a grouped action; dashboards mostly monitor.
5. *Language and localisation are bottlenecks* for AI tools (Shiksha Copilot, ORF).

## 4. Methods state of the art (what we reuse)
Detail: [`sources/methods-sota.md`](sources/methods-sota.md), [`sources/methods-sae-audit.md`](sources/methods-sae-audit.md).
- **Measurement:** IRT (maintained: R `mirt`, `TAM`; Python options less mature) and cognitive diagnosis models for competency-level diagnosis; knowledge tracing is built for dense click-streams and fits sparse termly school assessments poorly; classification CAT / SPRT stopping rules for short mastery tests.
- **Linking instruments:** UIS policy linking to the Global Proficiency Framework (SDG 4.1.1), AMPL, IEA Rosetta Stone, Harmonized Learning Outcomes — concordance between differently-scaled tests is an established practice.
- **Small-area estimation:** Fay–Herriot / hierarchical Bayes with benchmarking (World Bank poverty mapping; R `emdi`, `sae`).
- **Integrity and audits:** Jacob & Levitt-style answer-pattern forensics validated by re-tests; risk-limiting audits (SHANGRLA, ALPHA) for verifying threshold claims with sequential sampling; tax-audit practice of risk-selected plus random audits to keep population estimates unbiased.
- **Novelty check** ([`sources/novelty-check-measurement-assurance.md`](sources/novelty-check-measurement-assurance.md), 4 Oct 09:10): every element has precedent — exam-board moderation of school-based assessment (NSW NESA; Queensland QCAA "selected sample" confirmation; England KS2 local-authority moderation), survey back-checks (IPA: ≥ 10 % of surveys), World Bank results-based-financing verification, validation-subsample measurement-error correction, Fay–Herriot SAE of literacy (Kenya, 2026). No opened source combines them for government FLN census data as a non-punitive, known-probability re-test → design-based correction → benchmarked block estimates. **Claim adaptation/combination novelty, not "first ever".**

## 5. Where our design borrows, and where it goes further
| We borrow | From | We go further by |
|---|---|---|
| Group-by-level remediation | Pratham TaRL (RCT-backed) | A few-minute adaptive check and a Monday plan in ≤ 3 SMS / IVR, with a logged 6-week recheck |
| External verification of reported results | Gunotsav, Haryana Saksham, UP NIPUN RFP, Assam Gunotsav | Using the verification sample as a *moderation* sample with known inclusion probabilities, so it calibrates every school's data and yields block estimates with intervals — at a fraction of the sample (budget evaluated at 2.5–20 % of schools) |
| Dashboards in a state command centre | VSKs | Showing moderated, interval-backed numbers that add up across levels; no school-level blame labels (ADR 001) |
| Tamper-resistant, AI-scored oral reading | Vaachan Samiksha | Treating AI scores as one more instrument in the competency crosswalk, validated per language before use |
| Student-wise records | UDISE+ (since 2022-23) | Keying everything on UDISE+ codes, LGD codes and salted pseudonyms of the student ID |

## 6. Open questions (to close before 12 Oct)
- PARAKH 2024 state- and district-level tables (national report lists "50 High Performing Districts (Grade 3)", p. 13) — extract for the real-data ASER-vs-PARAKH comparison.
- Whether NIPUN's goal grade is "end of Grade III" (2021 document) or "Grade 2" (2024 parliamentary answer) in current guidelines.
- VSK architecture and stack at a government source (cQube/Sunbird adoption by state).
- Independent accuracy of AI oral-reading scoring in Indian languages.
- Causal evidence specific to Indian dashboards/VSKs (none found so far).
