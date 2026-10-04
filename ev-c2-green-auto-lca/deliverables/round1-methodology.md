# Round 1 — Methodology document (DRAFT v0.1, 4 Oct 2026)

**Track:** EV Infra & Green Mobility AI Challenge — Challenge 2: *Green Auto India* (India-specific automotive LCA database).
**Team:** _name, Team ID, institution, contacts — to be filled after registration (by 15 Oct)._
**Status of numbers:** every figure below comes from a committed run (`python3 eval/eval.py`, commit a2cfc31, n = 10,000 Monte Carlo draws, seed 20261004) or from a source we opened (listed in §9). Preliminary; not an ISO 14044 critical-reviewed study.

## 1. Problem understanding
Automotive LCAs used for Indian decisions still lean on international inventories that do not reflect India's grid, materials, supply chains, driving or recycling. Two facts from our first week show why this matters:
1. **The grid factor decides the EV answer.** For a 2.9 kWh electric scooter, electricity is 34 of 40 g CO2e/km in our India-2026 run. Using the Central Electricity Authority's FY2025-26 *average* grid factor (0.675 t CO2/MWh) the e-scooter emits **36.9 % less** than a 110 cc petrol scooter; using CEA's *operating margin* (0.963) only **14.0 %**; using the *build margin* (0.446) **55.2 %**. Which factor is right depends on the decision being made — a database must make that choice explicit.
2. **Published numbers are hard to audit.** The open reference for Indian two-wheelers (ICCT, 2021) reports a 38.4 % saving for e-scooters, but its stated inputs reproduce 48.5 %; its table implies 2.0 L/100 km and 4.13 kWh/100 km where the text says 2.2 and 3.7. Without number-level provenance, such gaps go unnoticed.

**Users and decisions.** MHI and ICAT (technology evaluation, scheme design such as PM E-DRIVE, homologation-adjacent sustainability work), OEMs and suppliers (product carbon footprints, material and process choices, ESG/BRSR reporting), researchers (reproducible inventories) and policymakers (fleet-level scenarios).

## 2. Goal and scope (ISO 14040/14044 structure)
- **Goal:** a transparent, extensible India-specific database and engine that estimates life-cycle impacts of vehicles, components and materials, and compares technologies and manufacturing choices.
- **Functional units:** 1 vehicle-km over the vehicle lifetime (vehicle comparisons); 1 kg of material or 1 unit of component (material/component comparisons); 1 kWh of battery capacity.
- **System boundary (cradle-to-grave):** raw materials → material production → component manufacturing → assembly → logistics → use (fuel/electricity production, tailpipe, maintenance) → end of life (reuse, recycling, recovery, disposal). Capital goods included where the source includes them; stated per record.
- **Impact categories:** climate change (GWP100, IPCC AR6 factors as the target basis; records state their own gas basis) first; then particulate matter, acidification, resource use and water via published characterisation factors as the database grows.
- **Modelling choices (explicit, switchable):** attributional by default; consequential-style sensitivity via CEA operating/build margins; end-of-life cut-off by default with avoided-burden as sensitivity; static (FY) and lifetime-average grid factors.

## 3. Database architecture and data-collection framework
- **Unit of data = a cited record.** Each number stores: value, unit, quantity type, gas basis, boundary, geography (IN or IN-state), reference year, technology, source, **locator** (page/table/cell), **verbatim quote**, access date, **pedigree scores** (reliability, completeness, temporal, geographical, technological; 1–5), status (`verified` / `derived` with formula / `assumption` / `synthetic` / `UNVERIFIED`). The loader fails closed: a `verified` record without a quote or a `derived` record without a formula is rejected.
- **Layers:** materials · components · manufacturing processes · energy (grid, fuels) · logistics · use phase · end of life · battery · vehicle templates · method (characterisation, pedigree factors).
- **Storage and versioning:** human-readable YAML in git (every change reviewed and diffable), validated by pydantic schemas; exports to CSV and openLCA JSON-LD (planned) so existing tools can consume it.
- **How new datasets plug in (data-collection framework):** (1) register the source and a fetch script; (2) extract candidate records — manually or with the AI-assisted extractor (spike A) that must return the page and a verbatim quote, which a verifier checks against the document text; (3) review and pedigree-score; (4) merge — contract tests and the benchmark harness run automatically. Suppliers and ICAT can submit records through the same template.

