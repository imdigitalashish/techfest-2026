# InnovateX · Theme 1: IoT underground water management — Thought Node

> Journal for `innovatex-t1-groundwater/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** ⏸ **PAUSED by the Supervisor at 09:55 IST, 4 Oct (user's decision: only 3 projects run at a time).** Queued: by 7 Oct the Supervisor picks the Delhi-zonal theme (this one or T2 AQI) from the memos and decks on main, then resumes the chosen lead to finish the deck by 9 Oct.
- **State on main:**
  - landscape, components + contracts v0.3.0, ADR 001, selection memo v1 (4.0/5);
  - zonal pitch notes, Marp deck draft (`deliverables/zonal-deck.md` + `figures/`), prototype plan with a verified BOM;
  - real DWLR profile and the C0 simulator;
  - C5 verifier v1 (holdout MdAPE 3.0 %; harsher evaluator v2: 13.0 %).
- **Nothing is running.** No background jobs, no sub-agents. All results are saved.
- **Resume point (in order):**
  1. **Ratchet v2 on C5.** Target: `eval_v2.py` dev MdAPE (v1 = 13.03 %) without worsening `eval.py` dev (3.902 %). Next idea: practical-significance threshold `|b−1| > max(2·SE, 0.15)`. Start from `components/recharge_verifier/autoresearch/candidates/v2_exp3_verifier.py`, copy it over `verifier.py`, and edit the beta-selection line. Run one job at a time:

     ```
     cd innovatex-t1-groundwater/components/recharge_verifier/autoresearch
     nice -n 10 ../../../.venv/bin/python eval.py --split dev
     nice -n 10 ../../../.venv/bin/python eval_v2.py --split dev
     ```

     Each run takes ~3–9 min under load. Keep a change only under the rule in `program.md`, then confirm with `--split holdout`.
  2. **C4 ingest-qc module.** Fault-injection F1 on the real DWLR snapshot.
  3. **C8 static dashboard** (offline HTML): real DWLR map + simulated pit storyline.
  4. **Deck polish.** Export with Marp (`npx @marp-team/marp-cli deliverables/zonal-deck.md --pdf`, needs approval to install), fill team details, rehearse Q&A against a hostile judge.
  5. **Close gaps.** Primary source for ₹204.46 cr (currently secondary: HT citing DJB data); NAQUIM Sy/T for Delhi; DJB tariffs and tanker prices.
- **Data regeneration:**

  ```
  innovatex-t1-groundwater/.venv/bin/python innovatex-t1-groundwater/components/data-ingest/fetch_delhi.py
  ```

  This restores `.data/delhi_weather_hourly.csv`, which the simulator needs. The venv needs pandas, numpy, scipy, pydantic, matplotlib, pastas and tqdm.
- **Needs from user:**
  - (a) Decide whether to pitch at the Delhi zonal (10 Oct, South Asian University) and register by 9 Oct.
  - (b) Team name, Team ID and members for slide 1.
  - (c) A pilot site: an RWA or campus recharge pit (IIT Delhi?).
  - (d) Approve the prototype purchase. Verified retail: about ₹10.1k per node (₹13.8k with a rain gauge), a ₹33.6k shared gateway and a ₹14.5k PPK2 bench tool (`research/bom-prices.md`).
- **Risks:**
  1. Pit numbers are simulation only until the physical rig exists.
  2. The v1 verifier assumes a linear drain; the harsher evaluator shows a 13 % error.
  3. Node cost is ≈ ₹10.1k at retail, above the earlier ₹6k target.
  4. Owner incentives and DJB adoption.
  5. ₹204.46 cr is secondary-sourced.

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
- 2026-10-04 — Ground the pitch in **Delhi**. The hero problem is **recharge verification for Delhi's RWH rebate/penalty regime**, under the official option "aquifer recharge analysis". Evidence: `research/landscape.md` §1 and §6.
- 2026-10-04 — Spikes: **C5 recharge-verifier** (primary) and **C4 ingest-qc** (data integrity), chosen after six hats and an independent rubber-duck antithesis. See [ADR 001](architecture/adr/001-spike.md).
- 2026-10-04 — Claims we will not make or pursue:
  - no claim to identify illegal borewells from 6-hourly DWLR data;
  - SealGuard is dropped from the pitch;
  - we report infiltrated volume with uncertainty, never "aquifer recharge" from pit stage.
- 2026-10-04 — Real data first: the India-WRIS dataset API (POST) and ArcGIS layer for groundwater; ERA5 via Open-Meteo for rain and pressure. Snapshots are committed under `eval/data/` with attribution.

## Components
Full table, contracts and graph: [architecture/components.md](architecture/components.md). Contracts: `architecture/contracts/gwcontracts.py` (v0.3.0, 17 JSON schemas).

| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C0 | twin-simulator | ERA5 rain + structure → RawSample + truth | — | test harness | **built** | mass-balance closure |
| C1 | sensor-front-end | physical → RawSample | vented / ultrasonic | — | design | stage RMSE (mm) |
| C2 | edge-firmware | RawSample → UplinkFrame | fixed-interval DWLR (2/day) | — | design | mAh/day at equal error |
| C3 | telemetry-link | UplinkFrame → DeliveryReport | GPRS | — | design | % events ≤24 h |
| C4 | ingest-qc | frames / WRIS JSON → Series + QCReport | range/flatline | ★2 | real-data profile done | fault F1; % usable |
| C5 | recharge-verifier | Series + structure → RechargeEvent | self-certification | ★1 | **ratchet v1: holdout MdAPE 3.0 % (sim)** | event-volume MdAPE |
| C6 | hydro-twin | Series → HeadModelFit, RechargeEstimate | Pastas TFN | — | planned | holdout NSE |
| C7 | inspection-queue | events/QC → InspectionTicket | complaints | — | planned | precision@k |
| C8 | dashboard | all → HTML | ThingSpeak/Blynk | — | planned | 5-task time |

## Selection memo
_v1, 4 Oct 2026, 07:55 IST. The final is due 7 Oct, 12:00. Scores are 1–5, with one line of evidence each. **Overall: 4.0/5** (mean of the five scores)._
- **Winnability — 4/5.** The problem is specific and very local, with dated sources:
  - DJB paid ₹204.46 cr in RWH rebates in 2017–24, and moved to self-certification in Apr 2026.
  - The minister said there was "no real checking" (HT, 21 Apr 2026).
  - 1,000 government RWH systems are non-functional (IE 2026).
  - Our own India-WRIS run shows 23 % zero readings across 185 telemetric stations.

  This hits the local-depth bonus squarely. Typical rival teams pitch ESP32 + ultrasonic sensor + dashboard.
- **Innovation headroom — 4/5.** The spike is a per-storm pit water balance that outputs infiltrated volume with an uncertainty band, a clogging index and fake detection. It turns a rebate rule into evidence.
  - The incumbents are self-certification or manual inspection.
  - CGWA-style DWLRs log 2 readings a day and cost about ₹38k (Acorn).
  - Not yet proven on real pits: simulation only tonight; the rig comes in October.
- **Feasibility by the deadline — 4/5.**
  - The hardware is cheap and shallow (≤3 m), and a drum-and-drain rig gives ground truth.
  - The software runs on the M5 Mac with no GPU.
  - Post-monsoon storms are scarce, so fill tests and the rig carry the Round-2 evidence.
  - User work is concentrated before 17 Nov, avoiding the 19–25 Nov exams.
- **Demo strength at the finals — 5/5.** Pour water into a pit model on stage and the event, verdict and clogging alert appear live. Pour without "rain" and it's flagged implausible. A real Delhi DWLR map sits behind it.
- **Fit with the user's strengths — 3/5.** Systems and data engineering (ingest, QC at scale, contracts, cloud) fit well. Frontier models play only a minor role (optional QC/anomaly models).
- **Biggest risk:** owner incentives (the device can cost an owner the rebate) and DJB adoption.
  - Mitigation: pilot with campuses and RWAs that need proof, and position this as a verification service for DJB's restoration drive.
  - Second risk: cost. Verified retail is ≈ ₹10.1k per node, above my earlier ₹6k target, though still about ¼ of the ₹38k CGWA-style DWLR.
- **One-line pitch:** *"Delhi has paid ₹204 crore for rainwater harvesting it never checked. JalSakshi puts a low-cost IoT witness in every recharge pit and turns each storm into measured, auditable recharge evidence — measured, not self-declared."*

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 03:25 IST — Phase 0 done; Phase 1 fan-out running
- Read PLAYBOOK, seeded brief and `_briefs/innovatex.txt`; wrote *Phase 0 — what we must show* (criteria → evidence).
- Launched research workers r1a, r1b, r2, r3, r4, r5 (data), r6, and a First-Principles physics agent. r6 and r1b failed with transient model errors (408, request too large); relaunched r6 and split r1b into r1b1 (CGWA) + r1b2 (Delhi rules/tariffs) with small-fetch, write-incrementally instructions.
- Early finding (r5, live query): India-WRIS ArcGIS REST `arc.indiawris.gov.in/server/rest/services/NWIC/GroundwaterLevel_Stations/MapServer/0` returns 382 stations with `state_name='Delhi'`, from CGWB and "Delhi SW GW", some flagged telemetric (DWLR). Notes: `components/data-ingest/research_sources.md`.
- Assumptions (no user available): ground the pitch in Delhi (zonal venue); target the user's team as ≤4 students; prototype budget unconstrained but BOM must be credible for a student build.

### 2026-10-04 07:55 IST — Morning package (lean mode)
- **Context:** the network was saturated and most sub-agents failed with 408 errors. The Supervisor declared lean mode at 05:49, so I did the work myself.
- **Data (real).** India-WRIS dataset API + ArcGIS layer: 382 Delhi stations; 483,253 readings for 2015–2026, from 185 telemetric stations. ERA5 rain and pressure via Open-Meteo. Fetcher: `components/data-ingest/fetch_delhi.py`; snapshot in `eval/data/`.
- **Real-data profile** (`eval/realdata_profile.py` → `eval/results/realdata_profile.json`):
  - readings arrive every 6 h;
  - only 46 of 185 telemetric stations reported in 2026;
  - 23.3 % of readings are exactly zero, and 17.4 % of 6-hourly slots are missing;
  - 76.3 % of readings are usable;
  - median monsoon-2025 water-level rise: 2.51 m (n=79 stations);
  - South district median depth to water: 38.4 m below ground.
- **Written:**
  - `research/landscape.md` (cited; what ships today; candidate comparison; component innovation scan);
  - `architecture/components.md` and contracts v0.3.0 (17 JSON schemas);
  - ADR 001 (six hats + independent rubber-duck antithesis);
  - `deliverables/zonal-pitch.md` and `deliverables/prototype-plan.md` (both DRAFT v1);
  - selection memo v1 (4.0/5).
- **Decision:** the hero is RechargeMeter, recharge verification for Delhi's RWH rebate regime. The antithesis changed the framing in three ways:
  - one hero, not three roles;
  - "infiltrated volume with uncertainty", not "aquifer recharge";
  - no claims to identify illegal borewells.
- **Not done yet, next:** simulator, verifier and evaluator numbers; the autoresearch loop; the dashboard.

### 2026-10-04 08:05 IST — Walking skeleton end-to-end (simulated pits, real rain)
- **Built:**
  - C0 `components/twin_simulator/simulate.py`: linear-reservoir pits, 1-minute step, exact mass balance, with clogging, blocked inlets, bucket fakes, noise and dropouts. Driven by real ERA5 hourly Delhi rain.
  - C5 baseline `components/recharge_verifier/verifier.py`.
  - Frozen evaluator `components/recharge_verifier/autoresearch/eval.py`.
- **Baseline, dev split** (monsoon 2025, 40 simulated pits, imperfect registry):

  | Metric | Value |
  |---|---|
  | Event MdAPE (primary) | **11.8 %** |
  | Event APE p90 | 95.8 % |
  | Season-total error | 61.0 % |
  | Coverage | 0.975 |
  | Clogging precision / recall | 1.0 / 1.0 |
  | Fake recall | 0.2 (n=10) |
  | False-implausible rate | 0.307 |
  | Blocked recall | 1.0 (n=1) |

  Logged in `results.tsv`. The holdout run (monsoon 2024) is in progress.
- **Reading:** volumes are already decent per event. The weak spots are the verdicts: fake detection, and honest pits flagged as implausible. That is the first ratchet target, ideas 1 and 6 in `program.md`.

### 2026-10-04 08:20 IST — First autoresearch ratchet on C5 (kept, holdout-confirmed)
- **Diagnosis** of the baseline (`/tmp` script, not committed):
  - All false "implausible" verdicts were light-rain events (<1 mm, ~0.05 m³). The rule "rain <1 mm ⇒ implausible" is physically wrong: 0.6 mm × 300 m² × 0.75 ≈ 0.14 m³.
  - Big multi-storm events underestimated infiltration about 2×. A single log-linear k fit spanned disjoint recession limbs and flattened the slope.
- **Fixes**, each run as a separate ablation in parallel temp trees and logged in `components/recharge_verifier/autoresearch/results.tsv`:
  - exp1: within-limb (fixed-effects) k fit;
  - exp2: rain-consistency implausibility test;
  - exp3: one-minute jump test against rain in ±5 min.
- **Results (simulated pits, real rain):**

  | Split | Event MdAPE | Season-total error | Fake recall | False-implausible | Clogging P/R |
  |---|---|---|---|---|---|
  | Dev | 11.8 % → **3.9 %** | 61 % → 4.8 % | 0.2 → 1.0 | 0.31 → 0 | — |
  | Holdout (monsoon 2024) | 10.3 % → **3.0 %** | 65 % → 7.6 % | 0.3 → 1.0 | 0.25 → 0 | 0.63/1.0 → 0.83/1.0 |

- **Honesty note:** the simulator and verifier share the linear-reservoir model, so these numbers are an upper bound. Evaluator v2 (model mismatch) comes next; the physical rig is the real test.
- Corrected the ledger and README timestamps to the actual run times.

### 2026-10-04 10:05 IST — Ratchet v2 (not kept), primary-source fixes, verified BOM, then PAUSE
- **Ratchet v2 on C5:**
  - Built the frozen evaluator v2 (drain law h^β with β ~ U(0.5, 1.5), plus a gauge factor and lag). The kept v1 verifier scores 13.03 % there; v1 on the original evaluator is unchanged at 3.902 %.
  - Three drain-law variants reached 4.86–5.28 % on v2 but worsened the original evaluator by 15–31 % relative. Under the keep rule in `program.md`, none was kept; all are logged in `results.tsv`. The verifier was reverted to v1, and the last candidate is saved under `autoresearch/candidates/`.
- **Primary-source checker** (`research/primary-source-checks.md`):
  - **CGWB 2025 (primary):** Delhi's stage of extraction is 92.10 %; 10 of 34 tehsils are over-exploited (337.44 km²).
  - The 2023 figure (617.25 km²) was higher, so the deck now says "still over-exploited", not "worsening".
  - ₹204.46 cr, the RWH rules and the NGT borewell figures are confirmed at secondary sources only.
- **BOM price verifier** (`research/bom-prices.md`): verified retail is ≈ ₹10,100.67 per node (MS5837 path), ₹13,829.67 with a rain gauge. My earlier "< ₹6,000" target was wrong and is corrected in the deck, pitch, plan and memo.
- Deck draft and figures added: `deliverables/zonal-deck.md`, `deliverables/make_figures.py`, `deliverables/figures/*.png` (map coordinates fixed).
- **Supervisor PAUSE at 09:55:** saved everything, no jobs running. Resume point is under *Now*.
