# Q&A prep — NullahNet (InnovateX Theme 3, Delhi zonal)

> Every number below is bound to a cited fact (`research/fact-check.md`) or rendered from a committed run (`eval/RESULTS.md`). Labels:
> - **SIMULATED**: digital-twin output.
> - **SENSITIVITY**: an assumption-driven what-if.
> - **SYNTHETIC**: generated test data.
> - **PLANNED**: not built yet.
>
> Rule for the room: if a number isn't on this sheet, say "we haven't measured that yet".

## A. "Is this real?"

**1. "The Ocean Cleanup is already doing this in Mumbai. Why you?"**
- They are putting Interceptors at two creek mouths, Malad and Trombay, expecting {{f:F02|61 to 92 tonnes}} a year from the first systems. That is about {{f:D01|1.2–1.8 %}} of the estimate.
- Plastic Fischer also runs TrashBooms in Mumbai, including one at Usha Nagar, Bhandup, with third-party verified kilograms.
- BMC runs its own booms: a 2025 report described {{f:F12|9}}, expanding to {{f:F12|23}}.
- We are not a new barrier operator. We propose to test whether fill sensing, tide-timed clearance and checked records improve BMC's existing boom workflow. Our records could also feed the per-kilogram verification Plastic Fischer already uses.

**2. "Your results are simulated. Why should we believe them?"**
- Don't believe them as field results; we don't present them that way. They come from one model with assumed plastic and boom behaviour, varied over {{r:n_draws}} parameter settings.
- The inputs are real: ERA5 rain, forecasts as they were archived, and a fitted tide.
- What the results do is choose our first experiments: capture geometry and pocket retention in a tow tank.
- Circularity, stated openly: escaped kilograms come from the same assumed model the policies act on.

**3. "Did you use real forecasts or actual rainfall?"**
- Both, for different jobs. Decisions use the JMA day-ahead forecast as archived: the value issued 24 hours before. Outcomes use ERA5 rain.
- One earlier run had a look-ahead bug in a 48-hour horizon. We fixed it, re-ran once, and disclosed both runs.

**4. "Why is your dispatch gain against today's schedule so small?"**
- Because it is small, and we say so: {{r:p2p0_med}} escaped vs an *assumed* fixed roster, central 90% scenario range {{r:p2p0_lo}} to {{r:p2p0_hi}} (SIMULATED).
- The robust comparison is our full policy against a fill-fraction-ranked rule: {{r:p2p1_med}}, lower in {{r:p2p1_n}} of {{r:n_draws}} settings.
- That comparison bundles three changes. Separated in the model: tide timing alone {{r:abl_tide_med}} (range {{r:abl_tide_lo}} to {{r:abl_tide_hi}}), forecasts {{r:abl_fc_med}}, ranking by kilograms {{r:abl_mass_med}}. None clears zero on its own; only the full combination does.

**5. "So what *is* the big lever?"**
- In our model, capture losses: {{r:ent_esc}} of escaped plastic passes under or through the boom; overflow is {{r:over_esc}}.
- But {{r:ent_floor_esc}} of all escape is a still-water leak we *assumed*, only {{r:ent_vel_esc}} is driven by flow speed, and just {{r:expo_kg}} of arriving plastic comes at high speed. So the first measurement is a real boom's leak.
- That pattern comes from a capture curve we assumed, informed by oil-boom guidance (about {{f:F14|0.35 m/s}} across the boom).
- Then angle and pocket retention. Under the assumed curves, a 30° boom gives {{r:ang30_med}} and a pocket that halves re-floating gives {{r:pk5_med}} (SENSITIVITY: these follow from our assumptions; they are not confirmations).

## B. Flood safety and hardware

**6. "Won't a barrier in a nullah make flooding worse?"**
- It could, which is why flood safety is our first design constraint and our first test.
- The fail-open section is *intended* to swing open before the boom backs water up beyond a set head.
- We will measure its opening head, delay, residual obstruction and reset after jams in the tow tank (test T3), and only then state an operating envelope.
- In the twin it changes capture by just {{r:fuse_med}}; it is a safety feature, not a capture feature.
- The twin does not model street flooding. Its nearest measures (SIMULATED): hours with debris spilling over a full boom, {{r:ovf_p2}} site-hours under our policy vs {{r:ovf_p1}} under the fill-fraction rule and {{r:ovf_p0}} under the roster, so our policy does not reduce them; and hours with water above a boom's bypass level, {{r:byp_h}} site-hours, set by tide and flow and the same under every policy. We make no flood-reduction claim.

