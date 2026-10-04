# C12: Municipal operations dashboard (static, offline-capable)

An **actionable overview**, not a data dump. The page opens on what to do today:
- a morning brief, written by a rule-based template (no language model) from the forecast, the tide-aware plan and the claims ledger
- a ranked action list: crews to dispatch, each with a copy-ready crew message; sites to watch; claims to check before payment
- a "Why?" on every action, showing its inputs, the planner's note, what the simpler rules would do instead, and the simulation evidence

Below the action list are:
- the map and site list
- one site's rain, tide, boom fill and escape charts with a hover read-out
- the claims that need attention, with in-browser hash-chain and Ed25519 verification and a tamper demo
- the plan comparison and camera check
- a sources panel that separates **real**, **SIMULATED** and **SYNTHETIC** data

The page is a seven-day **replay** of the wettest 2025 monsoon week, with day-by-day forecasts and plans (use ‹ › or the `[` `]` keys). All times are IST. Marathi and Hindi headings and crew messages are draft translations, **UNVERIFIED** until a native speaker reviews them. Product and design notes are in [PRODUCT.md](PRODUCT.md) and [DESIGN.md](DESIGN.md).

![Desktop view](screenshot-desktop.jpg)

| Phone | Tamper demo (one claim edited in the browser) |
|---|---|
| ![Phone](screenshot-phone.jpg) | ![Tamper detected](screenshot-tamper.jpg) |

## Run
```bash
python3 innovatex-t3-coastal-plastic/components/dashboard/build_bundle.py      # merge inputs -> site/
cd innovatex-t3-coastal-plastic/components/dashboard/site && python3 -m http.server 8000
# open http://localhost:8000  (phone on the same Wi-Fi: http://<laptop-ip>:8000)
python3 innovatex-t3-coastal-plastic/components/dashboard/screenshot.py        # headless render, fails on JS errors
cd innovatex-t3-coastal-plastic/components && python3 -m pytest dashboard/tests -q   # 6 tests
```

## Data flow
`build_bundle.py` merges three inputs:
- `components/twin_sim/results/bundle_part.json` (sites, forcing, interceptor, forecasts, plans, telemetry, metrics)
- `components/detection/results/metrics.json` plus sample detections, when they exist
- a ledger built by C11 on the twin's clearance events

It validates the result with `contracts.DashboardBundle` and writes:
- `site/dashboard_bundle.json`: the contract. When the twin publishes `metrics['twin_sim.window']` it holds the whole replay window, about 0.8 MB for 7 days × 4 sites: hourly series and telemetry, 24 h and 48 h forecasts and P0/P1/P2 plans for every day. Otherwise it holds the latest 6 days.
- The ledger covers the 30 days up to the end of the window. The page counts a claim only once it has ended by the replay day.
- `site/aux.json` — anchor, Ed25519 signatures, key registry, synthetic ground truth, detection samples
- `site/data.js` — the same data, so the page also opens from `file://`

If the twin output is absent, `--mock` or the fallback uses `mock_inputs.py`. That mock is **SYNTHETIC** everywhere: site names end in "(mock)", positions are approximate, and a banner says so.

The current build uses the twin's real forcing:
- Rain is **ERA5 reanalysis via Open-Meteo**.
- Tide is a **harmonic prediction** (UTide fit to Open-Meteo marine sea level).
- Each provenance comes from the twin's own `Provenance` fields, shown as badges next to the chart.

Boom fill, escape and telemetry are `simulated` and drawn on a hatched background. The evidence records are **SYNTHETIC claims**: honest, plus about 20 % injected inflation or phantom trips laid on the twin's simulated clearances. Expand a row to see its injected label.

## Design decisions (assumptions; no operator interview yet)
- **Operate mode, light theme** for daylight phone use. One water-blue accent; risk colours appear only where something needs attention. SIMULATED rows are hatched and tagged in text. Tokens are in [DESIGN.md](DESIGN.md).
- **Actions first.** Sites with a planned crew carry their risk on the dispatch row. A "Watch" row appears only for uncovered sites at 5% or more overflow or bypass risk in 24 h or 48 h. That threshold is a display choice, not a calibrated alarm level, and it is stated under "Why?".
- **Done state.** "Mark sent" and "Acknowledge" are stored in `localStorage` per bundle, so a refresh keeps them.
- **No page-level horizontal scroll.** Grid tracks are `minmax(0, …)`, and hashes, commands and URLs wrap. The full 66-record table is opt-in and scrolls inside its own box.
- **Verification** runs locally. SHA-256 uses WebCrypto, with a pure-JS fallback for plain-http LAN phones, which are not a secure context. Ed25519 uses WebCrypto, and signatures must come from the record's crew (or a delegation). "Tamper demo" raises one claim by 25% in memory; the chain check pinpoints that record, and the claim list shows the signed value next to the edited one.
- **Map.** Leaflet 1.9.4 is vendored (BSD-2-Clause, `site/vendor/leaflet/LICENSE`), so everything except the base tiles works offline.
  - OSM tiles follow the [OSMF tile usage policy](https://operations.osmfoundation.org/policies/tiles/) (opened 2026-10-04): HTTPS URL, visible attribution, Referer sent, **no bulk prefetch**.
  - Field use needs a self-hosted tile extract (UNVERIFIED next step).

## Not yet in
- No usability metric yet (task time to the first correct dispatch); planned with real ward staff.
- No live data: the replay uses archived forecasts and the twin's simulated sensors.
