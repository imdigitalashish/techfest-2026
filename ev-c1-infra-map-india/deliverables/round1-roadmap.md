# Round 1 — Implementation roadmap (DRAFT v1, 4 Oct 2026)

**Goal by the Grand Finale (16–18 Dec 2026):** a working web platform that delivers every expected deliverable of Challenge 1, demonstrated live on Maharashtra and at national level.

## 1. Expected deliverable → what we will show
| Expected deliverable (brief) | What we build | Components |
|---|---|---|
| Functional prototype / web platform with a unified view of charging infrastructure | Unified census of public charging *sites* (with connectors), every record traceable to its sources | C2–C5, C12 |
| Interactive national GIS map (chargers, coverage, gaps) | MapLibre map: sites, coverage factor per state/district, gap score layers, corridor gaps | C10, C13 |
| Analytical methodology document | This repo's methodology + an assumptions registry with sources and ranges | all |
| Charger requirement estimation and recommendation module | Requirements by charger class and year (3 scenarios) + recommended sites with reasons | C8, C9, C11 |
| Decision-support dashboard | Indicators per state/district (EVs per site, kW per EV, access index, growth, coverage), scenario sliders, export to PDF/CSV | C12, C13 |
| Demo video for ≥ 1 geography | Maharashtra: Mumbai–Pune–Nashik, Nagpur, and a rural district | all |
| Scalability roadmap | National refresh pipeline; how states add their own data; UEI integration path | C1, C2, C12 |

## 2. Development stages and dates
| Stage | Dates | Output | Exit test |
|---|---|---|---|
| 0. Data foundation (**started**) | 4–15 Oct | VAHAN national + RTO pipeline (**working**); OSM ingest (**working**); official totals (**working**); boundaries; RTO→district crosswalk for Maharashtra; second charger source | Σ RTO = state total within 1%; ≥ 95% of MH RTOs mapped |
| 1. Round-1 submission | by 30 Oct | Methodology + roadmap (this), with early real results | Submitted by the team leader on techfest.org |
| 2. Core engine | 1–17 Nov | Census with ER + completeness (spike 1); stock + demand; adoption forecast with backtest; gap metrics v1 | ER F1 ≥ 0.9 on labelled pairs; completeness error vs held-out official totals reported; forecast sMAPE reported |
| — Exams (team unavailable) | 19–25 Nov | Automated jobs only (data refresh, auto-research loops on the spikes) | — |
| 3. Requirements + siting | 26 Nov–5 Dec | Requirement module (3 scenarios), MCLP siting with grid flag, corridor analysis | Beats random, population-greedy and norm-grid baselines on demand covered per charger |
| 4. Platform + dashboard | 26 Nov–10 Dec | API + national map + Maharashtra drill-down + exports | A planner finds the 5 worst districts and their reasons in < 2 minutes |
| 5. Hardening + rehearsal | 10–15 Dec | Demo script, video, Q&A rehearsal against hostile-judge questions, offline fallback | Full demo runs offline on a laptop |
| Grand Finale | 16–18 Dec | Live demo + how the solution evolved from this roadmap | — |

## 3. Tools and technologies
- **Data pipeline:** Python 3.11, requests (VAHAN dashboard replay), Overpass API (OSM), pandas, GeoPandas, DuckDB (+ spatial), GeoParquet, H3.
- **Analytics:**
  - entity resolution: Splink (Fellegi–Sunter);
  - completeness: capture–recapture / log-linear multiple-systems estimation;
  - accessibility: PySAL `access` (2SFCA/E2SFCA);
  - optimisation: PySAL `spopt` (MCLP, p-median);
  - forecasting: Bass/logistic with hierarchical pooling (PyMC or statsmodels);
  - routing/isochrones: OSRM or Valhalla on OSM.
- **Platform:** FastAPI, MapLibre GL JS (+ deck.gl for H3 layers), PMTiles for national tiles.
- **Quality:** contract tests per component (pydantic schemas in `architecture/contracts/`), a frozen evaluation harness with fixed seeds, and auto-research "ratchet" loops for the two spike components.
- **Compute:** a laptop is enough (all inputs are small). Cloud is optional for scheduled refreshes.

## 4. Path to the final prototype (how each stage feeds the next)
Data foundation → unified census (with coverage factors) → demand by segment → gap metrics → requirement and siting → dashboard. Each stage has a fixed contract, so stages can improve independently. The evaluation harness re-runs end to end on every change and records the metrics, so the finale can show measured progress since Round 1.

## 5. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Open charger data is sparse (OSM ≈ 2% of official count) | Add OCM and operator/UEI feeds; publish coverage factors; calibrate to official state totals |
| Registrations ≠ vehicles on road | Survival curves by segment with documented ranges; sensitivity analysis |
| VAHAN dashboard changes its markup | Client fails loudly; cached snapshots; fix within a day |
| Official counts have different dates/definitions | Store as-on dates; align with VAHAN monthly series; never mix units silently |
| Map boundary compliance for government use | Use Survey of India–consistent boundaries for India's external boundary |
| Team availability (exams 19–25 Nov) | Automated jobs only in that window; finish the core engine by 17 Nov |

## 6. Scalability roadmap (to a nationwide planning platform)
1. **National refresh:** all 1,468 VAHAN offices and all charger sources on a schedule. Each run is reproducible and versioned.
2. **Federated inputs:** states, DISCOMs and operators upload or stream data through the same contracts (OCPI-style site/connector model). The Unified Energy Interface becomes a near-complete supply source when available, and our completeness estimator then audits it.
3. **More vehicle categories and uses:** fleets, e-trucks, battery swapping, depot charging.
4. **Planning workflows:** what-if scenarios for subsidy allocation (e.g. PM E-DRIVE), ULB-level reports, an API for third parties.
