# Round 1 — Methodology document · EV Infra Map India (v3, 4 Oct 2026)

**Challenge 1:** Mapping and integration of nationwide EV charger installations based on vehicle population, using VAHAN data.
**Team information** (to be completed by the team leader before submission): Team name — _TBD_ · Team ID — _TBD (registration by 15 Oct)_ · Institution — _TBD_ · Contact — _TBD_.

> Every number from our analysis is rendered from committed runs (`sh eval/run_all.sh` → `eval/results/latest.json`). Every external number is bound to a row of [`research/fact-check.md`](../research/fact-check.md), where the opened source and quote are recorded. `eval/check_docs.py` fails if either link breaks. No synthetic data is used.

## Where the evidence is (by judging criterion)
| Criterion (weight) | Where | Headline evidence |
|---|---|---|
| Problem understanding & relevance (<!--v:B1-->25%<!--/v-->) | §1 | The decision supported, the policy anchors (MoP 2024 norms, PM E-DRIVE, BEE database), and the measured fragmentation of public data |
| Feasibility & technical soundness (<!--v:B1-->25%<!--/v-->) | §2, Appendix | Running pipeline on real national data. Validation results, including the ones that **failed** (capture–recapture) and what replaced them |
| Innovation (<!--v:B1-->20%<!--/v-->) | §3 | Coverage audit of the charger inventory; point-in-time-tested district supply estimates; browser-free VAHAN pipeline to RTO level |
| Roadmap clarity (<!--v:B1-->20%<!--/v-->) | [roadmap](round1-roadmap.md) | Dated stages, exit tests, owners, data-access fallbacks |
| Data strategy (<!--v:B1-->10%<!--/v-->) | §4 | Source-role and vintage matrix; licences; the BEE open-API request |

## 1. Problem understanding
**The decision we support.** A State Nodal Agency (or MHI under PM E-DRIVE) decides where the next public chargers should go, which type, and which existing data must be verified first. Today that decision has no shared, located, date-stamped evidence base.

**Policy anchors (verified at the source).**
- **Density norms:** the Ministry of Power's 2024 guidelines (clause 11(1)) set one station per 1 km × 1 km grid in state-notified urban areas by FY2030, and every 20 km on both sides of highways, expressways and major roads.
- **Heavy-duty:** fast charging every 100 km on designated corridors, with <!--v:P8-->at least two chargers of 240 kW<!--/v--> each.
- **Data:** BEE maintains a national database of public stations with the State Nodal Agencies, and "will provide open APIs… restricted to non-confidential information" (clause 13; <!--v:P7-->fact-check P7<!--/v-->).
- **PM E-DRIVE:** ₹<!--v:P5-->2,000<!--/v--> crore for <!--v:P5-->22,100<!--/v--> e-4W fast chargers, <!--v:P5-->1,800<!--/v--> for e-buses and <!--v:P5-->48,400<!--/v--> for e-2W/3W.
- **NITI Aayog:** "there is no global consensus on number of charging points required for a certain number of EVs" — so requirements must be derived transparently, not from one ratio.

**Fragmentation, measured.** Published counts differ in date, source and probably definition:

| Count | As on | Source |
|---|---|---|
| <!--v:3-->12,146<!--/v--> | Feb 2024 | government data via IEEFA |
| <!--v:2-->25,202<!--/v--> | Dec 2024 | PIB |
| <!--v:E1-->26,367<!--/v--> | 1 Apr 2025 | BEE |
| <!--v:E2-->29,277<!--/v--> | 1 Aug 2025 | MoP |
| <!--v:4-->52,718<!--/v--> | Jul 2026 | IEEFA |

Operators report their own units: "<!--v:E3-->10000+<!--/v--> EV Chargers Installed" (Statiq); "<!--v:E4-->2,000+<!--/v--> mobility stations" (Jio-bp, fuel and EV combined). The three official snapshots we ingested give no coordinates.

**What open data shows.** Linking OpenStreetMap, Open Charge Map and Overture Maps gives <!--n:linked_sites-->3,325<!--/n--> candidate site clusters (150 m rule). That equals <!--n:open_coverage_pct-->11.4%<!--/n--> of the older official reference count, a *reference-coverage index* rather than a completeness measure, because dates and eligibility differ.

