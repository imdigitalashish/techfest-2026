# Round 1 — Methodology document · v1.1 (4 Oct 2026)

**EV Infra & Green Mobility AI Challenge (Techfest 2026, IIT Bombay × MHI × ICAT) — Challenge 2: *Green Auto India***

> **Release gate — not submittable until completed by the team (do not fabricate):** Team name _[ ]_ · Team ID _[techfest.org, registration closes 15 Oct]_ · Institution _[ ]_ · Team leader, the only person allowed to upload: _[name, email, phone]_ · Members (2–5 eligible UG/PG students, one team each): _[names, programmes, roles]_. Leader's upload checklist: these fields completed; this file and the roadmap exported to PDF; disclosures (§12) reviewed; uploaded once, before 30 Oct.

**Summary for the jury.**
- **What:** an open, India-specific automotive LCA database and engine. Every number carries its source page and a machine-checked verbatim quote.
- **What we found:**
  - The grid-accounting choice decides EV comparisons.
  - Published Indian LCAs are hard to audit from their own documentation.
  - Independent Indian studies disagree in ways that only Indian vehicle, material and consumption data can settle.
- **Now:** two case studies (scooters, sedans) with uncertainty and explicit method choices.
- **By December:** the extraction pipeline that grows the database from Indian public documents with measured reviewer effort, plus one Indian material/component route comparison. Both are proposals, not yet proven advances.

> <!-- headline:begin -->Central results (CEA FY2025-26 average grid, partial upstream, inputs id `d337af61e1-dirty`, n = 10000 paired Monte Carlo draws, seed 20261004): the legacy-data sedan case is harmonized: GWP100-AR5 — e-Verito-class BEV vs petrol sedan saving **10.0 % (-10.1 to 25.6)**, P(lower) 0.81 (not decisive). The scooter calculation gives **38.1 % (32.0 to 43.2)** lower emissions in a **partial, mixed-basis GHG indicator** (GWP100-AR5, GWP20(CH4), unspecified), not yet a harmonized GWP100 comparison.<!-- headline:end -->
>
> Every number comes from a committed run — `bash eval/run_all.sh` in `ev-c2-green-auto-lca/` (<!-- manifest:begin -->inputs id `d337af61e1-dirty`, n = 10000 paired Monte Carlo draws, seed 20261004<!-- manifest:end -->; tables in `eval/results/summary.md`) — or from a source we opened and quote verbatim (§12). Results are **screening-level**: they are not ISO 14044-conformant comparative assertions. Any public comparative claim would first need the critical review the standard prescribes; for comparative assertions disclosed to the public we understand this to be a panel of interested parties (our understanding, to be confirmed against the standard text). Intended use: research and decision support, not product certification or ESG compliance claims.

## 1. Problem understanding
India's vehicle LCAs mostly borrow international inventories, but the answer depends on Indian facts. Our first two case studies show three things.
1. **Grid electricity is the largest stage of every EV result, and the grid-accounting choice moves the answer more than input uncertainty does.**
   - **Sedan:** the legacy-data e-Verito-class BEV (19.2 kWh/100 km at the plug) is **10.0 % (-10.1 to 25.6)** lower than a petrol sedan on the CEA FY2025-26 average grid (central, then 5th–95th percentile). The comparison is harmonized on AR5 GWP100, but not decisive: the BEV is lower in about 81 % of paired draws. At CEA's operating margin it emits 20.5 % *more*.
   - **Scooter:** a 2.9 kWh e-scooter emits **38.1 % (32.0 to 43.2)** less than a 110 cc petrol scooter. This is a partial, **mixed-basis** GHG indicator: the scooter production factor uses ICCT's 20-year-methane basis and its maintenance factor has no stated basis.
   - **A like-for-like panel:** average, operating-margin and build-margin rows all on CO2 only (§10). This isolates the accounting method from differences in characterisation and completeness.
   - **Snapshot caveat:** each grid factor is one fiscal year held constant over the vehicle's life. It is not a forecast for a vehicle bought in 2026.
