# ADR 001 — Spike components: (A) verified-provenance ingestion, (B) India grid-factor service

- **Status:** accepted (first version, 4 Oct 2026, lead). Revisit at the 12 Oct selection gate.
- **Context:** Round 2 rewards technical robustness (25 %), data quality & integration (20 %), usability (20 %), innovation (15 %), scalability (10 %). The statement asks for a *database architecture and data-collection framework demonstrating how additional datasets can be incorporated* and judges "intelligence, transparency, and defensibility". Tonight's evidence (`eval/results/summary.md`, commit a2cfc31):
  - Engine replicates ICCT 2021 Table 1 to **0.06 % MAPE** — the calculation itself is not the hard part.
  - For the e-scooter, **grid electricity is 34 of 40 g CO2e/km**, and the *method* of the grid factor moves the EV saving from **14 %** (CEA operating margin) to **36.9 %** (average) to **55 %** (build margin).
  - ICCT's published inputs do not reproduce its own table (saving 48.5 % vs 38.4 %): provenance, not arithmetic, is where credibility breaks.
- **Process caveat:** lean mode (Supervisor 05:51) forbade sub-agents, so the antithesis below was written by the lead, not an independent adversarial agent. An independent `rubber-duck` + `First Prinicipals Agent` review is queued for when lean mode lifts.

## Candidates scored (1–5)
| Candidate | Impact on judged criteria | Novelty vs SOTA | Feasibility by 16 Dec | Measurability | Demoability | Total |
|---|---|---|---|---|---|---|
| **A. Verified-provenance ingestion (C3):** LLM/rule extraction of factors from Indian PDFs/XLSX (CEA, BRSR, EPDs, ministry reports) → candidate records with locator + verbatim quote, auto-verified against the document, pedigree-scored | 5 (is the "data-collection framework"; data quality 20 %, scalability 10 %) | 4 (open LCA tools import curated databases; none extract-and-verify Indian public disclosures) | 4 (PDFs on disk; Azure OpenAI available) | 5 (field-level F1 vs gold set; quote-found rate) | 5 (drop a PDF → new cited record → result updates) | **23** |
| **B. India grid-factor service (C4):** cited EF by region (national → state), period (FY → lifetime average, prospective), method (average / OM / BM / CM), delivery (busbar / meter), gas basis | 5 (dominant term of every EV result) | 4 (state- and margin-resolved Indian factors are not in open vehicle-LCA tools; carculator/premise are European/IAM-based) | 3 (state RE generation + inter-state flows needed; prospective needs CEA NEP) | 4 (reconstruct CEA national values from station data; back-test FY2025-26 from data to FY2024-25) | 5 (India map: same scooter, different state) | **21** |
| C. Calibrated pedigree uncertainty + data-gap ranking (C7) | 4 | 3 (pedigree MC is standard) | 4 | 3 (needs ≥5 independent benchmarks) | 4 | 18 |
| D. BOM-based vehicle model with Indian steel/aluminium routes (C5) | 4 | 2 | 3 | 3 | 3 | 15 |
| E. LLM chat "LCA copilot" over the DB | 3 | 2 | 5 | 2 | 4 | 16 |

## Six Thinking Hats
- **White (facts):** CEA v22 gives station-level CO2 and generation with STATE for FY2017-18..2025-26 (unit rows sum to 1,424.19 BU, matching Annexure-I); RE is national only. T&D 17.63 % (2023-24), state-wise annex exists. ICCT's 2021 India LCA is the only open 2W benchmark opened so far.
- **Red (gut / judges):** ICAT/MHI officials will love "every number has a page and a quote" and "your state's grid changes the answer". A chat bot would worry them.
- **Black (risks):** A — LLM hallucinated numbers (mitigated: never `verified` without quote-in-document match; humans approve). B — state factors ignore inter-state trade (must label "generation-based"; consumption-based needs flow data); prospective factors are projections, not facts. Both — scope creep before the 30 Oct Round 1.
- **Yellow (benefits):** A is literally the scalability answer (how ICAT, suppliers and researchers add data). B moves the headline number more than anything else and is India-specific by construction.
- **Green (alternatives):** hourly/seasonal charging factors (solar-hour charging) via CEA/Grid-India data; BRSR-based supplier-specific factors for steel/aluminium; a public "submit a dataset" pull-request flow with automatic checks.
- **Blue (decision):** Spike A + B; C stays best practice inside the engine (built); D phased in on top of A (material factors come through the ingestion pipeline); E rejected.

## Thesis → antithesis → synthesis
- **Thesis:** The bottleneck for an Indian automotive LCA database is not computation but trustworthy, maintainable Indian data; a pipeline that turns public Indian documents into verified, pedigree-scored records, plus a grid service for the dominant EV term, wins on defensibility and scalability.
- **Antithesis (lead-written):** Judges may want breadth — many materials, processes, vehicles — not a pipeline; LLM extraction can look like a gimmick; state grid factors without trade flows can mislead; and a 0.06 % replication of one study proves arithmetic, not truth.
- **Synthesis:** Use A to *produce* breadth (materials, processes, ELV) visibly during the build — the demo shows both the database (coverage table by layer) and the pipeline that fills it, with a fail-closed verifier. Ship B with explicit method labels and always show the three CEA margins side by side. Validate against more than one independent Indian study before claiming accuracy.

## First principles
An LCA result is Σ (activity amount × emission factor). For Indian vehicles the amounts (km, kWh/km, L/km, kg of material) and the factors (grid, steel, battery) are each uncertain, but **the result is only as credible as its least-traceable large term**. Tonight's numbers say the largest term is grid electricity (EV) / fuel (ICE), and the largest parameter uncertainty is real-world consumption. So: make the large terms India-specific and auditable first (B, plus on-road consumption data), and make adding *any* new term cheap and verifiable (A).

## Consequences
- C3 and C4 get autoresearch ratchets (frozen `eval.py` per spike): C3 → field-level F1 on a gold set of hand-verified records; C4 → national-reconstruction error and FY back-test error.
- Other components stay best practice (pydantic store, parameterised engine, pedigree Monte Carlo, static dashboard → API).
- Round-1 methodology and roadmap present A and B as the innovation; Round-2 demo: ingest a new Indian document live, then switch the scooter's charging state.
