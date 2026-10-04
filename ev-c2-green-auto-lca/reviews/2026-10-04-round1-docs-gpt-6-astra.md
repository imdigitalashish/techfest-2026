# Independent review: final Round-1 documents

- **Reviewer model:** GPT-6 Astra (`gpt-6-astra`), independent methodology/statistics/novelty and expert-jury reviewer.
- **Date:** 2026-10-04 (IST).
- **Commit reviewed:** `e023a91ddc635ad401a95681db2fcd99b141542c`, after the requested fetch and rebase.
- **Submission artifacts:** `deliverables/round1-methodology.md` v1.0 and `deliverables/round1-roadmap.md` v1.0.
- **Review boundary:** document claims checked against `_briefs/ev-infra.txt`, committed results, source records, scenario definitions, implementation, ADR v2 and previous review decisions. Paths below are relative to `ev-c2-green-auto-lca/` unless explicitly prefixed with the repository root.
- **ISO limitation:** all comments about ISO 14040/14044 requirements below rely on my own knowledge of those standards, not a newly opened copy of the paywalled text. This is neither a clause-by-clause conformity assessment nor the independent critical review required for an ISO-conformant public comparative assertion. The underlying study PDFs were not re-audited in this pass; their committed transcriptions were inspected. Literature metadata checks are identified separately below.

**Disposition: revise before submission. Findings: 2 critical, 9 major, 3 minor.** "Critical" means a submission blocker, including missing required administrative information; "major" means a material defensibility, capability or delivery-plan problem; "minor" means a qualification or release-readiness improvement. These are not fourteen newly discovered arithmetic failures.

## Round-1 criterion scores

These are strict, artifact-as-submitted judgments, not a prediction of selection. Weighted points are the score divided by ten, multiplied by the official criterion weight.

| Official criterion | Weight | Score / 10 | Weighted points | What would raise this score by two points |
|---|---:|---:|---:|---|
| Problem Understanding & Relevance | 25 | 8 | 20.0 | Freeze one real manufacturer/ICAT decision with equivalent service or material grade, an identified user and an explicit interpretation/action. Show why the Indian route evidence changes that decision, rather than relying mainly on a grid-sensitive legacy vehicle example. |
| Feasibility & Technical Soundness of Approach | 25 | 5 | 12.5 | Correct the mixed-basis headline, demonstrate the claimed compatibility/EOL rejection, bound important omissions and define model-conditional uncertainty. Deliver one fully specified chain rather than promising every method before the source data exist. |
| Innovation / Novelty of Proposed Solution | 20 | 6 | 12.0 | On genuinely unseen documents, show useful complete-record coverage at high precision and measured human-effort improvement over manual/rule baselines; demonstrate a source-qualified Indian route comparison. Neither extraction nor prospective vehicle LCA is itself new. |
| Clarity & Completeness of Implementation Roadmap | 20 | 6 | 12.0 | Add a two-person critical path, owners/capacity, coverage and acceptance thresholds, a data-qualified fallback, and dated milestones for every December commitment. Respect exams and the separately documented viva dates; make breadth/CFF/full AR6 conditional or stretch. |
| Planned Data Strategy (sources & integration approach) | 10 | 7 | 7.0 | Specify the actual route sources, minimum compatible fields, reuse permissions, deduplication/versioning and review ownership. Prioritize representative, decision-relevant records over reaching 300 largely correlated scalar entries. |
| **Total** | **100** | | **63.5 / 100** | |

The problem framing, public-data strategy and honest rejection of a premium-data prerequisite are strong. The official brief explicitly allows a defined demonstration scope; the team loses feasibility, not relevance, by making unnecessary breadth commitments.

## What the evidence does support

The existing engine tests passed: **18/18**, with bytecode and pytest cache writing disabled. To preserve the instruction not to modify generated files, I did not invoke the output-writing `eval.main()`. I called its calculation, summarization, verification and independent-crosscheck functions in memory at the committed **10,000 draws and seed 20261004**. All **13 scenario summaries**, verification results and independent-crosscheck results matched `eval/results/latest.json` exactly. This confirms reproducible implementation, not independent physical validation.

