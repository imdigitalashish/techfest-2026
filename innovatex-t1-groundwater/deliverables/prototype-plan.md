# Round-2 prototype plan — JalSakshi RechargeMeter (report + working prototype due 1 Dec 2026)

> **Status:** v2 (final for the zonal; updated 4 Oct 2026 after both zonal-pick reviews: `reviews/2026-10-04-lead-response.md`).
> **Architecture:** `architecture/components.md` (C0–C8). **Spike rationale:** `architecture/adr/001-spike.md`.
> **Price rule:** every BOM row carries a vendor URL and an access date. Anything without a price we saw ourselves is marked **UNVERIFIED**.
> **Status key:** everything in §2 is **PLANNED** hardware. **BUILT** today: the cloud software (C0 simulator, C4 real-data profile, C5 verifier with deferral, C8 offline demo), all tested in **simulation** only. Final-deck review response: `reviews/2026-10-04-final-deck-lead-response.md`.

## 1. What the prototype must prove (from the reviews)

| Must prove | How | Pass criterion (set before testing) |
|---|---|---|
| Clogging is detectable from falling-head recessions | Pour rig with interchangeable drain orifices (clogging levels) | Clogging precision/recall ≥ 0.8 on blind trials |
| The model-based infiltrated-volume estimate is close enough to be useful | Blind weighed-water pours; truth = water poured − water left in the drum − overflow collected | Report the median absolute error and the 90th percentile. No target is promised; the rig sets the number. A per-event uncertainty band is PLANNED, and its coverage is tested on this data |
| Fakes are flagged | Pours with the rain gauge covered, i.e. no "rain": large fast pours (≥ 100 L) **and** small/slow pours (20 L, 20-min trickle) | Report detection rate by size and rate (a 20 L pour is expected to be missed: below the 2 cm threshold); honest pours flagged < 10 % |
| The node survives the field | Bench current draw, outage buffering, recovery | Measured mAh/day (PPK2); zero lost events after a 24 h link outage (buffer capacity, overwrite and power-loss rules written down first) |
| Missing inputs never produce an accusation | Unplug the gauge or cut the stage cable mid-event | Verdict = `deferred` (BUILT in software, 7 unit tests; repeat on hardware) |
| The duty-cycled schedule doesn't break the numbers | Re-run blind pours with real 15-min dry polling + gauge-interrupt wake-up | Error within 2 points of the continuous-sampling result, or the deck numbers are restated |

## 2. Architecture

