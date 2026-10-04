# NullahNet: hostile-judge review of the Round-1 package

**Reviewer:** GPT-6 Astra, independent cross-model reviewer under PLAYBOOK section 10. Advisory: the lead accepts or rejects each finding.

**Reviewed:** 2026-10-04, 16:47 IST. Snapshot: `d6ce52dd88b3b926f8d1fa30edfc70e8f353e7ec`, after fetching and rebasing onto `origin/main`. Paths below are relative to `innovatex-t3-coastal-plastic/` unless stated otherwise.

**Scope:** All requested Markdown documents, the PDF's 14 pages as extracted text, a rendered visual check of slide 7 and the escape-split figure, the committed analysis JSON, and the two requested T1 comparison documents. I also opened the official brief, the sensing research, and the interceptor implementation where a claim needed tracing. I independently recomputed the six paired policy/hardware comparisons from committed draws and checked BOM arithmetic and scripted timings. I did not rerun training or the full twin, test hardware, or observe a rehearsal.

**Pending work:** No penalty for the trained detector or boom-angle results not having landed in this snapshot. Their required framing is below. Mid-training validation performance is not reviewed test evidence.

## Verdict

**NOT READY to present unchanged; agree with staying on T1.** This is a substantial, unusually transparent research package, not an empty idea. The explicit SIMULATED/SENSITIVITY labels, admission of a small fixed-schedule gain, historical forecast-bug disclosure, and low-prevalence fraud precision are strengths. Nevertheless, the main slides and memorisable speaking lines repeatedly outrun those caveats. Most seriously, an untested release mechanism is sold as a guarantee against upstream flooding.

There are **16 issues: 1 BLOCKER, 11 MAJOR, 4 MINOR**. BLOCKER means remove or substantiate before presenting; MAJOR means a material credibility, feasibility, or judging weakness; MINOR means a narrower correction. Round 1 does **not** require completed field hardware. Several issues can be resolved honestly by narrowing the claim and making the unproved design explicit, rather than rushing a physical build.

**Fix first:** remove the flood/retention guarantees; resolve what actually measures pocket fill when the camera fails; rewrite the inference and comparator claims so the simulation remains a hypothesis-generation tool, not an account of observed Mumbai performance.

## Scores against the official judging criteria

These are judgments of this Round-1 package, not probabilities of qualifying. The official criteria are in the repo-root `_briefs/innovatex.txt:251-278`.

| Criterion | Score / 5 | Evidence |
|---|---:|---|
| Creativity and novelty | 2 | Integration could be useful, but slide 6 concedes tidal-trap prior art, slide 4 already lists verified-kilogram incumbents, and the distinctive retrofit has no demonstrated advantage yet. |
| Functionality and usability under real conditions | 2 | Software and reproducible simulations exist; actual film retention, jammed release, tide-compensated fill sensing, and corrosion performance remain untested. |
| Cost and market value | 2 | Priced node parts are useful evidence, but slide 9 omits installed retrofit/service cost and turns a six-waterway contract into a per-site O&M claim. |
| Technical implementation and feasibility | 3 | The causal 24-hour forecast design and tow-tank plan are credible starting points; sensing roles, electrical compatibility, and quantitative acceptance criteria remain unresolved. |
| Regional scalability | 2 | Q&A 18 calls gated/open adaptation configuration, although the twin and Q&A 20 explicitly exclude flap-gated outfalls. |
| Environmental and socioeconomic impact | 2 | The -5.6% is conditional simulated escape, not verified additional dry flexible-plastic diversion; downstream handling and worker economics are not quantified. |
| Design and ergonomics | 2 | The deck explains layers but never shows a physical retrofit/clearance drawing; the operator dashboard is relegated to backup. |
| Mumbai-specific understanding, bonus | 4 | Strong detail on BMC contracts, tides, the 2026 flood plan, incumbent deployments and low-value packaging; asset selection and current-versus-historical network facts need repair. |

## Numbered findings

### 1. BLOCKER - The pitch promises impossible-to-support flood safety and retention

**Location:** `deliverables/zonal-deck.md`, slide 6 hardware row and slide 8 speaker notes; `deliverables/qa-prep.md:26-29`; `deliverables/zonal-pitch.md:14`.

