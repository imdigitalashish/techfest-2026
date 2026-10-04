# Sensing + edge AI node — specs, power, connectivity, BOM (InnovateX T3)

Owner: T3 research worker (tech + companies). Sources opened **2026-10-04**. Vendor specs are *(claims)*. Estimates are labelled **ESTIMATE/ASSUMPTION**. Missing data: **NOT FOUND / UNVERIFIED**.

## 1. Solar resource at Mumbai — NASA POWER climatology (real API pull)
Query (opened 2026-10-04): https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=ALLSKY_SFC_SW_DWN&community=RE&longitude=72.85&latitude=19.07&format=JSON — parameter ALLSKY_SFC_SW_DWN (all-sky surface shortwave downward irradiance), units **kW-hr/m^2/day** (horizontal surface, long-term monthly climatology as returned by the API).

| Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec | Annual |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4.8833 | 5.7439 | 6.5887 | 7.0786 | 7.0942 | 5.0006 | **3.7920** | 4.0363 | 4.7818 | 5.2109 | 4.8430 | 4.5336 | 5.2942 |

- Design month = **July (3.79 kWh/m²/day ≈ 3.79 peak-sun-hours)**, i.e. 53% of the May peak — and July is exactly when nullahs carry the most plastic. Size for July, not the annual mean.
- Caveat: a monthly mean hides runs of dark monsoon days; battery autonomy (below) covers that. Values are horizontal; a fixed 15–20° south tilt changes monsoon yield little (diffuse-dominated) — **ASSUMPTION**, not computed here.

### Sizing formula (ESTIMATE — reproducible)
`P_panel_W = E_load_Wh_per_day / (PSH_July × η_system)`, `C_batt_Wh = E_load_Wh_per_day × autonomy_days / DoD`, with η_system = 0.65 (PWM/MPPT, temperature, soiling, battery round-trip — **ASSUMPTION**), DoD = 0.8 for LiFePO4 (**ASSUMPTION**), autonomy = 3 days (**ASSUMPTION** for monsoon).

| Profile | Avg load (ASSUMPTION) | E_load Wh/day | Panel W (July) | Pick | Battery Wh (3 days) | Pick |
|---|---:|---:|---:|---|---:|---|
| P1 — Pi 5 + AI HAT+ + camera + 4G, inference 24 h | 8 W | 192 | 192/(3.79×0.65) = **78 W** | 100 W | 192×3/0.8 = **720 Wh** | 12.8 V 60 Ah LiFePO4 (768 Wh) |
| P2 — duty-cycled: 2 min of video per 10 min in daylight + event-triggered; modem sleeps | 3 W | 72 | 72/(3.79×0.65) = **29 W** | 40 W | 72×3/0.8 = **270 Wh** | 12.8 V 24 Ah (307 Wh) |
| P3 — Raspberry Pi AI Camera (on-sensor inference) + Pi Zero 2 W class host + NB-IoT/LoRa telemetry | 1.5 W | 36 | 36/(3.79×0.65) = **15 W** | 20 W | 36×3/0.8 = **135 Wh** | 12.8 V 12 Ah (154 Wh) |

Average-load figures are **ASSUMPTIONS** pending the measured component power below; replace with a bench measurement (USB power meter) on the flume prototype.

