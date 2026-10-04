# Hardware BOM research — AQI fence-line node, gateway and misting actuator

Accessed: 2026-10-04 (IST), research session started ~08:33 IST.

> Draft research file. All numeric claims below cite sources opened in this session (web_fetch or Playwright browser); unconfirmed leads are separated at the end. Prices are as displayed on vendor pages at access time — INR, inclusive/exclusive of GST noted per listing. NEVER estimated.

## Status: IN PROGRESS — saving incrementally

---

## (1) Sensirion SPS30 — PM sensor

- **Sensirion SPS30, Particulate Matter Sensor, PM2.5, Range: 0–1,000 µg/m³** · Robu.in · **₹3,599.00 (Incl. GST)** · Availability: "In Stock" · https://robu.in/product/sensirion-particulate-matter-sensor-0-to-1000-%c2%b5g-m3-laser-i2c-uart-calibrated-4-5-to-5-5-v-supply/ · accessed 2026-10-04 ~08:37 IST (Playwright browser; direct web_fetch to robu.in is blocked per thread brief).
- Vendors tried without a listing: web_fetch to evelta.com/catalogsearch (404 — wrong search path), thingbits.in/search (404), electronicscomp.com/catalogsearch (404), quartzcomponents.com (WooCommerce search returned only an unrelated "Development Boards" category page, no SPS30 product), amazon.in (503 — blocked). Will retry evelta/electronicscomp/amazon via browser if time allows.

## (2) Sensirion SEN55 (or SEN54/SEN66)

