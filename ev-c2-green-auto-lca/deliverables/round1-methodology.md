# Round 1 — Methodology document · v1.0 (4 Oct 2026)

**EV Infra & Green Mobility AI Challenge (Techfest 2026, IIT Bombay × MHI × ICAT) — Challenge 2: *Green Auto India***
**Team name:** _[to fill]_ · **Team ID:** _[from techfest.org registration]_ · **Institution:** _[to fill]_ · **Team leader (submits):** _[name, email, phone]_ · **Members (2–5):** _[names, programme, role]_

> <!-- headline:begin -->Central results (CEA FY2025-26 average grid, CO2e GWP100 (AR5, as ICCT inputs), partial upstream): e-scooter vs petrol scooter saving **38.1 % (32.0 to 43.2)**; e-Verito-class BEV sedan vs petrol sedan **10.0 % (-10.1 to 25.6)** (90 % intervals; inputs id `e8a4f972e7`).<!-- headline:end -->
>
> Every number below comes from a committed run — `python3 eval/eval.py` in `ev-c2-green-auto-lca/` (harness v2, inputs id `83a80a699b`, n = 10,000 paired Monte Carlo draws, seed 20261004; tables in `eval/results/summary.md`) — or from a source we opened and quote verbatim (§12). Results are **screening-level**: they are not ISO 14044-conformant comparative assertions, and any public comparative claim will first go through independent critical review.

## 1. Problem understanding
India's vehicle LCAs mostly borrow international inventories, but in India the answer depends on Indian facts. Our first two case studies show three things:
1. **Grid electricity is the largest stage of every EV result (contribution), and the grid-accounting method (a scenario choice) moves the answer more than parameter uncertainty within any one method.** On the Central Electricity Authority's FY2025-26 *average* grid (0.675 t CO2/MWh at the busbar; 0.842 kg CO2e/kWh at the meter once combustion CH4/N2O, coal-mine methane and 17.63 % T&D losses are added), a 2.9 kWh e-scooter emits **38.1 % (32.0 to 43.2)** less than a 110 cc petrol scooter (90 % interval in brackets). The same e-scooter saves only **16.2 %** if charging is attributed to CEA's *operating margin*, and **56.4 %** at its *build margin*. For an e-Verito-class electric sedan (19.2 kWh/100 km) the average-grid saving is just **10.0 % (-10.1 to 25.6)**, and at the operating margin it emits **20.5 % more** than petrol.
2. **Published numbers are hard to audit.** Re-computing ICCT's (2021) Indian two-wheeler LCA, its Table 1 stage values are consistent with about 2.0 L/100 km and 4.13 kWh/100 km, whereas its footnote states 2.2 and 3.7. This is a documentation gap, not evidence that ICCT's conclusion is wrong: rounding, a motorcycle/scooter label swap, charging losses or other unstated adjustments may explain part of it. We report both readings, carry the spread as uncertainty, and will ask the authors.
3. **Independent Indian studies disagree in informative ways.** Our ICCT-based CNG sedan (224 g CO2e/km) sits above the two CNG cars in TERI's 2026 rating study (168 and 209 g/km). India-specific inputs (CNG consumption, methane slip, vehicle mass) move such conclusions.

An Indian LCA database therefore has to do more than store more numbers. It must make every number auditable, show which Indian inputs drive a decision, and keep method choices (grid accounting, end of life, gas basis) explicit.

## 2. Users and decisions
| User | Decision | What the system gives |
|---|---|---|
| MHI / ICAT | Technology evaluation, scheme design (e.g. PM E-DRIVE), test and standards work | Comparisons with uncertainty and P(better); grid-method and state sensitivities; data-gap ranking to commission studies |
| OEMs and suppliers | Product carbon footprints, material and process choices, BRSR/ESG | Cited Indian factors, a contribution template, declared-unit results for materials and components |
| Researchers | Reproducible inventories | Versioned open data, page-and-quote provenance, scripts, a verification harness |
| Policymakers | Fleet and grid scenarios | Average vs margin vs prospective grid views, labelled as such |

