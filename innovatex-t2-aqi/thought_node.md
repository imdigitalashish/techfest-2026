# InnovateX · Theme 2: Rising AQI in modern cities — Thought Node

> Journal for `innovatex-t2-aqi/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 4–5 — morning package v1 pushed (landscape, components + contracts, ADR 001, pitch, prototype plan, selection memo, forecast walk-forward on real data, C6 attribution replay + first ratchet ledger). Lean mode until 08:30.
- **Plan:** source = **construction & demolition dust, Delhi-NCR**. Product = **DustLedger**: 3–4-node fence-line ring + wind → the site's own PM10 increment → misting only when the site is the cause → tamper-evident ledger → regulator ranking ("let clean sites work"). Spike = attribution with self-calibration (ADR 001).
- **Doing:** lead: multi-seed evaluator for the C6 replay (needed before further ratcheting).
- **Next:** (1) multi-seed C6 evaluator v1, then ratchet the idea backlog in `components/attribution/autoresearch/program.md`; (2) C8 closed-loop misting simulation (µg·h avoided per kL); (3) source BOM prices (vendor pages, with URL and date); (4) independent adversarial review of ADR 001 (`rubber-duck`) once sub-agents are allowed; (5) re-run the dead research threads: dust-suppression evidence, alternative sources, construction's share of Delhi PM (IIT Kanpur 2016), CAQM direction text, BMC Mumbai rules.
- **Needs from user:** (a) decide whether to pitch at the Delhi zonal (10 Oct, South Asian University) and register by 9 Oct; (b) team names/skills: an embedded/hardware teammate helps a lot; (c) by ~25 Oct: a pilot construction site (IIT Delhi campus works?) or permission for a short reference co-location next to a DPCC/CPCB monitor or an IIT Delhi reference instrument; (d) later: hardware purchase (BOM in `deliverables/prototype-plan.md`). Optional: a free OpenAQ API key for live ingestion.
- **Risks:** (1) low-cost optical sensors under-read coarse construction dust (CSTEP calls them qualitative) → differential design + reference co-location; (2) calm winter winds break attribution → abstain + report the rate; (3) health objection: combustion matters more than dust → pitch fairness and economics, not city AQI; (4) no field site by mid-Nov → controlled dust-source trial; (5) BOM prices still UNVERIFIED; (6) the OpenAQ archive for our 4 stations starts Feb 2025, so there's only one winter of history (fetch older CPCB data from another source).

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
- 2026-10-04 — City = Delhi-NCR; pollution source = construction & demolition dust; product = DustLedger (site-level attribution, not city AQI). Evidence: blanket bans in WAP 2026-27 and GRAP, flat fines, 1.38 M registered workers, no vendor attributes a site's own increment ([landscape](research/landscape.md)).
- 2026-10-04 — Spike = C6 attribution + inter-node self-calibration; second spike = C8 closed-loop misting; forecasting stays best-practice ([ADR 001](architecture/adr/001-spike.md)).
- 2026-10-04 — Real data via the OpenAQ public S3 archive (no key) + Open-Meteo (ERA5, CAMS). Everything simulated is labelled `provenance="SIMULATED"`.

## Components
Full map, contracts and metrics: [architecture/components.md](architecture/components.md) · [contracts.py](architecture/contracts/contracts.py).

| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | Fence-line node | air → NodeReading | SPS30-class + ESP32 | | designed (hardware Nov) | inter-unit CV of 1-min PM10 |
| C2 | Wind station | air → WindReading | cup + vane | | designed | direction error (°) |
| C3 | Gateway | readings → batches | ESP32 + LTE, SD buffer | | designed | delivery ratio after outage |
| C4 | Ingest + QA | batches → CleanReading | range/stuck checks | | designed | F1 on injected faults |
| C5 | Calibration | CleanReading → CalibratedReading | linear + RH, weekly re-fit | part of spike (self-cal) | designed | RMSE/R² vs reference (held out) |
| **C6** | **Attribution** | Calibrated + Wind → SiteIncrement | single-pair subtraction | **yes** | **replay v0 + ratchet ledger** (`components/attribution/`) | **increment MAE: ring+self-cal 36.2 vs fixed pair 77.0 µg/m³ (TEST, SIMULATED site)** |
| C7 | Background forecast | public data → BackgroundForecast | persistence; IITM AQEWS | | **running on real data** | MAE skill vs persistence |
| C8 | Suppression controller | SiteIncrement + forecast → ActuationCommand | timer anti-smog gun | 2nd spike | designed | µg·h avoided per kL (sim) |
| C9 | Misting actuator | command → ActuationLog | relay + pump | | designed | latency; litres logged vs metered |
| C10 | Evidence ledger | records → LedgerEntry, report | CCTV + self-audit | | designed | tamper detection rate |
| C11 | Work-window advisor | forecast → advice | none | | designed | dusty hours moved (replay) |
| C12 | Dashboards | all → UI | DPCC portal forms | | designed | time-to-answer (scripted) |

## Selection memo
_v1, 4 Oct 08:00 IST. Final by 7 Oct, 12:00 IST._ **Average 4.0 / 5.**
- **Winnability — 4:** a Delhi panel lives this problem: WAP 2026-27 restricts dusty construction Nov 1–Jan 31 with a total ban Dec 10–Jan 20; GRAP-3 stopped sites for 16 days in 2025; tankers were filmed spraying a reference monitor (Oct 2025). That's strong bonus-points material. Risk: AQI will be the most crowded theme at the Delhi zonal, so we must not look like "another IoT AQI monitor + ML forecast".
- **Innovation headroom — 4:** none of the Indian vendors we checked (Airveda, Prana Air, Oizom pages) attributes a site's *own* increment; they stream absolute PM to the DPCC cloud. Fence-line attribution exists for mines and refineries (Envirosuite, Aeroqual, EPA rings). Our novelty is adapting it to low-cost construction sites, with self-calibration from idle hours, abstention, tamper signatures and closed-loop misting. **First replay** (real Delhi background + ERA5 wind; SIMULATED site and sensors; single seed): ring + self-calibration cuts attribution MAE from **77.0 → 36.2 µg/m³** on held-out 2026 hours vs a fixed upwind/downwind pair, and CSI for > 50 µg/m³ events from 0.33 → 0.72 (`components/attribution/autoresearch/results.tsv`).
- **Feasibility by 1 Dec — 4:** software replay works on real Delhi data on the M5 now (pipeline + harness in `eval/`). Hardware is commodity (ESP32 + SPS30-class + LTE). The dependency is a field site or reference co-location by mid-Nov; nothing user-dependent falls in exam week 19–25 Nov.
- **Demo strength at finals — 5:** a live ring around a dust source on stage; only the downwind nodes light up, and the mister fires automatically. Visceral and hard to fake.
- **Fit with the user's strengths — 3:** data pipeline, attribution modelling, ratchet loops and dashboards fit large-scale systems and ML well. Embedded hardware and field trials don't; we'd want an embedded teammate.
- **Biggest risk:** sensor fidelity for coarse dust plus calm-wind attribution. If the replay shows the ring can't beat simple subtraction in calm conditions, the spike shifts to closed-loop misting + tamper evidence (ADR 001 fallback).
- **Real numbers so far** (`eval/results/forecast_walkforward.json`; monthly expanding window, test Nov 2025–Sep 2026, 4 Delhi CPCB/DPCC monitors, real data): next-day daily-mean **persistence** PM2.5 MAE **23.8 µg/m³** (r 0.91, n = 1,034; Nov–Feb MAE 42.9), PM10 MAE **45.1** (r 0.86). Gradient boosting with ERA5 meteorology adds at most +4 % (PM2.5, perfect-prog met) and +6 % (PM10) MAE skill overall, is *worse* than persistence in winter, and catches fewer severe days (CSI 0.34 vs 0.48). CAMS as served at one city point: PM2.5 MAE 53.6, PM10 177.8 (reference only). Reading: next-day city PM is hard to beat with one year of history; the state already forecasts it. That's why forecasting isn't our spike.
- **One-line pitch:** "Delhi stops every construction site every winter because it can't tell which ones are dusty. DustLedger measures each site's own dust with a low-cost, self-calibrating fence-line ring, mists only when the site is the cause, and gives regulators a tamper-proof ranking so clean sites can keep working."

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 03:55 IST — Phase 0 done; Phase 1 research running; data path found
- Read PLAYBOOK, this brief and `_briefs/innovatex.txt`; wrote *Phase 0 — constraints* (judging → evidence map, assumptions A1–A4).
- Research fan-out: 8 agents launched at 02:10; a truncated launch call plus model-API timeouts (HTTP 408, "timed out reading request body", turn 0) killed 5 of them. Relaunched with a shared brief (`research/raw/_AGENT_BRIEF.md`) and short prompts. Running: companies/products, sensors + calibration + fence-line, hardware BOM, dust-suppression evidence. Partial notes kept from the dead grounding agent: `research/raw/delhi-grounding.md` (unverified until re-checked).
- Data: the OpenAQ v3 API needs a key (HTTP 401), but the public S3 archive works unsigned. Verified: location 235 = "Anand Vihar, New Delhi - DPCC", 15-min PM10 on 2025-11-01. Open-Meteo archive (ERA5, incl. boundary-layer height) and air-quality (CAMS) APIs answer without a key. Scanning OpenAQ IDs 1–15000 for stations in the Delhi bbox (`components/ingest/discover_openaq_delhi.py`).

### 2026-10-04 07:55 IST — Morning package v1 pushed (lean mode, no sub-agents)
- **Network:** the session died on a model 408 at 06:17; resumed 07:11 on the Supervisor's call. All 8 research agents died on 408s; 4 left partial notes (`research/raw/`: companies-products, papers-sensors-calibration, social-signal, delhi-grounding), 4 left stubs (alt-sources, dust-suppression-evidence, hardware-bom; papers-forecasting none). The lead verified the Delhi Winter Action Plan 2026-27 construction ban directly (The News Mill, Sept 2026).
- **Decisions:** source = C&D dust in Delhi; product = DustLedger; spike = wind-resolved ring attribution with self-calibration (ADR 001). Antithesis written by the lead; the independent `rubber-duck` review is pending.
- **Shipped:** `research/landscape.md` (cited; "What companies ship today"; UNVERIFIED list) · `architecture/components.md` (12 components, isolated metrics, mermaid) · `architecture/contracts/contracts.py` + 11 JSON Schemas · `architecture/adr/001-spike.md` · `deliverables/zonal-pitch.md` (10 slides, notes, 15 judge Q&As) · `deliverables/prototype-plan.md` (**BOM prices UNVERIFIED**: vendor sites returned 403/429) · selection memo v1 (avg 4.0).
- **Real numbers:** data = OpenAQ public S3 archive (Anand Vihar 235, R K Puram 17, ITO 5613, Major Dhyan Chand Stadium 6929; ~12.8–13.1k hourly rows each) + ERA5/CAMS via Open-Meteo (26,352 hourly rows, Oct 2023–Oct 2026). **Lesson:** the archive for these stations starts in **Feb 2025**, so the first fixed split (train Oct 2024–Sep 2025) had no winter and its GBM numbers are invalid (kept in `forecast_baseline.json` as a documented failure; its persistence and CAMS rows are unaffected). The walk-forward eval is the valid one: persistence PM2.5 MAE 23.8 / PM10 45.1 µg/m³; GBM ≤ +6 % skill overall and worse in winter; CAMS 2–4× worse. Reproduce: `cd eval && OMP_NUM_THREADS=1 python forecast_walkforward.py` (needs `.data/` from `components/ingest/fetch_openaq_archive.py --ids 235 17 5613 6929 --start 2024-10-01 --end 2026-09-30` and `fetch_openmeteo.py`).
- **Ops note:** sklearn's HistGradientBoosting stalls under load ~110 (OpenMP oversubscription). Always run with `OMP_NUM_THREADS=1`.

### 2026-10-04 08:00 IST — Spike replay v0: first real numbers for attribution
- Built `components/attribution/` (`methods.py` = the editable implementation; `autoresearch/eval.py` = the frozen evaluator; `program.md`; `results.tsv`). Replay = REAL background PM10 (monitor 6929) + REAL ERA5 wind/RH, with a SIMULATED 120 m site (Gaussian plumes, meander, calm pooling, roadside confounder) and SIMULATED sensors (slope, offset, humidity growth, drift, noise).
- Held-out 2026 MAE (abstentions scored as 0): fixed pair 77.0 → ring 62.1 → **ring + idle-hour self-calibration 36.2 µg/m³**; CSI > 50: 0.33 → 0.55 → 0.72; coverage 0.95. Single seed, so multi-seed is next before any further keep/revert decisions. Reproduce: `cd components/attribution/autoresearch && python eval.py all`.
- Pitch and ADR updated with this result, labelled SIMULATED site/sensors.