- **In the pit:**
  - DFRobot KIT0139 4–20 mA throw-in level transmitter: 0–5 m; datasheet "Material: 316L stainless steel", IP68; 5 m vented cable. (The reviewer reports DFRobot's tutorial lists a 316L membrane with a 304 casing; not re-verified by us.) It hangs inside a slotted 50 mm PVC stilling tube with a geotextile sock, its tip on a stand 5–10 cm above the floor (the silt line).
  - **Datum:** stage is measured above the probe tip. The 5–10 cm below the tip is a blind zone, 0.11–0.23 m³ in a 2.25 m² pit (A); the commissioning fill fixes the tip-to-floor offset.
- **In the lid housing:**
  - MCU + LoRaWAN radio: RAK3172 (STM32WLE5CC, IN865) standalone. An ESP32-C6 dev board is the prototype host if needed.
  - 3.6 V Li-SOCl₂ D-cell.
  - Boost converter (3.6 V → 12 V) switched by a MOSFET, so the probe is powered only while sampling.
  - Flash ring buffer holding a signed, append-only log.
  - Antenna mounted clear of any metal lid (a flush antenna under a steel cover is shielded); site survey first.
  - **Mandatory** tipping-bucket rain gauge on the roof edge. It wakes the node (interrupt) and is the plausibility check; without it, verdicts defer.
  - Vent tube terminates in a desiccant chamber inside the lid housing (vented-cable moisture is a known failure mode: Solinst guidance in `research/landscape.md` [S16]).
  - A barometer **only if** the probe turns out to be absolute-referenced. The datasheet doesn't state the reference type; throw-in probes are commonly vented-cable. **Bench check.**
- **Firmware (C2):**
  - **Dry:** 1 sample every 15 min; uplink every 6–12 h.
  - **Wet:** a gauge tip (interrupt) or a stage rise > 2 cm switches to 1-min sampling until the stage returns to baseline, then sends an event summary plus the compressed series.
  - **Always:** heartbeats and tamper events (stage equal to the floor during rain; lid switch).
  - **Auto-zero: PLANNED, not in reported results.** Two simulated variants were rejected by the keep rule (`results.tsv` v3-c1, v3-c2). A real dry reference needs a defined condition, e.g. no rain for 48 h and a flat stage at the floor.
  - **Pre-monsoon check:** a metered hose fill before each monsoon. Clogging that develops in the dry season shows up only at the next storm otherwise.
- **Cloud (C4–C8):** Python services behind the typed contracts in `architecture/contracts/`. The verdict is advisory: **an inspector can override any verdict, and no bill changes automatically.**

## 3. Bill of materials — per node (prototype, single-unit retail)

| # | Part | Listing (as shown) | Vendor | ₹ | URL | Accessed | Status |
|---|---|---|---|---|---|---|---|
| 1 | Level probe 0–5 m, 4–20 mA, 0.5 % FS | DFRobot KIT0139 "Liquid Level Transmitter, Throw-in Type… Gravity Series" (DFRobot sells it with its current-to-voltage converter) | element14 India | 4,254.51 | https://in.element14.com/dfrobot/kit0139/liquid-level-trans-arduino-uno/dp/3974116 | 2026-10-04 | VERIFIED (27 in stock) |
| 2 | LoRaWAN module | "Rakwireless WisBlock LPWAN Module RAK3172 /RUI3/IN865" | electronicscomp.com | 1,672.80 | https://www.electronicscomp.com/rakwireless-wisblock-lpwan-module-rak3172-rui3-in865 | 2026-10-04 | VERIFIED |
| 3 | Prototype host MCU (drop in production) | "Espressif ESP32-C6-DevKitM-1-N4 Dev Board" | robu.in | 1,099.00 | https://robu.in/product/espressif-esp32-c6-devkitm-1-n4-dev-board/ | 2026-10-04 | VERIFIED |
| 4 | Battery | "Forte ER34615 D 3.6V Li-SOCL2 Battery" | robu.in | 879.00 | https://robu.in/product/forte-er34615-d-3-6v-li-socl2-battery/ | 2026-10-04 | VERIFIED |
| 5 | Enclosure | IP67 ABS junction box 150×100×70 mm with glands | amazon.in | 3,250.87 | https://www.amazon.in/Otdorpatio-Waterproof-Electrical-Enclosure-150x100x70mm/dp/B09F918F1N | 2026-10-04 | VERIFIED |
| 6 | Cable gland | "Polyamide Cable Gland PG 7" | robu.in | 10.00 | https://robu.in/product/polyamide-cable-gland-pg-7/ | 2026-10-04 | VERIFIED |
| 7 | Boost converter, MOSFET, IN865 antenna, connectors, potting | — | — | — | — | — | **UNVERIFIED** |
| 8 | Stilling tube (50 mm slotted PVC), geotextile sock, SS stand, cable ties | local hardware | — | — | — | — | **UNVERIFIED** |
| | **Per-node subtotal, verified rows 1–6** | | | **11,166.18** | | | arithmetic below |
| 9 | Rain gauge (optional) | DFRobot Gravity tipping-bucket rainfall sensor, 0.28 mm (listed as unavailable) | amazon.in | 3,729.00 | https://www.amazon.in/DFRobot-Gravity-Tipping-Bucket-Rainfall/dp/B0GGC21C1M | 2026-10-04 | VERIFIED price |
| 10 | Barometer (only if the probe is absolute-referenced) | "SparkFun SEN-13676 Atmospheric Sensor Breakout - BME280" | robu.in | 3,089.00 | https://robu.in/product/sparkfun-atmospheric-sensor-breakout-bme280/ | 2026-10-04 | VERIFIED (a generic BMP280 would be cheaper but is unpriced) |

**Arithmetic:** 4,254.51 + 1,672.80 + 1,099.00 + 879.00 + 3,250.87 + 10.00 = **₹11,166.18**.
- With the rain gauge: **₹14,895.18**.
- Production path without the dev board: ₹10,067.18 (+ gauge = ₹13,796.18).
- Rows 7–8 are not included.

**Shared, not per-node:**
- LoRaWAN gateway "Robocraze LPS8N Indoor LoRaWAN Gateway", ₹33,559 (https://www.amazon.in/Robocraze-Multi-Channel-Indoor-Gateway-Lorawan-LPS8N/dp/B0DP91M6BZ, 2026-10-04; IN865 variant not confirmed on the page).
- Bench tool "NRF-PPK2 Power Profiler Kit II", ₹14,500 (https://www.amazon.in/NRF-PPK2-Profiler-Current-Measurement-Development/dp/B0GVMSX4NZ, 2026-10-04).

**Alternative industrial probe:** "Digital Liquid Level Transmitter, Submersible level Gauge, Range 0~5meter, Output 4~20mA, Power 24VDC, Acc. +/- 0.5%", ₹17,500 (https://www.amazon.in/Digital-Liquid-Transmitter-Submersible-0-5meter/dp/B0GXP9WC6Y, 2026-10-04).

**Comparator:** one CGWA-compliant DWLR, Acorn PZM-24B: "Approx. Price: Rs 38,000 / Piece", logs 365 × 2 readings/day, ±0.5 % FS (https://www.acorncontrols.com/piezometer.html, 2026-10-04).

**Correction log:**
- The earlier "< ₹6,000" target and the ₹10,100.67 figure used the MS5837-30BA. That is a 30-bar part (listing: "30 bar, Digital, Sealed Gauge"), wrong for a 0–3 m pit, so it has been removed.
- The ₹32,428.67 in `research/bom-prices.md` summed *both* sensor options. It was never a per-node price.

## 4. Error budget (KIT0139; datasheet https://www.farnell.com/datasheets/3708809.pdf: "Overall Accuracy: 0.5%", "Measuring Range: 0-5m", 12–36 V supply, overload 300 %, IP68)

- **Worst-case absolute error per reading:** ±0.5 % × 5 m = **±25 mm**. On a 1.5 × 1.5 m pit (2.25 m², assumed geometry) that is ±0.056 m³.
- **Event inflow from the stage rise**, worst case with independent errors at both ends: ±2 × 25 mm × 2.25 m² = **±0.11 m³**. That is 2.8 % of a 4.0 m³ event (100 m² roof × 50 mm × runoff 0.8, assumed).
- **Offset:** the kept verifier does **not** remove a constant offset (auto-zero not adopted). Stage is referenced to the probe tip. Residual drift and nonlinearity are not in the datasheet, so the rig measures them.
- **Scope of this budget:** it covers the storage term only. It is not the infiltration uncertainty, which also depends on the drain-law fit, overflow and unobserved paths (see the observability table, deck Backup 4).
- **Simulated effect:** frozen evaluator v3 adds ±25 mm offset, ±10 mm/season drift and 2.1 mm quantisation. Results are in `components/recharge_verifier/autoresearch/results.tsv` and summarised in §8.
- **ADC (ASSUMPTION):** the converter output span is taken as ≈1.92 V on a 3.3 V, 12-bit ADC, about 2.1 mm/count. Verify on the bench.

## 5. Power budget (method + sensitivity; to be measured with the PPK2)

E/day = I_sleep·24 h + N_samples·(I_probe·t_on) + N_uplinks·Q_uplink.

- **Probe** (4–20 mA at 12 V through a boost from 3.6 V): roughly 25–80 mA drawn from the cell while on (ESTIMATE).
- **Warm-up:** DFRobot says output is "more steady … after preheating for 30 minutes", so **t_on is the key unknown**.

| Assumption (ESTIMATE) | Dry samples/day | t_on | Probe mAh/day | Battery life on ~19 Ah, probe only |
|---|---|---|---|---|
| Fast settle | 96 | 2 s | 96 × 80 mA × 2 s / 3600 ≈ 4.3 | ≈ 12 yr (probe only; not a claim) |
| Slow settle | 96 | 30 s | ≈ 64 | ≈ 0.8 yr → needs solar or a different sensor |

**Decision rule:** if the measured settle time is > 5 s, switch to a 1–2 W solar + Li-ion supply (lids are outdoors) or a low-power digital probe. MCU and radio sleep current are measured too. For scale only, a different LoRa node measured ≈ 11 mAh/day all-in (MichielBruijn/lora-humidity-sensor). **No battery-life claim until we measure.**

## 6. Pour rig (ground truth for blind trials; also the finals demo)

- **"Pit":** a 200 L HDPE drum (plan area measured on site) with a bottom drain fitted with **interchangeable orifice plates** (e.g. 6/4/3/2 mm) to emulate progressive clogging, plus a side overflow at a fixed height.
- **Inflow truth:** water weighed in 10 L buckets on a hanging scale, or a domestic water meter on a hose. Overflow is collected and weighed.
- **"Rain":** pour over the tipping-bucket gauge to emulate a storm. Pour with the gauge covered to emulate a fake.
- **Blind protocol:**
  1. A script draws volume, pour rate, orifice and fake/honest status.
  2. The pourer follows it.
  3. The verifier operator sees only the node data.
  4. Results are scored against the weighed truth.

  Run 20 storms × 3 orifices + 10 fakes.

## 7. Build steps and schedule (user exams 19–25 Nov and vivas 27–28 Nov avoided)

| When | Who | Step | Evidence |
|---|---|---|---|
| 4–9 Oct | lead (software) + user | Final deck, Q&A, offline demo; **user registers for the Delhi zonal by 9 Oct** | deck, demo |
| 10 Oct | team | Delhi zonal pitch (South Asian University) | — |
| 11–13 Oct | user / hardware teammate | Order rows 1–6, 9, gateway and PPK2 (element14 lead time: 4–6 business days from UK stock) | order receipts |
| 14–20 Oct | hardware teammate | Build the pour rig. Wire probe → converter → ADC; boost + MOSFET switching | rig photos, first readings |
| 18–31 Oct | lead + teammate | Firmware: sampling modes + gauge-interrupt wake-up, ring buffer (capacity/overwrite rules), LoRaWAN uplink; auto-zero candidate; cloud ingest of real frames | logs |
| 21–31 Oct | hardware teammate | PPK2: settle time, sleep current, mAh/day → power decision (§5) | measured budget |
| 1–12 Nov | team | **Blind rig trials** (§6) → C5 metrics on real data; rerun all frozen evaluators | results table |
| 1–16 Nov | user | 1–3 field pits (campus/RWA, with permission): install + metered fill test | site photos, fill-test data |
| 13–17 Nov | lead | Report draft; dashboard polish; video script | draft |
| 19–25 Nov | — | **Exams: no user-dependent work** (agents can polish the report) | — |
| 26–30 Nov | user (light; vivas 27–28 Nov) | Final read-through; team leader submits on techfest.org | submission |
| 15–18 Dec | team | Finals: live pour-rig demo | — |

## 8. What exists today (software, runnable offline)

- **C0 simulator:** linear-reservoir pits driven by Open-Meteo archive rain (reanalysis-based; default model, not pinned); the minute pattern inside each hour is synthetic. The hourly input is frozen in `eval/data/delhi_rain_hourly_openmeteo_default_monsoon2024_2025.csv`. Frozen evaluators v1 (same model), v2 (non-linear drains + imperfect gauge) and v3 (v2 + sensor offset/drift/quantisation).
- **C5 verifier v1, all on simulated pits:**
  - holdout event MdAPE 3.0 % on the same-model test;
  - **13.1 % on the stress test (v2)**;
  - fake detection 10/10 simulated fakes.
- **Real data:** India-WRIS DWLR profile for Delhi, 185 telemetric stations.
- **Offline demo:** `deliverables/demo/` (see `deliverables/demo/README.md`).

## 9. Hardware teammate: what we need (put under *Needs from user*)

Someone comfortable with:
- soldering and wiring a 4–20 mA loop to an ADC;
- flashing Arduino/STM32 firmware;
- basic plumbing for the drum rig;
- running PPK2 measurements.

About 4–6 h/week from 11 Oct to 16 Nov, plus finals travel (15–18 Dec).

## 10. Risks

1. Probe settle time (power).
2. Silt clogging the probe port: sock + stand, monthly check in the pilot.
3. Owner incentives: the buyer is DJB's government-building restorations, and an inspector can override verdicts.
4. Few post-monsoon storms: the rig + fill tests carry the evidence.
5. A pilot site depends on permission.
6. The ₹204.46 cr rebate figure is secondary-sourced (Hindustan Times citing DJB data).

## 11. Pilot cost (parts only; listings seen 4 Oct 2026) and stated assumptions

| Configuration | Arithmetic | ₹ (parts only) |
|---|---|---|
| Base node | rows 1–6 | 11,166.18 |
| First site: node + rain gauge + shared gateway | 11,166.18 + 3,729.00 + 33,559.00 | 48,454.18 |
| 3-pit pilot: 3 nodes + 3 gauges + 1 gateway | 3 × 11,166.18 + 3 × 3,729.00 + 33,559.00 | 78,244.54 |

- **Excluded:** tax/shipping adjustments; boost converter, antenna, tube, sock, mounting, potting, cable; installation; backhaul; service.
- **Labour (ASSUMPTIONS, no ₹ until a provider quotes):** ≈ 1 technician-day per pit to install, and ≈ ½ day per pit for the annual pre-monsoon fill check. DJB's 59 empanelled providers are the natural quote source.
- **Backhaul (ASSUMPTION):** site Wi-Fi/Ethernet for the gateway.
- **Price evidence:** the lead saw the listed prices on 4 Oct. An independent re-check the same day was blocked by most vendors (HTTP 403/503), so get quotes before buying.

## 12. Safety and water-quality boundaries (pilot conditions)
- **Install:** no pit entry. The probe is lowered from the lid by an empanelled installer; low-voltage battery device; lids stay closed and locked; written site permission.
- **Water quality:** pilot only on permitted roof-runoff structures with existing pretreatment (filter media / first-flush) and a responsible site operator.
  - The system never recommends recharging runoff it can't vouch for.
  - An EC channel is a later screening aid. Conductivity alone does not certify safety.
- **Customer status (4 Oct):** DJB's restoration programme is a *prospective* pilot customer; no contact or permission yet.
