# Prototype plan — NullahNet (Round 2: report + working prototype due 1 Dec 2026)

> Every price row carries its product URL and access date (2026-10-04). Subtotals are bound to `research/fact-check.md`, and results to committed runs. Labels: **SIMULATED**, **SYNTHETIC**, **SENSITIVITY**, **ASSUMPTION**, **PLANNED**. Architecture: [`../architecture/components.md`](../architecture/components.md). Spike rationale: [ADR 001](../architecture/adr/001-spike.md).

## 1. What we demonstrate on 1 Dec and at the finals
1. **Tow-tank flume.** A clear channel in which a towing carriage pulls a model boom through still water at set speeds; towing back reverses the flow. On it we compare a straight boom, an angled boom, and the angled boom with the one-way pocket and fail-open fuse (Spike 2).
2. **Edge sensor node over the pocket.** The same design as the field node: camera + ultrasonic range sensor + load cell. It sends `SiteTelemetry` (see contracts) to the cloud.
3. **Cloud twin, dispatch, dashboard and evidence records** (BUILT today). The flume appears as a live site beside SIMULATED Mumbai outfalls, and each emptying of the pocket becomes a signed evidence record checked against the load cell.

## 2. Why a tow tank, and the design
- **Why towing instead of pumping:** a pumped flume needs thousands of litres per hour to reach a few tenths of a metre per second, even in a narrow channel. Towing gives the same relative velocity with a small motor, exact speed control and free flow reversal. Large boom test facilities do this. Ohmsett tows equipment from {{f:F28|three movable bridges}} at up to {{f:F28|6 knots}} "to simulate ocean and river current flow".
- **Channel:** one acrylic sheet cut into two walls and a floor, about 2.4 m long and 0.3 m wide, with about 0.15 m of water (ASSUMPTION: design targets; final dimensions follow the sheet thickness quoted).
- **Carriage and speed:** a 12 V, 100 RPM geared motor winds a cord on a spool of about 0.1 m diameter. Full speed is π × 0.1 m × 100/60 ≈ 0.5 m/s (ASSUMPTION: unloaded speed; we calibrate the real speed from video). Runs straddle the boom escape speed of about {{f:F14|0.35 m/s}} (ITOPF).
- **Boom models:** PVC-pipe floats with a nylon-mesh skirt, at four angles to the motion (90°, 45°, 30°, 20°). The **one-way pocket** sits at the bank end with HDPE flaps on SS 316 hinges. The **fail-open fuse** is a hinged boom section held by a counterweight, set to open at a chosen water-level difference; the pocket sits outside its path.
- **Test items:** real carry-bag and film pieces, multilayer sachets, small PET bottles and thermocol, colour-tagged by type, in a fixed mix per run (ASSUMPTION: mix proportions until a Mumbai composition survey is cited).
- **Scaling:** we claim *comparative* behaviour between designs, not field efficiencies.

## 3. Test protocol (each condition ≥5 runs; report mean ± s.d.)
| Test | What we vary | Scalar metric | Pass / kill |
|---|---|---|---|
| T1 Capture | design × speed (three levels) | items captured ÷ items met | — (characterisation) |
| T2 Retention under reversal (Spike 2) | design × reversals (one, three, five) | items still held ÷ items captured | pocket beats the angled boom by more than run-to-run s.d.; else drop the retention claim |
| T3 Head rise and fuse | blockage (none to full) × speed | water-level difference across the boom (two range sensors on the carriage); opening head; items lost when the fuse opens | head rise stays under a set cap; the pocket keeps its catch when the fuse opens |
| T4 Fill alert (blinded) | fill states set by one teammate under glare, darkness, spray, occlusion | fill-% error; empty/half/full accuracy | — (feeds the fill estimator) |
| T5 Clearance | pocket design | seconds to empty; grams per person-minute (load cell) | — |
| T6 Boom angle | angle × speed | capture vs speed across the boom | calibrates the twin's capture curve, which is an ASSUMPTION today |

T2, T3 and T6 replace the twin's assumed retention and capture parameters with measured ones.

## 4. Bills of materials
Prices are as listed on the product page on the access date. GST treatment differs by seller (UNVERIFIED); IndiaMART prices are supplier listings, so confirm on quote.