2. **Published numbers are hard to audit.** Re-computing ICCT's (2021) Indian two-wheeler LCA, its Table 1 stage values are consistent with about 2.0 L/100 km and 4.13 kWh/100 km, whereas its footnote states 2.2 and 3.7. This is a documentation gap, not evidence that ICCT's conclusion is wrong: rounding, a motorcycle/scooter label swap, charging losses or other unstated adjustments may explain part of it. We report both readings, carry the spread as uncertainty, and will ask the authors. An independent review confirmed the arithmetic.
3. **Independent Indian studies give context, and some disagreement.** Our ICCT-based CNG sedan sits above the two CNG cars transcribed from TERI's 2026 rating study. Being outside such a range marks a reconciliation task (vehicle, consumption, methane slip?), not a proven model error; we have not yet tested the causes.

So the database must make every number auditable, keep method choices (grid accounting, end of life, gas basis) explicit, and show which Indian inputs drive a decision.

## 2. Users and decisions
| User | Decision | What the system gives |
|---|---|---|
| MHI / ICAT | Technology evaluation, scheme design (e.g. PM E-DRIVE), test and standards work | Comparisons with model-conditional uncertainty; grid-method rows; screening of which data to collect |
| OEMs and suppliers | Material and process choices, product footprints, BRSR/ESG preparation | Cited Indian factors with boundaries; declared-unit results; a contribution template |
| Researchers | Reproducible inventories | Versioned open data, page-and-quote provenance, scripts, a verification harness |
| Policymakers | Fleet and grid scenarios | Average vs margin views, labelled as sensitivities |

## 3. Goal and scope (ISO 14040/14044 structure)
- **Goal:** an open, extensible India-specific inventory and engine that estimates life-cycle GHG (later more categories) of vehicles, components and materials, and compares technologies and manufacturing choices — screening level now, review-ready later.
- **Functional units and reference flows:**
  - *Vehicle comparisons:* 1 vehicle-km over the same lifetime, with service held equivalent (same segment, same use).
  - **Case 1:** 110 cc petrol scooter vs 2.9 kWh e-scooter; 120,000 km; 1–2 riders, no payload difference between options; urban/mixed duty as embodied in ICCT's real-world consumption; no battery replacement (ICCT's assumption, tested as a sensitivity).
  - **Case 2:** sedan segment (segment-average mass 998 kg), petrol, diesel, CNG and battery-electric; 165,000 km over 15 years; no battery replacement (tested).
  - *Reference flows:* one vehicle (glider + powertrain + battery) per lifetime; fuel in L or kg per km; electricity in kWh per km **at the plug**. For the sedan BEV this explicitly includes 15 % charging losses (ICCT). For the e-scooter, inclusion of charging losses is an **assumption**: ICCT's grid factor includes T&D losses but the 2W document does not state where consumption is metered.
  - *Materials and components:* **declared units** (1 kg at the factory gate; 1 component) until functional substitution — grade, lifetime, substitution ratio — is established.
  - *Batteries:* 1 kWh nominal capacity for cradle-to-gate declared results. Battery comparisons will use lifetime delivered energy as the functional unit.
- **System boundary.** Every item has one of four classes: in scope, embedded in an aggregate, assumed absent (tested as a sensitivity), or outside the current screening scope.

