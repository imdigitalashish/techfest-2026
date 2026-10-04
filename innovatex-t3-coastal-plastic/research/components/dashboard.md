# Component research — C12 operations dashboard

_Sources opened 2026-10-04. Code: [`components/dashboard/`](../../components/dashboard/README.md)._

## Users and scene (ASSUMPTION — no interviews yet)
- **BMC ward engineer** (storm-water drains), at a laptop. Wants to know which outfalls are at risk in the next 1–2 days, where the crews are going today, and whether contractor claims hold up.
- **Crew supervisor**, on a phone outdoors in monsoon daylight, possibly on plain-http LAN or patchy data. Wants today's sites and their order, and a fast way to check a record.

## Choices and evidence
- **Static single page plus one JSON bundle.** No server, no build step, works from `python3 -m http.server` or `file://`. The JSON shape is fixed by `contracts.DashboardBundle`.
- **Leaflet with OpenStreetMap tiles.**
  - Leaflet 1.9.4 is BSD-2-Clause (license file vendored from unpkg).
  - The [OSMF tile usage policy](https://operations.osmfoundation.org/policies/tiles/) requires the HTTPS tile URL, visible attribution and a valid Referer. It **forbids bulk prefetch**, so true offline field maps need a self-hosted tile extract (next step).
  - Everything except base tiles works offline.
- **Provenance on every series.** The contract's `Provenance.kind` is shown as a badge: reanalysis, harmonic prediction, simulated, synthetic. Real forcing (ERA5 via Open-Meteo, a tide harmonic fit) is visibly different from the twin's simulated boom state.
- **In-browser verification.**
  - SHA-256 uses WebCrypto in secure contexts, with a pure-JS fallback for plain-http phones on the LAN.
  - Ed25519 uses WebCrypto where the browser supports it; verified 73/73 in headless Chromium (run in `screenshot.py`).
  - Python and JS produce byte-identical canonical JSON; tests run the browser verifier under node.

## Innovation candidates
- **Offline field tiles.** Self-hosted vector tiles for the ward, cached on the phone (UNVERIFIED: needs a tile-source choice compatible with the OSM licence).
- **Crew mode.** A route-ordered checklist for today's plan. Each completed clearance creates a signed record on the device and syncs later; the dashboard then shows the reconciliation flag in the field.
- **Task-time evaluation.** Measure how long a ward engineer takes to answer: which site needs a crew today, and is claim N credible? Compare against the current paper or WhatsApp workflow.