**Wrong:** "Never raises upstream flood levels", "never the reason a street floods", and the categorical answer that stored catch stays are guarantees, not design intentions. A head-triggered mechanism requires head to develop, may open late or foul, and must coexist with an obstructing pocket. In `components/twin_sim/interceptor.py:47-54`, keeping the catch is an input switch, not a prediction of mechanical survival. A small simulated change in escaped mass proves no hydraulic safety.

**Fix:** Say "PLANNED release intended to limit additional head rise within a tested flow/blockage envelope; retention during release is unproved." Show the pocket, anchors, bypass path and jam/failure states. Specify opening delay, opening head, residual obstruction and reset tests. Replace Q&A 7's "No" with the limits to be measured. Keep the existing prohibition on saying "can't flood" consistent with the actual script.

### 2. MAJOR - Correct paired numbers are being given stronger epistemic meaning

**Location:** `deliverables/zonal-deck.md`, slides 7 and 12; `deliverables/qa-prep.md:12,18`; `deliverables/presenter-card.md:31`; `research/components/twin.md`, sections 1, 3 and 5-6.

**Wrong:** The paired calculations are correct. But these are p05-p95 **scenario quantiles**, not a confidence interval for Mumbai effectiveness. "39 of 40 simulated seasons" actually means 40 parameter draws, each aggregating the same two weather seasons. "Believe/trust the ranking" ignores structural uncertainty. "Every assumed parameter" varies is also too strong: site geometry, crew rules and some assumptions are fixed. The 0.08 m tide number is an in-sample fit residual against another model, fitted through September 2025, not gauge-validated forecast accuracy; only policy tuning has the stated earlier-year boundary.

**Fix:** Use "better in 39/40 sampled parameter settings under this model; central 90% scenario range." Say the ranking guides experiments, not that it is trustworthy in the field. Label tide provenance and its fitting window explicitly. Do not imply all calibration was frozen before 2024. The earlier forecast correction is disclosed; I found no basis to allege that the old 48-hour bug persists.

### 3. MAJOR - The headline comparison does not isolate the value of tide timing

**Location:** `deliverables/zonal-deck.md`, slide 7 and its "sensors alone" line; `deliverables/qa-prep.md:18`; `research/components/twin.md`, section 2 and the reading after section 4.

**Wrong:** P1 ranks by fill fraction; P2 changes the ranking to mass at risk, adds forecasts, and changes shift timing. The research itself explains that P1 favours small full booms over larger masses. Thus -5.6% is not an isolated tide benefit, and "sensors alone don't help" does not follow. P0 is an assumed area-weighted roster, not an observed BMC schedule. Its clearance-access assumptions also need justification for the conveyor-equipped assets described in F12.

**Fix:** Call the policies what they are: "fraction-ranked fixed-shift heuristic", "assumed fixed roster", and "mass/risk-ranked flexible-shift policy". Add a mass-ranked sensor-only comparator and a timing-only ablation before attributing a gain to tides. Meanwhile narrow the claim to the complete P2-versus-P1 policy comparison and retain the small, uncertain P2-versus-P0 result.

### 4. MAJOR - The escape decomposition does not establish the claimed physical cause

**Location:** `deliverables/zonal-deck.md`, slide 5; `deliverables/presenter-card.md:12`; `research/components/twin.md`, sections 6-7; `components/twin_sim/interceptor.py:13-16,41-44`.

**Wrong:** "Booms fail by being too square to the flow, not by filling up" is not demonstrated by the 92.5%. The code labels every non-captured, non-bypass arrival entrainment, including the assumed still-water loss floor. Capacity and bulk density set the competing overflow term. The cited 0.35 m/s is explicitly an oil-boom analogy in F14, not a validated flexible-film threshold for BMC's steel nets. My small PDF fetch did not independently verify its wording.

**Fix:** Say "assumed capture losses dominate this twin; angle and retention are candidate experiments." Name the P2 scenario behind 92.5%, show floor versus velocity-dependent loss when available, and keep the oil-to-litter transfer as an assumption. Do not let an angle sensitivity become independent confirmation of a mechanism built into the capture equation.

### 5. MAJOR - The primary measurement changes between the pitch and its engineering basis

