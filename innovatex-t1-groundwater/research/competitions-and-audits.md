# InnovateX Theme 1 — Competitions and audits research

Context: Techfest 2026 (IIT Bombay) InnovateX Theme 1, IoT-Based Underground Water Management, Delhi zonal pitch on 2026-10-10. Research date/access date: 2026-10-04 IST.

Zero-hallucination note: cited URLs were opened before inclusion. SIH official archive coverage was poor in this time-box, so uncertain items are marked **UNVERIFIED** rather than filled from memory.

## 1. Smart India Hackathon groundwater problem statements (2023–2025)

| Year | PS ID | Title | Organisation | Opened official evidence | Description summary | Publicly described solutions |
|---|---:|---|---|---|---|---|
| 2023 | — | — | — | `https://www.sih.gov.in/sih2023PS` returned 404. Web search for `site:sih.gov.in` + groundwater/DWLR/CGWB found no relevant official result. | No official groundwater/DWLR PS confirmed in this time-box. | None confirmed from official SIH source. |
| 2024 | — | — | — | `https://www.sih.gov.in/sih2024PS` opened; direct text scan found no `ground`, `water`, `Jal`, `CGWB`, or `DWLR` occurrences in the visible HTML/table content. | No official groundwater/DWLR PS confirmed in visible 2024 SIH page content. | None confirmed from official SIH source. |
| 2025 | **SIH25068 (UNVERIFIED as official SIH page)** | **Real-time Groundwater Resource Evaluation using DWLR Data** | **Ministry of Jal Shakti / CGWB (UNVERIFIED as official SIH page)** | `https://www.sih.gov.in/sih2025PS` opened, but the visible page showed `0` hardware and `0` software statements and did not expose PS rows in the fetched HTML. The PS ID/title/org were repeatedly found in student repos, not in a directly opened `sih.gov.in` record. | Student repos describe the task as ingesting Digital Water Level Recorder (DWLR) telemetry for real-time groundwater resource evaluation, CGWB-style risk classification, trend forecasting, alerts and dashboards. Treat this as a strong public-trace item, not as an official SIH citation. | Several public prototypes: JalDrishti, Smart Groundwater DSS, flowState, SIH-DWLR data processing; no official winner page confirmed. |

Decision relevance: expect SIH/DWLR competitors to pitch a software-heavy dashboard/forecasting layer over DWLR data rather than a field-hardened underground IoT node.

## 2. GitHub student projects

Opened GitHub repo pages/search API results and recorded repo URL, stars, last push/commit proxy (`pushed_at`), and build pattern.

