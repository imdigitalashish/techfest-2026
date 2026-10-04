# Prototype plan — DustLedger (working prototype due 1 Dec 2026)

*Rendered from `deliverables/src/prototype-plan.md`. Architecture: [`architecture/components.md`](../architecture/components.md). Spike: [ADR 001](../architecture/adr/001-spike.md). Prices: listings the lead opened in a browser on 4 Oct 2026, 15:34–15:35 IST (`deliverables/bom/bom.csv`). Power: datasheets the lead opened (`deliverables/bom/power_budget.py`).*

## 1. What we build
- **4 fence-line nodes** (C1) on the site boundary at ~2.5–3 m, one per side, so that whatever the wind direction, some nodes are upwind and some downwind. Each node: Sensirion SPS30 (PM1/2.5/4/10 + size bins), SHT30 temperature/RH, ESP32-S3, SX1262 LoRa radio, 10 W panel + LiFePO4 battery + MPPT charger, IP65 box (a radiation shield and inlet are still to be sourced).
- **1 wind sensor** (C2), speed + direction in one head, on a 3–4 m mast clear of the building's wake.
- **1 gateway** (C3): ESP32-S3 + SX1262 (receives the nodes) + A7670C LTE Cat-1 board (uploads), on site power (ASSUMPTION: site offices have mains power).
- **1 misting line** (C8/C9): a 12 V misting kit (pump + 8 nozzles) switched by a relay, with a Hall-effect flow meter so every litre is logged. A 12 V solenoid valve is the option for mains-water sites.
- **Software** (C4–C7, C10–C12): ingest + QA, calibration, attribution, controller, ledger and dashboards behind the typed contracts in `architecture/contracts/`.