| Topic | Assessment at the reviewed commit |
|---|---|
| Goal, scope and units | Much improved: a screening GHG scope, vehicle-km, common lifetimes, battery reference flows, and declared rather than functional units for materials are now stated. Remaining operational qualifications are in issues 5, 6 and 12. |
| Car gas basis | The prior AR5/AR6 family-collapse defect is fixed for the current central and OM car scenarios. Their active grid characterization and aggregate fuel/vehicle factors are labelled AR5 GWP100; CO2-only car sensitivities remain separately flagged. This does not certify boundary completeness or audit every source's underlying elementary flows. |
| AR5 versus AR6 grid | Independently recomputed meter factors are approximately **0.841699** and **0.841676 kg CO2e/kWh**, respectively: a **0.00272%** difference for this particular partial-grid formulation. The document's "<0.01%" claim is supported; it does not justify relabelling aggregate inventories. |
| Paired Monte Carlo | Shared record IDs are sampled once per draw. The inactive-parameter pruning and tie-aware Spearman fixes are present. Pairing is not a substitute for the additional physical/source correlations that the roadmap acknowledges are missing. |
| Source ranges | The new two-piece lognormal preserves the listed central value as its median and the listed 2.5th/97.5th percentiles. It is not an ordinary single lognormal. Triangular bounds and uniform ambiguity ranges are modeling choices, not measured Indian population distributions. |
| Importance and pedigree | The renamed normalized squared Spearman importance and elasticity-weighted pedigree score are correctly described as screening measures, not a variance decomposition or validated DQR. The car ranking of approximately **64% BEV consumption** and **25% petrol consumption** matches the run. |
| Verification terminology | **0.06% 2W MAPE** and **0.999% car MAPE** reproduce. Calling these arithmetic implementation verification, rather than validation, is correct. Especially for the table-implied scooter inputs, agreement is partly constructional. |
| ICCT wording | The table-implied approximately **2.0 L/100 km / 4.13 kWh/100 km** versus printed **2.2 / 3.7** discrepancy is supported by the committed transcription and reconstruction. The current "documentation gap, not evidence that ICCT's conclusion is wrong" wording is appropriately cautious. Keep the request for author clarification; do not promote a proposed explanation into an established error. |

The reproduced headline quantities have different interpretations:

| Comparison | Plug-in central saving | 5th-95th percentile saving | Fraction of paired draws with lower alternative emissions |
|---|---:|---:|---:|
| 2W, average grid | 38.1% | 32.0% to 43.2% | 1.0000 |
| 2W, operating margin | 16.2% | 7.8% to 23.2% | 0.9993 |
| BEV sedan, average grid | 10.0% | -10.1% to 25.6% | 0.8078 |
| CNG sedan versus petrol, average-grid scenario | 0.9% | -24.1% to 11.0% | 0.3057 |

These values are conditional on the chosen distributions and fixed structural assumptions. The first two rows remain mixed-basis indicators, not harmonized climate-change comparisons.

## Numbered issues

1. **critical - Required team information is still blank.**

   **Evidence:** methodology header; roadmap header; repository-root `_briefs/ev-infra.txt`, "Round 1: Concept & Roadmap Submission", "Team Specification and Eligibility" and "Key Dates".

   Both documents retain registration/name placeholders. A final submission needs the team name, Team ID, institution and contact details; the actual 2-5 eligible members and authorized team leader must be known. The roadmap's reminder to fill these by 15 October is not the completed information. Registration closes **15 October**, submission **30 October**, and only the team leader may submit.

   **Concrete fix:** make completed administrative fields, eligibility/one-team confirmation and a leader-only upload checklist a release gate. Do not fabricate these details. If they are provided in a separate official form, explicitly identify that completed form instead of presenting these artifacts as independently complete.

2. **critical - The prominent 38.1% headline still presents an unharmonized indicator as an AR5 GWP100 saving.**

   **Evidence:** both documents' generated headline; methodology sections 1, 3 and 10; `eval/render_docs.py::headline/table`; `eval/results/latest.json`, `scenarios.in2026_avg_co2e`; `data/factors/vehicle_2w.yaml`.

   The car correction is real, but the common headline describes the results as "CO2e GWP100 (AR5, as ICCT inputs)" and then foregrounds the scooter saving. Its production factor is on the 20-year-methane basis **and its maintenance factor is unspecified**. In the central e-scooter total, approximately **10.6%** is assigned to the former and **2.5%** to the latter. Section 3 mentions production but not the unspecified maintenance basis; that later caveat does not adequately qualify the first thing a jury reads. The missing section-10 table's renderer would also call every row g CO2e/km without showing harmonization status.

   **Concrete fix:** separate the car result from the as-coded scooter illustration in every rendered surface; include the mixed/unspecified bases beside the number. Keep the scooter reproduction in the evidence appendix until its relevant aggregates are replaced or genuinely recharacterized. Do not "fix" this by relabelling source aggregates.

   **Suggested replacement:** "The legacy sedan case uses a consistently labelled AR5 GWP100 basis: its plug-in BEV saving is 10.0%, with a model-conditional 90% interval of -10.1% to 25.6%. The scooter calculation gives a 38.1% reduction in a partial, mixed-basis GHG indicator; it is not yet a harmonized GWP100 comparison."