| Repo | Stars | Last push | What they built | Likely weakness / note |
|---|---:|---|---|---|
| https://github.com/pleasingsunlight/flowState | 4 | 2026-09-24 | SIH-25 project for “real-time groundwater data tracking from DWLR data”; scalable/impact dashboard framing. | Looks data-app oriented; field sensing/calibration/power not evidenced in opened search result. |
| https://github.com/Swapnaneel07/JALDRISTHI_SIH2026_INTERNAL | 9 | 2026-09-03 | “AI-powered groundwater monitoring, forecasting, and intervention planning”; Streamlit dashboard, XGBoost risk engine, trend/anomaly pipeline, Buldana pilot dataset. | Strong analytics pitch but depends on datasets/model files; not a deployed borewell sensor design. |
| https://github.com/Debddj/JalDrishti | 0 | 2026-08-24 | README: “Real-time Groundwater Resource Evaluation & Advisory Platform using DWLR Telemetry”; badge says SIH 2025 problem statement 0068 / Ministry of Jal Shakti. | Good framing; likely software telemetry simulator/dashboard, not proof of rugged edge telemetry. |
| https://github.com/Kirubanithi0303/SIH-Project | 0 | 2025-10-31 | Search result title: “Real-Time Groundwater Resource Evaluation using DWLR Data.” | Could not reopen repo page reliably; keep as public-trace item only. |
| https://github.com/AjayrajC/Groundwater-monitoring-using-ESP32 | 0 | 2025-01-10 | README: ESP32 + HC-SR04 ultrasonic sensor, Blynk app, Google Sheets logging, calculates water usage/yield. | Classic hackathon pattern: Wi-Fi/Blynk/Sheets; no calibration chain, borewell acoustics, enclosure, power budget, telemetry fallback, pressure/barometric correction, or maintenance plan evident. |
| https://github.com/avinash0045/Automation-of-smart-Ground-water-recharge-system-IOT-Sensors-Esp32-Lora | 0 | 2026-09-23 | “Smart Artificial Groundwater Recharge (AGWR)” with IoT sensors, ESP32, LoRa, gravity filtration, real-time water-quality monitoring. | Better connectivity story (LoRa) but README content opened was only a short concept; implementation depth unclear. |
| https://github.com/alankrithshastry/Secure-Groundwater-Extraction-Monitoring-System | 0 | 2026-06-09 | README: groundwater extraction monitoring using ultrasonic sensors, anomaly detection, cybersecurity/tamper detection. | Interesting security angle; ultrasonic still likely fragile in borewell geometry unless calibrated/validated. |
| https://github.com/anirudhnss/AquaGuard-AI | 1 | 2026-07-23 | ESP32 borewell motor protection: phase/voltage/current faults, HC-SR04 water-level monitoring, LCD, Blynk Wi-Fi dashboard, offline hotspot fallback. | Stronger hardware demo, but water-level sensing is still threshold-centric and local; not groundwater resource evaluation or aquifer analytics. |

Typical student solution pattern: ESP32/Arduino + HC-SR04 ultrasonic or generic water-level sensor + Wi-Fi/Blynk/ThingSpeak/Google Sheets + web/mobile dashboard + threshold alerts; SIH25068-style teams instead build FastAPI/Streamlit/React dashboards over DWLR/synthetic telemetry with ML forecasting, GIS maps and risk labels.

Common weaknesses to beat:
- Ultrasonic-in-borewell assumptions: no stilling tube design, condensation/foam/echo/pipe-diameter handling, datum calibration, temperature/barometric compensation, or manual dip validation.
- Communications: Wi-Fi-first demos; weak rural fallback, store-and-forward, packet-loss handling, device identity and tamper evidence.
- Power: few show solar/battery sizing, duty cycling, sleep current, six-hour sampling economics, or monsoon enclosure/IP rating.
- Analytics: threshold alerts/forecast plots without hydrogeological context, observation-well density, recharge/extraction attribution, NOC compliance workflow, data QA flags, or uncertainty bands.
- Governance fit: little linkage to CGWB WIMS/India-WRIS, National Hydrograph Monitoring System, CGWA NOC conditions, or audit-observed enforcement gaps.

## 3. Techfest InnovateX past editions (2024–2025)

- `https://techfest.org/competitions` and `https://techfest.org/competitions/india71100` opened as a React single-page shell titled “Techfest | IIT Bombay” with metadata for Techfest 2026; the initial HTML did not contain `InnovateX`, `winner`, `AI for Technology`, `EV Infra`, or `India @71` text.
- Web search pointed to official `techfest.org/competitions` pages for current competition themes (AI for Technology Readiness, EV Infra & Green Mobility AI Challenge, UAV-X, CycloProp, Code Auditor, India @71/100), but I could not verify those details directly in opened page text because the content is loaded client-side from a large JS bundle that timed out during this time-box.
- No official 2024–2025 InnovateX winners page was confirmed. Marking past-edition winners/themes as **UNVERIFIED**.

## 4. Official audits / Parliament

### CAG — Performance Audit on “Ground Water Management and Regulation”

Source opened: archived raw PDF of CAG Report No. 9 of 2021: `https://web.archive.org/web/20220722210629id_/https://cag.gov.in/uploads/download_audit_report/2021/Report%20No.%209%20of%202021_GWMR_English-061c19df1d9dff7.23091105.pdf`. Live `cag.gov.in` fetch failed with transport/DNS errors in this session, so the Wayback copy was used; it is the archived original CAG PDF URL. Report year: 2021. Type: official audit report.

