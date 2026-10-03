# InnovateX · Theme 3: Coastal plastic pollution (Mumbai) — Thought Node

> Journal for `innovatex-t3-coastal-plastic/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 1–4 in parallel (research fan-out + walking skeleton), since 02:10 IST 4 Oct.
- **Plan (working hypothesis, ADR 001 pending):** target source = single-use flexible plastics (carry bags, sachets/MLP, thermocol, bottles) from dense settlements and markets that enter nullahs and leak at tidal outfalls into Mahim / Malad / Mahul creeks. System = a *measured, tide-aware interception network*: (1) flood-safe, tide-aware boom/trap at nullah outfalls; (2) solar camera node counting plastic flux + boom fill; (3) forecast- and tide-aware clearance dispatch; (4) tamper-evident MRV ledger → pay contractors per verified kg, route catch to recycling/co-processing (EPR); (5) ward hotspot feedback for source reduction. Spike candidates: vision flux sensing (C5/C6), forecast+tide-aware dispatch (C9/C10), MRV anti-fraud reconciliation (C11).
- **Doing:** child sessions — *T3 detection + flux* (C5/C6 + autoresearch), *T3 digital twin + dispatch* (C1–C4, C9–C10 + autoresearch), *T3 dashboard + MRV ledger* (C11, C12), *T3 research: Mumbai + policy*, *T3 research: tech + companies*. Lead: contracts, components.md, ADR 001, selection memo, deliverables.
- **Next:** push contracts → components.md → per-component research → ADR 001 (six hats + adversarial) → zonal-pitch.md + prototype-plan.md → integrate child results → push by 08:30.
- **Needs from user:** decide whether to pitch at the Delhi zonal (10 Oct, South Asian University) and register by 9 Oct. Nothing blocks tonight's work.
- **Risks:** (1) model-API congestion (HTTP 408) killed 13 research sub-agents overnight → work moved to resumable child sessions with small-context rules; tool round-trips take 5–8 min. (2) No public imagery of Mumbai nullahs → detector metrics are on a public proxy dataset; domain shift (black water, hyacinth, monsoon rain) is a known gap. (3) Simulator parameters are partly ASSUMPTION → we claim *relative* policy gains under Monte Carlo, not absolute tonnage.

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** InnovateX: The Future Habitats Challenge — Techfest IIT Bombay. Prize pool ₹80,000; top 3 teams per theme.
- **Official statement:** [`_briefs/innovatex.pdf`](../_briefs/innovatex.pdf) (text: [`_briefs/innovatex.txt`](../_briefs/innovatex.txt)).
- **Round 1 — in-person pitch at a city zonal (no online submission):** 10 minutes covering team info, the precise problem within the theme, background and why existing solutions fall short, the proposed solution and technology, impact and scalability. Top 5 teams per zonal advance. **Delhi zonal: 10 Oct at South Asian University** (registration open until the zonal date). Other zonals listed on techfest.org: Chennai 10 Oct, Gandhinagar 11 Oct, Hyderabad 11 Oct, Patna 18 Oct, Jaipur TBD.
- **Round 2:** detailed final report + **working prototype** submitted on the website by **1 Dec** (solution description, prototype evidence, cost & market viability, implementation plan, scalability plan, impact assessment); finals **15–18 Dec** at IIT Bombay. (The web page lists a 15 Nov shortlist announcement while the PDF says Round 1 results come on the zonal day — treat as unconfirmed.)
- **Judging:** creativity & novelty · functionality & usability (robust under real conditions) · cost & market value · technical implementation & feasibility (power, calibration, maintenance, weather) · regional scalability · environmental & socioeconomic impact · design & ergonomics · **bonus** for a deep, locally grounded understanding of the theme.
- **Rules:** students, team ≤4 (cross-institute encouraged); **one theme per team**; original work.
- **Gate — selection memo by 7 Oct, 12:00 IST:** the team pitches ONE theme at the Delhi zonal; the Supervisor picks from the three memos. The chosen lead then delivers the full pitch deck + speaker notes + Q&A prep by 9 Oct.
- **Round-1 deliverable for the morning package:** `deliverables/zonal-pitch.md` (10-min deck outline + speaker notes + likely judge questions) + `deliverables/prototype-plan.md` (architecture, bill of materials with costs, build steps, and what can be simulated now).

**Theme 3 — Rising Plastic Pollution in Coastal Cities.** Challenge question (verbatim): "How can technologies be leveraged to monitor, intercept, and reduce rising plastic waste leakage into Mumbai's coastal and urban drainage networks? Propose an innovative solution using IoT waste-level sensors, automated river/creek skimmers, AI-driven sorting mechanisms, barrier-net systems, or community-integrated recycling strategies. Your solution should address a specific plastic waste source and outline its benefits, feasibility, and implementation strategy."
- **Context from the statement:** survey data estimates ~5 million kg (5,000 tonnes) of plastic flows annually from Mumbai's waterways, creeks and stormwater drains (nullahs) into the Arabian Sea.
- **Objectives:** a specific source (single-use plastics entering stormwater drains, creek-mouth accumulation, unsegregated household garbage, beach litter) · a hardware or software solution to intercept, clear or upcycle · feasibility in coastal and urban conditions · implementation plan (sites such as the Malad or Trombay outlets, data, analytics, integration with municipal systems) · challenges (marine corrosion, tides, maintenance, monsoon overflow, reliability) · economic viability · quantified impact on plastic reduction, marine life, flood prevention.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Mumbai context: the Mithi River and the nullah network; BMC trash-boom and floating-barrier efforts; community clean-ups (e.g. Versova beach).
- Interception and detection: The Ocean Cleanup's Interceptor; computer-vision detection of floating plastic; fill-level sensors on trash traps; tide and monsoon data.
- Policy: Plastic Waste Management Rules and Extended Producer Responsibility (EPR).
- What companies ship: river-interception and waste-tracking startups — check recent deployments.

## Phase 0 — what we must be able to show (from the official statement)
- **Hard constraints:** team ≤ 4 students; one theme per team; original work (not patented/published); Round 1 = in-person 10-min pitch at the zonal, nothing to upload; Round 2 = report + *working prototype* by 1 Dec; finals 15–18 Dec at IIT Bombay.
- **Judging → evidence:** novelty → spike with a measured gain over the status quo · functionality under tides/monsoon/corrosion → twin driven by real 2019–2025 tide + rain, flume prototype, dashboard · cost & market → BOM with sourced prices, ₹/tonne vs today, revenue levers (EPR, verified contractor payment) · feasibility → power budget for monsoon insolation, maintenance and calibration plan · scalability → per-site config over fixed contracts; other coastal cities · impact → kg diverted with uncertainty, overflow hours avoided · design & ergonomics → ward-engineer dashboard + crew view · **bonus** → Mumbai specifics (BRIMSTOWAD outfalls, high-tide days, Mithi, booms, desilting probe).

## Key decisions
- 2026-10-04 03:00 — Research and builds run in child sessions (resumable) rather than sub-agents after repeated HTTP 408 failures.
- 2026-10-04 05:10 — Contracts v0.1 (`architecture/contracts/contracts.py`, pydantic v2) fix every component's I/O; children build behind them.

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | Forcing (tide + rain) | site, period → `ForcingSeries` | Open-Meteo ERA5 rain; tide source TBD | – | building | tide RMSE vs gauge |
| C2 | Catchment plastic load | rain, catchment → `LoadSeries` | build-up / wash-off model | – | building | NSE vs boom catch (needs field data) |
| C3 | Outfall hydraulics | rain, tide → `HydraulicSeries` | rational method + tidal stage | – | building | — |
| C4 | Interceptor model | load, hydraulics → `InterceptorSeries` | fixed-efficiency boom | candidate (tide-aware trap) | building | capture efficiency vs flume |
| C5 | Vision detector | frame → `FrameDetections` | YOLO11n | candidate | building | held-out mAP50 |
| C6 | Flux counter | detections → `FluxEstimate` | ByteTrack + line crossing | candidate | building | count error % |
| C7 | Fill estimator | frame + range → `FillEstimate` | ultrasonic / ToF range | – | planned | fill MAE |
| C8 | Edge telemetry | sensors → `SiteTelemetry` | MQTT over 4G / NB-IoT | – | planned | delivery rate, bytes/day |
| C9 | Risk forecaster | rain fcst, tide, fill → `SiteForecast` | rain-threshold rule | candidate | building | Brier score |
| C10 | Dispatch planner | states, forecasts, crews → `DispatchPlan` | fixed schedule (status quo) | candidate | building | escaped kg at equal crew-hours |
| C11 | MRV ledger | clearance records → `LedgerEntry` | manual weighbridge slips | candidate | building | inflated-claim recall at ≤5% false flags |
| C12 | Dashboard | `DashboardBundle` → UI | — | – | building | task time (later) |
| C13 | Recovery & upcycling | `CatchComposition` → `RecoveryRoute` | kabadiwala + co-processing | – | planned | ₹/t, diversion rate |
| C14 | Source attribution | outfall flux + catchments → `WardHotspot` | ward complaints | – | planned | rank correlation (sim) |

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

### 2026-10-04 02:10–05:15 IST — Phase 0 done; research fan-out; builds launched
- Read PLAYBOOK, seeded brief and the official statement; extracted constraints and judging → evidence (above).
- Launched 8 research sub-agents, then 7 narrower ones; 13 died with HTTP 408 ("timed out reading request body") as contexts grew — a machine-wide API congestion problem (sibling projects' agents failed the same way). Partial notes survived in `research/` (e.g. BRIMSTOWAD outfall counts) but lack source URLs, so they must be re-verified before use.
- Switched to 5 resumable child sessions (detection, twin + dispatch, dashboard + MRV, two research compilers) with small-context rules and a 07:45 IST results deadline.
- Wrote contracts v0.1 for C1–C14.