### 4A. Field sensor node (one boom)
| Function | Item (as listed by retailer) | Qty | Unit ₹ | Line ₹ | Retailer page (opened 2026-10-04) | Accessed |
|---|---|---:|---:|---:|---|---|
| Compute | Raspberry Pi 5, 8GB variant (in stock; 4GB ₹16,199.99 out of stock) | 1 | 21,199.99 | 21,199.99 | https://thinkrobotics.com/products/raspberry-pi-5 | 2026-10-04 |
| AI accelerator | Official Raspberry Pi AI HAT+ 13 TOPS (Hailo-8L) | 1 | 6,854.00 | 6,854.00 | https://quartzcomponents.com/products/official-raspberry-pi-ai-hat-13-tops | 2026-10-04 |
| Camera | Raspberry Pi Camera Module 3 | 1 | 3,245.00 | 3,245.00 | https://robocraze.com/products/raspberry-pi-camera-module-3 | 2026-10-04 |
| Backhaul (images + telemetry) | Waveshare SIM7600E-H 4G HAT for Raspberry Pi, LTE Cat-4, GNSS | 1 | 9,149.99 | 9,149.99 | https://thinkrobotics.com/products/sim7600e-h-4g-hat-for-raspberry-pi-lte-cat-4-4g-3g-2g-gnss | 2026-10-04 |
| Water/boom-fill level | DFRobot A02YYUW waterproof ultrasonic distance sensor, 3–450 cm (retailer title) | 1 | 2,259.00 | 2,259.00 | https://robocraze.com/products/dfrobot-a02yyuw-waterproof-ultrasonic-distance-sensor | 2026-10-04 |
| Solar | Loom Solar Mono PERC half-cut 55 Wp 12 V panel (x2 = 110 Wp for profile P1) | 2 | 2,200.00 | 4,400.00 | https://www.loomsolar.com/products/loom-solar-panel-55-watt-mono-crystalline | 2026-10-04 |
| Storage battery | CAML 12.8 V 100 Ah (1.28 kWh) LiFePO4 — smallest 12.8 V LiFePO4 found on an opened Indian page; ~5.3 days of P1 autonomy at 80% DoD (1,280 × 0.8 / 192) | 1 | 34,500.00 | 34,500.00 | https://www.loomsolar.com/products/caml-10012-low-voltage-lithium-battery | 2026-10-04 |
| Charge controller | 20A Digital PWM Solar Controller with LCD + USB (LiFePO4 profile support UNVERIFIED) | 1 | 339.00 | 339.00 | https://robocraze.com/products/20a-digital-pwm-solar-controller-with-lcd-and-usb-output-port | 2026-10-04 |
| 12 V → 5 V | SmartElex TPS5430 buck module 5 V 3 A (below the official 5 V/5 A, 27 W PSU rating — bench-test; upgrade if brown-outs) | 1 | 335.00 | 335.00 | https://robocraze.com/products/smartelex-tps5430-buck-module-5v-3a-dc-dc-converter | 2026-10-04 |

Plus an IP66 enclosure: Polycarbonate Junction Box, IP66, 160x250x115 mm, ₹ 1,200/piece — https://www.indiamart.com/proddetail/polycarbonate-junction-box-2859133826973.html — accessed 2026-10-04.
**Node total: {{f:D04|₹83,481.98}}** (electronics {{f:F26|₹82,281.98}} + enclosure). Not priced yet: SS 316 pole clamps, cable glands, rain gauge, lens wiper (UNVERIFIED). The battery is about half the node cost; the duty-cycled power profile needs a much smaller one (see sensing research).

