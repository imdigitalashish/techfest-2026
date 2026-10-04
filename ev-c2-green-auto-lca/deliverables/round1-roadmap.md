# Round 1 — Implementation roadmap (DRAFT v0.1, 4 Oct 2026)

**From concept to the Grand Finale prototype (16–18 Dec 2026, IIT Bombay).** Companion to `round1-methodology.md`. Day-1 state (4 Oct): cited factor database (23 records, 8 sources), calculation engine with paired Monte Carlo, frozen evaluation harness (ICCT 2021 replication at 0.06 % error), static dashboard and a first two-wheeler case study — all in the repository.

## 1. Development stages and exit criteria
| Stage | Dates | Build | Exit criterion (measured) |
|---|---|---|---|
| 0. Walking skeleton | done 4 Oct | Record schema + validator, engine, Monte Carlo, eval, dashboard, case study 1 (2W) | Replicates ICCT 2021 Table 1 ≤ 1 % (achieved 0.06 %) |
| 1. Data breadth I + Round-1 submission | 5–30 Oct | Energy layer (state T&D, CEA margins, E20 petrol, coal upstream), materials (steel, aluminium, copper, plastics: Indian production routes), battery (cell origin, LFP vs NMC), 2W/3W templates; methodology + roadmap submitted | ≥ 80 cited records across all 8 data layers; ≥ 2 independent Indian benchmarks transcribed |
| 2. Spike A — verified-provenance ingestion | 1–17 Nov | Extractor (rules + LLM) for PDF/XLSX → candidate records with page + quote; verifier; review queue; gold set | Field-level F1 ≥ 0.9 on a ≥ 100-record gold set; 100 % of auto-accepted records have the quote found in the document |
| 3. Spike B — India grid-factor service | 1–17 Nov (parallel) | State generation-based factors from CEA station data + state RE generation; lifetime-average and prospective factors; margins | National reconstruction error ≤ 1 %; year-ahead back-test error reported |
| — Exam freeze | 18–25 Nov | No user-dependent work (IIT Delhi end-semester exams 19–25 Nov) | — |
| 4. Data breadth II + engine v2 | 26 Nov–8 Dec | Components (body-in-white, battery pack, tyres, electronics), processes (casting, forging, machining, moulding, stamping, welding, painting, assembly), logistics (road, rail, coastal), end of life (recycling credits, informal sector); matrix LCI (Brightway-compatible); unit checking; JSON-LD export | 3 vehicle classes (2W, 3W, car) × 3 powertrains (ICE, CNG, BEV) computed; export opens in openLCA |
| 5. Product + demo | 1–15 Dec | Web app (API + dashboard): comparisons, India state map for charging, provenance on click, data-gap ranking, "add a dataset" flow; rehearsal against a hostile LCA-expert jury | Live demo script runs offline in < 10 min; every displayed number has provenance |
| 6. Grand Finale | 16–18 Dec | Live demo + walkthrough of how the prototype evolved from this roadmap | — |

## 2. Data sources by layer (status as of 4 Oct)
| Layer | Planned Indian sources | Status |
|---|---|---|
| Grid electricity | CEA CO2 Baseline Database (v22.0, FY2025-26; station-level workbook), CEA General Review, state RE generation, CEA National Electricity Plan | v22 national values **in DB**; T&D 17.63 % **in DB**; state RE + NEP to do |
| Fuels | IPCC 2006 defaults (in DB); India GHG inventory country-specific factors; ethanol blending (E20) data; refinery disclosures | partial |
| Materials | Ministry of Steel publications, steel and aluminium producers' BRSR/sustainability reports, Indian EPDs | to do (via spike A) |
| Components & battery | OEM/supplier disclosures, peer-reviewed India studies, GREET/BatPaC as labelled proxies | to do |
| Manufacturing processes | Indian plant disclosures (BRSR energy intensity), literature proxies with pedigree | to do |
| Logistics | Indian freight-mode emission factors (road, rail, coastal) from government/peer-reviewed sources | to do |
| Use phase | ICCT India 2W data (in DB); Indian Driving Cycle and on-road consumption studies; maintenance | partial |
| End of life | Vehicle scrappage policy data, recycler disclosures, informal-sector studies | to do |
| Benchmarks | ICCT 2021 (in DB); 2025–26 Indian peer-reviewed and SAE studies | 1 in DB |

Rule for every source: open it, record page/table + quote, score pedigree; label proxies and synthetic data explicitly.

## 3. Tools and technologies
Python 3.11 · pydantic (schemas/contracts) · NumPy (Monte Carlo) · PyYAML + git (versioned database) · pdfplumber/pdftotext (document parsing) · Azure OpenAI (extraction in spike A, behind the quote verifier) · Brightway/openLCA formats for interoperability · static HTML now → FastAPI + lightweight web front-end for the finale · pytest contract tests + frozen eval harness · GitHub for versioning and review.

## 4. Path to the final prototype — what the jury will see
1. Pick a vehicle (e-scooter vs petrol scooter, then 3W/car) → stage-wise results with 90 % intervals and P(one beats the other).
2. Switch the grid method and the charging state → see the saving change and why.
3. Click any number → source, page, quote, pedigree.
4. Drop in a new Indian document → the pipeline proposes records with quotes → accept → results and data-quality index update.
5. Data-gap ranking → which Indian dataset ICAT should collect next.

## 5. Scalability roadmap (beyond the finale)
- **Coverage:** more vehicle classes (3W, buses, trucks), powertrains (CNG, hybrid, hydrogen), and impact categories.
- **Institutional:** ICAT/MHI host the database; OEMs and suppliers submit records through the same template and verifier; versioned releases with change logs.
- **Interoperability:** exports to openLCA/ILCD formats; mapping to international datasets where Indian data are absent (labelled as proxies).
- **Continuous updates:** annual CEA releases ingested automatically; data-gap ranking guides which studies to commission.

## 6. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Sparse Indian process data | Proxies with pedigree scores; data-gap ranking makes the gaps visible and prioritised |
| LLM extraction errors | Fail-closed verifier (quote must be found in the document); human review; gold-set metric |
| Grid-factor method disputes | Show average, operating and build margins side by side; document the decision context for each |
| Jury questions on LCA rigour | Methodology states boundaries, allocation, end-of-life approach and gas basis; rehearsal with a hostile LCA-expert reviewer |
| Team time around exams (19–25 Nov) | Spikes finish by 17 Nov; only polish after 26 Nov |
