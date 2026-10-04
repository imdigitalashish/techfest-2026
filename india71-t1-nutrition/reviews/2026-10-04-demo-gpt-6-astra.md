⚠️ DEGRADED: single-context review; the assignment expressly prohibits sub-agents.

# Poshan Setu: hostile-but-fair finals demo review

**Reviewer:** gpt-6-astra, jury-watching-the-demo assignment.

**Inspection completed:** 2026-10-04 19:42 IST.

**Reviewed checkout:** `74e8dcec0ba1578503ae99aa7e5ab6725b6fefad`.

**Committed demo payload:** generated `2026-10-04 18:59 IST`, producer Git head `8864dc3`, as recorded in `demo/data/demo_data.js`.

**Scope:** Theme 1, official brief `_briefs/india71.txt`, PLAYBOOK sections 10/11, the seven-screen demonstration and its supporting implementation/evidence. Paths below are relative to `india71-t1-nutrition/` unless stated otherwise. Findings refer to this snapshot, not to subsequent main-branch fixes.

## Verdict

**Would I lean in within three minutes? Yes. Would I sign off this version for finals as narrated and projected? No.**

The real-data opening earns attention; the no-ID/noisy-record comparison and the chain-versus-checkpoint attack are memorable, concrete demonstrations. This is substantially better than a dashboard of aspirations. It also volunteers unusually important negative results: most episodes remain missed, linkage has not improved prediction, severe wasting was not calibrated, and a chain alone cannot detect truncation.

However, the narration claims a privacy boundary the implementation does not demonstrate. Six of seven screens exceed a 1280x720 viewport, with decision-relevant evidence below the fold. An infant-bypass promise is not implemented in the ranking path; undelivered capacity-overflow work acquires overdue/escalation history without the promised service-readiness gate; and the featured child's claimed onset is a later episode after earlier wasting/SAM. Those are precisely the seams a public-health/policy juror will press.

The strongest honest framing is: **a synthetic stress test of record matching, transparent prioritisation and accountable coordination behind existing systems, not a validated clinical predictor, a deployed privacy architecture, or a worker-performance system.** No source or implementation file was changed during this review.

## A. Execution, timings and coverage

| Check | Observed result |
|---|---|
| Environment | Created `.venv` with the requested `uv venv .venv --python 3.11`, then installed `requirements.txt` with `uv pip install --python .venv/bin/python -r requirements.txt`. CPython 3.11.14; environment creation 0.14 s; installation 0.73 s, 48 packages. These are local/cache-dependent timings, not a cold internet-install promise. |
| Memory/compute guard | `sysctl -n kern.memorystatus_level` returned **39**, above the required 30. Smoke ran CPU-only under `nice -n 10`, with numerical-library thread counts restricted. |
| `demo/smoke.sh` | **PASS**, elapsed **46.20 s**, user 20.72 s, system 2.62 s. Raw output is preserved in Appendix A. |
| Actual offline page | The smoke browser loaded the real `file://` page; first visual **0.18 s**, no page errors and no network requests. |
| `demo/run.sh` | Successful macOS launch/return in **1.88 s**. This measures the launcher returning, not an independently timed human-visible paint. |
| Interactive inspection | The supplied browser interface rejected `file://` with “Access to file protocol is blocked.” I therefore served the **unchanged** demo directory on loopback `127.0.0.1:8871`. Local-mirror FCP was 84 ms, DOM/load about 100.7/100.8 ms. This workaround does not replace the separate, successful real-file offline check. |
| Browser errors | No application exception observed. The HTTP mirror requested a nonexistent `/favicon.ico` once, yielding a 404. No third-party resources were requested. |
| Full exporter | **Not run**, as directed. Only the smoke test's `demo.export --check` executed. |
| Important skip | `--check` explicitly **skipped district CSV re-derivation** because `.data/raw/nfhs5` was absent. The check still validated committed district values/presets. This is not independent regeneration of the full district dataset. |
| Fallback | Existing 12 PNGs decode; the existing GIF decodes into 11 frames lasting 11.6 s. Visually inspected the noisy-linkage and truncation fallbacks. Did not regenerate or edit them. |
| Evidence | **20 PNG screenshots, 4,748,997 bytes total**, below 5,000,000 bytes, in `2026-10-04-demo-shots/`. |

Interactive coverage:

- All seven screens at **1440x900** and **1280x720**; arrow and numeric navigation; both district cohorts; all **36** state-picker options without a render error.
- All **35** linkage combinations: seven ID-coverage settings from 0% to 100%, five extra-error settings from 0% to 40%; all presets.
- Worklist K values, clamping at **1 and 10**, `+`, `-`, `r`, outcome reveal, and the featured plus **24** seeded AWC-month examples for each cohort; forward/reverse wrapping.
- Phone scrolling; all **six** request choices for each cohort; untouched, flip, reseal-one, reseal-all and delete-last-three ledger states for each cohort.
- Extra bounded arithmetic checks: **706 unique district rows**, all **2,824** indicator values finite and within 0..100; all **24** values tabulated in V5 match the payload; all **105** linkage precision/recall/F1 triples agree algebraically; all **50** example lists have consistent pool sizes, rank permutations and future-outcome tallies; both example bit counts/Dice and exported SMS character counts agree.

