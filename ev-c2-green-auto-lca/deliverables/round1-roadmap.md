# Round 1 — Implementation roadmap · v1.0 (4 Oct 2026)

**Green Auto India — EV Infra & Green Mobility AI Challenge, Challenge 2.** Companion to `round1-methodology.md`.
**Team name / ID / leader:** _[to fill after registration on techfest.org, by 15 Oct]_

<!-- headline:begin -->Central results (CEA FY2025-26 average grid, CO2e GWP100 (AR5, as ICCT inputs), partial upstream): e-scooter vs petrol scooter saving **38.1 % (32.0 to 43.2)**; e-Verito-class BEV sedan vs petrol sedan **10.0 % (-10.1 to 25.6)** (90 % intervals; inputs id `e8a4f972e7`).<!-- headline:end -->

## 0. What exists today (demonstrated, 4 Oct) vs what we commit to (December)
| Demonstrated now (in the repository, reproducible) | Committed for the Grand Finale (16–18 Dec) |
|---|---|
| Cited record store: <!-- dbcounts:begin -->127 records (107 verified, 20 derived) from 20 opened sources<!-- dbcounts:end -->; quote-presence verifier + value-in-quote check enforced by tests | Process/exchange layer with co-products and allocation; ≥ 300 records across all 8 data layers |
| Engine: parameterised stages, scenario inheritance, paired Monte Carlo, gas-basis flags | Elementary-flow inventory (CO2/CH4/N2O) characterised with AR6 GWP100; correlation groups |
| Two case studies (2W, sedans) + sensitivities; arithmetic verification vs ICCT (0.06 %, 1.0 %); independent plausibility vs 3 Indian car LCAs | Spike D: one Indian material/component route comparison, end to end, with an independent technical review |
| India grid CO2e (AR6, partial upstream), national, with margins as sensitivities | Harmonized national grid incl. remaining upstream (mining energy, rail, gas) or explicit bounds |
| Static offline dashboard with provenance on every input | Web app (API + dashboard), "add a dataset" flow, rejected-factor demo, offline rehearsal |
| — | Spike A: extractor with frozen document-level dev/test split, field-level F1, reviewer-minutes metric |

