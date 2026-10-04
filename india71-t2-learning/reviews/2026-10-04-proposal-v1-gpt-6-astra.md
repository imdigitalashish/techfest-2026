# Hostile re-review: proposal v1.0

**Reviewer:** GPT-6 Astra. **Date:** 4 October 2026. **Snapshot:** `8c34d94`.

**Verdict:** No remaining BLOCKING issue in the revised **concept**; this is not clearance for live child-data deployment. Nine original issues are resolved, sixteen partly resolved. Four new MAJOR issues follow. Mandatory team/contact/registration placeholders still prevent submission.

Reviewed the Markdown, final PDF, responses, preregistration and headline results. The PDF has six A4 pages, embedded Arial and minimum extracted text size 11 pt. Frozen assurance/evaluation code is unchanged since preregistration `f6601b9`; held-out results were committed subsequently. I checked stored outputs without rerunning the holdout.

## Original 25 findings

1. **RESOLVED** — ASER indicators are explicitly proxies, not measured NIPUN attainment.
2. **RESOLVED** — Conflicting Grade 2/3 statements are disclosed; the state's operative order governs the pilot.
3. **PARTLY** — Service-gap measurement is defined; district, population boundary and local bottleneck evidence remain unspecified.
4. **PARTLY** — Qualified table headings help, but "nothing obliges or equips anyone" survives; [AU349][vsk] explicitly describes actionable teaching tips.
5. **RESOLVED** — ASER/PARAKH concordance no longer purports to establish a crosswalk; indicators stay separate.
6. **RESOLVED** — Incompatible/stale anchoring is prohibited; supplying the replacement anchor remains a new feasibility issue below.
7. **PARTLY** — Synthetic precision/budget curves exist; field precision requirements, block/grade minima and pupil-selection/nonresponse rules do not.
8. **PARTLY** — Blinding, timing and cross-cluster assessment improve independence; shared incentives and correlated assessor errors remain.
9. **RESOLVED** — Universal verified "cure" is removed; routine support rechecks and sampled verification are distinct.
10. **PARTLY** — Cadence is clearer; replacing data entry does not establish zero additional assessment, teaching or supervision time.
11. **PARTLY** — Protected instruction and mentoring return; duration and justified adaptation for Grades 1-2 remain absent.
12. **PARTLY** — Misleading tablet-cost comparison is removed; priced scope remains absent; my request was for quotes/labelled estimates, not fabricated prices.
13. **PARTLY** — Roles and permission gates exist; named sponsor, procurement, maintenance funding and deliverable-specific acceptance remain conditional.
14. **RESOLVED** — Notified exemptions, deferred commencement and purpose-specific qualified review replace the invalid "holds either way" claim.
15. **PARTLY** — Personal-data status and retention are acknowledged; hosting, consent operations, device security and complementary-disclosure controls remain unspecified.
16. **RESOLVED** — Disease framing is removed; revisable support records, correction rights and a personnel-use firewall are explicit design commitments.
17. **RESOLVED** — Notification/cure quotas and dominant-strategy claims disappear; unmet need is an uncertain planning aggregate.
18. **PARTLY** — Paper, temporary IDs and no-phone access are specified; absent, migrating and unassessed children still lack denominator/recheck rules.
19. **RESOLVED** — Prelaunch language/accessibility decisions, a printed default and "not assessable" with human review address the conceptual omission.
20. **PARTLY** — False certainty wording is removed; the adaptive cap still needs an explicit uncertain-result/human-review rule.
21. **PARTLY** — Frozen held-out simulation and failure reporting improve honesty; error dependence, no-inflation and language-mismatch mechanisms remain untested.
22. **PARTLY** — Feasibility is separated from randomised evaluation; comparator, cluster count, power and operational primary outcome remain undefined.
23. **PARTLY** — Unsupported targeting gains are withdrawn; incremental learning, acceptable cost and harm thresholds remain unspecified.
24. **PARTLY** — Partial FLS statistics disappear; "in the mission's final year" still extrapolates 2024 observations to 2026-27.
25. **PARTLY** — PDF format defects are corrected; team/contact/ID fields and the actual submission filename remain unfinished.

