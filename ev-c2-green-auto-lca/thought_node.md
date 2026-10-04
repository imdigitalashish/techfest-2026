# EV Challenge 2 · Green Auto India (automotive LCA database) — Thought Node

> Journal for `ev-c2-green-auto-lca/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** Round-1 package complete (DoD 1–6). Round-1 methodology + roadmap v1.1 are content-final; team details pending registration. Two case studies with uncertainty. ADR v2 (spikes A + D, national grid as foundation). Four independent reviews processed, with 45 items accepted (some in part) and 0 rejected. Next: DONE to Supervisor → pause (batch mode).
- **Headline (rendered from `eval/results/latest.json`):** <!-- headline:begin -->Central results (CEA FY2025-26 average grid, partial upstream, inputs id `91a3e4ce38`, n = 10000 paired Monte Carlo draws, seed 20261004): the legacy-data sedan case is harmonized: GWP100-AR5 — e-Verito-class BEV vs petrol sedan saving **10.0 % (-10.1 to 25.6)**, P(lower) 0.81 (not decisive). The scooter calculation gives **38.1 % (32.0 to 43.2)** lower emissions in a **partial, mixed-basis GHG indicator** (GWP100-AR5, GWP20(CH4), unspecified), not yet a harmonized GWP100 comparison.<!-- headline:end -->
- **Plan:** DONE to Supervisor → **pause** while the user reviews. On reactivation: spike-D data gate (taxonomy-band fallback already sourced) and the gold set (roadmap stages 1a/1b).
- **Doing:** lead. Reviewer sessions done and idle: engine/claims (gpt-6-sol), Round-1 docs (gpt-6-astra).
- **Next (after reactivation):** D data gate memo (started: Green Steel Taxonomy records) → gold set with unseen-publisher split → one full source-to-comparison chain + independent technical review → Round 1 submission by the team leader (≤ 30 Oct).
- **Needs from user:** register by 15 Oct (EV track fixed at registration; this project is the current EV pick); team of 2–5 — ideally an environmental/mechanical teammate for LCA Q&A; team name, Team ID, institution and contacts for the Round-1 header; access to ISO 14040/14044 text (IIT Delhi library or BIS) for the methodology's ISO references.
- **Risks:** auditable-looking but non-comparable numbers (mitigated by harmonization flags, boundary matrix, rejected-factor demo); D's data gate; jury LCA rigour; exam window 19–25 Nov.

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
- 2026-10-04 — Every number is a `Record` with source, locator, verbatim quote, pedigree and status; the loader fails closed (`components/lca_engine/greenauto/db.py`). No free constants in product models.
- 2026-10-04 — Case study 1 = 110 cc petrol scooter vs 2.9 kWh e-scooter (India's fleet is 2W-heavy; ICCT 2021 gives an open, stage-wise Indian benchmark to replicate).
- 2026-10-04 — Central consumption values = those implied by ICCT Table 1 (2.0 L/100 km, 4.13 kWh/100 km), not its footnote (2.2 / 3.7): they reproduce the published table and are conservative for the EV claim; footnote values kept as a scenario.
- 2026-10-04 — Grid factor shown three ways (CEA average / operating margin / build margin), never one silent choice.
- 2026-10-04 — Spikes: A verified-provenance ingestion (C3), B India grid-factor service (C4) — [ADR 001](architecture/adr/001-spike.md).

- 2026-10-04 — Central case = CEA FY2025-26 average grid on CO2e (combustion CH4/N2O + India BUR-4 coal-mine methane, partial upstream), AR5 GWP100 to match ICCT inputs; CO2-only, operating margin and build margin are labelled sensitivities (CO2-only = upper bound on the EV saving).
- 2026-10-04 — Consumption values ICCT's sources disagree on enter decision scenarios as uniform source-ambiguity ranges, not as reverse-engineered single values.
- 2026-10-04 — Replication against ICCT is called arithmetic implementation verification; independent Indian car LCAs (TERI 2026, IITG 2025, IITK 2023) are a plausibility band, not validation.
- 2026-10-04 — ADR 001 v2: spikes A (evidence-anchored ingestion with semantic checks) + D (one Indian material/component route comparison, gated 4–7 Oct); B national grid foundation; C harmonization + honest uncertainty mandatory — [ADR](architecture/adr/001-spike.md), [astra review](reviews/2026-10-04-adr001-gpt-6-astra.md).
- 2026-10-04 — Documents render results from one run; `eval/check_docs.py` (in the test suite) fails on drift.

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | Source registry + fetchers | SourceSpec → Source + raw file | sources.yaml + fetch_sources.sh | | built | % re-fetchable |
| C2 | Factor store + validator | YAML → Record | pydantic schema | | built (23 records, 8 sources) | quote-verification rate |
| C3 | Ingestion / extraction | Document → CandidateRecord | manual transcription | ★A | verifier v5 (boundary-aware) + value-in-quote check built; extractor planned | doc-level F1, complete-record precision, reviewer minutes |
| C4 | Grid-factor service | GridFactorQuery → GridFactor | CEA v22 national records | foundation (was ★B) | national CO2 / CO2e (AR5|AR6), margins, state loss adjustment | accounting reconciliation; back-tests before any prospective claim |
| C5 | Product-system builder (+ ★D route comparison) | VehicleSpec → ProductSystem | 2 cases, 15 scenarios, inheritance | ★D | built; D gated 4–7 Oct | % params resolved; D: source-intensity reproduction |
| C6 | Calculation engine | ProductSystem → StageResult | engine.py | | built | replication MAPE (0.06 %) |
| C7 | Uncertainty / sensitivity / DQI | → UncertaintyResult | pedigree lognormal, paired MC | | built | interval calibration |
| C8 | Benchmark harness | → EvalReport | eval/eval.py (frozen) | | built | # benchmarks within ±2 % |
| C9 | Dashboard | EvalReport → HTML | static self-contained HTML | | built | % numbers with provenance |
| C10 | Exporters | Records → openLCA JSON-LD | — | | planned | round-trip import |

## Selection memo
_Final for the morning-after review, 4 Oct 2026 (lead); confirm at the 12 Oct gate. EV C2 is the current EV pick (Supervisor, 09:55) unless the user overrides._
- **Winnability — 4/5.** The engine reproduces the two open ICCT Indian LCAs to 0.06 % and 1.0 % (arithmetic verification) and sits inside the range of three independent Indian car LCAs for petrol and BEV. Each number traces to a page and a quote, checked automatically. We are not first: TERI (2026) rates 59 vehicles using a commercial teardown database (A2MAC1). Our edge is openness and auditability on public data, which is exactly what the statement rewards.
- **Innovation headroom — 3.5/5.** After the reviews we claim novelty narrowly: evidence-anchored ingestion with semantic checks and measured curation effort (A), plus an Indian material/component route comparison (D). LLM LCI extraction exists (Kumar et al. 2025; Tang et al. 2026), and premise maps India.
- **Feasibility — 4/5.** Public data, no GPU; skeleton, two cases, eval, dashboard and drift-checked docs exist on day 1; D has a fallback.
- **Demo strength — 4/5.** Switch the grid method or state and watch the scooter or car result move. Click any number to see its page and quote. Ingest a document and watch a factor get rejected for incompatibility. The case results are judge-relevant: the 2W saving is robust, while the sedan result depends on vehicle efficiency and grid method.
- **Fit with the user's strengths — 4/5.** Data systems + frontier-model extraction; LCA domain depth needs a teammate.
- **Biggest risk:** auditable-looking but non-comparable numbers (gas basis, boundary, allocation) under jury Q&A. Mitigated by harmonization flags, the boundary matrix, three reviews, and an independent technical review planned 13–18 Oct.
- **One-line pitch:** "An open India automotive LCA database where every number carries its page and quote, machine-checked; it shows which Indian data decide a vehicle or material choice, and grows from Indian public documents with measured reviewer effort."

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 02:10 IST — Phase 0 read
Read PLAYBOOK, seeded brief, official statement (`_briefs/ev-infra.txt`). Brief matches the statement (verified: deliverables, R1/R2 weights, dates, rules incl. "synthetic data must be clearly identified", "judged on intelligence, transparency and defensibility ... rather than access to premium or proprietary datasets"). Wrote `architecture/agent-brief.md` (record schema with source/locator/quote/pedigree per number). Session then died at ~03:04 on a model error (network 408s) before any commit.

### 2026-10-04 05:52 IST — Resumed in LEAN MODE
Supervisor directive: no sub-agents, small requests, push every 30 min. Committing skeleton now; doing research myself.

### 2026-10-04 07:34 IST — Morning package built (lean mode, lead only)
- **Data:** opened and transcribed CEA CO2 Baseline v22.0 (Aug 2026: FY2025-26 average 0.675, OM 0.963, BM 0.446 t CO2/MWh; 13-yr series), Lok Sabha USQ 842 (T&D 17.63 % FY2023-24), IPCC 2006 gasoline defaults, UNSD density, ICCT 2021 India 2W briefing (Table 1 + footnote inputs) and fact sheet (Fig. 2 digitized from vector PDF; matches Table 1 to ≤0.03 g/km). 23 records / 8 sources, all with locator + quote or derivation.
- **Learned:** ICCT footnote inputs don't reproduce its Table 1 (scooter 2.0 vs 2.2 L/100 km; e-scooter 4.13 vs 3.7 kWh/100 km, values look swapped) — saving 48.5 % vs published 38.4 %. Grid method dominates EV results; consumption data dominates parameter variance (65 %). Web-search summaries hallucinated ICCT values (claimed 90–100 g/km for petrol scooters; the source's axis tops at 80) — only opened PDFs used.
- **Built:** `components/lca_engine` (pydantic record store, pedigree→lognormal, paired MC, elasticity-weighted DQI, variance-share data-gap ranking; 6 contract tests pass), `data/vehicles/case1_2w_scooters.yaml` (5 scenarios), frozen `eval/eval.py` (results in `eval/results/`), static dashboard `deliverables/dashboard/index.html` (verified in browser: values match engine; what-if break-even 1.138 kg CO2/kWh at generation).
- **Docs:** `research/landscape.md`, `architecture/components.md` + `contracts/contracts.py`, ADR 001, selection memo. Supervisor 07:22 alignment check: agreed with its order; no reply needed.

### 2026-10-04 07:50 IST — First autoresearch loop (spike A gate: quote verifier)
- Frozen `components/ingestion/autoresearch/eval.py`: gold = 16 `verified` records with local PDFs; negatives = the same quotes with one digit changed (32); scalar = found-rate, forced to 0 on any false accept.
- Ledger (`results.tsv`): baseline v0 0.8125 → re-baseline 0.6875 after a **data fix** (OM/BM quotes did not contain their numbers — the eval caught my own transcription weakness) → v1 fragments-in-order **0.9375** (kept) → v2 600-char window: found 16/16 but **accepted a perturbed number** → scalar 0, reverted → v3 3-line table window **1.0**, FA 0/32 (kept). Overfit risk: only one quote uses the fallback; re-check on held-out records as sources grow.
- Dashboard rebuilt with updated provenance; tests 6/6; eval unchanged (replication MAPE 0.06 %).

### 2026-10-04 08:02 IST — Spike B baseline: grid-factor service + state T&D
- Parsed the Lok Sabha USQ 842 annex into **35 state/UT T&D-loss records** (`data/fetch/parse_state_td_losses.py`, FY2023-24; quotes verified by the spike-A verifier: held-out re-check 51/51 found, 0/102 false accepts).
- `greenauto/grid.py`: GridFactorQuery → GridFactor with record ids + derivation. Logic: CEA says India runs one integrated grid (since Dec 2013), so the generation mix is national; the state part is T&D loss. Meter factors range **0.754 (Goa) – 1.300 kg CO2/kWh (J&K + Ladakh, 48 % losses incl. commercial)**; refuses CO2e until coal-upstream data exist. 10/10 tests pass.
- Dashboard: charging-state selector in the what-if (verified in browser: All India 36.9 % saving = engine; Goa 41.2 %).
- DB now 58 records (51 verified, 7 derived), 8 sources.

### 2026-10-04 09:45–10:40 IST — Active batch: second case study, three independent reviews, CO2e central case
- **Inbox/Supervisor:** 09:40 resume (lean); 09:55 active batch (EV C2 = current EV pick; ≤ 2 sub-agents); 10:08 cross-model reviews; 10:15 sessions-only delegation. All followed. The ADR reviewer was started via `task` just before the sessions directive and allowed to finish.
- **Case study 2 (cars):** ICCT 2021 India sedans (petrol/diesel/CNG/BEV) reproduced at 1.0 % (arithmetic verification). Fact-sheet Figure 1 digitized (stage totals within 0.2 g/km of the quoted totals).
- **Reviews:**
  - Hostile LCA jury (rubber-duck): 15/15 accepted.
  - gpt-6-astra on ADR 001: 8/8 accepted → ADR v2 (A + D spikes, B national foundation), verifier v5 + value-in-quote check.
  - gpt-6-sol on engine, eval and claims (child session): 8/8 accepted, all 5 claims confirmed, clean checkout reproduced.
- **Data:**
  - India grid CO2e via a data agent: 31 upstream records (IPCC CH4/N2O, BUR-4 coal-mine methane, Coal Directory shares, AR5/AR6 GWPs) + 5 composition records → 0.693 kg CO2e/kWh busbar, 0.842 at the meter.
  - Three independent Indian car LCAs via a benchmarks agent: TERI 2026, IITG 2025, IITK 2023; 42 quotes verified. No open independent 2W study found.
- **Learned:**
  - The verifier's fuzzy fallback overfit: it failed held-out data (accepted perturbed numbers), so it was removed.
  - `0.675` matched inside `10.675` until v5.
  - AR5 and AR6 must not be pooled as "harmonized".
  - The e-Verito-class BEV sedan is not clearly better than petrol on today's average grid (10.0 %, interval spans 0); the 2W saving is robust (38.1 %).
  - Ledger and journal timestamps typed by hand were partly wrong; corrected from git commit times. Times now come only from `date`/git.
- **Docs:** methodology + roadmap v1.0, landscape, ADR v2, memo final; result blocks rendered from `latest.json`; `check_docs.py` in the tests.

### 2026-10-04 10:43–11:06 IST — Round-1 docs cross-model review (gpt-6-astra) applied → v1.1
- **Review (child session, gpt-6-astra, max):** 63.5/100 as submitted; 2 critical, 9 major, 3 minor. All 14 accepted (presentation trim in part) — `reviews/2026-10-04-round1-docs-gpt-6-astra.md`.
- **Bugs it found that tests missed:**
  - §10's results table was empty: adjacent markers defeated the render regex, and the drift check passed it.
  - The EOL flag was not enforced.
  Both fixed and covered by tests, plus a non-empty-block check.
- **Added:**
  - CO2-only panel (average / operating margin / build margin), so the grid method is compared on one basis;
  - transmission-only loss sensitivity (car BEV saving rises to 20.4 %, 3.1 to 33.9);
  - battery-replacement sensitivity (car 5.8 %, scooter 35.5 %);
  - roadmap roles R1/R2/R3 with hour estimates;
  - D fallback backed by the Green Steel Taxonomy;
  - vivas 27–28 Nov respected; feature freeze 10 Dec;
  - synthetic-data statement rendered; licences on all sources; duplicate CEA entry merged; `requirements.txt`.
- **Headline policy:** the harmonized sedan result leads. The scooter number always carries "partial, mixed-basis GHG indicator".
- **Supervisor 10:53:** gazette date checked against the PDF (notification 23 Dec 2024; release 12 Dec 2024 per steel.gov.in) and recorded. Spike D parked until reactivation.