3. **major - The results table is absent, and the claimed anti-drift protection certifies that absence.**

   **Evidence:** methodology section 10 has adjacent `results-table:begin/end` markers and no table; `eval/render_docs.py::render`; `eval/check_docs.py::main`; methodology introductory run identifier.

   I checked that the block contains **zero non-whitespace characters**, `render(text, latest)` leaves it unchanged, and the existing drift test passes. The regex requires a newline after the opening marker and another before the closing marker; the empty block has only the one separator. The final methodology therefore omits the promised scenario totals and P(lower) table despite claiming it was generated.

   Provenance also drifts: the introduction says inputs ID `83a80a699b`, while the headline/latest use `0d15e1cf49`. Under the harness's own tree-hash rule, reviewed HEAD is `4738c6f62d`: the later dashboard-code change changes `components/`. This is not an arithmetic discrepancy; all calculated summaries matched. It is an unresolved distinction between a historical run identity and current checkout identity.

   **Concrete fix:** handle empty marked blocks; assert the block exists exactly once and contains the required rows, bases and probabilities; render the artifact and inspect the submission export. Generate the introductory manifest too. Either retain an explicitly identified historical run snapshot or define an input fingerprint that accurately tracks the calculation dependencies. Do not present a passing string-replacement test as proof that a complete table exists.

4. **major - End-of-life safeguards and switchable models are described as implemented, but are only metadata/plans.**

   **Evidence:** methodology section 3 boundary matrix and section 5; `components/lca_engine/greenauto/db.py::Record`; `components/lca_engine/greenauto/engine.py::check_scenario/run_scenario`; roadmap stage 3.

   `eol_included` is stored but never checked by the scenario evaluator. In an in-memory copy of the current petrol sedan, adding an `end_of_life` stage using the already-EOL-inclusive production expression produced **no validation problem** and increased the result from **226.172 to 257.624 g/km**. Nothing rejects the double counting. The engine also has no selectable cut-off, avoided-burden or CFF implementations, despite section 5's present-tense "Three switchable models" and "default". Current cases inherit aggregate production/recycling factors; they are not demonstrations of the promised cut-off model.

   **Concrete fix:** distinguish current inherited-source accounting from planned EOL policies. Implement and test the incompatibility guard before claiming enforcement; until then explicitly call it a manual review rule. Defer CFF unless its necessary parameters, allocation factor and compatible source boundaries are available.

   **Suggested replacement:** "Current cases retain the source's embedded recycling treatment and do not add a separate EOL stage. `eol_included` records this fact; automated rejection of incompatible additions and selectable EOL models are planned."

5. **major - The proposed cut-off rule is not evidence that the current omissions are acceptable.**

   **Evidence:** methodology section 3, boundary matrix and "<1% / cumulative <5%" rule; sections 5 and 11; scenario stage definitions.

   Calling the rule "proposed" is honest, but no exclusion budget shows that mining energy, coal transport, gas supply, infrastructure or logistics meet it. No-replacement is a lifetime/model assumption, not automatically an immaterial cut-off. Using the team's own battery factor, one extra sedan pack adds **9.48 g/km**, about **4.7%** of the current BEV total; one extra scooter pack adds **1.64 g/km**, about **4.1%**. These calculations do not prove a replacement occurs; they show why exclusion cannot be justified as inherently below 1%.

   **Concrete fix:** classify each item as outside the chosen scope, assumed absent, embedded in an aggregate, or excluded after a quantified screen. For potentially decision-relevant omissions, give justified bounds or discrete sensitivities and a dated data action. Define the denominator and cumulative accounting for the 1%/5% rule and consider mass/energy as well as environmental significance. **ISO knowledge qualification:** those percentages are the team's proposed policy, not universal ISO 14044 thresholds.

   **Suggested replacement:** "The current screening cases do not yet demonstrate compliance with the proposed exclusion budget. Their intervals cover sampled input uncertainty, not unresolved exclusions, replacement assumptions or alternative system boundaries."