## 2. Edge platform specs (opened sources)
| Item | Key spec (verbatim where quoted) | Source |
|---|---|---|
| Raspberry Pi AI HAT+ | "available in 13 and 26 tera-operations per second (TOPS) variants, built around the Hailo-8L and Hailo-8"; uses "Raspberry Pi 5's PCIe Gen 3 interface"; "Operating temperature: 0℃ to 50℃ (ambient)"; "List price: AI HAT+ 13 TOPS – $70 / AI HAT+ 26 TOPS – $110" | Product brief PDF https://datasheets.raspberrypi.com/ai-hat-plus/raspberry-pi-ai-hat-plus-product-brief.pdf |
| Raspberry Pi AI Camera | "Sensor: Sony IMX500"; "Resolution: 12.3 megapixels"; "Horizontal field of view: 66.3 ±3 degrees"; "Vertical field of view: 52.3 ±3 degrees"; "2×2 binned: 2028×1520 10-bit 30fps; Full resolution: 4056×3040 10-bit 10fps"; "Operating temperature: 0°C to 50°C"; runs the network on the sensor itself | Product brief PDF https://datasheets.raspberrypi.com/camera/ai-camera-product-brief.pdf |
| NVIDIA Jetson Orin Nano Super Dev Kit | "67 Sparse TOPs, 102 GB/s memory bandwidth, and a 1.7 GHz CPU clock speed at a reduced price of $249"; older kits unlock "MAXN power mode by upgrading to JetPack 6.1" | NVIDIA Technical Blog https://developer.nvidia.com/blog/nvidia-jetson-orin-nano-developer-kit-gets-a-super-boost/ |
| Indian street prices (same items) | AI HAT+ 13 TOPS ₹6,854 / 26 TOPS ₹10,350 (Quartz); AI Camera ₹8,339 (Robocraze) / ₹8,500 (Quartz); Jetson Orin Nano Super Dev Kit ₹54,999.99 (Think Robotics), ₹73,999 (Robocraze) | product pages listed in §5 |

- **0–50 °C ambient** limits for both Pi accessories matter: a sealed dark enclosure in Mumbai sun can exceed 50 °C inside → white/vented enclosure, sun shade, thermal throttling test (**risk**, not measured).
- **Choice:** Pi 5 + AI HAT+ 13 TOPS is the pilot default (₹ and W far below Jetson; Hailo runs YOLO-class detectors). Jetson only as a central 'reprocessing' box, not per outfall. The AI Camera (on-sensor inference) is the low-power option (profile P3) if a small detector fits the IMX500.
- Raspberry Pi 5 official pages (raspberrypi.com/products/...) returned HTTP 403 to automated fetch on 2026-10-04; Pi 5 power figures beyond the retailer title "Official Raspberry Pi 5 27W USB-C PD Power Supply" are **UNVERIFIED** here.

