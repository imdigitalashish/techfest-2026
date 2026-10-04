# Round 1 — Implementation roadmap · v1.1 (4 Oct 2026)

**Green Auto India — EV Infra & Green Mobility AI Challenge, Challenge 2.** Companion to `round1-methodology.md`.

> **Release gate:** team name, Team ID, institution, leader contact and members must be filled by the team (registration closes 15 Oct; only the leader uploads, once, by 30 Oct). Not submittable until then.

<!-- headline:begin --><!-- headline:end -->

## 0. Demonstrated now vs committed vs conditional
| Demonstrated (4 Oct, reproducible with `bash eval/run_all.sh`) | Committed for the Grand Finale (16–18 Dec) | Conditional / stretch (only if the gate or exit criteria above it pass) |
|---|---|---|
| Cited record store (<!-- dbcounts:begin --><!-- dbcounts:end -->); quote-presence + value-in-quote checks in the tests | One Indian steel decision chain: Green Steel Taxonomy bands on one cited component mass (always), **or** a source-qualified route pair (if the D gate passes) | Route pair BF-BOF vs coal-DRI-EAF vs scrap-EAF with plant/product data |
| Engine: parameterised stages, scenario inheritance, paired Monte Carlo, gas-basis flags, EOL double-counting guard | One process with explicit co-product allocation; one EOL approach (cut-off) | Avoided burden and Circular Footprint Formula (only with compatible parameters) |
| Two case studies with grid-method, loss, battery-replacement and fuel sensitivities; arithmetic verification vs ICCT (0.06 %, 1.0 %); context from 3 independent Indian car LCAs | Extractor evaluated on unseen publishers against manual and rule baselines (§1, stage 2 metrics) | 300+ records across all eight layers; AR6 elementary-flow inventory (needs sources that report CH4/N2O separately) |
| National grid CO2e (partial upstream) with margins as sensitivities | Web app + offline demo with provenance on every input, and a "rejected incompatible factor" moment | State consumption-based or prospective grid factors (with back-tests) |

## 1. Roles, capacity and critical path
**Roles:**
- **R1 — data and software lead** (team leader): engine, extractor, app.
- **R2 — LCA and methods lead** (teammate to recruit): boundaries, allocation, EOL, pedigree reviews, the D decision.
- **R3 — data collection** (optional teammate): annotation, Indian sources.

The plan works with **R1 + R2 alone**. Hours are planning estimates, not measurements.

| Stage | Dates | Owner | Est. hours | Build | Exit criterion (measured) |
|---|---|---|---|---|---|
| 0. Walking skeleton | done 4 Oct | R1 | — | Schema, engine, MC, eval, dashboard, two cases, grid CO2e, three independent reviews | Verification ≤ 2 %; docs rendered from the run; drift test green |
| 1a. Decision freeze + D data gate | 5–7 Oct | R2 (R1 support) | 10 + 4 | Freeze the D decision; inventory Indian steel evidence on the taxonomy boundary (NISST certificates, producer EPDs/BRSR mapped to scope, Ministry of Steel publications). Rule: corporate intensity ratios are not product inventories | Go/no-go memo in `research/notes/spike-d-data-gate.md` |
| 1b. Gold set + baselines | 8–12 Oct | R1 + R3 | 12 + 8 | Annotate a diverse document set; reserve unseen publishers; timing protocol; manual and rule baselines | Frozen dev/test split committed; baseline scores on dev |
| — Selection gate | 12 Oct | Supervisor/user | — | Confirm EV track; register by 15 Oct | Registration done |
| 1c. One full chain + Round 1 | 13–18 Oct chain; 19–30 Oct submission | R1 + R2 | 15 + 10 | One source-to-comparison chain for D (or the fallback), including a deliberately rejected incompatible factor; independent technical review; leader uploads | Chain reproducible by `run_all.sh`; review recorded; **upload ≤ 30 Oct** |
| 2. Extractor | 1–15 Nov | R1 | 25 | Rules + LLM proposals with page/cell coordinates; checks; reviewer queue | On unseen publishers: complete-record recall ≥ 0.6 at precision ≥ 0.9, document-macro, failures counted; reviewer minutes per usable record vs manual |
| 3. D chain + process + EOL | 1–15 Nov | R2 | 20 | Steel chain; one allocated process; cut-off EOL model with its guard tests | D reproduces source intensities (accounting test); P(option A < B) reported |
| — Integration checkpoint | 16–17 Nov | R1 + R2 | 6 | Everything merged, tests green, docs rendered | Tag in git |
| — Exams and vivas | 18–28 Nov | — | 0 | No owner-dependent work (exams 19–25 Nov, vivas 27–28 Nov) | — |
| 4. App + rehearsal | 29 Nov–10 Dec | R1 (R2 rehearsal) | 20 + 6 | Web app, "add a dataset" flow, rejected-factor demo, hostile-jury rehearsal | **Feature freeze 10 Dec**; offline demo < 10 min |
| 5. Grand Finale | 16–18 Dec | team | — | Live demo + how the prototype evolved from this roadmap | — |