**Demand is observable.** VAHAN covers all <!--v:V1-->36/36<!--/v--> states/UTs and <!--v:V1-->1,468 of 1,469<!--/v--> offices.
- **Registered to date:** <!--n:nat_bev_cum-->10,550,090<!--/n--> battery-electric vehicles; <!--n:bev_since_2020_pct-->95.3%<!--/n--> of them in 2020 or later, so registrations approximate the fleet.
- **Date-aligned ratio:** BEV registered by July 2025 against stations on 1 August 2025 gives <!--n:nat_bev_jul2025_per_pcs-->236<!--/n--> per station nationally. Large states range from <!--n:state_bev_jul2025_per_pcs_karnataka-->99<!--/n--> (Karnataka) to <!--n:state_bev_jul2025_per_pcs_assam-->759<!--/n--> (Assam).
- **Caveat:** most e-2W/3W charge at home or depots, or swap batteries. So the ratio is *registration pressure*, not service need.

## 2. Approach and what the evidence shows
### 2.1 Integration
- **VAHAN:** we replay the public dashboard's own requests (state, RTO, class, fuel, month), with no browser. Exports are rejected unless every row sums to its total. The sum over RTOs equals the state total exactly (error <!--n:mh_reconciliation_err-->0.0<!--/n--> in Maharashtra and Chhattisgarh).
- **Chargers:** each source is normalised to one model (a *site* with connectors, operator, status, as-on date, licence and URL). <!--n:osm_private_excluded-->13<!--/n--> OSM records tagged private are excluded.
- **Linkage:** mutual nearest neighbours within `150 m`, with at most one record per source per site.

### 2.2 Coverage audit of the charger inventory (spike 1)
A log-linear capture–recapture model estimates the sites that no list contains.
- **Abstention:** it returns an estimate only where the lists overlap enough. That is <!--n:mse_states-->5<!--/n--> of the <!--n:mse_states_ge100-->22<!--/n--> states with ≥ 100 official stations; the rest are "not estimable".
- **Result:** where estimable, the median estimate is <!--n:mse_median_ratio-->1.27<!--/n-->× the older official count, and the 90% CI contains it in <!--n:mse_states_in_ci-->4<!--/n--> of <!--n:mse_states-->5<!--/n--> states. The stated rule (median error within 25% and ≥ 80% CI coverage) **<!--n:mse_passes-->fails<!--/n-->** narrowly; <!--n:mse_sens_any_pass-->one<!--/n--> of <!--n:mse_sens_runs-->6<!--/n--> sensitivity variants passes.
- **Stability:** nationally the estimate depends on the model (<!--n:mse_n_min_model-->14,248<!--/n-->–<!--n:mse_n_max_model-->70,921<!--/n-->), so no national total is quoted.
- **Use:** an *audit* that is re-run as denser lists arrive, never a planning number. List dependence and heterogeneity are hypotheses we test as lists are added.

### 2.3 District supply (small-area allocation)
- **Method:** the official state total is allocated to districts in proportion to BEV<sup>b</sup>, with b fitted across the other states.
- **Point-in-time test:** on Chhattisgarh's official district annex (Dec 2024; registrations to Dec 2024; the independent state total; <!--n:cg_labelled-->27<!--/n--> labelled districts), WAPE was <!--n:cg_pit_wape-->0.30<!--/n--> against <!--n:cg_pit_bevshare_wape-->0.58<!--/n--> for plain BEV shares. The 90% predictive interval contained <!--n:cg_pit_inside-->24/27<!--/n--> official counts.
- **Limits:** one state; the interval recipe was revised after a first comparison; an open-data term could not be tested at that date. Estimates are therefore labelled *conditional*.

### 2.4 Adoption forecast and 2026 nowcast (spike 2)
- **Forecast:** a pooled EV-share logit trend forecasts the next 12 months per state. On development origins whose targets do not overlap the held-out ones, WAPE is <!--n:c9v3_dev_logit-->0.177<!--/n--> vs <!--n:c9v3_dev_naive-->0.360<!--/n--> for "same as last year". The held-out score is retrospective (already viewed). A prospective test is frozen and committed: CY2026 is scored in Jan 2027.
- **Nowcast:** CY2026 ≈ <!--n:nowcast_2026_m-->about 3.6 million<!--/n--> BEV registrations, against <!--n:nat_bev_2025-->2,356,971<!--/n--> in 2025. On the three years used to choose the method, the mean absolute national error was <!--n:nowcast_mean_nat_err-->3.0%<!--/n-->.

