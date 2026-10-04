# Landscape — India-specific automotive LCA (Challenge 2: Green Auto India)

_Lead, 4 Oct 2026; updated 10:45 IST after three independent reviews and two data agents (independent benchmarks, grid upstream). Every source below was **opened** on 2026-10-04 unless marked **UNVERIFIED**. Raw copies: `.data/raw/` (gitignored; re-fetch with `data/fetch/fetch_sources.sh`)._

## 1. The problem in one paragraph
Automotive LCAs used in India mostly borrow European/global inventories (the official statement says so explicitly: studies "largely rely on international datasets that may not adequately reflect India's electricity mix, materials, manufacturing processes, supply chains, logistics systems, vehicle-use patterns, and recycling ecosystem" — `_briefs/ev-infra.txt`). The judges (MHI, ICAT) will reward "intelligence, transparency, and defensibility … rather than access to premium or proprietary datasets". So the winning artefact is not the biggest database; it is the **most defensible** one: every number traceable to an Indian public source, with stated quality and uncertainty, and an engine that shows which numbers matter.

## 2. Indian primary data that exists today (opened)
| Layer | Source (opened) | What it gives | Maturity / caveat |
|---|---|---|---|
| Grid electricity | **CEA CO2 Baseline Database v22.0** (User Guide dated Aug 2026; workbook) — cea.nic.in | FY2025-26 weighted average **0.675 t CO2/MWh**, OM 0.963, BM 0.446, CM 0.705 (Table S); 13-year series 0.774 (2013-14) → 0.675 (2025-26) (Annexure-I); unit-level net generation + CO2 for ~4,475 rows with STATE, SECTOR, FUEL, FY2017-18..2025-26 | Official, annual, station-measured. CO2 only, busbar (net of auxiliary), no upstream, no T&D. Station sheet holds conventional plants only (1,424.19 BU = Annexure-I conventional column — checked in code); RE is national-only (310.58 BU). |
| T&D losses | **Lok Sabha USQ 842 (4 Dec 2025)**, citing CEA General Review Nov 2025 | All-India T&D losses **17.63 % (2023-24)**; transmission-only 3.12–4.24 % by region; state-wise annex | Includes commercial losses. |
| Fuel combustion | **IPCC 2006 GL Vol 2 Ch 1**, Tables 1.2/1.4 | Motor gasoline NCV 44.3 TJ/Gg (42.5–44.8), CO2 69,300 kg/TJ (67,500–73,000) | Global default; India-specific values / E20 blend still a gap. |
| Fuel density | **UNSD Energy Statistics Yearbook 2020, Table II** | Motor gasoline 1,351 L per tonne → 0.740 kg/L | Global standard factor. |
| 2W life-cycle benchmark | **ICCT Briefing, Anup & Deo (Aug 2021), Table 1 + footnote 9** | Stage-wise g CO2e/km for 5 Indian 2Ws (FY2020-21) and every input (lifetime 120,000 km; 5.2 kg CO2e/kg vehicle; 69 kg CO2e/kWh battery; 767 g CO2e/kWh electricity; petrol WTT 0.64 / TTW 2.17 kg CO2e/L; consumption values) | Best open India 2W LCA found tonight. **We found internal inconsistencies** (below). |
| Grid upstream (CO2e) | **IPCC 2006 Vol. 2 Ch. 2 & 4; India BUR-4 (MoEFCC 2024); Coal Directory of India 2024-25; IPCC AR5/AR6 GWP tables** (opened by a data agent; quotes machine-verified) | Combustion CH4/N2O, India-specific coal-mine methane (surface 1.18 + 0.15 m3/t; underground degree I–III), opencast share 96.96 % (FY2024-25), GWP100 values | → India grid 0.693 kg CO2e/kWh busbar, 0.842 at the meter (partial upstream: no mining energy, rail, gas supply, infrastructure) |
| Independent Indian car LCAs | **TERI (2026)** LCA-based rating framework (59 vehicles, BoMs from the commercial A2MAC1 teardown database, 150,000 km); **IIT Guwahati PhD thesis (2025)**; **IIT Kanpur report (2023)** | Cradle-to-grave g CO2e/km for Indian petrol, CNG, diesel, hybrid and BEV cars | Used as a plausibility band (petrol and BEV inside; our CNG and diesel outside) |
| 2W/car benchmark | **ICCT Fact Sheet, Bieker (Sept 2021), Fig. 1–2** | India cars and 2Ws, 2021 and 2030 registrations; e-scooter 38–50 % lower (2021), 50–70 % (2030) | Figure values digitized from the PDF vector drawing (`data/fetch/digitize_icct_factsheet_2021.py`). Stages present in both match Table 1 within 0.04 g/km; the figure also shows maintenance (~1 g/km), so its totals are ~1 g/km higher than Table 1. |

