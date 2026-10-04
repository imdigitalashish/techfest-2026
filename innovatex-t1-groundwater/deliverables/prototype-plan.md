# Prototype plan — JalSakshi RechargeMeter (Round 2, due 1 Dec 2026) — DRAFT v1

> Architecture: `architecture/components.md` (C0–C8). Spike rationale: `architecture/adr/001-spike.md`.
> **Price policy:** a price appears only if it was read on a vendor page tonight (URL + date). Everything else is **UNVERIFIED** and must be confirmed before purchase. The target BOM is an estimate, not a quote.

## 1. Architecture (field → cloud)
- **In the pit (submerged):**
  - sealed absolute pressure sensor (0–3 m water range; e.g. TE MS5837-30BA class, or a 4–20 mA stainless hydrostatic probe);
  - water-temperature reading from the same sensor;
  - slotted PVC stilling tube with a geotextile sock;
  - sensor on a stand 5–10 cm above the floor (silt line).
- **In the lid housing (above water):**
  - MCU + LoRa radio (RAK3172, STM32WLE5CC, LoRaWAN 1.0.3; RAKwireless product page) or an NB-IoT module, chosen per site survey;
  - barometer (BME280 class) for compensation;
  - RTC, FRAM/flash ring buffer for the signed append-only log;
  - primary Li-SOCl₂ cell (or Li-ion + 1–2 W solar where the lid sees sun);
  - reed switch for lid open, tilt switch;
  - antenna flush with the lid. RF loss underground is the known failure mode (EEVblog thread in landscape §5).
- **Optional:** tipping-bucket rain gauge on the roof or boundary wall.
- **Firmware (C2):**
  - **Dry:** sample every 15 min, uplink every 6–12 h.
  - **Wet:** when the stage rises > 2 cm or the rain gauge tips, sample every 60 s until the stage returns to baseline, then send an event summary plus the compressed series.
  - **Always:** heartbeats and tamper events.
- **Cloud (C4–C8):** Python services behind the typed contracts (`architecture/contracts/`). They run on any VM (Azure available) or a laptop for the demo. The dashboard is static HTML and works offline.

## 2. Bill of materials (per node, prototype quantities)
| Part | Spec | Source / price status |
|---|---|---|
| Pressure sensor | MS5837-30BA (I²C, 0–30 bar abs, 0.2 mbar resolution class) or 4–20 mA SS hydrostatic probe 0–5 m | MS5837 vendor pages blocked/timed out tonight (robu.in 403, element14 timeout) → **UNVERIFIED**. A search summary suggested ₹2,600–7,500 for MS5837 breakouts and ₹6,000–10,000 for 4–20 mA probes: **UNVERIFIED leads** |
| LoRa module | RAK3172 (STM32WLE5CC) | product page opened (RAKwireless store); price not captured → **UNVERIFIED** |
| Barometer | BME280 breakout | **UNVERIFIED** |
| Battery | Li-SOCl₂ D-cell, ~19 Ah class | **UNVERIFIED** |
| Enclosure + glands | IP67/68 polycarbonate, PG7/PG9 glands, desiccant | **UNVERIFIED** |
| Stilling tube + stand | 50 mm PVC, slotted, geotextile sock, SS weight | local hardware; **UNVERIFIED** |
| Rain gauge (optional) | tipping bucket, 0.2–0.5 mm/tip | **UNVERIFIED** |
| Gateway (shared) | 8-channel LoRaWAN indoor/outdoor gateway (IN865) | **UNVERIFIED** |
| **Target total** | **< ₹6,000 per node** excluding gateway | **ESTIMATE**: confirm by 9 Oct |
| *Comparator* | CGWA-compliant piezometer/DWLR (Acorn PZM-24B, 2 readings/day, ±0.5 % FS, optional GPRS) | **≈ ₹38,000 / piece** — https://www.acorncontrols.com/piezometer.html (opened 2026-10-04) |
| *Comparator* | Pride CGWA telemetry flow meter / piezometer telemetry | **≈ ₹38,900 / piece** — https://www.pridecontrols.co.in/telemetry-flow-meter.html (opened 2026-10-04) |

## 3. Power budget (method; inputs to be bench-measured)
E/day = I_sleep·24 h + N_samples·Q_sample + N_uplinks·Q_uplink + N_storm_min·Q_burst.

- A community LoRa node with an ESP32-C3 measured a 220 µA sleep floor, about 11 mAh/day (MichielBruijn/lora-humidity-sensor). That is our **upper-bound reference, not our design**. An STM32WL-class design sleeps far lower (datasheet value **UNVERIFIED** tonight).
- Battery life = usable capacity / (E/day). We will publish the measured mAh/day from a Nordic PPK2 or µCurrent bench run in October.

## 4. Calibration and maintenance
1. **Factory:** two-point pressure check in a water column (0 and 1.000 m) and baro offset.
2. **Commissioning:** a metered fill (water meter on the hose, ~200 L) fixes pit area (stage–volume) and k_as_built. The data are stored in `RechargeStructure`.
3. **Annual:** dip-tape check; replace desiccant and clean the sock.
4. **Event-driven:** a clogging index below 0.5 raises a maintenance ticket.

## 5. Build steps (Oct–Nov; user exams 19–25 Nov avoided)
| When | Step | Evidence produced |
|---|---|---|
| 5–9 Oct | Confirm BOM prices; order parts; pitch rehearsal | priced BOM |
| 10 Oct | Delhi zonal pitch | — |
| 11–25 Oct | Bench node: sensor + MCU + radio + log; power measurement | mAh/day, stage RMSE vs a 1 m column |
| 11–31 Oct | **Physical rig:** 200 L drum "pit" with a calibrated orifice drain (adjustable to simulate clogging), metered inflow, overflow weir | ground truth for blind trials |
| 1–14 Nov | Blind trials: 20 synthetic storms × 3 clogging levels + 5 fakes; compare verifier vs metered truth | event-volume MdAPE, clogging precision/recall, fake detection |
| 1–16 Nov | Field pilot at 1–3 real pits (campus/RWA), with permission | real storm events (post-monsoon rains are rare: we'll use fill tests) |
| 17 Nov | Freeze; draft report | — |
| 26–30 Nov | Report + video + submission (team leader submits) | Round-2 package |

## 6. What can be simulated now (walking skeleton)
- **C0 twin-simulator:** pits with known geometry, runoff, clogging decay, faults and fakes, driven by **real ERA5 hourly rain for Delhi 2022–2025** (`.data/delhi_weather_hourly.csv`, regenerable via `components/data-ingest/fetch_delhi.py`).
- **C4 ingest-qc:** on real India-WRIS DWLR data (`eval/realdata_profile.py` already quantifies the pathologies).
- **C5 recharge-verifier baseline + frozen evaluator:** event-volume MdAPE on the simulated fleet; then the autoresearch ratchet on C5.

## 7. Risks
1. Price confirmation pending.
2. Post-monsoon Delhi has few storms before 1 Dec, so the rig and fill tests carry Round-2 evidence.
3. Access to private pits needs RWA consent.
4. ERA5 rain is smooth; the field version needs a gauge.
