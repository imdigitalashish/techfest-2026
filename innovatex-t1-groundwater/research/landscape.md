# Landscape — IoT for urban groundwater in Delhi (InnovateX Theme 1)

> Lead-written synthesis, 4 Oct 2026 (IST), lean mode. **Citation rule:** every source below was opened tonight by the lead or by a research worker whose notes are committed in `research/` (worker files: `domain-delhi-rules-economics.md`, `social-signal-news.md`, `../components/data-ingest/research_sources.md`). Numbers marked **[run]** come from our committed script `eval/realdata_profile.py` → `eval/results/realdata_profile.json`. Search-engine summaries that we could not open are listed only as **leads (UNVERIFIED)**. Accessed dates are 2026-10-04 unless noted.

## 1. The local problem, in numbers

**Depletion and over-extraction.**
- **CGWB 2025 (primary):** Delhi's annual recharge is 0.38 bcm, its extractable resource 0.35 bcm and its extraction 0.32 bcm, a **stage of extraction of 92.10 %**. **10 of 34 tehsils are over-exploited**, covering 337.44 km² of 1,487.62 km² recharge-worthy area (*National Compilation on Dynamic Ground Water Resources of India, 2025*, §7.32, PDF p. 154 / printed p. 128) [S23]. Verified by the primary-source checker (`research/primary-source-checks.md`).
- The 2023 assessment, as reported by The Hindu, had 617.25 km² of 1,487.61 km² (41.49 %) over-exploited [S6]. The over-exploited area therefore **shrank** between assessments. The pitch says "still over-exploited", not "worsening".
- Delhi land is sinking where groundwater is pumped. CNA's report from Dwarka quotes a housing-society representative: residents stopped using groundwater, but "the adjoining areas – they're still using the groundwater" [S14]. BusinessLine/Bloomberg (29 Oct 2025) reports a *Nature Sustainability* study finding more than 2,400 buildings in New Delhi, Mumbai and Chennai already at high structural-damage risk [S15].
- Quality: the New Indian Express (2 Dec 2025), summarising a CGWB report, says 13–15 % of Delhi samples exceeded the uranium safe limit, with nitrate, fluoride, lead and salinity also found [S13].

**Illegal extraction: enforcement happens on paper.**
- **DJB has identified tens of thousands of illegal borewells.** Its affidavit to the NGT reported 22,010 identified and 13,693 sealed (The Hindu, 20 Apr 2025) [S6]. District magistrates later told the NGT that 15,962 had been sealed out of 20,297 identified, and that "more than 4,000 identified by DJB couldn't be traced on the ground" (Hindustan Times, 10 Jun 2025, on an NGT order of 30 May 2025) [S7].
- **Seals don't hold.** In 2026 the NGT saw photographs of sealed borewells in Civil Lines, Saraswati Vihar and Model Town that "could be operated very conveniently without removing the seal" [S9].
- **Enforcement is manual.** In *Deepak Singh v. CGWA* (OA 703/2022, order of 27 Jul 2023), the Delhi Chief Secretary's SOP of 12 Jun 2020 makes drawing groundwater without permission illegal. Detection and closure are run by SDM-led joint teams of DJB, the DISCOMs (power disconnection) and police; DPCC issued environmental-compensation notices of ₹30,000 per violator [S8].

**Recharge is mandated and subsidised, but not verified. This is the hook we build on.**
- Rainwater harvesting (RWH) is mandatory on plots of **≥100 m²**. DJB subsidises installation (up to 50 % or ₹25,000 for 100–499.99 m²; up to ₹50,000 for ≥500 m²). Functional systems earn a **10 % water-bill rebate (15 % with wastewater recycling)**; non-compliance carries a **1.5× bill penalty**, rising to disconnection [S11].
- DJB disbursed **₹204.46 crore in RWH rebates in 2017–2024**. In April 2026 the government announced **annual self-certification** that RWH systems work. The water minister said: *"Till now, there was a rule but no real checking. That will change. We will introduce a system of verification and accountability…"* [S11].
- Government buildings alone: RWH exists at 4,343 of 4,861 school/college sites and 2,564 of 3,598 other department sites [S11]. DJB plans **500 new structures and restoration of 1,000 non-functional ones** [S12].

