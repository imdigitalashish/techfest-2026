# Landscape — EV Infra Map India (v1, 4 Oct 2026)

> **v2 (4 Oct 2026, 14:40 IST).** Every external claim here was opened by the lead (quotes in [`fact-check.md`](fact-check.md); tool: [`tools/verify.py`](tools/verify.py)). Run-derived numbers are rendered from `eval/results/latest.json` (markers checked by `eval/check_docs.py`). The agent-written files [`sota-methods.md`](sota-methods.md) and [`companies-products.md`](companies-products.md) are unverified leads except where fact-checked. Per-component innovation notes are §5 here and in [ADR 001](../architecture/adr/001-spike.md).

## 1. The problem in numbers (measured 4 Oct 2026)
| Fact | Value | Source (opened) |
|---|---|---|
| Public charging stations (PCS), BEE | **26,367** as on 1 Apr 2025 (tier-1 9,702 · tier-2 4,625 · tier-3 12,040) | PIB release 2118894, 4 Apr 2025 |
| PCS, Ministry of Power inputs | **29,277** (state-wise table: Karnataka 6,097 · Maharashtra 4,155 · Delhi 1,967 · Tamil Nadu 1,781 · Kerala 1,392 · Gujarat 1,208 · Telangana 1,066 …) | PIB release 2151390, 1 Aug 2025 |
| Operator claim, Statiq | "10000+ EV Chargers Installed", "1014+ Cities Across India" | statiq.in home page |
| Operator claim, Jio-bp | "2,000+ mobility stations across India" (fuel, fast EV charging, CNG …) | jiobp.com home page |
| Open data, OpenStreetMap | **<!--n:osm_n-->600<!--/n-->** `amenity=charging_station` features in India (OSM base 2026-10-04 00:26 UTC) = <!--n:osm_pct_official-->2.05%<!--/n--> of 29,277; <!--n:osm_operator_pct-->31.8%<!--/n--> have `operator`, <!--n:osm_socket_pct-->7.8%<!--/n--> any `socket:*` tag | Our Overpass run: [`components/charger_ingest/fetch_osm.py`](../components/charger_ingest/fetch_osm.py) |
| Open data, three sources linked | OSM <!--n:osm_n_in_india-->586<!--/n--> + OCM <!--n:ocm_n_in_india-->1,869<!--/n--> + Overture <!--n:ovt_n_in_india-->1,039<!--/n--> records inside India → <!--n:linked_sites-->3,325<!--/n--> candidate site clusters = <!--n:open_coverage_pct-->11.4%<!--/n--> of the official count; <!--n:sites_in_all3-->6<!--/n--> in all three | [`components/census_completeness/mse.py`](../components/census_completeness/mse.py) |
| Open data, Open Charge Map | API returns HTTP 403 without a key; the per-POI export ("experimental export of the live data", licensing per data provider) has 1,872 India POIs (export of 2026-04-22) | openchargemap/ocm-export README; our parse |
| Demand data, VAHAN 4 | Dashboard lists "All Vahan4 Running States (36/36)" and "All Vahan4 Running Office (1468/1469)"; EV fuel labels `ELECTRIC(BOV)`, `PURE EV`, `PLUG-IN HYBRID EV`, `STRONG HYBRID EV`; 76 vehicle classes incl. `E-RICKSHAW(P)`, `E-RICKSHAW WITH CART (G)` | vahan.parivahan.gov.in/vahan4dashboard (opened live) |
| Policy instruments named by government | MoP "Guidelines for Installation and Operation of Electric Vehicle Charging Infrastructure – 2024" (No. 12/2/2018-EV, 17 Sep 2024); "Guidelines for Installation and Operation of Battery Swapping and Charging Stations" (January 2025) | PIB 2151390; BEE copy of the guidelines |

**Reading.** The same quantity is reported as 25,202, 26,367 or 29,277 stations by government sources within eight months, as 52,718 by IEEFA a year later, as "10,000+ chargers" by one operator and as "2,000+ mobility stations" by another. Only ~2% of it is visible in open data. Fragmentation is not just "many apps": it is **different units, different dates and no locations in the official series**. That defines our integration design: canonical unit = *site* with a connector list, explicit as-on dates, and a measured completeness per region.

