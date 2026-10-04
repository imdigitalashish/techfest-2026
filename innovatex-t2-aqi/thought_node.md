# InnovateX · Theme 2: Rising AQI in modern cities — Thought Node

> Journal for `innovatex-t2-aqi/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 6 — **DONE as an honest, fully documented alternative** to T1 (2026-10-04 16:27 IST). Two cross-model reviews ran (gpt-6-astra max: hostile judge; gpt-6-sol max: code/eval), and their findings are applied (`reviews/2026-10-04-lead-response.md`, `reviews/ledger.tsv`). Memo FINAL v3 recommends **T1** for the Delhi zonal; gate 7 Oct 12:00 IST.
- **Package on main:** `deliverables/zonal-deck.pdf` / `.pptx` (9 main + 8 backup slides, timed notes: 8:45 + 1:15 reserve, ~99 wpm), `qa-prep.md` (22 Qs), `presenter-card.pdf` (1 page), `demo/dustledger-demo.html` (offline), `prototype-plan.md` (lead-verified BOM ₹60,711 parts; power model estimate), `research/fact-check.md` (25 rows) · numbers rendered by `eval/render_docs.py`, checked by `eval/check_docs.py` (0 problems).
- **Resume point if T2 is chosen:** (1) user fills team fields (slide 1, card); rehearse on the PDF with the card; (2) side-by-side sensor agreement test, then a blind known-source test; (3) attribution ratchet with **work-hour MAE** as the new primary metric on DEV, with a sealed holdout held by a separate reviewer; (4) swirling-wind / node-disagreement abstention; (5) source the open items (CAQM operative order, PM10 sensor targets, suppression efficiency).
- **Needs from user:** (a) zonal theme decision + registration by 9 Oct (T1 recommended); (b) team names/skills (an embedded teammate helps); (c) if T2: a pilot site or reference co-location slot by ~20 Oct, and institutional approval for a controlled dust test; (d) later: hardware purchase (parts list in `deliverables/bom/bom.csv`).
- **Risks (T2):** coarse-dust sensor agreement (CSTEP: qualitative); work-hour accuracy (simulated MAE ~116 µg/m³); calm-wind abstention; small city share of construction PM; untested willingness to pay; trial timing vs Delhi's 1 Nov restrictions.

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
- 2026-10-04 — City = Delhi-NCR; pollution source = construction & demolition dust; product = DustLedger (site-level attribution, not city AQI). Evidence: blanket bans in WAP 2026-27 and GRAP, area-based fines, 1.38 M construction workers on Delhi's welfare-board rolls (89,518 active), no vendor attributes a site's own increment ([landscape](research/landscape.md)).
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
| **C6** | **Attribution** | Calibrated + Wind → SiteIncrement | single-pair subtraction | **yes** | **replay v0 + ratchet ledger** (`components/attribution/`) | **increment MAE, stress-tested holdout (v2.1): ring+self-cal 57.4 vs ring 69.1 vs fixed pair 95.8 µg/m³ (SIMULATED site)** |
| C7 | Background forecast | public data → BackgroundForecast | persistence; IITM AQEWS | | **running on real data** | MAE skill vs persistence |
| C8 | Suppression controller | SiteIncrement + forecast → ActuationCommand | timer anti-smog gun | 2nd spike | designed | µg·h avoided per kL (sim) |
| C9 | Misting actuator | command → ActuationLog | relay + pump | | designed | latency; litres logged vs metered |
| C10 | Evidence ledger | records → LedgerEntry, report | CCTV + self-audit | | designed | tamper detection rate |
| C11 | Work-window advisor | forecast → advice | none | | designed | dusty hours moved (replay) |
| C12 | Dashboards | all → UI | DPCC portal forms | | designed | time-to-answer (scripted) |

## Selection memo
_FINAL v3 (honest alternative), 4 Oct 2026, after two cross-model reviews of this package (gpt-6-astra max: hostile judge, mean 2.3/5 core criteria; gpt-6-sol max: code/eval, reproduced the headline numbers). Gate: 7 Oct 12:00 IST. The two earlier pick-judges chose **T1 JalSakshi** (their T2 means 2.6 and 2.8/5). Scores below are 1–5, after the fixes in `reviews/2026-10-04-lead-response.md`._
- **Winnability — 2/5.** A Delhi panel knows the problem: the reported 2026-27 plan restricts dust-generating construction citywide Nov 1 – Jan 31 (total ban Dec 10 – Jan 20); GRAP-3 stopped construction for 16 days in 2025. But our honest answers (simulated sites, no city-AQI number, "inconclusive" in calm wind, no buyer) are hard to land in 10 minutes. Whether AQI is the most crowded theme at the zonal is UNVERIFIED.
- **Innovation headroom — 3/5.** Fence-line monitoring is established commercially; our increment is a low-cost Indian construction workflow (wind-resolved ring + abstention + self-calibration + misting control + signed records). Stress-tested replay (real background + wind, simulated sites; fresh seeds, **not blind**): fixed pair 95.8 → ring 69.1 → self-calibration **57.4 µg/m³** all hours vs **64.9** for the strongest reference-visit baseline. **In work hours self-calibration is no better (115.8 vs 115.0)**; its gain is about half the false alarms (FAR 0.145 vs 0.305).
- **Feasibility by 1 Dec — 2/5.** Parts are priced (₹60,711 per site kit, parts only) and power closes on paper (10.2 Wh/day per node, 2.1× in an average December; model estimates). Three hard problems compound: coarse-dust response of optical sensors (CSTEP: qualitative), calm wind (ERA5 grid below 0.5 m/s in 4.0 % of Nov–Jan hours; site calm unmeasured), and access — a real-site trial needs a site and approvals before Delhi's 1 Nov restrictions, otherwise an approved controlled test.
- **Impact — 2/5.** IIT Kanpur's study for DPCC put construction material at 2–5 % of ambient PM10 (2013–14 data). The case is targeted, fairer inspection; there is no measured PM, water or wage outcome, and near-site exposure is unmeasured.
- **Demo strength — 3/5.** An offline demo now exists (regulator ranking on simulated sites over a real Delhi week). A live ring around a dust source at the finals would be strong — if built.
- **Fit with the user's strengths — 3/5.** Pipeline, evaluators and modelling fit; embedded hardware and field trials need a teammate.
- **Biggest risk:** the coarse-dust measurement itself, plus work-hour accuracy. If identical low-cost sensors don't agree on construction dust, or work-hour errors stay near today's simulated levels, the site estimate can't support decisions.
- **Case FOR T2 over T1:** a policy pain the Delhi panel sees every winter; a deep, current local evidence base (restrictions, fines, workers, monitoring); a stronger software/ML story; an honest, reproducible evaluation stack (render/check pipeline, two reviews, ledger).
- **Case AGAINST T2 (stronger):** construction was a small share of city PM; the self-calibration spike does not improve work-hour accuracy in simulation; feasibility rests on unproven coarse-dust sensing and calm-wind abstention; the first real-site trial collides with Delhi's November restrictions; willingness to pay is untested; both pick-judges and this package's hostile reviewer chose T1. T1 also needs commissioning (node, rain gauge, gateway), but its physical evidence gate (a metered pour test) is shorter and more checkable.
- **Recommendation: pitch T1 at the Delhi zonal.** Keep T2 as the documented alternative if the user prefers AQI. If T2 is chosen: fill team fields, rehearse with `presenter-card.pdf`, and run the side-by-side sensor agreement test first.
- **One-line pitch (if chosen):** *"Delhi's winter dust rules follow the activity and the pollution stage, not what each site releases. DustLedger estimates each site's own dust with a low-cost fence-line ring, says 'inconclusive' when it can't tell, and gives inspectors a list of where to look first."*

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

### 2026-10-04 08:05 IST — Correction: replay evaluator v1 (5 seeds) supersedes the 07:57 single-seed numbers
- A 5-seed run exposed a bug in evaluator v0: simulated sensor slope drift was unbounded (5 %/month linear over ~20 months), so slopes could go negative, giving NaN for self-cal and inflated TEST errors. Fixed in v1: drift ±10 %/yr (1-sd), clipped to 0.5–1.5×; non-finite estimates count as abstentions; method guards (median ≥ 1, ratio clipped). The v0 rows stay in `results.tsv`, marked as not comparable.
- **v1 (TEST 2026, mean ± sd over 5 seeds):** fixed pair 97.8 ± 15.6 → ring 58.0 ± 16.0 → **ring + self-cal 33.8 ± 2.6 µg/m³**; CSI > 50: 0.34 → 0.58 → 0.76. The conclusion holds and is more robust. Thought node, ADR 001 and pitch corrected. Reproduce: `cd components/attribution/autoresearch && OMP_NUM_THREADS=1 python eval.py all 5`.

### 2026-10-04 08:45 IST — Independent hostile review acted on; post-08:30 work
- Supervisor (08:22): package accepted; tied with T1 for the Delhi zonal; gate 7 Oct after a hostile-judge review. Asks: land v1 (done, `30ed40b`), verify BOM prices, near-final deck, and an answer to "AQI is the most crowded theme — why you?" (now Q0 in the pitch).
- Ratchet r2 (top-2 downwind nodes): DEV −0.20 µg/m³, below the noise bar → not kept, reverted, logged.
- `rubber-duck` review: the spike holds, but lead with the decision gap + ring + abstention. The self-calibration gain is partly simulation-shaped; the evaluator v2 plan is in ADR 001. Eight overclaims fixed in the pitch; the Q&A was rewritten around what's real vs simulated.
- Running: `bom-prices` research agent (browser-based vendor listings). Next: build the near-final deck (`deliverables/deck/`, figures from committed results), then evaluator v2.

### 2026-10-04 09:10 IST — Near-final zonal deck v1
- `deliverables/deck/DustLedger_zonal.pptx`: 10 slides + 2 backup, speaker notes on every slide, figures generated from committed results (`make_figures.py`; simulated parts labelled on the figures). Rebuild: `cd deliverables/deck && OMP_NUM_THREADS=1 python make_figures.py && python make_deck.py`. Team name/ID/members are blanks for the user. Not visually QA'd in PowerPoint yet (no headless renderer); a heuristic overflow check passed.

### 2026-10-04 09:50 IST — Evaluator v2.1: the spike holds at an honest size (lean mode again)
- Built `components/attribution/autoresearch/eval_v2.py` from the reviewer's three fixes: separate dust/ambient gains, fouling, offsets, saturation; contaminated nights, spatial gradients, a neighbour site, a road; vane bias/decorrelation; 3 scenarios × 5 seeds; DEV printed; holdout = TEST + unseen seeds + a hidden site geometry, lead-only. Added the fair baseline `ring_refcal` (weekly reference visits). Bug found and fixed (v2.0 visits were all NaN) before comparing.
- **Holdout (run once):** pair 95.8 → ring 69.1 → ring + ref visits 69.4 → **ring + self-cal 57.4 µg/m³**; CSI 0.29 → 0.61. Self-cal wins in every scenario; its gain is −17 % (v1 said −42 %). Figure, deck (slide 8), pitch, ADR and ledger updated with the conservative numbers.
- Supervisor 09:40: lean mode back (no new sub-agents; `nice -n 10`; one heavy job at a time). `bom-prices` and the hostile-judge review were launched before that: the review is done and acted on; the BOM agent is still running.

### 2026-10-04 10:00 IST — Paused (Supervisor 09:55)
- Saved state: no compute jobs running; all results committed. Prototype plan points to the partial agent-sourced BOM listings (items 1–10). The memo now leads with the stress-tested replay numbers. *Now* holds the exact resume point and restart commands. Going idle; only the `bom-prices` agent's completion will be saved and pushed.
- 10:05 — `bom-prices` agent finished: all 16 BOM items have vendor listings with ₹ (incl. GST), stock and URL in `research/raw/hardware-bom.md`, plus datasheet quotes for 5 sensors. Caveats: no low-cost anemometer + vane in stock; SX1262 IN865 band unconfirmed. The lead spot-check and §2 fill remain resume step (2). Idle again.

### 2026-10-04 15:33 IST — Resumed (Supervisor 15:32)
- Batch slot freed by India@71 T3. Two judges picked T1 for the Delhi zonal; this project becomes a documented, honest alternative. *Now* rewritten with the Supervisor's definition of done and the new rules (child sessions only, no stash/autostash, clock timestamps, nice/memory gates).

### 2026-10-04 15:53 IST — Round-1 package rebuilt as an honest alternative
- **BOM verified by the lead** in a browser (17 listings, 15:34–15:35 IST): kit parts ₹60,711 (4 nodes ₹40,128 · wind ₹14,810 · gateway ₹3,516 · misting ₹2,257); `deliverables/bom/`. **Power budget** from datasheets the lead opened (SPS30 60 mA; ESP32-S3 13.2 mA modem-sleep) + NASA POWER irradiance: 10.2 Wh/day per node, 2.1× in December, 12.1 days autonomy.
- **New primary source:** IIT Kanpur's 2016 study for DPCC (Delhi govt copy) puts construction material at 2–5 % of ambient PM10; C&D = 3.6 % of PM10 emissions (our arithmetic from Table 3.1). This weakens T2's impact case, and the pitch and memo now say so upfront.
- **Calm wind** (ERA5, real): Nov–Jan wind < 1 m/s in 16.2 % of hours (< 0.5 m/s: 4.0 %), lower bounds for a site.
- **Docs pipeline:** templates in `deliverables/src/` → `eval/render_docs.py` (run numbers from committed results; cited numbers bound to `research/fact-check.md`, 25 rows) → `eval/check_docs.py` (drift, binding, unmarked numbers, stale claims, memo numbers): 0 problems.
- **Deck:** Marp → `zonal-deck.pdf` / `.pptx`, 10 main + 6 backup slides, timed notes (9:15 + 45 s); every slide visually checked (PNG contact sheets); figures regenerated from committed results (time series now from evaluator v2.1). The old python-pptx deck was removed. Presenter card: one A4 page (`presenter-card.pdf`). Q&A: 22 questions.
- **Memo v2:** honest case for and against T2; recommendation: pitch T1 at the zonal, keep T2 as the documented alternative.
- Note: one Marp build started at `kern.memorystatus_level` 29 (gate is 30); short job, no harm; later builds checked the gate first.

### 2026-10-04 15:57 IST — Lead re-verified the cited numbers; corrected the fine yardstick
- Re-opened 10 agent-sourced fact rows (F3, F5–F8, F11, F12, F14, F15, F19) with curl + grep: all quotes and numbers match, except one conflation found in F6. The HT article reports CAQM's 2024 schedule as **₹1–2 lakh per construction-site violation by area** (doubled under GRAP), and the '₹5 lakh irrespective of AQI' was Delhi's *pre-standardisation* practice. Fixed in the fact table, deck slides 3 and 9, Q&A Q10, presenter card, prototype plan, landscape and ADR 001. The parts cost is now framed as 30–61 % of one fine. Added the old phrasing to check_docs' STALE list. Deck/PDF/PPTX/card rebuilt; slides 3 and 9 checked visually.
- Reviewers launched (child sessions): gpt-6-astra max (hostile judge on the deck/pitch) and gpt-6-sol max (code/eval reproduction). They review commit 41e391e; this fine correction postdates it and will be noted in the lead response.

### 2026-10-04 16:03 IST — Offline demo added (parity with T1's package)
- `deliverables/demo/dustledger-demo.html` (offline, self-contained) + README with a 60-second script; screenshot on new backup slide B7. REAL panels: 4 monitors' winter PM10, the demo week's background + ERA5 wind. SIMULATED: six sites on real background/wind (same physics as evaluator v2.1 'medium'); regulator ranking, inconclusive share, misting-on hours vs timer (misting effect not modelled). The truth toggle shows the errors: estimates are below truth in calm hours, and the two cleanest sites swap ranks.
- Held-out ranking check (20 simulated sites, emissions 0.1–3×): Spearman ρ 0.99, top-5 found 5/5. That's an easy test by construction, and it's labelled as such. Rendered via `demo_rho` / `demo_top5` keys; check_docs 0 problems. Script timing: 838 words in 9:15 (~91 wpm).

### 2026-10-04 16:27 IST — Cross-model reviews applied; package final; DONE
- **gpt-6-astra (max)**, hostile judge: mean 2.29/5 (core); keep T1. 37 items: 32 accepted, 4 partial, 1 rejected (team fields stay placeholders). Main fixes: restrictions described by activity/stage (not "every site"), fine yardstick (₹1–2 lakh as reported; no ratio), survey attributed to Aledia, abstention claims matched to code (0.5 m/s), no site-calm "lower bound", approval-dependent trial plan, power labelled as model estimates, no "nobody" claims, forecasting moved to backup, solution now at 3:15.
- **gpt-6-sol (max)**, code/eval: reproduced every headline number (forecast, v2.1 holdout, calm wind, BOM, power, render/check, one-week ingest). 9 findings: 7 accepted, 2 partial. The forecast "≤ 4 %" gain was an **oracle** with tomorrow's weather; without it, PM2.5 ML lost to persistence. The holdout is **not blind**. A stronger baseline (`ring_refcal14`, 64.92) was added. **New machine-written breakdown: self-calibration is no better than that baseline in work hours (115.77 vs 115.05); its gain is fewer false alarms (FAR 0.145 vs 0.305).** The accuracy claim is withdrawn. check_docs hardened (exact-token binding, ₹ tokens, TSV-vs-JSON check; both reviewer attacks now fail). Ingest records completeness and refuses mixed units; undefined FAR is null.
- Deck rebuilt (Marp → PDF/PPTX) and every slide re-checked visually; presenter card one page; script ~868 words in 8:45.
- Memo FINAL v3: T2 scores 2–3/5 per criterion; recommendation: pitch **T1**.
