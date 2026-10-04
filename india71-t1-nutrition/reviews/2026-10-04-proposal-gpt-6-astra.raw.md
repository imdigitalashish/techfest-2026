# Cross-model review: Poshan Setu v0.2

The proposal has a concrete technical architecture, and the shift from worker scoring to supportive measurement diagnostics is substantive. The remaining weaknesses are principally **evaluation validity, unsupported prototype claims, and what happens when services are unavailable**.

Quotations and line numbers below refer to the [proposal](/Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-super-guide/india71-t1-nutrition/deliverables/round1-proposal.md). I also checked the small result files needed for the remaining prototype rows and traced the early-warning evaluator where necessary. No files were edited.

## Blocking issues

### 1. The early-warning evaluation uses information unavailable at prediction time

**Proposal:** “SYNTHETIC held-out cohort” and “Recall of children who become wasted within 3 months” — line 106.

There are three distinct problems:

- **Look-ahead:** [feature construction](/Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-super-guide/india71-t1-nutrition/components/early_warning/model.py#L23) calls `engine.assess(meas)` on the complete simulated measurement history. The [diagnostic engine](/Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-super-guide/india71-t1-nutrition/components/credibility_engine/engine.py#L92) aggregates that history by AWC; its resulting credibility value becomes a feature for earlier predictions. Holding out a simulation seed does not prevent this within-cohort look-ahead.
- **Oracle eligibility:** the [evaluator](/Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-super-guide/india71-t1-nutrition/components/early_warning/eval.py#L25) removes children who are *truly* already wasted before allocating the top five places. Deployment cannot observe synthetic truth; erroneous current measurements can leave such children in the queue.
- **Wrong reported unit:** the denominator is eligible **child-month prediction opportunities**, not unique children or incident episodes. Overlapping three-month windows can count one eventual episode repeatedly. Predicting a positive future monthly measurement also does not establish detection **at least 30 days before onset**.

**Impact:** the numerical result can match its JSON while still failing to establish the stated early-warning performance.

**Fix:** recompute features using only information available at each prediction date; allocate capacity using operationally observable eligibility; report unique-episode recall, actual lead time and repeated-alert burden. Add a test that appending future records cannot change earlier features or predictions.

### 2. Two prototype rows are not supported by their saved artifacts

**Proposal:** “every number below comes from a committed run” — line 99.

| Prototype claim | Artifact check | Finding |
|---|---|---|
| WHO: **87,408 points; 0.003 z; ±4 SD** | [Result](/Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-super-guide/india71-t1-nutrition/eval/results/growth_standards.json) contains 87,408 and 0.003; the [validator](/Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-super-guide/india71-t1-nutrition/components/growth_standards/validate_who.py#L1) covers −4 through +4. | **Supported numerical implementation check.** |
| Linkage: **5,000 children; F1 0.51 / 0.94 / 0.97** | [Linkage result](/Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-super-guide/india71-t1-nutrition/eval/results/identity_linkage.json) is **zero bytes**. | **None of these numbers is substantiated by this artifact.** This is missing evidence, not proof the results are false. |
| Diagnostics: **120 AWCs; 3 seeds; 1.00 / 0.69 / 0.995** | [Result](/Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-super-guide/india71-t1-nutrition/eval/results/credibility_engine.json): 1.0, 0.6942, 0.9952; seeds 11–13. The district demo reports 120 AWCs, though this result does not serialize its AWC count. | **Reported performance values round correctly.** These remain legacy simulation metrics, not validation of AWC–device–month diagnostics. |
| Early warning: **5/AWC/month; 0.33 / 0.25** | [Result](/Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-super-guide/india71-t1-nutrition/eval/results/early_warning.json): K=5; linked model 0.3251; rule 0.2531. | **Arithmetic matches; interpretation does not**, for reasons above. |
| Policy: **31/31; 0 false allows**, including employment denial | [Saved policy output](/Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-super-guide/india71-t1-nutrition/eval/results/policy_gate.json): **29 cases**, pass rate 1.0, false allows 0. | **Count mismatch.** The artifact also does not identify which employment-denial cases ran. |
| Audit: **100/100** random alterations detected | [Saved audit output](/Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-super-guide/india71-t1-nutrition/eval/results/audit_ledger.json): 100 mutations, detection rate 1.0. | **Supported for the tested mutations**, not every possible tampering strategy. |

**Fix:** save the missing linkage evaluation and refreshed policy run, or remove the unsupported claims. Until then, the blanket “every number” assurance is incorrect.

### 3. The service-readiness gate can make urgent children disappear from the clock

**Proposal:** “The worker’s clock starts only when the input exists” — line 96; “Doubtful measurements trigger a re-measure task, not a referral” — line 68.

Protecting workers from blame for missing supplies is appropriate. **Suspending the only visible clock is not.** An unavailable bed or transport could leave an urgent case indefinitely “not yet overdue.” Equipment checks must not become a prerequisite for clinical assessment when danger signs exist.

The capacity guarantee is also narrower than the wording suggests: the [pipeline demo](/Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-super-guide/india71-t1-nutrition/eval/results/pipeline_demo.json) generates **600 risk alerts but 1,608 total tasks**. Capping discretionary risk visits does not demonstrate that total workload is capped.

**Fix:** maintain separate **child elapsed-time**, **resource-resolution**, and **worker-responsibility** clocks. Urgent clinical pathways must bypass discretionary ranking; uncertain anthropometry must not suppress independent clinical concerns. Budget all task types across roles.

## Major issues — material to methodology and judging

### 4. The proposed study cannot decompose the historical national discrepancy

**Proposal:** concurrent re-measurement “to decompose the wasting discrepancy into true change, coverage, measurement and classification” — line 119.

A contemporary one-district study can estimate **current local** measurement and classification error. It cannot identify how much of a national 2019–21 versus 2025 difference represents historical change. Coverage requires an independent population denominator, not merely matching children already present in registries.

Likewise, randomly sampling unflagged AWCs does not automatically yield “unbiased ground truth for validating everything else” — line 74. Targeted and random samples need known inclusion probabilities and appropriate weighting. Re-measurement alone cannot validate future prediction, linkage accuracy or treatment effects.

**Fix:** separate:
1. household enumeration plus concurrent record/re-measurement comparison;
2. prediction-time-clean prospective validation under standard care;
3. intervention evaluation with independent outcomes.

Specify sector numbers, rollout periods, primary outcome and sample-size rationale before calling the stepped-wedge study an impact evaluation.

### 5. The strongest baseline nearly matches the model; linked health data show no predictive gain

The prototype table compares against the weaker no-gain rule but omits:

- Lowest current WHZ: **0.3178 recall**.
- Anthropometry-only logistic model: **0.3260**.
- Model plus linked health: **0.3251**.

Thus the linked model improves over current WHZ by only **0.73 percentage points**, without uncertainty estimates, and performs slightly below the anthropometry-only model. The proposed privacy and integration costs therefore have **no demonstrated incremental predictive payoff yet**. Linkage may still help care coordination—that is a different hypothesis.

“Calibrated” is also too strong. No probability-calibration evidence is reported. Moreover, the [cohort calibration receipt](/Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-super-guide/india71-t1-nutrition/eval/results/cohort_calibration.json) reports:

- birth wasting **22.8%**, against a **18.9%** target;
- cumulative incidence **65.5%**, against **52.2%**;
- only **87 children** observed from birth through 24 months.

These discrepancies need uncertainty and tolerances, not a blanket calibration claim.

**Judge’s objection:** “You have shown that a model recognizes your simulated world, barely better than sorting its current measurements.”

**Fix:** show the strongest baseline and health-data ablation. Freeze thresholds; use independently specified corruption scenarios, operational audit-budget precision, subgroup false-positive rates and cluster-aware uncertainty. The rejected 0.95 tuning candidate is useful discipline, but reusing simulator variants during development does not turn them into external validation.

### 6. “No new data entry” conceals the hardest implementation dependency

**Proposal:** “no new app and no new data entry” — line 39; “Nightly deltas” — line 59.

The architecture requires information about available transport, beds, scales, task acknowledgement, completed treatment, corrections and appeals. Where do these statuses come from? Neither read access nor FHIR compatibility establishes permission or technical ability to write worklists into existing apps.

**Fix:** distinguish implemented modules from proposed adapters. Define one minimum deployment contract: source event/version, child identifier, action, owner, due date, blocked-input status and acknowledgement. Name who supplies each field. Promise reuse of existing measurements, not zero additional workflow data.

### 7. Several evidence statements still outrun their sources

The main numerical evidence is generally sound: the prevalence table matches [PIB 2023](https://pib.gov.in/PressReleasePage.aspx?PRID=1988614) and [Parliament’s 2025 annexure](https://www.sansad.in/getFile/annex/268/AU477_kllCxU.pdf?source=pqars); the scale and 23-visit figures match the [PIB factsheet](https://pib.gov.in/FactsheetDetails.aspx?Id=150744&reg=48&lang=1); the ICDS-CAS effect sizes match the [paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC9296874/).

The remaining problems are interpretation:

- **“Height-based stunting agrees”** — line 17 — still invites the invalid-control interpretation challenged previously. Similar aggregate stunting percentages do not isolate weight-measurement failure.
- **“In Melghat, the data existed”** — line 19 — connects statewide Tracker totals to particular deaths without evidence of a record-level link. [The Hindu](https://www.thehindu.com/sci-tech/health/why-do-infant-deaths-persist-in-the-tribal-dominated-region-of-melghat-in-maharashtra/article70295537.ece) reports 1,82,443 statewide cases, but attributes the 65 infant-death claim to a petitioner and records disagreement about causes.
- **“71.1% of episodes resolve”** — line 25 — needs “across the studied cohorts.” [Mertens et al.](https://pmc.ncbi.nlm.nih.gov/articles/PMC10511327/) report lower recovery in South Asia and caution about treatment and survival/follow-up selection. This is not spontaneous recovery or an Indian program benchmark.
- **“The failure isn’t missing data”** and ecosystem-wide “No…” claims are not established. Missing and unregistered children are central to the proposed target population.

**Fix:** describe a testable local implementation gap rather than universal absence of linkage, ownership or data.

### 8. The intended beneficiaries and clinical feature scope do not yet align

**Proposal:** “For every child under 5 … WHO 2009 weight-velocity z” — line 65.

[WHO velocity standards](https://www.who.int/tools/child-growth-standards/standards/weight-velocity) provide monthly increments through 12 months and longer increments through 24 months—not a general monthly velocity z-score through age five.

Meanwhile, infants, tribal communities and migrants are three overlapping priorities, not one sharply defined pilot denominator. Registry-based missed-measurement alerts cannot discover children absent from both registries. Postnatal prediction cannot prevent wasting already present at birth.

**Fix:** define one initial age/geography cohort, explicitly include community identification of unregistered children, and separate infant clinical pathways from older-child monitoring. State what maternal or caregiver action the system actually enables.

### 9. The governance safeguards reduce risk but do not prove the claimed guarantees

**Proposal:** “s.9 exemptions … or verifiable parental consent” — line 69.

Consent and an exemption from restricted processing are not interchangeable. The legal gate should explicitly address whether the intended processing falls within section 9(3), and, if so, its applicable exemption—not imply parental consent automatically resolves that question.

Also:

- Producing aggregates does not remove the need for authority to ingest identifiable longitudinal records.
- [ADR 002](/Users/imdigitalashish/Projects/AshishKumarVerm/techfest-2026/.worktrees/imdigitalashish-super-guide/india71-t1-nutrition/architecture/adr/002-measurement-diagnostics.md) says employment use is “technically impossible.” A supervisor can infer a worker from an AWC and misuse information obtained under an allowed purpose.

**Fix:** make the fallback *lawfully supplied non-identifying aggregates*, unless microdata processing is separately authorized. Describe purpose denial as a safeguard with residual misuse risk, backed by oversight and grievance—not technical impossibility.

## Minor issues

- **Standalone evidence traceability:** “News reports compiled in our research notes” is not an adequate submission reference. Put identifiable titles/dates and compact links or DOIs in the six-page document itself.
- **Format remains unverified:** the Markdown contains approximately 2,516 words, but that cannot establish six-page compliance with tables, diagram and references. Check the rendered PDF’s page count, fonts and margins; do not solve overflow by shrinking labels.

## Judging-criteria assessment

| Criterion | Assessment and highest-value improvement |
|---|---|
| Problem identification | Strong implementation focus; replace the national discrepancy as the principal estimand with a measurable local failure and defined underserved cohort. |
| Evidence and context | Credible core sources; repair artifact mismatches, evaluation leakage and ecological inferences. |
| Existing ecosystem | Good component map; substantiate what fails in current workflows rather than claiming capabilities are universally absent. |
| Proposed solution | **Concrete enough at module level; not policy-only.** Add one operational input/output contract and distinguish built components from unapproved integrations. |
| Feasibility and roadmap | Appropriate prerequisites, but no costed pilot, staffing allocation, acknowledged integration partner or assessable trial design. |
| Impact and scalability | Sensibly avoids invented lives-saved estimates. Quantify referral completion, total workload and cost with uncertainty; national scale remains conditional on local institutions and interfaces. |

## Five most damaging remaining Q&A questions

1. **“Does your held-out evaluation use future information?”**  
   **Best honest answer:** “Yes: the current AWC credibility feature is calculated over the complete simulated history. Separate seeds prevent identity overlap, not that look-ahead. We must rerun prediction-time-only evaluation; the current recall is not prospective evidence.”

2. **“Why use ML and sensitive linked health data when sorting by current WHZ almost ties it?”**  
   **Answer:** “We have not demonstrated enough incremental predictive value. The simple baseline is a viable initial comparator or implementation. Health linkage remains a care-coordination hypothesis until it improves verified outcomes or prediction sufficiently to justify its costs.”

3. **“How can re-measuring children today explain the NFHS–Tracker difference years ago?”**  
   **Answer:** “It cannot explain historical national change. Our defensible study estimates current local coverage and recording errors, using independent enumeration and contemporaneous measurements.”

4. **“If there is no transport for a sick child, does your timer simply never start?”**  
   **Answer:** “The proposed wording permits that and needs correction. Child elapsed time must remain visible, while responsibility for a supply blockage escalates separately. Clinical urgency must not depend on the worker’s discretionary visit allocation.”

5. **“What is deployable without child-data authorization or approved app interfaces?”**  
   **Answer:** “A synthetic demonstration and, where available, diagnostics using lawfully supplied non-identifying aggregates. We cannot promise identifiable ingestion, named worklists or an operational aggregate fallback merely because the final output is aggregated.”

## Highest-leverage sentence-level rewrites

These replacements mostly remove overclaims rather than add scope.

1. **Replace “The failure isn’t missing data…”**
   > “The pilot will test whether existing measurements lead to a documented owner, timely assessment and completed care, while separately identifying children missing from routine records.”

2. **Replace the Melghat inference**
   > “Reporting from Melghat describes infant deaths and coordination failures alongside substantial recorded malnutrition; it does not establish that the children who died had been identified and followed up in Poshan Tracker.”

3. **Replace “no new app and no new data entry”**
   > “Poshan Setu reuses existing growth records; worklist delivery and action acknowledgements depend on agreed departmental interfaces.”

4. **Replace “These feed a calibrated, interpretable model…”**
   > “These feed an experimental 90-day ranking model; prospective calibration and incremental benefit over current-WHZ prioritisation remain unestablished.”

   Replace the universal velocity claim with:
   > “WHO velocity features are used only within their published age and measurement-interval ranges.”

5. **Replace the service-readiness paragraph**
   > “Child elapsed time runs from the first actionable flag. Missing supplies trigger a separate resource-resolution clock and escalation; they do not suspend visibility of clinical delay or urgent assessment.”

6. **Replace the simulator calibration and 0.95 tuning story**
   > “The simulator is parameterised from published cohort estimates but does not fully reproduce them. Synthetic runs test implementation under stated assumptions, not clinical effectiveness or real-world calibration.”

7. **Replace the pilot’s discrepancy-decomposition sentence**
   > “Independent household enumeration and concurrent blinded re-measurement will estimate current local coverage and measurement/classification errors; they will not explain historical national prevalence changes.”

8. **Replace the legal fallback sentence**
   > “Each identifiable data flow requires a written legal basis addressing consent and any applicable restrictions or exemptions; without it, deployment is limited to lawfully supplied non-identifying aggregates.”

9. **Replace “national by construction”**
   > “The components are reusable nationally, but expansion depends on state-specific approvals, interfaces, languages, service capacity and demonstrated pilot value.”

For space, cut the international superlative, “stunting agrees,” the tuning anecdote and repeated statutory exposition. Use the recovered space for **one pilot cohort, one primary outcome, a cost/staffing envelope and the minimal integration contract**.