## 1. Stages, dates and exit criteria
| Stage | Dates | Build | Exit criterion (measured) |
|---|---|---|---|
| 0. Walking skeleton | done 4 Oct | Record schema, engine, MC, eval, dashboard, two case studies, grid CO2e | Verification ≤ 2 % vs ICCT; docs rendered from the run (drift test) |
| 1a. Decision freeze + D data gate | 4–7 Oct | Freeze the D decision (candidate: a steel part via BF-BOF vs coal-DRI-EAF vs scrap-EAF, or primary vs recycled aluminium; battery cell origin vs Indian pack assembly). Inventory Indian public sources (Ministry of Steel, producers' BRSR/sustainability reports, EPDs). Rule: corporate intensity ratios are not product LCI without boundary checks | Go/no-go memo; if no-go, fallback = harmonized national grid + one material record set, no invented supplier detail |
| 1b. Gold set + baselines | 8–12 Oct | Annotate a diverse document set (CEA, ministry and Parliament answers, BRSR, EPDs, papers); reserve unseen publishers; manual and rule baselines; grid dimensional tests (done) | Frozen dev/test split committed; baseline field-level F1 on dev |
| 1c. One full chain + Round 1 | 13–30 Oct | One source-to-comparison chain for D, including a deliberately rejected incompatible factor; independent technical review; methodology and roadmap submitted by the team leader | Chain reproducible by `eval.py`; review recorded; **Round 1 submitted ≤ 30 Oct** |
| 2. Spike A — extractor | 1–17 Nov | Rules + LLM extractor proposing records with page/cell coordinates and quotes. Checks: quote presence (boundary-aware), value-in-quote, unit/year/locator binding. States: source-anchored → semantically checked → reviewer-approved | Test-split complete-record precision ≥ 0.9 at stated recall; 0 observed false accepts on hard negatives (regression gate, not a guarantee); reviewer minutes per accepted record reported |
| 3. Spike D + data breadth | 1–17 Nov (parallel) | Indian route records (steel, aluminium, battery cell origin), process/exchange layer, EOL models (cut-off, avoided burden, CFF) | D comparison reproduces source intensities (accounting test); P(route X < Y) with paired uncertainty |
| — Integration checkpoint | 17 Nov | Everything merged, tests green, docs rendered | Checkpoint tag in git |
| — Exam freeze | 18–25 Nov | No user-dependent work (IIT Delhi end-semester exams 19–25 Nov) | — |
| 4. Product + rehearsal | 26 Nov–12 Dec | Web app, India map of the national-grid view with labels, "add a dataset" flow; hostile-jury rehearsal | Offline demo < 10 min; every displayed number has provenance |
| 5. Grand Finale | 16–18 Dec | Live demo + walkthrough of evolution from this roadmap | — |

**Stretch (only after the exit criteria above):** 3W (e-rickshaw/e-auto vs CNG auto), buses, state consumption-based grid factors from inter-state flows, prospective grid factors (rolling-origin back-tested), openLCA JSON-LD export with tested round trip, further impact categories.

## 2. Data strategy by layer (sources and status)
| Layer | Indian public sources | Status 4 Oct |
|---|---|---|
| Grid electricity | CEA CO2 Baseline Database v22.0 (FY2025-26; station workbook); CEA General Review; Lok Sabha answers (T&D losses) | CO2 national + margins, CO2e adders (IPCC CH4/N2O, BUR-4 coal-mine CH4), 35 state T&D records |
| Fuels | IPCC 2006 defaults; ICCT India blends; India's BUR/National Communication; ethanol programme data (E20) | Petrol/diesel/CNG WTT+TTW; E20 WTW pending |
| Materials (spike D) | Ministry of Steel; producers' BRSR and sustainability reports; Indian EPDs; peer-reviewed India studies | Gate on 4–7 Oct |
| Components and battery | OEM and supplier disclosures; GREET/BatPaC as labelled proxies | ICCT battery factors (proxy) |
| Processes | BRSR energy intensities; literature with pedigree | Planned |
| Logistics | Indian freight-mode factors (road, rail, coastal) from government sources | Planned |
| Use phase | ICCT India consumption; Indian Driving Cycle; independent studies (TERI, IITG, IITK) | In DB; on-road data is the top data gap (screening importance) |
| End of life | Vehicle Scrapping Policy facilities; battery-waste rules; recycler disclosures; informal-sector studies | Planned |
| Benchmarks | ICCT 2021 (2W, cars); TERI 2026; IIT Guwahati 2025; IIT Kanpur 2023 | 6 studies transcribed |

**Integration approach:** every number enters as a cited record (page + verbatim quote, pedigree, gas basis, allocation, EOL flag). The fail-closed checks run in CI, and results and docs are regenerated from one run (`eval/eval.py` → `eval/render_docs.py` → `eval/check_docs.py`). **Synthetic data:** none so far; any synthetic data will be labelled `synthetic`.

## 3. Tools
Python 3.11 · pydantic · NumPy · PyYAML + git · openpyxl · pdfplumber/pdftotext · Azure OpenAI (extractor, behind the verifier) · Brightway/openLCA formats · FastAPI + lightweight front-end (December) · pytest (contract, dimensional, drift and value-in-quote tests).

## 4. Scalability roadmap (beyond the finale)
- **Coverage:** 3W, buses, trucks; CNG/hybrid/hydrogen; more impact categories.
- **Institutional:** ICAT/MHI-hosted versioned releases; OEM and supplier submissions through the same template and checks; reviewer roles.
- **Interoperability:** openLCA/ILCD exports; mappings to international datasets where Indian data are absent (labelled proxies).
- **Continuous updates:** annual CEA releases ingested by the extractor; the screening-importance ranking guides which Indian studies to commission.

## 5. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Numbers look auditable but are not comparable (biggest risk) | Mandatory harmonization flags; boundary matrix per result; rejected-factor demo; independent technical review in October |
| D's data gate fails | Fallback to the harmonized national grid + material records; no invented supplier detail |
| LLM extraction errors | Fail-closed checks; reviewer approval; hard negatives; frozen unseen test split |
| Grid-method disputes | Average = attributional central; margins as labelled sensitivities; no consequential claim |
| Jury questions on ISO 14044 rigour | Boundary, allocation, EOL and gas-basis sections; independent review before any public comparative claim |
| Exam window (19–25 Nov) | Integration checkpoint 17 Nov; polish only after 26 Nov |