**Critical path:** 1a (D decision) → 1c (one chain) → 3 (D + process + EOL) → 16–17 Nov integration → 4 (app). Stage 2 runs in parallel. If 1a is no-go, stage 3 uses the fallback, so the path does not stall.

**D no-go fallback (already backed by opened evidence):** the Ministry of Steel Green Steel Taxonomy bands (< 1.6, 1.6–2.0, 2.0–2.2 and > 2.2 t CO2e per tonne of finished steel) are applied to one cited component steel mass, as labelled sensitivities. The demo then shows how the taxonomy rating of the steel moves a vehicle's footprint; the route-pair comparison is withdrawn from the claims.

## 2. Data strategy by layer
| Layer | Indian public sources | Status 4 Oct | Minimum compatible fields |
|---|---|---|---|
| Grid electricity | CEA CO2 Baseline v22.0 (station workbook); CEA General Review; Lok Sabha answers (losses); BUR-4; Coal Directory | Central + margins + partial-upstream CO2e | Boundary (busbar/meter), gas basis, FY |
| Fuels | IPCC 2006; ICCT India blends; BUR/NC; ethanol programme (E20) | Petrol/diesel/CNG well-to-wheel; E20 pending | Blend share, gas basis, GWP set |
| Materials (D) | Ministry of Steel Green Steel Taxonomy; NISST; producers' EPDs/BRSR; peer-reviewed India studies | Taxonomy thresholds recorded | Taxonomy scope (scope 1 + 2 + limited 3), unit per tonne finished steel |
| Components, battery | OEM/supplier disclosures; GREET/BatPaC as labelled proxies | ICCT factors (proxy) | Chemistry, cell origin, capacity basis |
| Processes | BRSR energy intensities; literature with pedigree | Planned | Reference product, co-products, allocation |
| Logistics | Government freight-mode factors | Planned | Mode, load factor, tkm basis |
| Use phase | ICCT India consumption; Indian Driving Cycle; independent studies | In DB; on-road energy use is the top screening gap | Metering point (plug/battery), duty cycle |
| End of life | Vehicle Scrapping Policy facilities; battery-waste rules; recycler disclosures | Planned | Route, yield, quality ratio, formal/informal share |
| Benchmarks | ICCT 2021; TERI 2026; IITG 2025; IITK 2023 | 6 studies | Lifetime, boundary, GWP set, selection rule |

**Integration and governance:**
- Every number enters as a cited record (page + quote, pedigree with scorer and rationale, gas basis, allocation, EOL flag, licence status of its source).
- Outputs are regenerated in order by `eval/run_all.sh`, and docs fail on drift.
- Planned: source hashes, versioned releases with deduplication by document, review ownership (R2 approves pedigree and boundary fields), and a hosted CI for the existing local tests.

**Synthetic data:** <!-- synthetic:begin --><!-- synthetic:end -->

## 3. Tools
Python 3.11 · NumPy · SciPy · pydantic · PyYAML + git · openpyxl · pdfplumber/pdftotext · pytest (`requirements.txt`) · Azure OpenAI (extractor proposals, behind the checks) · openLCA/Brightway formats (export planned) · FastAPI + lightweight front-end (stage 4).

## 4. Scalability roadmap (beyond the finale)
- **Coverage:** 3W, buses and trucks; hybrid and hydrogen; more impact categories.
- **Institutional:** ICAT/MHI-hosted versioned releases; submissions from OEMs and suppliers through the same template and checks; reviewer roles.
- **Interoperability:** openLCA/ILCD exports; labelled mappings to international datasets where Indian data are absent.
- **Continuous updates:** annual CEA releases through the extractor; screening importance guides which Indian studies to commission.

## 5. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Numbers look auditable but are not comparable (biggest risk) | Gas-basis flags in every table; boundary classes; rejected-factor demo; independent technical review in October |
| D gate fails | Taxonomy-band fallback (above), already backed by an opened official source |
| Extraction errors or low coverage | Pre-declared precision **and** recall on unseen publishers; failures counted; reviewer approval |
| Grid-method disputes | Average = attributional central; margins and a common CO2-only panel as sensitivities; billed-energy loss convention stated |
| Jury questions on ISO 14044 rigour | Boundary, allocation, EOL and gas-basis sections; no public comparative claim before the prescribed critical review |
| Team capacity | Plan works with two people; owner-dependent work avoids 18–28 Nov; feature freeze 10 Dec |