## 3. Goal and scope (ISO 14040/14044 structure)
- **Goal:** an open, extensible India-specific inventory and engine that estimates life-cycle GHG (later more categories) of vehicles, components and materials, and compares technologies and manufacturing choices, at screening level now and review-ready later.
- **Functional units and reference flows:**
  - *Vehicle comparisons:* 1 vehicle-km of passenger transport by vehicles of the same segment and service, over the same lifetime. **Case 1:** 110 cc petrol scooter vs 2.9 kWh e-scooter, 120,000 km, 1–2 riders, no battery replacement (the ICCT assumption, stated as a limitation). **Case 2:** sedan-segment car (segment-average mass 998 kg) — petrol, diesel, CNG and battery-electric — 165,000 km over 15 years, no battery replacement. Reference flows: one vehicle (glider + powertrain + battery) per lifetime, fuel in L or kg per km, and electricity in kWh per km **at the plug** (charging losses included).
  - *Materials and components:* **declared units** (1 kg of material at the factory gate; 1 component), not functional units, because function depends on the application.
  - *Batteries:* 1 kWh of nominal capacity for cradle-to-gate declared results. Battery comparisons will use lifetime delivered energy (kWh throughput) as the functional unit.
- **System boundary.** The matrix below is generated from the scenario files; "excluded" items are reported, never silently dropped.

| Stage | Case 1 (2W) | Case 2 (cars) | Status |
|---|---|---|---|
| Materials + vehicle manufacture (glider, powertrain) | ✔ (mass × factor) | ✔ (mass × factor) | European proxy factors (ICCT/Ricardo) — Indian route data planned |
| Vehicle end of life / recycling | ✔ inside the production factor (hybrid cut-off / avoided burden, as in source) | ✔ same | Flagged `eol_included`, so no second EOL stage can be added |
| Traction battery manufacture | ✔ | ✔ | 68 kg CO2e/kWh (China/India, NMC622) |
| Battery replacement, second life, recycling | ✘ | ✘ | Excluded — planned (§5) |
| Fuel production (WTT) | ✔ ICCT India blend | ✔ | Includes ethanol share and inherited allocation |
| Electricity generation + T&D | ✔ CEA CO2 + CH4/N2O + coal-mine CH4, ÷ (1 − T&D) | ✔ | Partial upstream: mining energy, coal rail transport, gas supply chain and plant/grid infrastructure excluded |
| Tailpipe (TTW), incl. CNG methane slip | ✔ | ✔ | |
| Maintenance (tyres, fluids, after-treatment) | ✔ | ✔ | Digitized from ICCT; small |
| Charging equipment, roads, logistics to market | ✘ | ✘ | Excluded at screening level; logistics layer planned |

  **Cut-off rule (proposed):** a process may be excluded only if it is estimated, and documented, at < 1 % of the total and is not decision-relevant between the compared options. The cumulative exclusions must stay below 5 %. Exclusions are listed per result.
- **Modelling approach:** attributional by default (CEA weighted-average grid). CEA operating and build margins are reported as **decision sensitivities**, not as a consequential LCA. A consequential model would need charging-time profiles and marginal dispatch and capacity data.
- **Impact assessment and gas basis:** climate change, GWP100. Central results use IPCC AR5 values (CH4-fossil 30, N2O 265) because ICCT's vehicle and fuel factors exist only as AR5 CO2e aggregates; AR6 values (29.8, 273) change the grid factor by < 0.01 %. Moving everything to AR6 requires elementary-flow inventories (roadmap). Every record declares its gas basis (CO2-only, AR5/AR6 GWP100, 20-year methane, unspecified). The engine flags every result whose inputs mix bases. Today the **car case is harmonized** on AR5 GWP100. The **two-wheeler case is not yet harmonized**, because ICCT's 2W production factor uses a 20-year methane horizon; the dashboard labels it a partial indicator. Other impact categories (PM2.5, acidification, resource use) follow once the GHG core is reviewed.

## 4. Allocation policy (multi-output processes)
Hierarchy we apply to new data: (1) avoid allocation by subdivision or system expansion where the co-product system is known (e.g. refinery units, CHP with known heat use); (2) physical causality (mass or energy, by the dominant function); (3) economic allocation, stating the price year, with mass and energy as sensitivities. Every record carries an `allocation` field. Secondary aggregate factors keep the source's choice and are marked `inherited-unspecified` when the source does not state it (today: petrol, diesel and CNG WTT, and battery factors), so reviewers can see where allocation is not under our control. For refinery products, molasses ethanol, steel slag and by-product gases, and CHP, the database will hold process-level records with co-products before any allocation (roadmap stage 4).

## 5. End of life
Three switchable models, never mixed in one result: **cut-off / recycled content** (default; burdens of recycled input, no credit), **avoided burden** (credits for recycling at end of life), and the **EU PEF Circular Footprint Formula** (sensitivity, to align with export-market reporting). The fields are: collection rate, route (formal or informal), process yield, the secondary-material quality ratio, credits and burdens, and second-life allocation for batteries. Current vehicle factors already embed ICCT/Ricardo's hybrid approach and carry `eol_included: true`, so the engine will not add a second EOL stage to them. India-specific data to collect: Vehicle Scrapping Policy registered facilities, battery-waste rules and recycler disclosures, and informal-sector recovery shares.

