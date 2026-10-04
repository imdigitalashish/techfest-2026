# DustLedger: hostile final-deck review

**2026-10-04 15:57 IST** | Reviewer: gpt-6-astra | Snapshot: `4758e64`

Paths are relative to `innovatex-t2-aqi/`; D = `deliverables/`, R = `research/`, A = `components/attribution/`, QA = `D/qa-prep.md`. Scores and verdict are judgments; suggested experiments are not results.

## 1. Judging scores

| Item | Criterion | /5 | Evidence |
|---|---|---|---|
| 1.1 | Creativity/novelty | 3 | R/landscape.md acknowledges established fence-line attribution; integration remains the hypothesis. |
| 1.2 | Functionality/usability | 2 | Deck B2: attribution simulated; physical control and dashboards planned. |
| 1.3 | Cost/market value | 2 | D/prototype-plan.md prices parts, not operation; QA10 offers a buyer case, not a validated payer. |
| 1.4 | Technical feasibility | 2 | QA3/13: coarse-dust response and weather survival untested. |
| 1.5 | Regional scalability | 3 | QA20 requires local siting, aerosol and calibration checks. |
| 1.6 | Environmental/socioeconomic impact | 2 | QA11: suppression unverified; no measured PM, water or wage outcome. |
| 1.7 | Design/ergonomics | 2 | Deck B2: supervisor app planned; installation usability untested. |
| 1.8 | Local-depth bonus | 4 | Substantial Delhi evidence, weakened by policy misreadings below. |

**Unweighted mean: 2.29/5 across seven core criteria; 2.50/5 including bonus.** Not official competition weights.

## 2. Source checks and overclaims

Personally reopened these five load-bearing sources; quotation/number checks:

2.1 **[IIT Kanpur report](https://environment.delhi.gov.in/sites/default/files/environment/generic_multiple_files/final_report09jan2016_1.pdf), F9/F10: MATCH.** Section 4.6 gives construction-material ranges 2-5% PM10 and 0.6-5% PM2.5; Table 3.1 gives 5166.8376 kg/day PM10; dividing by 143 t/day gives 3.6%. Deck slide 4's "a few per cent of the city's PM" must remain a historical, category-specific estimate, not today's entire construction footprint.

2.2 **[Hindustan Times fines](https://www.hindustantimes.com/cities/delhi-news/caqm-standardises-penalties-for-pollution-violations-across-delhincr-101709058335907.html), F6: CONTEXT FAIL.** The ₹5 lakh quotation matches **existing Delhi practice**, contrasted with the article's **new ₹1-2 lakh construction schedule**. ₹7,500 and GRAP doubling match. Deck slides 3/9, QA10 and D/prototype-plan.md incorrectly turn the old figure into today's universal yardstick. Remove the "12%" comparison; current applicable orders remain **UNVERIFIED**.

2.3 **[Winter Action Plan article](https://thenewsmill.com/2026/09/delhi-launches-winter-action-plan-2026-27-with-50-work-from-home-and-construction-bans-to-reduce-pollution/), F1/F2: MATCH.** Nov 1-Jan 31, Dec 10-Jan 20, "100% CCTV" and 334 teams match. This is secondary reporting, not verified operative orders or permission to experiment.

2.4 **[Down To Earth](https://www.downtoearth.org.in/governance/with-grap-4-enforcing-construction-ban-is-government-compensating-daily-wage-labourers), F7/F8: NUMBERS MATCH.** 1,378,199; 89,518; five of 75; ₹8,000 match. R/fact-check.md wrongly calls this DTE's own survey: Aledia conducted it. Date the figures; neither rolls nor this sample measure wages DustLedger would protect.

2.5 **[CSTEP guidance](https://cstep.in/publication/guidance-for-evaluating-the-performance-and-use-of-air-quality-sensors-for-construction-dust-pm10-monitoring/), F12: MATCH.** Six models, five manufacturers, one year; "qualitatively assess" matches. It does not validate DustLedger's quantitative differential or causal attribution.

2.6 **Universal ban/causation:** D/presenter-card.md: "Delhi stops every site, clean or dirty, because it can't tell them apart." The opened [GRAP article](https://www.hindustantimes.com/cities/delhi-news/as-delhi-s-air-turns-severe-emergency-curbs-kick-in-under-grap-stage-3-101762885233197.html) lists exempt categories. Neither article establishes that causal explanation. Replace across deck, pitch and memo with activity-/stage-specific restrictions; triage does not confer exemption.

2.7 **Unbuilt protection:** QA6: "When the wind signature and the node pattern disagree, the system says inconclusive." `A/methods.py::_ring` only subtracts selected nodes and checks speed below 0.5 m/s; the reported method has no disagreement detector. Deck slide 6's "the site's own dust" is a hypothesis, not established causality.

2.8 **Threshold sleight:** Deck slide 8 says below 1 m/s "we say 'inconclusive' there"; the reported method uses 0.5. Show the actual threshold and its coverage beside MAE. B3/QA4's "lower bounds" on site calms are **UNVERIFIED**; `eval/results/calm_wind.json` contains grid statistics, not a site comparison.

2.9 **Impossible sequencing/unsupported permission:** QA12 says the campus fallback "needs no permission". Delete. D/prototype-plan.md allocates 26-31 Oct to assembling four nodes plus "one week side by side": six days, with no subsequent pre-November field window. Advance commissioning or make an appropriately approved, safety-controlled bench trial the default.

2.10 **Cost/power/tamper:** Parts-only exclusions and QA9's "None of this is tested yet" are good. But deck slide 9's "Battery with no sun | 12.1 days" needs **model estimate**, not demonstrated autonomy. D/prototype-plan.md explicitly assumes efficiency/usable capacity and warns about monthly-mean sunlight. Keep QA9's secure-key/off-site-anchor conditions in the talk.

2.11 **Residual boast:** Slide 7 notes say "where nobody is"; `architecture/adr/001-spike.md` says "Nobody measures what a given site adds." Opened [Envirosuite](https://envirosuite.com/solutions/dust-monitoring) markets low-cost networks that pinpoint sources. Use QA8's bounded integration claim. ADR's "real PM10 cuts" and combustion-signature extension also need correction against QA11/19: neither is demonstrated.

## 3. Eight hardest judge questions

| Item | Question | QA assessment; better truthful answer |
|---|---|---|
| 3.1 | Whose coarse dust is this? | **Partial, QA3/6:** "system says inconclusive." Say: differences are not causal proof; disagreement rejection is planned; blind source/reference challenges come first. |
| 3.2 | Does your error support decisions? | **Partial, QA5:** "still wins in all four scenarios." Say: 57.43 is simulated all-hour MAE (`A/autoresearch/results.tsv`); `A/autoresearch/eval_v2.py::score` substitutes zero for abstentions. Publish coverage and false-positive/negative rates before selecting an action threshold. |
| 3.3 | Who pays without exemptions? | **Weak, QA10:** "evidence in disputes". Say: willingness to pay and legal usefulness are UNVERIFIED; test demand for inspection triage independently of permission to operate. |
| 3.4 | Isn't this existing fence-line monitoring? | **Mostly good, QA8:** "low-cost workflow". Retain the narrow integration hypothesis; superior cost/performance versus incumbents is UNVERIFIED. |
| 3.5 | Can contractors manufacture clean readings? | **Good, QA9:** "Nothing stops it". Retain that answer: physical defenses are untested; authenticated records do not establish honest exposure. |
| 3.6 | What pollution or water have you saved? | **Partial, QA11:** "misting on and off". Say: none measured. Propose randomized comparable-work blocks, independent reference measurements and metered water; distinguish suppression from wetting the sensor. |
| 3.7 | What evidence arrives despite the ban? | **Bad, QA12:** "needs no permission". Say: approvals and commissioning gate trials; report a controlled experiment if field access fails, never relabel it field validation. |
| 3.8 | What fails in fog, outages and dust? | **Partial, QA13/15:** "humidity flag and correction". Say: the specification is non-condensing; fog performance, complete-system power and service intervals remain UNVERIFIED pending bench measurements. |

## 4. Slide-by-slide

Budgets total 9:15, leaving 45 seconds; actual delivery time is **UNVERIFIED**. The solution arrives only at 3:50.

| Item/slide | Budget | Problem/fix |
|---|---|---|
| 4.1 / 1 | 20s | Fill team fields; remove universal-ban opening. |
| 4.2 / 2 | 50s | Distinguish reported plan, activities and stages. |
| 4.3 / 3 | 50s | Fix obsolete fine; monitoring norm is not measured station spacing. |
| 4.4 / 4 | 60s | Historical source shares and worker rolls are not impact achieved. |
| 4.5 / 5 | 50s | [TERI's 314 ± 77](https://www.teriin.org/infographics/state-air-delhi-ncr-pollution-and-solution) matches, but covers NCR sites in 2016-17, not today's site background. |
| 4.6 / 6 | 80s | Move earlier; label causality and control as unproven. |
| 4.7 / 7 | 40s | Move forecasting to backup; remove "nobody". |
| 4.8 / 8 | 70s | Display fair 69.4 comparator, threshold and coverage together. |
| 4.9 / 9 | 50s | Withdraw fine ratio; visibly label power estimates. |
| 4.10 / 10 | 85s | Replace promised proof with approval-dependent milestones. |
| 4.11 / B1 | Backup | Gaps mean abstention, not zero pollution. |
| 4.12 / B2 | Backup | Bring built/simulated/planned distinctions forward. |
| 4.13 / B3 | Backup | Remove unsupported lower-bound claim. |
| 4.14 / B4 | Backup | Explain maximum-node truth and zero-scored abstentions. |
| 4.15 / B5 | Backup | Missing essential parts prevent a complete build-cost claim. |
| 4.16 / B6 | Backup | Add direct source links; distinguish reporting from orders. |

## 5. Selection memo

5.1 **Recommendation honest; some arguments aren't.** Both earlier reviews picked T1; T2's new pricing/power work genuinely addresses their omissions. "Most crowded theme" is UNVERIFIED; demo 4/5 is aspiration. Conversely, historical city shares don't settle near-site value. T1's current `innovatex-t1-groundwater/deliverables/prototype-plan.md` offers blind tests and pass criteria, but also requires a rain gauge, gateway and commissioning: not merely "one node". Compare physical evidence gates, not predicted spectacle or theme popularity.

## 6. Verdict

6.1 **Keep T1 for Delhi; DustLedger is not final-ready.** Its candid simulation and documented parts make a credible alternative, not a demonstrated enforcement instrument. The fine premise, claimed abstention behavior and trial sequencing need correction before presentation. The defensible case is a falsifiable inspection-triage experiment; protected wages, cleaner city air and earned permissions remain unproved. Without blind coarse-dust evidence, rhetorical confidence cannot substitute for measurement.