**Monitoring today: our analysis of the public data [run].**
- India-WRIS lists **382 groundwater stations in Delhi** (CGWB 279, Delhi state GW 103), of which **196 are flagged telemetric** [S2, run].
- **185 telemetric (GPRS DWLR) stations** have data in the public API (CGWB 91, Delhi state 94). Readings come every **6 h** (median interval) [S3, run].
- The public telemetric record looks like this (snapshot of 4 Oct 2026; latest reading 4 Jun 2026):
  - only **46 of 185 telemetric stations have any 2026 reading**;
  - **23.3 % of 480,428 telemetric readings are exactly 0.000 m**, and 65 stations are >50 % zeros;
  - **17.4 % of 6-hourly slots are missing**;
  - **76.3 %** of readings are usable after removing zeros and implausible values (|v| > 200 m);
  - sign conventions are mixed: 66 stations report negative values, 55 positive.
- Where data are clean, the aquifer is visibly recharged by the monsoon. Across 79 stations, the median 2025 pre- to post-monsoon rise is **2.51 m** (10th–90th percentile 0.80–8.08 m) [run].
- Median depth to water across 117 clean stations is **7.7 mbgl**. The South district's station median is **38.4 mbgl** [run].
- Caveat: the per-station sign convention is resolved heuristically (no manual overlap after 2022), and the record is too short (2023–26) for long-term trends.

**What this means.** Delhi's groundwater governance has three paper-based loops:
1. illegal borewells identified but not traceable or not sealed;
2. RWH rebates paid against self-certification;
3. a telemetric network whose public stream is about one-quarter zeros and mostly stale.

The **cheapest loop to close with IoT, cooperatively and measurably, is loop 2**. Loop 3 is where the outcome shows up (does recharge raise the water table?), and our analytics can clean and use it. Loop 1 is adversarial; see §6 for why we don't lead with it.

## 2. What companies and agencies ship today

| Who | What ships | Measures / cadence | Price (opened page) | Gap for urban Delhi |
|---|---|---|---|---|
| **CGWB + Delhi state GW (India-WRIS)** [S2, S3] | GPRS DWLR piezometers | Level, every 6 h | — | Public stream is 23 % zeros and stale (§1); no recharge accounting; nothing at RWH structures |
| **Acorn Controls**, PZM-24B "CGWA-compliant" piezometer/DWLR [S18] (one product; not every CGWA logger) | Hydrostatic SS sensor, logger, optional GPRS/4G, "MeitY-approved cloud – updates twice daily" | Level, ±0.5 % FS, 365 × 2 readings/day memory, 5+ yr battery claimed | **≈ ₹38,000 / piece** | Built for compliance on extraction wells. Two readings a day cannot resolve storm recharge events, which take hours |
| **Pride Controls**, CGWA piezometer/flow-meter telemetry [S19] | GSM telemetry, IP67, 24 V AC | Flow / level for CGWA NOC holders | **≈ ₹38,900 / piece** | Mains powered and industrial; meters extraction, not recharge |
| **Solinst** (pro loggers) [S16] | Vented cable transducers | Level | not published on page opened | Their own guidance: "The biggest worry is keeping the vent tube dry… dampness [causes] erroneous barometric compensation." We avoid this with a sealed absolute sensor plus a well-head barometer |
| **RAKwireless RAK3172** [S20] | STM32WLE5CC LoRa/LoRaWAN module, LoRaWAN 1.0.3 Class A/B/C, works with TTN/ChirpStack | — | not shown in excerpt (UNVERIFIED) | Commodity radio we can use |
| RWH "smart" kits — leads only: zbotic.in "Rainwater Harvesting Monitor: Tank Level with Ultrasonic"; JIIT Noida "Low Cost Smart Ground System for Rainwater Harvesting… Using IoT" (ResearchGate) | Ultrasonic level + ESP32/NodeMCU + app/GSM | Tank or pit level | search summary only: ₹5,000–20,000 (**UNVERIFIED**) | They show a level. None we found computes **audited per-storm infiltration with uncertainty** or plugs into the DJB rebate workflow. (Absence of evidence ≠ evidence of absence; re-check before the pitch) |
| CGWA-compliance vendors — leads only: Kritsnam (Dhaara), FluxGen (AquaGen), Aavad, SenseIndia, Vision World Tech, Frinso | Flow meters + DWLR + cloud for NOC holders | — | **UNVERIFIED** (search summary) | Same as Acorn/Pride: extraction compliance for industry |

