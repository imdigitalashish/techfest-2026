# InnovateX · Theme 1: IoT underground water management — Thought Node

> Journal for `innovatex-t1-groundwater/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 6, deliverables. **ACTIVE again since 10:20 IST, 4 Oct: picked as the InnovateX Delhi-zonal theme.** Both cross-model judges (gpt-6-astra max, grok-4.7 xhigh) chose JalSakshi over T2 DustLedger.
- **Definition of done (Supervisor), by 9 Oct 18:00 IST:**
  1. Final deck ✅ `deliverables/zonal-deck.md` (slides + notes + timing; team details to fill)
  2. Q&A ✅ `deliverables/qa-prep.md` (25 questions)
  3. 60-s offline demo ✅ `deliverables/demo/jalsakshi-demo.html`
  4. Round-2 plan ✅ `deliverables/prototype-plan.md` (verified BOM ₹11,166.18 per node, exam-aware schedule, hardware-teammate tasks)
  5. Second hostile cross-model review of the final deck ⏳ (child session, gpt-6-astra max)
  6. Memo final, journal, push ⏳
- **Doing:** lead + 1 child session (hostile deck review). No `task` sub-agents. A pre-lean r3 research agent is still running; I can't stop it.
- **Next:**
  1. Run the hostile review session.
  2. Mark ACCEPTED/REJECTED in `reviews/`, update `ledger.tsv`, fix the deck.
  3. Message the Supervisor "DONE — slot free".
- **Needs from user:**
  - (a) **Register for the Delhi zonal by 9 Oct** (South Asian University, 10 Oct), and send the team name, Team ID, members and contacts for slide 1.
  - (b) **A hardware teammate**: ~4–6 h/week, 11 Oct–16 Nov, for the node, the pour rig and the power measurements (prototype plan §9).
  - (c) A pilot partner (DJB zone, campus or RWA) and permission to instrument 1–3 pits. A short pilot email or letter would answer the "no committed buyer" attack.
  - (d) Two short interviews with RWH maintenance officers or empanelled service providers.
  - (e) After the zonal, approve parts: ≈ ₹11.2k per node + ₹33.6k gateway + ₹14.5k PPK2.
- **Risks:**
  1. All pit numbers are simulation until the rig exists. The deck leads with 13.1 %.
  2. Probe settle time decides battery vs solar.
  3. Buyer unproven: no pilot letter yet.
  4. ₹204.46 cr is secondary-sourced (HT citing DJB data).
  5. The C7 ticket rule v0 is a heuristic, not yet validated at fleet level.

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
_FINAL v2, 4 Oct 2026, 11:00 IST. **Outcome: picked for the Delhi zonal** by the Supervisor, after independent cross-model reviews (`reviews/`). Scores are 1–5 with one line of evidence each; mean **3.6/5** (v1's 4.0 was too generous on demo and cost)._
- **Winnability — 4/5.** It is specific, local and current, and both judges agreed.
  - Delhi has mandated RWH since 2001 (IE). It paid ₹204.46 cr in rebates in 2017–24 (HT, citing DJB data).
  - Certificates come only after inspection; self-disclosure is still being planned (HT).
  - DJB is restoring 1,000 non-functional government systems (IE).
  - Our India-WRIS analysis adds evidence: 185 telemetric stations, only 46 reporting in 2026, 23 % of readings exactly zero.
- **Innovation headroom — 4/5.** A per-storm drain-rate/clogging verdict plus infiltrated volume ± band turns the rebate rule into evidence. Today there is inspection, or one CGWA DWLR (Acorn) logging twice a day at ≈ ₹38k. Honest accuracy (simulation): 13.1 % stress, 14.5 % with a realistic probe, 3.0 % best case.
- **Feasibility by 1 Dec — 4/5.**
  - One node and a drum pour rig with weighed-water ground truth.
  - Verified BOM ₹11,166 per node.
  - The schedule avoids the 19–25 Nov exams.
  - Needs a hardware teammate.
- **Demo strength — 3/5 now; 5/5 once the pour rig exists.** Today's demo is an offline replay: real Delhi DWLR data plus a simulated pit with tickets.
- **Fit with the user's strengths — 3/5.** Data and systems engineering (ingest, QC at scale, contracts, evaluators) fit; frontier models are marginal.
- **Biggest risk:** no committed buyer yet. Mitigation: target DJB's Phase-I government restorations through its 59 empanelled service providers; verdicts rank inspections; inspectors can override. Second risk: probe power and settle time.
- **One-line pitch:** *"Delhi pays for rainwater harvesting it cannot check. JalSakshi puts a witness in every recharge pit that turns each storm into a drain-rate and infiltration verdict — measured, not self-declared."*

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

### 2026-10-04 11:00 IST — Activated as the InnovateX pick; review fixes; final deliverables
- **Supervisor (10:20):** both cross-model judges picked JalSakshi.
  - Response written: `reviews/2026-10-04-lead-response.md`.
  - Ledger: `reviews/ledger.tsv` has 2 lines. 28 T1 items accepted; the ₹47,389 figure from one item was rejected as not reproducible.
- **Source re-check:** I re-opened HT (21 Apr 2026) and IE myself.
  - HT: self-disclosure "being planned"; 1.5× penalty "may attract"; certificates "issued after inspection".
  - IE: mandatory since 2001; 7,596 of 9,148 government buildings have RWH; DJB to restore 1,000 + build 500 (Phase I, 30 Jun 2026 target); 733 M L/yr is an *estimated* potential; DJB portal planned; 59 empanelled service providers.
- **Sensor fix.** The MS5837-30BA (30 bar) is out; the DFRobot KIT0139 0–5 m probe is in.
  - Price: Rs. 4,254.51 at element14 India, verified with the browser.
  - Datasheet (farnell 3708809): 0.5 % overall accuracy, 12–36 V, IP68.
  - Verified per-node subtotal: ₹11,166.18. The ₹32,428.67 in `bom-prices.md` is corrected (it summed both sensor options).
- **New frozen evaluator v3** (probe offset, drift, quantisation). Kept v1 verifier:
  - holdout 14.5 %, dev 16.0 %;
  - v2 stress holdout 13.1 %.
- **Two auto-zero candidates, not kept** under pre-registered rules:
  - c1 improved v3 to 13.9 % but pushed the v1 evaluator to 4.35 % (> 4.29 bound);
  - c2 improved v3 by only 0.11.
- **Offline demo built and browser-tested.**
  - Fixed two honesty bugs: the ticket text wrongly said "no rain", and noisy tiny-storm clogging alerts were firing.
  - C7 rule v0: volume-weighted clogging index of the last 3 storms ≥ 0.5 m³.
- **Rewritten:** deck (rebate opening, borewells moved to backup, 13 % first, buyer = DJB restorations, inspector override), `zonal-pitch.md` talk track, `qa-prep.md` (25 questions), `prototype-plan.md` (Round-2 plan), selection memo v2 (3.6/5).
