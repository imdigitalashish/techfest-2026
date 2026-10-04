# InnovateX · Theme 3: Coastal plastic pollution (Mumbai) — Thought Node

> Journal for `innovatex-t3-coastal-plastic/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 3–6 in parallel (spike chosen; skeleton building; deliverables drafting). LEAN MODE until 08:30 (Supervisor).
- **Plan:** source = floating single-use flexible packaging (carry bags, films, sachets) from market and dense-settlement catchments leaking through Mumbai's *small* nullah outfalls. The Ocean Cleanup Interceptors cover the big creek mouths (Malad, Trombay, 2026). Our system is the network layer for the long tail:
  - pocket-fill sensing;
  - forecast- and gate-aware dispatch (Spike 1);
  - a ratchet pocket with a fail-open fuse retrofitted to existing booms (Spike 2, Round 2);
  - signed evidence records so contractors are paid per verified kg.

  Details: [ADR 001](architecture/adr/001-spike.md).
- **Doing:** child sessions — *T3 detection + flux*, *T3 digital twin + dispatch*, *T3 dashboard + MRV ledger*, *T3 research: Mumbai + policy*, *T3 research: tech + companies*. Lead: zonal-pitch.md, prototype-plan.md, then integrating results.
- **Next:** deliverables → integrate twin, detector and dashboard numbers → landscape.md check → final push by 08:15.
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
_First version, 4 Oct 06:20 IST. Final by 7 Oct, 12:00 IST (one theme is pitched at the Delhi zonal on 10 Oct). Scored 1–5, one line of evidence each; **[V]** = still being verified._
- **Winnability — 3/5.** Strong, current local story. The 5,000 t/yr figure in the brief comes from The Ocean Cleanup's 2026 Mumbai survey, and the brief's "Malad or Trombay" outlets are its two pilot Interceptor sites (MCGM permits, MPCB MoU, Plastic Fischer operating) — [mumbai-context](research/mumbai-context.md). Two cautions: Delhi judges may relate more readily to AQI (T2), and a big NGO already occupies the obvious "barrier at the creek mouth" answer.
- **Innovation headroom — 3/5.** Spike 1: forecast- and gate-aware clearance dispatch, scored on escaped kg at equal crew-hours against a fill-threshold baseline and a perfect-foresight oracle. Spike 2: a ratchet pocket with a fail-open fuse, retrofitted to existing booms at the long tail of small outfalls. One-way flap traps are prior art; our novelty is the tidal-outfall retrofit plus operations plus verified kg — [ADR 001](architecture/adr/001-spike.md).
- **Feasibility by the deadline — 4/5.** The software skeleton runs tonight on real ERA5 rain and real tide data on the M5 Mac. The flume prototype is a tabletop build. Prototype work fits in 10 Oct – 15 Nov, before the 19–25 Nov exams.
- **Demo strength at the finals — 4/5.** A reversible-flow flume where the tide turns and the trash stays, the fuse opens before the water rises, and a live dashboard counts it. That is visual and memorable.
- **Fit with the user's strengths — 3/5.** Systems, ML and data pipelines are a strong fit. Hydraulics and fabrication are not, so the flume needs a teammate with hands-on skills.
- **Biggest risk:** evidence is simulation-only until field data exists (circularity), and "why not just The Ocean Cleanup?". Mitigations:
  - position the work as complementary — it covers the outfalls Interceptors won't reach and makes per-kg pay verifiable;
  - report only relative gains under Monte Carlo;
  - run a flume test before 10 Oct.
- **One-line pitch:** "Two Interceptors will cover two of Mumbai's creeks. We make the hundreds of small nullah booms accountable. Crews clear before the storm and in the gate-closed window, a fail-open pocket keeps trash in when the tide turns, and contractors are paid only for verified kilograms."
- **Lead's recommendation (provisional):** pitch T3 only if the twin shows a held-out gain clearly beyond noise and someone can run the 2-hour flume test before 10 Oct. Otherwise defer to the sibling with the stronger demo.

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 02:10–05:15 IST — Phase 0 done; research fan-out; builds launched
- Read PLAYBOOK, seeded brief and the official statement; extracted constraints and judging → evidence (above).
- Launched 8 research sub-agents, then 7 narrower ones; 13 died with HTTP 408 ("timed out reading request body") as contexts grew — a machine-wide API congestion problem (sibling projects' agents failed the same way). Partial notes survived in `research/` (e.g. BRIMSTOWAD outfall counts) but lack source URLs, so they must be re-verified before use.
- Switched to 5 resumable child sessions (detection, twin + dispatch, dashboard + MRV, two research compilers) with small-context rules and a 07:45 IST results deadline.
- Wrote contracts v0.1 for C1–C14.

### 2026-10-04 05:15–06:20 IST — ADR 001, Mumbai reality check, lean mode
- `architecture/components.md` added: dependency graph, per-component contracts, metrics and SLOs, glossary.
- **ADR 001 accepted.**
  - Inputs: an independent adversarial review and a first-principles review, both stored verbatim in `research/reviews/`.
  - Spike 1: forecast- and gate-aware dispatch, hardened with archived forecasts, a P1 baseline, an oracle upper bound and Monte Carlo.
  - Spike 2: ratchet pocket with a fail-open fuse; hardware for Round 2, a labelled sensitivity in the twin tonight.
  - Detection and the MRV ledger stay best-practice support.
- **Key finding from research (cited in `research/mumbai-context.md`, `research/companies.md`).**
  - The brief's 5,000 t/yr figure is from The Ocean Cleanup's Smart Rivers Survey (10 Feb 2026).
  - Malad and Trombay creeks are its two pilot Interceptor sites: MCGM SWD permits, MPCB MoU (30 Apr 2026), Plastic Fischer operating, 61–92 t/yr expected.
  - Response: reposition to the long tail of small outfalls, complementary to the Interceptors.
- Children were steered with the review findings: archived forecasts, oracle baseline, gated vs open outfalls, the FWCE metric, ledger framing, and a prior-art check for the ratchet.
- The Supervisor declared LEAN MODE (no new agents or sessions, downloads ≤200 MB, push every 30 min). Complied: no new spawns; the detection child got the download cap.
- Selection memo v1 written.