6. **major - The grid comparison ladder changes characterization/completeness as well as accounting method.**

   **Evidence:** methodology section 1's 16.2%-56.4% span and section 9B; `data/vehicles/case1_2w_scooters.yaml` / `data/vehicles/case2_cars_sedan.yaml`, build-margin scenarios; `components/lca_engine/greenauto/grid.py::grid_factor`; `data/factors/energy.yaml`, T&D record.

   Average and operating-margin headline scenarios include non-CO2 and partial upstream additions; build margin is **CO2-only**, because its fuel mix is unknown. The source scenario labels and service refusal correctly say this, but the methodology's opening comparison does not. Thus the entire span is not a controlled estimate of "grid-accounting method" alone. Retaining average as attributional and explicitly declining a consequential-LCA claim are correct.

   Also, **17.63% includes commercial/unbilled losses**, according to the team's record. Grossing up by that number can be an explicit allocation of system emissions to billed electricity; it is not established as a purely physical loss on an EV's metered kWh. Finally, one FY2025-26 grid held constant over a 15-year vehicle lifetime is a snapshot sensitivity, not a forecast of a vehicle bought in 2026.

   **Concrete fix:** compare methods on a common CO2-only basis in one clearly partial panel, or qualify/complete the non-CO2 additions before comparing full indicators. Label the BM result and state-map units locally. State the commercial-loss convention and add a defensible technical-loss sensitivity rather than silently treating billed-energy accounting as delivery physics.

   **Suggested replacement:** "Average and OM use partial-upstream CO2e; BM is a separate CO2-only sensitivity pending a compatible fuel mix. These illustrative calculations hold the selected annual grid factor constant over the legacy vehicle lifetime."

7. **major - Probability, point-estimate and robustness language needs an explicit model-conditional interpretation.**

   **Evidence:** methodology sections 1, 7 and 10; `components/lca_engine/greenauto/engine.py::run_scenario/_importance`; `components/lca_engine/greenauto/db.py::Pedigree/Record.sample`; `data/factors/vehicle_car.yaml`, methane-slip record; committed results.

   "Always lower" is literally false even within the tested scooter scenarios: **7 of 10,000 OM draws are not lower**. The sedan's 10.0% is a plug-in central calculation, not a settled advantage: **P(lower)=0.8078** and the 90% interval spans zero. These are input-distribution probabilities, not frequentist confidence that Indian BEVs generally outperform petrol.

   The difference between point and distribution summaries matters beyond wording. The CNG central methane slip is **60 mg/km**, while its subjective uniform distribution is **60-1000 mg/km**. Its **+0.9% central saving**, **-5.2% median saving** and **P(lower)=0.3057** are therefore mathematically compatible, but unexplained in the submission. Label the plug-in estimate rather than implying it is the draw median.

   The uncertainty implementation improved, but its calibration has not been demonstrated: it uses a universal basic factor of 1.05, mostly subjective pedigree assignments, incomplete correlations and fixed structural choices. **121/124 records have blank pedigree rationale strings**. Uniform interpolation between two conflicting published readings does not turn either into measured on-road variability. The 64% screening-importance result is correct under those priors, but "highest-value next dataset" additionally requires achievable uncertainty reduction and collection cost; it is not a value-of-information calculation.

   **Concrete fix:** define central/median/interval/P(lower) together, retain scenario uncertainties outside the probabilistic interval, and schedule justification/review of dominant input priors and correlation assumptions. Identify the two-piece lognormal explicitly; explain that adopting a published central value as its median is an assumption, not an IPCC distribution fit.

   **Suggested replacement:** "Central estimates use the listed point inputs. Intervals are the 5th-95th percentiles of paired draws from our stated distributions; P(lower) is the fraction of those draws with lower emissions. They are not empirically calibrated coverage guarantees and omit unresolved structural choices. The scooter indicator is lower in nearly all tested draws; the sedan result is not decisive."

8. **major - The 1.4% false-accept bound still overstates what the verifier experiment establishes.**

   **Evidence:** methodology section 9A; ADR v2 "White"; `components/ingestion/autoresearch/eval.py`; prior ADR review issue 3 and its acceptance decision.

   For independent Bernoulli trials from a specified deployment distribution, zero events in 208 trials gives a one-sided 95% upper bound of approximately **1.43%**. That is not this experiment: the negatives are two deterministic digit perturbations per existing positive, clustered within reused source documents, and the verifier was adapted using this corpus. The earlier review explicitly warned that these clustered synthetic cases do not justify a real-world false-accept bound; the accepted revision retained the number but lost that restriction.

   **Concrete fix:** report the regression count without a deployment bound. Preserve the planned document/publisher-held-out evaluation, add wrong-unit/year/header/adjacent-cell and unchanged-quote/wrong-field negatives, and report uncertainty at an appropriate independent document/sample level. A value occurring somewhere in its own quote, including permitted 100/1000 scaling, still does not bind the correct unit or field.

   **Suggested replacement:** "The verifier accepted none of 208 synthetic digit-perturbed regression cases. Because these cases are clustered, reused and not sampled from deployment errors, this does not estimate or upper-bound the deployment false-accept rate."