## 3. Level sensing (boom fill, water level, tide check)
- **DFRobot A02YYUW** (IP67-class waterproof ultrasonic; retailer title: "3-450cm"): ₹2,259 at Robocraze. DFRobot wiki https://wiki.dfrobot.com/_A02YYUW_Waterproof_Ultrasonic_Sensor_SKU_SEN0311 opened but the spec table did not render in text (**UNVERIFIED** beyond the retailer title).
- **JSN-SR04T-class** waterproof transducer: ₹295 (Quartz), ₹345 (Robocraze) — fine for the flume, not for field (exposed transducer, wide beam).
- **LiDAR (Benewake TFmini-S)**: retailer title "TFmini-S Lidar Ranging Sensor, 12m Ranging Distance", ₹5,699.99 (https://thinkrobotics.com/products/tfmini-s-lidar-ranging-sensor-12m-ranging-distance); Benewake family page lists "Consumption ＜ 5V × 100mA" and protection levels from IP5X to IP67 depending on model (https://en.benewake.com/TFminiS/index.html). Optical ranging on dark/foamy water is a known risk → treat as optional; ultrasonic + camera-estimated fill is the baseline.
- Recommended: one downward ultrasonic over open water (stage/tide), and boom fill from the camera (floating-mat area) — the camera already sees the boom.

## 4. Connectivity options in Mumbai
| Option | Evidence | Use |
|---|---|---|
| 4G LTE Cat-4 HAT (SIM7600E-H) | Retailer pages above (₹9,149.99) | Default for pilot: needed for event images/clips for MRV audit. Coverage at specific outfalls must be checked on site (**UNVERIFIED**). |
| LoRaWAN (Tata Communications public network) | Kerlink reference: Tata's rollout "followed a successful large-scale pilot in 2016 with several hundred Kerlink LoRaWAN® Wirnet™ Stations that covered 40 million people in three major cities in India: Mumbai, Delhi and Bengaluru"; coverage planned for "all cities with a population greater than 1 million by 2018" — https://www.kerlink.com/references-alliances/references/tata-communication/ . Current (2026) Mumbai coverage/tariff: **UNVERIFIED**. | Telemetry only (counts, level, battery) — not images. |
| NB-IoT / LTE-M | LoRa Alliance news repost (ET Telecom): "Vodafone Idea, Reliance Jio and Airtel are preparing to give a push to their Internet of Things business through narrowband IoT (NB-IoT)" — https://lora-alliance.org/lorawan-news/lorawan-vs-nbiot-how-tata-comm-senra-driving-indias-iot-space-as-telcos-wait-and-watch/ (older article; current Mumbai NB-IoT availability **UNVERIFIED**). SIM7080G NB-IoT/Cat-M HAT ₹3,199.99: https://thinkrobotics.com/products/sim7080g-hat | Telemetry fallback for profile P3. |

Design rule: send **counts + fill + level every 5 min** over the cheapest link; send **images only on events** (fill threshold, anomaly, audit sample) over 4G. Store-and-forward on SD for outages.

## 5. Bills of materials (INR, from Indian retailer product pages opened 2026-10-04)
Prices as shown on the retailer's product data on 2026-10-04; GST inclusion is not stated in the product data (**UNVERIFIED** — check at checkout). Items without an opened page are listed as ESTIMATE and kept out of subtotals.

### BOM A — pilot field node (one nullah outfall, solar profile P1)
| Function | Item (as listed by retailer) | Qty | Unit ₹ | Line ₹ | Retailer page (opened 2026-10-04) |
|---|---|---:|---:|---:|---|
| Compute | Raspberry Pi 5, 8GB variant (in stock; 4GB ₹16,199.99 out of stock) | 1 | 21,199.99 | 21,199.99 | https://thinkrobotics.com/products/raspberry-pi-5 |
| AI accelerator | Official Raspberry Pi AI HAT+ 13 TOPS (Hailo-8L) | 1 | 6,854.00 | 6,854.00 | https://quartzcomponents.com/products/official-raspberry-pi-ai-hat-13-tops |
| Camera | Raspberry Pi Camera Module 3 | 1 | 3,245.00 | 3,245.00 | https://robocraze.com/products/raspberry-pi-camera-module-3 |
| Backhaul (images + telemetry) | Waveshare SIM7600E-H 4G HAT for Raspberry Pi, LTE Cat-4, GNSS | 1 | 9,149.99 | 9,149.99 | https://thinkrobotics.com/products/sim7600e-h-4g-hat-for-raspberry-pi-lte-cat-4-4g-3g-2g-gnss |
| Water/boom-fill level | DFRobot A02YYUW waterproof ultrasonic distance sensor, 3–450 cm (retailer title) | 1 | 2,259.00 | 2,259.00 | https://robocraze.com/products/dfrobot-a02yyuw-waterproof-ultrasonic-distance-sensor |
| Solar | Loom Solar Mono PERC half-cut 55 Wp 12 V panel (x2 = 110 Wp for profile P1) | 2 | 2,200.00 | 4,400.00 | https://www.loomsolar.com/products/loom-solar-panel-55-watt-mono-crystalline |
| Storage battery | CAML 12.8 V 100 Ah (1.28 kWh) LiFePO4 — smallest 12.8 V LiFePO4 found on an opened Indian page; ~6.7 days of P1 autonomy | 1 | 34,500.00 | 34,500.00 | https://www.loomsolar.com/products/caml-10012-low-voltage-lithium-battery |
| Charge controller | 20A Digital PWM Solar Controller with LCD + USB (LiFePO4 profile support UNVERIFIED) | 1 | 339.00 | 339.00 | https://robocraze.com/products/20a-digital-pwm-solar-controller-with-lcd-and-usb-output-port |
| 12 V → 5 V | SmartElex TPS5430 buck module 5 V 3 A (below the official 5 V/5 A, 27 W PSU rating — bench-test; upgrade if brown-outs) | 1 | 335.00 | 335.00 | https://robocraze.com/products/smartelex-tps5430-buck-module-5v-3a-dc-dc-converter |
| **Subtotal (priced items)** | | | | **82,281.98** | |

Not priced from an opened page (**ESTIMATE**, excluded from subtotal): IP65/IP66 enclosure big enough for Pi 5 + HAT + 4G HAT (the only IP65 box found was 90×90×60 mm, ₹458 — too small: https://quartzcomponents.com/products/plastic-enclosure-90x90x60-mm-for-adapters-led-drivers-general-purpose-housing); microSD/SSD; GI pole + clamps; cable glands; surge/lightning protection; IR illuminator for night; installation labour; SIM data plan.
Cost levers: profile P2 (duty-cycled) needs one 55 Wp panel and a ~300 Wh pack instead of 1.28 kWh — the battery is ~50% of BOM A; a 4S LiFePO4 pack with a DALY 4S 12 V 40 A BMS (₹1,125, https://quartzcomponents.com/products/daly-lifepo4-4s-12v-40a-waterproof-battery-management-system-bms-protection-board) is the cheaper build-your-own route (cells not priced).

### BOM B — student flume prototype (bench, mains-powered)
| Function | Item (as listed by retailer) | Qty | Unit ₹ | Line ₹ | Retailer page (opened 2026-10-04) |
|---|---|---:|---:|---:|---|
| Compute | Raspberry Pi 5, 8GB | 1 | 21,199.99 | 21,199.99 | https://thinkrobotics.com/products/raspberry-pi-5 |
| AI accelerator | Official Raspberry Pi AI HAT+ 13 TOPS (same stack as the field node, so models transfer) | 1 | 6,854.00 | 6,854.00 | https://quartzcomponents.com/products/official-raspberry-pi-ai-hat-13-tops |
| Camera | Raspberry Pi Camera Module 3 | 1 | 3,245.00 | 3,245.00 | https://robocraze.com/products/raspberry-pi-camera-module-3 |
| Power | Official Raspberry Pi 5 27W USB-C PD power supply | 1 | 1,249.00 | 1,249.00 | https://robocraze.com/products/raspberry-pi-5-27w-usb-c-power-supply-black-colour |
| Level in flume | Waterproof ultrasonic distance transducer (JSN-SR04T class) | 1 | 295.00 | 295.00 | https://quartzcomponents.com/products/waterproof-ultrasonic-distance-transducer-sensor |
| Sensor/actuator MCU | ESP32 38-pin WiFi + Bluetooth NodeMCU dev board (pump/gate control, level logging) | 1 | 425.00 | 425.00 | https://robocraze.com/products/esp32-development-board |
| LPWAN demo link | SX1278 LoRa module Ra-02 433 MHz (pair; note India's LoRaWAN band is 865–867 MHz — use for bench demo only) | 2 | 345.00 | 690.00 | https://robocraze.com/products/sx1278-lora-module-ra-02-433mhz-wireless-spread-spectrum-transmission |
| **Subtotal (priced items)** | | | | **33,957.99** | |

Not priced (**ESTIMATE**, excluded): acrylic/PVC flume channel + submersible pump + valve; mock boom (PVC pipe + mesh skirt); tide simulator (second pump on a timer via the ESP32); plastic test items (real bags/sachets/bottles).
Cheaper variant: drop the AI HAT+ and use the Raspberry Pi AI Camera (₹8,339) for on-sensor inference → saves ₹6,854 + ₹3,245 − ₹8,339 = ₹1,760, at the cost of a smaller model.

Subtotal check (python): A = ₹82,281.98; B = ₹33,957.99.
