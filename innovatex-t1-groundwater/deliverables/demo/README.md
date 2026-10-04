# 60-second offline demo — `jalsakshi-demo.html`

Open `jalsakshi-demo.html` in any browser by double-clicking it. It needs **no internet**: data, scripts and styles are embedded. Press **space** to play or pause, **r** to restart, and **2×** for double speed. A full season plays in about 45 s at 1×.

| Panel | Provenance | What it shows |
|---|---|---|
| Left | **REAL**: India-WRIS public API, fetched 4 Oct 2026 | Delhi's 185 telemetric DWLR piezometers (178 with usable coordinates). Colour = share of readings exactly 0.000 m; ring = reported in 2026 |
| Right | **SIMULATED pit, ARCHIVE rain**: Open-Meteo archive hourly, central Delhi, 1 Jul – 31 Aug 2025 (default model, not pinned; minute pattern synthetic) | One 2.25 m² recharge pit fed by a 250 m² roof. Each storm becomes an event with a verdict from the kept verifier (C5 v1) |

**Scripted in the simulation, and labelled on screen:**
- A **large injected pulse of 1,200 L in one minute** on 20 Aug 15:00 is flagged **implausible** by the jump test. The ticket is issued when that event window closes (22 Aug), not at 20 Aug. A 20 L bucket (≈ 9 mm rise in this pit) is below the 2 cm event threshold and isn't detected.
- Steady clogging is set at 0.012 per m³ of inflow, so the clogging-trend rule raises **Maintenance due** on 27 Aug.

**Ticket rule (C7 v0, a demo heuristic not yet validated across the fleet):** the volume-weighted mean clogging index of the last 3 storms with ≥ 0.5 m³ infiltrated falls below 0.5. Tiny storms give noisy recession fits, so they're excluded. **An inspector can override any verdict; no bill changes automatically.**

**Rebuild:** `innovatex-t1-groundwater/.venv/bin/python innovatex-t1-groundwater/deliverables/demo/build_demo.py`. It needs `.data/delhi_weather_hourly.csv` from `components/data-ingest/fetch_delhi.py`.

**60-second script:**
1. *(0–10 s, left panel)* "Real data: Delhi's own groundwater monitors. 185 telemetric stations, only 46 reported this year, and a quarter of all readings are exactly zero. We QC before we trust."
2. *(10–40 s, press space)* "A simulated pit on Delhi's real 2025 monsoon. Every storm becomes a verdict: green verified, orange clogged. The orange line is the clogging trend."
3. *(at the red band)* "Here, a large pulse the rain can't explain: flagged implausible when the event closes, and sent to random inspection, not a penalty."
4. *(end)* "The drain rate has fallen below half of as-built, so a maintenance ticket goes to the crew. That's the product: inspections where they matter."