**Where we borrow and where we beat them.**
- *Borrow:* the hydrostatic SS probe and DWLR logging pattern (Acorn/CGWB), LoRaWAN modules (RAK), and the vent-free design lesson (Solinst).
- *Beat:* (1) event-resolution sampling only when it rains (minutes during storms, hours otherwise), so energy goes where the information is; (2) a calibrated pit **water balance** that turns stage into infiltration volume with an uncertainty band; (3) a verdict that DJB can attach to a rebate (verified / clogged / no-inflow / implausible); (4) a QC layer for the existing public DWLR data (zeros, gaps, sign) so the city-scale outcome can be read.

## 3. Data we can use now (all fetched tonight; see `components/data-ingest/`)

- **India-WRIS** station layer: ArcGIS REST, no key [S2].
- **India-WRIS** time series: `POST /Dataset/Ground Water Level` per district × agency, 5,000 rows a page, no key; 483,253 Delhi rows, 2015–2026 [S3, run]. Reuse is non-commercial with attribution, and Survey-of-India layers are not redistributed (r5 notes) [S21].
- **Open-Meteo historical archive** (reanalysis-based; **default model, not pinned**; checked 4 Oct: not identical to `models=era5`, see `eval/data/README.md`): daily 2010–2026 and hourly 2022–2026 rain, surface pressure and temperature for central Delhi [S5]. It is reanalysis, not a gauge, and smooths convective storms. The prototype adds a ₹-cheap tipping bucket or links to an IMD AWS.
- **Not yet obtained:** data.gov.in (CGWB) timed out from this network; IMD gridded rain (`imdlib`); USGS high-frequency wells. All are optional.

## 4. Analytics state of practice (what we use as baselines)

- **Hydrograph response models.** Pastas, the open-source transfer-function-noise modelling package (v2.0.0 installed from PyPI tonight), is the standard baseline for head = f(rain, ET, pumping). It is our hydro-twin baseline at DWLR stations. The paper-level citation (Collenteur et al., 2019) has not been opened tonight: **UNVERIFIED**.
- **Water-table-fluctuation (WTF) recharge.** Recharge ≈ Sy × Δh. We compute Δh per station from real data [run]; Sy for Delhi aquifers still needs a source (**UNVERIFIED**; the r1a worker died before reporting).
- **Recharge-structure performance.** Falling-head (recession) analysis of stage after inflow stops is textbook infiltration testing. Applying it per storm, from telemetry, with a learned stage–discharge relation and a mass balance, is the spike (ADR 001).
- **Sensor QC.** Range, flatline, spike and step tests are standard. Tonight's public DWLR profile shows they are needed at scale: 23 % zeros [run].
- **Pumping detection from 6-hourly DWLR (first principles).** A 6 h sampling interval puts the Nyquist period at 12 h, so pump cycles shorter than ~12 h are aliased. Only long-duration drawdown or a 24 h-cycle signal is visible. Our run finds a median 24 h harmonic amplitude of **0.02 m**, with the 90th percentile at **0.113 m** and the 99th at **0.463 m** [run]. Those stations are candidates for "zone-level pumping influence", **not** pump identification. The adversarial review agrees.

## 5. Hardware, power and connectivity (what's established vs what we assume)