## 2. Real-data results so far (details: [methodology](../deliverables/round1-methodology.md) §2)
| Result | Value | Code |
|---|---|---|
| BEV registrations to date / in CY2025 | <!--n:nat_bev_cum-->10,550,090<!--/n--> / <!--n:nat_bev_2025-->2,356,971<!--/n--> (<!--n:nat_bev_share_2025-->8.05%<!--/n--> of all) | `eval/baseline_state_gap.py` |
| BEV per official station (national; Karnataka; Bihar; Assam) | <!--n:nat_bev_per_pcs-->360<!--/n-->; <!--n:state_bev_per_pcs_karnataka-->152<!--/n-->; <!--n:state_bev_per_pcs_bihar-->1,085<!--/n-->; <!--n:state_bev_per_pcs_assam-->1,123<!--/n--> | same |
| Capture–recapture (coverage audit) | Estimable in <!--n:mse_states-->5<!--/n--> of <!--n:mse_states_ge100-->22<!--/n--> states; there, median <!--n:mse_median_ratio-->1.27<!--/n-->× the older official count, CI covers it in <!--n:mse_states_in_ci-->4<!--/n-->; stated rule **<!--n:mse_passes-->fails<!--/n-->** narrowly; national total model-dependent (<!--n:mse_n_min_model-->14,248<!--/n-->–<!--n:mse_n_max_model-->70,921<!--/n-->), not quoted | `components/census_completeness/mse.py` |
| District allocation, Chhattisgarh point-in-time check | WAPE <!--n:cg_pit_wape-->0.30<!--/n--> vs plain BEV share <!--n:cg_pit_bevshare_wape-->0.58<!--/n-->; 90% interval contains <!--n:cg_pit_inside-->24/27<!--/n--> official counts (one state; conditional) | `components/access_gap/small_area.py` |
| Adoption forecast, held-out WAPE (pooled logit vs naive) | <!--n:c9_hold_logit-->0.157<!--/n--> vs <!--n:c9_hold_naive-->0.223<!--/n-->; CY2026 nowcast <!--n:nowcast_2026-->3,598,003<!--/n--> | `components/adoption_forecast/` |
| Maharashtra: verify-first districts (high registration pressure, thin visible supply) | <!--n:mh_verify_first-->Nagpur, Nashik, Ahilyanagar, Chhatrapati Sambhajinagar, Solapur, Amravati<!--/n--> | `components/access_gap/mh_district_gap.py` |

## 3. What governments and companies ship today
| Capability | Who ships it (opened tonight) | How (where public) | Gap in India | How we borrow / beat |
|---|---|---|---|---|
| National station registry + locator | **US DOE AFDC Station Locator**: "Find Stations", "Analyze Trends", "Build Corridors", "Charging Networks" (afdc.energy.gov/stations) | Federal registry with locator, trend analytics and corridor tools | India's BEE/MoP counts are state-wise press-release tables; BEE's EV Yatra portal did not respond from here (UNVERIFIED) | Same three views (find · trends · corridors), plus a completeness estimate per region that AFDC does not publish |
| Regional observatory | **European Alternative Fuels Observatory (EAFO)**: hosts "the full text and guidance on the Alternative Fuels Infrastructure Regulation (AFIR)" plus statistics | EU-wide observatory tied to binding infrastructure targets | No India equivalent tying counts to targets | Encode MoP 2024 norms (once verified) as benchmark layers, the way EAFO frames AFIR |
| Operator networks and apps | **Statiq** (10000+ chargers claimed, 1014+ cities); **Jio-bp pulse** (2,000+ mobility stations) | Each operator runs its own app/locator | Siloed: no common feed; units differ | Ingest via open feeds or permission; canonical *site* unit; dedupe across networks |
| Open crowd-sourced data | **OpenStreetMap** (600 India features); **Open Charge Map** (per-POI export repo; API key required) | Volunteer-mapped, open licences (OSM: ODbL) | ~2% coverage in India | Use as independent "capture" lists for completeness estimation, not as the census itself |
| Open places data built from big-tech listings | **Overture Maps places** (release 2026-09-23.1): CDLA-Permissive-2.0 / Apache-2.0 / CC0 by source (Meta, Microsoft, Foursquare, AllThePlaces …); "contains no OpenStreetMap data". In India: 391 places in category `ev_charging_station` + 659 EV chargers filed under other categories (e.g. Bolt.Earth listings as `corporate_or_business_office`) | Category-only queries miss most Indian chargers | Our third, OSM-independent list; category + strict name rule |
| Scraped operator locators (open) | **AllThePlaces** spiders publish brand locators openly (via Overture as CC0) | No spider for any Indian charging operator found (GitHub code search, 4 Oct 2026) | Contribute Indian operator spiders (with permission) → a fourth list |
| Siting / location-allocation tooling | **PySAL spopt v0.8.0**: LSCP, capacitated LSCP, backup coverage, MCLP, p-center, p-median, p-dispersion | Open-source Python | — | C11 baseline solver |
| Accessibility metrics | **PySAL access v1.1.10.post3**: FCA, 2SFCA, Enhanced 2SFCA (distance-decay weights) | Open-source Python | — | C10 baseline |
| Entity resolution at scale | **Splink**: probabilistic record linkage with DuckDB/Spark backends; examples incl. "Linking businesses", "Real time record linkage", "Evaluation from ground truth column" | Open-source (UK Ministry of Justice) | — | C4 baseline (Fellegi–Sunter) before any learned matcher |
| Hierarchical spatial index | **H3** (h3geo.org) | Open-source | — | Blocking for ER (C4) and the national grid (C6) |
| Ratchet-style auto-research | **karpathy/autoresearch**: an agent "modifies the code, trains for 5 minutes, checks if the result improved, keeps or discards, and repeats"; humans write `program.md` | Open-source | — | Our C5/C9 loops |