## 6. Database architecture and data-collection framework
- **Unit of data — a cited record:** value, unit, quantity type, gas basis, boundary, geography (IN or IN-state), reference year, technology, source, **locator** (page/table/cell), **verbatim quote**, access date, **pedigree scores** with scorer and rationale, allocation, `eol_included`, and status (`verified` / `derived` with formula / `assumption` / `synthetic` / `UNVERIFIED`). The loader fails closed: a `verified` record needs a quote, a `derived` record needs a formula, and unknown gas bases or allocation labels are rejected.
- **Today:** <!-- dbcounts:begin -->127 records (107 verified, 20 derived) from 20 opened sources<!-- dbcounts:end --> (per-layer counts in `eval/results/summary.md`; energy includes 35 state T&D-loss records and 31 upstream-grid records), plus 6 benchmark studies (3 of them independent Indian car LCAs).
- **Storage:** human-readable YAML in git (reviewable diffs, versioned releases), pydantic schemas, and a registry-driven fetcher that re-downloads every raw public file. Planned: a process/exchange layer (one process, many flows, co-products) that exports to openLCA JSON-LD.
- **How a new dataset plugs in:** (1) register the source and its URL; (2) propose candidate records with page and quote, manually or with the AI-assisted extractor (§9); (3) the **quote verifier** checks every quote against the document text, failing closed; (4) review and pedigree-score; (5) merge — contract tests and the verification harness run automatically. ICAT, OEMs and suppliers use the same template.

## 7. Calculation engine and uncertainty
- **Product systems** are parameterised: every parameter is a record id (no free constants). Each life-cycle stage is an expression, e.g. electricity = kWh/km × CO2e factor ÷ (1 − T&D loss). Scenarios inherit from a base and override only what changes, so each sensitivity is a one-line difference.
- **Uncertainty:** stated source ranges are used as given (95 % ranges as lognormal, bounds as triangular around the published value, source ambiguity as uniform — e.g. ICCT's 2.0–2.2 L/100 km). Otherwise a pedigree-matrix lognormal is used (ecoinvent/Weidema factors as in Brightway's `pedigree_matrix`; single scorer today, a second reviewer planned). Characterisation factors (GWP) are fixed. Monte Carlo is **paired**: shared records are sampled once per draw, so comparisons report P(option A < option B) without inflated noise. Correlation groups (e.g. one real-world uplift factor shared by all ICE consumption values) are planned.
- **Interpretation outputs:** 90 % intervals; P(lower); elasticities; an elasticity-weighted **pedigree screening score** (1 best … 5 worst), not a validated data-quality rating; the India-specific share of the result; and a **screening importance** (normalized squared Spearman rank correlation, not a variance decomposition) that ranks which Indian data to collect next.

## 8. Verification and validation
- **Arithmetic implementation verification** (not validation, since the same source supplies inputs and targets): ICCT (2021) 2W Table 1 reproduced at **0.06 % mean absolute error**; ICCT (2021) India sedans at **1.0 %** (petrol −0.8 %, diesel −2.3 %, CNG −0.9 %, BEV +0.1 %). The footnote-as-printed variant gives 8.96 %, which is the documentation gap in §1.
- **Independent plausibility band (not validation):** three non-ICCT Indian car LCAs — TERI (2026, 59 vehicles, 150,000 km), IIT Guwahati thesis (2025, 160,000 km), IIT Kanpur report (2023, 200,000 km). Our central petrol sedan (226 g/km) and BEV sedan (204 g/km) fall inside their ranges (184–247 and 156–265 g/km). CNG (224 vs 168–209) and diesel (239 vs one SUV at 272) do not, so we treat these as findings to explain, not to tune away.
- **Planned:** held-out Indian benchmarks for interval coverage (we found no open independent 2W study yet), an openLCA/Brightway cross-check of one case, and dimensional (unit) analysis.

