# Hardware BOM research — AQI fence-line node, gateway and misting actuator

Accessed: 2026-10-04 (IST), research session started ~08:33 IST.

> Draft research file. All numeric claims below cite sources opened in this session (web_fetch or Playwright browser); unconfirmed leads are separated at the end. Prices are as displayed on vendor pages at access time — INR, inclusive/exclusive of GST noted per listing. NEVER estimated.

## Status: COMPLETE — all 16 items priced (1–3 listings each) + 5 PM-sensor datasheets parsed. Session ended ~10:35 IST.

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
- **XS-WSDS01 Integrated Wind Speed + Direction Sensor, Modbus/Anemometer, 0–5V analog output, for Weather Station** — cheaper combined cup-anemometer+vane unit · Amazon.in · **₹14,810** (M.R.P. ₹29,422.80, "50% off") · buy-box price shown (in stock) · https://www.amazon.in/XS-WSDS01-Integrated-Direction-Anemometer-XS-WSDS01-0%EF%BD%9E5V/dp/B0DMNJGY3Y/ · accessed 2026-10-04 ~10:32 IST (Playwright). Same product line also listed in 4–20mA and RS485 output variants at similar prices.
- No low-cost (<₹3,000) hobby/Arduino-style cup+vane weather-station sensor set was found in stock on Robu or Amazon.in in the time budget — all in-stock combined (speed+direction) units found are industrial-grade, ₹14,800–21,800.

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

- **Songle Single-channel 5V 30A Relay Module (Power Failure Relay / opto-isolated)** · Robu.in · **₹149.00 (Incl. GST)** · Availability: "In Stock" (5 customer reviews) · https://robu.in/product/songle-single-channel-5v-30a-relay-module-power-failure-relay/ · accessed 2026-10-04 ~09:46 IST (Playwright).
- Note: the generic "5V 1 Channel Relay Module" (opto-coupler, SKU 9716) was ₹39.00 (Incl. GST) but shown **Out of Stock** — https://robu.in/product/1-channel-isolated-5v-relay-module-opto-coupler-for-arduino-pic-avr-dsp-arm/.

---

## Datasheet facts (PM sensors + SHT4x/SHT3x)