## 2. Parts list (one site kit)
| Subsystem | Item | Part as listed | Qty | ₹ each (incl. GST) | Line ₹ | Stock seen | Vendor (link) |
|---|---|---|---|---|---|---|---|
| node | PM sensor | Sensirion SPS30, Particulate Matter Sensor, PM2.5, Range: 0–1,000 µg/m³ | 4 | 3,599 | 14,396 | InStock | [robu.in](https://robu.in/product/sensirion-particulate-matter-sensor-0-to-1000-%c2%b5g-m3-laser-i2c-uart-calibrated-4-5-to-5-5-v-supply/) |
| node | T/RH sensor | Micro SHT30 sensor module + adapter board | 4 | 269 | 1,076 | InStock | [robu.in](https://robu.in/product/temperature-and-humidity-sensor-2/) |
| node | MCU | ESP32 S3 Devkit (ESP32 S3 WROOM 1 N16R8) | 4 | 839 | 3,356 | InStock | [robu.in](https://robu.in/product/esp32-s3-devkit-esp32-s3-wroom-1-n16r8/) |
| node | LoRa radio | IndieSemiC ISC-SX1262-B LoRa Module (868/915 MHz listed; IN865 suitability UNVERIFIED) | 4 | 549 | 2,196 | InStock | [robu.in](https://robu.in/product/indiesemic-isc-sx1262-b-an-advanced-lora-module-v0-1/) |
| node | Solar panel 10 W | Loom 10-Watt Solar Panel (polycrystalline) | 4 | 949 | 3,796 | In stock | [amazon.in](https://www.amazon.in/Loom-Solar-10-Watt-Panel/dp/B07JF2B35T/) |
| node | Battery | Pro-Range IFR 32650 12.8V 12000mAh 4S2P LiFePO4 pack | 4 | 3,359 | 13,436 | InStock | [robu.in](https://robu.in/product/pro-range-ifr-32650-lifepo4-12000mah-12-8v-4s2p-protected-battery-pack-3c/) |
| node | Solar charger | Elejoy CN3791 12V MPPT Solar Charger Module | 4 | 199 | 796 | InStock | [robu.in](https://robu.in/product/cn3791-12v-mppt-solar-charger-module/) |
| node | Enclosure | F1 195*115*75mm IP65 ABS junction box | 4 | 269 | 1,076 | InStock | [robu.in](https://robu.in/product/f1-19511575mm-ip65-abs-pcb-plastic-junction-box/) |
| wind | Wind speed + direction | XS-WSDS01 Integrated Wind Speed Direction Sensor (RS485 Modbus per listing title) | 1 | 14,810 | 14,810 | not shown | [amazon.in](https://www.amazon.in/XS-WSDS01-Integrated-Direction-Anemometer-XS-WSDS01-0%EF%BD%9E5V/dp/B0DMNJGY3Y/) |
| gateway | LTE Cat-1 board | SIM A7670C 4G LTE Development Board with 4G Flex Antenna | 1 | 1,859 | 1,859 | InStock | [robu.in](https://robu.in/product/sim-a7670c-4g-lte-development-board-with-4g-flex-antenna/) |
| gateway | MCU | ESP32 S3 Devkit (ESP32 S3 WROOM 1 N16R8) | 1 | 839 | 839 | InStock | [robu.in](https://robu.in/product/esp32-s3-devkit-esp32-s3-wroom-1-n16r8/) |
| gateway | LoRa radio | IndieSemiC ISC-SX1262-B LoRa Module | 1 | 549 | 549 | InStock | [robu.in](https://robu.in/product/indiesemic-isc-sx1262-b-an-advanced-lora-module-v0-1/) |
| gateway | Enclosure | F1 195*115*75mm IP65 ABS junction box | 1 | 269 | 269 | InStock | [robu.in](https://robu.in/product/f1-19511575mm-ip65-abs-pcb-plastic-junction-box/) |
| actuator | Misting kit | Fieldstar DIY Misting System Kit with Nozzles, Pump 12V, Pipe, Connectors (8 nozzles) | 1 | 1,999 | 1,999 | In stock | [amazon.in](https://www.amazon.in/Misting-System-Kit-Nozzles-Hydroponics/dp/B0F3DKV27D/) |
| actuator | Flow sensor | YF-S201 Water Flow Sensor 1–30 L/min | 1 | 219 | 219 | InStock | [robu.in](https://robu.in/product/yf-s201-water-flow-measurement-sensor-with-1-30liter-min-flow-rate-2/) |
| actuator | Relay | 5V 1 Channel Relay Module | 1 | 39 | 39 | OutOfStock | [robu.in](https://robu.in/product/1-channel-isolated-5v-relay-module-opto-coupler-for-arduino-pic-avr-dsp-arm/) |
| actuator_option (not in total) | Solenoid valve (mains-water variant) | 12V DC 1/2in Electric Solenoid Water Air Valve (Normally Closed) | 1 | 269 | 269 | InStock | [robu.in](https://robu.in/product/dc12v-plastic-electric-12v-water-solenoid-valve-electric-solenoid-valve-magnetic-nc-water-air-inlet-flow-switch-nc-12/) |
| alt_wind (not in total) | Wind (in-stock alternative) | FirstRate FST200-205 Wind Speed & Wind Direction Integrated Sensor (4–20 mA) | 1 | 21,759 | 21,759 | InStock | [robu.in](https://robu.in/product/firstrate-fst200-205-wind-speed-wind-direction-integrated-sensor/) |
| alt_solar (not in total) | Solar panel (alternative) | 10W 12Volts 36-cell Solar Panel | 1 | 1,047 | 1,047 | OutOfStock | [robu.in](https://robu.in/product/10w-solar-panel-36-cell-solar-plate-high-quality-10-w-10-watts/) |
| alt_pump (not in total) | Pump (alternative to kit pump) | 550 Diaphragm Pump 12V Water Pump | 1 | 399 | 399 | InStock | [robu.in](https://robu.in/product/550-diaphragm-pump-12v-water-pump-for-water-spray-fish-tank-reflux-pump/) |

**Kit parts total: ₹60,711** (4 nodes ₹40,128 · wind ₹14,810 · gateway ₹3,516 · misting ₹2,257). Single-unit retail, incl. GST. **Not included:** 5 V buck converters, cabling and glands, masts and mounting, radiation shields, SIM + data plan, gateway power supply, installation labour, reference co-location, maintenance. These are UNVERIFIED and must be priced before any "installed cost" claim. Notes: the relay listing was out of stock (any 5 V relay module works); the SX1262 module is listed for 868/915 MHz, so its suitability for India's IN865 band is UNVERIFIED; the wind sensor's stock status wasn't shown, and an in-stock alternative is listed at a higher price.

**Commercial yardstick** (fact F6): one violation costs a large Delhi site a ₹5 lakh flat fine. The parts are 12% of one fine, which says nothing yet about lifetime cost.

## 3. Power budget (per node)
| Load | W (average) |
|---|---|
| SPS30, continuous measurement (5 V × 60 mA) | 0.300 |
| ESP32-S3, modem-sleep 40 MHz idle (3.3 V × 13.2 mA) | 0.044 |
| LoRa radio + SHT30 + misc (ASSUMPTION: 3.3 V × 5 mA average) | 0.017 |

Daily energy at the battery (÷ 0.85 DC-DC efficiency, ASSUMPTION): **10.2 Wh/day**. 10 W panel, solar derate 0.7 (ASSUMPTION): December 21.2 Wh/day → **2.09×** the load in the worst month. Battery 153.6 Wh nominal, 80% usable (ASSUMPTION) → **12.1 days** with no sun. NASA POWER is a 20-year all-sky climatology; smog/fog weeks are darker than the monthly mean. Bench-measure the real draw.

Datasheet sources: Sensirion SPS30 v0.9 (60 mA average in measurement mode, fact F20), Espressif ESP32-S3 v2.1 (13.2 mA in modem-sleep at 40 MHz, fact F21), NASA POWER climatology for Delhi (December worst month, fact F22). Bench-measure the real draw in the first build week.

## 4. Connectivity
- Nodes → gateway: LoRa (SX1262). India's licence-exempt band is IN865; whether this module and our duty cycle comply is UNVERIFIED — check before deployment. Fallback: Wi-Fi from the gateway when nodes are within range.
- Gateway → cloud: LTE Cat-1 (A7670C) with store-and-forward on the ESP32 flash, so outages backfill.

## 5. Build steps and dates
| When | Step | Evidence it produces |
|---|---|---|
| 5–12 Oct | Order parts from two vendors per item; replay ratchet continues on evaluator v2.1 (software only) | order receipts; `results.tsv` |
| 13–25 Oct | Bench-build one node + gateway; firmware writes the `NodeReading` / `WindReading` contracts with on-device signing; measure real current draw | power bench log |
| 26–31 Oct | Build 4 nodes; one week side by side (inter-node agreement, metric C1); reference co-location if a slot is granted | co-location dataset |
| Before 1 Nov | Real construction-site trial window: Delhi prohibits dust-generating works from Nov 1 – Jan 31, so a real-site trial must happen before then or at a site permitted to operate | first real fence-line increments |
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
| Calm winter winds (ERA5: below 1 m/s in 16.2% of Nov–Jan hours, a lower bound) | Abstain and report the abstention rate; never treat "inconclusive" as clean |
| No real site before 1 Nov | Controlled dust-source trial on campus (labelled) with the same hardware |
| Panel soiling at a dusty site | Weekly wipe; solar derate assumption in the power budget; measure |
| Vendor delays / stock-outs | Order by 12 Oct; alternatives listed in the parts table |
| LoRa band compliance | Verify IN865 before field use; Wi-Fi fallback |
