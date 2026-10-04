---
marp: true
theme: default
paginate: true
size: 16:9
header: "DustLedger · InnovateX 2026 · Theme 2 (Rising AQI in Modern Urban Cities) · Delhi zonal"
footer: "Status labels: BUILT · SIMULATED · PLANNED · every run number is rendered from committed results (eval/render_docs.py)"
style: |
  section { font-size: 23px; }
  h1 { font-size: 34px; color: #0f766e; }
  table { font-size: 18px; }
  .small { font-size: 15px; color: #555; }
  .tag { font-size: 14px; font-weight: 700; padding: 1px 6px; border-radius: 4px; background: #eef2f5; }
  .sim { font-size: 14px; font-weight: 700; padding: 1px 6px; border-radius: 4px; background: #fdecd3; color: #b45309; }
  .big { font-size: 40px; font-weight: 700; color: #0f766e; }
---

<!-- _class: lead -->
# DustLedger
### Estimate each construction site's own dust — so inspectors can go where the evidence points

**Team:** ‹TEAM NAME› · **Team ID:** ‹ID› · **Theme 2:** Rising AQI Levels in Modern Urban Cities
‹Member 1 — role› · ‹Member 2 — role› · ‹Member 3 — role› · ‹Member 4 — role› · ‹email / phone›

Status today: data pipeline + replay <span class="tag">BUILT</span> · sites and sensors in the replay <span class="sim">SIMULATED</span> · sensor ring + misting <span class="tag">PLANNED</span>

<!--
TIME 0:00–0:20 (20 s). LOGISTICS: present zonal-deck.pdf from your own laptop, with demo/dustledger-demo.html pre-opened in a second tab (offline); backup slides B1–B8 follow the last main slide. Cue card: presenter-card.pdf.
SAY: "We're ‹team›. Delhi's winter dust rules are applied by activity and by pollution stage, not by what each site actually releases. We propose a way to estimate each site's own dust. Today we have the data pipeline and a stress-tested simulation; the sensor ring is our Round-2 build."
-->

---

# This winter, Delhi's plan restricts dust-generating construction citywide

| When (reported plan) | What |
|---|---|
| {{v:F1|Nov 1 – Jan 31}} | dust-generating demolition and outdoor civil works **prohibited** |
| {{v:F1|Dec 10 – Jan 20}} | **total ban** on construction and demolition |
| GRAP emergencies | stage-wise restrictions on top (some project categories exempt); GRAP-3 halted construction for {{v:F3|16 days}} in 2025 ({{v:F3|₹10,000}} compensation announced) |
| Every site | {{v:F1|100%}} CCTV coverage mandated |

**Restrictions follow the activity and the pollution stage — not each site's measured dust.**

<span class="small">Sources: Delhi Winter Action Plan 2026-27 as reported by The News Mill (Sept 2026; secondary, not the operative order); Hindustan Times (Nov–Dec 2025). Fact rows F1, F3.</span>

<!--
TIME 0:20–1:00 (40 s).
SAY: "Delhi's Winter Action Plan for this year, as reported, prohibits dust-generating demolition and outdoor civil works from November first to January thirty-first, and bans construction from December tenth to January twentieth. GRAP emergencies add stage-wise stops; last year GRAP-3 halted construction for sixteen days. These rules follow the activity and the pollution stage — not what each site actually releases."
-->

---

# A monitor can say the air is bad — not which site made it bad

- **City-scale sensing:** {{v:F5|47}} reference monitors in Delhi (going to {{v:F5|60}}); the planning norm is one per {{v:F5|25-50 km²}}
- **Site compliance = checklists:** anti-smog guns ({{v:F6|₹7,500}} fine per missing gun per {{v:F6|5,000 m²}}), CCTV, self-audit uploads
- **Fines by area, not by dust:** CAQM's 2024 schedule, as reported, sets {{v:F6|₹1 lakh to ₹2 lakh}} per construction-site violation depending on area, doubled under GRAP (current operative order UNVERIFIED)
- **Trust is strained:** in Oct 2025 water tankers were filmed spraying at the Jahangirpuri reference monitor; CPCB says its data can't be manipulated

**Penalties track checklists and area, not the dust a site actually releases.**

<span class="small">Sources: Hindustan Times (2026; Feb 2024, reporting the CAQM order of 6 Feb 2024); Newslaundry (30 Oct 2025); New Indian Express (3 Dec 2025). Fact rows F5, F6, F25.</span>

<!--
TIME 1:00–1:45 (45 s).
SAY: "Delhi measures air at city scale: forty-seven reference monitors, planned at about one per twenty-five to fifty square kilometres. A monitor can tell you the air is bad; it can't tell you which site around it made it bad. So compliance is a checklist — anti-smog guns, CCTV, self-audits — and fines depend on site area, not on how much dust a site releases. And when tankers are filmed spraying a reference monitor, people stop trusting the numbers."
-->

---

# A small source, handled with blunt tools

<div style="display:flex; gap:40px">
<div style="flex:1">

<span class="big">{{v:F9|2-5%}}</span>
of Delhi's ambient PM10 came from construction material in IIT Kanpur's receptor study for DPCC (data 2013–14; track-out onto roads is counted as road dust).
Construction & demolition: {{v:F10|3.6%}} of PM10 *emissions*; concrete batching another {{v:F10|10%}}.

</div>
<div style="flex:1">

<span class="big">{{v:F7|1,378,199}}</span>
construction workers on Delhi's welfare-board rolls (Dec 2024) — only {{v:F7|89,518}} active members.
In a rapid survey reported by Down To Earth, {{v:F8|5 of 75}} site workers were registered; none of those had received the {{v:F8|₹8,000}} aid.

</div>
</div>

**Stops fall hardest on daily-wage workers — for a source that was a few per cent of city PM in that study.**

<span class="small">Sources: IIT Kanpur (2016) for DPCC, §4.6 and Table 3.1 (primary; {{v:F10|3.6%}} is our arithmetic: {{v:F10|5.1668}} of {{v:F10|143}} t/d); Down To Earth (Dec 2024; survey by Aledia). Fact rows F7–F10.</span>

<!--
TIME 1:45–2:35 (50 s).
SAY: "Here's the honest size of the problem. In IIT Kanpur's source study for the Delhi government, construction material was two to five per cent of ambient PM10. It's a real source, but a small one in that study. The stops fall hardest on daily-wage workers: nearly fourteen lakh are on Delhi's welfare-board rolls but only about ninety thousand are active members, and in one survey most site workers weren't registered for the aid. So we are not promising to clean Delhi's air. We're proposing an evidence tool for fairer, targeted inspection."
-->

---

# Why today's tools fall short

| What exists | The gap |
|---|---|
| Reference monitors (CAAQMS) | city scale — can't single out a site |
| Compliance monitors streaming to the DPCC cloud (e.g. Airveda, Prana Air) | absolute PM; winter PM10 averaged {{v:F11|314 ± 77 µg/m³}} across NCR sites in TERI–ARAI's 2016-17 campaign, so a site is a small difference on top |
| Anti-smog guns, sprinklers | run on timers — no feedback on whether dust fell |
| City AQI forecasts (IITM, Google) | tomorrow's city AQI, not today's dusty site |
| Fence-line dust systems (e.g. Aeroqual, Envirosuite) | established for mines and industry; we didn't find a low-cost workflow for Indian construction sites in the product pages we reviewed |

<span class="small">Sources: research/landscape.md §3–4 (vendor pages; TERI–ARAI). Fact row F11.</span>

<!--
TIME 2:35–3:15 (40 s).
SAY: "Indian compliance monitors stream a PM number to the DPCC cloud. But Delhi's winter background is in the hundreds of micrograms, so a sensor at the fence mostly measures Delhi, not the site. Anti-smog guns run on timers. Forecasts predict the city, not the site. Fence-line attribution is established for mines and industry; we borrow it — we just didn't find it packaged for Indian construction sites at low cost."
-->

---

# DustLedger: a fence-line ring that subtracts Delhi

![bg right:40% fit](deck/fig_site.png)

1. **Sense** — 4 PM nodes + 1 wind sensor on the boundary; solar + LoRa; LTE gateway <span class="tag">PLANNED</span>
2. **Estimate** — downwind minus upwind = our estimate of the site's own dust (an inference, not proof of cause); **"inconclusive" below 0.5 m/s wind** <span class="sim">SIMULATED</span>
3. **Act** — mist only when the estimate says the site is adding dust; flow-metered <span class="tag">PLANNED</span>
4. **Record** — signed, hash-chained records → a list that tells inspectors where to look first <span class="tag">PLANNED</span>

A check for confused or swirling wind, and for nodes that disagree with the wind, is planned — not built.

<!--
TIME 3:15–4:45 (90 s).
SAY: "Four cheap sensors on the boundary and a wind sensor. Delhi's background reaches all four; the site's own dust reaches mostly the downwind ones. The difference is our estimate of the site's contribution — an inference, not proof of cause. When the wind is under half a metre per second, we say 'inconclusive', and inconclusive never means clean. A check for swirling wind and for nodes that disagree with the wind is planned, not built. When the estimate says the site is adding dust, the misting line turns on instead of running on a timer. Records are signed on the device and hash-chained, so edits become detectable. The output is a list that tells inspectors where to look first; penalties still need DPCC's own verification."
-->

---

# Attribution, stress-tested <span class="sim">SIMULATED sites · REAL background + wind</span>

![h:330](deck/fig_attribution.png)

All hours: self-calibration {{n:at_selfcal}} vs {{n:at_refcal14}} µg/m³ for the strongest reference-visit baseline; coverage {{n:at_cov}} ("inconclusive" below 0.5 m/s). **Work hours, when dust is emitted: no better ({{n:at_work_selfcal}} vs {{n:at_work_refcal14}}).** Its gain is fewer false alarms above 50 µg/m³ (FAR {{n:at_far_selfcal}} vs {{n:at_far_refcal14}}). Simulation only; fresh seeds, not blind.

<!--
TIME 4:45–6:15 (90 s).
SAY: "This is the core test. The background PM and the wind are real Delhi data; the sites, their dust and the sensor faults are simulated. Two independent reviewers made it harder: sensor fouling, dust responding differently from ambient air, dirty nights, a neighbouring site, a biased wind vane, and a stronger baseline — a fourteen-day median of weekly reference visits. Across all hours, the fixed pair is off by about ninety-six micrograms, the ring by about sixty-nine, and the ring with self-calibration by about fifty-seven, against sixty-five for the reference baseline. But in work hours, when dust is actually emitted, self-calibration is no better than the reference baseline, and both errors roughly double. Its real gain is fewer false alarms — about half as many — which matters if a flag sends an inspector to a clean site. It's a simulation with fresh seeds, not a blind test; a controlled dust test decides."
-->

---

# Cost and power — from vendor listings and datasheets

| | |
|---|---|
| Kit parts: 4 nodes + wind + gateway + misting | **₹{{n:bom_kit}}** (listed retail parts incl. GST; excludes masts, cabling, data plan, installation, upkeep — not a build cost) |
| One node | ₹{{n:bom_node}} |
| Wind sensor | ₹{{n:bom_wind}} — {{n:bom_wind_share_pct}}% of the kit |
| Power per node (model estimate) | {{n:pw_load}} Wh/day from datasheet currents + stated assumptions |
| 10 W panel in December (model estimate) | {{n:pw_margin}}× the daily load (monthly-mean sunlight; smog weeks are darker) |
| Battery with no sun (model estimate) | {{n:pw_autonomy}} days |

For scale: one construction-site violation costs {{v:F6|₹1 lakh to ₹2 lakh}} under CAQM's 2024 schedule as reported. Willingness to pay is untested.

<span class="small">Prices seen by the lead on robu.in / amazon.in, 4 Oct 2026 (deliverables/bom/bom.csv). Datasheets: Sensirion SPS30, Espressif ESP32-S3; irradiance: NASA POWER (fact rows F20–F22).</span>

<!--
TIME 6:15–7:15 (60 s).
SAY: "Costs come from vendor listings we opened: about sixty-one thousand rupees of parts for a four-node ring, a wind sensor, a gateway and a misting line. That's parts only — not installation or upkeep — and the wind sensor is a quarter of it. Power is a model estimate from datasheets: about ten watt-hours a day per node, so a ten-watt panel covers about twice the load in an average December, and the battery lasts about twelve days without sun. We'll bench-measure all of it. For scale, a single violation costs one to two lakh rupees under the 2024 schedule — but whether anyone will pay for this is untested."
-->

---

# What we will test by 1 December — and our ask

| When | What (approval-dependent) | Evidence it produces |
|---|---|---|
| 5–19 Oct | order parts; build and bench-test one node, then four | measured current draw; working firmware |
| 20–26 Oct | four nodes side by side; reference co-location if a slot is granted | inter-node agreement; calibration vs a reference |
| 27–31 Oct | real-site trial **only if a site and approvals are in place** (Delhi's restrictions start 1 Nov) | first real fence-line estimates |
| Nov | approved, safety-controlled dust-source test: ring + wind + misting on/off in randomised blocks | estimate vs a known source; abstention rate; litres used |
| 1 Dec | report + working prototype | real sensor data, labelled; never called field validation |

**Proposal, not a promise:** an "earned-permission" pilot for verified-clean sites, for CAQM to consider.
**Ask:** a pilot site · a reference co-location slot · a DPCC/CAQM contact

<!--
TIME 7:15–8:45 (90 s). Then stop: 1:15 reserve.
SAY: "Here's what we'll test, and every step depends on approvals. By mid-October, a bench-tested node, then four. In late October, four nodes side by side and, if we get a slot, next to a reference monitor. A real-site trial is only possible before November first, when Delhi's restrictions start, and only with a site and approvals in place. Otherwise our evidence is an approved, safety-controlled dust-source test with misting on and off in randomised blocks — measuring how well we recover a known source, how often we abstain, and the water used. We'll report that as a controlled test, never as field validation. One proposal — not a promise: an earned-permission pilot for sites that prove they're clean. Our ask: a pilot site, a reference co-location slot, and a DPCC or CAQM contact."
-->

---

# B1 · Forecasting on real Delhi data — why it isn't our spike <span class="tag">BUILT</span>

![h:330](deck/fig_forecast.png)

Next-day PM2.5 at 4 CPCB/DPCC monitors (data from Feb 2025; walk-forward, n = {{n:fc_n_pm25}} station-days): yesterday's value is off by {{n:fc_persist_pm25}} µg/m³. Our ML **without** future weather was {{n:fc_nofuture_worst_pct_pm25}}% to {{n:fc_nofuture_best_pct_pm25}}% vs that; only an oracle with tomorrow's actual weather gained {{n:fc_oracle_pct_pm25}}%.

<!-- BACKUP. Use for "why not forecasting?". Say: with only months of station history, our ML did not beat yesterday's value for PM2.5 without peeking at tomorrow's actual weather, which no forecaster has. The ERA5 inputs are retrospective; an operational version would need issued forecasts. CAMS here is one grid point with an uncontrolled forecast vintage, so it's a reference, not a fair competitor. IITM already runs city forecasting. -->

---

# B2 · One week of the replay <span class="sim">SIMULATED site</span>

![h:470](deck/fig_timeseries.png)

<!-- BACKUP. Use for "show me how it behaves". Top: real Delhi background PM10 at a DPCC monitor. Bottom: a simulated site's true contribution vs the fixed pair and DustLedger; gaps are 'inconclusive' hours, not zero pollution. The clipped peak is a calm-wind hour in the simulation. -->

---

# B3 · What is built, simulated and planned

| <span class="tag">BUILT</span> (committed, reproducible) | <span class="sim">SIMULATED</span> (labelled) | <span class="tag">PLANNED</span> (Round 2) |
|---|---|---|
| CPCB/DPCC hourly PM at 4 Delhi monitors (OpenAQ archive) + ERA5 | construction sites, emissions, plumes | 4-node ring, wind mast, gateway |
| forecast benchmark, walk-forward split | sensor gains, fouling, drift, faults | misting line with flow meter |
| attribution replay + frozen evaluators (v1, v2.1) + ledger | neighbour site, road, dirty nights | signed records + hash chain |
| typed contracts, verified parts list, power estimate, offline demo | misting effect: **not modelled** | swirling-wind check, supervisor app |

<!-- BACKUP. Use for "what have you actually built?" -->

---

# B4 · Calm wind and "inconclusive"

| Delhi, Nov–Jan (ERA5 grid, 2023–2026) | Share of hours |
|---|---|
| wind < 0.5 m/s (our current abstention threshold) | {{n:calm_lt05_winter_pct}}% |
| wind < 1.0 m/s | {{n:calm_lt10_winter_pct}}% |
| wind < 1.5 m/s | {{n:calm_lt15_winter_pct}}% |
| median wind | {{n:calm_median_winter}} m/s |

ERA5 is a ~25 km grid. Calm at a real site, behind buildings and hoardings, has not been measured — that's one of the first things the ring will log. "Inconclusive" never counts as clean.

<!-- BACKUP. Use for "what about Delhi's calm winter nights?" The replay abstains below 0.5 m/s; coverage in the stress test is shown on slide 7. Better calm-wind handling is on the backlog, not a claim. -->

---

# B5 · Stress-test details (evaluator v2.1, held-out Jan–Sep 2026)

| MAE, µg/m³ | Fixed pair | Ring | Ring + weekly ref. visit | Ring + 14-day ref. median | Ring + self-calibration |
|---|---|---|---|---|---|
| easy | {{n:at_pair_easy}} | {{n:at_ring_easy}} | {{n:at_refcal_easy}} | {{n:at_refcal14_easy}} | {{n:at_selfcal_easy}} |
| medium | {{n:at_pair_medium}} | {{n:at_ring_medium}} | {{n:at_refcal_medium}} | {{n:at_refcal14_medium}} | {{n:at_selfcal_medium}} |
| hard | {{n:at_pair_hard}} | {{n:at_ring_hard}} | {{n:at_refcal_hard}} | {{n:at_refcal14_hard}} | {{n:at_selfcal_hard}} |
| hard, other site shape | {{n:at_pair_hardrect}} | {{n:at_ring_hardrect}} | {{n:at_refcal_hardrect}} | {{n:at_refcal14_hardrect}} | {{n:at_selfcal_hardrect}} |
| **work hours only** | {{n:at_work_pair}} | {{n:at_work_ring}} | {{n:at_work_refcal}} | {{n:at_work_refcal14}} | {{n:at_work_selfcal}} |

Truth = the site's contribution at its most-exposed node; "inconclusive" hours are scored as zero. Events above 50 µg/m³: self-calibration POD {{n:at_pod_selfcal}}, FAR {{n:at_far_selfcal}}; 14-day reference median POD {{n:at_pod_refcal14}}, FAR {{n:at_far_refcal14}}. Fresh seeds but **not blind**: the test period was seen during earlier versions, and the extra site shape is visible in the evaluator.

<!-- BACKUP. Use for "isn't your simulator rigged?" Answer: the first simulator favoured us and was rebuilt after review; a second reviewer added a stronger reference baseline; self-calibration still wins on all-hour error, but work-hour errors are large and this is not a blind test. -->

---

# B6 · Parts list summary (prices seen 4 Oct 2026)

| Subsystem | ₹ (incl. GST) |
|---|---|
| 4 nodes (SPS30, SHT30, ESP32-S3, SX1262, 10 W panel, LiFePO4 + MPPT charger, IP65 box) | {{n:bom_nodes4}} |
| Wind speed + direction sensor | {{n:bom_wind}} |
| Gateway (A7670C LTE, ESP32-S3, SX1262, box) | {{n:bom_gateway}} |
| Misting kit + flow sensor + relay | {{n:bom_actuator}} |
| **Kit parts total (partial: not a build cost)** | **{{n:bom_kit}}** |

Not included: buck converters, cabling, masts, radiation shields, SIM/data, installation, reference co-location, upkeep. Every line with its URL: deliverables/bom/bom.csv. The relay listing was out of stock; the SX1262 module's IN865 band is unconfirmed.

<!-- BACKUP. Use for "how much does it cost?" Say "parts" every time; installed and lifetime costs are not known yet. -->

---

# B7 · Offline demo (screenshot) <span class="sim">SIMULATED sites · REAL background + wind</span>

![h:340](demo/demo.png)

Six simulated sites ranked by their own dust over a real Delhi week. Held-out check, 20 simulated sites: Spearman ρ {{n:demo_rho}}, {{n:demo_top5}} of the true top-5 found — an easy test (emissions differ up to 30-fold).

<!-- BACKUP. If the demo tab fails, show this. Say: "Real background and wind; simulated sites. The list tells an inspector where to look first; the truth toggle shows where the ring is wrong — the two cleanest sites swap places because both are near the noise floor." -->

---

# B8 · Sources (selected)

<span class="small">

- Delhi Winter Action Plan 2026-27 — [The News Mill, Sept 2026](https://thenewsmill.com/2026/09/delhi-launches-winter-action-plan-2026-27-with-50-work-from-home-and-construction-bans-to-reduce-pollution/) (reporting, not the order) · GRAP — Hindustan Times, Nov–Dec 2025
- CAQM penalty schedule (order of 6 Feb 2024) — [Hindustan Times, Feb 2024](https://www.hindustantimes.com/cities/delhi-news/caqm-standardises-penalties-for-pollution-violations-across-delhincr-101709058335907.html) (reporting) · CAAQMS network — Hindustan Times, 2026
- Construction workers and aid — [Down To Earth, Dec 2024](https://www.downtoearth.org.in/governance/with-grap-4-enforcing-construction-ban-is-government-compensating-daily-wage-labourers) (survey by Aledia)
- Source apportionment — [IIT Kanpur for DPCC, Jan 2016](https://environment.delhi.gov.in/sites/default/files/environment/generic_multiple_files/final_report09jan2016_1.pdf) (primary)
- Winter PM10 — TERI–ARAI (2016-17 campaign) · Low-cost sensors for construction dust — [CSTEP guidance (2025)](https://cstep.in/publication/guidance-for-evaluating-the-performance-and-use-of-air-quality-sensors-for-construction-dust-pm10-monitoring/)
- Datasheets — Sensirion SPS30 v0.9; Espressif ESP32-S3 v2.1 · Irradiance — NASA POWER climatology
- Data — CPCB/DPCC monitors via the OpenAQ archive; ERA5 and CAMS via Open-Meteo
- Every number with URL, quote and grade: research/fact-check.md · run numbers: eval/render_docs.py

</span>

<!-- BACKUP. Sources slide. -->
