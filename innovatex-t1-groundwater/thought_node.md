# InnovateX · Theme 1: IoT underground water management — Thought Node

> Journal for `innovatex-t1-groundwater/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 1 — SOTA research (fan-out running) · Phase 2 contracts started in parallel. Phase 0 done (see *Phase 0 — what we must show*).
- **Plan:** research fan-out → component map + typed contracts → per-component innovation scan + six hats + adversarial review + first principles → ADR 001 spike → walking skeleton (real India-WRIS/CGWB Delhi data + labelled simulated sensors) + eval harness → first auto-research loop → zonal pitch + prototype plan → selection memo v1. Morning package 08:30 IST.
- **Doing (agents):** r1a Delhi hydrogeology · r1b1 CGWA rules & market · r1b2 Delhi rules/RWH/NGT/tariffs · r2 companies & deployments · r3 hardware/power/connectivity/prices · r4 analytics SOTA · r5 real-data access (India-WRIS, weather, USGS high-frequency, iAWE) · r6 social signal & competitions · FP first-principles detectability physics. Lead: contracts + skeleton.
- **Next:** landscape.md synthesis → components.md → builders (sim, hydro-twin, detector, dashboard) → ADR 001 → deliverables.
- **Needs from user:** Decide whether to pitch at the Delhi zonal (10 Oct, South Asian University) and register by 9 Oct. Hardware purchases for the prototype come later (BOM in `deliverables/prototype-plan.md`).
- **Risks:** (1) research agents slow / transient model failures (two relaunched) → incremental writing, smaller scopes; (2) real high-frequency Delhi data may not be public → USGS high-frequency wells for real-signal validation + clearly labelled simulation; (3) physics may limit hidden-pump detection to large pumps/confined aquifers → FP agent quantifying before we commit the spike.

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** InnovateX: The Future Habitats Challenge — Techfest IIT Bombay. Prize pool ₹80,000; top 3 teams per theme.
- **Official statement:** [`_briefs/innovatex.pdf`](../_briefs/innovatex.pdf) (text: [`_briefs/innovatex.txt`](../_briefs/innovatex.txt)).
- **Round 1 — in-person pitch at a city zonal (no online submission):** 10 minutes covering team info, the precise problem within the theme, background and why existing solutions fall short, the proposed solution and technology, impact and scalability. Top 5 teams per zonal advance. **Delhi zonal: 10 Oct at South Asian University** (registration open until the zonal date). Other zonals listed on techfest.org: Chennai 10 Oct, Gandhinagar 11 Oct, Hyderabad 11 Oct, Patna 18 Oct, Jaipur TBD.
- **Round 2:** detailed final report + **working prototype** submitted on the website by **1 Dec** (solution description, prototype evidence, cost & market viability, implementation plan, scalability plan, impact assessment); finals **15–18 Dec** at IIT Bombay. (The web page lists a 15 Nov shortlist announcement while the PDF says Round 1 results come on the zonal day — treat as unconfirmed.)
- **Judging:** creativity & novelty · functionality & usability (robust under real conditions) · cost & market value · technical implementation & feasibility (power, calibration, maintenance, weather) · regional scalability · environmental & socioeconomic impact · design & ergonomics · **bonus** for a deep, locally grounded understanding of the theme.
- **Rules:** students, team ≤4 (cross-institute encouraged); **one theme per team**; original work.
- **Gate — selection memo by 7 Oct, 12:00 IST:** the team pitches ONE theme at the Delhi zonal; the Supervisor picks from the three memos. The chosen lead then delivers the full pitch deck + speaker notes + Q&A prep by 9 Oct.
- **Round-1 deliverable for the morning package:** `deliverables/zonal-pitch.md` (10-min deck outline + speaker notes + likely judge questions) + `deliverables/prototype-plan.md` (architecture, bill of materials with costs, build steps, and what can be simulated now).

**Theme 1 — Underground Water Management.** Challenge question (verbatim): "How can IoT technologies be designed and deployed to effectively monitor, protect, and manage underground water resources in an urban city? Propose an innovative IoT-based solution that addresses a specific groundwater-related challenge such as water level monitoring, contamination detection, illegal extraction prevention, pipeline leakage detection, or aquifer recharge analysis. Your solution should detail the problem, proposed technology, impact, and feasibility within a framework."
- **Objectives:** a specific groundwater problem (levels, quality, usage or distribution) · a comprehensive IoT solution (sensors, communications, analytics) · technical feasibility (sensor operation, data collection, network requirements, real-time monitoring) · operational challenges (underground connectivity, sensor durability, power, maintenance, data reliability) · economic analysis and a sustainable model for city-scale adoption · environmental and social impact.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Data: CGWB groundwater-level monitoring and India-WRIS; CGWA's extraction-permit (NOC) regime; Atal Bhujal Yojana; CGWB assessments for Delhi.
- Hardware: piezometers / pressure transducers, EC/TDS/nitrate/fluoride sensing, LoRaWAN or NB-IoT for underground links, low-power design.
- Analytics: leak detection from acoustic or pressure transients, anomaly detection for illegal extraction, aquifer models (MODFLOW via FloPy).
- What companies ship: smart-water and groundwater-monitoring startups and utility deployments — check recent launches.

## Phase 0 — what we must show (from the official statement, `_briefs/innovatex.txt`)
**Hard constraints.** Team ≤4, students, one theme per team, original work (not patented/published). Round 1 = 10-min in-person pitch at the zonal, nothing submitted online; must cover team info (name, Team ID, theme no., contacts), precise problem, background + why existing solutions fall short, proposed solution + technology + how it works, impact & scalability. Top 5 per zonal advance. Round 2: report + working prototype by 1 Dec (solution description, prototype evidence, cost & market viability, implementation plan, scalability plan, impact assessment); finals 15–18 Dec at IIT Bombay. Only the team leader submits online. Queries only via the portal's Doubt section.

| Judging criterion (official) | What we must be able to show |
|---|---|
| Creativity & novelty | One idea a judge hasn't seen: a spike component that beats what ships today, with a number |
| Functionality & usability (incl. subterranean connectivity) | A working twin + dashboard on real Delhi data; link budget and store-and-forward from a borewell; failure handling |
| Cost & market value | Sourced BOM (₹/node), cost vs incumbent loggers/flow meters, who pays (CGWA NOC compliance, DJB, RWAs) |
| Technical feasibility (power, calibration, maintenance, weather) | Power budget → battery years; calibration routine; drift/QC; Delhi heat (45 °C+) & monsoon; maintenance schedule |
| Regional scalability | Works on any India-WRIS station; parameters per aquifer type (alluvium vs hard rock); regulatory hooks that exist nationwide (CGWA) |
| Environmental & socioeconomic impact | Quantified: m³ of extraction made visible/avoided, recharge verified, ₹ value at Delhi tariffs/tanker prices |
| Design & ergonomics | Operator-first dashboard (inspection queue), citizen view, installable node in a 4–6" casing |
| Bonus: problem-centric (local) | Delhi-specific numbers: CGWB assessment, over-exploited units, telemetric stations, NGT orders, tanker mafia, RWH mandate |

## Key decisions
- _(none yet)_

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|

## Selection memo
_First version due in the morning package (08:30 IST, 4 Oct); final by 7 Oct, 12:00 IST (one theme is pitched at the Delhi zonal on 10 Oct). Score each 1–5 with one line of evidence._
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

### 2026-10-04 03:25 IST — Phase 0 done; Phase 1 fan-out running
- Read PLAYBOOK, seeded brief and `_briefs/innovatex.txt`; wrote *Phase 0 — what we must show* (criteria → evidence).
- Launched research workers r1a, r1b, r2, r3, r4, r5 (data), r6, and a First-Principles physics agent. r6 and r1b failed with transient model errors (408, request too large); relaunched r6 and split r1b into r1b1 (CGWA) + r1b2 (Delhi rules/tariffs) with small-fetch, write-incrementally instructions.
- Early finding (r5, live query): India-WRIS ArcGIS REST `arc.indiawris.gov.in/server/rest/services/NWIC/GroundwaterLevel_Stations/MapServer/0` returns 382 stations with `state_name='Delhi'`, from CGWB and "Delhi SW GW", some flagged telemetric (DWLR). Notes: `components/data-ingest/research_sources.md`.
- Assumptions (no user available): ground the pitch in Delhi (zonal venue); target the user's team as ≤4 students; prototype budget unconstrained but BOM must be credible for a student build.