### 4B. Flume electronics (bench, mains-powered)
| Function | Item (as listed by retailer) | Qty | Unit ₹ | Line ₹ | Retailer page (opened 2026-10-04) | Accessed |
|---|---|---:|---:|---:|---|---|
| Compute | Raspberry Pi 5, 8GB | 1 | 21,199.99 | 21,199.99 | https://thinkrobotics.com/products/raspberry-pi-5 | 2026-10-04 |
| AI accelerator | Official Raspberry Pi AI HAT+ 13 TOPS (same stack as the field node, so models transfer) | 1 | 6,854.00 | 6,854.00 | https://quartzcomponents.com/products/official-raspberry-pi-ai-hat-13-tops | 2026-10-04 |
| Camera | Raspberry Pi Camera Module 3 | 1 | 3,245.00 | 3,245.00 | https://robocraze.com/products/raspberry-pi-camera-module-3 | 2026-10-04 |
| Power | Official Raspberry Pi 5 27W USB-C PD power supply | 1 | 1,249.00 | 1,249.00 | https://robocraze.com/products/raspberry-pi-5-27w-usb-c-power-supply-black-colour | 2026-10-04 |
| Level in flume | Waterproof ultrasonic distance transducer (JSN-SR04T class) | 1 | 295.00 | 295.00 | https://quartzcomponents.com/products/waterproof-ultrasonic-distance-transducer-sensor | 2026-10-04 |
| Sensor/actuator MCU | ESP32 38-pin WiFi + Bluetooth NodeMCU dev board (pump/gate control, level logging) | 1 | 425.00 | 425.00 | https://robocraze.com/products/esp32-development-board | 2026-10-04 |
| LPWAN demo link | SX1278 LoRa module Ra-02 433 MHz (pair; note India's LoRaWAN band is 865–867 MHz — use for bench demo only) | 2 | 345.00 | 690.00 | https://robocraze.com/products/sx1278-lora-module-ra-02-433mhz-wireless-spread-spectrum-transmission | 2026-10-04 |

**Subtotal: {{f:F26|₹33,957.99}}.**

### 4C. Tow-tank structure and retrofit model
| Function | Item (as listed) | Qty | Unit ₹ | Line ₹ | Product page | Accessed | Note |
|---|---|---:|---:|---:|---|---|---|
| Channel walls + floor | Clear Acrylic Sheet, 8x4 ft, cast (thickness to confirm on quote; listing spans 2–18 mm) | 1 | 2,700.00 | 2,700.00 | https://www.indiamart.com/proddetail/clear-acrylic-sheet-2857837064473.html | 2026-10-04 | IndiaMART, Mumbai supplier, ₹ 2,700/sheet |
| Boom floats, carriage rails | 32mm OD PVC Pipe | 6 | 47.52 | 285.12 | https://www.indiamart.com/proddetail/32mm-od-pvc-pipe-2853173589197.html | 2026-10-04 | IndiaMART, ₹ 47.52/meter (qty in metres) |
| Boom skirt | Nylon Mesh Net | 10 | 20.00 | 200.00 | https://www.indiamart.com/proddetail/nylon-mesh-net-2852568984912.html | 2026-10-04 | IndiaMART, Mumbai, ₹ 20/sq ft (qty in sq ft) |
| One-way flaps, pocket walls | HDPE Sheet | 2 | 210.00 | 420.00 | https://www.indiamart.com/proddetail/hdpe-sheet-2849758578412.html | 2026-10-04 | IndiaMART, Pune, ₹ 210/kg (qty in kg) |
| Fuse hinge + flap hinges | SS 316 Butt Hinges | 4 | 60.00 | 240.00 | https://www.indiamart.com/proddetail/ss-316-butt-hinges-2854596724762.html | 2026-10-04 | IndiaMART, Thane, ₹ 60/piece |
| Towing winch | Johnson DC Geared Motor 12V 100 RPM (Grade A) | 1 | 549.00 | 549.00 | https://robocraze.com/products/johnson-dc-geared-motor-12v-100-rpm-grade-a | 2026-10-04 | robocraze product data |
| Winch speed control | L298N 2A Motor Driver Module | 1 | 128.00 | 128.00 | https://quartzcomponents.com/products/l298n-2a-based-motor-driver-module | 2026-10-04 | quartzcomponents product data |
| Weigh the catch (feeds the evidence record) | 5KG Load Cell - Weight Sensor | 1 | 131.00 | 131.00 | https://quartzcomponents.com/products/load-cell-5kg-with-hx711-a-d-module-weight-sensor | 2026-10-04 | quartzcomponents product data |
| Load-cell amplifier | HX711 Load Cell Amplifier Module | 1 | 38.00 | 38.00 | https://quartzcomponents.com/products/hx711-load-cell-amplifier-module | 2026-10-04 | quartzcomponents product data |
| Water-level changes (optional 'tide') | 12V Mini Submersible Water Pump – 10 L/min, 8W | 1 | 278.00 | 278.00 | https://robocraze.com/products/12v-mini-submersible-water-pump | 2026-10-04 | robocraze product data |

**Subtotal: {{f:D05|₹4,969.12}}.** Whole flume demonstrator (4B + 4C): **{{f:D06|₹38,927.11}}**. Not priced: acrylic solvent cement, silicone sealant, cord, a wooden carriage, SS 316 fasteners, a 12 V supply for the winch (UNVERIFIED). Test plastics are collected, not bought.

### 4D. Software and cloud
Open-source stack (Python, ultralytics, Leaflet). Free data APIs (Open-Meteo; NASA POWER). A static dashboard plus hourly batch jobs. Cloud cost per site is not estimated yet (UNVERIFIED).

## 5. Power (field node)
Design month is July, Mumbai's darkest: {{f:F15|3.79 kWh/m²/day}} of insolation vs {{f:F15|7.09}} in May (NASA POWER). The sizing method and three load profiles (continuous inference, duty-cycled, on-sensor inference) are in [`../research/components/sensing-edge-bom.md`](../research/components/sensing-edge-bom.md) §1. Their loads are ASSUMPTIONS until we measure the node on the bench with a USB power meter.

## 6. Build schedule (around the 10 Oct zonal and the 19–25 Nov exams)
| Window | Work | Owner |
|---|---|---|
| 4–9 Oct | Software live (twin, dashboard, records, detector). Optional: a two-hour tabletop reversal test (box, hand-pulled boom, film pieces, phone video) for T2 evidence | lead + a hands-on teammate |
| 10 Oct | Zonal pitch, if Theme 3 is chosen | team |
| 11–25 Oct | Buy parts (4B, 4C); build the tow tank; run T1–T3 and T6 | hardware teammate(s) |
| 26 Oct – 10 Nov | Node over the flume (T4, T5); live telemetry into the twin; fuse abuse tests (repeated cycles, salt water, grit, cloth tangles) | team |
| 11–17 Nov | Freeze prototype; record demo video; draft report | team |
| 19–25 Nov | **Exams: no user-dependent work** | — |
| 26 Nov – 1 Dec | Final report (solution, prototype evidence, cost and market, implementation, scalability, impact), submitted by the team leader | team leader |
| 15–18 Dec | Finals: live tow-tank flume + dashboard | team |

## 7. What is real, what is simulated (status 4 Oct)
- **Real:** hourly ERA5 rain; archived JMA forecasts; tide fitted to Open-Meteo Marine sea level (RMSE {{r:tide_rmse_mithi}} m at the Mithi); public detection data.
- **SIMULATED:** every boom state and escaped kilogram at Mumbai sites. Held-out 2024–25, paired over {{r:n_draws}} draws:
  - tide-aware vs clear-when-full: {{r:p2p1_med}} escaped (interval {{r:p2p1_lo}} to {{r:p2p1_hi}});
  - vs the fixed schedule: {{r:p2p0_med}} (interval {{r:p2p0_lo}} to {{r:p2p0_hi}}).
- **SENSITIVITY:** fuse alone {{r:fuse_med}}; one-way pocket halving re-float {{r:pk5_med}}.
- **SYNTHETIC:** evidence-record tests catch inflated claims at {{r:mrv_recall}} with {{r:mrv_ff}} false flags; tamper detection {{r:mrv_tamper}}.
- **BUILT detector:** {{r:det_line}}
- Reproduce commands: [`../eval/RESULTS.md`](../eval/RESULTS.md).

## 8. Field pilot (after the prototype; needs permission)
2–3 small outfalls in one ward, one flap-gated and one open tidal, away from the Interceptor sites at Malad and Trombay. We would measure:
- pocket fill (camera + range sensor);
- weighbridge kg per clearance;
- random sort samples for the dry-plastic fraction;
- **tagged-item releases** upstream, to measure flux-weighted capture efficiency across tide and flow states.

MCGM Storm Water Drain department permission is required; The Ocean Cleanup obtained such permits for its sites. Crews do no work during red alerts and never enter flowing channels.

## 9. Risks
| Risk | Mitigation |
|---|---|
| Flaps foul with hyacinth, rags or silt | Abuse tests with cloth and grit; flap check in the crew list; drop the retention claim if T2 fails |
| The fuse opens at peaks by design | Pocket outside the fuse path; report FWCE honestly; dispatch empties pockets before forecast surges |
| Camera blind at night, in rain and glare | Range sensor is the primary fill reading; health flags |
| Monsoon power deficit | July-sized panel and battery; duty-cycled inference |
| Theft or vandalism | Pole mount above reach; tamper flag; GPS |
| Simulation circularity | Relative claims only; Monte Carlo; archived forecasts; tow-tank calibration (T2, T6); tagged-item field releases |

## 10. Needs from the user
- A teammate with fabrication skills for the tow tank and the node.
- Approval to buy 4B + 4C ({{f:D06|₹38,927.11}}) and, for a field pilot, one node ({{f:D04|₹83,481.98}}).
- Team details for the report.