**7. "What happens at peak rain plus high tide? Does the release dump everything?"**
- We don't know yet; that's a test, not an answer.
- The design puts the pocket at the bank, outside the release path, intending that stored catch stays when the section opens. Whether it does, under what flow, and with what fouling, is measured in T3.
- At peak flow some loss is physics. We count it in capture efficiency rather than hide it.

**8. "Is the one-way pocket novel?"**
- No. Passive floating litter traps for tidal waterways exist: Bandalong lists them as suitable for {{f:F21|"waterways wider than 2 metres, including waterways subject to tidal action"}}.
- Our proposal is narrower: retrofitting BMC's existing steel-net booms (angle, pocket, fail-open section) plus the operations and evidence layer. We claim only what the tow tank shows.

**9. "What about corrosion, theft and biofouling?"**
- HDPE floats and SS316 fittings; existing traps use HDPE and marine-grade aluminium ({{f:F21|Bandalong}}).
- The node goes on a pole above the high-water mark, with tamper and tilt flags and a lens-cleaning routine in the crew checklist.
- Power is sized for July: {{f:F15|3.79 kWh/m²/day}} vs {{f:F15|7.09}} in May. The node's load is an assumption until we bench-measure it.

## C. Sensing and data

**10. "Can a camera see plastic at night, in rain, in black nullah water?"**
- Not reliably.
- Fill comes from the camera's view of the mat area in the pocket. When the camera is degraded, fill is reported "unknown" and crews follow the roster.
- Detector status: {{r:det_line}}

**11. "Show an empty pocket at high tide and a full pocket at low tide. What does your range sensor see?"**
- The ultrasonic sensor sits over open water and measures water level (stage), not fill. A single downward range over a pocket would confuse tide, mat thickness and patchy cover.
- Fill comes from the camera's mat-area estimate, calibrated against a painted gauge in the pocket.
- Test T4 checks empty, partial and thick-mat cases at different water levels, with a required error and availability before we use fill for dispatch.

**12. "How do you turn counts into kilograms?"**
- We don't, from counts. We use pocket area or volume × bulk density, checked at the weighbridge, plus random sort samples to correct for water and organic weight.
- Density matters: in our synthetic test, debris a quarter denser than assumed raises honest false flags to {{r:mrv_dens125}}. So density is calibrated per site.

**13. "Hash chains don't make data true."**
- Correct. With an external anchor, edits are detected ({{r:mrv_trunc_anchor}} for tail truncation; the chain alone catches {{r:mrv_trunc_chain}}).
- Truth needs *independent* evidence: before/after camera images, weighbridge and GPS.
- Across our SYNTHETIC fraud mixture, {{r:mrv_recall}} of bad claims are caught at {{r:mrv_ff}} false flags; inflated claims alone {{r:mrv_infl}}; small inflations only {{r:mrv_small}}.
- Precision is {{r:mrv_prec5}} when one claim in twenty is fraudulent, so a flag means review, never an automatic penalty.

**14. "Whose keys, scales and records stop a contractor supplying consistent but false evidence, or counting the same waste twice?"**
- Sensor and anchor keys stay with the city or an independent auditor, never with the contractor.
- Weighbridge slips come from a third-party bridge, and each load carries a batch ID linked to its before/after images.
- The auditor samples loads at random; duplicate batch IDs and impossible GPS tracks are rejected; disputes go to a named reviewer.
- This custody design is PLANNED; today we have the signing and chaining code.

**15. "Why should we trust the problem size?"**
- The {{f:F01|5 million kg}} a year is The Ocean Cleanup's 2026 survey estimate, not a measurement.
- A global model (Meijer et al. 2021) puts Malad Creek alone at {{f:F05|2,724 t/yr}}.
- Methods disagree on tonnage; our design doesn't depend on the exact figure.

## D. Money and adoption

**16. "How much does one site cost, and what is the payback?"**
- One sensor node is {{f:D04|₹83,481.98}} in *listed parts*, enclosure included (URL and date for each part in the prototype plan). That is about {{f:D03|0.8 %}} of a boom's reported ₹1-crore price.
- It excludes installation, anchoring, the retrofit, connectivity, servicing and waste handling.
- We do not claim a payback. The pilot must measure the extra verified dry kilograms per rupee against a stated baseline.

**17. "Why does this beat a cheap kilogram-ranked roster or an extra clearance visit?"**
- In our model, a cheap kilogram-ranked sensor rule gets part of the way: {{r:abl_mass_med}} vs the fill-fraction rule. Our full policy vs that kilogram-ranked rule is {{r:p2p1m_med}}, with a range ({{r:p2p1m_lo}} to {{r:p2p1m_hi}}) that crosses zero. So a simple kg-ranked rule may be enough; the field pilot should test it first.
- An extra visit costs crew-hours. Our comparisons hold crew-hours equal.