These checks establish rendering, internal consistency and the cited provenance chain. They do **not** independently regenerate every linkage cell or cohort, validate every original NFHS district PDF, demonstrate actual departmental integration, or validate results on real children. The script contains approximately **446 spoken words**, about **149 words/minute** before clicks; I did not perform a timed human spoken rehearsal.

## B. Screen-by-screen jury notes

| Screen | What I observed and how a juror will read it | Evidence |
|---|---|---|
| **1. India / REAL** | An effective opening: wasting **19.3% surveyed versus 5.46% reported**, lower PT wasting in **36/36** States/UTs. The different-year/age/denominator caveat is substantively correct. Stunting **35.5% versus 37.07%** is nationally close, but “stunting roughly agrees” must not become a claim of agreement across states. Both tile modes and all scatter indicators work. The tile grid is not pretending to be geographic boundaries; scatter axes are equal and start at zero. Eleven surveyed-wasting tiles have insufficient contrast for their small white labels. | [1440](2026-10-04-demo-shots/01-india-1440.png), [1280](2026-10-04-demo-shots/11-india-1280.png); V4 and `state_gap_verified.csv`. |
| **2. Districts / REAL** | The district swarm makes regional heterogeneity concrete. Nandurbar **30.7 / 13.5 / 45.8 / 57.2** and Amravati **26.2 / 10.7 / 29.0 / 38.0** are wasted/severely wasted/stunted/underweight percentages. **706 of 707**, with the conflicting Sahibganj record excluded, is disclosed. All states and both presets render. District indicator switches work; the common wasting colour domain is 0..32. This is the only screen that fits the measured 720px viewport without document overflow. | [1440](2026-10-04-demo-shots/02-districts-1440.png), [1280](2026-10-04-demo-shots/12-districts-1280.png); V5 and `demo/export.py:236-268`. |
| **3. Find every child / SYNTHETIC** | The clearest early lean-in moment. Default displayed F1 is **0.51 / 0.94 / 0.97** for IDs/plaintext/Bloom. At zero IDs and +40% errors, it is **0.00 / 0.70 / 0.89**, with **3,907 of 4,531** gold pairs recovered by Bloom matching. The 35 settings are actual exported runs, not interpolated measurements. At 100% coverage, IDs and pooled matching beat Bloom; that reversal is not hidden. But F1 masks a serious false-link trade-off, the departmental-boundary claim overreaches, and the fixed bit-pair does not change with the stress knobs. | [Default](2026-10-04-demo-shots/03-link-default-1440.png), [stress](2026-10-04-demo-shots/04-link-stress-1440.png), [projector](2026-10-04-demo-shots/13-link-stress-1280.png), [100% IDs](2026-10-04-demo-shots/20-link-100pct-1280.png). |
| **4. One child / SIMULATED** | The cross-registry timeline is well chosen for explaining coordination, and the severe-wasting calibration miss is honestly visible. The Nandurbar child has birth weight **2.18 kg**, one missed dose, and a selected lead of **3 months**. But the plotted history already includes wasting and recorded SAM before the marked “wasting begins”; this is a later episode, not first-ever onset. The “0.384 vs 0.384” no-prediction-gain statement is consistent with the committed results. Amravati switches correctly, but its repeated slot labels collide. | [Nandurbar 1440](2026-10-04-demo-shots/05-child-1440.png), [Nandurbar 1280](2026-10-04-demo-shots/14-child-1280.png), [Amravati 1280](2026-10-04-demo-shots/18-amravati-child-1280.png). |
| **5. This week / SIMULATED** | The matched-capacity baseline is valuable. Nandurbar K5 episode recall is **39.4% vs 36.3%**, not a spectacular clinical breakthrough; the uncertainty and missed episodes should remain visible. K1's difference CI includes zero. At K5 the featured reveal is **baseline 0 / ours 1**; at K8, where SCRIPT actually tells the presenter to reveal, it is **1 / 1**, and at K10 also **1 / 1**. The reference benchmark is monthly, despite weekly framing. Very young infants appear in the capped normal-status pool. At 720px, the comparison/outcome content requires scrolling. | [K5 reveal](2026-10-04-demo-shots/06-week-reveal-1440.png), [K10](2026-10-04-demo-shots/07-week-k10-1440.png), [1280](2026-10-04-demo-shots/15-week-1280.png); `SCRIPT.md:14`, `demo/js/week.js:62-94`. |
| **6. SMS / SIMULATED** | Scrolling works: this is not a frozen phone screenshot. Nandurbar has **20 tasks**: 4 SAM, 11 MAM, 5 prevention, capacity **10**. The shown SMS list holds 4 SAM plus 6 MAM; 5 MAM and all 5 prevention tasks overflow. The featured child is **task 18**, absent from this week's delivered list, then escalated after its deadline. “Nothing is dropped” means retained as a task, not delivered or completed. This is a useful disclosure, but a policy juror will see an unowned service-capacity deficit becoming apparent worker lateness. The screen also ignores the K/AWC-month chosen on the preceding screen. | [1440](2026-10-04-demo-shots/08-sms-1440.png), [1280](2026-10-04-demo-shots/16-sms-1280.png); `demo/js/week.js:102-132`, `demo/export.py:518-585`. |
| **7. Break it / SIMULATED** | A strong finale: deleting the tail or resealing the suffix leaves a valid chain but fails comparison with the retained checkpoint. Hash verification is genuinely executed in the browser. All six policy scenarios have the expected two allows/four denies, including explicit employment denial. However, picking a request replays an exported result; it does not run a new policy decision or append a new ledger entry. External custody of the checkpoint is modelled, not a demonstrated district-minutes integration. | [Truncate](2026-10-04-demo-shots/09-break-truncate-1440.png), [reseal all](2026-10-04-demo-shots/10-break-reseal-1440.png), [1280](2026-10-04-demo-shots/17-break-1280.png), [allowed request](2026-10-04-demo-shots/19-allowed-request-1280.png). |

