# Q&A prep — NullahNet (InnovateX Theme 3, Delhi zonal)

> Every number below is either bound to a cited fact (`research/fact-check.md`) or rendered from a committed run (`eval/RESULTS.md`). Labels: **SIMULATED** = digital-twin output · **SENSITIVITY** = assumption-driven what-if · **SYNTHETIC** = generated test data. Rule for the room: if a number isn't on this sheet, say "we haven't measured that yet".

## A. "Is this real?"

**1. "The Ocean Cleanup is already doing this in Mumbai. Why you?"**
They are putting Interceptors at two creek mouths, Malad and Trombay, expecting {{f:F02|61 to 92 tonnes}} a year from the first systems. That is about {{f:D01|1.2–1.8 %}} of the estimated leak. BMC runs its own booms at nullah mouths ({{f:F12|9}} today, {{f:F12|23}} planned). We don't build barriers; we make the city's existing booms measurable, better timed and verifiable. Our records could feed the same per-kilogram verification Plastic Fischer already uses.

**2. "Your results are simulated. Why should we believe them?"**
Believe the ranking, not the tonnage. Inputs are real: ERA5 rain, forecasts as they were archived, and tides fitted with RMSE {{r:tide_rmse_mithi}} m. The process is assumed, and every assumed parameter is varied across {{r:n_draws}} Monte Carlo draws. Tuning used 2019–2023; 2024–25 were held out. We state the circularity openly: escaped kilograms come from the same assumed model the policies act on. Round 2 calibrates it with tagged-item releases at real outfalls.

**3. "Did you use real forecasts or actual rainfall?"**
Both, for different jobs. Decisions use the JMA day-ahead forecast exactly as archived, so the policy never sees the future. Outcomes use ERA5 rain. One earlier run had a look-ahead bug in a 48-hour horizon; we fixed it, re-ran once, and disclosed both runs.

**4. "Why is your dispatch gain against today's schedule so small?"**
Because it *is* small, and we say so: {{r:p2p0_med}} escaped vs the fixed schedule, with a 90% interval from {{r:p2p0_lo}} to {{r:p2p0_hi}} (SIMULATED). The robust result is against the obvious sensor rule, "clear when full": tide-aware timing gives {{r:p2p1_med}}, better in {{r:p2p1_n}} of {{r:n_draws}} draws. Clear-when-full alone is worse than the schedule ({{r:p1p0_med}}). The lesson: sensors without tide-aware timing can make things worse.

**5. "So what *is* the big lever?"**
Capture. In the twin, {{r:ent_esc}} of escaped plastic slips under or through the boom (SIMULATED; the share includes an assumed still-water leak). Overflow is {{r:over_esc}} and flood release {{r:byp_esc}}. Oil-spill guidance puts boom escape at about {{f:F14|0.35 m/s}} across the boom. So the hardware levers are angling the boom and a one-way pocket. With the pocket halving tidal re-floating, escape changes by {{r:pk5_med}} (SENSITIVITY). The flume must measure the real retention.

## B. Flood safety and hardware

**6. "Won't a barrier in a nullah make flooding worse?"**
That is our first design constraint. The fail-open fuse opens at a set head difference, so a jammed boom can't back water up. In Round 2 we report a measured head-rise envelope from flume tests; we will never call the boom flood-proof. In the twin, the fuse alone changes capture by only {{r:fuse_med}}. It is a safety feature, not a capture feature.

**7. "What happens at peak rain plus high tide? Does the fuse dump everything?"**
No. The pocket sits at the bank, outside the fuse path, so stored catch stays when the fuse opens; only the arriving flow passes. At peak flow some loss is physics. That is why we report flux-weighted capture efficiency (FWCE), so peak-flow losses are counted rather than hidden.

**8. "Is the one-way pocket novel?"**
No. Passive floating litter traps for tidal waterways exist: Bandalong lists them as suitable for {{f:F21|"waterways wider than 2 metres, including waterways subject to tidal action"}}. Our claim is narrower: a retrofit for BMC's existing steel-net booms (fail-open fuse plus instrumented pocket) and the operations and evidence layer around it. We claim only what our flume shows.

**9. "What about corrosion, theft and biofouling?"**
HDPE floats and SS316 fittings; existing traps use HDPE and marine-grade aluminium ({{f:F21|Bandalong}}). The node sits on a pole above the high-water mark, with tamper and tilt flags, a lens wiper, and maintenance in the crew checklist. The power budget is sized for July, the darkest month at {{f:F15|3.79 kWh/m²/day}} vs {{f:F15|7.09}} in May.

## C. Sensing and data