**18. "Who takes the wet film, who pays to prepare and transport it, and what proves final disposal?"**
- Nobody buys it for its material value; waste-picker groups report sachets sometimes go to cement kilns for free ({{f:F25|Break Free From Plastic, 2023}}).
- Under the PWM Rules, non-recyclable plastic may go to end-of-life routes such as cement-kiln co-processing through registered processors. Category II covers {{f:F22|"carry bags, plastic sachet or pouches"}}.
- The chain we propose: dry and sort at a material recovery facility, then send it to a registered processor with a receiving record. Drain-plastic EPR eligibility is not settled, so producer money is upside.

**19. "Why will BMC adopt this?"**
- It plugs into contracts BMC already runs: booms of about {{f:F12|₹1 crore}} each and a {{f:F13|₹14.5 crore}} two-year maintenance contract across six waterways.
- It changes *when* crews go and *what proves* what they removed.
- BMC's proposed {{f:F24|₹13,000 crore}} flood plan adds mesh screens and expands water-level sensors beyond {{f:F24|seven}} pilot sites. Compatibility with those works is UNVERIFIED.
- The Mithi case shows why verified quantities matter: a police SIT's FIR alleges a wrongful loss of more than {{f:F11|₹65.54 crore}} (under investigation).

**20. "Isn't the real fix waste collection upstream?"**
- Yes; interception is the last line of defence. BMC itself estimated that {{f:F08|500 t/day}} goes uncollected into drains.
- Per-outfall data could help wards target collection and enforcement.

## E. Scale, plan and failure

**21. "How does it scale across India?"**
- The software takes local tide, rain and site data as configuration.
- Each new site still needs a survey, an anchoring design, an operating agreement and permissions: repeated local engineering, not a copy-paste.
- Gated outfalls are not modelled yet.

**22. "What will you have built by 1 December?"**
- Committed: a closed-loop bench rig — the tow-tank boom models (straight, angled, pocket, fail-open), the sensor node over the pocket, the twin and the signed records — with measured retention, head rise and fill error.
- A field pilot depends on permission, safety and a site survey.

**23. "Where does a longer, angled boom and a bank pocket fit without blocking access or the conveyor?"**
- At 20° the boom is {{r:ang20_len}}× the channel width, which may not fit narrow nullahs. That is why we start with one surveyed site and a dimensioned drawing.
- The concept sketch is not to scale; land, anchor and access permissions come first.

**24. "What happens when power, communications or a sensor fail during a storm?"**
- The fail-open section is mechanical and needs no power or cloud.
- The node buffers records locally and flags health problems; missing fill becomes "unknown" and crews revert to the roster.
- Outage-recovery behaviour is an acceptance test in the prototype plan.

**25. "Why these four sites?"**
- They are real outfalls located on OpenStreetMap: Mithi to Mahim Creek, Oshiwara to Malad Creek, the Dahisar mouth, and Trombay (an approximate geocode).
- They are river mouths and creeks, not the small nullah outfalls we target, and flap-gated outfalls are not modelled.

**26. "Can a city actually deploy your software stack?"**
- Mostly. The detector stack (Ultralytics YOLO) is AGPL-3.0, so serving a modified version over a network obliges publishing its source. We would publish ours or swap to a permissively licensed detector.
- Our data is CC BY 4.0 or ODbL, with attribution shown in the dashboard. Details are in the project README.

**27. "How many tonnes would this keep out of the sea?"**
- We have measured none. This is the arithmetic the pilot would test, labelled ILLUSTRATIVE ESTIMATE (`eval/impact_estimate.py`).
- A BMC boom reportedly collects {{f:F12|2.5–3 t/day}} in the monsoon, mixed garbage rather than only plastic. If that is the {{r:fwce_p0}} our twin says a boom retains under today's assumed roster, about {{r:imp_esc}} a day gets past each boom.
- Timing the crews alone: a median {{r:imp_disp}} less escaping per boom over a {{r:imp_days}}-day monsoon, and the range includes no gain (SIMULATED ratio).
- Angled boom, fail-open section and pocket together: a median {{r:imp_retro}} per boom per monsoon, range {{r:imp_retro_span}} (SENSITIVITY ratio from assumed capture curves).
- Every factor except the reported catch is assumed. The tow tank and one surveyed site exist to replace them.

## Don't say
**Don't say:** "tamper-proof" · "blockchain" · "can't flood" · "zero leakage" · "verified plastic kilograms" without "against our evidence rules" · any absolute tonnes from the twin · the illustrative per-boom tonnes as results (say "illustrative arithmetic") · "our trap is new" · "the booms have no sensors" (say "we found no public evidence") · "39 of 40 seasons" (say "parameter settings") · anything implying guilt in the Mithi investigation.
