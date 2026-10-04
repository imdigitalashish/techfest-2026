# EV Challenge 1 · EV Infra Map India — Thought Node

> Journal for `ev-c1-infra-map-india/`. Top = current state (rewritten in place); bottom = append-only log. Format and rules: [PLAYBOOK.md](../PLAYBOOK.md).

## Inbox
<!-- The user and the Supervisor write here. Lead: check at the start of every step, act, reply in the Log, then move handled items to "Handled". -->
- _(empty)_

### Handled
- _(none)_

## Now
- **Phase:** ▶ **RESUMED 13:05 IST** (batch slot; Supervisor). Goal: the definition of done below, then message "DONE — slot free". EV C2 is ✅ and the default EV pick, so the final memo must argue C1 for or against honestly.
- **Definition of done (Supervisor 13:05):**
  1. Facts: finish the fact-check (only 1 of 11 claims verified); verify the MoP 2024 norms and PM E-DRIVE targets at primary sources; every Round-1 number verified or marked UNVERIFIED.
  2. Analysis: C9 on VAHAN month-wise data (ensemble + 2026 nowcast with backtest error); C5 with a third source + a multiple-systems estimate with CI; a Maharashtra district gap map on current boundaries (incl. Palghar), SoI-consistent for anything government-facing.
  3. Round-1 methodology + roadmap final: numbers rendered from committed results, a doc-drift check (`eval/check_docs.py`), dashboard checked in a browser.
  4. Cross-model reviews (child sessions): gpt-6-astra max (hostile judge: ADR 001 + Round-1 docs); gpt-6-sol max (code + eval, reproduce headline numbers) → `reviews/` + `ledger.tsv`.
  5. Final memo, journal current, pushed.
- **Doing (lead):** step 1, facts (curl + local extraction, small requests).
- **Next:** month-wise VAHAN fetch → C9 · third charger source (Overture places / AllThePlaces, open licences) → C5 multiple-systems estimate · MH districts incl. Palghar → gap map · render/check docs · reviewers (≤ 2 child sessions) · memo.
- **Rules in force:** child sessions only (≤ 2); never `git stash` or `--autostash`; heavy jobs under `nice -n 10`, one at a time, only when `kern.memorystatus_level` ≥ 30; small requests.
- **Needs from user:** If EV C1 is preferred over C2: register by 15 Oct (track fixed at registration). Team of 2–5: names and skills. Optional: a free Open Charge Map API key.
- **Risks:** (1) supply data: open sources ≈ 8% of official → capture–recapture biased low; (2) registrations ≠ on-road stock; (3) VAHAN markup changes (client self-discovers ids); (4) operator data terms; (5) boundary/basemap compliance; (6) saturated uplink (408s).

## Brief (seeded by the Supervisor, 4 Oct 2026 — verify against the official statement)
- **Competition:** EV Infra & Green Mobility AI Challenge — Techfest IIT Bombay with the Ministry of Heavy Industries (MHI) and the International Centre for Automotive Technology (ICAT). Prize pool ₹2,00,000; top 3 teams per track.
- **Official statement:** [`_briefs/ev-infra.pdf`](../_briefs/ev-infra.pdf) (text: [`_briefs/ev-infra.txt`](../_briefs/ev-infra.txt)).
- **Rounds:** register by **15 Oct** (the track is fixed at registration) → Round 1 concept & roadmap due **30 Oct**: team info + methodology document (problem understanding, analytical approach) + implementation roadmap (data sources, tools, development stages, path to the final prototype) → results **7 Nov** → Grand Finale **16–18 Dec** at IIT Bombay: live demo of the working prototype covering the expected deliverables, plus how it evolved from the roadmap, then jury Q&A.
- **Round 1 judging:** problem understanding & relevance 25% · feasibility & technical soundness 25% · innovation 20% · clarity & completeness of the roadmap 20% · data strategy (sources & integration) 10%.
- **Round 2 judging:** technical & analytical robustness 25% · data quality & integration 20% · relevance & practical usability 20% · innovation 15% · scalability & replicability 10% · presentation 10%.
- **Rules:** team of 2–5 UG/PG students; one track per team; one team per person; open-source tools, models and public data allowed with attribution; synthetic data must be identified and documented; disclose AI tools, third-party software, external datasets and frameworks. The statement says solutions are judged "on the intelligence, transparency, and defensibility of the approach rather than access to premium or proprietary datasets."
- **Round-1 deliverable for the morning package:** `deliverables/round1-methodology.md` + `deliverables/round1-roadmap.md`.