### Projector measurements and design judgment

| Screen | Document height at 1280x720 |
|---|---:|
| India | 781px |
| Districts | 720px |
| Linkage | 840px |
| Child | 848px |
| Worklist | 942px |
| SMS | 752px |
| Break it | 843px |

The measured source-copy size is **11.26px** at 1280, versus **12.03px** at 1440; the corresponding main heading is about **26.71px / 28.54px**. No horizontal document overflow was observed. Small-source text is not merely decorative: it contains simulation, provenance and capability limitations.

For surveyed-wasting tiles, white-label contrast is below 4.5:1 in **11 states/UTs**: AS, BR, DH, GA, JK, JH, KA, MP, NL, TG and WB. The minimum is **2.86:1** on JK/MP, with background `rgb(227,127,53)`. These are small labels, not large-text exceptions. This is a contrast defect, not a criticism of the shared sequential colour scale.

The UI has a recognisable, topic-specific visual language rather than generic decorative cards: the district swarm, longitudinal child view, capacity lists and dual ledger verdicts all communicate real structure. Its weakness is trying to place the explanation, experiment, full evidence and caveats on the same projected slide. The remedy is hierarchy and progressive disclosure, not shrinking all text further.

A deterministic static design scan of `demo/index.html` returned exit 0 and `[]`. That file is largely a shell for JS-rendered screens; this result is **not** a clean bill of visual health and did not override the browser evidence.

## C. Numerical provenance and honesty audit

`demo/data/demo_data.js` stores the payload on **line 2**. The paths below identify its relevant subtrees without citing the entire very long line. Static axis ticks, K bounds, dates, protocol durations and navigation numbers are code-defined values, not claimed empirical findings.

| On-screen number family | Trace and result |
|---|---|
| State percentages, “36 of 36”, comparison scatter and source period | Payload `gap` -> `demo/export.py:209-234` -> `research/sources/state_gap_verified.csv` and V4. Smoke verifies every state row against the CSV. India wasting **19.3/5.46**, stunting **35.5/37.07**; Maharashtra wasting **25.6/4.01**, stunting **35.2/39.68**, underweight **36.1/14.8**. PT is lower for wasting and underweight in 36/36, stunting in 23/36. These comparisons do not establish under-detection or worker fault. The displayed ministerial remark traces to the secondary News18 attribution in `research/sources/R6-social-signal.md:37`, not an independently verified parliamentary transcript. |
| District dots, rankings, denominators, presets and four-indicator cards | Payload `districts` -> `demo/export.py:236-268` -> `eval/fetch_nfhs5.py`'s compiled-source pipeline, with V5's verification record. All **24** six-district values reported in V5 equal the exported values. This review checked that equality, not the original PDFs again. The **706** admitted rows and one exclusion are explicit; all 2,824 exported indicator values passed the bounded arithmetic/range check. Full district source re-derivation was skipped as noted above. |
| Linkage F1, precision, recall, true links, clerical shares and graph dots | Payload `linkage.cells` -> `demo/export.py:278-333` -> `components/identity_linkage/{synth_registries,link,eval_linkage}.py`. Default cell equals `eval/results/identity_linkage.json` and was recomputed by smoke. All 35 cells are committed, discrete results; lines join points and controls select exact cells. No interpolation passed off as computation was found. All 105 method triples have consistent F1 and true-link/recall arithmetic. |
| Linkage coverage/noise controls | Seven coverage and five noise settings are exporter/generator parameters, not measured Indian prevalence. The UI marks 35% as an assumption, correctly. However, the generator's coverage parameter is conditional on being in both registries, not the displayed denominator of all PT records: default IDs **1,565/4,776 = 32.77%**; at the nominal 100% setting **4,531/4,776 = 94.87%**. See N1. |
| Bit-grid counts, 1,000-bit size, Dice and 0.91 threshold | Payload `sim.<cohort>.story.child.link` -> `demo/export.py:405-503` -> linkage component. Nandurbar sets **792** PT bits, **799** health bits, **769** jointly; `2*769/(792+799)` rounds to **0.967**, above **0.91**. Both cohorts' exported bitsets reproduce their counts/Dice. This is the fixed story child, not a currently stress-mutated pair from the 5,000-child benchmark. |
| Calibrated cohort prevalence, size and linkage summaries | Payload `sim.<cohort>` -> `demo/export.py:686-729`, `demo/calibrate_district.py` and committed components. Both cohorts contain **8,597** simulated children, **8,169** paired health records. Nandurbar wasting/stunting **30.7/45.8**, Amravati **26.2/29.0**, are fitted by additive quantile shifts. Severe wasting is visibly **4.8 vs 13.5** and **3.7 vs 10.7**, respectively, and explicitly not fitted. Roughly **98.4% recall / 98.8% precision**, versus **34.1%** ID-only recovery, are simulated cohort-linkage summaries, not field performance. |
| Child dates, weights, missed doses, lead time, status and timeline | Payload `sim.<cohort>.story` -> `demo/export.py:405-503` and cohort component output. Nandurbar **PT-000097**, birth **10 July 2024**, birth weight **2.18 kg**, selected flag **22 March 2025**, selected episode **22 June 2025**, lead **3 months**. Amravati **PT-000062**, birth **13 May 2023**, **2.19 kg**, selected episode **10 May 2025**, lead **3 months**. Both have one shown missed dose. Story selection is an illustrative selected success, not an average individual treatment effect. The Nandurbar first-ever-onset wording is wrong; see M3. |
| K curves, bootstrap CIs, reference methods, example ranks and reveal counts | Payload `sim.<cohort>` worklist results/examples and `worklist_ref` -> `demo/export.py:177-207,335-390,505-515` -> `components/early_warning/eval_v1.py`, `model.py`, and `eval/results/early_warning_v1.json`. Capacity is **per AWC-month**; an incident episode is WLZ below -2 after two preceding non-wasted months, evaluated with 1-3 months' lead. Nandurbar has **13,797** episodes; K5 **.3940 vs .3629**, difference CI **[.0250,.0376]**. Amravati K5 **.3983 vs .3598**, CI **[.0309,.0458]**. Nandurbar K1 **.0880 vs .0863**, difference CI **[-.0030,.0059]**, includes zero. The reference has **10,690** episodes: WHZ **.4290**, programme **.3651**, random **.2688**, anthropometric logistic **.3838**, linked-health logistic **.3844**. Thus displayed **.384 vs .384** supports “no demonstrated predictive benefit from linkage,” not improved prediction. |
| SMS task counts, character lengths, capacity, deadlines and escalation | Payload `sim.<cohort>.sms` -> `demo/export.py:518-585` -> `components/action_router/router.py`, `protocol.yaml`, `components/frontline_worklist/render.py`. Fixed K5, capacity10 story: **20** tasks Nandurbar, **17** Amravati. Character counts equal string lengths and are <=80 in these samples. The committed reference `eval/results/pipeline_demo.json` supplies **1,685** tasks, **140** worklists and **482** escalations after eight days with **70% on-time completion assumed**. These are simulation results, not actual delivered services. |
| Request counts, pass rates, ledger size, attack verdicts and time | Payload policy scenarios and ledgers -> `demo/export.py:600-684`, `components/policy_gate`, `components/audit_ledger`, committed `policy_gate.json` **39/39** and `audit_ledger.json` **100/100**. Each cohort has **six** exported requests; two allowed, four denied. Browser `demo/js/ledger.js:126-170` really verifies SHA-256; `demo/js/break.js:51-54` measures its live runtime. The displayed hash-count label counts entries rather than actual operations; see N4. External checkpoint custody remains an assumption. |

