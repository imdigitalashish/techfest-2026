# Zonal pitch — InnovateX Theme 3 (Delhi zonal, 10 Oct 2026, 10 minutes)

> Draft v1.3 (4 Oct 2026, 07:35 IST) by the project lead. Every number carries a source key; the source list is at the end and in [`../research/`](../research/).
> - **[V]** = lead not yet verified at a primary source. Verify it or cut it before the pitch.
> - **SIMULATED** = output of our digital twin, not field data.
> - **⟨FILL⟩** = to be filled from a committed run or the sourced BOM. Never invent it.
>
> Working name: **NullahNet**. Run of show: 11 slides, about 55 s each, then Q&A.

## One-line pitch
Two Interceptors will soon guard two of Mumbai's creeks. NullahNet makes the long tail of small nullah outfalls accountable:
- crews clear the booms before the storm and in the gate-closed window;
- a fail-open pocket keeps trash in when the tide turns, without raising flood levels;
- contractors are paid only for verified kilograms.

---

## Slide 1 — Title and team (0:00–0:40)
- NullahNet: tide-aware, verified interception of plastic at Mumbai's nullah outfalls. Team name, Team ID, Theme 3, members and contacts: **⟨FILL — user⟩**.
- **Speaker notes:** "We picked one leak — floating single-use packaging escaping through Mumbai's small stormwater outfalls. We built a working software twin of real outfalls on real 2019–2025 tide and rain data before coming here."

## Slide 2 — The problem in numbers (0:40–1:40)
- **≈5 million kg/yr.** The Mumbai metropolitan region releases an estimated 5 million kg of plastic a year into the Arabian Sea and Indian Ocean. Impacts reach 220 km of coastline, 152 km² of mangroves, 107 protected species and ~1.9 million livelihoods (The Ocean Cleanup, Smart Rivers Survey, 10 Feb 2026) [S1].
- **≈50 outlets.** That flow enters the sea through "around 50 drains and nullahs" (Lokmat Times, reporting the same study) [S4].
- **186 outfalls.** Mumbai's storm-water network has ~2,000 km of open drains and 186 outfalls. Most drains were designed for ~25 mm/h of rain at low tide (BRIMSTOWAD, via a secondary summary; the primary PDF was unreachable) [M:S7].
- **The pulse is visible.** After more than 1,000 mm of rain in early July 2026, BMC removed 2,498.66 t of marine waste from seven beaches in 11 days (9–19 Jul 2026); 1,825 t came from Juhu alone [M:S17][M:S18].
- **Uncollected waste.** An older BMC estimate says 500 t/day of uncollected waste "ends up in the storm water drains". Mumbai generated 6,330 t/day of municipal waste in 2022 [M:S10][M:S16].
- **Global ranking.** An independent global model (Meijer et al. 2021, *Science Advances*) ranks Malad Creek #30 and the Mithi #48 of 31,819 modelled outfalls worldwide. These are modelled estimates, not measurements [S5][S6].
- **Speaker notes:** "Two different methods disagree on the exact tonnage. The model puts Malad Creek alone at ~2,700 t/yr. Both agree Mumbai is one of the world's largest urban sources. The same study names Malad and Trombay — the two outlets in your problem statement." Show one map: outfalls, Malad and Trombay creeks, the Mithi.

## Slide 3 — Our specific source (1:40–2:30)
- **What leaks:** floating single-use *flexible* packaging — carry bags, films, multilayer sachets — from market and dense-settlement catchments. It enters nullahs and leaks at *small* outfalls.
- **Why this one:**
  - Plastic made up 75.5% of 52,770 litter items counted at Juhu and Aksa beaches, and plastic bags were the largest beach-trash component in a 2015–16 survey [M:TL;DR 8].
  - It is the residue collection misses: low resale value means informal pickers skip it **[V]**.
  - The ban hasn't stopped it. In 2024 BMC fined 44,448 establishments a total of ₹41.7 lakh but confiscated only 2,148 kg of plastic [M:S19][M:S21].
  - It is light, so the first monsoon storms flush it.
  - It escapes under booms when the flow is fast.
- **Speaker notes:** "Bottles get picked up because they have resale value; films and sachets don't. That makes film the residual that reaches the sea." Say this only once a composition source is cited; otherwise frame it as our hypothesis and the first thing our camera measures.

