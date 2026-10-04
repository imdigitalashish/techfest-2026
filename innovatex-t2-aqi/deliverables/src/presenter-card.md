# DustLedger — presenter card (Delhi zonal, 10 min)

**Open:** zonal-deck.pdf on your own laptop · backups B1–B6 after slide 10 · team fields on slide 1 filled in · this card printed.

| # | Time | Slide | Land this line |
|---|---|---|---|
| 1 | 0:00–0:20 | Title | "Delhi stops every site, clean or dirty, because it can't tell them apart." |
| 2 | 0:20–1:10 | Restrictions | {{v:F1|Nov 1 – Jan 31}} restricted; {{v:F1|Dec 10 – Jan 20}} total ban; GRAP-3 {{v:F3|16 days}} in 2025. |
| 3 | 1:10–2:00 | Monitors & fines | {{v:F5|47}} monitors at city scale; fines {{v:F6|₹1 lakh to ₹2 lakh}} by area; checklists, not dust. |
| 4 | 2:00–3:00 | Small source, blunt tool | Construction = {{v:F9|2-5%}} of ambient PM10 (IIT Kanpur); {{v:F7|1,378,199}} workers on the rolls. |
| 5 | 3:00–3:50 | Tools fall short | Winter PM10 ~{{v:F11|314}} µg/m³: a fence sensor mostly measures Delhi. |
| 6 | 3:50–5:10 | DustLedger | Downwind − upwind = the site's dust; "inconclusive" never means clean. |
| 7 | 5:10–5:50 | Forecasting | Persistence {{n:fc_persist_pm25}} µg/m³; ML +{{n:fc_gbm_best_gain_pct_pm25}}% at most → not our spike. |
| 8 | 5:50–7:00 | Attribution | {{n:at_pair}} → {{n:at_ring}} → **{{n:at_selfcal}}** µg/m³ — **SIMULATED site**, real background + wind. |
| 9 | 7:00–7:50 | Cost & power | Parts ₹{{n:bom_kit}} (parts only); {{n:pw_load}} Wh/day; {{n:pw_margin}}× in December. |
| 10 | 7:50–9:15 | Proof plan & ask | Real-site trial before 1 Nov or a permitted site; else controlled dust trial. Ask: site · co-location · DPCC contact. |
| — | 9:15–10:00 | Reserve | Stop. Take questions. |

**Three numbers to remember:** ₹{{n:bom_kit}} of parts per site · {{n:at_selfcal}} vs {{n:at_refcal}} µg/m³ (self-calibration vs weekly reference visits, simulated) · construction = {{v:F9|2-5%}} of Delhi's ambient PM10.

**Never say:** tamper-proof · "we will cut AQI by …" · "clean sites can keep working" (it's a proposal) · "no one else does this".

**Fast answers** (full list: qa-prep.md)

- *Why you, in the most crowded theme?* Others measure the city; we answer which site added the dust — honestly, with "inconclusive" when we can't tell.
- *Built or simulated?* Data pipeline and forecast benchmark: built, real data. Site + sensors: simulated. Ring + misting: Round 2.
- *Sensors aren't accurate for dust.* Agreed (CSTEP 2025: qualitative). We use differences, then verify with a dust test and reference co-location; inspectors still verify before fines.
- *Calm winds?* Below 1 m/s in {{n:calm_lt10_winter_pct}}% of winter hours (ERA5, a lower bound) → "inconclusive", never clean.
- *Only a few per cent of PM — why bother?* Because that small source gets a blanket ban; targeting dirty sites is fairer. No city-AQI claim.
- *Trial during the ban?* Before 1 Nov or a permitted site; otherwise a controlled dust-source trial on campus.
