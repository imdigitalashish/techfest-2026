# Q&A prep — DustLedger (InnovateX Theme 2, Delhi zonal)

*Rendered from `deliverables/src/qa-prep.md` by `eval/render_docs.py`; run numbers come from committed results and cited numbers are bound to `research/fact-check.md` (checked by `eval/check_docs.py`). Rule for every answer: say what's **built**, what's **simulated**, what's **planned**, and never claim more.*

**Never say:** "tamper-proof" · "we will reduce Delhi's AQI by …" · "clean sites can keep working" (it's a proposal) · "low-cost sensors are accurate for dust" · "no one else does this" (say "we didn't find it in the product pages we reviewed").

## The five you will almost certainly get

**Q0. AQI is the most crowded theme here. Why should we pick you?** (30 s)
"Most teams will measure city AQI or predict tomorrow. Delhi already has 47 reference monitors, a state forecasting system, and vendors streaming PM to the DPCC cloud. We target the missing decision: which construction site actually added the dust? DustLedger combines a wind-resolved fence-line ring, honest 'inconclusive' calls and attributed suppression, so inspectors go where the evidence points instead of everyone being stopped. Our attribution evidence is simulated today, but it's Delhi-specific, testable, and we'll show it on a real dust source by December."

**Q1. What have you actually built?**
The data pipeline on four CPCB/DPCC monitors with ERA5 meteorology, a next-day forecast benchmark on a time-ordered split (1,034 test station-days), and an attribution replay where the background and wind are real but the site, sensors and plume are simulated — stress-tested after an independent review. The parts list is priced from listings we opened and the power budget comes from datasheets. The sensor ring, misting line and tamper detection are designs for Round 2. This is feasibility evidence, not field validation.

**Q2. Construction is only a few per cent of Delhi's PM. Why bother?**
Correct, and we say it on our slides: IIT Kanpur's study for DPCC put construction material at 2-5% of ambient PM10 (data 2013–14). That's exactly the problem: a small source gets the bluntest tool — every site stopped from Dec 10 – Jan 20 and restricted from Nov 1 – Jan 31. Measuring each site lets enforcement target the dirty ones. We don't claim a city-AQI gain. Near-site exposure for workers and neighbours is real but unquantified by us.

**Q3. Low-cost sensors are inaccurate, especially for dust. Why trust them?**
In absolute terms they're qualitative for construction PM10: CSTEP tested six models from five Indian makers for a year and says exactly that. Differencing identical sensors removes only *common-mode* error; it doesn't make them respond equally to coarse dust. So a controlled dust test and a reference co-location come first, and the output is a triage signal for inspectors, not a legal measurement. Penalties still need DPCC's reference instruments.

**Q4. Delhi's worst hours are calm. Then what?**
Then we say "inconclusive", and inconclusive never counts as clean. In Nov–Jan, ERA5 wind is below 1 m/s in 16.2% of hours and below 0.5 m/s in 4.0%; a site vane will see more calm than that 25 km grid, so these are lower bounds. We'll report the abstention rate by season. Better calm-wind handling is on our research list, not a claim.

## Method and evidence

**Q5. Isn't your simulation rigged in your favour?**
Our first simulator was, and an independent reviewer said so: quiet hours were guaranteed clean and the sensors responded to dust and ambient air identically. We rebuilt it (v2.1) with sensor fouling, separate dust and ambient gains, work on some nights, spatial gradients, a neighbour site, a road and a biased wind vane, added a fair baseline (weekly reference visits), and ran the held-out test once. The ring + self-calibration still wins in all four scenarios — 57.4 vs 69.4 µg/m³ overall — but by 17%, not the bigger gain the easy simulator showed. It's still a simulation until the dust test.

**Q6. A neighbouring site or a road?**
A neighbour's plume can hit just one side of the ring, so it doesn't always land in the "background". When the wind signature and the node pattern disagree, the system says inconclusive. Rings on neighbouring sites, or an inspector, resolve it. Our v2.1 stress test includes a neighbour site and a road; that's where most of the remaining error comes from.

**Q7. Why not do forecasting? You're ML people.**
We did, on real data: yesterday's value predicts tomorrow's daily PM2.5 within 23.8 µg/m³ at four Delhi monitors, and our gradient boosting added at most 4% with one year of history. IITM already runs city forecasting. We use forecasts only to schedule dusty work.

**Q8. Isn't this just Aeroqual or Envirosuite, cheaper?**
Fence-line attribution is established for mines and refineries, and we borrow it. Our claim is narrower: a low-cost workflow for Indian construction sites combining wind-resolved attribution, abstention, tamper evidence and control. We didn't find it in the Indian product pages we reviewed; that doesn't mean nobody anywhere has built it.

**Q9. What stops a contractor spraying your sensors?**
Nothing stops it; we aim to detect it. One node reading lower than the ring while its humidity jumps is a spray signature we can flag. Records are signed on the device and hash-chained, so edits become detectable if the keys are in secure storage and the chain is anchored off-site. Sealed boxes, flow-metered misting and the site's mandatory CCTV (100% coverage required) are cross-checks. None of this is tested yet.

## Cost, impact and feasibility

**Q10. What does it cost, and who pays?**
Parts for one site — four nodes, a wind sensor, a gateway and a misting line — come to ₹60,711 at listings we opened on 4 Oct, incl. GST. That's parts only: masts, cabling, data plan, installation and upkeep aren't in it. The wind sensor alone is ₹14,810. For scale, one violation is a ₹5 lakh flat fine for a large Delhi site. Near-term buyer case: evidence in disputes and targeted inspections. Permission to keep working through restrictions is a pilot we'd propose to CAQM, not an assumption.

**Q11. How much will it reduce AQI, or deaths?**
We don't know, and we won't extrapolate to city AQI or health. Construction is a small share of city PM, and we haven't verified how well misting suppresses dust. In the November trial we'll measure the fence-line increment with misting on and off, and the litres used.

**Q12. Your trial is in November — isn't construction banned then?**
Yes: Delhi prohibits dust-generating works from Nov 1 – Jan 31. So a real construction-site trial has to happen before 1 Nov or at a site permitted to operate. Our fallback, which needs no permission, is a controlled dust-source trial on campus with the same ring, wind sensor and misting line.

**Q13. Will it survive dust, fog, heat and outages?**
Not tested yet. On paper: the SPS30's operating range is -10 to +60 °C and 0-95 %RH non-condensing, so fog needs a humidity flag and correction; boxes are IP65; each node draws about 10.2 Wh/day by datasheet, a 10 W panel gives 2.1× that in December, and the battery covers 12.1 days without sun. A dust and fog bench test comes first.

**Q14. Calibration standard?**
The only sensor target we've verified is US EPA's for PM2.5 (R² > 0.70, RMSE < 7 µg/m³). It isn't a PM10 construction-dust criterion. PM10 targets and any CPCB certification route are UNVERIFIED; we're sourcing them.

**Q15. Maintenance?**
Optical sensors' inlets and fans need cleaning in dust; the interval will come from our bench test, not from a guess. Self-calibration flags a node drifting away from the ring, which tells the supervisor which node to service. Solar panels at a construction site need wiping too.

**Q16. Can you drop the expensive wind sensor?**
Not for attribution: the method needs the site's own wind direction, and a 25 km grid like ERA5 smooths it out. A shared wind sensor across adjacent sites is an idea we haven't tested.

## Context

**Q17. Why Delhi?**
Delhi stops every construction site each winter, already mandates CCTV, and runs an AI-enabled command centre with 334 enforcement teams from October 1. The policy hooks exist; the site-level measurement doesn't.

**Q18. Delhi's air is improving. Why now?**
The minister reported annual PM2.5 falling from 104 to 96 µg/m³ in 2025, which is still several times the WHO guideline, and the winter construction stops continue in the 2026-27 plan. Targeted enforcement matters more as the easy gains are taken.

**Q19. Isn't dust less harmful than smoke?**
Per microgram, the evidence points that way. The lead author of the Lancet 10-city study warns "we cannot remain too fixated on curbing dust". We aren't claiming to fix Delhi's health burden; we target an enforcement failure that costs workers wages. A PM-only node can't identify diesel or waste-burning smoke; that would need extra gas sensors.

**Q20. Other cities?**
The differential method needs no city-specific forecast model, but siting, local aerosol, climate and calibration need checking city by city. The hardware and software stay the same. NCAP notes only four cities — Delhi, Pune, Mumbai and Ahmedabad — have a decision-support system.

**Q21. Data ownership and privacy?**
The site owns raw data; the regulator gets signed summaries and exceedance events; the public sees site rankings, not personal data.
