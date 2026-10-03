# InnovateX · Theme 2: Rising AQI in modern cities — Thought Node

> Journal for `innovatex-t2-aqi/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 1 — SOTA research (running) + data path for the walking skeleton (in progress). Phase 0 done (see *Phase 0 — constraints* below).
- **Plan:** research fan-out → choose the pollution source + spike (ADR 001) → components + contracts → walking skeleton on real CPCB data (OpenAQ public S3 archive) + Open-Meteo meteorology → forecasting/attribution eval with real numbers → zonal pitch + prototype plan → selection memo. All by 08:30 IST.
- **Doing:** 4 research agents (companies/products, sensors + calibration + fence-line methods, hardware BOM with Indian prices, dust-suppression evidence). Lead: Delhi station discovery in the OpenAQ archive, then data pipeline.
- **Next:** (1) ingest Delhi CPCB hourly PM + meteorology; (2) baseline forecasts (persistence, climatology, gradient boosting) on a time-ordered split; (3) components.md + contracts; (4) ADR 001; (5) deliverables.
- **Needs from user:** Decide whether to pitch at the Delhi zonal (10 Oct, South Asian University) and register by 9 Oct. Hardware purchases for the prototype come later. Optional: a free OpenAQ API key (explore.openaq.org) would simplify live ingestion; not blocking (we use the public S3 archive).
- **Risks:** (1) Network uplink saturated by ~20 parallel sessions: 5 of 8 research agents died with HTTP 408 at turn 0; mitigation: ≤4 concurrent agents, short prompts, shared brief file, lead does targeted searches itself. (2) Forecasting PM in Delhi winter is a crowded space (IITM's operational systems) — the spike must sit where incumbents don't. (3) Low-cost optical sensors under-read coarse dust (to verify) — matters if the source is construction dust.

## Phase 0 — constraints (from `_briefs/innovatex.txt`, read 4 Oct 02:10 IST)
- **Round 1 (Delhi zonal, 10 Oct, 10 min, in person, no online submission):** team info · precise problem within the theme · background and why existing solutions fall short · proposed solution and technology · impact and scalability. Top 5 per zonal advance; results the same day.
- **Round 2:** report + **working prototype** on the website by **1 Dec** (only the team leader submits; one submission): solution description · prototype evidence of functionality and usability · cost and market viability · implementation plan · scalability plan across India · impact assessment. Finals 15–18 Dec at IIT Bombay.
- **Rules:** team ≤ 4 students, cross-institute allowed; one theme per team; solution must be original and "not protected by patents, copyrights, or publications" → don't publish the core idea before the finals; attribute all borrowed methods.
- **What we must be able to show (judging → evidence):**

| Criterion | Evidence we need |
|---|---|
| Creativity & novelty | A spike that existing networks/products don't do, shown against a named incumbent |
| Functionality & usability (incl. "high-dust atmospheres") | A working pipeline + dashboard on real data now; hardware node + actuator by 1 Dec with a field/bench test in dust |
| Cost & market value | BOM with sourced Indian prices; a payer (who pays and why: regulation, fines, savings) |
| Technical feasibility (power, calibration, maintenance, weather) | Power budget from datasheets; a calibration method with held-out numbers; maintenance plan; monsoon/fog/heat handling |
| Regional scalability | Same design under other Indian cities' rules and climates; per-site cost; no city-specific retraining needed (or a cheap path) |
| Environmental & socioeconomic impact | Quantified PM reduction / exposure avoided / water saved / jobs protected, each with cited factors and stated uncertainty |
| Design & ergonomics | Operator-first UI (site supervisor, regulator, resident); installable by one technician |
| Bonus: local depth | Delhi-specific pain points with numbers: GRAP, CAQM/DPCC rules, source apportionment, seasons |

- **Assumptions (decided, overnight mode):** A1 city = Delhi-NCR (we pitch at the Delhi zonal; bonus is for local depth). A2 pollution source chosen in ADR 001 after research; working hypothesis = construction & demolition dust. A3 real data = CPCB/DPCC monitors via the OpenAQ public S3 archive (no key) + Open-Meteo (ERA5 meteorology, CAMS forecasts). A4 anything simulated is labelled SIMULATED in code, data and slides.

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** InnovateX: The Future Habitats Challenge — Techfest IIT Bombay. Prize pool ₹80,000; top 3 teams per theme.
- **Official statement:** [`_briefs/innovatex.pdf`](../_briefs/innovatex.pdf) (text: [`_briefs/innovatex.txt`](../_briefs/innovatex.txt)).
- **Round 1 — in-person pitch at a city zonal (no online submission):** 10 minutes covering team info, the precise problem within the theme, background and why existing solutions fall short, the proposed solution and technology, impact and scalability. Top 5 teams per zonal advance. **Delhi zonal: 10 Oct at South Asian University** (registration open until the zonal date). Other zonals listed on techfest.org: Chennai 10 Oct, Gandhinagar 11 Oct, Hyderabad 11 Oct, Patna 18 Oct, Jaipur TBD.
- **Round 2:** detailed final report + **working prototype** submitted on the website by **1 Dec** (solution description, prototype evidence, cost & market viability, implementation plan, scalability plan, impact assessment); finals **15–18 Dec** at IIT Bombay. (The web page lists a 15 Nov shortlist announcement while the PDF says Round 1 results come on the zonal day — treat as unconfirmed.)
- **Judging:** creativity & novelty · functionality & usability (robust under real conditions) · cost & market value · technical implementation & feasibility (power, calibration, maintenance, weather) · regional scalability · environmental & socioeconomic impact · design & ergonomics · **bonus** for a deep, locally grounded understanding of the theme.
- **Rules:** students, team ≤4 (cross-institute encouraged); **one theme per team**; original work.
- **Gate — selection memo by 7 Oct, 12:00 IST:** the team pitches ONE theme at the Delhi zonal; the Supervisor picks from the three memos. The chosen lead then delivers the full pitch deck + speaker notes + Q&A prep by 9 Oct.
- **Round-1 deliverable for the morning package:** `deliverables/zonal-pitch.md` (10-min deck outline + speaker notes + likely judge questions) + `deliverables/prototype-plan.md` (architecture, bill of materials with costs, build steps, and what can be simulated now).

**Theme 2 — Rising AQI Levels in Modern Urban Cities.** Challenge question (verbatim): "How can technologies be leveraged to monitor, predict, and reduce rising AQI levels in modern urban environments? Propose an innovative solution using IoT sensors, AI-driven air quality forecasting, adaptive traffic control, drone-based monitoring, or urban planning strategies. Your solution should address a specific pollution source and outline its benefits, feasibility, and implementation strategy"
- **Objectives:** a primary contributor (vehicular emissions, industrial zones, construction dust, waste burning, etc.) · a feasible, sustainable, scalable smart-technology solution · practical feasibility · implementation plan (sensor placement, data collection, analytics, integration with city systems) · challenges (sensor calibration, weather, maintenance, reliability) · economic viability · quantified environmental and public-health impact.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Data: CPCB CAAQMS real-time monitors; Delhi's Graded Response Action Plan (GRAP); NASA FIRMS fire detections (crop-residue burning).
- Hardware: low-cost PM sensors (e.g. Plantower PMS5003, Sensirion SPS30) with ML calibration against reference monitors.
- Analytics: ML + meteorology forecasting, source attribution, construction-dust monitoring with automated suppression, adaptive traffic signals.
- What companies ship: urban air-quality networks and forecasting products — check recent launches and city deployments.

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

### 2026-10-04 03:55 IST — Phase 0 done; Phase 1 research running; data path found
- Read PLAYBOOK, this brief and `_briefs/innovatex.txt`; wrote *Phase 0 — constraints* (judging → evidence map, assumptions A1–A4).
- Research fan-out: 8 agents launched at 02:10; a truncated launch call plus model-API timeouts (HTTP 408, "timed out reading request body", turn 0) killed 5 of them. Relaunched with a shared brief (`research/raw/_AGENT_BRIEF.md`) and short prompts. Running: companies/products, sensors + calibration + fence-line, hardware BOM, dust-suppression evidence. Partial notes kept from the dead grounding agent: `research/raw/delhi-grounding.md` (unverified until re-checked).
- Data: the OpenAQ v3 API needs a key (HTTP 401), but the public S3 archive works unsigned. Verified: location 235 = "Anand Vihar, New Delhi - DPCC", 15-min PM10 on 2025-11-01. Open-Meteo archive (ERA5, incl. boundary-layer height) and air-quality (CAMS) APIs answer without a key. Scanning OpenAQ IDs 1–15000 for stations in the Delhi bbox (`components/ingest/discover_openaq_delhi.py`).