## 4. Calculation engine
- **Product systems** are parameterised: each parameter points to a record id (no free constants), and each life-cycle stage is an expression (e.g. electricity stage = kWh/km × grid factor ÷ (1 − T&D loss)). The engine returns stage-wise results per functional unit.
- **Uncertainty:** each record becomes a lognormal distribution — from the source's stated range when given (e.g. IPCC 95 % intervals), otherwise from its pedigree scores using the ecoinvent/Weidema uncertainty factors (as implemented in Brightway's `pedigree_matrix`). Monte Carlo is **paired**: a record shared by two vehicles is sampled once per draw, so comparisons are not inflated by independent noise.
- **Interpretation outputs:** 90 % intervals, probability that one option beats another, elasticity of the result to every record, an elasticity-weighted **data-quality index** (1 best … 5 worst), the India-specific share of the result, and a **data-gap ranking** (share of variance per record) that tells ICAT which Indian dataset to collect next.

## 5. Validation
- **Replication:** re-compute published Indian LCAs from their stated inputs. First result: ICCT (2021) Table 1 reproduced at **0.06 % mean absolute error** (petrol scooter 60.90 vs 60.9 g CO2e/km; e-scooter 37.54 vs 37.5) using the inputs the table implies; the inputs as printed give 8.96 % error — reported, not hidden.
- **Cross-checks:** the same study's figure (digitized from the PDF's vector drawing) matches the table to ≤ 0.03 g/km.
- **Planned:** independent Indian studies (2025–26 peer-reviewed and SAE papers), held-out benchmarks to calibrate the uncertainty intervals, internal consistency checks (CEA station data reproduce CEA national totals — conventional generation 1,424.19 BU matched exactly).

## 6. Innovation
- **A. Verified-provenance ingestion:** an AI-assisted pipeline that turns Indian public documents (CEA, ministry reports, SEBI BRSR disclosures, EPDs) into records with page + quote, automatically checked against the document — the scalable way to grow a national database without losing auditability. Measured by field-level accuracy against a hand-verified gold set.
- **B. India grid-factor service:** emission factors by region (national → state), period (financial year → vehicle-lifetime average, prospective), method (average / operating margin / build margin) and delivery point (busbar / consumer meter), each with its derivation. Measured by reconstructing CEA's published national values from station data and back-testing year-ahead estimates.
- Plus: number-level provenance in the dashboard, paired uncertainty, and data-gap ranking.

## 7. Preliminary case study — petrol vs electric scooter (India, 2026)
| Scenario (grid factor for charging) | Petrol scooter g CO2e/km [90 %] | E-scooter g CO2e/km [90 %] | EV saving [90 %] |
|---|---|---|---|
| CEA FY2025-26 average | 62.95 [57.59–68.99] | 39.71 [36.90–42.84] | 36.9 % [29.2–43.8 %] |
| CEA operating margin | 62.95 [57.59–68.99] | 54.15 [50.18–58.54] | 14.0 % [3.3–23.5 %] |
| CEA build margin | 62.95 [57.59–68.99] | 28.23 [26.30–30.40] | 55.2 % [49.8–60.0 %] |

Inputs: CEA CO2 Baseline v22.0; T&D losses 17.63 % (FY2023-24, Lok Sabha USQ 842); IPCC 2006 petrol defaults + UNSD density; ICCT (2021) vehicle and battery factors, lifetime and consumption. **Caveats:** the grid term is CO2-only (no coal-mining methane or plant construction yet), so EV values are a lower bound; petrol is modelled as E0 for tailpipe CO2 although India now blends ethanol; vehicle and battery factors are 2021 global values. Parameter uncertainty is driven mostly by real-world fuel and electricity consumption (≈ 65 % of variance) — Indian on-road data is the most valuable next dataset.

## 8. Limitations (stated up front)
Scope for the prototype: two-wheelers first (then 3W, cars, buses); GHG first. Indian process-level data (casting, forging, painting) is sparse — proxies will be labelled with pedigree scores. State-level grid factors from station data are generation-based and ignore inter-state trade unless flow data are added. Prospective factors are scenarios, not forecasts.

## 9. Sources, tools and disclosures
- **Data (opened):** CEA CO2 Baseline Database v22.0 user guide and workbook (2026); Lok Sabha Unstarred Q. 842 (4 Dec 2025); IPCC 2006 Guidelines Vol. 2 Ch. 1; UN Statistics Division Energy Statistics Yearbook 2020 Table II; ICCT Briefing "Fuel consumption standards for the new two-wheeler fleet in India" (Anup & Deo, 2021); ICCT Fact Sheet "Life-cycle GHG emissions of combustion engine and electric passenger cars and two-wheelers in India" (Bieker, 2021); Brightway `pedigree_matrix`.
- **Software:** Python, pydantic, NumPy, PyYAML, pdfplumber, pdftotext; openLCA/Brightway as reference engines. No synthetic data used so far; any synthetic data will be labelled.
- **AI tools:** GitHub Copilot (coding agent) assisted with code and drafting; planned use of large language models (Azure OpenAI) inside the extraction pipeline, always with quote verification and human review.