Short verified quotes extracted from the opened PDF:

- **Observation-well density shortfall, para 2.4 / executive summary:** “Against the proposed number of 50,000 observation wells (by the end of the XII Plan period i.e. 2012-17) to measure ground water level, a network of only 15,851 observation wells were being monitored as of 31 March 2019.”
- **DWLR/telemetry delay, para 2.4 / chapter 2:** “It was observed that as of March 2020, CGWB was still planning and was yet to undertake real time Ground Water monitoring through DWLRs and Telemetry which indicated that progress in this area was not as per targets of the GWMR Scheme.”
- **Assessment cadence gap, para 2.3:** “CGWB did not carry out this assessment for 2015 resulting in a gap of four years in assessment between 2013 and 2017.”
- **Piezometer/NOC data gap, section 3.6:** “Audit observed that no details regarding installation of piezometers, data on water level, change in water level, etc. were received from the project proponents. Consequently, piezometers were neither brought into the National Hydrograph monitoring system of CGWB, nor validated.”
- **NOC renewal enforcement, para 3.5 / 3.10.1:** “in 474 cases, renewal of NOC was due during 2013-18 but the project proponents did not apply for renewal. CGWA did not take any action under section 15 of the Environment (Protection) Act, 1986 against these project proponents.”
- **Show-cause notices, para 3.10.1:** “During 2013-18, CGWA had issued show cause notices to only 99 project proponents.”
- **Field non-compliance, para 3.10.2:** audit found “illegal extraction of ground water, non-installation of water flow meters, improper maintenance of rainwater recharge structures, absence of monitoring of water quality data, etc.”

Design implication: don’t pitch “sensor + dashboard” only. Pitch a monitoring system that explicitly fixes audit failures: denser/cheaper validated observation points, six-hour telemetry with offline buffering, calibration and data-quality flags, project-proponent compliance evidence, tamper logs, and integration exports for WIMS/India-WRIS/CGWA workflows.

### CGWB current monitoring baseline

Source opened: `https://cgwb.gov.in/en/ground-water-level-monitoring`.

- CGWB says it monitors groundwater levels “four times in a year” and has “about 25000 monitoring stations called ‘National Hydrograph Network Stations (NHNS)’”.
- CGWB says it has initiated automatic high-frequency monitoring under NHP: “Total DWLRs proposed under NHP is 5260”; “six hourly water level data” is transferred to WIMS and shared via India-WRIS.
- CGWB also says 7,000 PIB piezometers and 2,000 GWMR piezometers are envisaged, fitted with DWLR and telemetry.

Design implication: benchmark against six-hour DWLR telemetry and WIMS/India-WRIS, not only app alerts.

### Parliamentary Standing Committee / sansad.in

- A research sub-check attempted `sansad.in` and `eparlib.nic.in` Standing Committee reports. Correct-looking Water Resources Demands for Grants 2025–26 report was identified, but exact DWLR/telemetry/NOC quotes could not be re-opened reliably in the time-box. No parliamentary quote is included as verified.

## What the typical student team will pitch (and how to beat it)

They will probably pitch one of two things:

1. **Hardware demo:** ESP32/Arduino + ultrasonic sensor dropped into a borewell/tank + Wi-Fi/Blynk/ThingSpeak/Google Sheets + threshold alert.
2. **SIH25068-style software demo:** DWLR/synthetic CSV ingestion + Streamlit/React dashboard + GIS heatmap + ML forecast/anomaly detection + PDF reports.

Beat it by grounding InnovateX Theme 1 in official failure modes:

