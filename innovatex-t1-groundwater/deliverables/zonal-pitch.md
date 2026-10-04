# Zonal pitch — Delhi, 10 Oct 2026 (10 minutes) — DRAFT v1

> **Working name: JalSakshi** ("water witness"): measured, not self-declared, groundwater recharge for Delhi.
> Theme 1, IoT-Based Underground Water Management. Sub-problem: **aquifer-recharge verification** (an official option in the challenge question).
> Every number on the slides is in `research/landscape.md` with its source, or comes from our committed run (`eval/realdata_profile.py`). Keep the source on the slide footer. *Italics = speaker notes.*

## Slide plan (10:00 total)

**1. Title + team (0:00–0:30).** JalSakshi — "Delhi pays for recharge it cannot see."
- Team name / Team ID / Theme 1 / members + contacts: **TO FILL (user)**.
- *"We're <team>. In ten minutes we'll show you why Delhi's groundwater rules work on paper but not in the ground, and a ₹-cheap IoT instrument that changes that."*

**2. The local problem (0:30–1:45).** Three facts, three sources.
- Delhi extracts **92.1 %** of its annually extractable groundwater, and 10 of 34 tehsils (337.44 km²) are over-exploited (CGWB *Dynamic Ground Water Resources of India 2025*, §7.32, primary). The 2023 assessment, via The Hindu, had 617.25 km² over-exploited. Say "still", not "getting worse": the over-exploited area shrank between assessments.
- DJB identified 20,297 illegal borewells. 15,962 were sealed and more than 4,000 couldn't be traced (HT, 10 Jun 2025). In 2026 the NGT found seals that let borewells run "very conveniently".
- Dwarka residents stopped pumping; "the adjoining areas – they're still using the groundwater" (CNA). The ground is sinking.
- *Pause on the subsidence photo. The point: extraction policing is adversarial and slow. Recharge is the lever the city controls.*

**3. The lever Delhi already pulls, blind (1:45–3:00).**
- RWH is mandatory for plots ≥100 m². A functional system earns a 10 % bill rebate (15 % with recycling); non-compliance means 1.5× the bill (HT, 21 Apr 2026).
- **₹204.46 crore** of rebates paid 2017–2024. From 2026, owners **self-certify** that their system works.
- Water minister: *"Till now, there was a rule but no real checking."* DJB is restoring 1,000 non-functional systems (Indian Express).
- *Why existing solutions fall short:*
  - inspections are manual and rare;
  - CGWA-style DWLR loggers cost ≈ ₹38,000 (Acorn listing) and log twice a day, so they can't see a 2-hour storm;
  - hobby kits show a tank level with an ultrasonic sensor and stop there. Nobody turns a storm into evidence.

**4. Our data says the monitoring layer is fragile too (3:00–3:45).** From our own analysis of India-WRIS (public API, 483,253 Delhi readings):
- 185 telemetric piezometers report every 6 h;
- only 46 have a reading in 2026;
- 23 % of readings are exactly 0.000 m, and 17 % of 6-hour slots are missing.
- Where data are clean, the monsoon raises water levels by a median **2.5 m**: recharge works when water gets in.
- *Show the dashboard map: real stations, quality colour-coded. "Real data, our code, reproducible."*

**5. The solution (3:45–5:30).** One instrument per recharge pit, plus a city twin.
- **Node:**
  - sealed pressure sensor in a slotted stilling tube at the pit bottom;
  - barometer + MCU + LoRaWAN/NB-IoT radio in the lid housing;
  - optional tipping-bucket rain gauge;
  - samples every 15 min when dry and every minute when rain or rising water wakes it;
  - keeps a signed local log and forwards when the link is up.
- **Cloud, per storm:**
  1. event detection;
  2. **water balance**: inflow − overflow − Δstorage = infiltration, with an uncertainty band;
  3. **recession constant** → **clogging index** vs commissioning;
  4. **verdict**: verified / clogged / no inflow / implausible (e.g. a "bucket fake": rise with no rain).
- **City twin:** QC'd DWLR network + rain-response model shows whether ward-level aquifers respond. This is the outcome check.
- *Draw the water-balance equation on the slide; it answers "is this real recharge?" before they ask.*

**6. Demo (5:30–7:00).** Walking skeleton, laptop, offline.
1. Delhi map with the real DWLR stations and QC flags.
2. A simulated pit (labelled SIMULATED), driven by **real Delhi monsoon-2025 rain**, goes through a season: storm events, then the clogging index decaying, then a "maintenance due" ticket.
3. Inject a fake (water poured with no rain) → "implausible".
- *If the demo fails, use the screenshots in the backup slides. Never demo on venue Wi-Fi.*

**7. Feasibility under Delhi conditions (7:00–8:00).**
- **Power:** event-triggered sampling, a primary lithium cell, and a battery-life estimate (target ≥3 years, UNVERIFIED until bench-measured).
- **Connectivity:** antenna in the lid, never underground; store-and-forward.
- **Calibration:**
  - commissioning fill test with a metered hose fixes pit area and k;
  - the barometer compensates the sealed sensor, which avoids the vent-tube moisture failures pro vendors warn about (Solinst);
  - annual dip-tape check.