**Additional honesty findings that should be preserved:**

- REAL, SYNTHETIC and SIMULATED are visibly distinguished; cohort headers say real district rates do not mean real children. No unlabelled real-child performance claim or fabricated metric was identified.
- No claim that linkage improves prediction was found. The demo explicitly says the opposite, consistent with ADR 003. The old retracted early-warning result is not used as the active benchmark.
- No worker-level score, worker ranking or named-worker leaderboard was displayed. ADR 002's prohibition is not itself violated by a displayed scalar. Operational role/AWC identifiers and overdue-task history can nevertheless become employment proxies; do not mistake “no score” for “no surveillance risk.”
- No deceptive truncated metric axis was found: F1 is 0..1, recall is shown against a 0..70% axis containing the values, and scatter comparisons share zero-based axes.
- For “stunting roughly agrees,” the national aggregate is the defensible reading. Across state rows, the median absolute difference is **7.43 percentage points**; only **15/36** differ by <=5 points. That should not be narrated as state-wide concordance.
- V5 explicitly corrects the older district-source claim of a CC-BY licence and a 12/12 R7b check. `eval/fetch_nfhs5.py:1-31` still contains that stale wording and uses unpinned upstream URLs. This is provenance/rebuild debt, not evidence that the displayed district percentages were invented.

### Ledger attack observations

Entry indices are the zero-based indices displayed by the implementation.

| Variant | Nandurbar: chain alone / with checkpoint | Amravati: chain alone / with checkpoint |
|---|---|---|
| Untouched | pass / pass, 28 entries | pass / pass, 25 entries |
| Change deny to allow | fail #25 / fail #25 | fail #22 / fail #22 |
| Reseal that entry only | fail #26 / fail #26 | fail #23 / fail #23 |
| Reseal every later entry | pass / fail #27 | pass / fail #24 |
| Delete last 3 entries | pass / fail #25, 25 retained | pass / fail #22, 22 retained |

## D. Ranked issues and concrete fixes

“Blocking” means **fix before using this claim/layout at finals**, not a claim of an observed production breach. “Major” means a material clinical, governance, comparison or demonstration-semantics problem. “Minor” means a bounded clarity/encoding defect.

### B1 - Blocking: encoded-only departmental privacy is asserted, not demonstrated

**Evidence:** `SCRIPT.md:12` says “no names were pooled” and “only these 1,000-bit strings left each department.” `demo/js/find.js:8,100-107` repeats the names-never-leave/only-bitstrings wording; see [stress screen](2026-10-04-demo-shots/04-link-stress-1440.png). But `components/identity_linkage/link.py:128-185,207-265` consumes both sides' raw records in the same linkage implementation, constructs encodings there and uses plaintext blocking information, including phonetic mother-name information, village/DOB and sex. The `link_from_frames` entry point constructs both plaintext record lists.

