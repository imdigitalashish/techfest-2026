# Q&A prep — DustLedger (InnovateX Theme 2, Delhi zonal)

*Rendered from `deliverables/src/qa-prep.md` by `eval/render_docs.py`. Run numbers come from committed results; cited numbers are bound to `research/fact-check.md` (checked by `eval/check_docs.py`). Rule for every answer: say what's **built**, what's **simulated**, what's **planned**, and never claim more. Revised after two cross-model reviews (`reviews/`).*

**Never say:** "tamper-proof" · "we will reduce Delhi's AQI by …" · "clean sites can keep working" (it's a proposal) · "low-cost sensors are accurate for dust" · "no one else does this" (say "we didn't find it in the product pages we reviewed") · "field-validated" (nothing is yet).

## The five you will almost certainly get

**Q0. AQI is probably the most crowded theme here. Why you?** (30 s)
"Most teams will measure city AQI or predict tomorrow. Delhi already has 47 reference monitors, a state forecasting system, and vendors streaming PM to the DPCC cloud. We target a different decision: which construction site actually added the dust? DustLedger is a wind-resolved fence-line ring that says 'inconclusive' when it can't tell, so inspectors can start where the evidence points. Our evidence today is a simulation on real Delhi background and wind, and we'll test the ring on a known dust source by December."

**Q1. What have you actually built?**
The data pipeline on four CPCB/DPCC monitors with ERA5 meteorology; a forecasting benchmark on a time-ordered split; an attribution replay where the background and wind are real but the sites, sensors and plumes are simulated, stress-tested after two independent reviews; a parts list priced from listings we opened; a power estimate from datasheets; and an offline demo of the regulator view on simulated sites. The sensor ring, misting line, swirling-wind check and tamper detection are designs for Round 2. This is feasibility evidence, not field validation.

**Q2. Construction is only a few per cent of Delhi's PM. Why bother?**
Correct, and our slides say so: IIT Kanpur's study for DPCC put construction material at 2-5% of ambient PM10 (data 2013–14; track-out onto roads counts as road dust). Yet dust-generating construction is restricted citywide from Nov 1 – Jan 31 in the reported 2026-27 plan. We're proposing an evidence tool for targeted inspection, not a city-AQI fix. Near-site exposure for workers and neighbours may matter more than the city share, but we haven't measured it.

**Q3. Low-cost sensors are inaccurate, especially for dust. Why trust them?**
In absolute terms they're qualitative for construction PM10: CSTEP tested six models from five Indian makers for a year and says exactly that, and it doesn't validate our method. Differencing identical sensors removes only common-mode error; it doesn't make them respond equally to coarse dust, and a difference is not proof of cause. So the first experiments are a side-by-side agreement test, a reference co-location and a blind known-source test. Until then the output is a triage signal; DPCC verifies with reference instruments before any penalty.

**Q4. Delhi's worst hours are calm. Then what?**
Below 0.5 m/s our method says "inconclusive", and inconclusive never counts as clean. In Nov–Jan, ERA5's 25 km grid shows wind below 0.5 m/s in 4.0% of hours and below 1 m/s in 16.2%. Calm at a real site, behind buildings and hoardings, hasn't been measured; the ring will log it from day one, and we'll report the abstention rate by season.

## Method and evidence

**Q5. Isn't your simulation rigged in your favour?**
Our first simulator was, and a reviewer said so. We rebuilt it with sensor fouling, separate dust and ambient gains, work on some nights, spatial gradients, a neighbour site, a road and a biased wind vane, and a second reviewer added a stronger baseline (a 14-day median of weekly reference visits). Over all hours, self-calibration scores 57.4 vs 64.9 µg/m³. **In work hours it is no better (115.8 vs 115.0).** Its gain is fewer false alarms above 50 µg/m³ (FAR 0.145 vs 0.305). The test uses fresh seeds but isn't blind: we saw the test period during earlier versions.

**Q6. A neighbouring site or a road?**
A neighbour's plume can hit just one side of the ring, so it doesn't always land in the "background". Today's method doesn't detect that; a check for nodes that disagree with the wind direction is planned, not built. Rings on neighbouring sites, or an inspector, resolve it. Our stress test includes a neighbour site and a road; they're a large part of the remaining error.

**Q7. Why not do forecasting? You're ML people.**
We tried, on real data: yesterday's value predicts tomorrow's daily PM2.5 within 23.8 µg/m³ at four Delhi monitors. Our ML without future weather did −2.2% to −1.3% vs that; only an oracle that used tomorrow's actual weather gained 4.4%, and no forecaster has that. The station history starts in Feb 2025, which is short. IITM already runs city forecasting, so we use forecasts only to schedule dusty work.

**Q8. Isn't this just Aeroqual or Envirosuite, cheaper?**
Fence-line monitoring is established for mines and industry, and we borrow it. Our claim is narrower: a low-cost workflow for Indian construction sites combining a wind-resolved ring, abstention, tamper evidence and control. We didn't find it in the Indian product pages we reviewed. Whether it beats incumbents on cost and performance is UNVERIFIED.

**Q9. What stops a contractor spraying your sensors?**
Nothing stops it; we aim to detect it. One node reading lower than the ring while its humidity jumps is a spray signature we could flag. Records are signed on the device and hash-chained, so edits become detectable if the keys are in secure storage and the chain is anchored off-site. Sealed boxes, flow-metered misting and the site's mandatory CCTV (100% coverage required) are cross-checks. None of this is tested yet, and authenticated records don't prove honest exposure.

## Cost, impact and feasibility

**Q10. What does it cost, and who pays?**
Parts for one site — four nodes, a wind sensor, a gateway and a misting line — come to ₹60,711 at listings we opened on 4 Oct, incl. GST. That's parts only: masts, cabling, data plan, installation and upkeep aren't in it, and the wind sensor alone is ₹14,810. For scale, one construction-site violation costs ₹1 lakh to ₹2 lakh under CAQM's 2024 schedule as reported. Willingness to pay and legal usefulness are UNVERIFIED; we'd first test demand for inspection triage, separately from any permission to keep working.

**Q11. How much will it reduce AQI, or deaths? What have you saved?**
Nothing is measured yet, and we won't extrapolate to city AQI or health. Construction was a small share of city PM in IIT Kanpur's study, and we haven't verified how well misting suppresses dust. The test we propose: misting on and off in randomised blocks of comparable work, an independent reference measurement, and metered water — and we'll check that misting suppresses dust rather than just wetting the sensor.

**Q12. Your trial is in November — isn't construction restricted then?**
Yes: the reported plan prohibits dust-generating works from Nov 1 – Jan 31. A real-site trial can only happen before 1 Nov, with a site and approvals in place. Otherwise our evidence is an approved, safety-controlled dust-source test, and we'll report it as a controlled test, never as field validation.

**Q13. Will it survive dust, fog, heat and outages?**
Not tested yet. The SPS30's specified range is -10 to +60 °C and 0-95 %RH non-condensing, so fog performance is UNVERIFIED and needs a humidity flag and correction. Our power numbers are model estimates: about 10.2 Wh/day per node from datasheets, 2.1× that from a 10 W panel in an average December, 12.1 days on battery. Complete-system power and service intervals come from bench measurement.

**Q14. Calibration standard?**
The only sensor target we've verified is US EPA's for PM2.5 (R² > 0.70, RMSE < 7 µg/m³). It isn't a PM10 construction-dust criterion. PM10 targets and any CPCB certification route are UNVERIFIED; we're sourcing them.

**Q15. Maintenance?**
Optical sensors' inlets and fans need cleaning in dust; the interval will come from our bench test, not a guess. Self-calibration should flag a node drifting away from the ring, telling the supervisor which node to service. Solar panels at a dusty site need wiping too.

**Q16. Can you drop the expensive wind sensor?**
Not for attribution: the method needs the site's own wind direction, which a 25 km grid like ERA5 smooths out. A shared wind sensor across adjacent sites is an idea we haven't tested.

## Context

**Q17. Why Delhi?**
Delhi restricts dust-generating construction citywide every winter, already mandates CCTV at sites, and runs an AI-enabled command centre with 334 enforcement teams from October 1. The policy hooks exist; site-level measurement doesn't.

**Q18. Delhi's air is improving. Why now?**
The minister reported annual PM2.5 falling from 104 to 96 µg/m³ in 2025, still several times the WHO guideline, and the winter construction restrictions continue in the 2026-27 plan.

**Q19. Isn't dust less harmful than smoke?**
Per microgram, the evidence points that way. The lead author of the Lancet 10-city study warns "we cannot remain too fixated on curbing dust". We aren't claiming to fix Delhi's health burden. A PM-only node can't identify diesel or waste-burning smoke; that would need extra gas sensors.

**Q20. Other cities?**
The differential method needs no city-specific forecast model, but siting, local aerosol, climate and calibration need checking city by city. NCAP notes only four cities — Delhi, Pune, Mumbai and Ahmedabad — have a decision-support system.

**Q21. Data ownership and privacy?**
The site owns raw data; the regulator gets signed summaries and exceedance events; the public sees site rankings, not personal data.
