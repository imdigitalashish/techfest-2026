# EV Challenge 2 · Green Auto India (automotive LCA database) — Thought Node

> Journal for `ev-c2-green-auto-lca/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** 4 — walking skeleton + eval done for case study 1; morning-package docs landing (LEAN MODE per Supervisor 05:51 — no sub-agents until lifted).
- **Headline (committed run, `python3 eval/eval.py`, commit a2cfc31, n=10,000, seed 20261004):** engine replicates ICCT 2021 Table 1 (Indian scooters) at **0.06 % MAPE**. India 2026, CEA FY2025-26 average grid: petrol scooter **62.9 g CO2e/km [90 %: 57.6–69.0]**, 2.9 kWh e-scooter **39.7 [36.9–42.8]** → **36.9 % lower [29.2–43.8 %]**, P(EV lower) = 1.0. At CEA operating margin: only **14.0 % [3.3–23.5 %]**; at build margin **55.2 %**. EV grid term is CO2-only (no coal upstream) — a stated lower bound.
- **Plan:** (1) morning package (landscape ✓, components+contracts ✓, ADR 001 ✓, memo ✓, Round-1 drafts); (2) after lean mode lifts: independent rubber-duck review of ADR + methodology; per-component research; spike A (ingestion) and B (grid service) ratchets; materials layer (steel/aluminium/battery) via ingestion.
- **Doing:** lead alone, sequentially.
- **Next:** Round-1 methodology + roadmap drafts → push → state-level grid factors (needs state RE generation) → independent Indian benchmarks (SAE 2026, Energy 2025 — UNVERIFIED leads) → E20 petrol, coal-upstream records.
- **Needs from user:** Register by 15 Oct and pick one EV track (after the 12 Oct selection). Team of 2–5: names and skills — ideally one teammate with LCA / environmental-engineering background for jury Q&A.
- **Risks:** jury LCA rigour (ISO 14044 boundaries, allocation, end-of-life method); sparse Indian process data (casting, forging, painting) → explicit proxies + pedigree; only one Indian benchmark so far (which is also an input source — validation is partly circular); network saturation tonight.

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

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | Source registry + fetchers | SourceSpec → Source + raw file | sources.yaml + fetch_sources.sh | | built | % re-fetchable |
| C2 | Factor store + validator | YAML → Record | pydantic schema | | built (23 records, 8 sources) | quote-verification rate |
| C3 | Ingestion / extraction | Document → CandidateRecord | manual transcription | ★A | verifier built + ratchet 1 (0.6875→1.0, FA 0); extractor planned | field F1 vs gold set |
| C4 | Grid-factor service | GridFactorQuery → GridFactor | CEA v22 national records | ★B | national built | reconstruction / back-test error |
| C5 | Product-system builder | VehicleSpec → ProductSystem | case1 YAML (5 scenarios) | | built | % params resolved |
| C6 | Calculation engine | ProductSystem → StageResult | engine.py | | built | replication MAPE (0.06 %) |
| C7 | Uncertainty / sensitivity / DQI | → UncertaintyResult | pedigree lognormal, paired MC | | built | interval calibration |
| C8 | Benchmark harness | → EvalReport | eval/eval.py (frozen) | | built | # benchmarks within ±2 % |
| C9 | Dashboard | EvalReport → HTML | static self-contained HTML | | built | % numbers with provenance |
| C10 | Exporters | Records → openLCA JSON-LD | — | | planned | round-trip import |

## Selection memo
_First version 4 Oct 2026 07:40 IST (lead). Final by 12 Oct. Compare with `ev-c1-infra-map-india/thought_node.md` — the team registers ONE EV track by 15 Oct._
- **Winnability — 4/5.** No open India-specific automotive LCA database or engine found (GitHub search "india life cycle assessment vehicle": no repositories; open engines openLCA/Brightway/carculator are EU-centric — `research/landscape.md`). Our skeleton already replicates the main open Indian 2W benchmark (ICCT 2021) at 0.06 % and exposes an inconsistency in it — the kind of defensibility the statement asks for. Unknown: teams with LCA faculty support.
- **Innovation headroom — 4/5.** Spike A (documents → verified, pedigree-scored records; fail-closed) and spike B (grid factor by state / period / margin) vs the obvious baseline of static global factors. Grid method alone moves the e-scooter saving 14 → 55 % (committed run).
- **Feasibility — 4/5.** Public data only; no GPU needed (M5 Mac; Azure OpenAI for extraction). Engine, eval, dashboard exist on day 1. Build windows: 16 Oct–17 Nov and 26 Nov–15 Dec, nothing user-dependent in 19–25 Nov.
- **Demo strength — 4/5.** Live: ingest a new Indian PDF → a cited record appears with its quote → the scooter result and its data-quality index update; switch charging state / grid method; click any number to see page + quote.
- **Fit with the user's strengths — 4/5.** Data-system design and frontier-model extraction (Azure) are the core; LCA domain depth is the gap → add an environmental/mechanical teammate.
- **Biggest risk:** jury Q&A on LCA rigour (ISO 14044 boundaries, allocation, end-of-life method, non-CO2 gases) and scarce Indian process data. Mitigation: methodology document states every boundary; proxies labelled with pedigree; independent rubber-duck "hostile LCA judge" rehearsal.
- **One-line pitch:** "An open, auditable India automotive LCA database where every number has a page and a quote, an AI pipeline that grows it from Indian public documents, and a grid engine that shows what an EV really saves — by state and by method."

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 02:10 IST — Phase 0 read
Read PLAYBOOK, seeded brief, official statement (`_briefs/ev-infra.txt`). Brief matches the statement (verified: deliverables, R1/R2 weights, dates, rules incl. "synthetic data must be clearly identified", "judged on intelligence, transparency and defensibility ... rather than access to premium or proprietary datasets"). Wrote `architecture/agent-brief.md` (record schema with source/locator/quote/pedigree per number). Session then died at ~03:04 on a model error (network 408s) before any commit.

### 2026-10-04 05:52 IST — Resumed in LEAN MODE
Supervisor directive: no sub-agents, small requests, push every 30 min. Committing skeleton now; doing research myself.

### 2026-10-04 07:40 IST — Morning package built (lean mode, lead only)
- **Data:** opened and transcribed CEA CO2 Baseline v22.0 (Aug 2026: FY2025-26 average 0.675, OM 0.963, BM 0.446 t CO2/MWh; 13-yr series), Lok Sabha USQ 842 (T&D 17.63 % FY2023-24), IPCC 2006 gasoline defaults, UNSD density, ICCT 2021 India 2W briefing (Table 1 + footnote inputs) and fact sheet (Fig. 2 digitized from vector PDF; matches Table 1 to ≤0.03 g/km). 23 records / 8 sources, all with locator + quote or derivation.
- **Learned:** ICCT footnote inputs don't reproduce its Table 1 (scooter 2.0 vs 2.2 L/100 km; e-scooter 4.13 vs 3.7 kWh/100 km, values look swapped) — saving 48.5 % vs published 38.4 %. Grid method dominates EV results; consumption data dominates parameter variance (65 %). Web-search summaries hallucinated ICCT values (claimed 90–100 g/km for petrol scooters; the source's axis tops at 80) — only opened PDFs used.
- **Built:** `components/lca_engine` (pydantic record store, pedigree→lognormal, paired MC, elasticity-weighted DQI, variance-share data-gap ranking; 6 contract tests pass), `data/vehicles/case1_2w_scooters.yaml` (5 scenarios), frozen `eval/eval.py` (results in `eval/results/`), static dashboard `deliverables/dashboard/index.html` (verified in browser: values match engine; what-if break-even 1.138 kg CO2/kWh at generation).
- **Docs:** `research/landscape.md`, `architecture/components.md` + `contracts/contracts.py`, ADR 001, selection memo. Supervisor 07:22 alignment check: agreed with its order; no reply needed.

### 2026-10-04 07:50 IST — First autoresearch loop (spike A gate: quote verifier)
- Frozen `components/ingestion/autoresearch/eval.py`: gold = 16 `verified` records with local PDFs; negatives = the same quotes with one digit changed (32); scalar = found-rate, forced to 0 on any false accept.
- Ledger (`results.tsv`): baseline v0 0.8125 → re-baseline 0.6875 after a **data fix** (OM/BM quotes did not contain their numbers — the eval caught my own transcription weakness) → v1 fragments-in-order **0.9375** (kept) → v2 600-char window: found 16/16 but **accepted a perturbed number** → scalar 0, reverted → v3 3-line table window **1.0**, FA 0/32 (kept). Overfit risk: only one quote uses the fallback; re-check on held-out records as sources grow.
- Dashboard rebuilt with updated provenance; tests 6/6; eval unchanged (replication MAPE 0.06 %).