## New MAJOR issues

**N1 [MAJOR] Agreement does not identify accuracy.** Quote: "a 20 % double-assessed subsample estimates assessor error". `assurance.py::misclassification_rate` recovers an error rate only under equal, symmetric, independent assessor errors and the chosen better-than-chance solution. Two assessors can agree on the same wrong answer; different sensitivity/specificity cannot generally be identified from their disagreement alone. **Fix:** describe the observable as agreement, state the identification assumptions, and require adjudicated-reference validation plus asymmetric/correlated-error stress tests before field correction.

**N2 [MAJOR] Coverage uncertainty uses the wrong independence unit.** Quote: "96.7 % (92.9–98.5)". `coverage_test.py::summarise` computes a binomial Wilson interval across 180 blocks, although six blocks share each world's fitted calibration and anchor. There are 30 independent simulated districts, not 180 independent coverage trials. **Fix:** keep the preregistered point estimate and threshold unchanged; append clearly labelled district-cluster uncertainty calculated from stored outputs. Do not present this Wilson interval as calibrated uncertainty. This objection does not establish failure of the preregistered test.

**N3 [MAJOR] The corrected anchor introduces unowned fieldwork.** Quote: "an independent survey of the same construct, population and term". The simulator supplies a separate 20-school survey, up to 200 children; the roadmap identifies neither a matching real survey nor its supplier, sampling protocol and cost. The quoted 120 assessments plus 24 double checks exclude that dependency. **Fix:** identify and resource the contemporary anchor explicitly, or make the unbenchmarked method the pilot default and compare its precision.

**N4 [MAJOR] The separation headline lacks a valid contrast and baseline.** Quote: "55 % of blocks fall clearly above or below the district average, all on the correct side". `run_eval.py::separation_exploratory` compares marginal block intervals against an estimated, unweighted block mean, not joint intervals for child-weighted block-minus-district contrasts. `headline.json` also reports unthresholded direction agreement of 98.3% raw versus 96.1% moderated; those are different from selective-flag accuracy, but demand a comparator. **Fix:** use joint-bootstrap contrasts and matched-coverage raw/unbenchmarked baselines, or delete this exploratory benefit claim.

[vsk]: https://www.sansad.in/getFile/annex/257/AU349.pdf?source=pqars

## Criterion scores for v1.0

| Criterion | /10 | Justification |
|---|---:|---|
| Problem Identification | **6** | The service gap is measurable, but the locality, beneficiary boundary and present-day mechanism remain unvalidated. |
| Evidence & Context | **7** | Traceable sources and honest simulation limits improve credibility, though temporal extrapolation and headline inference need correction. |
| Existing Ecosystem Analysis | **5** | Comparative scope is narrower, but blanket absence claims persist despite the newly cited VSK mandate. |
| Proposed Solution | **6** | The support workflow and safeguards are clearer, while error identification and anchor dependence still require design decisions. |
| Feasibility & Implementation Roadmap | **5** | Responsibilities and gates replace assumptions, but workload, survey provision, procurement and full costs remain uncommitted. |
| Impact & Scalability | **5** | Negative targeting results are disclosed, but incremental benefit, evaluation comparator and explicit scale thresholds are still missing. |

## Three highest-value fixes within six pages

1. Replace the exploratory separation row with **assumptions and limits**: dependent assessors, district-cluster coverage uncertainty and the unbenchmarked comparator; retain the preregistered results unchanged.
2. Replace generic scale prose with a **pilot operating box**: Grade 3 first, proposed district/language, protected minutes, staff/travel/anchor quantities, supplier and budget-approval gate; no invented prices.
3. Replace absolute ecosystem claims with source-bounded wording, correct the 2024/final-year inference, and specify **same supported pedagogy without the layer** as the evaluation comparator with learning/workload/harm scale gates.
