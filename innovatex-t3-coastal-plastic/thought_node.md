# InnovateX · Theme 3: Coastal plastic pollution (Mumbai) — Thought Node

> Journal for `innovatex-t3-coastal-plastic/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** ▶ **RESUMED 2026-10-04 15:57 IST** (Supervisor). T1 JalSakshi is the Delhi-zonal pick. T3's job is to be a complete, honest, documented alternative, not to out-spin T1.
- **Definition of done (Supervisor, 15:56):**
  1. **Evidence:**
     - YOLO11n detector baseline: "GPU request" sent first; ≤60 min.
     - Twin: escape split by cause (entrainment, overflow, bypass), fail-open fuse sensitivity, paired P2−P1 interval. All SIMULATED and labelled.
  2. **Zonal package at T1's bar:** deck (PDF + PPTX), Q&A prep, one-page presenter card, prototype plan with ₹ + URL + date for every part. ⟨FILL⟩ markers filled; the 2 [V] claims resolved or marked UNVERIFIED.
  3. **Numbers rendered from committed results:** `eval/render_docs.py` + `eval/check_docs.py` (drift check); licences recorded in `README.md`.
  4. **Cross-model reviews as child sessions:** gpt-6-astra (max) as hostile judge on deck and pitch; gpt-6-sol (max) on code and eval, reproducing the headline numbers. Recorded in `reviews/` + `reviews/ledger.tsv`.
  5. **Final memo (honest T3 vs T1),** thought node current, all pushed → message "DONE — slot free".
- **Doing (16:37):**
  - *T3 detection + flux*: YOLO11n training on the GPU (≤60 min), then test eval.
  - *T3 hostile judge (astra)*: gpt-6-astra, max effort, reviewing the deck and package.
  - Twin child is done: angle, entrainment-split and exposure code pushed (13135c3). The lead runs `nice -n 10 python -m twin_sim.analysis` once the lock frees.
  - Next: when detection finishes, launch *T3 code/eval review (sol)* (gpt-6-sol, max).
- **Rules now:** child sessions only, no `task` sub-agents. No `git stash` / `--autostash`. Timestamps from `TZ=Asia/Kolkata date`.
- **Plan:** source = floating single-use flexible packaging (carry bags, films, sachets) from market and dense-settlement catchments, leaking through Mumbai's *small* nullah outfalls. The Ocean Cleanup's 2026 Interceptors cover the big Malad and Trombay creek mouths. NullahNet is the network layer for the rest:
  - pocket-fill sensing;
  - tide-aware dispatch (Spike 1, support: −2.1% escaped in the twin);
  - a **fail-open fuse retrofit with an instrumented pocket** for BMC's steel-net booms (Spike 2, headline; flume-tested);
  - signed evidence records for pay per verified kg.
  See [ADR 001](architecture/adr/001-spike.md).
- **Done tonight:** [landscape](research/landscape.md) · [components + contracts](architecture/components.md) · [per-component research](research/components/README.md) · [ADR 001](architecture/adr/001-spike.md) · selection memo v1 (below) · [zonal pitch](deliverables/zonal-pitch.md) · [prototype plan](deliverables/prototype-plan.md) · skeleton: twin + dispatch on real forcing, evidence ledger, dashboard, detection scaffold · [results](eval/RESULTS.md) · two autoresearch ledgers (twin, detection).
- **Needs from user:**
  1. Decide whether to pitch at the Delhi zonal (10 Oct, South Asian University) and register by 9 Oct.
  2. If T3 is chosen, name a teammate with fabrication skills. Ideally that teammate runs a ~2-hour tabletop reversed-flow flume test before 10 Oct (a box, a small pump, film pieces, phone video — see [prototype-plan](deliverables/prototype-plan.md) §3, T2/T3).
  3. Approve purchases later: flume electronics ₹33,958 and field node ₹82,282, both sourced. The flume structure is not yet priced.
  4. Supply team name, Team ID and member details for slide 1.
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
- 2026-10-04 16:25 — Spike 2 reframed: capture geometry + one-way pocket are the capture levers; the fuse is for flood safety. Dispatch is a supporting lever. Prototype method changed to a tow tank ([ADR 001](architecture/adr/001-spike.md)).
- 2026-10-04 16:10 — Deliverables are rendered from templates + committed results; `eval/check_docs.py` enforces source binding and drift (0 problems required).

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | Forcing (tide + rain) | site, period → `ForcingSeries` | ERA5 rain + archived JMA forecasts; UTide fit to Open-Meteo Marine | – | **done (v0)** | tide fit RMSE ≈ 0.08 m (vs model sea level, not a gauge) |
| C2 | Catchment plastic load | rain, catchment → `LoadSeries` | build-up / wash-off model | – | building | NSE vs boom catch (needs field data) |
| C3 | Outfall hydraulics | rain, tide → `HydraulicSeries` | rational method + tidal stage | – | building | — |
| C4 | Interceptor model | load, hydraulics → `InterceptorSeries` | fixed-efficiency boom | Spike 2 (ratchet + fuse, via H1) | **done (v0, SIMULATED)** | capture efficiency vs flume |
| C5 | Vision detector | frame → `FrameDetections` | YOLO11n | – (instrumentation) | zero-shot only; training paused | zero-shot COCO YOLO11n — TUD-GV held-out test (254 img): mAP50 0.394, mAP50-95 0.209, P 0.756 / R 0.140 @ 0.25; Groningen cross-site: mAP50 0.405 ± 0.026, R 0.010 @ 0.25 |
| C6 | Flux counter | detections → `FluxEstimate` | ByteTrack + line crossing | – | **v0** | count error 75% on a SYNTHETIC sequence (zero-shot detector) |
| C7 | Fill estimator | frame + range → `FillEstimate` | ultrasonic / ToF range | – | planned | fill MAE |
| C8 | Edge telemetry | sensors → `SiteTelemetry` | MQTT over 4G / NB-IoT | – | planned | delivery rate, bytes/day |
| C9 | Risk forecaster | rain fcst, tide, fill → `SiteForecast` | rain-threshold rule | candidate | building | Brier score |
| C10 | Dispatch planner | states, forecasts, crews → `DispatchPlan` | fixed schedule (status quo) | Spike 1 (support) | **done (v0) + ratchet** | held-out escaped kg: −2.1% median vs P0 (SIMULATED) |
| C11 | MRV ledger | clearance records → `LedgerEntry` | manual weighbridge slips | – (support) | **done (v0)** | recall 0.72 @ 4.7% false flags; precision 0.45 @ 5% prevalence (SYNTHETIC) |
| C12 | Dashboard | `DashboardBundle` → UI | — | – | **done (v0)** | task time (later) |
| C13 | Recovery & upcycling | `CatchComposition` → `RecoveryRoute` | kabadiwala + co-processing | – | planned | ₹/t, diversion rate |
| H1 | Barrier hardware: angled boom + one-way pocket + fail-open fuse | flow → retained catch, head rise | BMC steel-net boom | **Spike 2** | designed; tow tank priced (Oct) | T2 retention after N reversals; T3 head rise ≤ cap; T6 capture vs angle |
| C14 | Source attribution | outfall flux + catchments → `WardHotspot` | ward complaints | – | planned | rank correlation (sim) |

## Selection memo
_v2, 4 Oct 2026, 16:30 IST (after the afternoon evidence; final after the cross-model reviews). **Context:** T1 JalSakshi was picked for the Delhi zonal by two independent judges. This memo is the honest case for and against T3 as the alternative. Scores are 1–5 with one line of evidence each. Sources: [fact-check](research/fact-check.md) · [results](eval/RESULTS.md)._

- **Winnability — 3/5.**
  - For: specific, current and Mumbai-grounded, which is the theme's own city. The brief's 5 million kg figure is The Ocean Cleanup's 2026 survey. BMC is growing its boom network from 9 to 23 at ≈ ₹1 crore each, plus a ₹14.5 crore two-year O&M contract, so there is a clear buyer and a clear budget line. T1 lacks this.
  - Against: an internationally known incumbent (The Ocean Cleanup + Plastic Fischer) already holds the two outlets the brief names, and a Delhi audience gets no home advantage.
- **Innovation headroom — 2/5 on today's evidence, 4/5 if the tow tank confirms the pocket.**
  - Tide-aware dispatch robustly beats the sensor-only rule: −5.6% escaped, better in 39/40 draws (SIMULATED). Against today's fixed schedule the gain is small and uncertain (−2.1%, interval crosses zero).
  - The twin says escape is mostly under the boom, so the big lever is capture geometry and retention. That claim is a SENSITIVITY, and one-way floating traps are prior art (Bandalong).
  - T1 scored 3 on novelty under hostile review.
- **Feasibility by 1 Dec — 4/5.** A tow-tank flume with every part sourced, URL and date per line: structure ₹4,969.12 + electronics ₹33,957.99. The dashboard, twin and evidence records are BUILT. The schedule avoids the exams. Needs a hands-on teammate, as T1 does.
- **Demo strength — 3/5 now, 4/5 with the tow tank.** Live dashboard and twin figures today. At the finals, a boom model towed back and forth while the pocket keeps its catch.
- **Fit with the user's strengths — 3/5.** Systems, data and evidence pipelines fit well; the detector is commodity; hydraulics and fabrication need a teammate.
- **Cost realism — weaker than T1.** A field node is ₹83,481.98 (Pi 5, AI HAT, 4G, 1.28 kWh battery) against T1's ≈ ₹11k. A duty-cycled variant needs a much smaller battery, but it is not yet priced as a set.
- **Biggest risks:**
  - every outcome number is simulated, with the circularity stated;
  - the hardware lever is unproven and has prior art;
  - AGPL-3.0 on the detector stack for any commercial use;
  - "why not The Ocean Cleanup?"
- **Verdict (honest):** **against switching.** T3's mean is ≈ 3.0 vs T1's 3.4 after hostile review. T3's strongest card (named buyer and budget, Mumbai specificity) does not outweigh its modest measured gains, a ~7× costlier node and a strong incumbent at the named sites. Keep T3 as a documented alternative. It becomes competitive only if a two-hour reversal test shows clear pocket retention before 10 Oct.
- **One-line pitch:** *"Mumbai's trash booms leak in fast flow, are cleared on a fixed schedule and are paid on claimed loads. NullahNet retrofits them so crews clear at the right tide, the boom keeps its catch and never raises flood levels, and contractors are paid per verified kilogram."*

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

### 2026-10-04 06:20–07:20 IST — Deliverables v1, research landed, first real numbers
- `deliverables/zonal-pitch.md` (11 slides, speaker notes, 15 judge Q&A) and `deliverables/prototype-plan.md` written. The prototype plan covers the flume plus edge node plus cloud, tests T1–T5, and a schedule around the exams. Both were then filled from cited research:
  - BMC runs 9 steel-net nullah booms with conveyors, 14 more planned, at ≈ ₹1 crore each, catching 1.5–3 t/day (HT). Boom O&M is ₹14.5 crore for 2 years at 6 sites (FPJ, 30 Jul 2026).
  - Boom escape velocity is ≈ 0.35 m/s (ITOPF).
  - NASA POWER insolation in Mumbai: July 3.79 vs May 7.09 kWh/m²/day.
  - Sourced BOM: field node ₹82,282; flume electronics ₹33,958.
- The tech + companies session delivered `research/landscape.md` (with "What companies ship today"), `companies.md`, `components/interception-hardware.md` and `components/sensing-edge-bom.md`.
- **Twin, held-out 2024–25 (SIMULATED plastic; real ERA5 rain, archived JMA forecasts, UTide tide):**
  - P2 dispatch: median −2.1% escaped vs the fixed schedule (90% interval −12.5% to +1.5%; 28 of 40 draws better). The gain is mostly tide-aware timing. The held-out evaluation was re-run once after a disclosed look-ahead bug fix.
  - P1 fill threshold: +3.1% escaped.
  - Conclusion: timing is a small lever, so ADR 001 now leads with capture hardware (Spike 2). Reproduce: `cd innovatex-t3-coastal-plastic/components && python -m twin_sim.run`.
- **Evidence ledger (SYNTHETIC records):**
  - 100% tamper detection.
  - 72% of inflated claims caught at 4.7% false flags; a simple ratio check catches 67%.
  - Precision 0.45 at 5% fraud prevalence, so flags trigger review only.
  - Reproduce: `cd innovatex-t3-coastal-plastic/components && python3 -m mrv_ledger.evaluate`.
- `eval/collect_results.py` → `eval/RESULTS.md` collects every committed metric with its reproduce command.

### 2026-10-04 07:20–07:50 IST — Children report done; verification
- **Twin (final, main 56654a1).**
  - Held-out P2 vs P0: median −2.1% escaped (90% interval −12.5% to +1.5%; 28/40 draws better).
  - P1: +3.1% escaped.
  - The gain comes mostly from tide-aware timing (−3.7% on the tuning metric); forecast terms add ≤0.5%.
  - The held-out evaluation was re-run once after a disclosed look-ahead bug (48 h → causal 24 h horizon); see twin.md §4.
- **Dashboard + evidence ledger (main ce18a5e).**
  - Evidence: SHA-256 chain over canonical JSON, published anchor, and Ed25519 per-crew signatures, verified in the browser.
  - Main risk: a +25% bulk-density error raises false flags to 17.8%, so density must be calibrated per site.
  - The Mithi case is cited from HT and The Hindu (May 2025).
- **Lead verification.** `python3 -m pytest -q twin_sim/tests mrv_ledger/tests dashboard` → 32 passed (07:35). The desktop screenshot was checked visually: provenance badges, SIMULATED hatching and Marathi/Hindi labels are present.
- **Research complete:** `mumbai-context.md`, `policy-economics.md` and `recovery-upcycling.md` added; `landscape.md` now lists 109 source URLs collected from the research files.
  - Still open: scrap, EPR and credit prices; desilting rates; whether drain-recovered plastic earns EPR certificates (NOT FOUND); the minimum-wage source URL; C14 not started.
- **Prior art check (lead, 07:58).** The Bandalong Litter Trap (floating, passive, suitable for tidal waterways >2 m wide) already exists. Spike 2 narrows to a fail-open fuse retrofit for BMC's steel-net booms plus an instrumented pocket; see ADR 001 update 08:00.
- **Detection (08:05).**
  - The trained YOLO11n baseline did not complete: the machine was thrashing (swap full, load average ~85).
  - Committed instead:
    - zero-shot COCO YOLO11n on the held-out Groningen cross-site split (63 images, 383 boxes): mAP50 0.405 ± 0.026 (bootstrap), recall 0.01 at conf 0.25;
    - SYNTHETIC flux sequence: 3 of 12 crossings counted (75% error).
  - Reproduce commands are in `eval/RESULTS.md`.
  - **Next:** train on the TUD-GV grouped split once the machine is free.
- **Open items before 10 Oct.** The pitch still has 6 ⟨FILL⟩ markers: team details, detector mAP (×2), flume result, retrofit cost. It has 2 [V] markers: the low-resale-value claim and flood-tide re-floating at open outfalls.
- **Contract change queued for Round 2 (not applied tonight, to avoid drift while children finish):** add optional `signature`, `signer_key_id` to `LedgerEntry` and `ledger_anchor` to `DashboardBundle`. These currently live in `dashboard/site/aux.json`.

### 2026-10-04 08:22 IST — Supervisor accepted the morning package
- The Supervisor agrees that T3 is unlikely to be the Delhi-zonal pick unless T1 and T2 falter.
- From 08:30 Lean Mode lifts with limits: at most 2 concurrent sub-agents or child sessions; no downloads over 1 GB without a stated reason; keep effort light until 7 Oct.
- Actions:
  - No new spawns.
  - The detection child holds one queued task: train the YOLO11n baseline only while the 1-min load is under 20, stop above 40, 60-min cap.
  - The lead keeps the package current and will finalise the selection memo by 7 Oct 12:00.

### 2026-10-04 09:55 IST — PAUSED (user decision via the Supervisor)
- Only 3 projects now run at a time (Namma Space, Perceptron P7, EV C2). T3 is paused, and the Delhi-zonal pick will be T1 or T2.
- The detection child was told to drop its queued YOLO training. Its load-guarded script had been waiting since 08:35 (load 67) and never started; ps confirms no T3 process is running.
- Results saved: the detection child's later commit added zero-shot metrics on the TUD-GV held-out test (mAP50 0.394, mAP50-95 0.209, P 0.756 / R 0.140 @ 0.25). `eval/RESULTS.md` was regenerated and now covers 6 result files.
- The precise resume point is under *Now*. The lead is idle.

### 2026-10-04 15:56–16:26 IST — RESUMED: evidence + final package
- **Resumed** by the Supervisor; Now rewritten.
- **GPU request** sent and granted (15:58). The detection child is training YOLO11n on the GPU under the memory guard and lock. After 3 epochs, val mAP50 is 0.868; zero-shot test mAP50 was 0.394.
- **Twin analysis** (child; SIMULATED; held-out 2024–25; 40 draws):
  - escape is 92.5% under or through the boom (this share includes the assumed still-water leak);
  - P2 vs P1: −5.6%, better in 39/40 draws; P2 vs P0: −2.1%;
  - fuse alone −0.1%; one-way pocket ×0.5 −5.0%.
  - Boom-angle sensitivity requested.
- **Render/check system:** `eval/doc_numbers.py` (47 result aliases), `eval/render_docs.py`, `eval/check_docs.py` (drift, fact binding, unmarked numbers, stale text). `research/fact-check.md` has 29 facts + 6 derived rows. The lead re-opened the headline sources: TOC press release, HT trash booms, Bandalong, BFFP 2023, Ohmsett.
- **Both [V] claims resolved:**
  - low-value film is ignored → BFFP 2023 pp. 40–41;
  - the tide pushes waste back → Lokmat quote.
- **Package v1 built:** deck (10 + 4 backup slides, notes) as PDF and PPTX, Q&A prep (20 questions), one-page presenter card, prototype plan. The flume became a **tow tank**: BOM C ₹4,969.12, with URL and date per row (IndiaMART pages read in a browser, Shopify product data). Node incl. IP66 enclosure ₹83,481.98. `check_docs`: 0 problems.
- **Licences:** `README.md` (AGPL-3.0 detector stack; CC BY 4.0 data; Open-Meteo, NASA POWER and OSM attribution). Lead fix: Open-Meteo attribution added to the dashboard footer (licence compliance).
- **Selection memo v2:** honest verdict against switching from T1 (≈3.0 vs 3.4).