### 2.5 Maharashtra, the demonstration geography
For each of <!--n:mh_districts-->35<!--/n--> district units (2021 LGD geometry, Mumbai City + Suburban merged), we show:
- **Registration pressure (observed):** BEV registrations, 2025 growth, segment mix.
- **Visible supply (observed, lower bound):** open-data sites per 10k BEV. The state averages <!--n:mh_state_open_density-->3.7<!--/n-->; <!--n:mh_zero_open_districts-->17<!--/n--> districts show none.
- **Estimated stations (model, conditional range).** Rankings shift with the allocation recipe (Spearman <!--n:mh_rank_sens-->0.66<!--/n-->), so we do not rank investments on modelled supply.
- **Verify first:** high pressure with thin visible supply. These are <!--n:mh_verify_first-->Nagpur, Nashik, Ahilyanagar, Chhatrapati Sambhajinagar, Solapur, Amravati<!--/n-->. Nagpur, for example, has <!--n:nagpur_bev-->113,736<!--/n--> BEV (<!--n:nagpur_3w_pct-->24%<!--/n--> three-wheelers) and <!--n:nagpur_open-->4<!--/n--> visible sites.

### 2.6 Requirement estimation
- **Built (norm-based):** the MoP 20 km rule on <!--n:cor_side_km-->37,065<!--/n--> carriageway-side km of national highways and expressways (<!--n:cor_nh_ref_pct-->88.9%<!--/n--> of the length carries an NH reference) requires <!--n:cor_norm_stations-->1,853<!--/n--> stations. Only <!--n:cor_cov_lb-->11.7%<!--/n--> of side-km have a visible site within 10 km, a lower bound.
- **Benchmark only:** matching Karnataka's density would need <!--n:mh_net_ka-->3,621<!--/n--> more stations statewide. This is not a budget request.
- **Round 2 (energy-based):** chargers per class = public kWh per day ÷ (deliverable kW × 24 h × target utilisation), checked against a peak-hour queueing target. It is applied by segment and charging mode (home, depot, swap, public), with sourced parameter ranges. CEA's DISCOM-level public-charging energy (<!--v:P9-->1102.59<!--/v--> MU in FY2025-26 to December, partially reported) is the independent cross-check.

### 2.7 Roles of the official counts
- In the coverage audit: external comparator.
- In the allocation: other states' totals train b; the target state's total constrains the sum.
- For Chhattisgarh's districts: benchmark only.

## 3. Innovation (scoped claims)
1. **A coverage audit of a national charger inventory**, with abstention and stated pass rules. In three dated searches we found no prior application of capture–recapture to EV-charging inventories ([log](../research/fact-check.md)). This is an application claim, not methodological priority.
2. **District supply estimates tested at a past date** against official district counts, with conditional ranges.
3. **A browser-free, fail-closed VAHAN pipeline** to RTO, month and fuel, reconciled exactly to state totals.
4. **Claim-level provenance:** every number in this document is rendered from a run or bound to a quoted source.

## 4. Data strategy (source roles and vintages)
| Source | Role | As on | Licence / access | Status |
|---|---|---|---|---|
| VAHAN 4 dashboard | demand | live (fetched 4 Oct 2026) | public dashboard | ingested, monthly, RTO level |
| PIB 2086533 · PIB 2118894 · PIB 2151390 | official reference counts | 20 Dec 2024 · 1 Apr 2025 · 1 Aug 2025 | government releases | ingested |
| OSM · Open Charge Map · Overture places | candidate sites | Oct 2026 · Apr 2026 · Sep 2026 | ODbL · per provider · CDLA-P/Apache/CC0 | ingested and linked |
| geoBoundaries ADM1 / ADM2 (2021, LGD-based) | geography | 2011 / 2021 | CC BY 2.5 IN / ODbL | ingested; not SoI-certified |
| CEA PCS energy report | energy cross-check | Dec 2025 | government report | planned |
| BEE national database / open API | authoritative supply | — | request via MHI/ICAT (clause 13) | requested; fallback = open sources |

## 5. Limitations
- Registration pressure is not service need.
- Official counts lag, and the sources differ in definitions.
- Open data is sparse, urban-biased and partly unverifiable for access and uptime.
- The coverage audit fails its stated rule.
- District supply rests on a model tested in one state.
- The RTO → district crosswalk is ours; it needs official confirmation.
- Boundaries are not Survey of India–certified.