**Documentation gap (reproducible, worded without blame):** under a literal reconstruction of ICCT (2021) Table 1, the published stage values do not fully reconcile with footnote 9. They are consistent with about 2.0 L/100 km and 4.13 kWh/100 km, whereas the footnote states 2.2 and 3.7. Rounding, a motorcycle/scooter label swap, charging losses or other unstated adjustments may explain part of the difference, and it is not evidence that ICCT's conclusion is wrong. With the printed inputs the e-scooter saving would be 48.5 % instead of the published 38.4 % (`eval/results/summary.md`, `icct2021_stated`). We report both readings, model the spread as uncertainty, and will ask the authors. Independent review (gpt-6-sol) confirmed the arithmetic.

## 3. State of the art — engines, data, methods
**Open-source LCA engines (GitHub API, 2026-10-04):**
- **openLCA** (GreenDelta) — `GreenDelta/olca-app`, MPL-2.0, 266★, pushed 2026-09-29. Desktop LCA suite; the de-facto open tool for practitioners; imports ecoinvent/ILCD/JSON-LD.
- **Brightway** — `brightway-lca/brightway2-calc` (BSD-3, pushed 2026-10-03) and `brightway25` (pushed 2025-11-27). Python LCA framework (matrix calculation, Monte Carlo). Its `pedigree_matrix` package (pushed 2022-06-16) supplies the uncertainty factors our engine uses.
- **premise** — `polca/premise` (BSD-3, 187★, pushed 2026-09-29): couples integrated-assessment-model scenarios with LCA databases → *prospective* LCA (future grids, future steel). Relevant for the lifetime-average grid problem.
- **carculator** — `Laboratory-for-Energy-Systems-Analysis/carculator` (BSD-3, 54★, pushed 2026-04-29): "prospective environmental and economic life cycle assessment of vehicles" (PSI). **carculator_two_wheeler** exists (same org, pushed 2025-04-06, 0★) — the closest existing open 2W LCA engine; European defaults.
- GitHub search `india life cycle assessment vehicle` returned **no repositories** (2026-10-04). A narrow search cannot establish absence. **premise does map India**: its country-to-IAM-region table maps IN to India regions (opened 2026-10-04), so prospective India-region inventories are possible with ecoinvent + premise. Our claim is narrower: an openly auditable, Indian-public-data corpus with machine-checked evidence.
- **LLM extraction of LCA data exists:** Kumar, Nazemi, Kodamana, Ramteke (2025), "A Large Language Model-based Framework to Retrieve Life Cycle Inventory and Environmental Impact Data from Scientific Literature", *Environ. Sci. Technol.*, doi:10.1021/acs.est.5c05955; Tang, Dreger, Jiang, Malek (2026), "From literature to knowledge graphs: automated extraction and retrieval of LCA data with large language models", doi:10.1007/s44498-026-00135-8. Metadata verified via Crossref; full texts not opened (publisher 403/406), so how they validate extractions is UNVERIFIED.

**Licensed / free datasets (not opened tonight — UNVERIFIED details):** ecoinvent (licensed; has some IN-regional datasets), Argonne GREET (free; US-centric, has battery and vehicle-cycle models), USLCI, EU Environmental Footprint data. We design our schema to *map* to ILCD/openLCA JSON-LD so these can be plugged in, but our demo does not depend on them (the judging rubric rewards public data).

**Methods we adopt (best practice):** ISO 14040/44 phases (goal & scope → LCI → LCIA → interpretation); pedigree-matrix data quality → lognormal uncertainty (Weidema/ecoinvent, as implemented in Brightway `pedigree_matrix`: σ = √Σ ln²Uᵢ / 2); Monte Carlo with **paired sampling** for comparisons; contribution and rank-correlation sensitivity; explicit attributional vs consequential (average vs marginal grid) choice.