**Why it matters:** the run supports a matching-quality result for Bloom encodings. It does not establish an encoded-only interchange boundary or demonstrate that departmental names were unavailable to a common matcher. The two drawn departmental boxes cannot supply that missing property. This is an unsupported capability claim, **not evidence of actual data exfiltration**.

**Fix:** immediately narrow the copy to “synthetic benchmark of encoded matching; a proposed departmental encoding boundary is not implemented here.” If retaining the stronger claim, expose and test an encoded-record-only interface with department-side encoding and an explicitly reviewed blocking-data contract; demonstrate that the matcher cannot read both raw tables. Continue stating that Bloom filters are attackable and keyed encoding is not anonymisation.

### B2 - Blocking: the claimed projector layout hides the proof and its caveats

**Evidence:** six screen heights exceed 720px; the worklist reaches **942px**. Sources are **11.26px**, and 11 state-tile label contrasts fall below 4.5:1. See [linkage](2026-10-04-demo-shots/13-link-stress-1280.png), [worklist](2026-10-04-demo-shots/15-week-1280.png), [ledger](2026-10-04-demo-shots/17-break-1280.png), and the measurements above. `SCRIPT.md:3` claims projector scaling; `demo/index.html:16,76` defines the small text.

**Why it matters:** the audience cannot simultaneously read the comparison, its outcome and its limitation at the requested projector size. A caveat below the fold is weak protection against an overclaim made aloud.

**Fix:** add a genuine 1280x720 presentation layout: one primary comparison/verdict, concise always-visible scope/limitation, shorter lists, and secondary evidence behind a clearly available detail control. Increase important comparison/caveat type rather than globally scaling down. Choose tile text colour using measured contrast. Recheck every screen and extreme state, not just the opening.

### M1 - Major: under-six-month children are still in capped rankings

**Evidence:** `deliverables/round1-proposal.md:102-107` promises the infant bypass. `demo/export.py:177-207,518-539` and `components/early_warning/eval_v1.py:100-151` select observed-normal records without the corresponding age exclusion. In `sim.nandurbar.examples[0].children`, **PT-000245**, age **1.8 months**, AWC **P1S1A04**, **16 March 2025**, WHZ **-1.86**, is ours rank **5** and programme rank **6**. Amravati's corresponding example includes **PT-000246**, age **0.2 months**, WHZ **-1.99**, ours rank **1**, programme rank **2**.

Across the 25 exported examples per cohort, K5 selects **8** under-six-month rows in Nandurbar and **9** in Amravati. These are sampled child-month rows, not a cohort-wide rate or necessarily unique infants.

**Fix:** implement an explicit age/clinical eligibility split before both rankings and route young infants through the promised age-appropriate assessment pathway outside prevention-slot competition. Keep the frozen v1 benchmark clearly historical or regenerate a separately identified, coherently gated comparison; do not merely hide infant rows in the UI while retaining old curves.

### M2 - Major: capacity/resource failure can be presented as worker non-performance

**Evidence:** [SMS screen](2026-10-04-demo-shots/08-sms-1440.png) shows **20 tasks / capacity 10**, with the featured child at **task 18**. Five MAM and all five prevention tasks are outside the delivered list. Its due date is **29 March**, escalation checked **30 March**, then assigned to ASHA with **6 April** due. `components/action_router/router.py:43-121` creates deadlines and escalates open overdue tasks without a demonstrated readiness/acknowledged-delivery gate. `architecture/contracts/models.py:303-321` has open/done/escalated/closed, not a blocked-input clock state. `components/action_router/protocol.yaml:8` asserts a preceding readiness gate, but that gate is not called in this path. This falls short of ADR 002's support-before-scrutiny/service-readiness commitment.

**Why it matters:** a task can accrue lateness before it was ever on the worker's deliverable list. Passing it to another cadre is not proof that capacity or supplies appeared. A policy juror can reasonably read the history as surveillance even without a numeric worker score.

**Fix:** surface a capacity/resource exception immediately with an institutional owner. Separate service/input availability, notification/acceptance and worker-action clocks; pause the worker clock where readiness or delivery is absent. Demonstrate the blocked-resource path and its employment-use protections. Replace “nothing is dropped” with “retained but not yet delivered” until that distinction is visible.

### M3 - Major: the selected later episode is narrated as first-ever wasting

**Evidence:** `demo/js/child.js:53,96` and `SCRIPT.md:13`; [child timeline](2026-10-04-demo-shots/05-child-1440.png). PT-000097 has true WLZ **-2.1926 on 22 October 2024**, **-2.0587 on 22 November**, observed **MAM -2.54 on 22 January 2025**, and observed **SAM -3.2 on 22 February**, before the selected **22 June** onset. The **22 March** flag genuinely precedes the selected later episode by three months under the frozen evaluator's incident-episode definition.

**Fix:** say “three months before the next qualifying episode/recurrence,” explicitly acknowledge the earlier recorded SAM, and label the selected episode rather than “wasting begins.” Alternatively choose a first-ever-onset example and disclose the selection rule. Do not relabel a valid recurrence metric as primary prevention of this child's first wasting.

### M4 - Major: F1-led victory conceals the clinically important false-link cost