**Location:** `deliverables/zonal-deck.md`, slides 6 and 8; `deliverables/qa-prep.md`, Q10-Q11; `research/components/sensing-edge-bom.md:38-43`; `deliverables/prototype-plan.md:24-25,41,58`.

**Wrong:** The pitch relies on ultrasonic fill when the camera cannot see. The sensing research instead recommends one ultrasonic over **open water for stage**, with **camera-derived mat area for fill**. A single downward range is not, by itself, pocket-volume occupancy: tide, mat thickness, patchy coverage and water surface can change that reading differently. This is the measurement used both to dispatch crews and to challenge claimed mass.

**Fix:** Draw and freeze the sensing geometry: water reference, debris/area observation, pocket geometry and calibration. Test empty/partly covered/thick-mat cases at different water levels. If fill is unobservable during camera failure, output "unknown/degraded" and a safe manual/fixed-roster fallback, not a confident ultrasonic fill. Reconcile the sensing research, BOM and Q&A before claiming the primary measurement is solved.

### 6. MAJOR - The proposed pilot is not yet a specified, supported deployment

**Location:** `deliverables/zonal-deck.md`, slides 5, 10 and 12; `deliverables/qa-prep.md:68,74`; `deliverables/prototype-plan.md:107-114`; `research/components/twin.md`, section 1 and site table.

**Wrong:** Four modelled river/creek locations do not establish suitability for the long tail of small BMC outfalls. Trombay's anchor is explicitly a bus-station geocode in the research, not a surveyed outfall. Q&A 18 treats gated/open sites as configuration while Q&A 20 admits gates are unmodelled. The ask nevertheless includes a gated site. "No new civil works" is not established for an angled boom, bank pocket and changed anchors. Q&A 2 also promises real-outfall calibration in Round 2 while the prototype plan makes field work permission-dependent and subsequent.

**Fix:** Specify one candidate existing, open-tidal BMC asset first, clearly unsurveyed/uncontacted: owner, width, bank access, conveyor interface, gate status and intended operator. Defer gated deployment explicitly. Make the December commitment the closed-loop rig; field calibration is conditional on permission, safe retrieval and a site survey. Scale means repeated local engineering and operating agreements, not just configuration.

### 7. MAJOR - The incumbent gap is asserted more strongly than it has been researched

**Location:** `deliverables/zonal-deck.md`, slide 4, especially its gap paragraph and speaker notes; `deliverables/qa-prep.md`, Q1 and Q16.

**Wrong:** "The booms have no sensors" and "what nobody has" are unsupported absence claims. The same slide credits Plastic Fischer with third-party kilogram tracking. The opened F12 article also describes a Plastic Fischer boom at Usha Nagar, Bhandup: incumbent work is not exhausted by two creek-mouth Interceptors. The Mithi investigation is relevant institutional context, not evidence of defects in every boom contractor's payment workflow.

**Fix:** Present the gap as an operator-discovery hypothesis: "We propose to test whether instrumented BMC retrofits and tide-aware dispatch improve an existing workflow." Identify the exact missing capability and compare it with the incumbent workflow. Remove universal negatives and any inference that the other outfalls are uncontested. Retain the careful allegation wording.

### 8. MAJOR - Correct parts arithmetic is not an installed cost or validated payback case

**Location:** `deliverables/zonal-deck.md`, slide 9; `deliverables/qa-prep.md:54`; `research/fact-check.md`, D02-D04; `deliverables/prototype-plan.md`, sections 4 and 10.

**Wrong:** I verified INR 83,481.98 for the listed node plus enclosure and INR 38,927.11 for the listed flume parts. But the node total excludes the actual field retrofit, anchoring, installation, several fittings, commissioning, servicing, connectivity and waste handling. F13 covers six **rivers/nullahs**, not six established single-boom sites. D02 admits the one-boom-per-site assumption; slide 9 and Q&A drop it. A fraction of incumbent capital cost is not evidence that the intervention pays for itself.

**Fix:** Label rounded figures "listed parts only", keep exclusions visible, and budget installed retrofit plus recurring operation separately. Quote the INR 14.5 crore network contract without a per-boom division until its asset schedule is obtained. Estimate incremental cost per additional verified dry-plastic kilogram using a stated baseline, including review and disposal costs. A named department and existing budget are prospective demand, not a customer commitment.

