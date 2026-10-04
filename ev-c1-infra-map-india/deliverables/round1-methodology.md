# Round 1 — Methodology document (DRAFT v1, 4 Oct 2026)

**Challenge 1: EV Infra Map India** — Mapping and integration of nationwide EV charger installations based on vehicle population using VAHAN data.
**Team information:** Team name — _TBD_ · Team ID — _TBD (after registration by 15 Oct)_ · Institution — _TBD_ · Contact — _TBD_ (to be filled by the team leader).

> Every number below comes from a reproducible run in this repository ([`eval/baseline_state_gap.py`](../eval/baseline_state_gap.py)) or from a cited public source. Synthetic data: none used so far. Estimates are labelled.

## 1. Problem understanding
**Users and decisions.** MHI, ICAT, state nodal agencies, DISCOMs and urban local bodies need to decide *where*, *how many* and *what type* of public chargers to fund or permit, and need to defend those decisions. That requires three things nobody publishes together today:
1. a unified, located inventory of public charging infrastructure;
2. a demand picture by region and vehicle segment;
3. a forward estimate of need.

**Fragmentation, measured.** On 4 Oct 2026 we found the same national quantity reported as:

| Count | What | Source |
|---|---|---|
| 26,367 | public charging stations, as on 1 Apr 2025 | BEE, via PIB release 2118894 |
| 29,277 | public charging stations | MoP inputs, via PIB release 2151390, 1 Aug 2025 |
| "10000+" | chargers in "1014+" cities | one operator (Statiq) |
| "2,000+" | mobility stations | another operator (Jio-bp) |
| 600 | charging features (= **2.05%** of the official count) | OpenStreetMap; only 31.8% name an operator, 7.8% list any connector |

The official series are state-level tables without locations. Operator data sits in separate apps with different units. Open data is sparse. *Fragmentation is a problem of units, dates and missing locations, not only of many apps.*

**Demand is observable.** The VAHAN 4 dashboard now covers all 36 states/UTs and 1,468 of 1,469 registering offices. From it we measured **10,550,090 battery-electric registrations to date** (`ELECTRIC(BOV)` + `PURE EV`) and **2,356,971 in calendar 2025, 8.05% of all registrations that year**.

**First gap signal.** Nationally there are ≈ **360 BEV registrations per official public charging station**. Across large states the figure ranges from 152 (Karnataka) to 1,085 (Bihar) and 1,123 (Assam) (table: [`eval/results/state_gap_baseline.csv`](../eval/results/state_gap_baseline.csv)). We treat this ratio as a *starting point, not an answer*:
- registrations are not on-road stock;
- the station counts are 14 months older than the registrations;
- the ratio ignores the segment mix. E-rickshaws and two-wheelers mostly charge at home or depots, or swap batteries, and the hypothesis to test is that this is why some states look extreme.

Our methodology exists to turn this crude ratio into a defensible, segment-aware, coverage-adjusted estimate.

**Study boundary.** India; public and semi-public charging (all segments: 2W, 3W, 4W, buses, light goods); battery swapping counted as an alternative supply where data exist. Horizon: today to 2030. Geographic levels: national → state → district → city grid (H3) → highway corridor segments. Demonstration geography: **Maharashtra** (largest e-car market, by state BEV registrations second only to Uttar Pradesh: 1,185,108).

## 2. Analytical approach
The system is 14 components with typed contracts, each with an isolated metric ([architecture](../architecture/components.md)). The stages:

### 2.1 Integration: a unified, provenance-tracked charger census
- **Ingest** every accessible source through one adapter each:
  - OpenStreetMap (ODbL) — working;
  - Open Charge Map (open licence, API key);
  - operator locators and the Unified Energy Interface where their terms allow;
  - official state-wise totals (PIB/BEE/MoP) as benchmarks.
- **Normalise** to one canonical model: a *site* with connectors, where each connector has a type (CCS2, Type 2, CHAdeMO, GB/T, LECCS, Bharat AC-001/DC-001…), count and kW. Add operator, segments served, status and an as-on date. Every field keeps its source and licence.
- **Resolve** duplicates across sources: H3 spatial blocking, then probabilistic record linkage (Fellegi–Sunter; Splink) on distance, name, operator and connector similarity. Measured by pairwise F1 on hand-labelled pairs.
- **Innovation — estimate what no source lists.** Treat each source as an independent "capture" of the true set of sites. Multiple-systems (capture–recapture) estimation, with log-linear terms for source dependence, then gives an estimated total and a confidence interval per state and district. We validate against the *held-out* official state totals: 36 states, 29,277 stations.
  - The output is a **coverage factor** for every region ("we observe 61% of this district's stations, CI 52–70%"; illustrative format, not a result).
  - Every downstream gap figure is coverage-adjusted.
  - If source overlap is too thin, it falls back to calibration against the official totals.