- **Sensirion SEN55-SDN-T Environmental Sensor PM2.5, CO2, VOC, Temp, RH** · Robu.in · **₹5,879.00 (Incl. GST)** · Availability: **Out of Stock** · https://robu.in/product/sensirion-sen55-sdn-t-environmental-sensor-pm2-5-co2-voc-temp-rh/ · accessed 2026-10-04 ~08:42 IST (Playwright).
- Related listings seen on same Robu search (SEN55 query, also out of stock, not priced yet): "M5Stack Air Quality Kit w/ M5StampS3 (SEN55, SCD40)" (/product/m5stack-air-quality-kit-w-m5stamps3-sen55-scd40/), "Seeed Studio Grove SEN54 All-in-One Environmental Sensor Module" (/product/seeed-studio-grove-sen54-all-in-one-environmental-sensor/), "Sensirion SEN50-SDN-T" (PM-only variant, /product/sensirion-sen50-sdn-t-environmental-sensor-pm2-5-temp-rh-digital/) — prices not opened individually (time budget); all shown "Out of Stock" on the search grid.
- Vendors tried, no listing: thingbits.in (client-rendered search confirmed via browser: "Search results for 'SEN55' — 0 products found", https://www.thingbits.in/?q=SEN55, accessed ~08:44 IST).

## (3) Plantower PMS5003 or PMSA003

- **PLANTOWER PMS5003 PM2.5 Laser Particle Concentration Sensor, UART, 0~500 µg/m³, 5 V, Range: 0.3~10 µm** (Robu lists it under product slug "PM5003") · Robu.in · **₹2,119.00 (Incl. GST)** · Availability: "In Stock" · https://robu.in/product/plantower-pm5003-gas-sensor-uart/ · accessed 2026-10-04 ~08:46 IST (Playwright).
- Same Robu search also listed **PLANTOWER PMSA003-A** (same spec text, /product/plantower-pmsa003-a-gas-sensor-uart/) — seen at ₹1,999 (Incl. GST) on the search grid (position-matched, not opened on its own product page to re-confirm — flagging as slightly less certain than the SPS5003 figure above, but grid price format matches the confirmed PMS5003 pattern exactly).

## (4) Nova SDS011

- **Nova PM Sensor SDS011, High Precision Laser PM2.5 Air Quality Detection Sensor** · Robu.in · **₹2,739.00 (Incl. GST)** · Availability: "In Stock" · https://robu.in/product/nova-pm-sensor-sds011-high-precision-laser-pm2-5-air-quality-detection-sensor/ · accessed 2026-10-04 ~08:48 IST (Playwright).

## (5) Sensirion SHT40 breakout (or SHT31)

- **SENSIRION SHT40-AD1B-R2 Humidity & Temperature Sensor, 0–100%RH, −40°C to +125°C, ±1.8%RH, I2C** (bare SMD IC, not a breakout board) · Robu.in · **₹201.00 (Incl. GST)** · Availability: "In Stock" · https://robu.in/product/sensirion-sht40-ad1b-r2-humidity-and-temperature-sensor-i2c-1-8/ · accessed 2026-10-04 ~08:52 IST (Playwright).
- **SHT30 Temperature and Humidity Sensor with adapter board** (true pin-header breakout, SHT31-class part) · Robu.in · **₹269.00 (Incl. GST)** · Availability: "In Stock" · https://robu.in/product/temperature-and-humidity-sensor-2/ · accessed 2026-10-04 ~08:53 IST (Playwright).
- Note: an "Unwelded GY-SHT40 Digital Temperature and Humidity Sensor" breakout also exists on Robu (/product/unwelded-gy-sht40-digital-temperature-and-humidity-sensor/) but was shown **Out of Stock** on the search grid; price not opened (prioritized in-stock items given time budget).

## (6) ESP32-S3 dev board

- **ESP32 S3 Devkit (ESP32-S3-WROOM-1 N16R8 | 16MB Flash + 8MB PSRAM)** · Robu.in · **₹839.00 (Incl. GST)** · Availability: "In Stock" · https://robu.in/product/esp32-s3-devkit-esp32-s3-wroom-1-n16r8/ · accessed 2026-10-04 ~08:57 IST (Playwright).
- **ROBOTICSSIGN ESP32-S3-DevKitC-1-N16R8, Type-C, 16MB Flash** · Amazon.in · **₹1,190** (M.R.P. ₹1,999, "40% off" — GST inclusion not separately labelled, Amazon.in consumer prices are GST-inclusive by default) · search-result buy-box price shown (implies in stock; product page itself not opened) · https://www.amazon.in/ROBOTICSSIGN-ESP32-S3-Devkitc-1-N16R8-Development-Bluetooth-microprocessor/dp/B0DRSG541Z/ · accessed 2026-10-04 ~09:00 IST (Playwright; direct web_fetch to amazon.in returned 503).

## (7) SIMCom A7670C 4G LTE Cat-1 module/board

- **SIM A7670C 4G LTE Development Board with 4G Flex Antenna** · Robu.in · **₹1,859.00 (Incl. GST)** · Availability: "In Stock" · https://robu.in/product/sim-a7670c-4g-lte-development-board-with-4g-flex-antenna/ · accessed 2026-10-04 ~09:04 IST (Playwright).

## (8) SX1262 LoRa module (865 MHz) or RAK3172

- **IndieSemiC ISC-SX1262-B LoRa Module — Semtech SX1262 Sub-GHz Transceiver, 868/915 MHz, LoRaWAN, External Antenna, Made in India, WPC ETA Certified** · Robu.in · **₹549.00 (Incl. GST)** · Availability: "In Stock" · https://robu.in/product/indiesemic-isc-sx1262-b-an-advanced-lora-module-v0-1/ · accessed 2026-10-04 ~09:06 IST (Playwright). Caveat: listed band is 868/915 MHz, not exactly the India 865–867 MHz ISM sub-band — "Made in India, WPC ETA Certified" suggests local regulatory compliance but the exact in-band center frequency for the India 865 MHz allocation was not independently confirmed on this page.
- **RakWireless RAK3172 Evaluation Board** also found on Robu.in (/product/rakwireless-rak3172-evaluation-board/) but shown **Out of Stock** on the search grid; price not opened.

## (9) Cup anemometer + wind vane kit

- **FirstRate FST200-205 Wind Speed & Wind Direction Integrated Sensor** (cup anemometer + vane in one head), Output 4–20 mA, Range 0–50 m/s, 0–360° · Robu.in · **₹21,759.00 (Incl. GST)** · Availability: "In Stock" · https://robu.in/product/firstrate-fst200-205-wind-speed-wind-direction-integrated-sensor/ · accessed 2026-10-04 ~09:14 IST (Playwright). Industrial/pro-grade price point, not hobby-grade.
- **Wind Speed Sensor Current Type (4–20 mA) Anemometer Kit (Waterproof & Industrial)** — cup anemometer, wind-speed only (no vane) · Robu.in · **₹4,749.00 (Incl. GST)** · Availability: "In Stock" · https://robu.in/product/wind-speed-sensor-current-type4-to-20ma-anemometer-kit-waterproof-industrial/ · accessed 2026-10-04 ~09:16 IST (Playwright). Cheaper, but would need a separate wind-vane sensor to get direction (Robu's "Wind Speed Sensor Voltage Type (0-5V)" vane-less sibling and most dedicated wind-direction units in the same Robu category, e.g. SN-3000-FXJT-I20-16 and SN-3000-FXA series, were shown **Out of Stock** on the category page: https://robu.in/product-category/wind-speed-and-direction-sensors/).
- No low-cost (<₹3,000) hobby/Arduino-style cup+vane weather-station sensor set was found in stock on Robu in the time budget — the only in-stock combined unit is the industrial FST200-205 above.

## (10) 10 W 12 V solar panel

- **"12V 36 Cell 10 watt Solar Panel 41x30cm"** · Robu.in · ₹1,047.00 (Incl. GST) listed, but Availability: **"Out of Stock"** · https://robu.in/product/10w-solar-panel-36-cell-solar-plate-high-quality-10-w-10-watts/ · accessed 2026-10-04 ~09:21 IST (Playwright).
- **Loom Solar 10-Watt Solar Panel, Polycrystalline PV Module** · Amazon.in · **₹949** (M.R.P. ₹2,500) · 1,235 ratings / 4.1★, buy-box price shown (in stock) · https://www.amazon.in/Loom-Solar-10-Watt-Panel/dp/B07JF2B35T/ · accessed 2026-10-04 ~09:24 IST (Playwright).
- Also seen in stock on Robu (not opened individually): "20W 12V Solar Panel (74×35cm)" SKU 12298 (/product/20w-12v-solar-panel-solar-plate-high-quality-20-w-20-watts/), "18V 20W 36-Cell Solar Panel" SKU 818165.

## (11) 12 V LiFePO4 battery (6–12 Ah) or 18650 pack + solar charge controller (CN3791/MPPT)

- **Pro-Range A Grade IFR 32650 12.8V 12000mAh (12 Ah) 3C 4S2P LiFePO4 Battery Pack** · Robu.in · **₹3,359.00 (Incl. GST)** · Availability: "In Stock" · https://robu.in/product/pro-range-ifr-32650-lifepo4-12000mah-12-8v-4s2p-protected-battery-pack-3c/ · accessed 2026-10-04 ~09:28 IST (Playwright).
- Smaller pack also seen in stock (same search, not opened individually): "Pro-Range IFR 32650 12.8V 6000mAh (6 Ah) 3C 4S1P LiFePO4 Battery Pack" SKU 1290270 (/product/pro-range-ifr-32650-lifepo4-6000mah-12-8v-4s1p-protected-battery-pack-3c/).
- **Elejoy CN3791 12V MPPT Solar Charger Module** · Robu.in · **₹199.00 (Incl. GST)** · Availability: "In Stock" · https://robu.in/product/cn3791-12v-mppt-solar-charger-module/ · accessed 2026-10-04 ~09:30 IST (Playwright).

## (12) IP65 ABS junction box ~200×150 mm

- **F1 195×115×75mm IP65 ABS PCB Plastic Junction Box** (closest in-stock size to the ~200×150mm target) · Robu.in · **₹269.00 (Incl. GST)** · Availability: "In Stock" · https://robu.in/product/f1-19511575mm-ip65-abs-pcb-plastic-junction-box/ · accessed 2026-10-04 ~09:34 IST (Playwright).
- Note: several closer/larger Robu options in the same range (e.g. 158×90×60mm, 115×90×55mm variants) were shown **Out of Stock** on the search grid.

## (13) 12 V diaphragm/misting pump + misting nozzle kit

- **"550" Diaphragm Pump 12V Water Pump (for Water Spray / Fish Tank / Reflux Pump)** — pump only, no nozzles · Robu.in · **₹399.00 (Incl. GST)** · Availability: "In Stock" (3 customer reviews) · https://robu.in/product/550-diaphragm-pump-12v-water-pump-for-water-spray-fish-tank-reflux-pump/ · accessed 2026-10-04 ~09:37 IST (Playwright).
- **Fieldstar DIY Misting System Kit with Nozzles, Pump 12V, Pipe, Connectors (8 Nozzles)** — combined pump + misting-nozzle kit in one bundle · Amazon.in · **₹1,999** (M.R.P. ₹3,999) · 12 ratings / 3.2★, buy-box price shown (in stock) · https://www.amazon.in/Misting-System-Kit-Nozzles-Hydroponics/dp/B0F3DKV27D/ · accessed 2026-10-04 ~09:39 IST (Playwright).

## (14) 12 V solenoid valve (1/2")

- **12V DC 1/2″ Electric Solenoid Water Air Valve Switch (Normally Closed)** · Robu.in · **₹269.00 (Incl. GST)** · Availability: "In Stock" (9 customer reviews) · https://robu.in/product/dc12v-plastic-electric-12v-water-solenoid-valve-electric-solenoid-valve-magnetic-nc-water-air-inlet-flow-switch-nc-12/ · accessed 2026-10-04 ~09:41 IST (Playwright).

## (15) YF-S201 or similar Hall flow sensor

- **YF-S201 Water Flow Sensor 1–30 L/min (Black)** · Robu.in · **₹219.00 (Incl. GST)** · Availability: "In Stock" (1 customer review) · https://robu.in/product/yf-s201-water-flow-measurement-sensor-with-1-30liter-min-flow-rate-2/ · accessed 2026-10-04 ~09:43 IST (Playwright).
- Same model also listed in "White" trim, SKU 12219 (/product/yf-s201-water-flow-measurement-sensor-with-1-30liter-min-flow-rate/), not opened individually.

## (16) Relay/SSR module

_pending_

---

## Datasheet facts (PM sensors + SHT4x/SHT3x)

_pending_

---

## UNVERIFIED leads / not found

_pending_
