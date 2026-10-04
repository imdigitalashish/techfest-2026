# Prototype plan — DustLedger (working prototype due 1 Dec 2026)

*Rendered from `deliverables/src/prototype-plan.md`; revised after two cross-model reviews (`reviews/`). Architecture: [`architecture/components.md`](../architecture/components.md). Spike: [ADR 001](../architecture/adr/001-spike.md). Prices: listings the lead opened in a browser on 4 Oct 2026, 15:34–15:35 IST (`deliverables/bom/bom.csv`). Power: datasheets the lead opened (`deliverables/bom/power_budget.py`).*

## 1. What we build
- **4 fence-line nodes** (C1) on the site boundary at ~2.5–3 m, one per side, so that whatever the wind direction, some nodes are upwind and some downwind. Each node: Sensirion SPS30 (PM1/2.5/4/10 + size bins), SHT30 temperature/RH, ESP32-S3, SX1262 LoRa radio, 10 W panel + LiFePO4 battery + MPPT charger, IP65 box (a radiation shield and inlet are still to be sourced).
- **1 wind sensor** (C2), speed + direction in one head, on a 3–4 m mast clear of the building's wake.
- **1 gateway** (C3): ESP32-S3 + SX1262 (receives the nodes) + A7670C LTE Cat-1 board (uploads), on site power (ASSUMPTION: site offices have mains power).
- **1 misting line** (C8/C9): a 12 V misting kit (pump + 8 nozzles) switched by a relay, with a Hall-effect flow meter so every litre is logged. A 12 V solenoid valve is the option for mains-water sites.
- **Software** (C4–C7, C10–C12): ingest + QA, calibration, attribution, controller, ledger and dashboards behind the typed contracts in `architecture/contracts/`.

## 2. Parts list (one site kit)
{{table:bom}}

**Kit parts total: ₹{{n:bom_kit}}** (4 nodes ₹{{n:bom_nodes4}} · wind ₹{{n:bom_wind}} · gateway ₹{{n:bom_gateway}} · misting ₹{{n:bom_actuator}}). Single-unit retail, incl. GST. **Not included:** 5 V buck converters, cabling and glands, masts and mounting, radiation shields, SIM + data plan, gateway power supply, installation labour, reference co-location, maintenance. These are UNVERIFIED and must be priced before any "installed cost" claim. Notes: the relay listing was out of stock (any 5 V relay module works); the SX1262 module is listed for 868/915 MHz, so its suitability for India's IN865 band is UNVERIFIED; the wind sensor's stock status wasn't shown, and an in-stock alternative is listed at a higher price.

**For scale** (fact F6): one construction-site violation costs {{v:F6|₹1 lakh to ₹2 lakh}} under CAQM's 2024 schedule as reported (doubled under GRAP; the current operative order is UNVERIFIED). This says nothing about lifetime cost or willingness to pay, both UNVERIFIED.

## 3. Power budget (per node) — a model estimate, not a measurement
{{table:power}}

Datasheet sources: Sensirion SPS30 v0.9 (60 mA average in measurement mode, fact F20), Espressif ESP32-S3 v2.1 ({{v:F21|13.2}} mA in modem-sleep at 40 MHz, fact F21), NASA POWER climatology for Delhi (December worst month, fact F22). Bench-measure the real draw in the first build week.

## 4. Connectivity
- Nodes → gateway: LoRa (SX1262). India's licence-exempt band is IN865; whether this module and our duty cycle comply is UNVERIFIED — check before deployment. Fallback: Wi-Fi from the gateway when nodes are within range.
- Gateway → cloud: LTE Cat-1 (A7670C) with store-and-forward on the ESP32 flash, so outages backfill.

## 5. Build steps and dates (every field step is approval-dependent)
| When | Step | Evidence it produces |
|---|---|---|
| 5–12 Oct | Order parts from two vendors per item; software work continues on the replay (software only) | order receipts; `results.tsv` |
| 13–19 Oct | Bench-build one node + gateway; firmware writes the `NodeReading` / `WindReading` contracts with on-device signing; measure real current draw; then build the other three nodes | power bench log; four working nodes |
| 20–26 Oct | Four nodes side by side (inter-node agreement, metric C1); reference co-location if a slot is granted | co-location dataset |
| 27–31 Oct | Real construction-site trial **only if a site and approvals are in place**: the reported plan prohibits dust-generating works from {{v:F1|Nov 1 – Jan 31}} | first real fence-line estimates |
| 1–17 Nov | Approved, safety-controlled dust-source test (e.g. chalk dust + fan at a known spot, with the institution's approval and safety controls): ring + wind + misting on/off in randomised blocks, an independent reference measurement if available, metered water | recovery of a known source, abstention rate, litres used, misting effect vs wetting the sensor |
| 18–25 Nov | No user-dependent work (IIT Delhi end-semester exams 19–25 Nov) | — |
| 26–30 Nov | Report: functionality evidence, cost, implementation and scalability plans; impact only from measured numbers; a controlled test is never called field validation | final report |
| 15–18 Dec | Finals demo: a ring around a dust source on stage (if the venue allows); only the downwind nodes light up; misting triggers | live demo |

## 6. What is simulated now (labelled)
- The construction site, its emissions, plumes, sensor faults and the neighbour/road confounders (`components/attribution/autoresearch/eval_v2.py`, `provenance = SIMULATED`).
- **Real:** background PM (CPCB/DPCC monitors via the OpenAQ archive), meteorology (ERA5 via Open-Meteo), CAMS fields (reference only).
- **Not modelled at all:** the misting effect on dust. No reduction figure exists until the trial.

## 7. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Optical sensors respond differently to coarse dust than to ambient air (CSTEP: qualitative) | Differential use; dust test + reference co-location before any claim; the size bins allow a size-aware correction |
| Calm winter winds (ERA5 grid: below 0.5 m/s in {{n:calm_lt05_winter_pct}}% and below 1 m/s in {{n:calm_lt10_winter_pct}}% of Nov–Jan hours; site-level calm not yet measured) | Abstain below 0.5 m/s and report the abstention rate; never treat "inconclusive" as clean; a swirling-wind check is planned |
| No real site or approvals before 1 Nov | Approved, safety-controlled dust-source test with the same hardware, reported as a controlled test |
| Panel soiling at a dusty site | Weekly wipe; solar derate assumption in the power budget; measure |
| Vendor delays / stock-outs | Order by 12 Oct; alternatives listed in the parts table |
| LoRa band compliance | Verify IN865 before field use; Wi-Fi fallback |