### 9. MAJOR - F23 and slide 10 misquote what takes more than half the BMC budget

**Location:** `research/fact-check.md`, F23; `deliverables/zonal-deck.md`, slide 10, first bullet.

**Wrong:** The opened OpenCity article says the **general budget, which includes roads and storm-water drains**, takes more than half the allocation. It does not say roads and storm-water drains alone do. The INR 80,952.56 crore total matches; the scope does not. This is a concrete example of numeric source binding passing while the claim is wrong.

**Fix:** Restore the source's exact category or remove the half-budget claim. Do not present the citywide budget, or the proposed INR 13,000 crore flood programme, as money available for this product. Use the much more relevant, correctly scoped boom O&M contract.

### 10. MAJOR - The MRV headline conflates fraud classes and suppresses key operating assumptions

**Location:** `deliverables/zonal-deck.md`, slide 8; `deliverables/qa-prep.md:46`; `eval/RESULTS.md:195-254`.

**Wrong:** "Inflated claims caught 71.6%" is the aggregate across 3,000 inflated, 1,000 phantom and 1,000 wetted synthetic cases. Inflation-only recall is 69.4%; small-inflation recall is 24.4%. The 100% tamper result requires the tested attack set and a trusted external anchor; chain-only detection misses tail truncation. More importantly, the committed density sensitivity raises honest false flags from 4.7% to 17.8% when true density is 25% higher. That matters for mixed wet nullah debris.

**Fix:** Say "71.6% across our specified synthetic fraud mixture" and scope the tamper result to the anchored test suite. Surface the density sensitivity alongside the good low-prevalence precision disclosure. Explain who controls sensor keys, the weighbridge evidence and the independent anchor, and who pays for review. Keep "review, not penalty"; do not rename internally consistent inputs "verified plastic kilograms".

### 11. MAJOR - The impact claim lacks a stable, source-specific measurement boundary

**Location:** `architecture/adr/001-spike.md`, first-principles FWCE definition; `components/twin_sim/results/analysis.json:32-35`; `deliverables/qa-prep.md`, Q11, Q15 and Q17; `deliverables/prototype-plan.md`, section 8.

**Wrong:** The source is flexible packaging, but the cited beach share is all plastic and the twin models generic floating debris. The ADR defines FWCE against arriving mass; the analysis uses catchment load because arrivals include re-exposure. These are not interchangeable denominators. Stored material at September's end is not yet verified final diversion. Q&A 15 candidly says dirty film has no material buyer but does not identify a funded drying, sorting, transport and final-treatment chain.

**Fix:** Define the boundary once: unique incoming source-specific dry plastic, material cleared, material still stored, and escape, with re-arrivals excluded from unique input. Separate temporary retention from documented final diversion. Specify sort sampling and moisture correction, a matched baseline, handling costs and worker protections. Report intended impact metrics without inventing tonnes. Any field tracers need containment/recovery and permission; do not solve a pollution problem by releasing unrecoverable plastic.

### 12. MAJOR - The hardware plan needs an executable acceptance specification, not just priced items

**Location:** `deliverables/prototype-plan.md:12-29,43-45,57-75`; `deliverables/zonal-deck.md`, slide 9; `research/components/sensing-edge-bom.md`, section 1.

**Wrong:** T3 needs two level readings but BOM 4B prices one range transducer. The head cap is unspecified; T4 has no required fill-error/availability threshold. T2's "greater than run-to-run s.d." is not a clear paired design comparison with an agreed minimum useful gain. The field BOM itself flags a 5 V/3 A supply below its stated Pi supply rating and unverified LiFePO4-controller support. July climatology is verified, but the 8 W operating load is assumed. None of this proves failure; it prevents calling the design already sized and complete.

**Fix:** Before procurement, reconcile sensor counts, power compatibility and excluded construction parts. Freeze a randomized/paired rig protocol, useful-effect threshold, head/response envelope, and measurement uncertainty. Calibrate towing speed and allow for acceleration, reversal and settling in the short tank. Measure actual runtime power and outage recovery. Present these as acceptance gates, not completed robustness.

### 13. MINOR - Historical network facts are being spoken as today's inventory

**Location:** `deliverables/zonal-deck.md`, slides 2 and 4; `deliverables/presenter-card.md:22`; `deliverables/qa-prep.md:9`; `research/fact-check.md`, F06, F12 and F24.

