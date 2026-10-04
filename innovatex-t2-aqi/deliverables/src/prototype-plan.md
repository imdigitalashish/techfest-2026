# Prototype plan — DustLedger (working prototype due 1 Dec 2026)

*Rendered from `deliverables/src/prototype-plan.md`. Architecture: [`architecture/components.md`](../architecture/components.md). Spike: [ADR 001](../architecture/adr/001-spike.md). Prices: listings the lead opened in a browser on 4 Oct 2026, 15:34–15:35 IST (`deliverables/bom/bom.csv`). Power: datasheets the lead opened (`deliverables/bom/power_budget.py`).*

## 1. What we build
- **4 fence-line nodes** (C1) on the site boundary at ~2.5–3 m, one per side, so that whatever the wind direction, some nodes are upwind and some downwind. Each node: Sensirion SPS30 (PM1/2.5/4/10 + size bins), SHT30 temperature/RH, ESP32-S3, SX1262 LoRa radio, 10 W panel + LiFePO4 battery + MPPT charger, IP65 box (a radiation shield and inlet are still to be sourced).
- **1 wind sensor** (C2), speed + direction in one head, on a 3–4 m mast clear of the building's wake.
- **1 gateway** (C3): ESP32-S3 + SX1262 (receives the nodes) + A7670C LTE Cat-1 board (uploads), on site power (ASSUMPTION: site offices have mains power).
- **1 misting line** (C8/C9): a 12 V misting kit (pump + 8 nozzles) switched by a relay, with a Hall-effect flow meter so every litre is logged. A 12 V solenoid valve is the option for mains-water sites.
- **Software** (C4–C7, C10–C12): ingest + QA, calibration, attribution, controller, ledger and dashboards behind the typed contracts in `architecture/contracts/`.

## 2. Parts list (one site kit)
{{table:bom}}

**Kit parts total: ₹{{n:bom_kit}}** (4 nodes ₹{{n:bom_nodes4}} · wind ₹{{n:bom_wind}} · gateway ₹{{n:bom_gateway}} · misting ₹{{n:bom_actuator}}). Single-unit retail, incl. GST. **Not included:** 5 V buck converters, cabling and glands, masts and mounting, radiation shields, SIM + data plan, gateway power supply, installation labour, reference co-location, maintenance. These are UNVERIFIED and must be priced before any "installed cost" claim. Notes: the relay listing was out of stock (any 5 V relay module works); the SX1262 module is listed for 868/915 MHz, so its suitability for India's IN865 band is UNVERIFIED; the wind sensor's stock status wasn't shown, and an in-stock alternative is listed at a higher price.

**Commercial yardstick** (fact F6): one construction-site violation costs {{v:F6|₹1 lakh to ₹2 lakh}} under CAQM's 2024 schedule (doubled under GRAP). The parts are {{n:bom_kit_vs_fine2l_pct}}–{{n:bom_kit_vs_fine1l_pct}}% of one fine, which says nothing yet about lifetime cost.

## 3. Power budget (per node)
{{table:power}}

Datasheet sources: Sensirion SPS30 v0.9 (60 mA average in measurement mode, fact F20), Espressif ESP32-S3 v2.1 ({{v:F21|13.2}} mA in modem-sleep at 40 MHz, fact F21), NASA POWER climatology for Delhi (December worst month, fact F22). Bench-measure the real draw in the first build week.

## 4. Connectivity
- Nodes → gateway: LoRa (SX1262). India's licence-exempt band is IN865; whether this module and our duty cycle comply is UNVERIFIED — check before deployment. Fallback: Wi-Fi from the gateway when nodes are within range.
- Gateway → cloud: LTE Cat-1 (A7670C) with store-and-forward on the ESP32 flash, so outages backfill.

## 5. Build steps and dates
| When | Step | Evidence it produces |
|---|---|---|
| 5–12 Oct | Order parts from two vendors per item; replay ratchet continues on evaluator v2.1 (software only) | order receipts; `results.tsv` |
| 13–25 Oct | Bench-build one node + gateway; firmware writes the `NodeReading` / `WindReading` contracts with on-device signing; measure real current draw | power bench log |
| 26–31 Oct | Build 4 nodes; one week side by side (inter-node agreement, metric C1); reference co-location if a slot is granted | co-location dataset |
| Before 1 Nov | Real construction-site trial window: Delhi prohibits dust-generating works from {{v:F1|Nov 1 – Jan 31}}, so a real-site trial must happen before then or at a site permitted to operate | first real fence-line increments |
| 1–17 Nov | Controlled dust-source trial on campus (sand or chalk dust + fan at a known spot): ring + wind + misting on alternate runs | increment, abstention rate, litres used, misting effect |
| 18–25 Nov | No user-dependent work (IIT Delhi end-semester exams 19–25 Nov) | — |
| 26–30 Nov | Report: functionality evidence, cost, implementation and scalability plans, impact from trial numbers only | final report |
| 15–18 Dec | Finals demo: a live ring around a dust source on stage; only the downwind nodes light up; misting triggers | live demo |

## 6. What is simulated now (labelled)
- The construction site, its emissions, plumes, sensor faults and the neighbour/road confounders (`components/attribution/autoresearch/eval_v2.py`, `provenance = SIMULATED`).
- **Real:** background PM (CPCB/DPCC monitors via the OpenAQ archive), meteorology (ERA5 via Open-Meteo), CAMS fields (reference only).
- **Not modelled at all:** the misting effect on dust. No reduction figure exists until the trial.

## 7. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Optical sensors respond differently to coarse dust than to ambient air (CSTEP: qualitative) | Differential use; dust test + reference co-location before any claim; the size bins allow a size-aware correction |
| Calm winter winds (ERA5: below 1 m/s in {{n:calm_lt10_winter_pct}}% of Nov–Jan hours, a lower bound) | Abstain and report the abstention rate; never treat "inconclusive" as clean |
| No real site before 1 Nov | Controlled dust-source trial on campus (labelled) with the same hardware |
| Panel soiling at a dusty site | Weekly wipe; solar derate assumption in the power budget; measure |
| Vendor delays / stock-outs | Order by 12 Oct; alternatives listed in the parts table |
| LoRa band compliance | Verify IN865 before field use; Wi-Fi fallback |