**10. "Can a camera see plastic at night, in rain, in black nullah water?"**
Not reliably, which is why the primary reading is pocket fill from an ultrasonic range sensor, with the camera as support. Detector status: {{r:det_line}}

**11. "How do you turn counts into kilograms?"**
We don't, from counts alone. We use pocket volume × bulk density, checked at the weighbridge, plus random sort samples to correct for water and organic weight. Count-to-mass conversions are unreliable for films.

**12. "Hash chains don't make data true."**
Correct. They make edits detectable (tampering detected: {{r:mrv_tamper}} in tests). Truth comes from *independent* evidence: before/after fill, weighbridge and GPS. On SYNTHETIC records we catch {{r:mrv_recall}} of inflated claims at {{r:mrv_ff}} false flags, against {{r:mrv_base}} for a simple ratio check. Small inflations, up to half again the true weight, are hard: only {{r:mrv_small}} caught. Precision is {{r:mrv_prec5}} when one claim in twenty is fraudulent, so a flag means a review, never an automatic penalty.

**13. "Why should we trust the problem size?"**
The {{f:F01|5 million kg}} a year is The Ocean Cleanup's 2026 survey estimate for the metropolitan region, not a measurement. A global model (Meijer et al. 2021) puts Malad Creek alone at {{f:F05|2,724 t/yr}}. The methods disagree on exact tonnage; both put Mumbai among the world's largest urban sources. Our design doesn't depend on the exact figure.

## D. Money and adoption

**14. "How much does one site cost, and what is the payback?"**
One sensor node is {{f:D04|₹83,481.98}} of priced parts, enclosure included (URL and date for each part in the prototype plan). That is about {{f:D03|0.8 %}} of a ₹1-crore boom. Boom upkeep runs about {{f:D02|₹1.2 crore}} per site-year (our arithmetic from the {{f:F13|₹14.5 crore}} two-year contract). We do not claim a payback period; it depends on an effect size the pilot must measure.

**15. "Who buys wet, dirty film?"**
Nobody, for its material value. Waste-picker groups report sachets sometimes going to cement kilns for free ({{f:F25|Break Free From Plastic, 2023}}). Under the PWM Rules, non-recyclable plastic may go to end-of-life routes such as cement-kiln co-processing through registered processors, and Category II covers {{f:F22|"carry bags, plastic sachet or pouches"}}. Whether drain-recovered plastic earns EPR certificates is not settled in the rules, so we treat it as upside.

**16. "Why will BMC adopt this?"**
It slots into contracts BMC already runs: booms at about {{f:F12|₹1 crore}} each and a {{f:F13|₹14.5 crore}} maintenance contract. It changes *when* crews go and *how* they are paid, with no new civil works. BMC's {{f:F24|₹13,000 crore}} flood plan already adds {{f:F24|8 to 10 feet}} mesh screens and expands water-level sensors from {{f:F24|seven}} pilot sites; we are the measurement and dispatch layer for such assets. The Mithi case, where the police SIT's FIR alleges a wrongful loss of more than {{f:F11|₹65.54 crore}} (under investigation), shows why verified quantities matter.

**17. "Isn't the real fix waste collection upstream?"**
Yes. Interception is the last line of defence. BMC itself estimated that {{f:F08|500 t/day}} goes uncollected into drains. Our per-outfall data ranks catchments by leakage, so wards can target collection and enforcement where it matters.

## E. Scale and plan

**18. "How does it scale across India?"**
Every site-specific input is configuration: tide, rain, geometry, and gated or open outfall. Tide and rain feeds are global. A new coastal city needs site surveys and its contractors on the records system, not new software.

**19. "What will you have built by 1 December?"**
A tow-tank flume comparing a straight boom, an angled boom and the one-way pocket, with measured capture, retention under reversal and head rise. An edge node over the flume streaming fill data into the twin. The dashboard and evidence records, live. Hardware is PLANNED today; we say so on every slide.

**20. "Why these four sites?"**
They are real outfalls located on OpenStreetMap: Mithi to Mahim Creek, Oshiwara to Malad Creek, the Dahisar mouth, and Trombay (approximate). They cover river mouths and creeks on both coasts. Flap-gated outfalls are not modelled yet, and we say so.

**21. "Can a city actually deploy your software stack?"**
Mostly yes. The detector stack (Ultralytics YOLO) is AGPL-3.0, which obliges anyone serving a modified version over a network to publish its source. For a municipal deployment we would publish our code or swap in a permissively licensed detector. The data we use is CC BY 4.0 or ODbL, with attribution shown in the dashboard. Details are in the project README.

## Don't say
**Don't say:** "tamper-proof" · "blockchain" · "can't flood" · "zero leakage" · any absolute tonnes from the twin · "our trap is new" · anything implying guilt in the Mithi investigation.
