# Landscape — EV Infra Map India (v1, 4 Oct 2026)

> **Scope of this version.** Written under Lean Mode. 7 of 9 research sub-agents died tonight on model-side timeouts, and the other two had not reported at the time of writing. So this version cites **only pages the lead opened tonight** (fetched over HTTP; cached in gitignored `.cache/sources/`) plus our own measured runs. Pages that failed to open are listed as **UNVERIFIED** leads. Classic method papers are named as anchors to confirm, not as citations. The per-component research (`research/components/*.md`) is folded into §4–§5 for now.

## 1. The problem in numbers (measured 4 Oct 2026)
| Fact | Value | Source (opened) |
|---|---|---|
| Public charging stations (PCS), BEE | **26,367** as on 1 Apr 2025 (tier-1 9,702 · tier-2 4,625 · tier-3 12,040) | PIB release 2118894, 4 Apr 2025 |
| PCS, Ministry of Power inputs | **29,277** (state-wise table: Karnataka 6,097 · Maharashtra 4,155 · Delhi 1,967 · Tamil Nadu 1,781 · Kerala 1,392 · Gujarat 1,208 · Telangana 1,066 …) | PIB release 2151390, 1 Aug 2025 |
| Operator claim, Statiq | "10000+ EV Chargers Installed", "1014+ Cities Across India" | statiq.in home page |
| Operator claim, Jio-bp | "2,000+ mobility stations across India" (fuel, fast EV charging, CNG …) | jiobp.com home page |
| Open data, OpenStreetMap | **600** `amenity=charging_station` features in India (OSM base 2026-10-04 00:26 UTC) = **2.05%** of 29,277; 31.8% have `operator`, 7.8% any `socket:*` tag | Our Overpass run: [`components/charger_ingest/fetch_osm.py`](../components/charger_ingest/fetch_osm.py) |
| Open data, Open Charge Map | API returns HTTP 403 without a key; OCM also publishes an "experimental export of the live data" as one file per POI, with licensing per data provider | openchargemap/ocm-export README |
| Demand data, VAHAN 4 | Dashboard lists "All Vahan4 Running States (36/36)" and "All Vahan4 Running Office (1468/1469)"; EV fuel labels `ELECTRIC(BOV)`, `PURE EV`, `PLUG-IN HYBRID EV`, `STRONG HYBRID EV`; 76 vehicle classes incl. `E-RICKSHAW(P)`, `E-RICKSHAW WITH CART (G)` | vahan.parivahan.gov.in/vahan4dashboard (opened live) |
| Policy instruments named by government | MoP "Guidelines for Installation and Operation of Electric Vehicle Charging Infrastructure – 2024" (September 2024); "Guidelines for Installation and Operation of Battery Swapping and Charging Stations" (January 2025) | PIB 2151390 (norm values themselves: UNVERIFIED tonight) |

**Reading.** The same quantity is reported as 26,367 or 29,277 stations by two government sources four months apart, as "10,000+ chargers" by one operator and as "2,000+ mobility stations" by another. Only ~2% of it is visible in open data. Fragmentation is not just "many apps": it is **different units, different dates and no locations in the official series**. That defines our integration design: canonical unit = *site* with a connector list, explicit as-on dates, and a measured completeness per region.

## 2. Our first real-data result (walking skeleton v0)
BEV registrations (VAHAN "Till Today", `ELECTRIC(BOV)` + `PURE EV`) per official PCS (PIB 2151390), all 36 states/UTs matched. Full table: [`eval/results/state_gap_baseline.csv`](../eval/results/state_gap_baseline.csv). Reproduce: see the header of [`eval/baseline_state_gap.py`](../eval/baseline_state_gap.py).

| Large states (>3 lakh BEV registrations) | BEV regs till today | Official PCS | BEV per PCS |
|---|---|---|---|
| Assam | 386,338 | 344 | 1,123.1 |
| Bihar | 565,118 | 521 | 1,084.7 |
| Uttar Pradesh | 1,842,283 | 2,326 | 792.0 |
| Odisha | 346,713 | 623 | 556.5 |
| Madhya Pradesh | 519,491 | 1,147 | 452.9 |
| Tamil Nadu | 721,587 | 1,781 | 405.2 |
| Maharashtra | 1,185,108 | 4,155 | 285.2 |
| Delhi | 547,611 | 1,967 | 278.4 |
| Karnataka | 928,891 | 6,097 | 152.4 |

Caveats: registrations ≠ on-road stock (no deregistration feed). The PCS counts are from 1 Aug 2025 while VAHAN is as of 4 Oct 2026, so ratios are inflated by ~14 months of EV growth (to be aligned using VAHAN monthly series). The ratio ignores the segment mix (hypothesis in ADR 001: e-rickshaw-heavy states look worse than they are).