## 9. Innovation (spikes) — honest status
Chosen after two independent reviews (`reviews/`): **A + D are the spikes**, the national grid (B) is a bounded foundation, and harmonization plus honest uncertainty (C) are mandatory practice.
- **A. Evidence-anchored ingestion.** An extractor (to build) proposes records from Indian public documents (CEA, ministry and Parliament answers, SEBI BRSR, EPDs) with page/cell coordinates and quotes. Fail-closed checks (built):
  - quote presence: every fragment verbatim and in order, and a number may not match inside a larger one;
  - value-in-quote: the stored value must appear in its own quote (one documented PDF-text artifact waived).
  Records move through states: source-anchored → semantically checked → reviewer-approved. Current results: <!-- verifier:begin -->quote presence: 107/107 quotes found; 0 observed false accepts in 214 synthetic digit-perturbed negatives (rule-of-three 95 % bound ≈ 1.4 %, not zero); value_in_quote: 104/105 direct, 1 waived with reason, 0 mismatches (verifier v5-fragments-in-order-number-boundaries)<!-- verifier:end -->. Zero observed false accepts is not a guarantee. The ratchet ledger keeps a rejected variant that overfit and failed on held-out records. The innovation we claim is semantic qualification and measured curation effort (reviewer minutes per usable record), not extraction itself — LLM-based LCI extraction already exists (Kumar et al., 2025, *Environ. Sci. Technol.*; Tang et al., 2026).
- **D. One Indian material/component route comparison** (behind a 4–7 Oct source-availability gate). Example: a steel part via BF-BOF vs coal-based DRI-EAF vs scrap-EAF, or primary aluminium (captive coal power) vs recycled, or battery cell origin vs Indian pack assembly — built end to end from Indian public sources, with the boundary checks that stop corporate intensity ratios being used as product inventories.
- **B (foundation). National grid factor** — built: CEA average as the attributional central value; operating and build margins as labelled sensitivities; CO2, or partial-upstream CO2e at AR5 or AR6 GWP100; busbar or meter. The state view is a national generation factor with a state T&D-loss adjustment (0.754–1.30 kg CO2/kWh at the meter), not a state generation mix. State consumption-based and prospective factors are deferred until they can be back-tested.

## 10. Preliminary results (committed run; g CO2e per vehicle-km; 90 % intervals)
<!-- results-table:begin -->
<!-- results-table:end -->

**Reading:** for two-wheelers, the EV advantage is robust to parameter uncertainty and to grid method (always lower). For cars, the answer depends on the vehicle's efficiency and on the grid method: the 2021-era e-Verito-class BEV is not clearly better on today's average grid. The input that matters most is **real-world BEV consumption** (64 % of the screening importance), followed by petrol consumption (25 %). Indian on-road energy-use data is the highest-value next dataset. **Caveats:** legacy 2021 vehicle data (an illustrative "2026-grid" case, not a 2026 fleet claim); partial grid upstream; European production proxies; no battery replacement or second life.

## 11. Limitations (stated up front)
- Prototype scope: 2W and cars first (3W and buses next); GHG first.
- Indian process-level data (casting, forging, painting) is sparse; proxies carry pedigree scores and labels.
- The grid CO2e excludes mining energy, coal transport, gas supply and infrastructure.
- The state view is loss-adjusted national generation, not a state mix.
- Pedigree scores have one scorer; correlations beyond shared records are not yet modelled.
- No independent open 2W benchmark has been found yet.
- Prospective grid factors will be scenarios, not forecasts.

## 12. Sources, tools and disclosures
**Data (opened; full registry with URLs, locators and quotes in `data/sources/*.yaml`):**
- **Grid, losses and coal:** CEA CO2 Baseline Database v22.0 (user guide and workbook, 2026); Lok Sabha Unstarred Q. 842 (4 Dec 2025, T&D losses); Ministry of Coal / Coal Directory of India 2024-25 (mine-type shares); India's Fourth Biennial Update Report (MoEFCC, 2024; coal-mine methane factors).
- **IPCC and statistics:** IPCC 2006 Guidelines Vol. 2 Ch. 1, 2 and 4; IPCC AR6 WG1 Ch. 7 (GWP100); IPCC AR5 WG1 Ch. 8; UN Statistics Division Energy Statistics Yearbook 2020, Table II.
- **ICCT:** Anup & Deo (2021) "Fuel consumption standards for the new two-wheeler fleet in India"; Bieker (2021) India fact sheet; Bieker (2021) "A global comparison of the life-cycle GHG emissions of combustion engine and electric passenger cars".
- **Independent Indian studies:** TERI (2026) "Life Cycle Assessment Based Rating Framework for Four-Wheeler Passenger Vehicles"; IIT Guwahati PhD thesis (2025); IIT Kanpur report (2023).
- **Method:** Brightway `pedigree_matrix`.

**Software:** Python, pydantic, NumPy, PyYAML, openpyxl, pdfplumber/pdftotext; openLCA and Brightway as reference engines. **Synthetic data:** none. Assumed ranges are labelled `assumption` or noted in the record. **AI tools:** GitHub Copilot coding agents (Claude Opus 5.5; reviewers on GPT-6 models) assisted with code, data transcription (every quote machine-verified) and drafting. Planned LLM use inside the extractor always passes the quote verifier and human review.