**Evidence:** zero IDs/+40% cell in `linkage.cells` and [stress view](2026-10-04-demo-shots/04-link-stress-1440.png). Bloom recovers **3,907** true links at precision **0.9143459**: **4,273 accepted**, hence **366 false accepted links**. Plaintext recovers **2,456** at precision **0.9863454**: **2,490 accepted**, hence **34 false accepted links**. Counts follow `components/identity_linkage/eval_linkage.py:14-44`; accepted = true links / precision, rounded back to its integer count. Bloom's higher F1 trades much higher recall for lower precision.

**Why it matters:** joining the wrong child's history can misroute care. Precision is present in small print, so this is not a missing-source accusation; it is a materially incomplete spoken comparison. The nearby **Dice 0.967** example is also a different, fixed simulated pair, not the stress experiment's current pair.

**Fix:** display correct and false accepted links together, mention the trade-off aloud, and distinguish the fixed illustration from the 5,000-child experiment. Set an explicit adjudication/abstention and acceptable false-link policy before operational use. A clinically matched-precision comparison would be more defensible than treating maximum F1 as sufficient.

### M5 - Major: the scripted/current capacity state does not survive the journey

**Evidence:** `SCRIPT.md:14` selects K **5 -> 3 -> 8** before revealing, but speaks K5/K3 numbers. The featured example ties **1 vs 1** at K8, unlike **0 vs 1** at K5. More importantly, `demo/js/week.js:102` always reads fixed `co.sms`, generated for the story at K5 in `demo/export.py:518-585`. After selecting **P4S5A02, 10 May 2026, K1** on screen 5, screen 6 still shows **P1S1A02, 22 March 2025, five prevention tasks**.

**Fix:** reveal at K5 first and return to the narrated K when quoting its numbers. Either derive SMS/routing from the chosen AWC-month and K or visibly transition back to “fixed featured-child pipeline, K5” before showing it. Keep the monthly benchmark unit explicit; do not translate its recall into a measured weekly service guarantee.

### M6 - Major: live policy decisions/appending are implied by a recorded replay

**Evidence:** `demo/js/break.js:73` says the picked request is decided and “lands” in a ledger. The click handler at **87** changes the selected exported scenario and re-renders; all six decisions are already in the exported ledger, which remains unchanged when clicking every request. The footer at **80** accurately says “at export,” but it is not the main message. The SHA-256 verification at **51-54** is genuinely live. The checkpoint is a retained test input in this demo, not evidence of an externally controlled district-minutes system.

**Fix:** put “recorded policy decisions; live local hash verification; simulated external checkpoint” beside the controls. Alternatively implement actual policy execution and append/reverify on interaction. In either case, say explicitly that a party able to replace both ledger and checkpoint defeats this demonstration's trust assumption.

### Minor issues

| ID | Evidence and concrete fix |
|---|---|
| **N1 - Coverage denominator** | `components/identity_linkage/synth_registries.py:156-160,188-191` documents and applies shared-ID probability conditional on a child being in both registries; `demo/js/find.js` labels the knob as all PT records. Nominal 100% is actually **94.87% of PT records**, nominal 35% **32.77%**, in these fixtures. Label the nominal conditional probability precisely and optionally show the realised all-PT fraction. Likewise explain +40% as the generator's extra per-field corruption parameter, not measured Indian typing quality or a calibrated relative deterioration. |
| **N2 - False unconditional degradation copy** | `demo/js/find.js:94`; [100%-ID screenshot](2026-10-04-demo-shots/20-link-100pct-1280.png). At 100% IDs/+40% noise, Bloom F1 is **0.995 versus 0.992** without added noise, pooled stays **1.000**, yet the text says “Both degrade.” Derive the sentence from the selected results or restrict that claim to the regimes where it is true. |
| **N3 - Amravati timeline collisions** | `demo/js/child.js:79-81`; [Amravati projector shot](2026-10-04-demo-shots/18-amravati-child-1280.png). Repeated slot labels overlap around late 2025. Stagger/group repeated annotations or show only selected milestones with accessible detail; do not reduce their already small font. |
| **N4 - Units and execution labels** | `demo/js/week.js:78-79` displays the recall difference/CI with `%`; use **percentage points**. `demo/js/break.js:78` reports `shown.length` as “SHA-256 hashes checked,” although verification runs with and without a checkpoint and can exit early; label **entries** or instrument actual hash operations. `SCRIPT.md:15` says at most 80 SMS characters, while `components/frontline_worklist/render.py:32-78` permits 160 generally; say “these exported messages are <=80 characters” unless enforcing an 80-character contract. |

An initially suspected overlap of the ALLOWED stamp was **not** reproducible after the entry animation settled; [the saved allowed-request image](2026-10-04-demo-shots/19-allowed-request-1280.png) is not evidence of that bug. Browser-helper issues with hidden duplicate selectors and SVG text access were also inspection-tool issues, not application failures.

## E. Five hardest jury questions, with the best honest answers

### 1. “Are you accusing Anganwadi workers of hiding wasting by comparing different populations and years?”

**Best answer:** No. NFHS-5's **19.3%** and June 2025 Tracker's **5.46%** are different instruments, periods and denominators. The state-wide direction is an important unexplained discrepancy, not an estimate of under-detection or worker misconduct. Coverage, selection, measurement, age mix and reporting processes all need investigation. We propose independent, blinded re-measurement and AWC/device/time-level support diagnostics, not worker scores. A close national stunting aggregate does not prove local measurement quality.