9. **major - The dated roadmap is useful, but the minimum scope and D fallback are not yet a credible two-person contract.**

   **Evidence:** roadmap sections 0, 1 and 5; methodology sections 4, 5 and 8; ADR v2 plan/status; repository-root `PLAYBOOK.md` sections 8 and 10.

   Credit: deadlines match the official brief, registration and leader submission are recognized, and the 17 November checkpoint/18-25 November freeze is sensible. However, two parallel 1-17 November streams promise an extractor, route data, process/exchange modeling and three EOL methods, followed by a web app/data-entry flow/rehearsal. The December commitments also include **300 records across eight layers**, correlation groups and an **elementary-flow AR6 inventory**, without owners, effort or a source gate for decomposing legacy CO2e aggregates. An AR6 conversion cannot be promised merely because AR5 aggregate factors exist.

   The D no-go fallback still requires a "material record set" without identifying a source that survives failure of the material-data gate. It has no replacement comparison/acceptance criterion, and section 0 still unconditionally commits to D. Broad source types are not a guaranteed compatible route pair.

   Reconcile smaller scheduling contradictions too: methodology sends process records to "roadmap stage 4", which is actually product/rehearsal; ADR says revisit on 12 October although the D decision gate is 7 October; the earlier ADR chain target is 13-18 October versus 13-30 in the roadmap. The playbook additionally records **vivas on 27-28 November**, while the product phase starts on 26 November.

   **Concrete fix:** assign actual role owners and realistic student-hours with a two-person base plan. Require one compatible Indian route pair, one allocated process and one EOL approach; move 300-record breadth, CFF and unavailable elementary-flow conversion to conditional/stretch scope. Give each remaining commitment a date and measured exit. Define a no-go branch using already identified, usable evidence and a revised demo, or explicitly retain the existing vehicle/grid demonstration and withdraw the route-comparison promise. Add a feature-freeze date before rehearsal and keep owner-dependent work out of the viva window.

10. **major - The narrow novelty claim is credible as a hypothesis, but its evaluation can still pass without useful extraction.**

   **Evidence:** methodology section 9A/D; roadmap stages 1b and 2; ADR v2 metrics; `research/landscape.md` section 5, "Nobody ships...".

   The correction from "first-ever extraction/prospective India LCA" to evidence-anchored semantic qualification plus measured curation effort is substantial and appropriate. An Indian material-route demonstration is relevant application value, not automatically a new LCA method. No measured curation gain or complete D chain yet supports a delivered novelty claim.

   "Complete-record precision >=0.9 at stated recall" allows arbitrarily low recall, even acceptance of only a trivial subset. Field-level F1 on development data does not establish useful coverage on unseen publishers. Reporting reviewer minutes without a timing protocol also permits omission of setup, failed documents, rejected candidates and corrections. The landscape's universal "Nobody ships" assertion remains stronger than either its narrow search or the newly cautious methodology.

   **Concrete fix:** predeclare a minimum complete-record recall/coverage, document-macro reporting, denominator including failures, independently adjudicated gold annotations and a human-timing protocol. Compare manual entry, rules, extractor alone and extractor plus semantic checks on the same held-out task; distinguish annotation/setup cost from recurring curation cost. Replace the universal absence claim with the bounded search result. Cite the verified prior work below without claiming its exact semantic-check behavior is known.

   **Suggested replacement:** "We will test whether evidence binding and compatibility checks reduce human minutes per correct, usable Indian LCA record at a prespecified precision and coverage level. We have not yet established a performance advantage over prior extraction systems."

11. **major - The synthetic-data disclosure is internally contradictory and should be scoped explicitly.**

   **Evidence:** methodology section 12, "Synthetic data: none"; roadmap section 2, "none so far"; methodology section 9A and the verifier evaluator's generated negatives; official General Rules 5-6.

   There may be no synthetic **inventory** records, but the solution already uses **208 synthetic digit-perturbed evaluation cases**. Both meanings can coexist; an unqualified "none" cannot. The official requirement applies to synthetic data used in the solution, not only environmental factors. Monte Carlo draws should also be described as simulated uncertainty draws, not additional observations.

   **Concrete fix / replacement:** "No synthetic inventory or vehicle-performance records are used in the current case studies. Verifier evaluation uses 208 labelled synthetic digit-perturbed quote negatives generated from source records. Monte Carlo draws simulate the stated uncertainty model and are not measured data. Future synthetic inventory records will be explicitly labelled."

