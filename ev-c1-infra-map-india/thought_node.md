# EV Challenge 1 · EV Infra Map India — Thought Node

> Journal for `ev-c1-infra-map-india/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 1–4 in parallel, LEAN MODE (Supervisor 05:49: no sub-agents, small requests, push every 30 min).
- **Plan:** real-data walking skeleton (VAHAN + OSM chargers + boundaries) for the national view and one demo state, **Maharashtra**; landscape → components + contracts → ADR 001 → selection memo → Round-1 drafts.
- **Doing (lead, sequential):** VAHAN plain-HTTP client works (no browser): JSF partial-AJAX + Excel export, validated on the CY2025 State × Fuel table. Next: national pulls, OSM charger pull, docs.
- **Next:** (1) push skeleton code; (2) research/landscape.md; (3) architecture/components.md + contracts; (4) ADR 001; (5) selection memo; (6) deliverables/round1-*.md; (7) gap analysis numbers + map.
- **Needs from user:** Register by 15 Oct and pick one track (after the 12 Oct selection). Team of 2–5: names and skills. An Open Charge Map API key (free signup) would add a third charger source; meanwhile OSM is the open source.
- **Risks:** (1) VAHAN registrations ≠ on-road stock (no deregistration feed); (2) open charger data is incomplete vs official counts → we measure and publish completeness per state; (3) RTO → district crosswalk is manual; (4) tonight's network saturation (most sub-agents died on model 408s).

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** EV Infra & Green Mobility AI Challenge — Techfest IIT Bombay with the Ministry of Heavy Industries (MHI) and the International Centre for Automotive Technology (ICAT). Prize pool ₹2,00,000; top 3 teams per track.
- **Official statement:** [`_briefs/ev-infra.pdf`](../_briefs/ev-infra.pdf) (text: [`_briefs/ev-infra.txt`](../_briefs/ev-infra.txt)).
- **Rounds:** register by **15 Oct** (the track is fixed at registration) → Round 1 concept & roadmap due **30 Oct**: team info + methodology document (problem understanding, analytical approach) + implementation roadmap (data sources, tools, development stages, path to the final prototype) → results **7 Nov** → Grand Finale **16–18 Dec** at IIT Bombay: live demo of the working prototype covering the expected deliverables, plus how it evolved from the roadmap, then jury Q&A.
- **Round 1 judging:** problem understanding & relevance 25% · feasibility & technical soundness 25% · innovation 20% · clarity & completeness of the roadmap 20% · data strategy (sources & integration) 10%.
- **Round 2 judging:** technical & analytical robustness 25% · data quality & integration 20% · relevance & practical usability 20% · innovation 15% · scalability & replicability 10% · presentation 10%.
- **Rules:** team of 2–5 UG/PG students; one track per team; one team per person; open-source tools, models and public data allowed with attribution; synthetic data must be identified and documented; disclose AI tools, third-party software, external datasets and frameworks. The statement says solutions are judged "on the intelligence, transparency, and defensibility of the approach rather than access to premium or proprietary datasets."
- **Round-1 deliverable for the morning package:** `deliverables/round1-methodology.md` + `deliverables/round1-roadmap.md`.

**Challenge 1 — EV Infra Map India:** "Mapping and Integration of Nationwide EV Charger Installations Based on Vehicle Population Using VAHAN Data."
- **Objective:** a data-driven national platform that integrates and maps existing public EV charging infrastructure across India; uses VAHAN registration data to relate EV population to charging availability; identifies underserved areas and charging gaps; estimates future charging requirements by region; supports evidence-based planning by MHI, ICAT, state governments and others.
- **Data layers to consider:** EV population & registrations (VAHAN, state transport data) · existing chargers (public charging apps, charger networks, open databases) · geographic & administrative boundaries · road & mobility network (national highways, major roads, corridors) · demographics & economic activity · electricity infrastructure (public grid/utility info) · context (tourism, logistics, land use, urban development). Public, open, sample or realistic synthetic data allowed — document every source and assumption.
- **Expected deliverables (finale):** functional platform with a unified view of charging infrastructure · interactive national GIS map (chargers, coverage, gaps) · analytical methodology document · charger-requirement estimation & recommendation module for selected states, districts, cities or corridors · decision-support dashboard · demo video for at least one representative geography · scalability roadmap.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Data: the VAHAN dashboard (registrations by state, RTO and fuel); BEE's public-charging data and the EV Yatra app; Open Charge Map; OpenStreetMap `amenity=charging_station`; charge-point operators' public locators; PM E-DRIVE charger allocations; Ministry of Power charging-infrastructure guidelines (spacing norms as a policy benchmark); boundaries from LGD / DataMeet / Census.
- Methods: cross-source entity resolution to deduplicate chargers; isochrones (OSRM, Valhalla); two-step floating catchment (2SFCA) accessibility; demand modelling from registrations, traffic and points of interest; location-allocation (MCLP, p-median).
- What companies ship: charger-locator apps and siting-analytics products from charge-point operators, utilities and mapping companies.

## Key decisions
- _(none yet)_

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|

## Selection memo
_First version due in the morning package (08:30 IST, 4 Oct); final by 12 Oct (the team registers for one EV track by 15 Oct). Score each 1–5 with one line of evidence._
- **Winnability:**
- **Innovation headroom** (the spike, and why it beats the obvious baseline):
- **Feasibility by the deadline** on an M5 Mac (+ Azure), around the 19–25 Nov exams:
- **Demo strength** at the finals:
- **Fit with the user's strengths** (large-scale systems, frontier models):
- **Biggest risk:**
- **One-line pitch:**

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 05:55 IST — Phase 0–1 under network saturation
- Phase 0 done: brief, judging weights and deliverables read from `_briefs/ev-infra.txt`.
- Launched 9 research sub-agents (methods, India data/policy, companies, social, OSS/data, India EV parameters, benchmarks, policy norms); 7 died on model-side "408 Timed out reading request body" (portfolio-wide network saturation). Two original agents are still running; told them to wrap up.
- **VAHAN spike succeeded.** The public dashboard (`vahan4dashboard/.../reportview.xhtml`) lists "All Vahan4 Running States (36/36)" and "All Vahan4 Running Office (1468/1469)". Plain HTTP replay of the JSF/PrimeFaces AJAX (state → RTO cascade, axis selection, Refresh `j_idt65`, export `groupingTable:xls`) returns full pivot tables as .xlsx. Validated: CY2025 State × Fuel, 36 rows; Andaman row sums to its TOTAL (9,658). EV fuel labels: `ELECTRIC(BOV)`, `PURE EV` (+ `PLUG-IN HYBRID EV`, `STRONG HYBRID EV`). Code: `components/vahan_ingest/vahan_client.py`.
- Open Charge Map API returns 403 without a key → use OSM `amenity=charging_station` (Overpass) as the open charger source tonight.
- Decision (assumption, reversible): demo geography = **Maharashtra** (largest e-4W market, Mumbai–Pune–Nashik corridors, state EV Policy 2025); pipeline stays state-agnostic.
- Switched to LEAN MODE per Supervisor.