## Slide 4 — What exists and why it falls short (2:30–3:30)
| Approach | What it does | Gap for Mumbai's small outfalls |
|---|---|---|
| The Ocean Cleanup Interceptors at Malad and Trombay creeks (MCGM permits, MPCB MoU, 2026) [S1][S2] | Big solar barriers at two creek mouths; 61–92 t/yr expected from the first systems [S1] | ≈1.2–1.8% of 5,000 t/yr (our arithmetic). The other outfalls are untouched. |
| Plastic Fischer TrashBooms (on-ground partner) [S2][S7] | Low-tech booms; 3.2 million kg recovered with 71 booms across 8 sites (India + Indonesia); per-kg third-party verification [S7] | Manual chain of custody; no forecasting or tide logic; sees only what reaches the bank |
| BMC steel-net trash booms with conveyors at nullah mouths [S11] | 9 booms since ~2022, 14 more planned (→ 23). About ₹1 crore each. About 1.5 t/day per boom in the dry season and 2.5–3 t/day in the monsoon (mixed garbage). O&M is ₹14.5 crore for 2 years across six western-suburb sites [S12] | Un-instrumented: no fill sensing, no forecast or tide logic, and pay is per contract, not per verified kg. Quantities are hard to verify. In the Mithi desilting case, the EOW SIT's FIR cites a ₹65.54 crore wrongful loss. The SIT is examining ₹1,100 crore spent on the Mithi by BMC and MMRDA since 2005 (allegations under investigation) [P:P5]. |
| Trash wheel (Baltimore), Bubble Barrier (Amsterdam), WasteShark | ~500 tons/yr at one site (operator claim) [S8]; ~1 t/yr at one canal [S9]; 160-litre basket [S10] | Costly fixed civil works, mains power, or tiny capacity. None built for twice-daily tidal reversal. |
- **Speaker notes:** "We are not competing with The Ocean Cleanup. They take the two biggest mouths. We take the long tail, and our data layer could plug into their verification too."

## Slide 5 — The insight (3:30–4:30)
1. **Plastic flux peaks exactly when barriers fail.**
   - Heavy rain → fast flow → items dragged under the skirt and pockets overflow; flood rules force booms open.
   - Floating booms lose their catch above an escape velocity of about 0.35 m/s, whatever the skirt depth (oil-boom guidance) [S14]. Angling the boom keeps the normal velocity below that — something we test in the flume.
   - So barriers catch far less of the plastic that actually flows than their average performance suggests.
2. **Tide matters differently by outfall.**
   - Behind tide-locked flap gates the water is still at high tide. That is the best capture and clearance window.
   - At open outfalls the flood tide re-floats the catch **[V]**.
3. **Money follows claimed wet tonnes, not kilograms prevented.**
- Our north-star number: **flux-weighted capture efficiency** = verified kg retained ÷ kg arriving, over a monsoon.
- **Speaker notes:** "Every product on the previous slide reports kg *removed*. Nobody reports kg *prevented*. We measure the ratio."

## Slide 6 — NullahNet: four layers (4:30–5:45)
1. **Pocket-fill eye** at each boom: solar camera + range sensor + rain gauge. It reports how full the pocket is and how much plastic is arriving.
2. **Tide-and-forecast brain** (digital twin of each outfall):
   - Combines real rain forecasts, tide predictions and the fill readings.
   - Forecasts the risk of overflow, re-floating or release for the next 24–48 h.
3. **Crew dispatch:**
   - Each morning plan plus storm alerts.
   - Empty the pockets *before* the surge and in the gate-closed window.
   - Prioritise by predicted overflow.
4. **Ratchet pocket + fail-open fuse** (retrofit for existing booms):
   - A one-way pocket keeps the catch when the flow reverses.
   - A hinged section opens at a set water head, so the boom can never raise upstream flood levels.
   - Every clearance is a **signed, hash-chained evidence record**. It is checked against the camera's before/after fill and the weighbridge, and pays the contractor per verified kg. The catch is routed to recycling or cement-kiln co-processing with EPR paperwork **[V]**.
- **Speaker notes:** Point at the dashboard screenshot: map, fill gauges marked SIMULATED, today's plan, ledger with ✓ verified badges.

