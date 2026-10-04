# Q&A prep — Delhi zonal, 10 Oct 2026 (JalSakshi)

> Answer in ≤ 30 s. **Bold** = the sentence to say first. Sources: `research/landscape.md`, `reviews/2026-10-04-lead-response.md`, `components/recharge_verifier/autoresearch/results.tsv`.
> **Accuracy numbers.** Simulated pits, real ERA5 Delhi rain, kept verifier v1. Median absolute % error of infiltrated volume per storm, monsoon-2024 holdout (dev in brackets):
>
> | Test | Median error | p90 |
> |---|---|---|
> | Same-model | **3.0 %** | 16 % |
> | Stress (non-linear drains + imperfect gauge) | **13.1 %** (dev 13.0 %) | 58 % |
> | Realistic probe (±25 mm offset, drift, quantisation) | **14.5 %** (dev 16.0 %) | 61 % |
>
> - Fakes flagged: **10/10 simulated** in every test. Honest storms wrongly flagged: ≤ 1.3 %.
> - End-of-season clogging verdict: precision 0.60–0.67, recall 0.90–1.0 (stress tests, holdout).
> - Ledger: `components/recharge_verifier/autoresearch/results.tsv`.

## A. Measurement honesty (from both judges)
1. **"How does one level sensor measure recharge?"**
   - **It doesn't, and we don't claim aquifer recharge.**
   - We measure two things at the structure. (1) The **drain rate** after each storm (a falling-head test the rain runs for us), which gives a clogging index. (2) **Infiltrated volume with a band**: the rise is checked against rain × roof area, overflow is capped at the spill level, and pit area and as-built drain rate come from one metered hose fill at commissioning.
   - An unseen bypass widens the band.
2. **"Your 3 % grades your own simulator."**
   - **Yes. That's why we lead with 13 %.** 3.0 % is same-model.
   - With non-linear drains and an imperfect gauge it's 13.1 % on holdout, and 14.5 % with a realistic probe offset. And 1 storm in 10 is off by more than ~60 %, so per-storm numbers carry a wide band.
   - We rejected five candidate fixes that helped one test but hurt another, under a rule we fixed before running them.
   - Real evidence will be blind weighed-water trials on a drum rig by 1 Dec.
3. **"What's actually real here?"**
   - **Real:** the Delhi groundwater data (India-WRIS, 185 telemetric stations, 483k readings), the rain (ERA5) and the software.
   - **Simulated:** every pit. Ten caught fakes means ten *simulated* fakes.
4. **"Can an owner cheat?"**
   - **Yes, a bypass during real rain can fool it.**
   - A pour with no rain gets flagged (10/10 simulated). Pulling the sensor shows a floor reading during rain. Signed logs prove the *records* weren't edited, not where the water went.
   - Suspicious events trigger a random inspection; they're not proof.
5. **"How do you prove impact without monsoon rain before 1 Dec?"**
   - **Metered fills before and after cleaning a clogged pit.** The drain-rate change is the measured benefit, reported with uncertainty.
   - We will not quote invented city-wide recharge.

## B. Policy, buyer, money
6. **"Is self-certification already the rule?"**
   - **No. It's being planned (HT, 21 Apr 2026).** Today DJB issues functionality certificates *after inspection*, and the minister said "there was a rule but no real checking".
   - **The verification system doesn't exist yet; we're bidding to be it.**
7. **"Who pays if the owner can lose a rebate?"**
   - **Not households first.** DJB is restoring 1,000 non-functional systems in government buildings (Indian Express). Those buildings, worked on by DJB's 59 empanelled service providers, are the first buyer.
   - Campuses and RWAs that *want* proof come next.
   - The verdict ranks inspections. **An inspector can override it, and no bill changes automatically.**
8. **"Is ₹204 crore your market?"**
   - **No.** It's what DJB data (via HT) say was paid in RWH rebates 2017–24 with little checking. It shows the stakes, not our revenue.
9. **"What does a node cost?"**
   - **₹11,166 in verified single-unit retail parts** (probe ₹4,254.51 at element14, LoRa module, host board, battery, IP67 box, gland). Tube, cable and potting are extra and not yet priced.
   - Compare: one CGWA-compliant DWLR (Acorn) lists ≈ ₹38,000 and logs twice a day.
   - Volume pricing isn't quoted yet, so we don't claim it.
10. **"What's the impact number?"**
    - **DJB estimates ≈ 733 million litres a year of recharge potential from its Phase-I campaign (Indian Express). That's the claim we'd audit, structure by structure.**
    - Our number will be measured litres per verified structure.
11. **"Why would DJB adopt this rather than random inspections?"**
    - **We make inspections smarter, not unnecessary.** Ranking 1,000 sites by drain-rate decline sends crews to the clogged ones first.
    - DJB is already building a portal to "track installations, monitor compliance" (Indian Express), and our events can feed it.

## C. Technical feasibility (power, connectivity, calibration, weather)
12. **"Underground connectivity?"**
    - **The radio isn't underground.** Only the probe goes into the pit. The antenna sits flush with the lid, because below-grade antennas lose badly.
    - LoRaWAN (IN865) or NB-IoT, chosen by site survey. A local buffer means no event is lost during outages.
13. **"Battery life?"**
    - **We won't claim one until we've measured it.** The probe needs 12–36 V and DFRobot advises warm-up, so settle time decides everything: ~2 s of on-time is fine on a D-cell; ~30 s means solar.
    - We'll measure with a power profiler in October. Pit lids are outdoors, so solar is a fallback.
14. **"Sensor accuracy?"**
    - **±0.5 % FS on a 0–5 m probe = ±25 mm per reading** (datasheet).
    - On a 2.25 m² pit, the worst-case error on a storm's stage rise is ±0.11 m³, about 3 % of a 4 m³ storm.
    - A constant offset is removed by zeroing on the dry floor between storms.
15. **"Silt will bury your sensor."**
    - **The probe hangs in a slotted stilling tube with a geotextile sock, on a stand above the silt line.**
    - A floor-level reading during rain triggers a maintenance check.
16. **"Delhi heat and monsoon flooding?"**
    - **The probe is rated −20 to 70 °C, 316L stainless steel, IP68 (datasheet); the enclosure is IP67.**
    - Battery performance at 45 °C+ is a bench item: we have no datasheet number yet, so no claim.
17. **"Calibration?"**
    - **One metered hose fill at commissioning fixes pit area and as-built drain rate.**
    - Then: auto-zero on the dry floor, an annual dip-tape check, and a re-fill test after any cleaning.
18. **"What if the rain gauge fails?"**
    - **The verdict is deferred, never guessed.** The nearest AWS can stand in, labelled as such.

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
    - Of 185 telemetric stations, only 46 reported in 2026, and 23 % of readings are exactly 0.000 m.
    - Our QC layer cleans this, so the aquifer-level outcome can actually be checked.
23. **"Does it scale beyond Delhi?"**
    - **Anywhere a city mandates RWH and pays for its upkeep.**
    - The pit physics is the same everywhere. The city-twin layer runs on any state's India-WRIS stations.
    - Each structure needs one commissioning fill.
24. **"Does recharging polluted runoff harm the aquifer?"**
    - **That's a real risk, and we don't monitor quality today.**
    - The node has a free channel for EC, the cheapest proxy, as a later extension. Inflow should pass through a first-flush diverter.
25. **"Who's on your team, and who builds the hardware?"**
    - **<Fill in: team, roles.>** We need a hardware teammate for the rig and node (see the prototype plan, §9).
