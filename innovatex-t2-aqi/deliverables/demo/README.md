# Offline demo — `dustledger-demo.html`

Open `dustledger-demo.html` in any browser (double-click). It needs **no internet**: data, script and styles are embedded. Click a site row to see its week; press **Show / hide simulation truth** to see where the ring is wrong.

| Panel | Provenance | What it shows |
|---|---|---|
| Left, top | **REAL**: hourly PM10 at 4 CPCB/DPCC monitors (OpenAQ public archive), daily means Oct 2025 – Feb 2026 | Delhi's winter background. A sensor at a site's fence mostly measures this |
| Left, bottom | **REAL**: hourly PM10 at Major Dhyan Chand National Stadium (DPCC) + ERA5 wind speed, 17–23 Nov 2025 | The demo week. Below 0.5 m/s the ring says "inconclusive" |
| Right | **SIMULATED sites on REAL background + wind**: six construction sites with different emission levels, the same physics and sensor-fault model as evaluator v2.1 ('medium'), attribution by `methods.ring_selfcal` | Regulator ranking by each site's own dust, hours above 50 µg/m³, share of inconclusive hours, misting-on hours vs a timer schedule; per-site hourly chart |

**Demo rule, not validated:** misting turns on in an hour when the site estimate is > 50 µg/m³, the wind isn't calm and ERA5 shows no rain. The effect of misting on dust is **not modelled**, so the demo counts misting hours only, never dust or water saved.

**What the truth toggle reveals (honestly):** estimates are lower than the simulation truth, mostly because calm hours (where the truth includes pooled dust) are abstained; the two cleanest sites swap ranks because both sit near the ring's noise floor. The ranking check in `ranking_check.json` (20 simulated sites on the held-out Jan–Sep 2026) is easy by construction — emission levels differ up to 30-fold.

**Rebuild:** `OMP_NUM_THREADS=1 nice -n 10 python3 deliverables/demo/build_demo.py` (from `innovatex-t2-aqi/`; needs `.data/` from `components/ingest/`). Screenshot `demo.png` is for backup slide B7.

**60-second script:**
1. *(0–10 s, left)* "Real data: Delhi's monitors this winter. A fence-line sensor mostly sees this background."
2. *(10–35 s, right)* "Six simulated sites on a real Delhi week. The ring ranks them by their own dust; the inspector starts at the top. Nearly a quarter of this calm week is 'inconclusive' — we don't guess."
3. *(35–50 s, click Show truth)* "Here's where we're wrong: we under-read calm hours, and the two cleanest sites swap places. That's why DPCC verifies before any penalty."
4. *(50–60 s)* "Misting runs only when the estimate says the site is adding dust — here fewer hours than a timer for most sites. Whether that cuts dust is what our November trial measures."