## Slide 7 — Built for Mumbai conditions (5:45–6:45)
- **Tides:** each site is modelled as gated or open; the dispatch and ratchet logic depend on it.
- **Monsoon:** the fail-open fuse has a measured head-rise envelope. We will never claim "cannot flood". The twin uses 2019–2025 real monsoons, including extreme bursts.
- **Corrosion:** HDPE floats, SS316 hardware, IP67 enclosure mounted above the highest recorded water level.
- **Power:** sized for July, the darkest month and also the month of peak plastic flux. Mumbai gets 3.79 kWh/m²/day of insolation in July vs 7.09 in May (NASA POWER climatology) [S13]. A duty-cycled node needs about a 40 W panel and a 300 Wh LiFePO4 battery for 3 days' autonomy (estimate) [S13].
- **Connectivity:** 4G/NB-IoT with ≥7 days of store-and-forward.
- **Maintenance:** lens wiper and health flags (dirty lens, low battery, tamper) appear on the dashboard.
- **Speaker notes:** "Judges asked for robustness under tides, corrosion and monsoon overflow. Each of those is a design input, not an afterthought."

## Slide 8 — Evidence so far (6:45–7:45)
All four results come from runs committed to our repo, each with a reproduce command (see [`../eval/RESULTS.md`](../eval/RESULTS.md)).
- **Digital twin (SIMULATED plastic, real forcing):**
  - Inputs: 4 Mumbai outfalls; ERA5 rain; archived JMA day-ahead forecasts (so no hindsight); tide fitted with UTide to Open-Meteo Marine sea level (RMSE ≈ 0.08 m).
  - Held-out monsoons 2024–25; 2 crews × 8 h/day for every policy; 40 Monte Carlo draws.
  - Forecast- and tide-aware dispatch cut escaped plastic by a median **2.1%** vs the fixed schedule (90% interval: from 1.5% more to 12.5% less; better in 28 of 40 draws). Most of the gain comes from *tide-aware* timing, not from rain forecasts.
  - Clearing whenever the pocket looks full did *worse* (+3.1% escaped).
  - **Lesson:** timing alone is a small lever. About half the arriving plastic is not captured whatever the schedule. So the headline lever is capture physics at high flow, which is why we build the angled-boom ratchet pocket.
  - Reproduce: `python -m twin_sim.run`.
- **Detector:** YOLO11n on a public floating-litter dataset; held-out mAP50 = ⟨FILL⟩.
- **Evidence records (SYNTHETIC test data):**
  - Tampering detected 100% of the time.
  - 72% of inflated claims caught at a 4.7% false-flag rate. A simple claimed-vs-sensor ratio check catches 67%; today's slip check catches 0%.
  - Precision is only 0.45 at 5% fraud prevalence. So flags trigger a *review*, never an automatic penalty.
  - Reproduce: `python3 -m mrv_ledger.evaluate`.
- **Flume:** ⟨FILL if run before 10 Oct⟩. A reversed-flow test shows the pocket's retention vs a straight boom.
- **Speaker notes:** Say "simulated" out loud. Credibility matters more than the size of the number.

## Slide 9 — Cost and business model (7:45–8:45)
- **Per outfall:**
  - Field sensor node: ₹82,282 for electronics priced on Indian retailer pages (the battery is about half of that). The duty-cycled variant is cheaper; the enclosure is not yet priced [S13].
  - Ratchet/fuse retrofit: ⟨FILL after the flume build⟩.
  - **For comparison:** a BMC boom costs ≈ ₹1 crore [S11], and boom O&M runs ≈ ₹1.2 crore per site-year (derived from ₹14.5 crore / 6 sites / 2 years; assumes one boom per site) [S12]. Instrumenting a boom costs **under 1% of the boom's price**.
- **Who pays:**
  - BMC already pays for booms and clearance. Its 2026-27 budget is ₹80,952.56 crore, with roads and storm-water drains taking "more than half". Boom O&M runs ₹14.5 crore for two years at six sites [P:P4][S12]. We make that spend verifiable and better timed.
  - Producers (PIBOs) under EPR. Category II explicitly covers "carry bags, plastic sachet or pouches". Non-recyclable plastic may go to end-of-life routes such as cement-kiln co-processing [P:P1]. **Open question:** whether drain-recovered plastic earns EPR certificates is NOT FOUND in the rules. The workaround is a registered processor partner.
  - CSR and plastic-credit buyers pay for verified kg. Plastic Fischer already sells verified waste credits [S7].
- **Speaker notes:** "Our wedge is pay-per-verified-kg. It saves the city money on the claims that cannot be verified. It is not another cost line."