12. **minor - Operational functional equivalence, allocation and public-review wording need one more tightening pass.**

   **Evidence:** methodology sections 2-4 and introductory public-comparison disclaimer; `data/factors/vehicle_2w.yaml`, plug-consumption ambiguity record.

   Vehicle-km is defensible when service is held equivalent; passenger-km is not automatically required. But "same segment and service" and "1-2 riders" do not yet freeze payload, duty cycle, range/service constraints or the D part's grade, lifetime and substitution ratio. The two-wheeler record says charging losses are **assumed** included, whereas section 3 states inclusion without that qualification. The car record does explicitly include a 15% charging-loss uplift. Do not imply the same evidence exists for both.

   **Concrete fix:** specify a compact decision protocol for each case and keep 1 kg at gate as a declared-unit comparison unless functional substitution is established. Mark the scooter charging boundary as an assumption and test it.

   **ISO knowledge qualification:** the allocation hierarchy is broadly consistent with my understanding of ISO 14044, but "mass or energy, by the dominant function" is not by itself a demonstration of physical causality. Explain the physical relationship or justify another allocation basis and sensitivity. For public comparative assertions claiming ISO conformity, a generic independent expert check is not interchangeable with the appropriate interested-party panel critical review. State intended audience/use and keep current outputs out of product-certification or ESG-compliance claims.

13. **minor - Keep the independent studies as heterogeneous context, not a statistical band or a causal diagnosis.**

   **Evidence:** methodology sections 1 and 8; `eval/eval.py::independent_crosscheck`; the three non-ICCT benchmark YAML files.

   The explicit "not validation" wording is good and the reported min/max arithmetic is correct. However, the range pools selected hatchbacks, SUVs and grouped studies with different lifetimes, grids, boundaries and characterization: TERI is AR6, IITK uses AR5-like factors, and IITG's exact characterization is not transcribed. TERI's report covers 59 vehicles but only eight selected rows are present here. Diesel has one SUV point; CNG has two transcribed TERI points, not two independent studies.

   **Concrete fix:** call it a "range of transcribed heterogeneous published estimates", state the row-selection rule and distinguish vehicle-point count from study count. Do not infer that methane slip or mass explains a mismatch until a harmonized bridge calculation tests that hypothesis. These studies have already been inspected; reserve new compatible cases before later calling an assessment held-out interval validation.

   **Suggested replacement:** "Our estimate is contextualized against the selected published vehicle estimates below. Inclusion in their range is not evidence of accuracy, and being outside it identifies a reconciliation task rather than a model error."

14. **minor - The data-release and tooling disclosure needs an auditable implementation path, not just a source list.**

   **Evidence:** methodology sections 6 and 12; roadmap sections 2-4; `data/sources/*.yaml`; `components/lca_engine/greenauto/engine.py::_ranks`; project README; repository CI configuration.

   AI assistance, core software, external datasets and sources are substantially disclosed, so I would not claim the disclosure section is missing. Remaining gaps matter for a promised open corpus: **16/19 source registry entries have blank license fields**, and the other three do not assert open reuse rights. There are **19 source IDs but 18 distinct URLs**, including a duplicate CEA guide; distinguish registry entries from unique documents. Public accessibility alone does not establish a redistribution license, although lack of an open license does not by itself prove a factual extraction is impermissible.

   The code now imports **SciPy**, absent from both the methodology software list and quickstart dependencies. The reviewed repository has no checked-in CI workflow/configuration establishing the claim that these checks run automatically on merge; current tests demonstrate local checks, not a hosted admission pipeline.

   **Concrete fix:** record reuse status per source and separate redistributable records/brief quotations from source-document distribution; add source hashes/version retrieval and deduplication policy. Publish a complete dependency/environment manifest, including SciPy, and distinguish installed reference engines from planned integrations. Either wire the claimed CI gates or label them planned. Give standalone submissions usable references rather than assuming judges can navigate repository-relative paths.

## Novelty: verified comparison points and limits

I independently opened Crossref metadata on 2026-10-04 for both recent papers named by the team:

