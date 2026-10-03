# EV Challenge 2 · Green Auto India (automotive LCA database) — Thought Node

> Journal for `ev-c2-green-auto-lca/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

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

**Challenge 2 — Green Auto India:** "Creation of an India-Specific Life Cycle Assessment Database for the Automotive Sector."
- **Objective:** an India-specific automotive LCA database and assessment framework that represents key materials, components, processes, energy sources, logistics and end-of-life pathways relevant to India; estimates the environmental footprint of automotive products and technologies; supports comparisons across vehicle technologies, materials, components or manufacturing choices; provides a transparent, scalable foundation; supports MHI, ICAT, manufacturers, suppliers, researchers and policymakers.
- **Data layers to consider:** materials (steel, aluminium, copper, plastics, composites, recycled) · components (body, chassis, powertrain, battery, tyres, electronics) · manufacturing processes (casting, forging, machining, moulding, stamping, welding, painting, assembly) · energy (electricity, renewables, natural gas, hydrogen, other fuels) · transport & logistics (road, rail, coastal shipping) · use phase (energy or fuel use, maintenance) · end-of-life (reuse, recycling, recovery, disposal) · indicators (GHG and other impact categories). A defined scope is fine; state sources, boundaries, assumptions, limitations and data quality.
- **Expected deliverables (finale):** prototype India-specific automotive LCA database with a clearly defined scope · database architecture & data-collection framework showing how new datasets plug in · environmental-impact calculation engine · web dashboard with lifecycle results and comparisons · methodology document (boundaries, assumptions, sources, calculations, limitations) · demo case study on at least one product, component, material or technology · scalability roadmap.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Standards and engines: ISO 14040/14044; openLCA and Brightway (open-source); ecoinvent (licensed), Argonne GREET (free), USLCI, EU Environmental Footprint data.
- India-specific inputs: the CEA CO2 Baseline Database (grid emission factors), state grid mixes, Indian steel and aluminium production routes, battery manufacturing (Argonne BatPaC), Indian driving cycles, recycling and informal-sector end-of-life.
- Method: data-quality pedigree scoring and Monte Carlo uncertainty; India's fleet is 2W/3W-heavy, so compare ICE, CNG, hybrid and BEV across segments.
- What companies ship: LCA software vendors and automakers' published product-carbon-footprint methods.

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
