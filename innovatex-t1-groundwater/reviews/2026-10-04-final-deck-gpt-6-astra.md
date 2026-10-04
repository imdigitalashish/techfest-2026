# Final-deck hostile review - JalSakshi

- **Date:** 2026-10-04 (IST)
- **Reviewer model:** `gpt-6-astra`
- **Reasoning effort:** `max`
- **Commissioned by:** the T1 lead at the Supervisor's request
- **Setting:** InnovateX Delhi zonal, South Asian University, 10 October 2026; in person; 10 minutes.
- **Reviewed snapshot:** checkout `31cef5c95461e06d31544085b4d8052d6d91bd37`; final-package commit `4af4af6`. Paths below are relative to `innovatex-t1-groundwater/` unless stated otherwise.
- **Method:** read the requested package and previous reviews in order, then inspected the relevant implementation and saved results. No sub-agents or child sessions. Only this review is changed.

**Verdict: READY WITH FIXES for the concept-presentation zonal, not ready to present unchanged.** The local problem is strong, the corrected CGWB figures stand up, the BOM addition is correct, and the offline replay works. The largest remaining weakness is that the presentation sells capabilities the kept software does not have: per-event uncertainty, missing-rain deferral, and auto-zero. There are also two avoidable experiment-history contradictions.

The official brief permits a Round-1 concept, architecture and feasibility plan; it does not require a finished physical prototype at the zonal. My objections are to confusing proposed functionality with demonstrated functionality, not to having scheduled the rig for Round 2.

## A. Number and source verification

### A.1 Sources reopened

**Verification labels:** PRIMARY = opened the originating institution/manufacturer; SECONDARY = opened the news report, not its underlying government record; REPRODUCED = recalculated from the committed input; RECORDED = matches saved results and inspected scoring code, but not a fresh full evaluator run. **NOT VERIFIED** means I could not independently establish the claim; it does not mean the team fabricated it.

