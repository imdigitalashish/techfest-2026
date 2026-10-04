# Q&A prep — Delhi zonal, 10 Oct 2026 (JalSakshi)

> Answer in ≤ 30 s. **Bold** = the sentence to say first. Sources: `research/landscape.md`, `reviews/2026-10-04-lead-response.md`, `components/recharge_verifier/autoresearch/results.tsv`.
> **Accuracy numbers.** Simulated pits; Open-Meteo archive rain (default model, not pinned; minute pattern synthetic); kept verifier v1; monsoon-2024 holdout (dev in brackets). Errors are scored over **detected event windows** with ≥ 0.2 m³ true infiltration; a window can hold several storms.
>
> | Test | Median error | p90 | Scored windows |
> |---|---|---|---|
> | Same-model | 3.0 % | 16 % | 1,369 |
> | Stress | **13.1 %** (dev 13.0 %) | 58 % | 1,233 |
> | Realistic probe | **14.5 %** (dev 16.0 %) | 61 % | 952 |
>
> - Large injected pulses (500–2,000 L) flagged: 10/10 in every test.
> - Honest windows wrongly flagged: 2/1,291 (stress), 15/1,156 (probe).
> - Clogged-pit precision/recall: holdout 0.67/1.0 (10 clogged pits); dev 0.40/0.67 (only 3).
> - Results assume 1-min stage sampling throughout.
> - Ledger: `components/recharge_verifier/autoresearch/results.tsv`; checksums: `eval/results/manifest.json`.

## A. Measurement honesty (from both judges)
1. **"How does one level sensor measure recharge?"**
   - **It doesn't, and we don't claim aquifer recharge.**
   - We measure two things at the structure. (1) The **drain rate** after each storm (a falling-head test the rain runs for us), which gives a clogging index. This is the core product: maintenance screening. (2) **Infiltrated volume as a model-based estimate**: storage plus a drain law fitted from one metered hose fill, with the rise checked against rain × roof area.
   - What we can't see: a leak out of the pit looks like infiltration; overflow volume is only estimated; water below the probe tip is a blind zone (Backup 4).
   - A per-event uncertainty band is planned, not built. Today's error statistics are fleet-level.
2. **"Your 3 % grades your own simulator."**
   - **Yes. That's why we lead with 13 %.** 3.0 % is same-model.
   - With non-linear drains and an imperfect gauge it's 13.1 % on holdout, and 14.5 % with a realistic probe offset. And 1 storm in 10 is off by more than ~60 %, so per-storm numbers carry a wide band.
   - We rejected five candidate fixes under a written keep rule: four helped one test but hurt another, and one didn't help enough.
   - Git shows the rules for the first two rounds were committed before their results (08:03 → 08:15, 08:26 → 09:46). The third rule was committed together with its results, so we don't call it pre-registered.
   - Real evidence will be blind weighed-water trials on a drum rig by 1 Dec.
3. **"What's actually real here?"**
   - **Real:** the Delhi groundwater data (India-WRIS, 185 telemetric stations, 483k readings) and the software. The rain is a public archive (Open-Meteo, reanalysis-based, default model; not a gauge on site), and the minute pattern is synthetic.
   - **Simulated:** every pit. Ten caught fakes means ten *simulated* fakes.
4. **"Can an owner cheat?"**
   - **Yes, a bypass during real rain can fool it.**
   - A **large** sudden pulse the rain can't explain gets flagged: 10/10 simulated pulses of 500–2,000 L.
   - A 20 L bucket raises a 2.25 m² pit by ~9 mm, below our 2 cm event threshold, so it isn't even an event. Slow pours are untested.
   - Signed logs (planned) would prove the *records* weren't edited, not where the water went.
   - Suspicious events trigger a random inspection; they're not proof.
5. **"How do you prove impact without monsoon rain before 1 Dec?"**
   - **Metered fills before and after cleaning a clogged pit.** The drain-rate change is the measured benefit, reported with uncertainty.
   - We will not quote invented city-wide recharge.