**Wrong:** F12 is dated May 2025 in the fact table, yet the card says "9 today, 23 planned" in October 2026. The opened article describes a staged expansion, not the present inventory. The old BRIMSTOWAD summary's 25 mm/h and the 2026 flood-plan article's approximately 50 mm/h are also different historical/asset scopes, not one current universal drainage standard.

**Fix:** Say "a 2025 report described nine existing units and expansion to 23; current completion UNVERIFIED." Distinguish legacy drainage design, upgraded capacity and proposed future capacity. Retain 186 outfalls as a cited historical network figure, not a verified present addressable asset count.

### 14. MINOR - "Fined 44,448 establishments" overstates the source wording

**Location:** `deliverables/zonal-deck.md`, slide 3; `research/fact-check.md`, F10.

**Wrong:** The opened article says penalties were collected "by acting against 44,448 establishments"; it does not establish that each was fined. It separately gives INR 41.7 lakh total penalties and INR 5,000 for a first offence, making the stronger fine-count interpretation particularly unsafe.

**Fix:** Preserve "action against" and the independently reported seizure figure, or omit the establishment count. Mark the number actually fined UNVERIFIED. This does not invalidate the broader point that banned plastic remains in circulation.

### 15. MINOR - The time budget fits on paper, but the solution arrives too late and too densely

**Location:** `deliverables/zonal-deck.md`, slides 2-10 and timing notes; `deliverables/presenter-card.md`, run of show.

**Wrong:** The ten allocations add to 555 seconds, so I do not claim a demonstrated overrun. However, the explicit product architecture only arrives at 4:40. Slide 8 has three separate evidence stories in 60 seconds; slide 10 combines markets, policy, pilot and roadmap in 35 seconds. There is no physical mechanism drawing, and the working dashboard is only backup. The visual spot-check found no clipping on slide 7; the problem is explanation load, not a broken render.

**Fix:** Move secondary problem statistics to backup, show the retrofit and operator action within the first two minutes, and separate the physical what-if from software tests. Buy a short worked clearance example with the time saved. Rehearse with actual slide changes; do not assume the spare 45 seconds also buys an unscheduled dashboard tour.

### 16. MINOR - The selection conclusion is sound, but some supporting comparisons are not

**Location:** `thought_node.md:91-111`; comparison: repo-root `innovatex-t1-groundwater/thought_node.md:77-85` and its deck, "Cost, prospective customer, adaptation".

**Wrong:** "Modest measured gains" should be simulated gains. T1 does name a prospective customer and public programme; neither project demonstrates buyer commitment. The roughly sevenfold node comparison excludes T1's rain gauge/shared gateway and T3's retrofit/service burden, so it is not a pilot-cost comparison. The 3.0 and 3.4 means are selection-memo scores, not official-rubric totals or qualification probabilities. A successful two-hour retention test would improve evidence, not automatically make a known trap concept highly novel.

**Fix:** Keep the against-switching conclusion, but compare equally scoped pilot commitments and separate evidence maturity from novelty. Treat a tabletop test as a risk-reduction gate, not a sufficient reversal of the selection decision.

## Source spot-check receipts

I opened **11 distinct URLs from the fact-check table**, always with fetch `max_length` at most 2,800 characters; paginated where needed. F01 and F02 share one URL and are not counted twice. Matching an article validates attribution, not the underlying survey, operating performance or official approval. Unopened facts, supplier availability and firsthand municipal conditions remain **UNVERIFIED by this reviewer**.