### 2. “Where is the actual department boundary, and why should I accept hundreds of wrong child links?”

**Best answer:** This prototype does not yet demonstrate an encoded-only departmental interface. It benchmarks Bloom matching over synthetic registries, and its present implementation has access to raw records and blocking fields. At the harsh zero-ID/+40% setting, the gain in recovered pairs comes with **366 false accepted links versus 34** for plaintext, so F1 alone is not an operational acceptance criterion. Bloom filters can be attacked; keyed hashes are not anonymity. A legal/data-sharing gate, a genuinely constrained matching boundary, matched-precision evaluation and independently adjudicated uncertain links are prerequisites, not achievements established by this screen.

### 3. “Your child was already SAM. What did you predict three months early, and does fitting district prevalence validate the result?”

**Best answer:** The displayed lead is to a **later qualifying incident episode** after the evaluator's recovery window, not this child's first-ever wasting. The current first-onset wording needs correction. The benchmark measures a transparent ranking rule on synthetic monthly trajectories; fitting wasting/stunting prevalence by quantile shifts does not validate trajectories, care behaviour, measurement errors or predictive utility. Severe wasting remains substantially too low and is disclosed. Linkage adds no meaningful demonstrated predictive gain: the two logistic scores round to **.384/.384**. Real benefit must be established prospectively, not inferred from calibration or one selected success.

### 4. “The child you celebrate gets no visit, a newborn competes for a slot, and you escalate to another overworked cadre. What have you actually improved?”

**Best answer:** We have demonstrated a synthetic prioritisation comparison and an inspectable task trail, not completed care or reduced malnutrition. At K5 the simulated Nandurbar rule lists **39.4% versus 36.3%** of qualifying episodes; most are missed. The example's capacity deficit remains real within the simulation, and retaining/escalating the task is not resolution. The under-six-month bypass and readiness/worker-clock separation are not correctly implemented in this demo path. Those must be fixed, with institutional ownership of supply/capacity constraints. A pilot must measure feasible workload, completed support and referral timeliness; the existing Tracker is the intended delivery surface, not something this offline page has already integrated with.

### 5. “A supervisor can declare an allowed purpose and punish a worker, or rewrite your ledger and checkpoint together. What prevents that?”

**Best answer:** The demonstrated policy rejects declared employment use, but cannot prove that an authorised reader will never misuse information. There is no displayed worker score, yet AWC-linked operational history can still be a proxy. Minimisation, worker participation, contractual employment-use prohibitions, appeals and independently governed review are necessary. The request picker currently replays six decisions; only hash verification is live. A chain detects certain changes, not arbitrary history replacement. Truncation/resealing is detected only relative to a trusted checkpoint outside the adversary's control; external custody is simulated here and must be independently implemented and governed before a deployment claim.

## F. PLAYBOOK section 11 bar: snapshot verdict

| Item | Yes / No | Reason |
|---|---|---|
| **1. One command, offline, first visual <=60 s, CPU** | **Yes** | `demo/run.sh` succeeds; actual file-page visual 0.18 s; smoke observes no network; CPU-only review. |
| **2. Core demonstration, real first, side-by-side baseline, synthetic labels** | **Yes, for the benchmark** | Real state/district evidence precedes clearly labelled matching/ranking comparisons; this does not establish the claimed departmental privacy boundary or real-world clinical benefit. |
| **3. “Crazy” element with a judge knob** | **Yes** | Removing IDs/adding noise changes a large visible comparison; capacity controls respond; truncation/resealing exposes the chain/checkpoint distinction. |
| **4. Honest numbers and no unsupported new claims** | **No** | Numerical provenance is mostly strong, but encoded-only privacy, first-onset narration, live-request wording and operational bypass/readiness promises outrun the demonstrated implementation. |
| **5. Accurate three-minute script and recorded fallback** | **No, as written** | Script and usable recorded media exist, but the prescribed K8 reveal quotes inactive K5/K3 numbers and the talk track contains the substantive overclaims above. |
| **6. Headless smoke asserting key outputs** | **Yes** | Smoke passes in 46.20 s; its district-source re-derivation skip and lack of clinical/governance-semantic checks must remain explicit. |
| **7. gpt-6-astra jury review recorded in reviews and ledger.tsv** | **No, pending lead registration** | This file and its screenshots record the review; the lead must add the review to `reviews/ledger.tsv`, which the review-only edit instruction forbids me to change. |

**Lead action:** record acceptance/rejection and disposition of the ranked findings in the review ledger. Fix or explicitly narrow B1/B2 and the clinical/governance narrative before declaring “DEMO DONE.” This review deliberately does not modify the implementation, script, fallback or ledger.

## Appendix A. Raw smoke output

The checker's “no worker-level identifiers or scores” line is its own assertion text; it should not be interpreted as proof that role/AWC operational records can never identify or be used against a worker. Likewise its successful “wasting begins” string assertion does not validate that clinical wording.