## B. Policy, buyer, money
6. **"Is self-certification already the rule?"**
   - **No. It's being planned (HT, 21 Apr 2026).** Today DJB issues functionality certificates *after inspection*, and the minister said "there was a rule but no real checking".
   - **Nothing measures a pit storm by storm today. We propose that layer, alongside inspection, not instead of it.**
7. **"Who pays if the owner can lose a rebate?"**
   - **Not households first.** Our *prospective* pilot customer is DJB's Phase-I restoration of 1,000 non-functional government systems (IE; target was 30 Jun 2026) and its 59 empanelled providers. DJB is the RWH nodal agency (HT).
   - **We have no contact or commitment yet.** That's our ask.
   - Campuses and RWAs that *want* proof come next.
   - The verdict ranks inspections. **An inspector can override it, and no bill changes automatically.**
8. **"Is ₹204 crore your market?"**
   - **No.** It's what DJB data (via HT) say was paid in RWH rebates 2017–24 with little checking. It shows the stakes, not our revenue.
9. **"What does a node cost?"**
   - **Parts only (listings seen 4 Oct): base node ₹11,166; first site with gauge + shared gateway ₹48,454; 3-pit pilot ₹78,245.** Excludes tax, shipping, mounting, tube/cable/potting.
   - Installation (≈ 1 technician-day per pit) and an annual pre-monsoon fill visit (≈ ½ day per pit) are ASSUMPTIONS; their cost comes from an empanelled provider's quote, so we won't guess rupees.
   - Backhaul: site Wi-Fi/Ethernet for the gateway (assumed). The probe-powered battery, if used, is ₹879 per cell.
   - Compare: one CGWA-compliant DWLR (Acorn) lists ≈ ₹38,000 and logs twice a day.
   - Volume pricing isn't quoted yet, so we don't claim it.
10. **"What's the impact number?"**
    - **The Phase-I campaign's recharge potential is estimated at ≈ 733 million litres a year (rooftop area × average rainfall, as reported by Indian Express). That's the estimate we'd audit, structure by structure.**
    - Our number will be measured litres per verified structure.
11. **"Why would DJB adopt this rather than random inspections?"**
    - **We make inspections smarter, not unnecessary.** Ranking 1,000 sites by drain-rate decline sends crews to the clogged ones first.
    - DJB is developing a portal to "track installations, monitor compliance" (Indian Express). Our events *could* feed it; we have no API or permission yet.

## C. Technical feasibility (power, connectivity, calibration, weather)
12. **"Underground connectivity?"**
    - **The radio isn't underground.** Only the probe goes into the pit. The antenna sits flush with the lid, because below-grade antennas lose badly.
    - LoRaWAN (IN865) or NB-IoT, chosen by site survey. A local buffer is *planned*; a 24 h outage with zero lost events is an October acceptance test, not yet a result.
    - The antenna must sit clear of any metal lid.
13. **"Battery life?"**
    - **We won't claim one until we've measured it.** The probe needs 12–36 V and DFRobot advises warm-up, so settle time decides everything: ~2 s of on-time is fine on a D-cell; ~30 s means solar.
    - We'll measure with a power profiler in October. Pit lids are outdoors, so solar is a fallback.
14. **"Sensor accuracy?"**
    - **±0.5 % FS on a 0–5 m probe = ±25 mm per reading** (datasheet).
    - On a 2.25 m² pit, the worst-case error on a storm's stage rise is ±0.11 m³, about 3 % of a 4 m³ storm.
    - The probe tip sits 5–10 cm above the floor, so 0.11–0.23 m³ in a 2.25 m² pit is never seen.
    - Auto-zero was tested in simulation and not adopted (rejected by the keep rule); it remains planned firmware.
15. **"Silt will bury your sensor."**
    - **The probe hangs in a slotted stilling tube with a geotextile sock, on a stand above the silt line.**
    - A floor-level reading during rain triggers a maintenance check.