## 6. Disclosure
- **AI tools:** AI coding assistants wrote code and drafts; cross-model reviews are logged in `reviews/`.
- **Open-source software:** Python, pandas, GeoPandas, DuckDB, NumPy/SciPy, MapLibre GL JS.
- **External datasets:** as in §4, with attribution.
- **Synthetic data:** none.

## Appendix — validation results
**A1. Coverage audit (capture–recapture)**
- **Lists:** <!--n:osm_n_in_india-->586<!--/n--> OSM + <!--n:ocm_n_in_india-->1,869<!--/n--> OCM + <!--n:ovt_n_in_india-->1,039<!--/n--> Overture records → <!--n:linked_sites-->3,325<!--/n--> clusters; <!--n:sites_in_all3-->6<!--/n--> in all three lists.
- **National, AIC-selected model:** <!--n:mse_nat-->28,657<!--/n--> (90% CI with model re-selection <!--n:mse_nat_lo-->25,355<!--/n-->–<!--n:mse_nat_hi-->143,737<!--/n-->). AIC-weighted <!--n:mse_n_aic-->41,990<!--/n-->; per-model range <!--n:mse_n_min_model-->14,248<!--/n-->–<!--n:mse_n_max_model-->70,921<!--/n-->.
- **Sensitivity** (selection rule × linkage radius): <!--n:mse_nat_min_model-->21,257<!--/n-->–<!--n:mse_nat_max_model-->51,005<!--/n-->; the only passing variant uses <!--n:mse_sens_pass_radius-->250 m<!--/n-->.
- **Raw union:** median <!--n:union_median_ratio-->0.128<!--/n-->× the official count on the evaluated states.

**A2. District allocation, Chhattisgarh (official annex, 20 Dec 2024; total <!--n:cg_total-->271<!--/n-->; unlabelled: <!--n:cg_unlabelled-->Gaurella Pendra Marwahi<!--/n-->)**

| Variant | WAPE | 90% interval contains official count |
|---|---|---|
| BEV-only, point-in-time (b = <!--n:cg_pit_b-->0.66<!--/n-->) | <!--n:cg_pit_wape-->0.30<!--/n--> | <!--n:cg_pit_inside-->24/27<!--/n--> |
| Plain BEV share, point-in-time | <!--n:cg_pit_bevshare_wape-->0.58<!--/n--> | — |
| Current covariates with open data (sanity check, not a historical test) | <!--n:cg_cur_wape-->0.39<!--/n--> | <!--n:cg_cur_inside-->22/27<!--/n--> |

Open-data sites known in Chhattisgarh by Dec 2024: <!--n:cg_open_asof-->0<!--/n-->.

**A3. Forecast backtests (WAPE, next 12 months, 36 states)**

| Model | v3 development (no overlap) | v2 development | v2 held out (retrospective) |
|---|---|---|---|
| Same as last 12 months | <!--n:c9v3_dev_naive-->0.360<!--/n--> | <!--n:c9_dev_naive-->0.232<!--/n--> | <!--n:c9_hold_naive-->0.223<!--/n--> |
| Pooled growth | <!--n:c9v3_dev_pooled-->0.231<!--/n--> | <!--n:c9_dev_pooled-->0.173<!--/n--> | <!--n:c9_hold_pooled-->0.166<!--/n--> |
| Ensemble | <!--n:c9v3_dev_ensemble-->0.200<!--/n--> | <!--n:c9_dev_ensemble-->0.158<!--/n--> | <!--n:c9_hold_ensemble-->0.161<!--/n--> |
| **EV-share logit trend** | **<!--n:c9v3_dev_logit-->0.177<!--/n-->** | <!--n:c9_dev_logit-->0.147<!--/n--> | <!--n:c9_hold_logit-->0.157<!--/n--> |

**Nowcast method selection (2023–2025):** state WAPE <!--n:nowcast_wape-->7.2%<!--/n-->; mean absolute national error <!--n:nowcast_mean_nat_err-->3.0%<!--/n--> (worst <!--n:nowcast_max_nat_err-->7.7%<!--/n-->); mean absolute error of the Oct–Dec increment <!--n:nowcast_q4_err-->11%<!--/n-->.