## Slide 10 — Impact and scale (8:45–9:30)
- **Per site:** we will quote kg diverted only once the flume and a field pilot measure capture. The twin's job is to rank levers, not to promise tonnes. In the twin, dispatch alone moves escape by a few percent (SIMULATED); the capture hardware is the larger lever, still to be quantified.
- **City:** same contracts, any number of outfalls; site configuration is data (gated or open, width, catchment).
- **India:** any coastal city with tidal drains (e.g. Chennai, Kochi, Surat, Kolkata) — same software, local tide and rain feeds.
- **Co-benefits:** fewer choked outfalls before high-tide storms, mangrove protection, data for source reduction by ward.
- **Speaker notes:** "Interception is the last line of defence. The ward-level flux data is how we fund collection upstream."

## Slide 11 — Roadmap and ask (9:30–10:00)
- **Oct:** reversed-flow flume and fuse abuse tests; fill-alert blind test.
- **Nov:** edge-node prototype, finished before the 19–25 Nov exams.
- **1 Dec:** report plus working prototype.
- **Dec:** finals demo — live flume plus dashboard.
- **Integration hook:** BMC's ₹13,000 crore flood plan already adds 8–10 ft garbage mesh screens and water-level sensors at 7 pilot sites [M]. NullahNet is the measurement, dispatch and evidence layer for exactly those assets.
- **Pilot ask:** one BMC ward with 2–3 small outfalls (one gated, one open), with the option of interoperating with the Plastic Fischer / The Ocean Cleanup verification flow.

---

## Likely judge questions — with answers
1. **"The Ocean Cleanup is already doing this in Mumbai. Why you?"**
   - They target two big creek mouths, with 61–92 t/yr expected [S1].
   - Our layer is for the many small outfalls, and it is complementary: our per-kg evidence and dispatch could serve their operator too.
2. **"Won't a barrier in a nullah make flooding worse?"**
   - That is our first design constraint. The fuse opens at a set head, and we will show the measured head-rise envelope from flume tests.
   - Dispatch empties pockets *before* forecast storms, so the barrier is not full when the surge comes.
3. **"What happens at peak rain plus high tide? Does the fuse dump everything?"**
   - At peak flow some loss is physics. The pocket sits at the bank, outside the fuse path, so the stored catch stays.
   - We report flux-weighted capture efficiency precisely so these losses are counted, not hidden.
4. **"Your results are simulated. Why should we believe them?"**
   - They are relative comparisons under stated assumptions, with Monte Carlo over every assumed parameter.
   - Rain forecasts are archived ones, so the policy has no hindsight. Held-out years were never used for tuning.
   - Field calibration (tagged-item releases at real outfalls) is in the Round-2 plan.
5. **"Did you use real forecasts or actual rainfall?"** Both, for different jobs. Decisions use the archived JMA day-ahead forecast as it was issued, which we checked is archived back to 2019. Outcomes use ERA5 rain. The policy never sees the future.
6. **"Can a camera see plastic at night, in rain, in black nullah water?"**
   - Not reliably. That is why the primary reading is *pocket fill*: an area and range measurement that is robust to glare and supported by an IR camera and a range sensor.
   - Item counting is secondary. Detector metrics are on a public dataset ⟨FILL mAP⟩. Domain shift to Mumbai water is our first data-collection task.
7. **"How do you turn counts into kilograms?"**
   - Not from counts alone. We use pocket volume × bulk density, checked against the weighbridge.
   - We also do random sort samples for the dry-plastic fraction, to correct for water and organic weight.
8. **"Hash chains don't make data true."**
   - Correct. They make edits detectable. Truth comes from *independent* evidence: camera before/after fill, weighbridge, GPS.
   - Disagreements are flagged for review, not auto-rejected.
9. **"Who buys wet, dirty film?"**
   - Nobody buys it for its material value. Under the PWM Rules, non-recyclable plastic may go to end-of-life routes — road construction, waste-to-energy, waste-to-oil, cement-kiln co-processing — through processors registered on CPCB's EPR portal [P:P1].
   - Producers' EPR obligations are the paying party. We have not found a rule confirming that drain-recovered plastic earns certificates, so we treat that revenue as upside, not as the base case.
10. **"Isn't the real fix waste collection upstream?"**
    - Yes, and interception is the last line of defence.
    - Our outfall data ranks catchments by leakage, so the ward can target collection and enforcement. That is source reduction informed by data.
