# Independent India vehicle LCA benchmarks opened on 2026-10-04

## What I searched

Searches targeted non-ICCT India-specific vehicle LCA / WTW+production results (2019-2026): SAE 2026-26-0235/0239, Elsevier Energy S0360544225015531, IIT/IISc reports and theses, TERI/CSTEP/CEEW/NITI/WRI India reports, and open-access papers with `India`, `life cycle`, `vehicle`, `g CO2/km`, `BEV`, `ICEV`, `two-wheeler`, and `passenger car` terms.

## What I opened and used

1. **TERI (2026), _Life Cycle Assessment Based Rating Framework for Four-Wheeler Passenger Vehicles_** (`.data/raw/benchmarks_independent/teri_lca_rating_2023.pdf`). Usable held-out **Indian car** benchmark: cradle-to-grave, 59 market vehicles, GWP100 IPCC AR6, 150,000 km lifetime, stage table (material / use / OEM manufacturing and logistics / total). It covers petrol, diesel, CNG, hybrid, and BEV cars. It is independent of ICCT as a reporting source, although the literature review cites ICCT among many sources.
2. **IIT Guwahati PhD thesis (2025), _Life Cycle Analysis (LCA) of Vehicles Powered by Clean Energy: An Indian Perspective_** (`.data/raw/benchmarks_independent/iitg_vehicle_lca_thesis_2025.pdf`). Usable held-out **Indian car** benchmark: Chapter 2 gives gasoline, BEV, and HEV hatchback/compact-SUV LCA with vehicle-cycle and fuel-cycle tables and g CO2-eq/km results over 160,000 km. Independent of ICCT as a reporting source.
3. **IIT Kanpur / Engine Research Laboratory (2023), _LCA and TCO Analyses of BEVs, HEVs, and ICEVs_** (`.data/raw/benchmarks_independent/iitk_lca_tco_2023.pdf`). Usable, but coarser, held-out **Indian car** benchmark: GREET cradle-to-grave totals for BEV/HEV/ICEV over 200,000 km, with India 2020-21 electricity mix. Independent of ICCT as a reporting source.
4. **EVS38 (2025), _Developing a Comprehensive State-level Metric for Quantifying EV GHG Emissions in India_** (`.data/raw/benchmarks_independent/evs38_state_metric_2025.pdf`). Opened but **not entered as a benchmark YAML** because it is WTW operational CO2 for electric four-wheelers vs petrol only; the paper explicitly says it does not include manufacturing/recycling, so it is not a full LCA or WTW+production benchmark.

## Leads checked but unavailable or not usable

- **SAE 2026-26-0235**: public abstract indicates an Indian passenger-car LCA, but full text is paywalled; not used.
- **SAE 2026-26-0239**: public abstract indicates a circularity/LCA review for Indian EV sector, likely not a primary numeric benchmark; full text is paywalled; not used.
- **Elsevier Energy 2025, S0360544225015531 / DOI 10.1016/j.energy.2025.135911, _Impact of electrification on two-wheelers in India..._**: ScienceDirect access was blocked/paywalled; no open PDF was found in this pass; not used.
- **Springer/ResearchGate, Jani Das 2021/2022, _Comparative life cycle GHG emission analysis of conventional and electric vehicles in India_**: identified as relevant, but Springer access returned an anti-bot page and ResearchGate PDF returned 403; not used.
- **Oxford Clean Energy 2024, _Techno-economic and environmental impact analysis of electric two-wheeler batteries in India_**: PDF requests returned 403; also appears battery-focused, not a full vehicle LCA benchmark; not used.

## Held-out benchmark usefulness

- **2W petrol vs 2.9 kWh e-scooter at ~120,000 km:** no independent open full-LCA two-wheeler benchmark was verified in this pass. The best 2W lead remains the Elsevier Energy 2025 paper, but it is UNVERIFIED/paywalled here.
- **Indian passenger cars at ~165,000 km:** TERI 2026 is strongest for petrol/diesel/CNG/BEV market vehicles (150,000 km). IIT Guwahati 2025 is also strong for petrol/BEV/hybrid hatchback and compact SUV (160,000 km). IIT Kanpur 2023 is useful for sensitivity and triangulation but assumes 200,000 km and reports grouped vehicle sets.

## Row-selection status (lead, 4 Oct 2026, after the gpt-6-astra Round-1 review)
The 8 TERI rows were picked by the benchmark agent to span powertrains (petrol, CNG, diesel, BEV). They are not a random sample, and no explicit selection rule was recorded at transcription time. Before these studies are used for anything stronger than context:
- record a selection rule (e.g. all sedan/compact rows, or all 59 vehicles);
- separate vehicle-point counts from study counts;
- reserve compatible unseen cases for any later held-out check.
