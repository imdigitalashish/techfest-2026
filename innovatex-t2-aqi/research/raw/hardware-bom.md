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

_pending_

## (5) Sensirion SHT40 breakout (or SHT31)

_pending_

## (6) ESP32-S3 dev board

_pending_

## (7) SIMCom A7670C 4G LTE Cat-1 module/board

_pending_

## (8) SX1262 LoRa module (865 MHz) or RAK3172

_pending_

## (9) Cup anemometer + wind vane kit

_pending_

## (10) 10 W 12 V solar panel

_pending_

## (11) 12 V LiFePO4 battery (6–12 Ah) or 18650 pack + solar charge controller (CN3791/MPPT)

_pending_

## (12) IP65 ABS junction box ~200×150 mm

_pending_

## (13) 12 V diaphragm/misting pump + misting nozzle kit

_pending_

## (14) 12 V solenoid valve (1/2")

_pending_

## (15) YF-S201 or similar Hall flow sensor

_pending_

## (16) Relay/SSR module

_pending_

---

## Datasheet facts (PM sensors + SHT4x/SHT3x)

_pending_

---

## UNVERIFIED leads / not found

_pending_