**UNVERIFIED leads (pages failed to open tonight; confirm before citing):** BEE EV Yatra features and API · Unified Energy Interface (UEI) / Beckn charging discovery (ueialliance.org, beckn.org) · Germany's StandortTOOL (standorttool.de) · NREL alt-fuel-stations API docs · Tata Power EZ Charge network size (page 404) · ChargeZone and PlugShare (connection errors) · MapmyIndia/Mappls EV layer (home page opened, no EV claim found in the HTML) · ET Auto report of JMK Research's 29,151 PCS for Dec 2025 (opened by a sub-agent, not re-verified by the lead) . (MoP 2024 density norms and PM E-DRIVE targets are now verified: fact-check P1, P5.)

## 4. Methods (state of the art to confirm; anchors not yet re-opened)
- **Accessibility:** two-step floating catchment (2SFCA, Luo & Wang 2003) and enhanced/Gaussian variants. The tooling is verified above (PySAL access).
- **Location-allocation:** MCLP (Church & ReVelle 1974), p-median (Hakimi), flow-refuelling location models for corridors (Hodgson 1990; Kuby & Lim 2005). Tooling verified above (spopt); corridor flows need an OD proxy (UNVERIFIED data source).
- **Entity resolution:** Fellegi–Sunter probabilistic linkage (verified tooling: Splink). The spatial-POI conflation literature (OSM vs proprietary; Overture Maps) is still to be reviewed.
- **Completeness estimation:** capture–recapture / multiple-systems estimation (Lincoln–Petersen, Chapman, log-linear models with source interactions). Applications to map/POI completeness and **any application to EV charger databases: UNVERIFIED, still to search.** Our literature check died with the agent. This is the novelty claim to verify first.
- **Adoption forecasting:** Bass diffusion / logistic per region with hierarchical pooling; validate by backtest on VAHAN annual and monthly series (data on disk).

### Verified evidence added in v2
- **Regional EV forecasting:** Flower et al., *Nature Communications* (13 Jun 2026). A Gaussian-process framework for neighbourhood-level EV adoption beats scaled-scenario, logistic-growth and linear-extrapolation baselines, significantly at horizons of 3+ years (1,294 neighbourhoods; code public). This is our candidate for RTO/district disaggregation.
- **Charger reliability** (why "installed" ≠ "usable"):
  - IEEFA's Delhi sample: 31 of 37 public chargers non-functional (83.7%);
  - Rempel et al. (Bay Area): 73.3% of 655 DC fast-charging ports functional;
  - J.D. Power 2025 (US, via secondary reports): 14% of owners had a visit without charging.

  Uptime data (MoP clause 13 energy-sold reporting) belongs in the census.
- **Kilowatt-based benchmark:** EU AFIR requires 1.3 kW of public power per battery-electric car and 0.8 kW per plug-in hybrid. India has no equivalent; we report it as a comparison benchmark, not a target.
- **Novelty search (capture–recapture on charger inventories):** none found (fact-check row 11).

## 5. Innovation room by component (summary; details in ADR 001)
| Component | Best existing practice | Room for innovation | Pick |
|---|---|---|---|
| C4 resolve + C5 completeness | Distance + name matching; raw counts | Multiple-systems estimation of unseen sites, validated on official state totals; coverage-adjusted gap metrics | **Spike 1** |
| C9 forecast + C11 requirement | CAGR; norm-based counts; MCLP | Segment- and charging-mode-aware need (home/depot/public/swap), pooled regional diffusion, queueing-based sizing | **Spike 2** |
| C1 VAHAN ingest | Manual Excel downloads | Plain-HTTP replay of the dashboard's JSF calls (done): full RTO-level refresh without a browser | Engineering win (done) |
| C10 access/gap | EVs per charger | E2SFCA + corridor spacing + coverage factor + ranked reasons | Best practice + spike inputs |
| C13 dashboard | Static choropleths | Every number clickable to its sources and as-on date | Best practice |