| Stage | Cases 1 and 2 | Class |
|---|---|---|
| Materials + vehicle manufacture (glider, powertrain) | mass × production factor (European proxy, ICCT/Ricardo) | In scope (proxy) |
| Vehicle end of life / recycling | inside the production factor (source's hybrid cut-off / avoided-burden treatment) | Embedded in an aggregate (`eol_included`) |
| Traction battery manufacture | capacity × 68 kg CO2e/kWh (China/India, NMC622) | In scope (proxy) |
| Battery replacement | one extra pack: +9.5 g/km for the sedan, +1.6 g/km for the scooter (§10) | Assumed absent; tested |
| Battery second life and recycling | — | Outside current scope |
| Fuel production (well-to-tank) | ICCT India blends (incl. ethanol share, inherited allocation) | In scope |
| Electricity generation + delivery | CEA CO2 + combustion CH4/N2O + coal-mine methane, ÷ (1 − T&D) | In scope, partial upstream |
| Coal mining energy, coal rail transport, gas supply chain, plant/grid infrastructure | — | Outside current scope (not yet bounded) |
| Tailpipe (tank-to-wheel), incl. CNG methane slip | | In scope |
| Maintenance | digitized from ICCT (small) | In scope |
| Charging equipment, roads, logistics to market | — | Outside current scope |

  **Cut-off rule (proposed policy, not an ISO threshold).** An item may be excluded only after a documented screen shows it is below 1 % of the total, and cumulative exclusions are below 5 %; both are measured on the GHG total of the option being compared, considering mass and energy too. **The current screening cases do not yet demonstrate compliance with this budget.** Their intervals cover sampled input uncertainty, not unresolved exclusions, replacement assumptions or alternative boundaries.
- **Modelling approach.** Attributional by default (CEA weighted-average grid). Margins are labelled decision sensitivities, not a consequential LCA; a consequential model would need charging-time profiles and marginal dispatch and capacity data.
- **Delivery losses.** The central case grosses up by all-India T&D losses of 17.63 %, which include commercial (unbilled) losses: an explicit convention that allocates system emissions to billed electricity. A transmission-only sensitivity (3.12–4.24 %) gives a lower bound on physical losses.
- **Impact assessment and gas basis.** Climate change, GWP100. Central results use IPCC AR5 values (CH4-fossil 30, N2O 265), because ICCT's vehicle and fuel factors exist only as AR5 CO2e aggregates. AR6 values (29.8, 273) change the grid factor by < 0.01 %; moving everything to AR6 needs elementary-flow inventories (conditional roadmap item). Every record declares its gas basis, and the engine flags results that mix bases: the **sedan case is harmonized on AR5 GWP100**, while the **scooter case is mixed** and labelled so wherever it appears. Other impact categories follow once the GHG core is reviewed.

## 4. Allocation policy (multi-output processes)
For new data:
1. Avoid allocation by subdivision or system expansion where the co-product system is known (refinery units, CHP with known heat use).
2. Otherwise allocate on an underlying **physical relationship**, which must be explained (e.g. energy content for fuels from one refinery unit). Picking mass or energy is not itself a demonstration of physical causality.
3. Otherwise use economic allocation with a stated price year, and test physical bases as sensitivities.

Every record carries an `allocation` field. Aggregate factors keep the source's choice and are marked `inherited-unspecified` when the source is silent (today: petrol, diesel and CNG well-to-tank, and battery factors). Process-level records with co-products are roadmap stage 3.

## 5. End of life
**Current cases** keep the source's embedded recycling treatment and add no separate EOL stage. `eol_included` records this, and the engine **rejects** any scenario that adds an EOL stage to a product whose factors already include end of life (tested). **Planned:** selectable end-of-life models — cut-off/recycled content (intended default), avoided burden, and the EU PEF Circular Footprint Formula only if its parameters and compatible boundaries are available. Fields: collection rate, formal/informal route, process yield, secondary-material quality ratio, credits and burdens, battery second-life allocation. Indian data to collect: Vehicle Scrapping Policy facilities, battery-waste rules and recycler disclosures, informal-sector recovery shares.

## 6. Database architecture and data-collection framework
- **Unit of data — a cited record:**
  - the number: value, unit, quantity type, gas basis, boundary, geography (IN or IN-state), reference year, technology;
  - its evidence: source, **locator** (page/table/cell), **verbatim quote**, access date;
  - its quality and method: **pedigree scores** with scorer and rationale, allocation, `eol_included`;
  - its status: `verified` / `derived` with formula / `assumption` / `synthetic` / `UNVERIFIED`.
  The loader fails closed: a `verified` record needs a quote, a `derived` record needs a formula, and unknown gas bases or allocation labels are rejected.
- **Today:** <!-- dbcounts:begin -->128 records (107 verified, 21 derived) from 19 opened sources<!-- dbcounts:end -->, plus 6 benchmark studies (3 of them independent Indian car LCAs). Per-layer counts are in `eval/results/summary.md`.
- **Storage:** human-readable YAML in git (reviewable diffs, versioned releases), pydantic schemas, and a registry-driven fetcher that re-downloads every raw public file. Licence status is recorded per source: most public documents state no licence, so we store only extracted values and short attributed quotations, never redistribute the documents, and keep source hashes and versions on the roadmap.
- **How a new dataset plugs in:**
  1. Register the source and its URL.
  2. Propose candidate records with page and quote, manually or with the planned extractor (§9).
  3. Automatic checks: quote presence and value-in-quote (§9).
  4. Review and pedigree-score.
  5. Merge: the local test suite runs the contract, dimensional, value-in-quote and document-drift tests (hosted CI is planned).
  ICAT, OEMs and suppliers use the same template.

## 7. Calculation engine and uncertainty
- **Product systems** are parameterised: every parameter is a record id, so there are no free constants. Each life-cycle stage is an expression, e.g. electricity = kWh/km × CO2e factor ÷ (1 − T&D loss). Scenarios inherit from a base and override only what changes. Inherited parameters no longer used are dropped.
- **Input distributions** — modelling choices, not measured Indian population distributions:
  - stated 95 % ranges use a **two-piece lognormal** whose median is the published value and whose 2.5th/97.5th percentiles are the stated bounds (an assumption, not an IPCC distribution fit);
  - stated bounds without a shape use a triangular distribution around the published value;
  - conflicting published readings use a uniform range (e.g. ICCT's 2.0–2.2 L/100 km) — this does not make either reading a measurement;
  - otherwise a pedigree lognormal (ecoinvent/Weidema factors as in Brightway's `pedigree_matrix`, one basic factor of 1.05).
  - GWP factors are fixed.
  - **Known gaps:** most pedigree rationales are still blank, there is a single scorer, and correlations beyond shared records are not modelled. Justifying the dominant priors and adding a second reviewer are scheduled.
- **How to read results.**
  - *Central* estimates use the listed point inputs.
  - *Intervals* are the 5th–95th percentiles of 10,000 **paired** draws: shared records are sampled once per draw.
  - *P(lower)* is the fraction of draws in which the alternative is lower.
  These are not empirically calibrated coverage guarantees and omit structural choices, which appear as separate rows. The central value need not equal the draw median. Example: CNG's methane-slip range (60–1,000 mg/km, its upper end the China value ICCT cites) makes the central +0.9 % saving coexist with a negative median saving and P(lower) ≈ 0.31.
- **Screening outputs:** elasticities; an elasticity-weighted **pedigree screening score** (not a validated data-quality rating); the share of the footprint from stages whose dominant emission factor is Indian; and a **screening importance** (normalized squared Spearman rank correlation, not a variance decomposition and not a value-of-information calculation). For the sedan, real-world BEV consumption dominates (~64 %), then petrol consumption (~25 %).

## 8. Verification and context
- **Arithmetic implementation verification** — not validation, because the same source supplies inputs and targets, and for the table-implied scooter inputs the agreement is partly built in:
  - ICCT (2021) two-wheeler table reproduced at 0.06 % mean absolute error;
  - ICCT (2021) India sedans at 1.0 %;
  - the footnote-as-printed variant gives 8.96 %, which is the documentation gap in §1.
  An independent reviewer reproduced all scenario summaries.
- **Context from heterogeneous published estimates (not validation):**
  - *Rows transcribed:* 8 of TERI's (2026) 59 vehicles (rows transcribed by our benchmark agent across powertrains; not a random sample, and no selection rule was recorded — to be documented and extended), plus IIT Guwahati thesis (2025, 160,000 km) and IIT Kanpur report (2023, 200,000 km) rows. These differ in vehicles, lifetimes, boundaries and characterisation (TERI AR6, IITK AR5-like, IITG not transcribed).
  - *Where we fall:* our petrol and BEV sedans fall inside the transcribed ranges; CNG (2 TERI vehicles from 1 study) and diesel (1 SUV) do not.
  - *What that means:* inclusion is not evidence of accuracy, and exclusion is a reconciliation task.
- **Planned:** reserved compatible cases for later held-out checks; an openLCA/Brightway cross-check of one case; dimensional tests (one exists for the grid adder).

## 9. Innovation — what we will test (honest status)
Chosen after independent reviews (`reviews/`):
- **Spike A — evidence-anchored ingestion.** An extractor (to build) proposes records from Indian public documents (CEA, ministry and Parliament answers, SEBI BRSR, EPDs) with page/cell coordinates and quotes.
  - *Fail-closed checks (built):* every quote fragment must appear verbatim and in order, with number boundaries respected; the stored value must appear in its own quote (one documented PDF-text artifact waived). These do not yet bind unit, field or year — that is planned.
  - *Current results:* <!-- verifier:begin -->quote presence: 107/107 quotes found; the verifier accepted 0 of 214 synthetic digit-perturbed regression cases (clustered, reused and not sampled from deployment errors, so this does not estimate or bound the deployment false-accept rate); value_in_quote: 104/105 direct, 1 waived with reason, 0 mismatches (verifier v5-fragments-in-order-number-boundaries)<!-- verifier:end -->.
  - *Record states:* source-anchored → semantically checked → reviewer-approved.
  - *Hypothesis:* evidence binding and compatibility checks reduce **human minutes per correct, usable Indian LCA record** at a pre-declared precision **and** coverage (complete-record recall ≥ 0.6 at precision ≥ 0.9 on unseen publishers, document-macro reporting, failures counted, adjudicated gold labels, a timing protocol covering setup and corrections). Compared against manual entry, rules, and the extractor alone.
  - *Prior work:* LLM-based LCI extraction already exists (Kumar et al., 2025, *Environ. Sci. Technol.* 59, 22533–22543; Tang et al., 2026, *J. Ind. Ecol.* 30, 1985–2000). We have not established any advantage over them.
- **Spike D — one Indian material/component route comparison**, behind a source-availability gate:
  - *Example:* a steel part at the Government of India Green Steel Taxonomy bands (< 1.6, 1.6–2.0, 2.0–2.2 and > 2.2 t CO2e per tonne of finished steel; scope 1 + 2 + limited scope 3), or a BF-BOF vs coal-DRI-EAF vs scrap-EAF route pair, using Indian evidence on the taxonomy boundary.
  - *Fallback:* if the gate fails, demonstrate the taxonomy bands as labelled sensitivities on one cited component mass, and withdraw the route-comparison claim.
- **Foundation — national grid factor (built):**
  - *Method:* CEA average as the attributional central value, margins as labelled sensitivities.
  - *Gas basis and delivery:* CO2, or partial-upstream CO2e at AR5 or AR6 GWP100; busbar or meter.
  - *State view:* a national generation factor with a state T&D-loss adjustment, not a state generation mix (losses include commercial losses).
  - *Deferred:* state consumption-based and prospective factors, until they can be back-tested.

## 10. Preliminary results (committed run; g per vehicle-km)
<!-- results-table:begin -->
| Case and grid view | Gas basis | Reference (g/km, 90 %) | Alternative (g/km, 90 %) | Saving vs reference: central (5th–95th pct) | P(lower) |
|---|---|---|---|---|---|
| **Car, CEA average grid, partial-upstream CO2e (central)** | harmonized: GWP100-AR5 | Petrol sedan (6.8 L/100 km real-world) 226.2 (202.6–253.8) | Battery-electric sedan (23 kWh, 19.2 kWh/100 km at the plug) 203.5 (174.4–241.6) | 10.0 % (-10.1 to 25.6) | 0.8078 |
| Car, central — diesel | harmonized: GWP100-AR5 | Petrol sedan (6.8 L/100 km real-world) 226.2 (202.6–253.8) | Diesel sedan (6.0 L/100 km real-world) 239.4 (214.4–269.0) | -5.9 % (-24.1 to 9.7) | 0.2817 |
| Car, central — CNG (methane-slip range 60–1000 mg/km skews the draws) | harmonized: GWP100-AR5 | Petrol sedan (6.8 L/100 km real-world) 226.2 (202.6–253.8) | CNG sedan (5.0 kg/100 km real-world) 224.1 (210.6–268.7) | 0.9 % (-24.1 to 11.0) | 0.3057 |
| Car, one battery replacement (structural sensitivity) | harmonized: GWP100-AR5 | Petrol sedan (6.8 L/100 km real-world) 226.2 (202.6–253.8) | Battery-electric sedan (23 kWh, 19.2 kWh/100 km at the plug) 213.0 (183.7–251.4) | 5.8 % (-14.6 to 21.6) | 0.6835 |
| Car, transmission-only losses (lower bound on technical losses) | harmonized: GWP100-AR5 | Petrol sedan (6.8 L/100 km real-world) 226.2 (202.5–253.5) | Battery-electric sedan (23 kWh, 19.2 kWh/100 km at the plug) 180.1 (155.2–212.8) | 20.4 % (3.1 to 33.9) | 0.9722 |
| Car, CO2-only panel — CEA average | MIXED: CO2-only, GWP100-AR5 | Petrol sedan (6.8 L/100 km real-world) 226.2 (202.4–254.1) | Battery-electric sedan (23 kWh, 19.2 kWh/100 km at the plug) 199.2 (170.4–234.5) | 11.9 % (-7.4 to 27.5) | 0.8613 |
| Car, CO2-only panel — CEA operating margin | MIXED: CO2-only, GWP100-AR5 | Petrol sedan (6.8 L/100 km real-world) 226.2 (202.4–254.1) | Battery-electric sedan (23 kWh, 19.2 kWh/100 km at the plug) 266.4 (225.5–316.4) | -17.8 % (-44.8 to 3.9) | 0.0928 |
| Car, CO2-only panel — CEA build margin | MIXED: CO2-only, GWP100-AR5 | Petrol sedan (6.8 L/100 km real-world) 226.2 (202.4–254.1) | Battery-electric sedan (23 kWh, 19.2 kWh/100 km at the plug) 145.9 (126.4–169.6) | 35.5 % (22.2 to 46.3) | 1.0000 |
| Car, CEA operating margin, partial-upstream CO2e | harmonized: GWP100-AR5 | Petrol sedan (6.8 L/100 km real-world) 226.2 (202.6–253.8) | Battery-electric sedan (23 kWh, 19.2 kWh/100 km at the plug) 272.6 (231.4–326.4) | -20.5 % (-48.7 to 1.1) | 0.0609 |
| **2W, CEA average grid (central; partial, mixed-basis indicator)** | MIXED: GWP100-AR5, GWP20(CH4), unspecified | Petrol scooter 110 cc class 64.3 (60.1–69.0) | Electric scooter 2.9 kWh 39.8 (37.7–42.5) | 38.1 % (32.0 to 43.2) | 1.0000 |
| 2W, one battery replacement (structural sensitivity) | MIXED: GWP100-AR5, GWP20(CH4), unspecified | Petrol scooter 110 cc class 64.3 (60.1–69.0) | Electric scooter 2.9 kWh 41.4 (39.2–44.2) | 35.5 % (29.2 to 40.8) | 1.0000 |
| 2W, transmission-only losses | MIXED: GWP100-AR5, GWP20(CH4), unspecified | Petrol scooter 110 cc class 64.3 (60.0–69.0) | Electric scooter 2.9 kWh 35.0 (33.2–37.3) | 45.5 % (40.1 to 49.9) | 1.0000 |
| 2W, CO2-only panel — CEA average | MIXED: CO2-only, GWP100-AR5, GWP20(CH4), unspecified | Petrol scooter 110 cc class 64.3 (60.0–68.9) | Electric scooter 2.9 kWh 38.9 (36.7–41.3) | 39.5 % (33.8 to 44.5) | 1.0000 |
| 2W, CO2-only panel — CEA operating margin | MIXED: CO2-only, GWP100-AR5, GWP20(CH4), unspecified | Petrol scooter 110 cc class 64.3 (60.0–68.9) | Electric scooter 2.9 kWh 52.6 (49.6–55.8) | 18.2 % (10.5 to 25.1) | 1.0000 |
| 2W, CO2-only panel — CEA build margin | MIXED: CO2-only, GWP100-AR5, GWP20(CH4), unspecified | Petrol scooter 110 cc class 64.3 (60.0–68.9) | Electric scooter 2.9 kWh 28.0 (26.5–29.7) | 56.4 % (52.4 to 60.0) | 1.0000 |
| 2W, CEA operating margin, partial-upstream CO2e | MIXED: GWP100-AR5, GWP20(CH4), unspecified | Petrol scooter 110 cc class 64.3 (60.1–69.0) | Electric scooter 2.9 kWh 53.9 (51.0–57.5) | 16.2 % (7.8 to 23.2) | 0.9993 |
| 2W, petrol tailpipe as E0 (no ethanol credit) | MIXED: CO2-only, GWP100-AR5, GWP20(CH4), unspecified | Petrol scooter 110 cc class 66.9 (62.4–71.9) | Electric scooter 2.9 kWh 39.8 (37.7–42.4) | 40.5 % (34.5 to 45.5) | 1.0000 |

_Rendered from `eval/results/latest.json` (inputs id `d337af61e1-dirty`, n = 10000, seed 20261004) by `eval/render_docs.py`. Central = plug-in calculation with the listed point inputs; interval = 5th–95th percentile of paired draws from the stated input distributions; P(lower) = fraction of draws in which the alternative is lower. Model-conditional, not calibrated coverage; structural choices (boundary, grid method, lifetime) are shown as separate rows, not inside the intervals._
<!-- results-table:end -->

**Reading:**
- **Scooter:** the e-scooter indicator is lower in nearly all tested draws and in every grid row, but the comparison is mixed-basis.
- **Sedan:** the result depends on vehicle efficiency and the grid method. The 2021-era e-Verito-class BEV is not decisively better on today's average grid, and is worse at the operating margin.
- **Input that matters most:** real-world BEV consumption has the highest screening importance, so Indian on-road energy-use data is a priority.
- **Caveats:**
  - legacy 2021 vehicle data (an illustrative 2026-grid case, not a 2026 fleet claim);
  - partial grid upstream;
  - European production proxies;
  - snapshot grid held constant;
  - billed-energy loss convention.

## 11. Limitations (stated up front)
- **Scope:** 2W and cars first (3W and buses next); GHG first.
- **Process data:** Indian process-level data (casting, forging, painting) is sparse; proxies carry pedigree scores and labels.
- **Grid:** the CO2e excludes mining energy, coal transport, gas supply and infrastructure. The state view is loss-adjusted national generation.
- **Uncertainty model:** pedigree scores have one scorer and few rationales; correlations beyond shared records are not modelled.
- **Benchmarks:** no independent open 2W benchmark found yet.
- **Exclusion budget:** not yet demonstrated.
- **EOL:** models are planned; only the double-counting guard is implemented.

## 12. Sources, tools and disclosures
**Data (opened; full registry with URLs, licence status, locators and quotes in `data/sources/*.yaml`):**
- **Grid and coal:** CEA CO2 Baseline Database v22.0 (user guide and workbook, 2026); Lok Sabha Unstarred Q. 842 (4 Dec 2025); Coal Directory of India 2024-25 (Ministry of Coal); India's Fourth Biennial Update Report (MoEFCC, 2024).
- **IPCC and statistics:** IPCC 2006 Guidelines Vol. 2 Ch. 1, 2, 4; IPCC AR5 WG1 Ch. 8; IPCC AR6 WG1 Ch. 7; UN Statistics Division Energy Statistics Yearbook 2020, Table II.
- **Steel:** Ministry of Steel, Taxonomy for Green Steel for India (notified 23 Dec 2024).
- **ICCT:** Anup & Deo (2021), two-wheeler fuel consumption briefing; Bieker (2021) India fact sheet; Bieker (2021) global passenger-car LCA white paper.
- **Independent Indian studies:** TERI (2026) LCA-based rating framework for four-wheelers; IIT Guwahati PhD thesis (2025); IIT Kanpur report (2023).
- **Method:** Brightway `pedigree_matrix`.

**Synthetic data:** <!-- synthetic:begin -->No synthetic inventory or vehicle-performance records are used in the case studies. Verifier evaluation uses 214 labelled synthetic digit-perturbed quote negatives generated from source records. Monte Carlo draws simulate the stated uncertainty model and are not measured data. Any future synthetic inventory record will carry status `synthetic`.<!-- synthetic:end -->

**Software:** Python 3.11, NumPy, SciPy, pydantic, PyYAML, openpyxl, pdfplumber/pdftotext, pytest (`requirements.txt`). openLCA and Brightway are reference formats; integration is planned, not installed.

**AI tools:** GitHub Copilot coding agents (Claude Opus 5.5) wrote code, transcribed data (every quote machine-checked) and drafted text. Independent reviews used GPT-6 models (gpt-6-astra, gpt-6-sol). Planned LLM use inside the extractor always passes the checks above and human review.