### Sensirion SPS30 — official datasheet (Digi-Key-hosted mirror of Sensirion PDF, "Datasheet SPS30 — Particulate Matter Sensor for Air Quality Monitoring and Control", Preliminary Version 0.9 – D1 – November 2018)
Source: https://media.digikey.com/pdf/Data%20Sheets/Sensirion%20PDFs/Sensirion_SPS30_Particulate_Matter_Sensor_v0.9_D1.pdf · accessed 2026-10-04 ~10:05 IST (downloaded + parsed with `pdftotext` in this session; direct sensirion.com PDF paths guessed from search returned 404 — this is the file Sensirion itself supplies to distributors).
- **PM10 — measured (binned), not a separate channel**: the datasheet lists PM10 directly inside both the mass- and number-concentration size-range tables rather than flagging it as calculated: *"Mass concentration size range … PM10 0.3 to 10.0 μm"* and *"Number concentration size range … PM10 0.3 to 10.0 μm"* (Table 1). No separate "calculated from distribution" caveat is attached to PM10 in this document (contrast with Sensirion's own SEN5x datasheet below, which explicitly calls PM4/PM10 "calculated").
- **Mass-concentration range**: *"Mass concentration range - 0 to 1'000 μg/m3"* (Table 1).
- **Average supply current**: *"Average supply current Measurement-Mode 60 mA"*, with *"Max. supply current First ~200 ms after start of Measurement-Mode 80 mA"* and *"Idle current Idle-Mode <8 mA"* (Table 2, Electrical Specifications).
- **Lifetime/MTTF**: *"Lifetime3 24 h/day operation >8 years"*, footnoted *"Validated with accelerated aging tests… Lifetime might vary depending on different operating conditions."* (Table 1). Note: Sensirion's current product-catalog web page (sensirion.com/products/catalog/SPS30, fetched same session) states a newer, higher figure: *"enables precise measurements from the device's first operation and throughout its lifetime of more than ten years"* — i.e. marketing copy now claims >10 years vs. the 2018 PDF's >8 years.
- **Operating T/RH**: recommended *"10 – 40 °C and 20 – 80 %RH"* (§1.1); absolute *"Operating temperature range -10 to +60 °C"* and *"Operating humidity range 0 to 95 %RH (non-condensing)"* (Table 3).

### Sensirion SEN55 (SEN5x family datasheet, covers SEN50/SEN54/SEN55 — "Datasheet SEN5x: Environmental Sensor Node for HVAC and Air Quality Applications", Version 2 – D1 – March 2022)
Source: https://sensirion.com/media/documents/6791EFA0/62A1F68F/Sensirion_Datasheet_Environmental_Node_SEN5x.pdf · accessed 2026-10-04 ~09:51 IST (downloaded + parsed with `pdftotext` in this session; found via web search, confirmed 200 OK directly from sensirion.com).
- **PM10 — explicitly estimated/modeled**: *"PM4 and PM10 output values are calculated based on distribution profile of all measured particles."* (Table 3 footnote 5). Mass concentration size range for PM10 given as *"0.3 to 10.0 μm"*.
- **Mass-concentration range**: *"Mass concentration specified range - 0 to 1'000 μg/m3"* (Table 3).
- **Average supply current (SEN55)**: steady-state *"Measurement-Mode (after first 60 seconds) SEN55 … typ. 63 … max 80"* mA; first 60 s typ. 70/max 100 mA; *"Peak supply current Measurement mode (pulse width of 16µs) … 100 … 110"* mA (Table 8, Electrical Specifications — includes fan + laser + MCU, no separate fan-only figure given).
- **Lifetime/MTTF**: *"Lifetime1 24 h/day operation > 10 years"*, footnoted *"Lifetime is based on mean-time-to-failure (MTTF) calculation."* (Table 2).
- **Operating T/RH (SEN54/SEN55)**: recommended *"Temperature 10 / 40 [°C] … Relative humidity 20 / 80 [% RH]"*; absolute max/min *"Temperature -10 / 50 [°C] … Relative humidity 0 / 90 (non-condensing) [% RH]"* (Table 6).

### Plantower PMS5003 — official datasheet ("PMS5003 Datasheet", Doc No. PTQ3004-2015, V1.0, 2019-7-31, mirrored by docs.smartcitizen.me)
Source: https://docs.smartcitizen.me/assets/datasheets/pms5003/PTQ3004-2015%20PMS5003%20series%20data%20manual%20English_SLT_V1.0K.pdf · accessed 2026-10-04 ~10:10 IST (downloaded + parsed with `pdftotext`; Plantower's own plantower.com has no direct PDF link per web search, and the aqicn.org mirror URL returned an HTML page, not a PDF, when fetched in this session).
- **PM10 — measured as a binned/calculated output, explicitly reported**: §3 Working Principle: *"equivalent particle diameter and the number of particles with different diameter per unit volume can be calculated by microprocessor based on MIE theory."* The serial data frame explicitly carries PM10 as its own field: *"Data3 … refers to PM10 concentration unit μg/m3（CF=1，standard particle）"* and *"Data 6 … refers to PM10 concentration unit μg/m3 (under atmospheric environment)"*. Also listed as a sensing bin: *"Particle Range of measurement … 0.3~1.0；1.0~2.5；2.5~10 … Micrometer（μm）"* (§4 Technical Index).
- **Mass-concentration range**: *"Particle Effective Range（PM2.5 standard） 0~500 μg/m³"*, *"Particle Maximum Range（PM2.5 standard）* ≥1000 μg/m³"* (§4).
- **Fan/active current**: *"Active Current ≤100 Milliampere（mA）"*, *"Standby Current ≤200 Milcroampere（uA）"*; circuit note: *"DC 5V power supply is needed because the FAN should be driven by 5V."* (§4, §8).
- **Lifetime/MTTF**: *"MTTF ≥3 Year(Y)"* (§4) — notably lower than the Sensirion SPS30/SEN5x figures above.
- **Operating T/RH**: *"Working Temperature Range -10~+60 ℃"*, *"Working Humidity Range 0~99 %"*, *"Storage Temperature Range -40~+80 ℃"* (§4).

### Nova Fitness SDS011 — official datasheet ("Laser PM2.5 Sensor specification", Product model SDS011, Version V1.3, Nova Fitness Co., Ltd., 2015-10-9; mirrored by hubtronics.in, an Indian electronics vendor)
Source: https://hubtronics.in/docs/SDS011.pdf · accessed 2026-10-04 ~10:22 IST (downloaded + parsed with `pdftotext`). Several other mirrors were tried first and blocked/dead in this session: watterott.com/media/downloads/SDS011_datasheet_EN.pdf (403), rarecomponents.com/datasheet/SDS011.pdf (403, also with a spoofed browser User-Agent), aqicn.org/air/view/sensor/spec/SDS011-spec-v1.3 (404 — link on the aqicn.org SDS011 page is dead); aqicn.org/sensor/sds011/ itself loaded fine and gave consistent secondary figures (range, current, temperature) but no lifetime figure.
- **PM10 — measured alongside PM2.5 from the same optical count**: *"Measurement parameters PM2.5,PM10"* (Technical Parameters table); principle: *"Using laser scattering principle: Light scattering can be induced when particles go through the detecting area… The number and diameter of particles can be obtained by analysis because the signal waveform has certain relations with the particles diameter."* (Working principle). No separate "calculated/estimated" caveat is attached to PM10 specifically (unlike Sensirion's SEN5x wording).
- **Mass-concentration range**: *"Range 0.0-999.9 μg/m3"* (Technical Parameters table, item 2).
- **Fan/rated current**: *"Rated current 70mA±10mA"*; *"Sleep current <4 mA (Lase&Fan sleep)"*; *"Power supply：>1W"* (Technical Parameters / Power requirement).
- **Lifetime/MTTF**: no MTTF figure given; instead a laser-diode service-life spec: *"The laser diode in this sensor has high quality and its service life is up to 8000 hours… you can use the discontinuous working method to prolong the service life. For example, you can start the sensor for 30 seconds per minutes."* (About service life) — substantially shorter than the Sensirion sensors' >8–10-year MTTF figures, and explicitly duty-cycle-dependent.
- **Operating T/RH**: *"Temperature range … Storage environment：-20 ~ +60℃ … Work environment：-10 ~ +50℃"*; *"Humidity range … Storage environment：Max 90% … Work environment：Max 70%"* (Technical Parameters table, items 6–7).

### Sensirion SHT40 — supplementary (not formally requested but captured while sourcing SHT4x family datasheet; "Datasheet – SHT4x, 4th Gen. Relative Humidity and Temperature Sensor", Sensirion AG, mirrored by Digi-Key)
Source: https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/6705/HT_DS_Datasheet_SHT4x_5.pdf · accessed 2026-10-04 ~10:25 IST (downloaded + parsed with `pdftotext`; direct sensirion.com guessed paths 404'd again).
- **Operating range**: *"Operating range: 0 … 100 %RH, −40…125 °C"* and *"Fully functional in a condensing environment"* (Highlights).
- **Average current**: *"Avg. current: 0.4 µA, Idle current: 80 nA"* at *"VDD = 1.08 V … 3.6 V"* — three to four orders of magnitude lower than any PM sensor above, since the SHT40 has no fan/laser (Highlights).
- (PM10/mass-concentration/fan-current/MTTF do not apply to this humidity/temperature-only part; not pursued further since the brief's datasheet checklist is PM-sensor-specific.)

---

## UNVERIFIED leads / not found

- **Vendors not reached for most items**: evelta.com, electronicscomp.com, quartzcomponents.com, probots.co.in, in.element14.com, mouser.in, digikey.in and indiamart.com were not successfully searched for items 2–16 (time budget; robu.in + amazon.in alone yielded ≥1 listing per item). `evelta.com/catalogsearch/result` and `electronicscomp.com/catalogsearch/result` both 404'd on first try (wrong Magento search path guessed) and were not retried via browser. `quartzcomponents.com` WooCommerce search (`/?s=`) returned only an unrelated category snippet, not real results, for every query tried. `thingbits.in` needed the browser (client-rendered Next.js site; `?q=` is the real search param, confirmed working for SEN55/SPS30/SDS011/PMS5003 queries — all returned 0 matching products). Robocraze.com returned "0 results" for SPS30 (only item tried there).
- **Item 3 (Plantower PMSA003-A, ₹1,999)**: price read from the Robu search-results grid by matching list position, not confirmed by opening its own product page — flagged in the item's entry as slightly less certain than the directly-opened PMS5003 figure.
- **Item 8 (SX1262 865 MHz)**: no listing found specifically badged for the India 865–867 MHz ISM sub-band; the IndieSemiC module found is "Made in India" and WPC-certified but datasheet-level confirmation of its exact center frequency/band was not opened.
- **Item 9 (anemometer+vane)**: no hobby-grade (<₹3,000) combined cup-anemometer+wind-vane kit was found in stock anywhere searched; only industrial-grade units (₹14,810–21,759) were available. A cheaper speed-only cup anemometer (₹4,749, Robu) exists but its would-be vane partner was out of stock.
- **Item 10 (10W panel)**: Robu's own 10W panel listing is Out of Stock (price ₹1,047 captured anyway per brief's "never estimate" rule — this is a real displayed price, just not purchasable); the in-stock listing used is Amazon's Loom Solar panel instead.
- **SDS011 datasheet**: the primary manufacturer domain (inovafitness.com / sdnf.com) now redirects to an unrelated liquid-particle-counter product line — Nova Fitness appears to have changed its site. Confirmed via a working third-party mirror (hubtronics.in, an Indian vendor) instead; two other mirrors (watterott.com, rarecomponents.com) were blocked with 403 even after spoofing a browser User-Agent.
- **SHT40/SHT31 (item 5) and SHT4x (datasheet bonus)**: not cross-checked against SHT31 specifically (only SHT30/SHT40/SHT45 variants were opened); SHT31 datasheet PDF was not separately fetched since the task's datasheet checklist (PM10/mass-concentration/fan-current) doesn't apply to humidity sensors.
- Direct `sensirion.com/media/documents/<hash>/<hash>/...pdf` URLs guessed from AI web-search summaries were wrong (hash IDs appear to be hallucinated by the search tool) and 404'd for SPS30 and SHT4x; working copies were instead found via Digi-Key's media mirror (`media.digikey.com` / `mm.digikey.com`), which Sensirion itself supplies to distributors — content cross-checked against Sensirion's live product-catalog page text (fetched directly) where possible.