### 2.2 Demand: from registrations to public-charging need
- **VAHAN ingest** by replaying the public dashboard's own requests: state, RTO, vehicle class, fuel, month and year. No browser and no third-party mirrors.
- **RTO → district crosswalk**: name matching, then manual review and office geocoding. The share of RTOs mapped is the metric.
- **Registrations → on-road stock** via segment survival curves. Assumptions are documented with ranges.
- **Stock → public energy need**. For each segment: daily km × Wh/km × share of energy from public charging (vs home, depot or swapping). Parameters come from Indian studies, each cited with a range. Sensitivity analysis is shown, not hidden.
- **Spatial disaggregation** of district demand to an H3 grid with population, built-up area and points of interest (dasymetric mapping).

### 2.3 Gap assessment
For each district and grid cell:
- coverage-adjusted EVs per site and kW per EV;
- spatial accessibility with the enhanced two-step floating catchment method (E2SFCA, drive-time catchments);
- for highways, spacing gaps against the Ministry of Power's 2024 guideline norms, encoded as benchmark layers once verified clause-by-clause.

A composite **gap score** carries ranked, human-readable reasons, e.g. "4W demand grew 62% y/y; nearest DC charger 38 km; coverage 0.4" (illustrative format).

### 2.4 Estimation of future requirements
- **Adoption forecast** per state/district to 2030: Bass/logistic diffusion with regions pooled (hierarchical), under three scenarios (business-as-usual, policy target, high). Validated by backtest: train ≤ 2024, test 2025, metric sMAPE.
- **Charger requirement** by class (LEV AC, AC 7–22 kW, DC 30–60 kW, DC 120 kW+, bus depot): energy need ÷ (power × utilisation), with a queueing check on peak-hour waiting times.
- **Recommended sites** by location-allocation: maximal covering and p-median (PySAL spopt). Candidate sites are fuel stations, parking, malls, highway amenities and government land. A grid-readiness flag comes from substation proximity.
- **Baselines the recommender must beat:** random, population-greedy and norm-grid placements, measured by demand covered per added charger.

### 2.5 Validation and transparency
- **Held-out official totals** for the census.
- **Backtests:** do gap scores at year T predict where sites appear by T+1? Is the adoption forecast accurate on 2025?
- **Sensitivity:** tornado charts over the demand parameters.
- **An assumptions registry:** every parameter has a source, range and owner.
- **Provenance on every number:** the dashboard shows source and as-on date.

## 3. Innovation (summary)
1. **A completeness-aware national census.** Coverage and confidence are published, instead of a raw count that silently misses most stations.
2. **Segment- and charging-mode-aware requirement estimates.** These avoid the naive "EVs per charger" trap.
3. **A live, browser-free VAHAN pipeline down to RTO level**, refreshable on demand.
4. **Evidence-first planning outputs.** Every recommendation carries its reasons, its data lineage and the baseline it beats.

## 4. Data strategy
| Layer | Source | Granularity | Licence / terms | Status |
|---|---|---|---|---|
| EV registrations | VAHAN 4 dashboard (MoRTH/NIC) | state, RTO × vehicle class × fuel × month/year | public dashboard | **Ingested** (national + Maharashtra RTOs) |
| Official charger totals | PIB 2151390 (MoP, 1 Aug 2025), PIB 2118894 (BEE, 1 Apr 2025) | state (× city tier) | government release | **Ingested** (benchmarks) |
| Charger locations | OpenStreetMap (Overpass) | point | ODbL 1.0 | **Ingested** (600 features) |
| Charger locations | Open Charge Map; operator locators; Unified Energy Interface | point + connectors | per source | Planned (key/permission) |
| Boundaries | Survey of India–consistent state/district boundaries; LGD codes | polygon | per source | Planned |
| Population / activity | Census 2011 + projections; gridded population; OSM POIs | district / grid | open | Planned |
| Roads / corridors | OSM national highways; MoRTH NH list | line | ODbL / government | Planned |
| Grid context | OSM substations; public DISCOM data where available | point | ODbL / per source | Planned |

**Disclosure.** AI coding assistants were used to write code and drafts; all numbers come from the committed scripts. Open-source software: Python, pandas, GeoPandas, H3, DuckDB, PySAL (spopt, access), Splink, MapLibre. External datasets as listed above, with attribution. No synthetic data so far; any synthetic data will be labelled.