## 6. Open questions
1. Which charger sources can we ingest under their terms? OCM (free key) for sure; operator locators need permission; UEI if it exposes discovery.
2. Is there official guidance on the BEE vs MoP definitions (26,367 vs 29,277), and on stations vs chargers?
3. RTO → district crosswalk: is there an official mapping (MoRTH/NIC)? Otherwise manual + office geocoding.
4. What survival curves for 2W/3W/4W in India turn registrations into on-road stock?

## Sources opened tonight
| URL | What we used | Accessed |
|---|---|---|
| https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml | Coverage (36/36 states; 1,468/1,469 offices), fuel labels, vehicle classes, all VAHAN tables | 2026-10-04 |
| https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2118894 | BEE PCS 26,367 as on 1 Apr 2025, state × tier table | 2026-10-04 |
| https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2151390 | MoP 29,277 PCS state-wise; names of the MoP 2024 and battery-swapping guidelines | 2026-10-04 |
| https://overpass-api.de/api/interpreter | OSM India charging features (600) | 2026-10-04 |
| https://github.com/openchargemap/ocm-export | OCM export format and licensing note | 2026-10-04 |
| https://www.statiq.in/ | Statiq network claims | 2026-10-04 |
| https://www.jiobp.com/ | Jio-bp network claim | 2026-10-04 |
| https://afdc.energy.gov/stations | AFDC Station Locator features | 2026-10-04 |
| https://alternative-fuels-observatory.ec.europa.eu/ | EAFO scope (AFIR text and guidance) | 2026-10-04 |
| https://pysal.org/spopt/ | spopt v0.8.0 model list | 2026-10-04 |
| https://pysal.org/access/ | access v1.1.10.post3 methods (FCA, 2SFCA, E2SFCA) | 2026-10-04 |
| https://moj-analytical-services.github.io/splink/ | Splink capabilities | 2026-10-04 |
| https://h3geo.org/ | H3 grid | 2026-10-04 |
| https://github.com/karpathy/autoresearch | Ratchet-loop pattern | 2026-10-04 |
| https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2086533 | 25,202 PCS (20 Dec 2024) + state annex + Chhattisgarh district annex; PM E-DRIVE budget; NITI Aayog quote | 2026-10-04 |
| https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2060774 | PM E-DRIVE charger targets (1 Oct 2024) | 2026-10-04 |
| https://www.beeindia.gov.in/WriteReadData/L45218/2841453721548450.pdf | MoP Guidelines 2024 (No. 12/2/2018-EV): clause 11(1) density norms, clause 13 national database, UEI/OCPP/OCPI | 2026-10-04 |
| https://wri-india.org/initiatives/powering-ev-shift-building-indias-charging-ecosystem | 34,629 stations / 5.4 million EVs (Nov 2024) | 2026-10-04 |
| https://ieefa.org/articles/india-needs-make-ev-charging-more-reliable-affordable-and-accessible-accelerate-shift | 5,151 (2022) → 52,718 (Jul 2026) stations | 2026-10-04 |
| https://ieefa.org/sites/default/files/2024-09/Briefing%20Note%20-%20Upgrading%20India%27s%20Public%20EV%20Charing%20Experience_Sept2024.pdf | 12,146 stations (Feb 2024); Delhi reliability sample (83.7% non-functional) | 2026-10-04 |
| https://www.nature.com/articles/s41467-026-74155-0 | Gaussian-process neighbourhood EV forecasting (13 Jun 2026) | 2026-10-04 |
| https://www.osti.gov/servlets/purl/2327095 | Rempel et al., Bay Area DC fast-charger functionality (73.3% of 655) | 2026-10-04 |
| https://transport.ec.europa.eu/transport-themes/clean-transport/alternative-fuels-sustainable-mobility-europe/alternative-fuels-infrastructure_en | AFIR 1.3 kW per BEV / 0.8 kW per PHEV | 2026-10-04 |
| https://evchargingstations.com/chargingnews/j-d-power-ev-chargers-becoming-more-reliable/ | J.D. Power 2025 failed-visit share (secondary report) | 2026-10-04 |
| https://docs.overturemaps.org/guides/places/ | Overture places licences and sources; DuckDB access pattern | 2026-10-04 |
| https://stac.overturemaps.org/catalog.json | Overture release 2026-09-23.1 | 2026-10-04 |
| https://github.com/wmgeolab/geoBoundaries (IND ADM1/ADM2 metadata) | Boundary vintages and licences (ADM1 DataMeet/ECI CC BY 2.5 IN; ADM2 2021 Pathways Data/LGD ODbL) | 2026-10-04 |
| https://en.wikipedia.org/wiki/Manendragarh-Chirmiri-Bharatpur_district | Split from Korea district on 9 Sep 2022 (crosswalk for the Chhattisgarh validation) | 2026-10-04 |