- **Silt and heat:**
  - slotted stilling tube with a geotextile sock;
  - sensor body below the silt line on a stand;
  - enclosure rated for 50 °C+.
- **Maintenance:** clogging alerts are themselves the maintenance schedule.

**7b. Results (simulation, honest) — see deck slide 7 and `components/recharge_verifier/README.md`.**
- On the monsoon-2024 holdout, v1 has a median per-storm volume error of 3.0 %, catches 100 % of fakes, and wrongly flags 0 % of honest storms.
- On the harsher stress test, the error is 13.0 %. The fixes we tried improve the stress test but worsen the ideal case, so they are not adopted yet. Saying so builds trust.

**8. Cost and model (8:00–9:00).**
- **Cost:** BOM target **< ₹6,000 per node** at prototype quantities (deliverables/prototype-plan.md; part prices to be confirmed) vs ≈ ₹38,000 for a CGWA-style DWLR (Acorn listing).
- **Who pays:** pilot with RWAs and institutional campuses that want the rebate or need to show compliance. Then DJB's restoration programme (1,000 systems) as a verification layer.
- **Model:** device + ₹/year verification service, and the rebate-linked verdict feeds DJB billing.
- **Scale:** every Indian city with an RWH bylaw. The DWLR twin works for any state on India-WRIS.

**9. Impact (9:00–9:40).**
- Every verified structure turns a paper rebate into measured m³.
- Clogging alerts recover lost recharge.
- Fake or non-functional systems stop being paid.
- Quantification plan: per-structure m³ per monsoon × number of structures. The pitch gives the formula and the pilot target, not an invented city total.

**10. Ask + roadmap (9:40–10:00).**
- **Oct:** rig build.
- **Nov:** 3-site pilot (campus / RWA), blind trials vs a metered inflow.
- **1 Dec:** report + working prototype.
- **Ask:** a DJB / RWA pilot partner.
- *"Measured, not self-declared."*

## Likely judge questions — answers (keep each ≤30 s)
1. **"A water level isn't recharge. How do you get volume?"**
   - From a water balance.
   - Inflow comes from the stage rise during the storm, cross-checked against rain × roof area × runoff coefficient.
   - Overflow is bounded by the spill level; Δstorage comes from pit area (fixed at commissioning).
   - We report infiltration with an uncertainty band. We call it *infiltrated volume*, not aquifer recharge.
2. **"Why not an ultrasonic sensor and ThingSpeak like everyone else?"**
   - An ultrasonic sensor in a humid, silty pit fogs and reflects off debris.
   - A sealed pressure sensor with baro compensation is what professional loggers use.
   - Our value isn't the reading, it's the per-storm verdict and the uncertainty.
3. **"Can the owner cheat?"**
   - Pouring water without rain is flagged "implausible": rise without rain, or volume ≫ rain × catchment.
   - Removing the sensor shows up as a stage equal to the barometer, i.e. out of water.
   - Logs are signed.
   - It's not unbreakable; it's far harder to fake than a self-certification form.
4. **"Who pays, given the owner might lose a rebate?"**
   - Owners who already comply gain the 10 % rebate without inspections.
   - Institutions and RWAs need proof.
   - DJB saves inspection visits and stops paying for non-functional systems.
   - We pilot where incentives align first.
5. **"Underground connectivity?"**
   - The radio and antenna sit at the lid, not underground (antennas lose badly below grade).
   - LoRaWAN or NB-IoT, chosen by site survey.
   - Local buffering means no lost events.
6. **"Power and heat?"**
   - Sleep almost always; burst only during storms. A primary lithium cell.
   - The estimate is in the prototype plan, labelled; we'll bench-measure in October.
   - Enclosure and battery are rated for Delhi's 45 °C+ summers.
7. **"Can you detect illegal borewells?"**
   - Not from 6-hourly piezometers. Sampling aliases pump cycles and the signal is confounded.
   - We show a zone-level influence index as context only and never accuse a well.
   - Our focus is the lever the city controls: recharge.
8. **"Is any of this real?"**
   - The DWLR data are real (India-WRIS, 185 Delhi telemetric stations), and so is the rain (ERA5).
   - The pits are simulated tonight and labelled.
   - Round 2 adds a physical rig with a metered inflow and blind trials.
9. **"Why Delhi specifically?"** The ₹204 cr rebate history, the April 2026 self-certification switch, the 1,000-system restoration drive, and our own DWLR data-quality analysis.
10. **"What if rain data are coarse?"** An on-site tipping bucket, or the nearest AWS. ERA5 is used only for simulation and is labelled as reanalysis.

## Must not claim
1. That pressure + rain directly measures aquifer recharge. We measure infiltrated volume at the structure.
2. That piezometers identify illegal borewells or individual pumps.
3. That the node is tamper-proof or ready for city-wide rollout today.
