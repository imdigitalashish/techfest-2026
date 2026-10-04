# Prototype plan — DustLedger (working prototype due 1 Dec 2026)

*Draft v1, 4 Oct 2026. Architecture: [`architecture/components.md`](../architecture/components.md). Spike: [ADR 001](../architecture/adr/001-spike.md).*

> **Prices: UNVERIFIED.** The BOM research agent died on network errors, and Indian vendor sites blocked scripted lookups tonight (robu.in 403, robocraze 429, electronicscomp had no SPS30 listing). No price below is a fact yet. Each line names the part and where to buy it; filling sourced ₹ prices with URL and date is task #1 once lean mode lifts. We won't put a ₹ total on a slide until then.

## 1. What we build (physical)
- **4 fence-line nodes** (C1), on the site boundary at ~2.5–3 m height (breathing zone above hoarding level), placed at the four compass sectors, or at least one node upwind and two downwind of the prevailing winter wind (NW in Delhi winter: **UNVERIFIED**, to check from ERA5 on disk).
- **1 wind station** (C2) on a 3–4 m mast, clear of the building's wake.
- **1 gateway** (C3): LTE Cat-1 + SD buffer. The nodes talk to it over LoRa or Wi-Fi.
- **1 misting controller** (C8/C9): relay/SSR → pump or solenoid on 1–2 misting lines along the dustiest boundary, with a flow meter.
- **Software** (C4–C7, C10–C12): FastAPI ingest + Postgres/Parquet, attribution service, ledger, dashboard (web; supervisor view in Hindi/English).

## 2. Bill of materials (per 4-node site kit)
| Subsystem | Item | Part (candidate) | Qty | Key spec to verify (datasheet) | Unit ₹ | Source |
|---|---|---|---|---|---|---|
| Node ×4 | PM sensor | Sensirion SPS30 (or SEN55/SEN66), exposes number bins | 4 | PM10 measured or *estimated*? lifetime; fan cleaning | UNVERIFIED | robu.in / evelta.com / mouser.in |
| Node ×4 | T/RH | Sensirion SHT40 | 4 | ±1.8 % RH | UNVERIFIED | same |
| Node ×4 | MCU | ESP32-S3 dev board | 4 | deep-sleep current | UNVERIFIED | same |
| Node ×4 | Radio | LoRa SX1262 module (IN865) or Wi-Fi | 4 | IN865 duty-cycle rules | UNVERIFIED | same |
| Node ×4 | Power | 10 W solar panel + 12 V LiFePO4 + MPPT charger | 4 | autonomy in fog weeks | UNVERIFIED | same / amazon.in |
| Node ×4 | Housing | IP65 ABS box + louvred radiation shield + inlet | 4 | 50 °C ambient | UNVERIFIED | local |
| Wind | Anemometer + vane | cup anemometer + wind vane (pulse/analog) | 1 | start-up speed ≤ 0.5 m/s (needed for calm-wind abstention) | UNVERIFIED | robu.in / indiamart |
| Gateway | LTE Cat-1 | SIMCom A7670C + ESP32 + microSD + RTC | 1 | Jio/Airtel band support | UNVERIFIED | same |
| Actuator | Pump/solenoid + nozzles | 12/24 V misting pump or mains solenoid on site water; 0.2–0.3 mm nozzles; inline filter | 1 line | droplet size vs PM10 capture (to research) | UNVERIFIED | indiamart |
| Actuator | Flow meter + relay | Hall-effect flow sensor + SSR/relay | 1 | ±3 % flow | UNVERIFIED | robu.in |
| QA | Reference co-location | 1–2 weeks next to a DPCC/CPCB CAAQMS (permission needed) or IIT Delhi's reference instrument | — | — | — | **Needs from user** |

**Commercial yardsticks** (from opened sources): CAQM's flat ₹5 lakh fine per large Delhi site, and ₹7,500 per missing anti-smog gun per 5,000 m² (landscape §2). Prices of commercial dust monitors (Aeroqual, Oizom, Airveda): **UNVERIFIED** (none public on the pages opened).

## 3. Power budget (to fill from datasheets)
Per node: PM sensor fan at a duty cycle (e.g. 30 s on / 30 s off for 1-min means) + ESP32 + LoRa bursts. Solar sizing needs Delhi winter irradiance (fog and smog cut it): fetch NASA POWER or Global Solar Atlas values (**UNVERIFIED**). Until then, design for ≥ 3 days of battery autonomy.

## 4. Build steps
1. **Now – 12 Oct (software, no hardware):** replay harness for C6 attribution: real CPCB 15-min PM10 background (OpenAQ archive, on disk) + real wind + simulated plumes and sensor faults (labelled SIMULATED). Baseline: single-pair subtraction. Then the spike: ring + self-calibration + abstention + tamper flags, with an autoresearch ratchet on increment MAE.
2. **13–25 Oct:** order parts; bench-build one node and the gateway; firmware for `NodeReading`/`WindReading` contracts with on-device signing.
3. **26 Oct – 8 Nov:** build 4 nodes; a co-location week with all four side by side (inter-unit precision, metric C1); a reference co-location if a CAAQMS or IIT Delhi instrument is available.
4. **9–17 Nov:** field trial at a partner construction site (or a controlled dust source: a sand pile + leaf blower on campus): ring + wind + misting line; record increment with misting off/on (alternating days) and water used. *(User exams 19–25 Nov: nothing user-dependent in that window.)*
5. **26–30 Nov:** report: functionality evidence, cost, implementation and scalability plans, impact assessment from trial numbers.
6. **15–18 Dec finals:** live demo: a ring around a dust source on stage (fan + talc or chalk dust in a box), the dashboard lighting up only for the downwind nodes, misting triggering automatically.

## 5. What is simulated now (labelled)
- Fence-line nodes, wind station and actuator: `provenance="SIMULATED"` generators that write the same contracts as the hardware will.
- Site plumes (Gaussian dispersion with stability classes) and sensor faults (slope, offset, humidity growth, drift, spray events).
- **Real:** background PM (CPCB/DPCC monitors via the OpenAQ archive), meteorology (ERA5 via Open-Meteo), CAMS fields (reference only).

## 6. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Sensors under-read coarse construction dust | Differential use; check with a reference co-location; bins → size-aware correction; consider a PM10-specific sensor (OPC class) for one node |
| Calm winds in winter | Abstain + report the abstention rate; ring geometry; night-time accumulation analysis |
| No partner site by mid-Nov | Controlled dust-source trial on campus (labelled), still with real sensors |
| Vendor delays | Order by 20 Oct; two vendors per part |