| Prior work | Verified fact | Consequence for the claim |
|---|---|---|
| Kumar et al. (2025), *A Large Language Model-based Framework to Retrieve Life Cycle Inventory and Environmental Impact Data from Scientific Literature*, Environmental Science & Technology 59, 22533-22543, [DOI 10.1021/acs.est.5c05955](https://doi.org/10.1021/acs.est.5c05955) | Title, authors, journal and publication metadata exist in [Crossref](https://api.crossref.org/works/10.1021/acs.est.5c05955). | Generic LLM retrieval of LCI/impact data is not a defensible novelty claim. |
| Tang et al. (2026), *From literature to knowledge graphs: automated extraction and retrieval of life cycle assessment data with large language models*, Journal of Industrial Ecology 30, 1985-2000, [DOI 10.1007/s44498-026-00135-8](https://doi.org/10.1007/s44498-026-00135-8) | Title, authors, journal and publication metadata exist in [Crossref](https://api.crossref.org/works/10.1007/s44498-026-00135-8). | LCA extraction/retrieval/knowledge-graph packaging already has contemporary prior work. |
| [carculator modeling documentation](https://carculator.readthedocs.io/en/latest/modeling.html) | Opened: parameterized vehicle models, inventories, impact calculation, exports and a web interface. | A vehicle engine/dashboard is useful integration, not itself the novel component. |
| [premise overview and boundaries](https://premise.readthedocs.io/en/latest/getting_started/overview.html) | Opened: IAM-based prospective inventory updates, explicit system models, external inventories and licensed ecoinvent dependency. | Prospective grids/material inventories are established; public-data accessibility can be a genuine product distinction, not proof of globally unique methodology. |

Publisher full text for the two recent papers returned **403/406**. I therefore do **not** claim that they lack quote verification, field binding or human-effort evaluation, nor that this implementation outperforms them. No exhaustive 2024-2026 literature search or universal absence claim is established by these checks.

**Novelty verdict:** A is a credible, measurable engineering hypothesis if it demonstrates compatibility-aware curation on Indian public documents. D is credible challenge-specific utility if it compares genuinely equivalent routes with usable Indian evidence. A plus D is more persuasive than a broad state-grid service, but the current evidence supports a proposal, not a proven methodological advance.

## Did the earlier ACCEPTED decisions actually land?

The three review records contain no rejected items. Acceptance should not be equated with closure.

| Earlier decision | Current assessment |
|---|---|
| Sol 1, 3, 6, 7: exact AR5/AR6 families, inactive bindings, asymmetric source quantiles, rank ties | **Reflected in the inspected code and passing regressions.** Do not resurrect the old car AR5/AR6 defect. |
| Sol 4: India-specific share | **Changed as promised** to stage-weighted dominant-emission-factor geography. It remains a coarse stage classification, not proof that every input in that stage is Indian. |
| Sol 5 / hostile 14: rendered documents and anti-drift | **Incomplete:** correct headline numbers, but missing table, stale introductory identifier and a false-negative drift check (issue 3). |
| Hostile 2-5: scope, functional units, allocation, EOL | **Substantially better documentation; incomplete implementation:** untested exclusion budget, charging-boundary assumption and non-enforced EOL metadata (issues 4, 5, 12). |
| Hostile 8 / Astra 6: uncertainty and distinct contribution/scenario/sampling statements | **Partly reflected:** correct terminology and source-range handling; robustness and prior justification remain too strong/incomplete (issues 6-7). |
| Astra 2-3: semantic qualification and honest verifier evidence | **Partial:** number-boundary/value checks are real; field/unit/year/locator checks are planned, and the real-world 1.4% inference is still unsupported (issues 8, 10). |
| Astra 1, 4, 7-8: A+D, bounded national grid, narrowed novelty, feasible plan | **Strategic change reflected; completion conditional:** D is not source-qualified yet, the fallback/scope needs repair, and the landscape still contains a universal absence claim (issues 9-10). |
| Hostile 10 and ICCT wording | **Reflected:** arithmetic verification is distinguished from plausibility, and the discrepancy is attributed cautiously (retain these changes). |

The hostile-review decision log still describes the earlier AR6-grid/AR5-input resolution, whereas the later Sol decision and current code supersede it with AR5. Preserve raw historical reviews, but add a superseding status note rather than leaving contradictory "done" explanations for a jury to reconcile.

## Presentation and submission readiness

The two files contain approximately **2,821 and 1,251 whitespace-delimited words** respectively, even without the missing results table. The brief says concise; it does not supply a page cap in the inspected text. Do not invent one. A short decision/evidence summary plus a compact dated owner/exit table would serve Round 1 better than repeating the headline in every artifact. Move implementation detail to an appendix if the portal permits it.

Expand WTT/TTW, pedigree, CFF, BF-BOF/DRI-EAF and the internal "spike A/D" labels on first use. The jury should understand the decision, what is working now, what remains conditional and why the evidence is defensible without reading the ADR. The official Round-2 dashboard/database/engine/case-study/scalability surfaces are represented in the plan; missing credibility is mainly in how all commitments become deliverable, not in an absent generic deliverable heading.

## Five-line verdict

1. **Not submission-ready as labelled final:** required team information and the misleading mixed-basis scooter headline are critical blockers.
2. **The arithmetic reproduces:** 38.1% is a mixed-indicator result; the AR5-labelled sedan's 10.0% saving is conditional and its interval crosses zero.
3. **The strongest assets are traceability and honest verification terminology;** repair the empty table, unimplemented EOL guarantees and false-accept inference.
4. **Keep A+D, but narrow the contract:** one source-qualified decision chain, meaningful extraction coverage and measured human effort, with a genuinely executable fallback.
5. **Strict Round-1 score: 63.5/100; findings: 2 critical, 9 major, 3 minor;** focused evidence and claim repairs would matter more than another hundred records.

## Lead decisions (4 Oct 2026, 11:05 IST)
| # | Decision | Reason / action |
|---|---|---|
| 1 | **ACCEPTED** (gate; cannot be fabricated) | Release-gate box at the top of both documents, plus the leader's upload checklist. Team details are a user action item (register by 15 Oct). Documents are content-final v1.1 and administratively pending. |
| 2 | **ACCEPTED** | The rendered headline now leads with the harmonized AR5 sedan result (10.0 %, P(lower) 0.81, "not decisive"). The scooter 38.1 % is labelled a "partial, mixed-basis GHG indicator" with its gas-basis families listed. The results table has a gas-basis column. §1 rewritten per the suggested replacement. |
| 3 | **ACCEPTED** | Render regex fixed for adjacent markers. `check_docs.py` now fails on any empty marked block and on fewer than 8 table rows. The introduction's run identity is rendered (manifest block). The inputs id covers only result-determining inputs (`components/lca_engine`, `data`, `eval/eval.py`). |
| 4 | **ACCEPTED** | `check_scenario` rejects an EOL stage on any product whose records carry `eol_included` (test reproduces the reviewer's case). §5 now distinguishes current embedded treatment from planned models; CFF is conditional. |
| 5 | **ACCEPTED** | Boundary rows are classed: in scope / embedded / assumed absent (tested) / outside current scope. The explicit sentence "current cases do not yet demonstrate compliance with this budget" is added. Battery-replacement sensitivities were added (sedan +9.5 g/km, scooter +1.6 g/km). The 1 %/5 % rule is labelled our proposed policy, not ISO. |
| 6 | **ACCEPTED** | Added a common CO2-only panel (average / operating margin / build margin) for both cases. The build margin is labelled CO2-only. The commercial-loss convention is stated, with a transmission-only sensitivity added (lower bound on physical losses). A snapshot-grid caveat is in §1 and §10. |
| 7 | **ACCEPTED** | Central, interval and P(lower) are defined together. "Always lower" is removed. The CNG central-vs-median skew is explained; the two-piece lognormal is named as an assumption; the blank pedigree rationales are acknowledged with review scheduled. "Highest-value dataset" became "screening priority". |
| 8 | **ACCEPTED** | The deployment bound is removed from all documents and the renderer. Rendered wording: "accepted 0 of N synthetic digit-perturbed regression cases … does not estimate or bound the deployment false-accept rate". |
| 9 | **ACCEPTED** | Roadmap v1.1 adds roles R1/R2/R3 with hour estimates, a two-person base plan and a critical path. Commitments are split into committed vs conditional/stretch (300 records, CFF and AR6 elementary flows moved to conditional). The D fallback rests on already-opened evidence (Green Steel Taxonomy bands). Vivas 27–28 Nov are respected (app from 29 Nov), feature freeze is 10 Dec, and dates and stage references are made consistent (ADR: D gate 7 Oct, ADR revisit 12 Oct). |
| 10 | **ACCEPTED** | Pre-declared targets: complete-record recall ≥ 0.6 at precision ≥ 0.9 on unseen publishers, document-macro reporting, failures counted, adjudicated gold labels, a timing protocol, and baselines. The landscape's universal absence claim is replaced by a bounded search result. |
| 11 | **ACCEPTED** | The synthetic-data statement is rendered: no synthetic inventory or vehicle records; N synthetic regression negatives; Monte Carlo draws are simulations. |
| 12 | **ACCEPTED** | Duty cycle and payload stated; the 2W charging-loss inclusion marked as an assumption; physical-causality wording corrected; ISO public-comparison review worded as "panel of interested parties (our understanding)"; intended use stated. |
| 13 | **ACCEPTED** | Now called "heterogeneous published estimates". Row-vs-study counts are separated. The TERI row-selection status is recorded honestly (no rule was recorded at transcription; to be documented). No causal inference. |
| 14 | **ACCEPTED** | Licence status set on every source; duplicate CEA registry entry merged (19 sources = 19 unique URLs); `requirements.txt` incl. SciPy; CI labelled planned (local tests today). |
| — | **ACCEPTED** | A superseding status note was added to the hostile-review record (AR5 now used for the grid adders). |
| Presentation | **ACCEPTED in part** | Added a "Summary for the jury" and expanded jargon on first use where touched. A deeper trim is deferred until the portal's format and length limits are known. |

Accepted 15 (one in part), rejected 0.