11. **"What about corrosion, theft and biofouling?"** HDPE and SS316 hardware, an IP67 node on a pole above the high-water mark, tamper and tilt sensing, a lens wiper, and monthly maintenance included in the crew plan.
12. **"How much does one site cost, and what is the payback?"**
    - The node is ≈ ₹82k in priced parts [S13], against ≈ ₹1 crore per boom [S11] and ≈ ₹1.2 crore of O&M per site-year (derived) [S12].
    - If dispatch and per-kg verification improve the value of O&M spend by even ~1%, one node pays for itself in under a year. That is our arithmetic and an ASSUMPTION about effect size; the twin's measured relative gain replaces it.
13. **"Why will BMC adopt this?"**
    - It slots into existing boom and clearance contracts. It changes *when* crews go and *how* they are paid.
    - It needs no new civil works. The dashboard is built for a ward engineer.
14. **"Is the ratchet pocket novel?"**
    - One-way flap litter traps exist (prior art noted in [interception-hardware.md](../research/components/interception-hardware.md) ⟨FILL⟩).
    - Our contribution is the tidal-outfall retrofit with a calibrated fail-open fuse, plus instrumentation. We claim nothing beyond what our flume shows.
15. **"Scalability across India?"** All site specifics are configuration (gated or open, geometry, catchment); tide and rain feeds are global. A new city needs site surveys, not new software.

## Sources (opened by the research sessions on 2026-10-04; details in the research files)
- [S1] The Ocean Cleanup, press release "The Ocean Cleanup Enters India…", Mumbai, 10 Feb 2026 — https://theoceancleanup.com/press/press-releases/the-ocean-cleanup-enters-india/
- [S2] The Ocean Cleanup, press release on the Mumbai Interceptors (MPCB MoU, MCGM permits, Plastic Fischer), 30 Apr 2026 — https://theoceancleanup.com/press/press-releases/the-ocean-cleanup-deploys-mumbai-interceptors/
- [S4] Lokmat Times, "Mumbai Among Top Global Polluters as Plastic Waste Chokes Coastline" (2026) — https://www.lokmattimes.com/mumbai/mumbai-among-top-global-polluters-as-plastic-waste-chokes-coastline-a525/
- [S5] Plastic Bank river page, Malad Creek (presents Meijer et al. 2021 model output) — https://rivers.plasticbank.com/rivers/malad-creek
- [S6] Plastic Bank, India rivers page (Meijer et al. 2021, Table S5) — https://rivers.plasticbank.com/rivers/country/india
- [S7] Plastic Fischer project data via Pinwheel and plasticfischer.com — see [companies.md](../research/companies.md)
- [S8] Mr. Trash Wheel (operator claim, 500 tons/yr) — see [companies.md](../research/companies.md)
- [S9] DutchNews, 17 Sep 2024, citing a City of Amsterdam report on the Westerdok Bubble Barrier — see [companies.md](../research/companies.md)
- [S10] RanMarine WasteShark+ product page — https://www.ranmarine.io/wasteshark/
- [S11] Hindustan Times on BMC's nullah trash booms (9 installed, 14 planned, ≈ ₹1 crore each, t/day) — URL and quotes in [interception-hardware.md](../research/components/interception-hardware.md) and [landscape.md](../research/landscape.md)
- [S12] Free Press Journal, 30 Jul 2026, on BMC's ₹14.5-crore two-year boom O&M contract (Virgo Specialties) — see [interception-hardware.md](../research/components/interception-hardware.md)
- [S13] NASA POWER climatology API (Mumbai) and Indian retailer product pages, opened 2026-10-04 — see [sensing-edge-bom.md](../research/components/sensing-edge-bom.md)
- [M:…] keys in [research/mumbai-context.md](../research/mumbai-context.md) (sources S1–S21: The Ocean Cleanup, Lokmat, Plastic Bank / Meijer et al. 2021, BRIMSTOWAD summary, BMC ESR 2022-23, beach-clean-up and ban-enforcement reporting, EOW FIR coverage)
- [P:…] keys in [research/components/policy-economics.md](../research/components/policy-economics.md) (P1 PWM Rules 2016 as amended / EPR guidelines; P4–P7 BMC budget 2026-27; P8 Maharashtra minimum wages)
- [S14] ITOPF Technical Information Paper 3 (boom escape velocity ≈ 0.35 m/s) — see [interception-hardware.md](../research/components/interception-hardware.md)
