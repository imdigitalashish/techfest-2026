# Round 1 — Implementation roadmap · EV Infra Map India (v3, 4 Oct 2026)

**Goal for the Grand Finale (16–18 Dec 2026):** a working platform that covers every expected deliverable, demonstrated live at national level and on Maharashtra. It builds on what already runs ([methodology](round1-methodology.md) §2), and keeps a public-data-only fallback for every step.

## 1. Expected deliverables → what we will show
| Expected deliverable | What we build | Status today |
|---|---|---|
| Unified view of charging infrastructure | Census of candidate sites from every accessible source, each with source, date, licence and URL | **Running:** <!--n:linked_sites-->3,325<!--/n--> linked clusters; 3 official snapshots |
| National GIS map (chargers, coverage, gaps) | MapLibre dashboard: sites, date-aligned registration pressure, reference coverage per state, Maharashtra drill-down | **Running** (`components/dashboard_map/dist/`) |
| Methodology document | Methodology + fact-check + assumptions registry | **Drafted** |
| Requirement estimation & recommendations | Norm-based (MoP 20 km / 100 km / 1 km grid) and energy-based requirements; candidate sites with reasons | **Running:** highway norm for Maharashtra (<!--n:cor_norm_stations-->1,853<!--/n--> stations); the rest in stages 2–3 |
| Decision-support dashboard | Indicators with ranges and reasons, "verify first" lists, scenario sliders, exports | Indicators and reasons **running**; scenarios and exports in stage 3 |
| Demo video (≥ 1 geography) | Maharashtra: a verify-first district (Nagpur), the Mumbai–Pune corridor, a data-thin district | Stage 4 |
| Scalability roadmap | §4 | Drafted |

## 2. Stages, owners and exit tests
Owners are roles until the team is registered: **D** = data & pipeline lead, **A** = analytics lead, **P** = platform/UI lead, **L** = team leader (submission, partner requests).

| Stage | Dates | Output | Owner | Exit test |
|---|---|---|---|---|
| 0. Data foundation (**done**) | 4 Oct | VAHAN national/monthly/RTO pipeline (fail-closed); 3 open charger lists; official snapshots; boundaries; crosswalks | D | Σ RTO = state total (achieved) |
| 1. Round 1 | by 30 Oct | Registration by 15 Oct; this submission; BEE open-API request (clause 13) and CEA energy-report ingestion | L, D | Submitted by the team leader; API request sent with a 30-day follow-up date |
| 2. MVP engine — **scope cut before exams** | 1–17 Nov | (a) Requirement MVP: the three MoP norms on directed carriageways and state-notified urban areas (heavy-duty only with ≥ 2 × 240 kW chargers). (b) Segment- and mode-aware public energy demand with sourced ranges, cross-checked against CEA DISCOM energy. (c) A hand-audited sample of 200 sites (access, status, connectors) and pairwise match labels | A, D | Matching F1 measured on labels; CEA energy within the model's stated range for ≥ 2 states, or the gap explained |
| — Exams | 19–25 Nov | Scheduled data refresh only | — | — |
| 3. Recommendations + platform | 26 Nov–8 Dec | Candidate sites with a grid-status field (`verified / unknown / infeasible`, with evidence and date); MCLP siting; FastAPI store; dashboard scenarios and exports | A, P | Beats random, population-greedy and norm-grid placement on demand covered per added charger; a planner finds the verify-first districts and their reasons in < 2 minutes (3 users) |
| 4. Hardening | 9–15 Dec | Offline demo (vendored map library, cached data), video, hostile-jury rehearsal, licence/redistribution review | P, L | Full demo offline on one laptop |
| Finale | 16–18 Dec | Live demo + how the work evolved from this roadmap | all | — |

**Stretch, not dependencies:** Gaussian-process district disaggregation; drive-time catchments (OSRM/Valhalla); national district coverage beyond Maharashtra.

## 3. Safeguards for ministry-facing claims
| Risk | Safeguard | Fallback if no new data arrives |
|---|---|---|
| Open lists see only a fraction of stations (reference-coverage index <!--n:open_coverage_pct-->11.4%<!--/n-->) | BEE open-API request (L, by 30 Oct); coverage audit re-run on every new list | Publish coverage per state; label every supply number "lower bound" or "model, conditional" |
| District supply is model-based (tested in one state) | Re-test on every official district annex obtained; ranges only | Rank on observed registration pressure and visible supply; never on modelled supply alone |
| Grid and land feasibility | `verified / unknown / infeasible` with evidence (MoP clause 11(3)); DISCOM checks for finalists only | Recommendations stay "provisional" |
| Scheme rules change (PM E-DRIVE guidance, eligibility) | Version every scheme document used; distinguish announced / sanctioned / installed / operational | Use only verified, dated documents |
| Map and jurisdiction compliance | Boundary provenance and vintage tracked; RTO crosswalks reviewed with transport-department lists | Show merged units explicitly; state "not Survey of India–certified" |
| VAHAN dashboard changes | Ids discovered by label; exports rejected unless rows sum to totals | Cached, checksummed snapshots |

## 4. Scalability (towards a nationwide planning platform)
1. **National refresh:** all <!--v:V1-->1,468<!--/v--> VAHAN offices and every charger source on a schedule, versioned and reproducible.
2. **Federated inputs:** states, DISCOMs and operators push data through the same site/connector contract. The BEE database becomes the backbone, and the coverage audit measures *its* completeness.
3. **More segments:** fleets, e-trucks, depots, battery swapping.
4. **Planning workflows:** PM E-DRIVE allocation what-ifs (once allocation data are verified), ULB-level reports, an open API.
