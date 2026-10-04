# Round 1 — Implementation roadmap · EV Infra Map India (v2, 4 Oct 2026)

**Goal for the Grand Finale (16–18 Dec 2026):** a working web platform that delivers every expected deliverable of Challenge 1. It will be demonstrated live at national level and on Maharashtra, starting from what already runs today (methodology §2).

## 1. Expected deliverables → what we will show
| Expected deliverable (brief) | What we build | Status today |
|---|---|---|
| Functional platform with a unified view of charging infrastructure | Census of public charging *sites* from every accessible source, each record traceable to its source, as-on date and licence | **Running:** 3 open sources linked into <!--n:linked_sites-->3,336<!--/n--> sites, plus 3 official snapshots |
| Interactive national GIS map (chargers, coverage, gaps) | MapLibre dashboard: sites, BEV per station, open-data coverage per state, district drill-down | **Running:** national and Maharashtra pages (`components/dashboard_map/dist/`) |
| Analytical methodology document | [Methodology](round1-methodology.md) + assumptions registry + fact-check | **Drafted** (this submission) |
| Charger requirement estimation and recommendation module | Requirements by charger class and year (3 scenarios), energy- and norm-based; recommended sites with reasons | Running: benchmark density (Maharashtra: <!--n:mh_shortfall_ka-->3,641<!--/n--> more stations to reach Karnataka's density) and the MoP highway norm (<!--n:cor_norm_stations-->1,853<!--/n--> corridor stations for Maharashtra); energy-based module and siting in stage 3 |
| Decision-support dashboard | Indicators per state and district with ranges, ranked reasons, scenario sliders, PDF/CSV export | Indicators and reasons **running**; scenarios and export in stage 4 |
| Demo video for ≥ 1 geography | Maharashtra: Nagpur (most underserved), Mumbai–Pune–Nashik corridor, a data-thin district | Stage 5 |
| Scalability roadmap | §5 below | Drafted |

## 2. Development stages
| Stage | Dates | Output | Exit test (measured by the frozen evaluators) |
|---|---|---|---|
| 0. Data foundation (**done**) | 4 Oct | VAHAN pipeline (national, monthly, RTO); 3 open charger sources; official snapshots; boundaries; Maharashtra and Chhattisgarh crosswalks | Σ RTO = state total (achieved: error <!--n:mh_reconciliation_err-->0.0<!--/n-->) |
| 1. Round-1 submission | by 30 Oct | This methodology + roadmap; team registration by 15 Oct | Submitted by the team leader on techfest.org |
| 2. Core engine | 1–17 Nov | Fellegi–Sunter site matching (hand-labelled pairs); coverage re-estimated with any new list; segment-aware demand (stock, km, Wh/km, public share); forecast with uncertainty to 2030 | Matching F1 ≥ 0.9; held-out forecast WAPE ≤ <!--n:c9_hold_logit-->0.157<!--/n--> (today's level); district validation repeated on every new official annex |
| — Exams (team unavailable) | 19–25 Nov | Scheduled data refresh and auto-research loops only | — |
| 3. Requirements + siting | 26 Nov–5 Dec | Energy-based requirements; urban 1 km grid norm; heavy-duty 100 km norm (the 20 km highway norm already runs for Maharashtra); MCLP siting with a grid-readiness flag | Beats random, population-greedy and norm-grid placements on demand covered per added charger |
| 4. Platform | 26 Nov–10 Dec | FastAPI + DuckDB/GeoParquet store; dashboard with scenarios, exports and source lineage; Survey of India–consistent boundaries | A planner finds the five worst districts and their reasons in < 2 minutes (timed with 3 users) |
| 5. Hardening + rehearsal | 10–15 Dec | Offline demo (vendored map library, cached data), video, hostile-jury Q&A rehearsal | Full demo runs offline on one laptop |
| Grand Finale | 16–18 Dec | Live demo + how the solution evolved from this roadmap | — |

## 3. Tools and technologies
- **Data:** Python 3.11, requests (VAHAN replay), Overpass API, DuckDB (+ spatial, httpfs for Overture), pandas, GeoPandas, GeoParquet.
- **Analytics:**
  - capture–recapture: log-linear Poisson, our own code, validated;
  - small-area allocation with bootstrap intervals;
  - forecasting: pooled logit trends; a Gaussian-process disaggregation is to be tried (Nature Communications 2026, verified);
  - Splink (entity resolution), PySAL `spopt` (siting) and PySAL `access` (2SFCA);
  - OSRM or Valhalla for drive times.
- **Platform:** FastAPI, MapLibre GL JS, PMTiles.
- **Quality:**
  - typed contracts (`architecture/contracts/`);
  - frozen evaluators with held-out splits;
  - auto-research ledgers;
  - `eval/run_all.sh` → `eval/check_docs.py` on every change.
- **Compute:** one laptop is enough; all inputs are small.

## 4. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Open charger data is sparse (<!--n:open_coverage_pct-->11.4%<!--/n--> of the official count) | Request the BEE national database and operator data via MHI/ICAT (MoP 2024 clause 13); use UEI/Beckn discovery when open; coverage shown on the map |
| District supply rests on a model tested in one state | Re-test on every official district annex; show ranges, never single numbers |
| Registrations ≠ vehicles on the road | Survival curves by segment with documented ranges; sensitivity charts |
| VAHAN dashboard markup changes | Client discovers widget ids by label and fails loudly; cached snapshots |
| Government map compliance | No third-party basemap; Survey of India–consistent boundaries before the finale |
| Team availability (exams 19–25 Nov) | Core engine by 17 Nov; only automated jobs in the exam window |

## 5. Scalability roadmap (towards a nationwide planning platform)
1. **National refresh:** all 1,468 VAHAN offices and all charger sources on a schedule; versioned, reproducible runs.
2. **Federated inputs:** states, DISCOMs and operators push data through the same site/connector contract (OCPI-like). The BEE database and UEI become near-complete sources, and the capture–recapture audit then measures *their* coverage.
3. **More segments and uses:** fleets, e-trucks, battery swapping, depots.
4. **Planning workflows:** PM E-DRIVE allocation what-ifs, ULB-level reports, an open API.
