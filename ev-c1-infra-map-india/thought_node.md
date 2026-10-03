# EV Challenge 1 · EV Infra Map India — Thought Node

> Journal for `ev-c1-infra-map-india/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 0 — Brief (not started)
- **Plan:** _(lead fills)_
- **Doing:** _(what, and which agents/sessions)_
- **Next:** _(ordered)_
- **Needs from user:** Register by 15 Oct and pick one track (after the 12 Oct selection). Team of 2–5: names and skills.
- **Risks:** _(lead fills)_

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