```text
2026-10-04 19:26 IST
Memory level before smoke: 39

== 1/5 data file invariants (demo/check_data.py)
  ok   data file size 364,581 bytes (< 5 MB)
  ok   data file contains no URLs
  ok   committed.identity_linkage == eval/results/identity_linkage.json
  ok   committed.early_warning_v1 == eval/results/early_warning_v1.json
  ok   committed.pipeline_demo == eval/results/pipeline_demo.json
  ok   committed.policy_gate == eval/results/policy_gate.json
  ok   committed.audit_ledger == eval/results/audit_ledger.json
  ok   committed.growth_standards == eval/results/growth_standards.json
  ok   committed.cohort_calibration == eval/results/cohort_calibration.json
  ok   gap: 36 State/UT rows identical to research/sources/state_gap_verified.csv
  ok   gap: Poshan Tracker wasting below NFHS-5 in 36/36
  ok   gap: India 19.3% vs 5.46%
  ok   gap labelled REAL
  ok   districts: 706 rows, 1 excluded and listed
  ok   districts: Nandurbar == V5 (30.7, 13.5, 45.8, 57.2)
  ok   districts: Amravati == V5 (26.2, 10.7, 29.0, 38.0)
  ok   linkage: 35% / +0% cell == eval/results/identity_linkage.json (F1, precision, recall, clerical share)
  ok   linkage: 7 x 5 = 35 cells
  ok   linkage: PPRL F1 > shared-ID F1 + 0.25 whenever RCH-ID coverage <= 50%
  ok   linkage: at 0% coverage shared-ID F1 = 0 and PPRL F1 >= 0.85 at every typo level
  ok   linkage: PPRL F1 > pooled plaintext F1 in every cell below 100% coverage
  ok   linkage labelled SYNTHETIC
  ok   worklist_ref: recall at K = 5 == early_warning_v1.json for all 5 methods
  ok   worklist_ref: WHZ rule 0.429 vs programme rule 0.3651 at K = 5
  ok   worklist_ref: bootstrap CIs at K = 5 == committed
  ok   sim[nandurbar] labelled 'SIMULATED children, REAL district rates'
  ok   sim[nandurbar] targets == REAL district values
  ok   sim[nandurbar] achieved wasting/stunting 30.7/45.8 == target
  ok   sim[nandurbar] example child linked by PPRL (correct vs truth), not by shared IDs
  ok   sim[nandurbar] example child listed 3 month(s) before onset
  ok   sim[nandurbar] K = 5: WHZ rule > programme rule > random
  ok   sim[nandurbar] every SMS <= 80 characters
  ok   sim[nandurbar] gate: 2 allows, 4 denies as expected
  ok   sim[nandurbar] gate: employment use denied by its own rule
  ok   sim[nandurbar] ledger: truncation caught only with the checkpoint
  ok   sim[amravati] labelled 'SIMULATED children, REAL district rates'
  ok   sim[amravati] targets == REAL district values
  ok   sim[amravati] achieved wasting/stunting 26.2/29.0 == target
  ok   sim[amravati] example child linked by PPRL (correct vs truth), not by shared IDs
  ok   sim[amravati] example child listed 3 month(s) before onset
  ok   sim[amravati] K = 5: WHZ rule > programme rule > random
  ok   sim[amravati] every SMS <= 80 characters
  ok   sim[amravati] gate: 2 allows, 4 denies as expected
  ok   sim[amravati] gate: employment use denied by its own rule
  ok   sim[amravati] ledger: truncation caught only with the checkpoint
  ok   no worker-level identifiers or scores in the simulated data (ADR 002)
check_data: all checks pass

== 2/5 ledger parity: page JS == Python (node demo/js/check_ledger.cjs)
  ok   [amravati] flip_reseal_all / checkpoint: JS [false,24] == Python [false,24]
  ok   [amravati] truncate_3 / no_checkpoint: JS [true,null] == Python [true,null]
  ok   [amravati] truncate_3 / checkpoint: JS [false,22] == Python [false,22]
ledger parity: JS == Python

== 3/5 offline: no external URLs or network APIs
  ok   index.html, js/*.js and data/demo_data.js reference nothing outside the folder

== 4/5 exporter re-derivation (.venv/bin/python -m demo.export --check)
  ok  gap (state_gap_verified.csv)
  skip districts: .data/raw/nfhs5 missing (run eval/fetch_nfhs5.py)
  ok  committed eval/results
  ok  linkage default cell (re-run, == identity_linkage.json)
  ok  ledger[nandurbar] chain + tamper verdicts (Python)
  ok  ledger[amravati] chain + tamper verdicts (Python)
export --check: all re-derived values match

== 5/5 headless page load (demo/check_page.py)
  ok   first visual ready in 0.18 s (bar: 60 s)
  ok   #india     all 36 States and UTs, 19.3%, 5.46%, REAL DATA
  ok   #districts In Nandurbar, 30.7%, 13.5%, 45.8%, 706 of 707 districts
  ok   #find      0.51, 0.94, 0.97, simulation assumption, SYNTHETIC
  ok   #find      true by definition, 0.89, 0.70
  ok   #child     SIMULATED children · REAL district rates, correctly, wasting begins
  ok   #week      Who gets them?, Listed and then wasted, 0.429
  ok   #sms       no names, overflow, ASHA
  ok   #break     DENIED, deny-employment-action, broken at entry, chain verifies
  ok   #break     chain verifies, broken at entry
  ok   no shared IDs, +40% typos: Bloom-filter F1 0.89 beats shared-ID 0.0 and pooled names 0.7
  ok   no page errors; no network requests (file:// only)
check_page: all checks pass

SMOKE: PASS
real 46.20
user 20.72
sys 2.62
```