| Source opened on 4 October | Exact supporting text or access outcome | What it establishes |
|---|---|---|
| [Hindustan Times, supplied as 21 Apr 2026](https://www.hindustantimes.com/cities/delhi-news/delhi-makes-rainwater-harvesting-mandatory-penalties-for-violators-101776711439024.html) | "10% rebate on water bills for functional systems"; "increases to 15% if both rainwater harvesting and wastewater recycling systems are installed"; "Non-compliance may attract penalties, including a 1.5-times increase in water bills" | SECONDARY support for the rebate and conditional penalty wording. I did not obtain the operative government rule. |
| Same HT article | "₹204.46 crore in rebates was disbursed between 2017 and 2024"; "adequacy and functionality certificates are issued after inspection and require periodic renewal"; "A self-disclosure mechanism is also being planned" | The money is reported DJB data, not a ledger independently inspected by this reviewer. Inspection already exists; self-disclosure is described as planned. |
| Same HT article | "Till now, there was a rule but no real checking." | The slide's minister quotation is exact. It does not establish the broader assertion that nobody can check a pit or that no verification system exists. |
| [Indian Express RWH campaign report](https://indianexpress.com/article/cities/delhi/delhi-government-rainwater-harvesting-campaign-groundwater-recharge-djb-10718827/) | "for plots measuring 100 square metres and above since 2001"; "many have become non-functional due to inadequate maintenance" | SECONDARY support for the threshold, year and maintenance problem. |
| Same IE article | "construct 500 new harvesting structures and restore 1,000 non-functional systems"; "Around 7,596 of Delhi’s 9,148 government buildings"; "targeted for completion by 30 June 2026" | An announced programme and target, not verification that those works are still awaiting procurement in October. |
| Same IE article | "approximately 733 million litres of water annually"; "empanelled 59 service providers"; "developing a dedicated online portal to track installations, monitor compliance" | An estimated recharge potential, provider count and portal-development announcement. Not JalSakshi impact, a purchase commitment, or an available integration API. |
| [CGWB 2025 PDF](https://cgwb.gov.in/cgwbpnm/download/1741), PDF page 154 / printed page 128, section 7.32 | "the stage of groundwater extraction of the UT is estimated at 92.10%"; "Out of 34 assessment units (tehsils), 10 units (29.41 %)"; "337.44sq km" | PRIMARY, independently downloaded and extracted. It agrees with `research/primary-source-checks.md`. The page also gives 383.04 mcm recharge, 345.57 mcm extractable resource and 318.28 mcm extraction; the last two reproduce 92.10%. |
| [Acorn piezometer page](https://www.acorncontrols.com/piezometer.html) | "Approx. Price: Rs 38,000 / Piece"; "Built in with 365 days X 2 readings per day, Time & Date stamped storage"; cloud "updates twice daily" | VERIFIED vendor listing for this product. Neither universal logger limitations nor independent certification of the vendor's CGWA-compliance claim. |
| [Required element14 KIT0139 listing](https://in.element14.com/dfrobot/kit0139/liquid-level-trans-arduino-uno/dp/3974116) | Repeated fetch timeouts; direct retrieval also failed, including an HTTP/2 transport error and a bounded HTTP/1.1 retry. | **₹4,254.51, stock and tax basis: NOT VERIFIED in this review.** The team's earlier observation is recorded in the plan, but I did not see this listing's body. |
| [Required Farnell datasheet](https://www.farnell.com/datasheets/3708809.pdf) | Web fetch and bounded direct PDF requests timed out without a usable document. | **This PDF: NOT VERIFIED.** I used the manufacturer sources below as an explicit alternative, not as a claim to have read the PDF. |
| [DFRobot KIT0139 manufacturer page](https://wiki.dfrobot.com/kit0139/) and [manufacturer tutorial](https://wiki.dfrobot.com/kit0139/docs/18950) | Specification table: "Measuring Range 0-5m", "Overall Accuracy 0.5%", "Operating Voltage 12-36V", "Operating Temperature -20℃-70℃", "Protection Class IP68". Pinout: "AIR PIPE"; "Air guiding tube". | PRIMARY alternative support for the range, output, supply, temperature and protection specifications. The table says **overall accuracy**, not explicitly **FS**. The membrane is 316L; the casing is 304 stainless steel. |
| Same manufacturer tutorial | "The atmospheric pressure P0 on the liquid surface is introduced into the back chamber of the sensor through the air guiding tube" | The reference arrangement is documented: the air path matters. The plan need not speculate that the KIT0139 might be absolute-referenced. Protect the vent instead. |
| [HT borewell report](https://www.hindustantimes.com/cities/delhi-news/ngt-seals-illegal-borewell-in-central-delhi-101749492629182.html), [Millennium Post](https://www.millenniumpost.in/delhi/delhi-seals-nearly-16000-illegal-borewells-4000-still-untraced-612532) and [The Bar Bulletin](https://thebarbulletin.com/ngt-delhi-illegal-borewells-improper-sealing-report/) | HT states 15,962 sealed, more than 4,000 untraceable, and 20,297 identified. Millennium Post corroborates those quantities. Bar Bulletin says borewells "could be operated very conveniently without removing the seal". | SECONDARY support for Backup 1. No underlying NGT filing was independently checked here. |

Publication dates not displayed by the extracted article bodies were not independently authenticated; the HT date above is the supplied citation date. Official zonal venue/date are commissioning context; the supplied official brief itself establishes the ten-minute limit and the 1 December report/prototype deadline.

### A.2 Slide-by-slide numerical audit

Main slides are numbered 1-10; B1-B3 mean the three labelled backups, excluding the backup divider.

| Slide | Numbers checked | Finding |
|---|---|---|
| 1-2 | Theme 1; team information; 25 years; 100 m²; 2001; 10%; 15%; ₹204.46 crore; 2017-2024; annual certification; 1.5× | Theme and required team fields match `_briefs/innovatex.txt`. The elapsed **calendar-year** difference is 2026 minus 2001 = 25. The remaining quantities match the news reports with the policy qualifications above. Actual team details remain placeholders. |
| 3 | 92.1%; 10/34 tehsils; 337.44 km² | VERIFIED PRIMARY from CGWB section 7.32. Do not recompute the percentage from the heavily rounded 0.32/0.35 bcm values. |
| 3 | 1,000 restorations; 500 new structures; 30 Jun 2026; 7,596/9,148 buildings; approximately 733 million L/year | VERIFIED SECONDARY as an announced programme and estimate. October implementation/procurement status is **NOT VERIFIED**. |
| 4 | 483,253 readings; 185 stations; 46 reporting in 2026; six hours; 23% zeros; 17% missing slots | REPRODUCED from `eval/data/delhi_gw_levels.csv.gz`: **480,428 telemetric + 2,825 manual = 483,253**; 185 telemetric stations; 46 with any 2026 row; median interval 6.0 h; 111,837 exact zeros = **23.2786% of telemetric rows**; **17.4235%** missing expected slots **between each station's first and last report**. Not a current network-uptime estimate. |
| 4 and its figure | 2.5 m; 79 stations; mapped 178; ringed 44 versus fleet 46 | REPRODUCED: median **2.507 m**, rounded to 2.51 in JSON, from 79 stations. This is the median of each station's **April-June maximum depth minus August-November minimum depth**, not a difference of seasonal means. Map: 178 coordinate-valid stations, 44 with a 2026 row; two of the fleet's 46 are outside the mapped subset. No numerical contradiction between those counts. |
| 5 | 0-5 m; 0.5% FS; dry 15 min / wet 1 min; two outputs / four verdicts | Range is supported by the manufacturer. FS interpretation is conditional, not explicit in the opened table. Sampling periods are **design choices**, not measured node performance. Four verdict labels exist in code; a numerical uncertainty output does not. |
| 6 and screenshot | 60 seconds; July-August 2025; 250 m² roof; 2.25 m² pit; 185/46/23%; 178 mapped; 480,428 readings | The areas and period are explicitly scripted fixtures in `deliverables/demo/build_demo.py`, not surveyed geometry. Fleet statistics reproduce. Playback completed at 1× in **45.022 s** in this review; it fits a 60-second narrated demo if switching is controlled. Rain provenance has the qualification below. |
| 6 screenshot / live replay | 39 events; 34 verified; 4 clogged; 1 implausible; 63.6 versus 64.8 m³; last-three-event trend; 0.5 m³ eligibility; 0.5 threshold; 0.48 final trend | VERIFIED against embedded data, builder and rendered replay. The volume totals exclude the implausible event; the trend is a **demo heuristic**, not the fleet evaluator's maintenance metric. Dates on tickets label event starts, not issuance times. |
| 7 | 13.1% / 58%; 14.5% / 61%; 3.0% / 16%; 10/10; false flags ≤1.3%; clogging precision 0.60-0.67 / recall 0.90-1.0 | RECORDED correctly after rounding; exact values and denominator restrictions are below. These are simulation results, not field accuracy or uncertainty-interval coverage. |
| 7 | Five rejected fixes; rule set before the runs | Five rejected candidates exist, but **not all five made another test worse**. The v3 preregistration timestamp is later than its candidate timestamps. See D12-D13. |
| 8 | ±25 mm; 2.25 m²; ±0.11 m³; about 3%; 4 m³ | Conditional arithmetic is correct: 0.005 × 5 m = 0.025 m; one reading gives 0.05625 m³; two endpoint errors give **0.1125 m³**, or **2.8125% of 4 m³**. This bounds an illustrative **storage difference**, not total inferred infiltration. Geometry is assumed. |
| 8 | -20 to 70 °C; 316L; IP68; IP67; annual dip check | Manufacturer supports probe temperature/IP68 and **316L membrane, 304 casing**. The IP67 enclosure's current listing could not be verified. Annual checking is a proposed maintenance interval, not a sourced proof of stability. |
| 9 / B2 | ₹11,166; ₹4,254.51; approximately ₹38,000; six base prices; optional ₹3,729; shared ₹33,559; 3.6 V; enclosure dimensions; IN865 | Subtotal arithmetic passes. Current independent price/specification checks are separated in A.3; most retailer pages were unavailable. Acorn price/cadence and the RAK listing were independently readable. |
| 9 | 1,000 government buildings; 59 providers; ₹204 cr | Matches the earlier IE announcement / rounded HT rebate figure. Neither is a validated addressable market or signed customer. The explicit disclaimer that ₹204 cr is not the market is good. |
| 10 | Approximately 733 M L/year; October/November plan; 1-3 field pits; 3-pit ask; 1 Dec | 733 is the external estimate, not team impact. Pit counts and build months are targets. **1 December 2026** matches the official brief. The campaign's aquifer-recharge estimate cannot be independently certified by summing modelled pit losses. |
| B1 | 20,297; 15,962; 4,000+; six-hour cadence / approximately 12-hour aliasing limit | News figures corroborated. Twelve hours is the ideal sampling-theory period corresponding to six-hour samples; it is not a validated detector cutoff. The refusal to accuse individual borewells is appropriate. |
| B3 | 40 pits/split; 2025 dev / 2024 holdout; exponent 0.5-1.5; lognormal 0.25/day; lag 0-5 min; ±25 mm offset; ±10 mm seasonal drift; zero floor; 2.1 mm quantisation; registry ±5-10% | VERIFIED as evaluator settings, not measurements. Area is perturbed ±5%; catchment and reference drain rate ±10%; runoff prior is separately fixed at 0.75. Quantisation is approximately **2.098 mm/count** for the assumed 1.92 V span, 3.3 V reference and 12-bit ADC. The ±10 mm drift is invented stress-test input, not a manufacturer specification. |
| B3 | Improvement >0.5 points; other evaluators no worse than 10%; holdout confirmation | Matches the written v3 keep rule, not proof that it was registered before testing. Earlier program wording differs in how regressions are constrained. |

**Exact saved holdout results** (`eval/results/recharge_v1_holdout.json`, `recharge_v1_evalv2_holdout.json`, `recharge_v1_evalv3_holdout.json`; scoring inspected in `components/recharge_verifier/autoresearch/eval.py`):

| Evaluator | Scored detected events | MdAPE | APE p90 | False-implausible rate | Clogging precision / recall |
|---|---:|---:|---:|---:|---:|
| v1 same-model | 1,369 | 2.97284% | 16.09080% | 0% | 0.8333 / 1.0 |
| v2 stress | 1,233 | 13.09716% | 57.53899% | 0.15492% | 0.6667 / 1.0 |
| v3 sensor stress | 952 | 14.45662% | 60.68678% | 1.29758% | 0.60 / 0.90 |

All six saved dev/holdout results contain ten simulated fakes and recall 1.0. The headline percentages exclude detected events with true infiltration below **0.2 m³** and are computed over the verifier's event windows, not independently delineated storms. Clogging is a **last-scored-event, end-of-season** classification. On **dev**, v2 and v3 both have clogging precision **0.40** and recall **0.6667**. The v3 holdout also misses one of six blocked pits (recall 0.8333). Do not present the demo's maintenance ticket as independently validated by these numbers.

I did not rerun the six full seasonal evaluators: their hourly weather input is absent from this clean worktree and must be fetched. The saved numbers, scoring implementation and small adversarial reproductions were checked. India-WRIS quantities were independently recomputed from the committed raw snapshot.

### A.3 BOM: correct addition, incomplete deployment economics

| Listed item | Listed ₹ | Independent check in this review |
|---|---:|---|
| KIT0139 | 4,254.51 | **NOT VERIFIED**: element14 timeouts/transport failure; manufacturer specifications checked separately. |
| RAK3172 IN865 | 1,672.80 | VERIFIED: [vendor HTML](https://www.electronicscomp.com/rakwireless-wisblock-lpwan-module-rak3172-rui3-in865) contains `Rs.1672.80` in displayed and structured price fields. |
| ESP32-C6 prototype host | 1,099.00 | **NOT VERIFIED**: [Robu listing](https://robu.in/product/espressif-esp32-c6-devkitm-1-n4-dev-board/) returned HTTP 403. |
| Forte ER34615 cell | 879.00 | **NOT VERIFIED**: [Robu listing](https://robu.in/product/forte-er34615-d-3-6v-li-socl2-battery/) returned HTTP 403. |
| IP67 enclosure, 150×100×70 mm | 3,250.87 | **NOT VERIFIED**: [Amazon listing](https://www.amazon.in/Otdorpatio-Waterproof-Electrical-Enclosure-150x100x70mm/dp/B09F918F1N) returned HTTP 503. |
| PG7 gland | 10.00 | **NOT VERIFIED**: [Robu listing](https://robu.in/product/polyamide-cable-gland-pg-7/) returned HTTP 403. |
| Optional rain gauge | 3,729.00 | **NOT VERIFIED**: [Amazon listing](https://www.amazon.in/DFRobot-Gravity-Tipping-Bucket-Rainfall/dp/B0GGC21C1M) returned HTTP 503. The team's own source log says unavailable. |
| Shared LPS8N gateway | 33,559.00 | **NOT VERIFIED**: [Amazon listing](https://www.amazon.in/Robocraze-Multi-Channel-Indoor-Gateway-Lorawan-LPS8N/dp/B0DP91M6BZ) returned HTTP 503. The team's own log does not confirm the IN865 variant. |

Decimal recomputation:

```text
  4,254.51 + 1,672.80 + 1,099.00 + 879.00 + 3,250.87 + 10.00
= 11,166.18

Base + one rain gauge                         = 14,895.18
Base without prototype host                   = 10,067.18
Base without prototype host + gauge           = 13,796.18
One base node + one gauge + one shared gateway = 48,454.18
Three base nodes + three gauges + one gateway  = 78,244.54
```

The last two are **illustrative allocations of listed parts**, not installed quotes, and assume a shared gateway is suitable for the sites. They exclude the unpriced boost converter, switching circuit, antenna, tube, sock, mounting, protection, installation, backhaul, service and any tax/shipping adjustment. PPK2 is a separate bench tool, not a per-node charge. There is no justification for carrying forward the previous review's unreproduced ₹47,389 figure; the current arithmetic above is the appropriate reference.

### A.4 Did the accepted previous-review fixes actually land?

This checks every accepted row in `reviews/2026-10-04-lead-response.md`, including its grouped Q&A rows. "Done" means the specific correction is visible, not that field performance is proved.

| Accepted item | Status in the final package |
|---|---|
| Astra A1: measurement observability | **Partial.** Slide 5 separates drainage and volume and disclaims aquifer recharge in notes. It still promises an unimplemented band and treats the commissioning model as sufficient verification; D3-D4. |
| Astra A2: circular simulation | **Presentation fix done; experiment pending.** Slide 7 leads with 13.1/14.5%, labels simulation and n=10. Blind trials and the hardware teammate are future work, not evidence already obtained. |
| Astra A3: affordability | **Partial.** Corrected base subtotal and explicit unpriced parts, but no installed or annual quote; D10. The earlier judge's numerical estimate was rightly not accepted without reproduction. |
| Astra A4: buyer | **Partial.** Government buildings and providers are a target segment. `thought_node.md:27-35` still requests a pilot letter and interviews and says there is no pilot letter; D11. |
| Astra A5: reliability | **Partial.** Sampling/power/outage plans are explicit. The optional-gauge wake-up gap and unconditional no-loss wording remain; D8-D9. |
| Astra Q1-Q5 | **Included:** current Q&A 1, 19, 4, 3 and 5 respectively. The measurement answer remains inadequate; the narrower hardware-novelty, cheating, simulation and metered-fill answers are present. |
| Astra R1: policy wording | **Partial.** Slide 2 correctly says planned/inspection/may. Absolute no-verification statements and stale landscape text survive; D2. |
| Astra R2: city-wide extraction claim | **Done.** Slide 3 uses 92.1% and 10/34; primary CGWB check passes. |
| Astra R3: one Acorn product, not all loggers | **Done in the deck.** Slide 9 says "one"; Q&A 19 also refers to one device. This still does not establish novelty over all existing event loggers. |
| Astra R4: wrong-range pressure sensor | **Range correction done.** KIT0139 replaces the 30-bar part. FS basis, installation datum and complete error propagation still need qualification; D7. |
| Grok G1: sensor, barometer and price | **Mostly done in the deck.** Correct-range probe and no baseline BME280. Current retailer price was not independently reachable; vent handling and mixed materials need correction; D7/D10. |
| Grok G2: self-certification | **Done on slide 2, not throughout the evidence pack**; D2. |
| Grok G3: lead with rebate/stress test; borewells to backup | **Done.** Slides 1-3, 7 and B1 implement it. |
| Grok G4: owner incentives / inspector override | **Advisory wording done.** Slides 5 and 9 do not automate billing. Actual willingness to pay remains unproved; D11. |
| Grok G5: impact, battery and team | **Partial.** 733 M L/year is labelled external, battery life is not promised. Team fields are still unfilled, and structure drainage is not the same outcome as the campaign's recharge estimate; D1/D3. |
| Grok Q1-Q5 | **Included:** current Q&A 1, 2, 9, 7 and 20 respectively. Inclusion has not resolved uncertainty, total cost or procurement evidence. |
| Grok O1/O2: policy status column | **Done in the deck.** Cross-document cleanup is incomplete; D2. |
| Grok O3: range and installation extras | **Partial, with a response-ledger contradiction.** Range fixed; extras explicitly excluded. The response's "The installed cost includes them." is not true of the published subtotal; D10. |
| Grok O4: demo score, BOM note, secondary-source attribution | **Done for the stated corrections.** Memo now scores the current demo 3/5; BOM has the both-sensors correction; slide 2 attributes ₹204.46 crore to HT citing DJB. These are not reasons to demand a physical rig at Round 1. |

## B. Scores against the official criteria

These are hostile-judge evidence scores, not official weights or a forecast of selection. The bonus is scored separately rather than folded into a made-up official total.

| Official criterion | Score / 5 | Evidence |
|---|---:|---|
| Creativity and novelty | **3** | Per-event maintenance evidence tied to Delhi's RWH workflow is specific; falling-head testing, loggers and rainfall checks are familiar, and the claimed uncertainty innovation is absent from C5 output. |
| Functionality and usability | **2** | The replay works, but an absent rain series produces an implausible verdict rather than deferral; real radio/outage/sensor robustness is not demonstrated. |
| Cost and market value | **2** | ₹11,166.18 is a correct partial parts sum, not a deployed service price; no buyer commitment or operating-cost comparison with inspection is present. |
| Technical implementation and feasibility | **2** | Correct-range sensing and a weighed-water rig are credible directions; venting, sensor elevation, warm-up, event wake-up, calibration and weatherproof installation remain unresolved. |
| Regional scalability | **2** | A common software interface helps, but the main deck does not explain adaptation beyond Delhi; Q&A's identical-physics answer skips different structures, geology and purchasing rules. |
| Environmental and socioeconomic impact | **2** | Cleaning-before/after drainage is a measurable prospective benefit; no saved-water outcome, aquifer attribution, maintenance-cost saving or water-quality safety result exists yet. |
| Design and ergonomics | **3** | The advisory workflow and provenance labels are useful. Small screenshot text, a clipped map heading, disappearing tickets and no demonstrated operator task/override flow limit the case. |
| Problem-centric local-understanding bonus | **4** | Reopened Delhi policy reporting, primary CGWB numbers and original WRIS profiling are substantially better than a generic IoT pitch; stale programme status and causal overinterpretation lose the fifth point. |

## C. Five strongest panel attacks and fixes by 9 Oct, 18:00 IST

The quoted questions below are proposed judge questions, not source quotations. Each remedy is achievable as a software, evidence or presentation correction before the deadline; none requires pretending to finish the December field programme.

### C1. "Show me the uncertainty interval on one actual event. What observation distinguishes infiltration from a bypass?"

**Why the present answer fails:** Q&A 1, 2 and 17 assert a band and a commissioning solution. The kept verifier emits only point estimates. A spill height caps stored water, not cumulative overflow; an unobserved bypass is not made observable by declaring a wider band.

**Deadline fix:** Make calibrated **drainage-performance screening** the demonstrated product. Label litres as model-based estimates, not verified aquifer recharge. Remove the band claim unless interval fields, a defined uncertainty model and coverage results are actually implemented. Show one controlled fill with independently measured inflow/overflow and state which paths remain unobserved. For the zonal, a labelled schematic and an explicit validation protocol are sufficient.

### C2. "Unplug the rain gauge. Why does your software accuse my building? How does a sleeping sensor see a short storm?"

**Why the present answer fails:** Q&A 18 promises deferral; the code treats absent/NaN rainfall like zero rainfall. Q&A 12-17 describe proposed hardware protections as if they close failure modes. The 15-minute dry loop and optional gauge do not establish timely wake-up.

**Deadline fix:** Add and demonstrate an explicit insufficient-data/maintenance state before issuing performance or tamper verdicts. Cover absent rain, absent stage, stale observations and link outage with small executable cases. Make the gauge mandatory for the demonstrated wake-up mode, or restrict that claim. Add a node cross-section with the sensor datum, dry vent termination, above-metal antenna placement and finite buffer capacity. Mark warm-up/current draw and 24-hour outage recovery as October acceptance tests, not completed guarantees.

### C3. "Who signs a purchase order, and what does the first installed site cost?"

**Why the present answer fails:** Q&A 7, 9 and 11 substitute a June-targeted campaign for a current customer. A gateway allocation alone changes the first-site parts total substantially. There is no annual service cost or measured saving from ranked inspection.

**Deadline fix:** Put base-node, first-site and three-node-pilot subtotals side by side, with unpriced and tax/shipping items explicit. Obtain a dated supplier quotation or retained listing evidence for the load-bearing probe/gateway and one actual service-provider or campus conversation. If a pilot letter is not obtained, use **prospective pilot customer**, not **first buyer**. Add a cost-comparison plan using inspections avoided, false tickets and cleaning cost; do not invent ROI.

### C4. "Your preregistration is timestamped after the tests. Why should I trust the rest of the evidence?"

**Why the present answer fails:** Q&A 2 repeats the five-regressions story. `program.md` says v3 was preregistered at 10:50; `results.tsv` records candidates at 10:36 and 10:39. One of those candidates failed minimum improvement, not cross-test regression. The weather fetch does not pin an ERA5 model despite repeated ERA5 labels.

**Deadline fix:** Publish a compact experiment manifest linking exact verifier/evaluator revisions, input checksum, split and metric denominator. Correct the rejected-candidate reasons. Establish the actual chronology from existing evidence; if prior registration cannot be established, remove that claim rather than backdating it. Pin or accurately relabel the weather source, and disclose synthetic minute-scale disaggregation. Present the current holdout as a recorded check, not an untouched prospective validation set.

### C5. "That 'bucket' is 1,200 litres. When does a real maintenance officer actually receive the alert?"

**Why the present answer fails:** Q&A 4 says a no-rain pour gets flagged without identifying the tested scale. The fleet fakes are 500-2,000 L; the demo fake is 1,200 L. An ordinary 20 L no-rain pour produces no event in a clean synthetic check. The replay's maintenance ticket is issued at the end of the season, although its label says 27 August; C7 is explicitly an unvalidated heuristic.

**Deadline fix:** Call the current example a **large injected pulse**, show its litres and show at least one undetected small/slow pour. Display event start, end and ticket time separately. Do not claim immediate alerts if the current evaluator waits for a long recession to finish. Add a compact false-ticket/latency table, including v2/v3 dev clogging precision 0.40; keep the inspector override and explain the next maintenance validation experiment.

## D. Numbered red flags for ACCEPTED / REJECTED disposition

### D1. Required team information is not finished

**Location:** deck slide 1, lines 19-20; `deliverables/qa-prep.md:102-103`; official `_briefs/innovatex.txt`, Round-1 requirements.

The deck still contains `‹TEAM NAME›`, `‹ID›` and member/contact placeholders; Q&A 25 has `<Fill in: team, roles.>`. A brand name does not supply the required team ID and member contacts. **Fix:** fill the registered details and presenter roles, staying within the official four-member maximum.

### D2. The inspection vacuum is still overclaimed, including in the opening

**Location:** deck slide 1 notes, line 24; slide 2 notes, line 47; slide 3, line 59; `deliverables/zonal-pitch.md:12`; `deliverables/qa-prep.md:40`; `research/landscape.md:19-20,38,85`.

Exact deck claims include "Nobody can tell you whether those pits work." and "The verification system doesn't exist yet." The reopened HT article explicitly describes inspection and periodic renewal. The landscape still says "self-certification since Apr 2026" and presents the penalty without the corrected qualification. **Fix:** describe the proposed addition as continuous per-event performance evidence alongside existing inspection. Keep the minister's quotation attributed, not converted into a universal fact.

### D3. The water-balance claim remains stronger than the observations

**Location:** deck slides 5 and 10, lines 96 and 182; `deliverables/qa-prep.md:19-20,51-53,76`; `components/recharge_verifier/verifier.py:79-93`.

"An unseen bypass widens the band." is not an implemented or generally sufficient remedy. The code uses `infil = k_use * A * integral`; overflow is an estimate from a rainfall prior and time near spill stage. Spill height does not bound the total volume that can spill while inflow continues. A commissioning fill can calibrate a restricted model, but cannot establish where all future outflow goes. **Fix:** qualify geometry, drainage law, bypass and overflow assumptions; distinguish storage, drainage loss and aquifer recharge. Do not promise to certify DJB's aquifer-recharge total from this instrument alone.

### D4. The core uncertainty feature is absent

**Location:** deck slide 5, lines 96/103; `deliverables/qa-prep.md:19,23`; `components/recharge_verifier/verifier.py:111-125`; `architecture/contracts/gwcontracts.py:304-318`.

"Infiltrated volume ± band" has no lower/upper bound, confidence level or validity flag in the returned event. The contract also lacks interval fields. Aggregate APE p90 is not a per-event calibrated interval. **Fix:** remove or explicitly label this as planned until implemented and tested for coverage.

### D5. Missing rain does not defer the verdict

**Location:** `deliverables/qa-prep.md:78-79`; deck slide 5 verdicts; `components/recharge_verifier/verifier.py:43,79,96-104`.

Q&A says "The verdict is deferred, never guessed." I ran the kept verifier on a six-hour synthetic series with a known rise/recession, using both an empty rain series and an all-NaN rain series. Both returned `rain_mm: 0.0` and `verdict: "implausible"`, just like measured zero rain. No AWS fallback is wired into this function. **Fix:** separate missing from observed-zero inputs and abstain before judging the event.

### D6. Auto-zero is described as available although both candidates were rejected

**Location:** deck slide 8, line 153; `deliverables/qa-prep.md:68,77`; `deliverables/prototype-plan.md:32,72`; `components/recharge_verifier/autoresearch/results.tsv:12-13`.

"A dry-floor auto-zero removes constant offset." is a present-tense capability. The ledger says both auto-zero candidates were not kept and that the verifier reverted to v1. The kept function has no auto-zero stage. **Fix:** label firmware auto-zero as planned and not included in reported results, or implement it and rerun the relevant cases. Explain how a real dry reference is recognised.

### D7. The sensor error budget omits its installation datum and misstates material/reference details

**Location:** deck slides 5/8; `deliverables/prototype-plan.md:19,27,68-74`; `deliverables/qa-prep.md:65-77`; opened DFRobot specifications/tutorial.

The planned sensing tip is 5-10 cm above the floor, while the budget treats the reading as floor-referenced stage. For the illustrative 2.25 m² open pit, that corresponds to **0.1125-0.225 m³ below the sensing elevation**; above the sensor, the known height offset must also enter the storage/drainage model. Dry-zeroing the electronics cannot observe water below the tip. The primary table says overall 0.5%, without an explicit FS basis, and identifies a **316L membrane / 304 casing** and an air-guiding tube. **Fix:** draw and model the datum/blind region, qualify the FS calculation, protect the dry vent, and stop treating a two-reading storage-error calculation as the infiltration uncertainty budget.

### D8. The advertised acquisition schedule is not the evaluated acquisition schedule

**Location:** deck slide 5, lines 91-92; `deliverables/prototype-plan.md:26,29-30`; `components/twin_simulator/simulate.py:81-119`; `components/recharge_verifier/verifier.py:43,102`.

The rain gauge is optional, yet its interrupt is the only described way to wake before the next dry poll. A powered-down pressure sensor does not continuously observe a rise. Evaluators supply essentially one-minute samples throughout, with sparse random dropouts; rolling 30/11-sample windows assume that cadence. **Fix:** evaluate the actual duty cycle and interrupt path, or explicitly restrict the results to continuously available one-minute telemetry. Do not carry those error numbers over to 15-minute acquisition without testing.

### D9. Proposed hardware integrity and reliability read like completed guarantees

**Location:** deck slide 1 notes, line 24; slide 5, line 91; slide 8, lines 152-156; `deliverables/qa-prep.md:31,59-64`; `deliverables/prototype-plan.md:14,80-88,111-112`.

"We built the instrument that can." and "A local buffer means no lost events." overrun the current software-replay evidence. A finite buffer needs capacity, retention, overwrite and power-loss rules; a flush antenna can still be shielded by a metal lid. The plan itself identifies sensor settle time as unknown and quotes a 30-minute preheat recommendation, while the power examples assume seconds; that recommendation was **not independently verified from the unavailable PDF**. **Fix:** add BUILT / SIMULATED / PLANNED status, a bounded outage claim, an installation sketch and measured-power acceptance criteria. Keeping battery life unpromised is the right decision.

### D10. The base parts sum is being used where a deployment cost is needed

**Location:** deck slide 9 / B2; `deliverables/qa-prep.md:47-50`; `deliverables/prototype-plan.md:35-65`; `reviews/2026-10-04-lead-response.md:26,47`.

The deck does disclose exclusions, so **the ₹11,166 addition itself is not wrong**. However, the response ledger says "The installed cost includes them." while the plan excludes installation hardware. Gauge, gateway, backhaul, labour, recurring service and tax/shipping treatment are not reconciled in the buyer comparison. Current independent retail verification also remains incomplete, as recorded in A.3. **Fix:** retain the qualified base subtotal, add allocated pilot cost and annual cost, and archive price evidence. Do not compare a partial DIY node directly with a packaged commercial logger as proof of better value.

### D11. An expired target and a provider list are not a current buyer

**Location:** deck slides 3/9; `deliverables/qa-prep.md:41-44,54-56`; `thought_node.md:27-35`; reopened IE article.

The source targets June 30 completion; the pitch is in October. "First buyer: DJB's Phase-I restorations of 1,000 government buildings." assumes ongoing need, procurement access and willingness to pay that the source does not establish. A portal announcement does not establish an API or permission to integrate. **Fix:** use a prospective maintenance-pilot segment and explicitly state the current contact/permission status.

### D12. Preregistration chronology contradicts the run log

**Location:** deck slide 7, line 140, and B3 title; `components/recharge_verifier/autoresearch/program.md:22-25`; `results.tsv:12-13`; Q&A 2.

The program says "pre-registered 4 Oct 2026, 10:50 IST, before any v3 candidate was run"; candidate rows say **10:36** and **10:39**. The documents alone therefore do **not** verify the deck's before-the-runs assertion. This may be a timestamp/documentation error; it is not evidence sufficient to accuse the team of deliberate fabrication. **Fix:** reconcile from existing records or remove the preregistration claim. Never repair this by inventing an earlier timestamp.

### D13. The five-rejections explanation is factually wrong

**Location:** deck slide 7, line 140; `deliverables/qa-prep.md:24`; `components/recharge_verifier/autoresearch/results.tsv:8-13`.

"We rejected five fixes that improved the stress test because they made another test worse." Four candidates have documented cross-evaluator regressions. `v3-c2` improved v3 by only 0.113 points, with v1 and v2 unchanged; it failed the required >0.5-point gain. **Fix:** say five candidates failed the keep rules, four through regression and one through insufficient gain. Do not use an inaccurate story as evidence of experimental discipline.

### D14. The fake-pour example is much larger than an ordinary bucket

**Location:** deck slides 5-7; `deliverables/qa-prep.md:29-32`; `components/twin_simulator/simulate.py:64-68`; `deliverables/demo/build_demo.py:51-54`; verifier `H_ON` at line 22.

Fleet fake volumes are **0.5-2.0 m³ (500-2,000 L)**, and the demo injects **1.2 m³ (1,200 L)** in one minute. In a noise-free 2.25 m² synthetic pit, my 20 L no-rain injection peaked at 0.00883 m and produced **no event**; 100/500/1,200 L injections were flagged. This is not a failure of the stated 10/10 fixture result, but it defeats the implied generality of "a bucket". Also, fleet fake timestamps are randomly chosen, not explicitly restricted to rain-free times. **Fix:** disclose volume/rate and adversary conditions, and add small/slow/real-rain cases without claiming guaranteed fraud detection.

### D15. The demo conflates event labels with alert time

**Location:** deck slide 6; `deliverables/demo/README.md:9-12`; `deliverables/demo/build_demo.py:72-90`; rendered `jalsakshi-demo.html`.

Observed replay: the implausible ticket is labelled **19 Aug 08:52**, appears with the clock at **22 Aug**, and reports **27.7 mm over the event**; the injected pulse is dated 20 Aug. The maintenance ticket is labelled **27 Aug 23:03** but appears at the replay's end, with the clock at **1 Sep**. Builder code schedules tickets at `t1` and labels them with `t_start`. **Fix:** separate onset, completion and issuance, qualify the no-rain claim as an instantaneous-pulse test rather than a rain-free event window, and disclose latency. The replay is not evidence of immediate maintenance alerts.

### D16. "Per storm" and "wide band" hide the actual scoring unit

**Location:** deck slide 7; `deliverables/qa-prep.md:2-13,23`; `components/recharge_verifier/autoresearch/eval.py:12-17,65-85`; `deliverables/demo/README.md:12`.

The errors are over detected windows with true infiltration ≥0.2 m³, and those windows can contain multiple storms. APE p90 is not a per-event confidence band. The false-implausible metric uses only the healthy/clogging pit classes, not every non-fraudulent event across all classes. End-of-season clogging classification is not precision of the last-three-event ticket rule. The reported holdout precision 0.60 is compatible with 40% false positives among positive classifications; dev stress precision is only 0.40. **Fix:** show event counts/thresholds, dev and holdout maintenance results, and a separate future ticket-latency/precision evaluation. Do not market this as already proven inspection efficiency.

### D17. ERA5-specific and minute-scale rainfall provenance are not established as stated

**Location:** deck slides 6-7/B3; `deliverables/demo/README.md:8`; `components/data-ingest/fetch_delhi.py:101-118`; `components/twin_simulator/simulate.py:48-53`.

The fetch uses the Open-Meteo archive without a `models` parameter. I could not establish the actual selected upstream model from the available request/cache evidence; **ERA5-specific provenance is NOT VERIFIED**. Minute rainfall is then created with a seeded Dirichlet split of hourly totals. This matters to a one-minute jump detector. The exact hourly input is not in this checkout. **Fix:** pin the source/model and retain a checksum or reproducible fixture, and label minute timing as synthetic. A public historical weather series is not a measured roof rain gauge.

### D18. WRIS arithmetic is sound, but the hydrological interpretation is too strong

**Location:** deck slide 4 and notes; `deliverables/qa-prep.md:91-97`; `eval/realdata_profile.py:54-107`; `eval/results/realdata_profile.json`.

The latest telemetry row is **4 Jun 2026**, so "reported in 2026" does not mean online at the October pitch. The missing-slot metric stops at each station's last report. The 2.5 m statistic compares seasonal extremes under heuristic sign resolution; it does not attribute the change to RWH. Spike/flatline diagnostics are calculated but not removed before the hydrology calculation, which excludes zeros and gross range failures. **Fix:** call this a public-stream snapshot and an exploratory seasonal depth-change statistic, not proof that cleaning the stream verifies a particular pit's aquifer benefit.

### D19. Regional scalability is not actually explained in the main presentation

**Location:** deck slides 9-10; `deliverables/qa-prep.md:95-98`; official Round-1 "Impact & Scalability" requirement.

Campuses and RWAs are additional customers, not a regional adaptation plan. "The pit physics is the same everywhere." does not answer geometry, porous media, underdrains, aquifer type, rainfall, telemetry or tariff differences. **Fix:** add a short eligibility/adaptation line: standard software, site-specific storage/drain calibration and safety checks, local communications and buyer rules. Limit the first pilot to one explicitly described structure type.

### D20. The water-quality objection has no deployment gate

**Location:** `deliverables/qa-prep.md:99-101`; deck slide 10 impact claims; `deliverables/prototype-plan.md:140-147`.

The answer correctly admits no quality monitoring, but a future EC channel and a suggested first-flush diverter are not an acceptance procedure for sending runoff into the ground. **Fix:** state a restricted, permitted roof-runoff pilot with existing pretreatment and a responsible site operator; define when the system must not recommend recharge. Do not imply conductivity alone certifies water safety.

### D21. The physical-feasibility and validation documents still contain stale descriptions

**Location:** `research/landscape.md:50,98`; `components/recharge_verifier/README.md`, final paragraph; prototype plan section 2.

The landscape still proposes a sealed absolute sensor plus barometer while the current manufacturer documents a vented arrangement. The verifier README still describes evaluator v2 as planned although v2/v3 results are already used in the final deck. **Fix:** add a clearly dated current-state summary and retain genuinely historical results as history, not the current design.

### D22. Presentation assets and sourcing do not meet the footer's absolute promise

**Location:** deck footer, line 7; slides 4-8; `deliverables/figures/dwlr_quality_map.png`; `deliverables/figures/demo_screenshot.png`.

"Every number is sourced on its slide" is not literally true: slide 5's cadence and slide 8's illustrative geometry are unlabeled assumptions, and the crucial software-result reference is in speaker notes. The inspected map image has a clipped heading. The complete UI screenshot contains text too small to carry the argument when reduced into a slide. **Fix:** use visible compact citations/status labels, mark assumptions, repair the map asset and crop/enlarge the decisive event/ticket. Verify the final exported presentation on the actual display.

### D23. The ten-minute plan has no explicit handoff reserve

**Location:** `deliverables/zonal-pitch.md:8-20,33-34`; deck TIME notes.

The ten allocations sum to exactly 600 seconds. The final 75 seconds say "incl. buffer" without specifying how much is speech versus reserve, while the pitch separately asks for a 9:30 rehearsal. Human delivery time is **NOT VERIFIED**. **Fix:** move slide 4 to backup, pre-open the demo, and use the revised 9:15 allocation in E.

### D24. "Before the monsoon" needs a scheduled test, not just storm-triggered logic

**Location:** deck slide 10, line 183; `deliverables/prototype-plan.md:29-32`; `deliverables/qa-prep.md:75-77`.

Clogging that develops during a dry period produces no new recession evidence. Annual dip checks and a one-time commissioning fill do not by themselves establish pre-monsoon drainage performance. **Fix:** specify a pre-monsoon metered-fill inspection, or qualify the benefit as detection following the next observed storm / preparation for the next season.

## E. Ten-minute delivery check

**Possible in principle; not verified as a human delivery.** Current allocations are:

```text
20 + 80 + 50 + 45 + 90 + 75 + 60 + 45 + 60 + 75 = 600 seconds
```

The observed 45.022-second replay fits the 75-second demo slot, leaving about 30 seconds for opening, narration outside playback and returning to slides. Its advertised 60-second script is therefore plausible. The final maintenance ticket arrives only at the end of playback: stopping early to recover time loses the payoff.

**Cut slide 4, the standalone DWLR analysis, first.** It is repeated in the demo's left panel, does not prove the recharge-pit product and invites a separate hydrology argument. Keep the public-data snapshot as a backup, not a second product pitch. This saves 45 seconds without cutting the official problem, background, proposed solution or impact requirements.

| Revised section | Clock |
|---|---|
| Title/team | 0:00-0:20 |
| Existing policy and inspection gap | 0:20-1:40 |
| Why now | 1:40-2:30 |
| Solution and measurement boundary | 2:30-4:00 |
| Demo, pre-opened | 4:00-5:15 |
| Results and limits | 5:15-6:15 |
| Physical feasibility | 6:15-7:00 |
| Cost, prospective buyer and regional adaptation | 7:00-8:00 |
| Impact, safety boundary and ask | 8:00-9:15 |
| Reserve | 9:15-10:00 |

Rehearse with the actual presenter handoff and final exported slides by 9 October, not just by reading the TIME comments. Keep a legible static ticket fallback. Do not cut the measurement-boundary or feasibility material to make room for extra groundwater statistics.

## F. Verdict and top three fixes

**READY WITH FIXES for Round 1.** This is a credible Delhi-specific maintenance-screening concept with a functioning, honestly labelled simulation replay. It is not yet an independently validated recharge meter, fraud detector or inspection-economics product. None of the fixes requires claiming a rig exists before the official Round-2 build period.

1. **Make every claimed capability match the kept implementation.** Remove or mark planned the uncertainty band and auto-zero; implement missing-data abstention; make model-based drainage the demonstration boundary. Show the actual fake-pour scale and alert timing. This closes the most damaging live Q&A failure: asking to see a feature that does not exist.
2. **Repair the experimental evidence story before presenting it.** Reconcile the 10:50/10:36/10:39 chronology without backdating, correct the four-regressions-plus-one-small-gain explanation, disclose detected-event denominators and synthetic minute rain, and pin the weather provenance. The saved headline error numbers themselves do not need embellishment.
3. **Turn the deck into a bounded pilot proposal and finish the presentation.** Publish first-site/pilot cost with omissions and price-verification status; call DJB a prospective customer until contact/permission is evidenced; add the sensor/vent/datum and safety/adaptation boundaries; fill all team details; move slide 4 to backup and rehearse the 9:15 route.

**Release gate: 9 Oct 2026, 18:00 IST.** All three fixes, registered team details and a timed rehearsal should be complete before calling this a final zonal deck. If the missing capabilities and experiment-history contradictions are left in the spoken pitch, my verdict becomes **NOT READY to present that version**.