## 3. What governments and companies ship today
| Capability | Who ships it (opened tonight) | How (where public) | Gap in India | How we borrow / beat |
|---|---|---|---|---|
| National station registry + locator | **US DOE AFDC Station Locator**: "Find Stations", "Analyze Trends", "Build Corridors", "Charging Networks" (afdc.energy.gov/stations) | Federal registry with locator, trend analytics and corridor tools | India's BEE/MoP counts are state-wise press-release tables; BEE's EV Yatra portal did not respond from here (UNVERIFIED) | Same three views (find · trends · corridors), plus a completeness estimate per region that AFDC does not publish |
| Regional observatory | **European Alternative Fuels Observatory (EAFO)**: hosts "the full text and guidance on the Alternative Fuels Infrastructure Regulation (AFIR)" plus statistics | EU-wide observatory tied to binding infrastructure targets | No India equivalent tying counts to targets | Encode MoP 2024 norms (once verified) as benchmark layers, the way EAFO frames AFIR |
| Operator networks and apps | **Statiq** (10000+ chargers claimed, 1014+ cities); **Jio-bp pulse** (2,000+ mobility stations) | Each operator runs its own app/locator | Siloed: no common feed; units differ | Ingest via open feeds or permission; canonical *site* unit; dedupe across networks |
| Open crowd-sourced data | **OpenStreetMap** (600 India features); **Open Charge Map** (per-POI export repo; API key required) | Volunteer-mapped, open licences (OSM: ODbL) | ~2% coverage in India | Use as independent "capture" lists for completeness estimation, not as the census itself |
| Siting / location-allocation tooling | **PySAL spopt v0.8.0**: LSCP, capacitated LSCP, backup coverage, MCLP, p-center, p-median, p-dispersion | Open-source Python | — | C11 baseline solver |
| Accessibility metrics | **PySAL access v1.1.10.post3**: FCA, 2SFCA, Enhanced 2SFCA (distance-decay weights) | Open-source Python | — | C10 baseline |
| Entity resolution at scale | **Splink**: probabilistic record linkage with DuckDB/Spark backends; examples incl. "Linking businesses", "Real time record linkage", "Evaluation from ground truth column" | Open-source (UK Ministry of Justice) | — | C4 baseline (Fellegi–Sunter) before any learned matcher |
| Hierarchical spatial index | **H3** (h3geo.org) | Open-source | — | Blocking for ER (C4) and the national grid (C6) |
| Ratchet-style auto-research | **karpathy/autoresearch**: an agent "modifies the code, trains for 5 minutes, checks if the result improved, keeps or discards, and repeats"; humans write `program.md` | Open-source | — | Our C5/C9 loops |

**UNVERIFIED leads (pages failed to open tonight; confirm before citing):** BEE EV Yatra features and API · Unified Energy Interface (UEI) / Beckn charging discovery (ueialliance.org, beckn.org) · Germany's StandortTOOL (standorttool.de) · NREL alt-fuel-stations API docs · Tata Power EZ Charge network size (page 404) · ChargeZone and PlugShare (connection errors) · MapmyIndia/Mappls EV layer (home page opened, no EV claim found in the HTML) · ET Auto report of JMK Research's 29,151 PCS for Dec 2025 (opened by a sub-agent, not re-verified by the lead) · MoP 2024 spacing/density norms · PM E-DRIVE charger targets.

## 4. Methods (state of the art to confirm; anchors not yet re-opened)
- **Accessibility:** two-step floating catchment (2SFCA, Luo & Wang 2003) and enhanced/Gaussian variants. The tooling is verified above (PySAL access).
- **Location-allocation:** MCLP (Church & ReVelle 1974), p-median (Hakimi), flow-refuelling location models for corridors (Hodgson 1990; Kuby & Lim 2005). Tooling verified above (spopt); corridor flows need an OD proxy (UNVERIFIED data source).
- **Entity resolution:** Fellegi–Sunter probabilistic linkage (verified tooling: Splink). The spatial-POI conflation literature (OSM vs proprietary; Overture Maps) is still to be reviewed.
- **Completeness estimation:** capture–recapture / multiple-systems estimation (Lincoln–Petersen, Chapman, log-linear models with source interactions). Applications to map/POI completeness and **any application to EV charger databases: UNVERIFIED, still to search.** Our literature check died with the agent. This is the novelty claim to verify first.
- **Adoption forecasting:** Bass diffusion / logistic per region with hierarchical pooling; validate by backtest on VAHAN annual and monthly series (data on disk).

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