- **Sensing (updated 4 Oct after the reviews).** A 0–5 m 4–20 mA stainless steel throw-in probe (DFRobot KIT0139). Datasheet: "Overall Accuracy: 0.5%", 12–36 V supply, IP68, 316L stainless steel (https://www.farnell.com/datasheets/3708809.pdf). Price Rs. 4,254.51 at element14 India (accessed 2026-10-04). That is ±25 mm per reading, or ±0.11 m³ worst case on a 2.25 m² pit's stage rise. Vent-tube moisture is a known failure mode of vented probes [S16]. An earlier draft used a 30-bar MS5837; that part is the wrong range and has been dropped.
- **Event scale (arithmetic, assumptions labelled).** A 100 m² roof (the RWH threshold [S11]) in a 50 mm storm with runoff coefficient 0.8 (**assumed**) yields 100 × 0.05 × 0.8 = **4.0 m³**.
- **Connectivity underground.** Antenna performance drops sharply below ground [S17]. Pits sit at grade under a lid, so we put the radio and antenna in the lid-mounted housing, store-and-forward locally, and uplink on LoRaWAN (RAK3172 [S20]) or NB-IoT/LTE-M. A link budget for Delhi needs measurement: **UNVERIFIED**, a Round-2 field test.
- **Power.** A community LoRa node built on the same radio class measured a 220 µA sleep floor and about 11 mAh/day [S22]. Our design target is much lower (MCU deep sleep, 15 min idle sampling, burst sampling only during rain). The battery-life estimate in `deliverables/prototype-plan.md` is labelled as an estimate.

## 6. Candidate problems and why we chose recharge verification

| Candidate | Physics/observability | Local pull | Adversarial risk | Verdict |
|---|---|---|---|---|
| Recharge verification (RWH pits/shafts) | Stage in a pit is directly observable. The drain rate (clogging) is measured; infiltration is a model-based estimate (a per-event band is planned; leaks out of the pit are unobservable) | ₹204 cr in rebates, self-certification since Apr 2026, minister asking for "verification and accountability" [S11]; 1,000 non-functional govt systems [S12] | Cooperative (the owner wants the rebate). Gaming is detectable against rainfall | **Hero** |
| Network QC + outcome twin (existing DWLR) | Real data available now [run] | 185 telemetric stations, ~¼ of readings zero | Low | **Secondary layer** (closes the loop: did the aquifer respond?) |
| Hidden-pumping detection from DWLR | 6 h sampling aliases pump cycles; confounded by legal pumping, barometric and tidal effects | Strong (20k+ illegal borewells [S6, S7]) | High: false accusations; not evidence-grade | Zone-level prioritisation at most; **don't claim pump identification** |
| Sealed-borewell tamper guard | Vibration/current/reed switches are bypassable | Strong (improper seals [S9]) | High: legal access, bypass, false alarms | Dropped from the pitch |
| Contamination sentinel (EC) | EC drifts and fouls; plumes travel slowly | Real (uranium/lead [S13]) | Medium | Future extension (EC channel on the same node) |
| Pipeline leakage | Distribution network, not the aquifer | Weak link to "underground water" | — | Out of scope |

## 7. Component innovation scan (lean-mode stand-in for `research/components/*.md`)

Scores are 1–5 for judged impact, novelty, feasibility by 1 Dec, measurability and demoability. Totals are out of 25.

| Component | Best existing practice | Innovation candidate | Scalar metric | I | N | F | M | D | Total |
|---|---|---|---|---|---|---|---|---|---|
| sensor-front-end | Vented transducer or ultrasonic | 0–5 m vented throw-in probe (KIT0139) with a desiccant vent end, stilling tube, silt guard; mandatory rain gauge (updated 4 Oct) | stage RMSE vs reference (mm) | 3 | 2 | 5 | 5 | 4 | 19 |
| edge-firmware | Fixed-interval logging (e.g. 2/day [S18]) | Rain- and stage-triggered burst sampling, delta packing, signed log | mAh/day at equal event-volume error | 3 | 3 | 4 | 5 | 3 | 18 |
| telemetry-link | GPRS | LoRaWAN/NB-IoT from a lid antenna + store-and-forward | % of events delivered ≤ 24 h | 3 | 2 | 4 | 5 | 3 | 17 |
| ingest + QC | Range/flatline checks | QC tuned on real DWLR pathologies (zeros, sign, gaps) | F1 on injected faults; % usable data | 4 | 3 | 5 | 5 | 4 | 21 |
| **recharge-verifier** (spike) | Manual inspection / self-certification | Per-storm water balance with learned stage–discharge, clogging index, verdict + uncertainty | **event infiltration-volume error (MdAPE)**; clogging F1 | 5 | 5 | 4 | 5 | 5 | **24** |
| hydro-twin (outcome) | Pastas TFN | Pastas + QC + WTF recharge per ward, linked to verified structures | holdout NSE; recharge mm per monsoon | 4 | 3 | 4 | 4 | 4 | 19 |
| inspection-queue | Complaint-driven inspections | Rank by m³ at stake × confidence; rebate verdicts | precision@k on simulated fleet | 4 | 3 | 5 | 4 | 4 | 20 |
| dashboard | Generic IoT dashboards | Operator inbox + citizen view; provenance labels | task time in 5-task test | 4 | 2 | 5 | 3 | 5 | 19 |

**Spike choice (ADR 001):** recharge-verifier, plus data-integrity work (QC + signed logs) as the second spike.

## Sources (opened)
- [S1] Official statement: `_briefs/innovatex.txt` (Techfest 2026-27 InnovateX).
- [S2] India-WRIS/NWIC ArcGIS layer: https://arc.indiawris.gov.in/server/rest/services/NWIC/GroundwaterLevel_Stations/MapServer/0 (queried 2026-10-04; maintained, production).
- [S3] India-WRIS dataset API: `POST https://indiawris.gov.in/Dataset/Ground%20Water%20Level?stateName=Delhi&districtName=…&agencyName=…` (queried 2026-10-04; production).
- [S5] Open-Meteo historical archive (default model, not pinned; not identical to ERA5 as checked 4 Oct): https://archive-api.open-meteo.com/v1/archive (queried 2026-10-04).
- [S6] The Hindu, "Delhi's illegal borewell boom running on empty", 20 Apr 2025: https://www.thehindu.com/news/cities/Delhi/delhis-illegal-borewell-boom-running-on-empty/article69469292.ece
- [S7] Hindustan Times, "NGT seals illegal borewell in central Delhi", 10 Jun 2025: https://www.hindustantimes.com/cities/delhi-news/ngt-seals-illegal-borewell-in-central-delhi-101749492629182.html
- [S8] NGT OA 703/2022, *Deepak Singh v. CGWA*, order 27 Jul 2023 (IndianKanoon): https://indiankanoon.org/doc/19049265/
- [S9] The Bar Bulletin, NGT on improper sealing (case listed 1 Apr 2026): https://thebarbulletin.com/ngt-delhi-illegal-borewells-improper-sealing-report/
- [S10] BharatSpeaks (secondary), 153 illegal borewells untraceable, Jan 2026: https://bharatspeaks.com/ngt-report-flags-major-data-gaps-as-153-illegal-borewells-remain-untraceable/
- [S11] Hindustan Times, "Delhi makes rainwater harvesting mandatory; penalties for violators", 21 Apr 2026: https://www.hindustantimes.com/cities/delhi-news/delhi-makes-rainwater-harvesting-mandatory-penalties-for-violators-101776711439024.html
- [S12] Indian Express, Delhi RWH campaign (2026): https://indianexpress.com/article/cities/delhi/delhi-government-rainwater-harvesting-campaign-groundwater-recharge-djb-10718827/
- [S13] New Indian Express, 2 Dec 2025: https://www.newindianexpress.com/cities/delhi/2025/Dec/02/high-levels-of-toxic-chemicals-found-in-delhis-groundwater-study
- [S14] CNA, Delhi land subsidence and groundwater (2025): https://www.channelnewsasia.com/asia/india-new-delhi-sinking-land-subsidence-groundwater-extraction-5499456
- [S15] BusinessLine/Bloomberg, 29 Oct 2025: https://www.thehindubusinessline.com/news/real-estate/indias-cities-are-sinking-under-their-own-weight-scientists-sound-alarm/article70215337.ece
- [S16] Solinst, "Vented Cable Design, Proper Use & Maintenance": https://www.solinst.com/onthelevel-news/water-level-monitoring/water-level-datalogging/aquavent-vented-cable-design/
- [S17] EEVblog forum, "Underground LoRa device": https://www.eevblog.com/forum/projects/underground-lora-device/
- [S18] Acorn Controls, Piezometer/DWLR PZM-24B: https://www.acorncontrols.com/piezometer.html (opened 2026-10-04; "Approx. Price: Rs 38,000 / Piece")
- [S19] Pride Controls, telemetry flow meter / CGWA piezometer telemetry: https://www.pridecontrols.co.in/telemetry-flow-meter.html (opened 2026-10-04; "Approx. Rs 38,900 / Piece")
- [S20] RAKwireless RAK3172 product page: https://store.rakwireless.com/products/wisduo-lpwan-module-rak3172
- [S21] `india-water-data` client (provenance of the WRIS dataset API): https://github.com/DrJagadeeshG/india-water-data
- [S22] MichielBruijn/lora-humidity-sensor (measured sleep floor 220 µA; ≈11 mAh/day): https://github.com/MichielBruijn/lora-humidity-sensor
- [S23] CGWB, *National Compilation on Dynamic Ground Water Resources of India, 2025*: https://cgwb.gov.in/cgwbpnm/publication-detail/1741 (PDF: https://cgwb.gov.in/cgwbpnm/download/1741), §7.32 Delhi. Opened 2026-10-04 by the primary-source checker.
- [run] `eval/realdata_profile.py` → `eval/results/realdata_profile.json`. Reproduce: `innovatex-t1-groundwater/.venv/bin/python innovatex-t1-groundwater/components/data-ingest/fetch_delhi.py && innovatex-t1-groundwater/.venv/bin/python innovatex-t1-groundwater/eval/realdata_profile.py`.

## Gaps / UNVERIFIED (to close before 9 Oct)
- ~~CGWB 2025 assessment for Delhi~~ closed: 92.10 % stage of extraction [S23]. Still open: primary DJB/Assembly source for the ₹204.46 cr figure, which is only secondary (HT citing DJB data). See `research/primary-source-checks.md`.
- Delhi aquifer parameters (Sy, T) from the CGWB NAQUIM report. They are needed for WTF recharge in mm.
- ~~BOM prices~~ closed: verified per-node subtotal ₹11,166.18 (`deliverables/prototype-plan.md` §3). Still unpriced: tube, sock, potting, cable, boost converter, antenna.
- What RWH-monitoring products really do: open the zbotic/JIIT/Kritsnam/FluxGen pages.
- DJB tariff slabs and tanker prices, to value water in ₹.
- X/Twitter: worker searches with `site:x.com` returned no relevant results; no X posts are cited.

## Status note (4 Oct 2026, 12:30 IST, after the final-deck review)
Some sections above are historical. Current statements override them:
- **Policy:** RWH functionality certificates are issued after inspection with periodic renewal. Annual self-certification is *being planned*; the 1.5× penalty "may attract" (HT, 21 Apr 2026). Older lines here saying "self-certification since Apr 2026" overstated this.
- **Rain data:** every evaluator and the demo use Open-Meteo archive rain, default model, not ERA5-pinned. The hourly input is frozen in `eval/data/`.
- **Sensor:** a vented 0–5 m probe (KIT0139), replacing the earlier "sealed absolute sensor + barometer" idea.
- **Buyer:** DJB's restoration programme is a *prospective* pilot customer; no contact yet.