## 4. What companies ship today
| Who | What ships (opened) | Where our design borrows / beats it |
|---|---|---|
| **GreenDelta (openLCA)** | Open-source desktop LCA, active weekly releases (olca-app pushed 2026-09-29) | We borrow its data model idea (processes, flows, providers) and will export to openLCA JSON-LD; we beat it on India data + per-number provenance in the UI. |
| **PSI / LEA (carculator, carculator_two_wheeler)** | Open Python vehicle-LCA engines, prospective, with web front-end (carculator) | Closest analogue. We borrow parameterised vehicle models; we differ by Indian data, per-number quote/locator, and a data-gap ranking for ICAT. |
| **Brightway** | Open Python LCA framework used by researchers | We may use bw2calc for the matrix LCI in phase 2; our skeleton uses a simpler parameterised model. |
| **ICCT** | Policy LCAs for India (2021 cars + 2Ws) as PDFs | The reference benchmark; we make it executable and audit it (found the input inconsistency above). |
| **TERI (2026)** | LCA-based star-rating framework for Indian four-wheelers (z-score rating on a 5-point scale; 59 vehicles; BoMs from A2MAC1) — opened | The closest Indian practice. We borrow its cradle-to-grave scope and use it as an independent benchmark. We differ: open public-data inputs with per-number provenance and uncertainty, versus a commercial teardown database |
| **Tata Motors** | Public circularity programme statements, e.g. **Re.Wi.Re (Recycle with Respect)** vehicle scrapping, Prolife reconditioned parts (Tata Motors blog, opened) | End-of-life pathway data partner candidate; we found no Tata product-level LCA numbers on the page we opened. |
| ecoinvent, Sphera (GaBi/LCA for Experts), SimaPro, Catena-X PCF rulebook, OEM product LCAs (e.g. Polestar) | **UNVERIFIED tonight** (not opened) | To verify in the next pass. |

Leads found but **not opened** (UNVERIFIED): SAE paper 2026-26-0235 "Evaluating the Environmental Footprint of Electric Vehicles: A Life Cycle Assessment Approach — Sustainable Mobility India"; SAE 2026-26-0239 "Circularity and LCA: Enhancing Sustainability in the Indian Electric Vehicle Sector"; *Energy* (Elsevier, 2025) S0360544225015531 "Impact of electrification on two-wheelers in India…" (ScienceDirect blocked the fetch); CEEW "Auto net zero studies" press release (18 Jul 2025).

## 5. What this means for our design
<!-- headline:begin -->Central results (CEA FY2025-26 average grid, CO2e GWP100 (AR5, as ICCT inputs), partial upstream): e-scooter vs petrol scooter saving **38.1 % (32.0 to 43.2)**; e-Verito-class BEV sedan vs petrol sedan **10.0 % (-10.1 to 25.6)** (90 % intervals; inputs id `8997a50ce9`).<!-- headline:end -->

1. **Three different statements about the grid:**
   - *Contribution:* electricity is the largest stage of every EV result.
   - *Between-method scenarios:* the grid-accounting choice (CEA average vs operating vs build margin) moves the e-scooter saving from 16 % to 56 % and flips the sign for an e-Verito-class sedan.
   - *Within-method parameter uncertainty:* smaller, and driven mostly by real-world consumption.
   We keep the average grid as the attributional central result and show the margins as labelled sensitivities.
2. **Indian on-road energy use** (2W and BEV cars) is the top parameter data gap by screening importance.
3. **Defensibility needs machine-checked evidence:**
   - the ICCT documentation gap;
   - our own transcription slips caught by the verifier;
   - a reviewer finding that `0.675` matched inside `10.675` before v5.
4. **Independent Indian studies (TERI, IITG, IITK) disagree with ICCT-based values for CNG and diesel cars.** Indian vehicle, material and consumption data, not grid arithmetic, decide many car comparisons. This is why spike D (an Indian material/component route) follows (ADR 001 v2).
5. **Nobody ships an open, India-specific, page-and-quote-auditable automotive LCA corpus.** We found no such resource; that is narrower than "no India LCA exists", and we claim only the narrower point.

## 6. Gaps in this scan (next pass, with sub-agents when the Supervisor lifts lean mode)
Indian steel/aluminium/copper production-route intensities (Ministry of Steel green-steel taxonomy, JSW/Tata Steel/Hindalco/Vedanta BRSR), battery cell origin and chemistry (LFP vs NMC) for Indian packs, Indian Driving Cycle and real-world 2W consumption, E20 petrol, coal-mine methane (upstream of the grid), state-wise RE generation (for state grid factors), ELV/recycling-sector data (scrappage policy, informal sector), CEA National Electricity Plan projections, company PCF methods (Catena-X, PACT), recent peer-reviewed India LCAs (the UNVERIFIED leads above).