| Rows and opened URL | Quote/number check | Result |
|---|---|---|
| F01-F02: [The Ocean Cleanup, enters India](https://theoceancleanup.com/press/press-releases/the-ocean-cleanup-enters-india/) | The press release contains the estimated 5 million kg/year, 220 km, 152 km2, and expected 61-92 tonnes/year for initial Trombay/Malad systems. | **MATCH.** Estimate and expectation, not measured diversion; the derived approximately 1.2-1.8% is arithmetic, not a comparison of field effectiveness. |
| F12: [HT, 14 more trash booms](https://www.hindustantimes.com/cities/mumbai-news/bmc-to-install-14-more-trash-booms-to-stop-garbage-from-flowing-into-arabian-sea-thane-creek-101746212815731.html) | Nine existing, expansion to 23, approximately INR 1 crore each, 1.5 tonnes/day dry and 2.5-3 monsoon, two-foot net and daily conveyor clearance all appear. | **MATCH to report.** Present inventory not established. The article also names the Usha Nagar Plastic Fischer installation. |
| F13: [FPJ, maintenance contract](https://www.freepressjournal.in/mumbai/mumbai-bmc-approves-145-crore-contract-to-maintain-trash-boom-systems-across-6-rivers-and-nullahs) | INR 14.5 crore, two years, six rivers/nullahs, July 2022 commissioning and 1.3% below estimate appear. | **MATCH.** No verified one-boom-per-waterway denominator: D02 is conditional arithmetic, not an observed unit cost. |
| F24: [Mumbai Live, flood plan](https://www.mumbailive.com/en/civic/flood-gates-to-be-installed-at-33-locations-in-mumbai-93716) | INR 13,000 crore; October 2026-2029 schedule; 33 additional locations; 8-10-foot protective screens; approximately 50 to 100-120 mm/h; seven pilot sensor locations appear. | **MATCH.** Proposed works/in-principle approval, not completed procurement for NullahNet. Screens keep garbage out of drains; retrofit compatibility is not established. |
| F06: [BRIMSTOWAD summary](https://en.wikipedia.org/wiki/Brihanmumbai_Storm_Water_Disposal_System) | 186 outfalls and approximately 25 mm/h at low tide appear. | **MATCH to secondary historical description.** Not independent verification of current drainage capacity. |
| F15: [NASA POWER query](https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=ALLSKY_SFC_SW_DWN&community=RE&longitude=72.85&latitude=19.07&format=JSON) | JSON gives July 3.7920 and May 7.0942 kWh/m2/day, using the 2001-2020 climatological period. | **MATCH.** Does not measure node demand or prove dark-spell autonomy. |
| F23: [OpenCity budget analysis](https://opencity.in/analysing-the-bmc-budget-for-2026-27/) | INR 80,952.56 crore and 8.7% match. The half-budget wording refers to the general budget, which includes roads/drains. | **PARTIAL MATCH; scope error in the fact row and deck.** Finding 9. |
| F10: [Mumbai Live, plastic enforcement](https://www.mumbailive.com/en/civic/bmc-resumes-crackdown-on-single-use-plastic-recovers-inr-1.45-lakh-in-fines-87417) | 44,448 establishments, INR 41.7 lakh and 2,148 kg appear, with "acting against" rather than a count of establishments individually fined. | **PARTIAL MATCH; stronger deck wording unsupported.** Finding 14. |
| F14: [ITOPF TIP 3 PDF](https://www.itopf.org/fileadmin/uploads/itopf/data/Documents/TIPS_TAPS_new/TIP_3_Use_of_Booms_in_Oil_Pollution_Response.pdf) | Fetch returned PDF bytes, not readable text. | **UNVERIFIED** quote/threshold in this spot-check. No claim that the citation is false. |
| F16: [Pinwheel, Plastic Fischer](https://www.pinwheel.earth/projects/plastic-recovery-and-recycling-india-and-indonesia) | Readable excerpts describe manual retrieval, drying/sorting, recycling and cement-plant routing. The fetched text did not expose the claimed 3.2 million/71/98/eight totals or the named tracking software. | **UNVERIFIED** numerical totals and exact software claim in this spot-check; not a finding of contradiction. |
| F20: [Interceptor Original](https://theoceancleanup.com/rivers/interceptor-original/) | The simplified response exposed only the cookie notice; a continuation exposed no further content. | **UNVERIFIED** sensor/text-message quote in this spot-check. |

Additional check: I opened the [Open-Meteo Previous Runs documentation](https://open-meteo.com/en/docs/previous-runs-api). It defines `_previous_day1` as the value predicted 24 hours before valid time. That supports using only the next 24 hours at the decision boundary; it is a fixed-lead-time series, not one complete forecast issuance. The research's statement that these semantics were not checked can now be updated. It does not validate the twin's plastic-process assumptions.

## Statistical and reproducibility checks that passed

- From all 40 draws in the committed per-policy arrays, recomputing `(a-b)/b`, the median, p05/p95 and count below zero exactly reproduces the stored rounded results: P2/P1 `-0.0557 [-0.1575, -0.0033], 39/40`; P2/P0 `-0.0214 [-0.1251, +0.0149], 28/40`; P1/P0 `+0.0314 [+0.0001, +0.0602], 2/40`.
- The same computation reproduces the fuse and two pocket sensitivities: medians `-0.0009`, `-0.0503`, `-0.0941`, with their stored quantiles and sign counts. These are paired changes, not ratios of marginal median totals. Do not "correct" them into the latter.
- P2 escape-share medians sum to 99.12%, not 100%. Marginal medians need not sum to one: this is not a mass-balance failure. State this if showing a composition graphic rather than silently normalising it into a different statistic.
- BOM line multiplication and sums match the quoted listed-parts totals. The critique is completeness and the economic denominator, not arithmetic.
- The scripted 9:15 total and the 10-main-plus-four-backup PDF count match. Rehearsed timing is **UNVERIFIED**.
- The mass-balance and equal-crew-hour checks are recorded as passing in committed analysis. I did not rerun the simulator and do not present those as new independent executions.

## Questions the present Q&A does not adequately answer

| Likely judge question | Minimum credible answer to prepare |
|---|---|
| "Show an empty pocket at high tide and a full pocket at low tide. What does your one range sensor see?" | A labelled sensing geometry, a calibration example and an explicit unknown/degraded state; not "the camera is only support". |
| "Why does this beat a cheap kg-ranked roster or an extra clearance visit?" | A correctly scoped comparator and incremental labour/equipment cost; currently not established. |
| "Whose keys, scales and records prevent a contractor supplying consistent but false evidence or counting the same waste twice?" | Independent custody/anchoring, audit sampling, batch identity and dispute handling; hashes alone are not the answer. |
| "Who takes the wet film, who pays to prepare and transport it, and what proves final disposal?" | A proposed funded chain with named types of responsible operator and receiving evidence; no guaranteed EPR revenue. |
| "Where exactly does a longer diagonal boom and a bank pocket fit without obstructing access or the conveyor?" | A dimensioned candidate-site retrofit drawing, stated land/anchor permissions and deployment exclusions. |
| "What happens when power, communications or a sensor fail during a storm?" | A local safety mechanism independent of cloud inference, buffered records, health/unknown flags and a conservative operating fallback, with planned acceptance tests. |

## How to frame the two pending results

**Trained detector:** Replace the zero-shot line only with the committed held-out test result for frozen weights and the documented grouped split. Keep dataset/domain, image count, mAP50, mAP50-95 and operating-threshold precision/recall available; do not turn validation mAP near 0.9 into a test claim. TUD-GV litter detection is not Mumbai flexible-film detection, pocket-fill estimation, mass estimation, or monsoon reliability. A higher mAP does not resolve finding 5. Retain zero-shot as a reference, and do not claim Pi/Hailo throughput or power from a Mac evaluation.

**Boom angle:** A new row is useful as **SENSITIVITY**, not proof or another validated "held-out result". The model reduces normal velocity by construction. State each comparison's same-hardware denominator, retain paired draws, and do not add its percentage to a dispatch/pocket percentage. The documented length multiplier is about 2.9 at 20 degrees, while capacity/cost/mooring effects are held fixed or omitted. Put that caveat with the row. Floor/velocity decomposition and exposure help interrogate the hypothesis; they do not calibrate the model or establish safe hydraulics.

## Selection-memo judgment

**Agree: do not switch from T1 for Delhi.** T1's opened deck has a tighter decision product, a worked offline demo, an explicit missing-input deferral and a simpler proposed blind rig. It remains largely simulation-backed, so this is not a claim that T1 has proven field impact. T3 has an excellent Mumbai research advantage but asks the audience to accept more unresolved physical and institutional links: interception geometry, flood safety, primary fill observability, wet-to-dry mass evidence and contractor adoption.

The decision should rest on those execution and evidence gaps, not a supposedly scientific 3.0-versus-3.4 ranking, the citywide budget, or an unscoped node-price ratio. A good reversal video would strengthen T3 as an alternative, but would not alone settle hydraulic safety, sensor observability or differentiation from known tidal traps.