**Challenge 1 — EV Infra Map India:** "Mapping and Integration of Nationwide EV Charger Installations Based on Vehicle Population Using VAHAN Data."
- **Objective:** a data-driven national platform that integrates and maps existing public EV charging infrastructure across India; uses VAHAN registration data to relate EV population to charging availability; identifies underserved areas and charging gaps; estimates future charging requirements by region; supports evidence-based planning by MHI, ICAT, state governments and others.
- **Data layers to consider:** EV population & registrations (VAHAN, state transport data) · existing chargers (public charging apps, charger networks, open databases) · geographic & administrative boundaries · road & mobility network (national highways, major roads, corridors) · demographics & economic activity · electricity infrastructure (public grid/utility info) · context (tourism, logistics, land use, urban development). Public, open, sample or realistic synthetic data allowed — document every source and assumption.
- **Expected deliverables (finale):** functional platform with a unified view of charging infrastructure · interactive national GIS map (chargers, coverage, gaps) · analytical methodology document · charger-requirement estimation & recommendation module for selected states, districts, cities or corridors · decision-support dashboard · demo video for at least one representative geography · scalability roadmap.

**Starting leads** (the Supervisor's pointers — verify each one at the primary source; go well beyond them, newest work first):
- Data: the VAHAN dashboard (registrations by state, RTO and fuel); BEE's public-charging data and the EV Yatra app; Open Charge Map; OpenStreetMap `amenity=charging_station`; charge-point operators' public locators; PM E-DRIVE charger allocations; Ministry of Power charging-infrastructure guidelines (spacing norms as a policy benchmark); boundaries from LGD / DataMeet / Census.
- Methods: cross-source entity resolution to deduplicate chargers; isochrones (OSRM, Valhalla); two-step floating catchment (2SFCA) accessibility; demand modelling from registrations, traffic and points of interest; location-allocation (MCLP, p-median).
- What companies ship: charger-locator apps and siting-analytics products from charge-point operators, utilities and mapping companies.

## Key decisions
- 2026-10-04 — Demo geography = Maharashtra (assumption, reversible; pipeline is state-agnostic).
- 2026-10-04 — VAHAN via plain-HTTP replay of the public dashboard (no browser, no third-party mirror).
- 2026-10-04 — Canonical supply unit = *site* with connector list; official PIB state totals are held-out ground truth, never training data.
- 2026-10-04 — [ADR 001](architecture/adr/001-spike.md): Spike 1 completeness-aware census (C4+C5); Spike 2 forecast + requirement (C9+C11).

## Components
| # | Component | Input → Output | Baseline (existing) | Spike? | Status | Isolated metric |
|---|---|---|---|---|---|---|
| C1 | vahan_ingest | dashboard → RegistrationRecord | manual Excel export | | **real data** | Σ RTO vs state reconciliation error |
| C2 | charger_ingest | sources → ChargerRecord | per-source scrapers | | OSM + official totals | schema-valid share; freshness |
| C3 | charger_normalize | ChargerRecord → canonical | rule tables | | taxonomy drafted | field accuracy on labelled sample |
| C4 | charger_resolve | ChargerRecord[] → Site[] | distance + name match | ★ | planned | pairwise F1 |
| C5 | census_completeness | Site[] → CompletenessEstimate | raw counts | ★ | ground truth on disk | rel. error vs held-out official totals |
| C6 | admin_geo | boundaries → AdminUnit, RTO↔district | Census-2011 shapes | | MH RTO list | % RTOs mapped |
| C7 | ev_stock | registrations → StockEstimate | cumulative regs | | baseline | holdout error |
| C8 | demand_model | stock → DemandEstimate | EVs-per-charger ratio | | planned | rank corr. vs observed sites |
| C9 | adoption_forecast | series → future stock | CAGR | ★2 | data on disk | backtest sMAPE |
| C10 | access_gap | sites + demand → GapRecord | EVs per charger | | **v0 real (state)** | backtest AUC |
| C11 | requirement_siting | gaps → Recommendation | norm-based counts | ★2 | planned (spopt) | demand covered per charger |
| C12 | platform_api | outputs → API | static CSV | | planned | p95 latency |
| C13 | dashboard_map | API → map UI | static choropleth | | planned | planner task time |
| C14 | eval | all → metrics | — | | v0 | — |

## Selection memo
_v1, 4 Oct 08:05 IST — final by 12 Oct. Scores 1–5 with one line of evidence each. Overall **4.2 / 5**._
- **Winnability — 4:** a real national pipeline already runs on day 1: VAHAN (36/36 states, RTO-level) + official state charger totals + OSM. Most teams will have static or synthetic data; ours updates from the public dashboard.
- **Innovation headroom — 4:** measured completeness of the national charger census (open data shows 600 of 29,277 official stations = 2.05%), with CIs validated against held-out official totals, plus segment-aware requirement estimates. Novelty vs. literature still UNVERIFIED (check by 12 Oct).
- **Feasibility — 4:** all inputs are public and small (VAHAN tables are KB-sized); an M5 Mac suffices; Azure is optional. Risk: second and third charger sources need a key or permission.
- **Demo strength — 5:** a national map → Maharashtra drill-down → "where do the next N chargers go, and why" is live-demoable, with every number clickable to its source.
- **Fit with the user's strengths — 4:** large-scale data systems, ingestion, geospatial, cloud. Frontier models are secondary (ER, NL queries), not central.
- **Biggest risk:** supply-side data. Open sources are ~2% complete in India, so district-level supply depends on getting operator/OCM/UEI feeds; fallback is calibration to official state totals.
- **One-line pitch:** India's first completeness-aware EV charging census. We fuse every public charger source, measure what is still missing, and tell each district how many chargers of which type it needs, and where, with an evidence trail for every number.
- **Headline real numbers (from [`eval/results/state_gap_baseline.csv`](eval/results/state_gap_baseline.csv)):** 10,550,090 BEV registrations in VAHAN till today (`ELECTRIC(BOV)` + `PURE EV`, 36 states/UTs); 2,356,971 in CY2025 = 8.05% of all CY2025 registrations; 360 BEV registrations per official public charging station nationally (29,277 PCS, PIB 1 Aug 2025); BEV registrations per PCS run from 152 in Karnataka to 1,085 in Bihar and 1,123 in Assam.

## Log
### 2026-10-04 01:50 IST — Seeded by the Supervisor
Folder, brief and journal created. The lead session starts Phase 0.

### 2026-10-04 05:55 IST — Phase 0–1 under network saturation
- Phase 0 done: brief, judging weights and deliverables read from `_briefs/ev-infra.txt`.
- Launched 9 research sub-agents (methods, India data/policy, companies, social, OSS/data, India EV parameters, benchmarks, policy norms); 7 died on model-side "408 Timed out reading request body" (portfolio-wide network saturation). Two original agents are still running; told them to wrap up.
- **VAHAN spike succeeded.** The public dashboard (`vahan4dashboard/.../reportview.xhtml`) lists "All Vahan4 Running States (36/36)" and "All Vahan4 Running Office (1468/1469)". Plain HTTP replay of the JSF/PrimeFaces AJAX (state → RTO cascade, axis selection, Refresh `j_idt65`, export `groupingTable:xls`) returns full pivot tables as .xlsx. Validated: CY2025 State × Fuel, 36 rows; Andaman row sums to its TOTAL (9,658). EV fuel labels: `ELECTRIC(BOV)`, `PURE EV` (+ `PLUG-IN HYBRID EV`, `STRONG HYBRID EV`). Code: `components/vahan_ingest/vahan_client.py`.
- Open Charge Map API returns 403 without a key → use OSM `amenity=charging_station` (Overpass) as the open charger source tonight.
- Decision (assumption, reversible): demo geography = **Maharashtra** (largest e-4W market, Mumbai–Pune–Nashik corridors, state EV Policy 2025); pipeline stays state-agnostic.
- Switched to LEAN MODE per Supervisor.

### 2026-10-04 08:05 IST — Morning package v1 (Lean Mode)
- **Real data, reproducible:** VAHAN national pulls (State × Fuel for Till-Today and CY2020–2026; 36 states × vehicle class × fuel) and Maharashtra RTO tables (34/61 offices so far), plus OSM India chargers (600 features) and official state-wise PCS parsed from PIB 2151390 (36 states, sum 29,277 ✓) and PIB 2118894 (BEE, 26,367 ✓).
- **Baseline v0 (C10 state level):** 10,550,090 BEV registrations till today; 360 per official PCS nationally; worst large states Assam 1,123, Bihar 1,085, UP 792; best Karnataka 152. Hypothesis: e-rickshaw-heavy states are over-flagged by the naive ratio → segment-aware demand (C8) is required.
- **Found and fixed:** the PIB pages contain each table twice, which doubled the totals → dedupe plus a sum check against the stated totals. The baseline's summary JSON was stale at 08:05 (fixed 08:25, see next entry).
- Wrote research/landscape.md (only pages opened tonight; leads marked UNVERIFIED), architecture/components.md + contracts (pydantic + JSON Schemas), and ADR 001 (six hats, thesis/antithesis/synthesis, scores; the independent adversarial review is pending: no sub-agents in Lean Mode).

### 2026-10-04 08:25 IST — VAHAN redeploy handled; baseline summary corrected
- At ~07:28 the dashboard's JSF auto-ids shifted (state dropdown `j_idt34` → `j_idt37`, Refresh `j_idt65` → `j_idt75`), and the resumed Maharashtra fetch silently got 0 RTOs. The client now discovers widget ids from the page by their labels, and the fetcher never overwrites a good RTO list with an empty one. The Maharashtra fetch resumed (35/61 offices at 08:25).
- `eval/results/baseline_summary.json` regenerated; it now agrees with the CSV and the memo: 36/36 states matched; 10,550,090 BEV registrations till today; 2,356,971 in CY2025 (8.05%); 29,277 official PCS; 360.4 BEV per PCS; OSM 600 = 2.05% of official, 31.8% with operator, 7.8% with socket tags.

### 2026-10-04 08:45 IST — Second charger source + Spike 1 v0 (real numbers)
- **Second source without a key:** the Open Charge Map per-POI export is organised by country. A sparse clone of `data/IN` gives **1,872 India POIs** (export commit 2026-04-22). Status ids: 1,836 × 50, 16 × 100, 14 × 30, 5 × 150, 1 × 75 (labels per OCM reference data, UNVERIFIED). All POIs have DataProviderID 1 (OCM contributors). Code: `components/charger_ingest/fetch_ocm.py`.
- **C4 baseline (mutual nearest neighbour):** OSM 600 × OCM 1,872 → 71/81/83/93/111 matches at 50/100/150/250/500 m. Only 13.3% of the 150 m pairs have name similarity ≥ 60 → a hand-labelled pair set is needed before claiming F1.
- **C5 baseline (two-source Chapman, per state, scored against held-out official PCS from PIB 2151390):** national union = 2,385 sites = **8.15%** of 29,277. For the 5 states with ≥ 3 matches, median |relative error|: **union 0.901 → Chapman 0.697**. Kerala: Chapman 1,613 ± 204 vs official 1,392 (+16%). Delhi −73%, Karnataka −70%, Maharashtra −83%, Tamil Nadu −45%. Reading: both open sources capture the same "easy" sites (positive dependence, heterogeneous catchability) → next: covariate/stratified estimators, more sources, calibration. Results: `eval/results/census_v0_*`.
- **Data-quality finding:** 156 OCM POIs have a free-text state that contradicts their coordinates (e.g. an EESL station at Nava Raipur, Chhattisgarh, labelled "Odisha") → C3 must validate by point-in-polygon, never trust text fields.
- Supervisor tip noted (CEA v22 station-level workbook with a STATE column; T&D losses 17.63% from Lok Sabha USQ 842, both via `ev-c2-green-auto-lca/data/sources/sources.yaml`) → candidate inputs for the grid-context layer (C11).
- The `sota-methods` research agent finished: `research/sota-methods.md` (21.6 KB, condensed; claims to be fact-checked). Its novelty finding: no published capture–recapture / multiple-systems estimation on EV charger databases, and no EV-charger-specific entity resolution (searched by the agent; spot-check pending).

### 2026-10-04 09:10 IST — First auto-research loop (C5, spike 1): real ledger
- Set up `components/census_completeness/autoresearch/`: `program.md`, a **frozen** `eval.py` (DEV = 12 states scored leave-one-state-out against official PCS; HOLDOUT = 11 states, lead-only), `results.tsv`. Only `estimator.py` changes.
- 7 hypotheses (dev median |ln(est/official)|; keep if < best − 0.02):
  - two-source Chapman r = 150 m: 2.987 (first baseline);
  - union only: 3.362;
  - r = 50 m and r = 500 m: 2.987 (no change; most states have < 3 matches);
  - **calibration on ln(VAHAN BEV registrations) alone: 0.349 → kept, holdout 0.417**;
  - + ln(union): 0.334; + ln(Chapman): 0.333 (both inside the noise margin → not kept).
- **Finding (changes the spike):** with today's two sparse open sources (8% of official), capture–recapture is far off (~20× low for the median state), and open-data counts add almost no information beyond EV demand. The census spike therefore needs denser lists (operator feeds, UEI) before multiple-systems estimation can work. Meanwhile a demand-calibrated small-area model (±42% median at state level) is the honest fallback for district-level supply estimates. ADR 001's gate criterion (C5 relative error < 25% for states with ≥ 2 sources) is **not met yet**; revisit after adding a third source.

### 2026-10-04 09:25 IST — National map v0 (real data), verified in a browser
- `components/dashboard_map/build_map.py` → self-contained `dist/index.html` (0.8 MB, MapLibre). Layers: state choropleth of BEV registrations per official station (all 36 states joined); 2,472 OSM + OCM sites; top-10 underserved ranking. Popups show VAHAN, PIB and open-data numbers, and the footer names every source and as-on date. Rendered in Chromium (Playwright): only console error is a missing favicon. Screenshot: `components/dashboard_map/screenshot-v0.png`.
- Caveats on the map itself: registrations ≠ stock, a 14-month date gap, segment mix ignored, open data ≈ 8% of official. Boundaries are geoBoundaries (DataMeet/ECI) and *not* Survey of India–certified; the OSM raster basemap uses OSM's international depiction. **For the government-facing finale, switch to SoI-consistent boundaries and a compliant basemap (e.g. Mappls/Bhuvan or no basemap).**
- Fact-checker agent running on the top research claims (→ `research/fact-check.md`).

### 2026-10-04 09:40 IST — Maharashtra drill-down on real data (all 61 RTOs)
- All 61 Maharashtra RTOs fetched (Till-Today + CY2025). **C1 reconciliation: Σ RTO BEV = 1,185,108 = state table → error 0.0.**
- RTO → district crosswalk `components/admin_geo/data/rto_district_MH.csv`: 60/61 mapped to 35 units (Mumbai City + Suburban merged; the TC office has 0 BEV). Method per row (name_match / manual); to verify against the Transport Department's jurisdiction list.
- **District demand** (`eval/results/mh_district_demand.csv`): Pune 282,970 BEV (30,428 4W), Nagpur 113,736 (27,143 3W), Mumbai 78,814 (33,950 4W — most cars), Nashik 77,534, Kolhapur 71,548. Segment mix: 2W 83.6%, 3W 5.5%, 4W 9.6%, bus 0.4%, goods 0.8%.
- Benchmark-equivalence requirement (not a demand model): to match the national median density (308 BEV/station) Maharashtra needs 3,848 stations (it has 4,155 official); to match Karnataka (152.4) it needs 7,776 (+3,621). Per-district figures are in the CSV.

### 2026-10-04 09:55 IST — Second auto-research loop (C9, spike 2): real ledger
- `components/adoption_forecast/autoresearch/`: a frozen `eval.py` (36 states; DEV = rolling one-step origins 2022→23 and 2023→24; HOLDOUT 2024→25, lead-only; metric = registration-weighted WAPE), `forecaster.py`, `program.md`, `results.tsv`.
- 8 hypotheses, DEV WAPE: naive 0.281 (baseline) · 1-yr growth 0.783 · damped growth 0.308 · pooled growth 50:50 0.270 · pooled national growth 0.244 · share-logit k = 3 0.847 / damped 0.245 · **share-logit k = 2, pooled 50:50, damped 0.5: 0.178 (kept, −37%)**.
- **Holdout (2024→2025):** naive 0.150 · pooled national growth 0.101 · share-logit 0.110 (national error +2.0%). Both pooled models beat naive by 27–33%; the DEV winner is not confirmed over pooled growth (0.009 gap, inside noise) → next: monthly data for more origins, then an ensemble.
- Observation: CY2026 to date (to 4 Oct) = 2,556,580 BEV registrations, already more than all of CY2025 (2,356,971), so adoption is re-accelerating after the 2023–25 slowdown (yearly growth ×3.1 in 2022, then ×1.49, ×1.28, ×1.16).

### 2026-10-04 10:05 IST — Paused (user decision via Supervisor)
- No background jobs or agents were running (the fact-checker and companies-products agents had already been stopped). Their partial files are committed: `research/fact-check.md` (1 claim verified) and `research/companies-products.md` (85.6 KB, unverified agent output; not cited anywhere yet).
- Reproducibility fix before pausing: the PIB source fetcher and boundary download are now committed scripts (`components/charger_ingest/fetch_sources.py` + `source_urls.txt`, `components/admin_geo/fetch_boundaries.sh`), so every number in the docs has a committed reproduce command.
- Resume point and full rebuild commands: see *Now*.

### 2026-10-04 13:10 IST — Resumed (Supervisor: batch slot)
- Definition of done received (see *Now*). New rules adopted: PLAYBOOK §4 (child sessions only, ≤ 2), §6 (no stash/autostash), §10 (cross-model reviews + ledger). Memory level 39 at resume.

### 2026-10-04 13:45 IST — Step 1 (facts) done: fact-check + policy norms verified at primary sources
- `research/fact-check.md` (lead-verified, reproducible with `research/tools/verify.py`): 11 agent claims → 7 VERIFIED (2 with corrections, 2 with scope notes), 1 via secondary reports only (J.D. Power), 1 PARTLY (DTE 1:191 ratio UNVERIFIED), 1 GitHub check, and the novelty search (none found in 3 searches + 2 candidate checks).
- **Policy numbers verified:** MoP guidelines No. 12/2/2018-EV (17 Sep 2024), clause 11(1): one station per 1 km × 1 km urban grid by FY2030; every 20 km on both sides of highways; fast charging every 100 km for long-range/heavy-duty. Clause 13: BEE runs a "National online database of all public charging stations", and CPOs share annual energy sold per charger with it. PM E-DRIVE (PIB 2060774, 1 Oct 2024): ₹2,000 crore for 22,100 e-4W fast chargers + 1,800 e-bus + 48,400 e-2W/3W (our sum 72,300). NITI Aayog: "no global consensus on number of charging points required".
- **New official time point:** PIB 2086533 (20 Dec 2024) has 25,202 stations with a state annex. With BEE (Apr 2025) and MoP (Aug 2025) that is three state-wise snapshots → growth-aligned supply series for C5/C10.
- Agent files (`sota-methods.md`, `companies-products.md`) are now headed "unverified — cite only via fact-check.md".

### 2026-10-04 13:35 IST — C9 v2 on month-wise VAHAN (forecast ratchet + 2026 nowcast)
- VAHAN client gained fuel-filtered queries (`query_filtered`, ids auto-discovered). Fetched State × Month Wise for 2019–2026, BEV-filtered and all fuels (16 tables). **Reconciliation: 2025 monthly BEV totals = yearly State × Fuel BEV for every state (0 difference; 2,356,971).**
- **12-month forecast ratchet** (frozen `eval_monthly.py`, 8 DEV + 4 HOLDOUT quarterly origins; WAPE):

  | Model | DEV | HOLDOUT |
  |---|---|---|
  | naive | 0.232 | 0.223 |
  | pooled growth | 0.173 | 0.166 |
  | **share-logit** | **0.147** | **0.157** |
  | ensemble | 0.158 | 0.161 |

  The ensemble did not beat the single model, so share-logit is kept and confirmed on the holdout (−29% vs naive).
- **2026 nowcast:** YoY scaling, the best in the 2023–25 backtest (state WAPE 0.072, mean national error 3.0%, max 7.7%). **CY2026 ≈ 3.60 million BEV registrations** (methods span 3.56–3.60M) vs 2.36M in CY2025. Files: `eval/results/c9_nowcast_2026.csv`, `c9_nowcast_backtest.csv`, `c9_summary.json`.
- Also parsed the third official snapshot (PIB 2086533, 20 Dec 2024: 25,202 ✓) and the Chhattisgarh district annex (31 districts, 271 ✓): the first official *district-level* counts, usable to validate district allocation.

### 2026-10-04 13:45 IST — C5 three-source estimate, validated small-area supply, Maharashtra gap map v1
- **Third source:** Overture Maps places 2026-09-23.1 (CDLA-P-2.0 / Apache-2.0 / CC0; "contains no OpenStreetMap data"). India bbox: 391 rows with category `ev_charging_station`, plus 659 found by a strict EV-name rule (many chargers are miscategorised, e.g. Bolt.Earth as `corporate_or_business_office`) = 1,050. AllThePlaces has no Indian charging-operator spiders.
- **Multiple-systems estimate** (`components/census_completeness/mse.py`; log-linear Poisson, AIC model choice, bootstrap CI):
  - 3,507 records → 3,336 sites; very thin overlaps (only 7 sites in all 3 lists).
  - National: 80,833 sites (90% CI 35,915–171,036) vs official 29,277 (Aug 2025) and IEEFA 52,718 (Jul 2026).
  - **State validation** (17 states with ≥ 100 official stations): median estimate/official 0.58 (union: 0.094); median |ln ratio| 0.84; 90% CI covers official in 47% of states → **fails** the pass rule (median within 25% and coverage ≥ 80%).
- **Supervisor 13:25 proposal** (validate the estimate, use it only if it passes, otherwise allocate with intervals, show coverage): agreed with two refinements (replied). Implemented as `components/access_gap/small_area.py`:
  - ln(official_s) ~ ln(BEV_s) + ln(open_s + 1), fitted across states; allocate the state total; predictive intervals (coefficient bootstrap + multinomial).
  - **District-level validation on Chhattisgarh** (official district annex, PIB 2086533; 28 districts in 2021 boundaries; RTO→district crosswalk; Σ RTO BEV = state 218,859 exactly):

    | Method | WAPE | Spearman |
    |---|---|---|
    | open-share | 0.995 | 0.46 |
    | 50:50 blend | 0.705 | 0.77 |
    | BEV-share | 0.540 | 0.855 |
    | **small-area model** | **0.410** | **0.841** |

    The model's 90% predictive intervals cover 82% of districts. Its state-level leave-one-out median |ln err| is 0.52 (36 states).
  - Correction: the first MH table used a 50:50 blend that tied 17 data-thin districts at ~571 BEV/station (an artifact). Replaced by the validated model.
- **Maharashtra district gap** (`components/access_gap/mh_district_gap.py`; geoBoundaries ADM2 2021, LGD-based, 36 districts incl. Palghar, Mumbai City + Suburban merged = 35 units):

  | District | BEV per estimated station (90% range) |
  |---|---|
  | **Nagpur** | **574** (423–774); 113,736 BEV, 24% 3W, only 4 open-data sites |
  | Amravati | 467 |
  | Nashik | 441 |
  | Jalgaon | 413 |
  | Chhatrapati Sambhajinagar | 395 |

  State average 285; 17 of 35 districts have no open-data site. Matching Karnataka's density (152.4) needs +3,641 stations.
- **Dashboard v1** (`components/dashboard_map/`; `dist/index.html` + `dist/maharashtra.html`): no third-party basemap (boundary compliance); national layers BEV/station and **open/official coverage per state** (Supervisor item 3); district drill-down with ranges and reasons. Checked in Chromium (Playwright, private pages; the shared browser was being navigated by another session): 0 console errors, both layers switch, ranking row → zoom + popup. Screenshots committed. Browser closed.

