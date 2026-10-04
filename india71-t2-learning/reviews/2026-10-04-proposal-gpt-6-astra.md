# Hostile jury review: Ek Tasveer, Round 1 proposal v0.3

**Reviewer:** GPT-6 Astra, independent cross-model review under PLAYBOOK section 10.

**Date:** 4 October 2026.

**Fixed snapshot:** repository commit `3c8eb29`; proposal blob `d5603b0e9d50814f3b68430c254aa3ebee99b0cd`.

**Scope:** the official Theme 2 brief and Round 1 rules, proposal v0.3, architecture companion, research/source notes, ADR 001, and the two evaluation summaries. I also inspected the simulator, real-data analysis script and existing rendered PDF where necessary to check claims. No proposal, implementation, evidence or evaluation file was changed.

**Verdict: do not submit v0.3 unchanged.** The stated NIPUN attainment gap is not what the cited instruments measure; the proposed survey anchoring does not have a defensible common target quantity; and the learning-case register creates child- and teacher-level risks that the stated safeguards do not contain. A smaller, specified classroom-support intervention is more defensible than the present claim to produce one trusted picture at every level.

**Findings: 25 issues -- 4 BLOCKING, 19 MAJOR, 2 MINOR.** BLOCKING means a core claim is invalid or the proposed child-data deployment needs redesign before proceeding; it does not mean a synthetic demo is already violating the law. MAJOR means a material weakness against the competition criteria. MINOR means a citation or submission-preparation defect.

The lead is recalculating synthetic results, including interval calibration. This review does **not** treat the current error/coverage digits as final. The methodological objections below survive a change in those digits. No synthetic result is treated as observed performance on Indian children.

## Source spot-check ledger

Source-note abbreviations: **U** = `research/sources/official-udise-nipun.md`; **O** = `research/sources/official-data.md`; **E** = `research/sources/evidence-base.md`; **D** = `research/sources/deployed-states-ngos.md`; **M** = `research/sources/methods-sae-audit.md`; **N** = `research/sources/novelty-check-measurement-assurance.md`. All primary sources linked below were opened in this review. Where the evidence supports only a narrower statement, that limitation is explicit.