- **Measurement credibility:** pressure transducer or radar/ultrasonic with stilling tube, surveyed datum, manual dip calibration workflow, temperature/barometric compensation, drift detection, and sensor-health flags.
- **Rural telemetry:** LoRaWAN/NB-IoT/2G fallback, store-and-forward, signed packets, tamper-open detection, local OLED/QR maintenance mode, six-hour sampling aligned to CGWB DWLR cadence.
- **Power and deployment:** solar/battery budget, sleep-current calculation, IP-rated enclosure, lightning/surge plan, service interval, Delhi pilot BOM.
- **Audit-fit dashboard:** missing-data heatmap, observation-well density planner, CGWA NOC condition checklist, flow-meter/piezometer evidence upload, renewal/non-compliance alerts, WIMS/India-WRIS export schema.
- **Analytics beyond thresholds:** uncertainty-banded trends, rainfall/recharge lag, pump/extraction correlation, anomaly classes (`sensor fault`, `telemetry gap`, `rapid drawdown`, `recharge event`), and “why this alert matters” narratives for officials.

## Sources

- `https://www.sih.gov.in/sih2024PS` — Smart India Hackathon 2024 Problem Statements page, accessed 2026-10-04, type: official competition page.
- `https://www.sih.gov.in/sih2025PS` — Smart India Hackathon 2025 Problem Statements page, accessed 2026-10-04, type: official competition page.
- `https://www.sih.gov.in/sih2023PS` — attempted SIH 2023 Problem Statements URL, returned 404, accessed 2026-10-04, type: official competition URL attempt.
- `https://github.com/pleasingsunlight/flowState` — GitHub repository, accessed 2026-10-04, type: student project.
- `https://github.com/Swapnaneel07/JALDRISTHI_SIH2026_INTERNAL` — GitHub repository, accessed 2026-10-04, type: student project.
- `https://github.com/Debddj/JalDrishti` — GitHub repository, accessed 2026-10-04, type: student project.
- `https://github.com/Kirubanithi0303/SIH-Project` — GitHub repository/search result, accessed 2026-10-04, type: student project.
- `https://github.com/AjayrajC/Groundwater-monitoring-using-ESP32` — GitHub repository, accessed 2026-10-04, type: student project.
- `https://github.com/avinash0045/Automation-of-smart-Ground-water-recharge-system-IOT-Sensors-Esp32-Lora` — GitHub repository, accessed 2026-10-04, type: student project.
- `https://github.com/alankrithshastry/Secure-Groundwater-Extraction-Monitoring-System` — GitHub repository, accessed 2026-10-04, type: student project.
- `https://github.com/anirudhnss/AquaGuard-AI` — GitHub repository, accessed 2026-10-04, type: student project.
- `https://techfest.org/competitions` — Techfest IIT Bombay competitions SPA shell, accessed 2026-10-04, type: official competition page.
- `https://techfest.org/competitions/india71100` — Techfest IIT Bombay competition route SPA shell, accessed 2026-10-04, type: official competition page.
- `https://web.archive.org/web/20220722210629id_/https://cag.gov.in/uploads/download_audit_report/2021/Report%20No.%209%20of%202021_GWMR_English-061c19df1d9dff7.23091105.pdf` — CAG Report No. 9 of 2021, Performance Audit on Ground Water Management and Regulation, accessed 2026-10-04, type: official audit report archived from CAG URL.
- `https://cgwb.gov.in/en/ground-water-level-monitoring` — CGWB Ground Water Level Monitoring page, accessed 2026-10-04, type: official government technical page.

## Gaps / UNVERIFIED

- Official SIH page for **SIH25068** was not directly retrieved from `sih.gov.in`; ID/title/org are supported by multiple public student repos but remain **UNVERIFIED as official SIH**.
- No SIH 2023/2024 groundwater/DWLR problem statement was confirmed from official SIH pages.
- No official SIH winning solution page was found/opened.
- Techfest InnovateX 2024–2025 winners/themes were not verified from official page text; current Techfest site is a client-rendered SPA and the JS bundle fetch timed out.
- Parliamentary Standing Committee exact quotes on DWLR/CGWB/NOC enforcement remain unverified; retry `sansad.in`/`eparlib` later with a stable PDF fetch.