16. **"Delhi heat and monsoon flooding?"**
    - **The probe is rated −20 to 70 °C, 316L stainless steel, IP68 (datasheet); the enclosure is IP67.**
    - Battery performance at 45 °C+ is a bench item: we have no datasheet number yet, so no claim.
17. **"Calibration?"**
    - **One metered hose fill at commissioning fixes pit area and as-built drain rate.**
    - Then: a pre-monsoon metered-fill check (clogging that develops in the dry season shows only at the next storm), an annual dip-tape check, and a re-fill test after any cleaning.
18. **"Unplug the rain gauge. Does it accuse my building?"**
    - **No. It defers.** If rain data cover < 90 % of the event window, or the stage record has a gap > 60 min, the verdict is "deferred": no accusation, no clogging call.
    - This is implemented and unit-tested (`components/recharge_verifier/test_verifier.py`), and the demo's "Unplug rain gauge" button shows it live.

## D. Novelty and scope
19. **"Why not an ordinary logger plus a dashboard?"**
    - **The hardware isn't the innovation.** The innovation is a per-storm verdict with uncertainty that a maintenance crew and DJB can act on.
    - Typical kits show a tank level. One CGWA DWLR logs twice a day, so it misses a two-hour storm.
20. **"This isn't underground water management. And can you catch illegal borewells?"**
    - **The brief explicitly lists aquifer-recharge analysis.**
    - On borewells: Delhi's public piezometer data are 6-hourly, which aliases pump cycles. We won't accuse a well. (Backup slide: 20,297 illegal borewells identified, 4,000+ untraceable. Enforcement is a separate, adversarial problem.)
21. **"Delhi's groundwater is improving per CGWB. Why act?"**
    - **The 2025 assessment still puts extraction at 92.1 % of the extractable resource, with 10 of 34 tehsils over-exploited.**
    - Recharge infrastructure is the lever the city funds, so it should work.
22. **"What does your India-WRIS analysis add?"**
    - **It shows the city's own telemetry needs QC.**
    - Of 185 telemetric stations, only 46 reported in 2026 (latest public reading 4 Jun 2026), and 23 % of readings are exactly 0.000 m. It's a public-stream snapshot.
    - The 2.5 m monsoon rise is exploratory and not attributed to RWH.
    - Our QC layer cleans this, so the aquifer-level outcome can actually be checked.
23. **"Does it scale beyond Delhi?"**
    - **Same software everywhere; each site still needs adaptation.** That means a metered-fill calibration and safety check per structure, a local radio choice and local rebate/buyer rules.
    - Different geology and structure designs change the drain law, which is why we fit it per site.
    - The first pilot covers one structure type: a roof-runoff pit with filter media.
24. **"Does recharging polluted runoff harm the aquifer?"**
    - **That's a real risk, and we don't monitor quality today.**
    - **Gate:** pilot only on permitted roof-runoff structures with existing pretreatment and a responsible site operator. We never recommend recharging runoff we can't vouch for.
    - An EC channel is a later screening extension. Conductivity alone does not certify safety.
25. **"Who's on your team, and who builds the hardware?"**
    - **<Fill in: team, roles.>** We need a hardware teammate for the rig and node (see the prototype plan, §9).

## E. Added after the final-deck review (4 Oct)
26. **"How does a sleeping sensor see a short storm?"**
    - **In the pilot the rain gauge is mandatory**: its first tip wakes the node into 1-min sampling.
    - Our accuracy numbers assume 1-min sampling throughout. The duty-cycled schedule (15-min polls when dry) is **untested**; it's an October bench test.
27. **"When does the maintenance officer actually get the alert?"**
    - **When the event closes**: after the pit has drained, hours to days after the storm started. A maintenance ticket also needs a sustained trend over 3 storms (rule v0, not yet validated across the fleet).
    - It's for scheduling cleaning, not real-time response.
28. **"Who signs the purchase order?"**
    - **Prospectively DJB, the RWH nodal agency, through its restoration programme. Today we have no contact.**
    - A pilot letter from DJB, a campus or an RWA is our main ask.