| Check | Proposal number or quotation | Comparison with source notes and primary source |
|---|---|---|
| F1 | SDG score **71**; elementary adjusted net enrolment **96.5%** | Matches U and the [PIB release][pib-sdg]. Crucial omitted date: the release says the 96.5% ANER is **for 2021-22**, not an observation of current 2026 enrolment. The separately quoted SDG 4 score of 61 matches U's image transcription; I did not independently inspect that image. |
| F2 | NIPUN: **2026-27**, Grade 3, reading with meaning **at least 60 words/minute**, numbers **9,999** | Matches U and the [2021 launch document][nipun], including its Lakshya graphic. The numeracy graphic also requires simple multiplication. These are not equivalent to the ASER story/subtraction indicators. |
| F3 | Grade 3 presented as the unqualified current mission endpoint | U already records a conflicting later statement. The [7 February 2024 parliamentary answer][nipun-2024] explicitly says **Grade 2 by 2026-27**. The [UP government page][up-nipun] still says Grade 3. A state/version reconciliation is necessary; neither silently deleting Grade 3 nor silently ignoring Grade 2 is justified. |
| F4 | ASER government Std III reading: **20.9%, 16.3%, 23.4%** in 2018/2022/2024 | Matches O and the [ASER report][aser], national findings and school-type table. This is reading a Std II text in **rural government-school** children, not measured NIPUN Grade 3 mastery. |
| F5 | ASER government Std III subtraction: **20.2% to 27.6%** | Matches O and [ASER][aser]. The underlying task is a two-digit numerical subtraction problem with borrowing; it is not the full numeracy target. |
| F6 | Private-school Std III reading: **35.5%** | Matches the landscape and [ASER][aser]. Same rural-survey scope; it is not a causal estimate of the private-school advantage. |
| F7 | **14.71 lakh schools**, **68.9% government** | [UDISE+ 2024-25][udise] verifies 1,471,473 total and 1,013,322 government schools. Their ratio is 68.86%, rounding to 68.9%, as U states. These are **school counts across the system**, not the share of Grade 1-3 children in rural government schools. |
| F8 | **104,125 single-teacher schools; 33.8 lakh enrolled** | Matches U/O and UDISE+ Table 2.2: 3,376,769 enrolments. The national table is not restricted to the proposal's rural, government, Grade 1-3 intersection. |
| F9 | Student-wise UDISE+ records since **2022-23**, **more than 60 fields** | Matches U/O and [UDISE+][udise]. The opened source names an **EID**, not proof of access to a PEN/APAAR API or a live classroom-assessment feed. U explicitly marks PEN terminology and actual learning/attendance fields unverified. |
| F10 | PARAKH: **2,115,022 children; 74,229 schools; 781 districts; 599,026 Grade 3 students** | Matches O and the [national report][parakh]. The first three numbers cover Grades 3, 6 and 9 together; the proposal distinguishes the Grade 3 count correctly. |
| F11 | PARAKH Grade 3: rural **64/60**, ST **61/57**, Others **66/61**, shapes/money **50%** | Matches O and the [national report][parakh], printed pp. 3-4. They are average scores/percent correctly answered questions, **not percentages of children proficient**. |
| F12 | FLS: **86,000 pupils, 10,000 schools, 20 languages**; numeracy **37/42/10%** | The [parliamentary answer][fls] directly supports the sample and language-specific benchmarking. The percentages appear in the question text, which also includes the omitted **11% lacking basic skills**. U/O's shorthand should not turn a partial distribution or a parliamentary question into a reproduced NCERT results table. |
| F13 | MP audit **283 schools**, inflation **38.9/33.8 pp**, retest levels **25.1/37.9%** | Matches E and [Singh's paper][singh]. The estimand is percent correct on matched test items. The paper compares January/February **2017** assessments; this is not an observed 2026 pilot-district FLN inflation rate. |
| F14 | AP tablet testing **about US$0.50 per test** | The number exists in [Singh][singh], as E records, but the footnote derives it from a roughly US$60 tablet and three-year depreciation. It is not a costed CRC visit, independent oral retest, coaching session or state deployment. |
| F15 | TaRL: **six randomized evaluations, seven states, over 60 million students** | Matches D/E and the [J-PAL case study][tarl]. The same source says the approach works best from Grade 3, describes substantial instructional time and mentoring, and says training/materials alone did not improve learning. The scale statement is from a case study updated in August 2022, not an independently re-audited 2026 count. |
| F16 | Haryana: **over 80% score over 50%; all 119 blocks** | Matches M and the [Haryana release][haryana], describing February **2020** examinations. Coverage of every block does **not**, by itself, establish a census of every child. |
| F17 | Gujarat Gunotsav: **3,000 officials; 25% of schools** | Matches M and the [official description][gunotsav]. It describes whole-day school visits and a broader evaluation, not an interchangeable unit-cost comparator for a short FLN retest. |
| F18 | QCAA reviews **"a selected sample"** | Matches N and [QCAA][qcaa]. The sample is existing **student work**, for every subject in every school; it is not a random 10% sample of schools retesting children. |
| F19 | Vaachan Samiksha **nearly 30,000 Gujarat schools** | Matches D and the [developer account][vaachan]. It also describes a teacher using the first two periods with batches of 5-10 children. The deployment/tamper-proof statements are developer claims, not independent proof of validity or negligible workload. |
| F20 | Rajasthan: PARAKH language **70%**, ASER government reading **12.1%** | Both match the primary [Rajasthan report][rajasthan] (PDF p. 14, printed p. 12) and [ASER][aser] (printed p. 52). A read-only recalculation from committed CSVs reproduced the reported 27-state correlations, ranks and leave-one-state-out errors. The problem is their interpretation, not their arithmetic. |
| F21 | DPDP section 9: verifiable parental consent and tracking/behavioural-monitoring restriction | The wording is in the [Act][dpdp-act], but the source-note directory contains no DPDP entry. I additionally opened the [commencement notification][dpdp-start] and [final Rules 2025][dpdp-rules]: section 9 is on the deferred 18-month schedule; Rule 12/Fourth Schedule already specify conditional education exemptions. These cannot be treated as unspecified future rules. |
| F22 | TB programme incentivises notification and treatment completion | The claim appears in the [2017-25 strategy][tb], specifically in its private-provider engagement design. There is no evidence there that translating this incentive model to children's learning is safe, effective or incentive-compatible. No TB source note was found in the cited source directory. |

## Numbered issues

### 1. [BLOCKING] The central measurable gap compares different standards

**Claim at issue -- proposal section 1:**

> "Share of Grade 3 children in government schools who meet the Grade 3 reading and numeracy goals"
>
> "mission target 100 % in 2026-27 [2]; independently measured ≈ 23 % (reading) and ≈ 28 % (subtraction) [3]."

**Why it fails:** ASER does not measure the stated Grade 3 NIPUN endpoint. Reading a Grade 2 story is not a validated test of at least 60 words per minute **with meaning**; subtraction is not the full numeracy domain, including the listed number range and multiplication. The simulator itself calls these a "goal proxy." Presenting the percentages as independently measured mission attainment is a construct substitution. The operational ladder also omits domains such as money and shapes that the proposal identifies as weak.

**Concrete fix:** Call these **ASER foundational-skill proxies**, retain the exact task/population/year, and state that the corresponding NIPUN attainment percentage is not established by these figures. Define a separate, state-approved operational outcome with task, language, comprehension/numeracy criteria, denominator and assessment date. Do not relabel either the synthetic or observed ASER indicators "% meeting the NIPUN goal."

### 2. [MAJOR] The current policy endpoint is unresolved in the proposal's own evidence

**Claim at issue -- proposal section 1:**

> "by the end of Grade 3 [2]. **2026-27 is this school year.**"

**Why it fails:** This rests on the 2021 launch document while U already records the later parliamentary Grade 2 statement. I verified the latter and also the still-Grade-3 UP page. That is an unresolved policy/version issue, not a licence to pick the more convenient target. A SCERT juror will ask which current curricular framework, state Lakshya and assessment order the product actually implements.

**Concrete fix:** Specify the pilot state, cite its operative order and version the competency mapping. Explain that the proposal studies a defined Grade 3 cohort, where applicable, rather than asserting a reconciled nationwide 2026 target that has not been established. Preserve the distinction between an older mission goal, a foundational-stage endpoint and the intervention's evaluation cohort.

### 3. [MAJOR] A national learning deficit is not evidence of this local implementation bottleneck

**Claims at issue -- proposal section 1:**

> "those the data system sees least well"
>
> "The implementation gap — five breaks."

**Why it fails:** Single-teacher-school counts, ST score differences and low national reading levels establish disadvantage, not that these children lack an assessment-to-action record or that this is their binding constraint. Teacher vacancies, absence, multigrade teaching, unfamiliar instructional language and lack of protected time remain rival explanations. The national all-school counts do not size the proposed rural government Grade 1-3 population. There is no selected district, intersectional denominator or observed service-gap baseline.

**Concrete fix:** Define one pilot population and one auditable implementation measure, for example the share of assessed below-level Grade 3 pupils receiving an appropriate activity and a follow-up within a specified period. Obtain a small, explicitly non-representative workflow/time-use validation with teachers, CRCs and families before asserting the mechanism; label it planned if not yet possible. Separate national context counts from the pilot's actual eligible-child count.

### 4. [MAJOR] The ecosystem is weakened artificially to make the combination look necessary

**Claims at issue -- proposal sections 1 and 3:**

> "no system links them"
>
> "Monitoring, not a classroom action; no causal evaluation found"
>
> "Verification grades schools or blocks; it is not used to *calibrate* the data, so it must be huge"

**Why it fails:** Not finding an evaluation is not evidence that a system has no classroom action. The national-DPI source note is an empty scaffold. UDISE+'s absence of actual learning fields is still marked unverified in U. Coverage of 119 Haryana blocks does not prove a pupil census, and a grading purpose does not mathematically require a huge verification sample. QCAA is moderation of existing work in every school, not evidence for this proposal's retest sampling rate. The novelty search itself is bounded and records extensive prior art.

**Concrete fix:** Replace universal negatives with "not documented in the sources reviewed." Compare two relevant state workflows on named functions, staff, sample design and documented limitations. Describe novelty as a **proposed adaptation/combination** of established assessment, back-check and estimation methods; demonstrate incremental value over existing TaRL plus random verification. Do not claim a smaller necessary sample until equal-precision/equal-cost comparisons support it.

### 5. [MAJOR] The real-data analysis is a concordance check, not a reason to build a crosswalk

**Claim at issue -- proposal section 2:**

> "The instruments measure different things — so a crosswalk with explicit uncertainty must come before either drives decisions."

**Why it fails:** The recalculated correlations and leave-one-state-out errors match the report, but ASER rural government-school task proficiency is compared with PARAKH all-management/location average scores. Low concordance can arise from population composition, constructs, mode, language or sampling error. A regression between 27 state aggregates is not a child-level linking study, cannot isolate these explanations, and does not show either instrument is unusable for its intended decisions. Rank gaps from rounded scores also need uncertainty.

**Concrete fix:** Conclude only that these particular aggregates should not be substituted for one another. Keep the two indicators separate. If linking is needed, specify a common-person or common-item validation design, comparable populations, language-specific measurement checks, uncertainty in both instruments and an independently assessed linking error. A competency-code ontology is not a statistical score crosswalk.

### 6. [BLOCKING] The promised benchmark can erase real progress or combine incompatible quantities

**Claim at issue -- proposal section 4:**

> "**block numbers with intervals that add up to the PARAKH/ASER anchor**"

**Companion claim -- architecture section 3:**

> "benchmark to PARAKH/ASER anchor (precision-weighted)"

**Why it fails:** There is no single PARAKH/ASER anchor on the stated target scale. Average percent correct and the share passing a particular oral task are not totals that become comparable through precision weighting. The 2024 cohorts are also not the 2026 term's Grade 3 children. Forcing current block estimates to an old aggregate can mechanically remove genuine improvement. An enrolment-weighted estimate for the target population must also be distinguished from an average across schools. The simulator sidesteps this by generating a contemporaneous, same-construct "ASER/PARAKH-like" survey.

**Concrete fix:** Define one estimand and its population weights first. Use same-period, same-population, same-instrument independent data for any actual benchmark. Treat legacy survey values as contextual evidence, or as explicitly uncertain model information with a tested time/cohort model, not a hard total. Never average incompatible anchors. With no suitable anchor, report a design-based retest estimate and its limits rather than manufacturing cross-level agreement.

### 7. [MAJOR] Ten percent is a budget choice, not a demonstrated precision guarantee

**Claim at issue -- proposal section 5:**

> "a block of 100 schools needs 10 school re-tests per term — about 12 children each"

**Related claim -- section 4:**

> "A model-assisted estimator calibrates every school's reported results"

**Why it fails:** This supplies about 120 retests per block, potentially spread over three grades. For orientation only, 120 independent unassisted Bernoulli observations at 50% prevalence give a 90% interval half-width of about **7.5 percentage points**, before clustering; this is not a bound on a model-assisted estimator, which might improve precision. No residual variance, school ICC, nonresponse, within-school sampling probabilities, subgroup precision or decision tolerance is specified. Known school inclusion probabilities alone do not make each unaudited school's prediction design-validated.

**Concrete fix:** Make sample size follow a stated decision/precision requirement and observed pilot variance, with minimum samples by block/grade and explicit absence handling. Record school and pupil selection probabilities and appropriate variance/replicate calculations. Show random-sample and model-assisted results at the same cost. Distinguish model-predicted school adjustments from directly validated block estimates, and suppress decisions when evidence is insufficient.

### 8. [MAJOR] A CRC is neither automatically independent nor a timeless gold standard

**Claim at issue -- proposal section 4:**

> "re-tested by the cluster coordinator during the regular academic-support visit, who then coaches that group"

**Why it fails:** The CRC shares supervisory relationships and performance pressures with the schools whose results are being checked. Changing the adult does not remove incentives, advance preparation, pupil selection or assessor error. A retest after weeks of instruction also mixes actual learning, forgetting, practice effects and administration differences with reporting bias. The coaching role can be valuable, but does not confer measurement independence.

**Concrete fix:** Define a short verification window for checking the original report, separate from later learning follow-up. Randomly select pupils from a frozen eligible roster, record absences without convenient replacements, use blinded scores and standard administration, and include cross-cluster/independent quality checks with inter-rater assessment. Coach **after** recording the independent assessment. State who can challenge a discrepancy and prohibit treating a discrepancy alone as proof of cheating.

### 9. [MAJOR] A sampled audit cannot verify every child's claimed completion

**Claim at issue -- proposal section 4:**

> "a \"cure\" counts only when someone other than the teacher verifies it"

**Why it fails:** The register follows every below-level child, but the costed independent retest covers 10% of schools and roughly 12 children in each. Most children will never receive the stated verifier's check in that round. The proposal alternates between an individual service workflow and a sampled population assurance system without specifying which claims each can support. Universal independent completion checks would be a different workload and sampling design.

**Concrete fix:** Separate routine teacher-led support/rechecks from independently sampled verification. At child level, distinguish observed progress from externally checked progress. At system level, estimate the reliability of reported progress from the probability sample; do not stamp all children as independently verified. If universal external verification is retained, cost and staff it explicitly.

### 10. [MAJOR] The teacher workload has contradictory frequencies and missing tasks

**Claims at issue -- proposal sections 4 and 5:**

> "**Loop 1 — the classroom, weekly.** A teacher runs a few-minute oral check per child"
>
> "Teacher: one short oral check per child per term and one message a week."

**Why it fails:** Weekly activity, termly diagnostics and a six-week recheck may be compatible, but only with a specified timetable; the current text does not give one. Receiving a short message is not the cost of checking children, grouping them, teaching multiple groups, recording actions, resolving ID mismatches and rechecking them. Even an **assumed** three-minute total check for a class of 60 consumes three teacher-hours per round, excluding all those other tasks. A single-teacher school cannot leave the remaining children unsupervised.

**Concrete fix:** Give a per-term task budget, assessment cadence, instructional schedule and replacement for an existing reporting task. State who supervises other pupils during one-to-one checks, how a multigrade class is handled and what is deferred when capacity is absent. Measure actual time on basic-phone/paper and smartphone routes; do not use item count or message bytes as teacher-time evidence.

### 11. [MAJOR] TaRL's effects are being attached to a much thinner, younger intervention

**Claims at issue -- proposal sections 4 and 6:**

> "TaRL groups, one activity per group from the state's own content"
>
> "TaRL-style grouping has strong RCT support [8]"

**Why it fails:** The cited J-PAL account says TaRL works best with Grade 3 and older children, describes one or two hours of daily instruction in the government model and substantial mentoring, and warns that training/materials alone did not improve learning. The proposal serves Grades 1-3 but specifies neither age-appropriate foundational-stage pedagogy nor protected teaching time. A Monday message is not the evaluated treatment. ADR 001 already identified a state order protecting a daily instructional period as part of the minimum pilot; the submitted proposal drops it.

**Concrete fix:** Restore the instructional period, mentoring, materials and supervision into the actual intervention and cost model. Start with a justified cohort, or define a separate play-/activity-based Grade 1-2 approach aligned with SCERT guidance. Treat TaRL effect sizes as prior evidence for these delivery conditions, not expected effects of the software. Evaluate the software's incremental benefit over the same pedagogical support.

### 12. [MAJOR] The cost claim confuses device depreciation with delivered service

**Claim at issue -- proposal section 5:**

> "**Costs:** no new devices; SMS/IVR as fallback; tablet-based re-testing was costed at about US$0.50 per test in the Andhra Pradesh study [5]."

**Why it fails:** The cited 50 cents is derived from tablet cost/depreciation, not a budget for trained independent assessors, travel, pupil time, coaching, supervision, content validation, integration or recurrent messaging. "Inside visits" does not make the marginal workload or the displaced support activity free. "No new devices" has no asset-availability audit behind it.

**Concrete fix:** Add a pilot bill of quantities in rupees: schools/children/visits, staff-hours and travel, training and back-checks, printing/content/localisation, integration/security/hosting, messaging, maintenance and contingency. Mark unit prices as estimates until quoted, distinguish cash from opportunity cost, and show low/high scenarios. Identify the budget holder and recurrent funding route. Use the historical tablet figure only as a narrowly labelled comparator.

### 13. [MAJOR] The state roadmap has no authority, procurement or acceptance chain

**Claims at issue -- proposal sections 4 and 5:**

> "a thin decision layer on what states already run"
>
> "1 state via its VSK"

**Why it fails:** A component diagram does not grant UDISE+ student-data access, state-app write access, a VSK hosting slot, permission for independent assessments or time in the school timetable. CRC/BRC capacity is assumed; DIET and SCERT are not assigned operational responsibilities. There is no procurement/onboarding path, data-sharing arrangement, content licence, training responsibility or maintenance owner. A three-month staggered start is presented without these dependencies.

**Concrete fix:** Include a compact responsibility/approval chain: state FLN/Samagra mission authorises and funds; SCERT owns assessment/content standards; DIET trains and checks assessors; BRC allocates support capacity; CRC coaches within an agreed workload; teachers deliver instruction; the VSK/IT team operates only approved services; an independent evaluator measures outcomes. Make procurement, state orders, data-sharing/processor agreements, language readiness, timetable release and connectivity/device checks explicit phase-zero gates. Label partnerships and dates conditional rather than implying agreements exist.

### 14. [BLOCKING] The legal position is not current, and pseudonymisation does not make it hold "either way"

**Claim at issue -- proposal section 4:**

> "the design holds either way, with pseudonymised, purpose-bound server records and consent captured at enrolment where required"

**Why it fails:** A pseudonymous longitudinal learning record can still be personal data under section 2(t). Consent is not an alternative to the section 9(3) tracking restriction when that restriction applies. Nor is "consent at enrolment" evidence of specific, informed, verifiable consent for every later use.

The [13 November 2025 notification, G.S.R. 843(E)][dpdp-start] puts section 9 on an 18-month commencement schedule, so it is **not yet in force on 4 October 2026 under that schedule**. The [final Rules 2025][dpdp-rules] are already notified: Rule 12 and Fourth Schedule Part A item 3 conditionally exempt an educational institution's specified educational/safety monitoring from sections 9(1) and 9(3). Their operative commencement is also deferred. This is not an unresolved choice of hypothetical future rules. The exemption does **not** remove section 9(2)'s child-well-being restriction and cannot simply be assumed to cover every VSK, research, vendor or allocation use.

**Concrete fix:** Replace "holds either way" with a dated, purpose-by-purpose legal deployment gate covering the period before and after commencement. Identify fiduciary/processor roles and the basis and conditions for classroom support, state analytics, external research and messaging. Obtain specific/verifiable consent where required, with accessible notices, refusal/withdrawal without loss of ordinary educational support, and a documented guardian-verification route. Obtain qualified review of the chosen exemption before live use; an education label is not a blanket exemption.

### 15. [MAJOR] The claimed data boundary contradicts the architecture

**Claims at issue -- proposal section 4 and companion sections 2/4:**

> "child-level data only on the teacher's device"
>
> "D->>P: levels by pseudonym"
>
> "`ps_<16 hex>` = salted SHA-256 of PEN/APAAR"

**Why it fails:** Removing names does not turn individual level/response/history rows into aggregates. The plan service and action ledger receive linkable child records; the state holds the salt and source identity context. WhatsApp/SMS/IVR and a teacher's personal or shared phone introduce additional recipients, backups and visible notifications. Cell suppression below ten is not sufficient protection against small-school inference, complementary totals or repeated releases. No retention, lost-device, staff-transfer, deletion, access-review or incident workflow is specified.

**Concrete fix:** Choose and document an honest boundary. Prefer local child-to-group membership with only minimised aggregates/operational counts sent centrally where possible. Otherwise explicitly disclose the necessary child-level processing and implement a field/recipient/retention matrix, device access controls, encryption, processor terms, access revocation, deletion/correction and incident handling. Protect small-cell releases across related tables/time, not just one cell. The 36 policy tests establish only the cases they test, not legal compliance or an end-to-end privacy guarantee.

### 16. [BLOCKING] The case/cure register is not protected against stigma or punitive use

**Claims at issue -- proposal section 4 and companion sections 4/5:**

> "each child found below level is notified to an owner with a recheck date"
>
> "a \"cure\" counts only when someone other than the teacher verifies it"
>
> "Inaction, not low levels, becomes the visible failure."
>
> "visible only to the moderation team and the state"

**Why it fails:** A child struggling with a skill is not a disease case. Persistent case/cure/overdue labels can become perceived ability labels, particularly for children with disabilities or unfamiliar instructional languages. The same system can blame a teacher for slow progress caused by staffing, attendance or missing support. Keeping school trust data off a public dashboard does not prevent the state employer from using it for transfers, discipline or pressure. "Non-punitive" is therefore an intention, not an enforceable feature.

**Concrete fix:** Remove the disease/cure framing from the design, not just the pitch. Use a time-limited **learning-support record** with revisable observations, neutral groups, contextual support needs and no permanent low-ability label. Put service responsibility on the institution with the resources to respond. Require a state-approved firewall against personnel or pupil-progression decisions based on these diagnostic/moderation records, restricted access, documented appeals/correction, and teacher/parent participation in oversight. Any legally required misconduct inquiry must be a separate evidentiary process, not an inference from this score.

### 17. [MAJOR] Notification targets move Campbell's law; they do not solve it

**Claim at issue -- proposal section 4:**

> "survey-anchored prevalence × UDISE+ enrolment − notified children estimates **missing cases**"

**Related claim -- ADR 001:**

> "makes truthful reporting the dominant strategy"

**Why it fails:** No incentive analysis establishes that assertion. Rewards for finding cases can encourage duplicate or marginal notifications; completion pressure can encourage coaching to the test, premature closure, fabricated activity logs or avoiding persistently absent/hard-to-help children. The subtraction is interpretable only with matched population, time, case definition, unique children and valid uncertainty; a 2024 survey proxy multiplied by current enrolment does not reveal named children who were missed. Sampling error, false-positive notifications and cohort changes can even produce negative residuals.

**Concrete fix:** Delete the dominant-strategy claim. Keep estimated unmet need as an uncertain **aggregate service-planning quantity**, never a quota or an accusation. Report uncertainty and reconcile populations; do not silently truncate impossible residuals into a persuasive dashboard. Separate reporting accuracy from service progress, independently sample both reported successes and children not receiving support, and forbid notification/completion quotas or automatic rewards tied to them.

### 18. [MAJOR] The inclusion route is unspecified for missing IDs, basic phones and absent children

**Claims at issue -- proposal section 5 and companion section 2:**

> "no new devices"
>
> "participant T as Teacher (basic phone)"
>
> "participant D as C4 Diagnostic (on device)"

**Why it fails:** A generic basic phone does not execute an on-device adaptive engine merely because the output fits SMS. The architecture keys pupils through PEN/APAAR but describes no safe temporary-ID or mismatch process. Enrolled-but-absent, migrating or unassessed children can disappear from the denominator. UDISE+ cannot supply a roster of all out-of-school children by multiplying survey prevalence. The proposal does not require each child to own a phone; it should not accidentally introduce such a requirement through consent or follow-up.

**Concrete fix:** Specify a paper/printed-plan and ordinary-phone workflow alongside the actual supported app/client, including where computation and storage occur. Allow locally assigned, non-Aadhaar-dependent IDs without withholding support; reconcile later under controlled access. State that neither child/family phone ownership nor APAAR is a condition of service. Track missing assessments explicitly, arrange make-up visits and describe the referral boundary for children outside the enrolled-school frame.

### 19. [MAJOR] Language and disability safeguards are postponed until after classification

**Claim at issue -- proposal section 5:**

> "language → per-language validation of items and AI scoring"

**Why it fails:** That is a future task, not an operating safeguard. Language mismatch, dialect, speech/hearing/visual disability and unfamiliar scripts can look like low skill to the same short test. A uniform fluency rule and a five-level label may misclassify the proposal's priority groups. Neither the proposal nor companion specifies accessible response modes, permitted accommodations, culturally appropriate material, an unassessable state or specialist referral. An automated low score must not become a disability diagnosis.

**Concrete fix:** Choose the pilot's actual languages and accessible assessment modes before launch, with SCERT/DIET and relevant specialist review. Validate task interpretation, rater agreement and classification by language/disability context; keep adaptations documented rather than assuming scores are interchangeable. Permit "not assessable with this instrument" and human review without denying instruction. Publish an explicit no-AI-scoring fallback and avoid collecting sensitive labels that are unnecessary for support.

### 20. [MAJOR] A posterior threshold is being presented as dependable diagnostic certainty

**Claim at issue -- proposal section 4:**

> "An adaptive engine stops once ≥ 90 % sure of the level"

**Why it fails:** A model's posterior under assumed item parameters is not an empirically established 90% correctness guarantee on real children. The same proposal caps testing at eight items and calls exact-level accuracy a baseline. It does not say what happens when the cap is reached without sufficient evidence, when responses are inconsistent, or when the child is unlike the calibration population. Synthetic item difficulty/discrimination do not validate an Indian-language assessment bank.

**Concrete fix:** Describe the threshold as a simulation/model stopping rule, not field certainty. Specify an uncertain result at the cap, human/branching-assessment fallback and an explicit no-auto-label/no-auto-close rule. Compare against a simple ASER-style branching assessment at equal observed time; validate skill-level false positives/negatives and confidence calibration on independently scored real responses, including underserved groups. Exact agreement on five broad levels is not sufficient evidence of the right remedial activity.

### 21. [MAJOR] Matching two ASER marginals does not validate the synthetic world

**Claims at issue -- proposal section 4:**

> "ASER-calibrated"
>
> "Detecting inflating schools (AUC) from public signals only"

**Why it fails:** `eval/sim/calibration.py` calibrates two national ASER proxy rates. School effects, covariate relationships, reporting distortion, item-response behaviour and the contemporaneous survey anchor are generated assumptions in `world.py`. Success at detecting that generated distortion is not evidence of the prevalence of cheating, discrimination-free detection or cost-effective correction in a state. The real-data analysis's weak state-level covariate associations neither validate nor disprove the assumed school-level relationships. Multiple seeds within the same mechanism do not test transportability.

**Concrete fix:** Label the result "synthetic stress test matched to two ASER marginals." Freeze and publish scenarios covering no inflation, benign measurement/language differences, heterogeneous distortion, CRC error/collusion, absence, weak covariates and time-shifted anchors. Use held-out mechanisms as well as seeds. Compare raw reports, simple probability-sample estimates, adjustment-only and adjustment-plus-SAE at identical cost; report uncertainty/decision errors and subgroup behaviour, not just AUC/MAE. Report the revised coverage, widths, replication count and failure regimes together. If SAE or risk targeting adds no robust value, omit it from the pilot rather than defending complexity.

### 22. [MAJOR] A staggered start is not automatically a causal comparison

**Claim at issue -- proposal section 5:**

> "clusters staggered"
>
> "staggered start gives a causal comparison"

**Why it fails:** Administrative rollout order can track readiness, baseline performance or staff capacity. Calendar effects, maturation, repeated testing and shared CRC support can then explain apparent differences. Two blocks do not describe the number of independent clusters, the unit of assignment, contamination or statistical power. The proposed exit criterion is plan use and a reporting gap, not independent learning improvement.

**Concrete fix:** Specify randomised rollout/order at an appropriate unit or state clearly that the first phase is only a feasibility study. Pre-specify the primary independently administered learning measure, baseline/endline, assignment unit, cluster count, ICC/MDE assumptions, analysis, attrition handling and spillover controls. Keep evaluator independence from the support team. If three months cannot support a learning-effect claim, make that phase's claims operational and reserve causal impact for a properly designed later evaluation.

### 23. [MAJOR] The allocation and scaling story has no defined incremental benefit or equity constraint

**Claims at issue -- proposal sections 4 and 6:**

> "ranked by expected children helped and weighted for single-teacher schools and SC/ST share"
>
> "the layer runs on the state's VSK"

**Why it fails:** Estimated need is not an estimate of the causal response to a camp or training intervention. Maximising an assumed "children helped" score can favour easy-to-reach or borderline pupils and displace support from expensive remote or disabled learners. The demo's simulated children reached is not additional children learning. Existing evaluation summaries do not establish an allocation advantage; the proposal itself says gains are not yet shown. Hosting on a VSK is not an institutional or financial scaling mechanism.

**Concrete fix:** Define the decision, actual discretionary budget, approving official, alternative allocation rule and appeal route. Preserve minimum support entitlements and explicit access/equity constraints; do not automatically remove resources because a noisy estimate is low. Evaluate additional independently observed learning and cost per additional beneficiary over the same pedagogical programme without the layer. Make scale contingent on incremental benefit, feasible workload, acceptable harm indicators, language readiness and funded maintenance, not just component adoption.

### 24. [MINOR] Dates, partial distributions and evidence locations need repair

**Claims at issue -- proposal sections 1/2 and references:**

> "the adjusted net enrolment rate in elementary education is 96.5 %"
>
> "Numeracy: 37 % limited, 42 % sufficient, 10 % superior skills"
>
> "quotes and page numbers in `research/sources/`"

**Why it fails:** The ANER observation is from 2021-22. The FLS row lists only 89% of the distribution without saying it is partial, and its cited parliamentary source places those percentages in the question. References 18 and 23 do not have the promised source notes; reference 18 also lacks a URL. Several deployment claims refer to historical pages, not a verified current deployment snapshot.

**Concrete fix:** Show observation year separately from publication/access year, include or explicitly omit the remaining FLS category, and cite the actual NCERT results table for that distribution. Supply the Act, commencement and final Rules references and precise TB context. Mark historical/developer/bounded-search evidence consistently. Do not imply that opening a source in 2026 updates the age of its data.

### 25. [MINOR] Six pages alone does not complete the submission preflight

**Claims at issue -- proposal header and official Round 1 rules:**

> "**Team:** ⟦Team name⟧ · **Team ID:** ⟦Team ID⟧ · **Institution(s):** ⟦…⟧ · **Contact:** ⟦email, phone⟧"
>
> "Arial font, minimum 11pt, single PDF file"

**Why it fails:** The existing PDF is six A4 pages and its main text is Arial at approximately 11 pt, but inline code is embedded as Menlo. The architecture diagram is a downscaled raster, so a body-font check does not certify its label sizes; `diagram.html` uses 15 px labels before scaling. Team details are placeholders and the built filename is not the required submission filename. The separate companion cannot carry information essential to judging a single-PDF submission.

**Concrete fix:** Fill the required details, use `India71_100_[Team ID].pdf`, enforce Arial for ordinary/code text and inspect diagram labels at final printed size against the minimum. Keep essential operating and safeguard commitments in the six-page PDF itself. Recover space by cutting speculative component/analogy material, not by shrinking text. This is a finalisation checklist, not a claim that the current six-page count is wrong.

## Primary references opened for this review

[pib-sdg]: https://pib.gov.in/PressReleaseIframePage.aspx?PRID=2032857
[nipun]: https://static.pib.gov.in/WriteReadData/specificdocs/documents/2021/jul/doc20217531.pdf
[nipun-2024]: https://sansad.in/getFile/annex/263/AU523.pdf?source=pqars
[up-nipun]: https://basiceducation.up.gov.in/en/page/nipun-bharat-(mission-prerna)
[aser]: https://asercentre.org/wp-content/uploads/2022/12/ASER_2024_Final-Report_13_2_24-1.pdf
[udise]: https://dashboard.udiseplus.gov.in/report-new-v.11-demo2025/static/media/UDISE+2024_25_Booklet_existing.118ba29d4773e6372f72.pdf
[parakh]: https://parakh.ncert.gov.in/sites/default/files/2025-07/REPORT_India_IND.pdf
[fls]: https://sansad.in/getFile/annex/259/AU3224.pdf?source=pqars
[singh]: https://riseprogramme.org/sites/default/files/2020-11/RISE_WP-042-Singh.pdf
[tarl]: https://www.povertyactionlab.org/case-study/teaching-right-level-improve-learning
[haryana]: https://www.prharyana.gov.in/en/the-saksham-haryana-programme-an-initiative-of-haryana-school-education-department-which-has-been-0
[gunotsav]: https://gunotsav.gujarat.gov.in/aboutus.html
[qcaa]: https://www.qcaa.qld.edu.au/senior/assessment/quality-assurance/confirmation
[vaachan]: https://www.wadhwaniai.org/vaachan-samiksha-leveraging-ai-to-bridge-the-literacy-divide/
[rajasthan]: https://parakh.ncert.gov.in/sites/default/files/2025-07/REPORT_Rajasthan_IND008.pdf
[dpdp-act]: https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf
[dpdp-start]: https://www.meity.gov.in/static/uploads/2025/11/c56ceae6c383460ca69577428d36828b.pdf
[dpdp-rules]: https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf
[tb]: https://extranet.who.int/cpcd/sites/default/files/public_file_repository/IND_India_National-Strategic-Plan-for-TB-Elimination_2017-2025.pdf

The links in the source-check table resolve to the primary documents above. The commencement notification was also checked at <https://egazette.gov.in/WriteReadData/2025/267647.pdf>. The official PIB Rules explainer, used to locate the final legal PDFs, is <https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/nov/doc20251117695301.pdf>; where an explainer's broad wording differs from the phased legal text, the notification and Rules control. HTML transport failures were worked around with direct public-source retrieval and read-only PDF text extraction; no failed fetch is represented as a verified quotation.

## Criterion scores

These are hostile-juror scores for **v0.3**, not official competition weights or a prediction of the final result.

| Official criterion | Score / 10 | One-sentence justification |
|---|---:|---|
| Problem Identification | **4** | The named population is broad, the local implementation bottleneck is unmeasured, and the headline mission-attainment comparison substitutes ASER proxies for NIPUN outcomes. |
| Evidence & Context | **6** | Many historical figures are traceable, but construct/population extrapolations, unresolved current policy and synthetic-only operational evidence weaken what those figures actually establish. |
| Existing Ecosystem Analysis | **4** | Numerous systems are named, but unsupported negative claims and unmatched verification comparisons overstate the remaining gap and the combination's advantage. |
| Proposed Solution | **4** | The two loops are described, but incompatible anchoring, unvalidated diagnostics and the case-register accountability model undermine their validity and safety. |
| Feasibility & Implementation Roadmap | **3** | Staffing, protected teaching time, complete costs, permissions and a viable independent retest process are missing from the claimed thin-layer rollout. |
| Impact & Scalability | **3** | Neither staggered rollout nor simulated children reached establishes incremental learning, and state adoption lacks equity, funding and evidence-based scale gates. |

## Five changes most likely to raise the score

1. **Fix the target quantity before the model.** Separate ASER proxy evidence from NIPUN attainment, reconcile the chosen state's current grade/competency order, retain ASER and PARAKH as distinct indicators, and remove cross-instrument/time-period hard benchmarking unless a valid link and matched anchor exist. Addresses issues 1, 2, 5 and 6.
2. **Replace case/cure accountability with a protected learning-support workflow.** Remove disease labels and notification/completion quotas; specify institutional support ownership, no punitive reuse, correction/appeal, minimal data, no-ID/no-phone access and current purpose-specific DPDP compliance gates. Addresses issues 14-19.
3. **Make one district/cohort operationally believable.** Choose a bounded population and language, restore protected instructional time and mentoring, show what teacher reporting is replaced, assign state/SCERT/DIET/BRC/CRC/VSK responsibilities, and provide a full rupee cost and approval/dependency table. Addresses issues 3 and 10-13.
4. **Treat assurance as a costed independent measurement protocol, not a 10% slogan.** Define sampling units/probabilities, pupil absence handling, assessor independence, verification windows, accuracy/precision requirements and escalation rules; distinguish sampled verification from each child's routine recheck and retain simple baselines. Addresses issues 7-9, 20 and 21.
5. **Specify a credible test of incremental benefit and a stop rule.** Compare the layer with the same supported pedagogy without it, randomise rollout where feasible, use independently measured learning and workload/harm outcomes, and gate expansion on benefit at acceptable cost rather than dashboard adoption. Addresses issues 4, 22 and 23.
