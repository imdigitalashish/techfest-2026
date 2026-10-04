# Component research: site-level digital twin + dispatch (C1–C4, C9, C10)

Code: [`components/twin_sim/`](../../components/twin_sim/README.md). All web sources were accessed on **2026-10-04**. Labels: **REAL** means agency, model or reanalysis data we downloaded. **SIMULATED** means twin output. **ASSUMPTION** means a chosen parameter with a stated range. **UNVERIFIED** means a figure seen but not confirmed at a primary source.

## 1. What is real and what is simulated

| Layer | Status | Source (opened / fetched 2026-10-04) |
|---|---|---|
| Site coordinates | REAL (OSM) | Overpass API `way[waterway][name~"Mithi\|Dahisar\|Oshiwara\|…"](18.88,72.75,19.32,73.05); out geom;`. The downstream end node of the named way is used, because OSM waterways are drawn in the direction of flow. Ways used: [420108354](https://www.openstreetmap.org/way/420108354) (Mithi), [257443428](https://www.openstreetmap.org/way/257443428) (Oshiwara), [420108348](https://www.openstreetmap.org/way/420108348) (Dahisar). Trombay: Nominatim `q=Trombay` gave node [1366794662](https://www.openstreetmap.org/node/1366794662) (a bus station), used as an **approximate** anchor for a creek-shore nullah outfall. Nominatim found no "Mahim Creek" or "Mahul Creek" objects. |
| Hourly rain 2019–2025 (Jun–Sep) | REAL (ERA5 reanalysis) | `https://archive-api.open-meteo.com/v1/archive?latitude=…&longitude=…&start_date=2019-06-01&end_date=2025-09-30&hourly=precipitation&models=era5&timezone=UTC`. The fetched seasons have no gaps. |
| Day-ahead rain forecast | REAL archived NWP | Open-Meteo Previous Runs API, `hourly=precipitation_previous_day1&models=jma_gsm` (the run issued one day earlier). Probes for 15 Jul 2019: `jma_gsm` had data; `ecmwf_ifs025`, `gfs_seamless` and `best_match` `previous_day1` were empty. `ecmwf_ifs025` did have data on 15 Jul 2024. JMA GSM was chosen because it is the only model probed that covers both the tuning and held-out years. Skill at Mithi, daily totals over Jun–Sep 2019–2025: correlation with ERA5 0.658, total bias ×1.02 (computed from the committed `data/forcing_jjas.csv.gz`). The Historical Forecast API was **not checked**: the docs fetch timed out. |
| Tide | REAL model data → harmonic prediction | Open-Meteo Marine API `hourly=sea_level_height_msl`. Probe at 19.04 N 72.80 E, July 2025: clear semidiurnal signal, daily ranges 1.67–3.99 m (neap to spring). The series is empty for 2019, 2021 and mid-2022 probes; the first value is 2022-11-23. We therefore fitted constituents with the `utide` Python package (v0.4.0; OLS, nodal corrections, 2022-11-23 → 2025-09-30, 24,600 h) and predicted 2019–2025. Fit: variance explained 0.992–0.993, RMSE 0.078–0.080 m. M2 is 1.06–1.16 m and S2 0.43–0.46 m (`data/tide_fit.json`). UHSLC was **not checked** (time). This is a model sea level, not a tide gauge. |
| Plastic load, hydraulics, boom, sensors, crews | SIMULATED with ASSUMPTION parameters | Parameter table in §3. |
| City-wide plastic flux | Brief | `_briefs/innovatex.txt` line 121: about 5 million kg per year from Mumbai's waterways. |

Spatial resolution caveat: ERA5 is 0.25°, so Mithi and Trombay share one rain cell, and Oshiwara and Dahisar share another. Mithi and Trombay also share one Open-Meteo marine cell, giving identical constituents, so Thane Creek amplification is not represented. The largest hourly ERA5 rain in the series is 27.7 mm/h. A 0.25° grid smooths convective peaks, so thresholds are expressed on this ERA5 scale.

## 2. Model (hourly, vectorised over Monte Carlo draws × sites)

- **C2 catchment load.** Generation G = L_city/(A_city·8760)·m·A kg/h. Initial stock M₀ = 24·G·d₀. Wash-off W = M(1−e^(−k_w·r)) + k_dry·M, and M ← M + G − W. This is the exponential build-up/wash-off form, with first flush.
- **C3 hydraulics.** Rational-method inflow Q_in = C·r·A/3.6 + Q_sewage. It is routed through a linear reservoir with lag k = (1.5 + 0.05·A)·mult h. Level η = tide + a·Q^0.6. Signed surface velocity v = (Q − A_tidal·dη_tide/dt)/(B·(h₀+η)), positive seaward.
- **C4 boom.**
  - On flood tide (v ≤ 0), new debris is held upstream in a "pool". On ebb (v > 0), it arrives together with k_ret·pool. This represents tidal re-floating and return.
  - Capture efficiency e(v) = e_max/(1+exp((|v|−v₅₀)/w)). Entrainment = (1−e)·arrived.
  - Captured = min(e·arrived, capacity − stored); the excess is overtopping.
  - Bypass or flood release happens when Q > Q_bypass or η > η_bypass. Then all arrivals bypass and stored debris is released at k_rel per hour.
  - On flood tide, a fraction k_ref of stored debris re-floats into the pool.
  - Clearance = min(stored, crews·rate·access).
  - Access is 1 at low water (η ≤ η_work) with |v| ≤ v_work. It is multiplied by access_poor for each violated condition, and is 0 in rain above the safety limit.
  - Invariants (tested): arrived = captured + entrainment + overtopping + bypass, and stored ≥ 0. Season mass balance: load = escaped + cleared + Δstored + Δpool.
- **C9 risk forecaster.** Issued daily at 00 UTC (05:30 IST). The twin is run with **nominal** parameters, starting from the state implied by past rain and driven by the archived JMA forecast and the harmonic tide. Outputs: 24/48 h arrivals, P(bypass), predicted access per hour, and p_overflow = 1−(1−σ((E[fill]−1)/0.15))·(1−P(bypass)). The policy never sees a draw's true parameters or the observed future rain.
- **C10 dispatch.** All policies use the same crew-hours: 2 crews × 8 h/day, one site per crew-shift (asserted).
  - P0 (status-quo fixed schedule): crew 1 at Mithi daily; crew 2 on a weekly area-weighted rotation; 08:30–16:30 IST.
  - P1 (fill-threshold): crews go to the two highest simulated-sensor fill fractions; fixed shift.
  - P2 (forecast- and tide-aware): greedy allocation by kg-at-risk = (sensed kg + w_arr·E[capture of 24 h forecast arrivals]) × (w_stock + w_bypass·P(bypass) + w_over·p_overflow). The shift start (06:30–10:30 IST) maximises predicted access, which targets low-water and slack/ebb windows.

## 3. Parameters

Every parameter, with nominal value, Monte Carlo range, unit and source or reasoning. This table is generated from `components/twin_sim/params.py`. The Monte Carlo uses 40 independent uniform draws over the ASSUMPTION ranges (seed 20261004).

| parameter | nominal | MC range | unit | kind | source / reasoning |
|---|---|---|---|---|---|
| `city_load_t_yr` | 5000 | fixed | t/yr | source | _briefs/innovatex.txt line 121 (official InnovateX statement): ~5 million kg/yr from Mumbai waterways |
| `city_area_km2` | 603 | fixed | km2 | ASSUMPTION | Greater Mumbai area, commonly quoted; UNVERIFIED in this run. Used only to scale load per km2 |
| `load_mult` | 1.0 | 0.3 – 1.5 | - | ASSUMPTION | share of the city-wide flux that is floating macroplastic reaching these outfalls; wide range |
| `stock0_days` | 30 | 10 – 60 | days of generation | ASSUMPTION | catchment stock on 1 Jun after dry-season build-up minus pre-monsoon desilting |
| `kw_per_mm` | 0.08 | 0.03 – 0.2 | 1/mm | ASSUMPTION | exponential wash-off M*(1-exp(-k*rain)) as in SWMM-style build-up/wash-off; 25 mm washes ~86% at nominal |
| `k_dry_per_h` | 0.002 | 0.0005 – 0.005 | 1/h | ASSUMPTION | dry-weather (sewage base flow) transport of floatables |
| `kg_per_item` | 0.01 | 0.005 – 0.02 | kg/item | ASSUMPTION | mean mass of a floating macroplastic item |
| `runoff_coeff` | 0.7 | 0.5 – 0.9 | - | ASSUMPTION | rational-method C for dense urban catchments |
| `k_res_mult` | 1.0 | 0.5 – 2.0 | - | ASSUMPTION | linear-reservoir lag k = (1.5 h + 0.05 h/km2 * area) * mult |
| `sewage_l_cap_day` | 150 | 100 – 200 | L/person/day | ASSUMPTION | dry-weather flow in nullahs (untreated sewage) |
| `depth_msl_m` | 2.5 | 1.5 – 4.0 | m | ASSUMPTION | channel depth below MSL at the boom line |
| `stage_coeff` | 0.05 | 0.02 – 0.1 | m/(m3/s)^0.6 | ASSUMPTION | river-flow stage rise a*Q^0.6 on top of tide |
| `tidal_store_mult` | 1.0 | 0.5 – 2.0 | - | ASSUMPTION | upstream tidal storage area (site table) multiplier; sets tidal current = A*deta/dt / section |
| `e_max` | 0.85 | 0.7 – 0.95 | - | ASSUMPTION | capture of floating items at slack water (misses submerged items) |
| `v50_ms` | 0.45 | 0.3 – 0.7 | m/s | ASSUMPTION | speed at which boom capture halves through entrainment under the skirt; oil-boom practice ~0.35-0.5 m/s normal velocity (UNVERIFIED here), diagonal booms tolerate more |
| `v_width_ms` | 0.08 | 0.05 – 0.12 | m/s | ASSUMPTION | logistic width of the entrainment curve |
| `bulk_density_kg_m3` | 150 | 80 – 300 | kg/m3 | ASSUMPTION | wet mixed floating debris retained at a boom |
| `k_refloat_per_h` | 0.03 | 0.01 – 0.08 | 1/h | ASSUMPTION | stored debris re-floated per flood-tide hour (flow reversal) |
| `k_return_per_h` | 0.3 | 0.15 – 0.5 | 1/h | ASSUMPTION | held-back/refloated debris returning to the boom per ebb hour |
| `bypass_rain_mm_h` | 12 | 8 – 20 | mm/h equiv. (ERA5 scale) | ASSUMPTION | boom opened/bypassed (flood release) when routed runoff exceeds this rain-equivalent |
| `bypass_level_m` | 2.6 | 2.3 – 3.2 | m MSL | ASSUMPTION | boom bypass/overtopping when water level exceeds this |
| `k_flood_release` | 0.3 | 0.1 – 0.6 | 1/h | ASSUMPTION | stored mass released per bypass hour |
| `n_crews` | 2 | fixed | crews | ASSUMPTION | fixed budget: 2 crews x 8 h/day for every policy (equal crew-hours) |
| `shift_h` | 8 | fixed | h | ASSUMPTION | one shift per crew per day |
| `clear_rate_kg_h` | 400 | 200 – 800 | kg/h | ASSUMPTION | crew with nets/grab at good access (low water, slack) |
| `work_v_ms` | 0.5 | 0.3 – 0.8 | m/s | ASSUMPTION | above this current, boat work at the boom is slowed |
| `work_level_m` | 0.5 | 0.0 – 1.0 | m MSL | ASSUMPTION | above this level, debris is out of reach from the bank |
| `access_poor` | 0.3 | 0.15 – 0.5 | - | ASSUMPTION | relative clearance rate when current OR level is unfavourable |
| `unsafe_rain_mm_h` | 15 | 10 – 25 | mm/h | ASSUMPTION | no work in intense rain |
| `fill_noise_sd` | 0.05 | 0.02 – 0.1 | fraction | ASSUMPTION | SIMULATED fill sensor error (camera/range sensor) |

Per-site ASSUMPTIONS (`sites.py`, `params.py`):

| site | channel width (m) | boom length (m) | boom capacity (m³) | catchment (km²) | upstream tidal storage (km²) |
|---|---|---|---|---|---|
| mithi_mahim | 70 | 90 | 60 | 73 | 0.5 |
| oshiwara_malad | 40 | 55 | 35 | 20 | 0.3 |
| dahisar_mouth | 35 | 45 | 30 | 35 | 0.25 |
| trombay_mahul | 15 | 20 | 12 | 8 | 0.05 |

The Mithi (73 km²) and Dahisar (35 km²) areas match the commonly quoted 7,295 ha and 3,488 ha. Those figures were seen only in search-result snippets; MRDPA and Wikipedia did not load (**UNVERIFIED**). Population is area × 20,000/km² (**UNVERIFIED** density).

## 4. Results (SIMULATED twin, real forcing)

Metric: escaped_kg summed over the 4 sites. For each Monte Carlo draw we compute the relative reduction vs P0; the table shows the median and 90% interval (p05–p95) over 40 draws. P2 was tuned only on 2019–2023, and the held-out years 2024–2025 were evaluated once.

**Held-out Jun–Sep 2024 + 2025** (`results/metrics.json`). Crew-hours: 3,904 per policy. Load median 964 t. Bypass 13 site-hours (policy-independent).

| policy | escaped kg, median (p05–p95) | reduction vs P0, median [90% interval] | draws better than P0 | captured fraction | cleared kg | overflow site-hours |
|---|---|---|---|---|---|---|
| P0 fixed schedule | 428,336 (144,443–961,537) | — | — | 0.461 | 435,726 | 90.5 |
| P1 fill-threshold | 455,001 (151,216–980,895) | **−3.1%** [−6.0%, −0.01%] | 2/40 | 0.444 | 424,964 | 74.5 |
| P2 forecast + tide-aware | 410,771 (146,876–917,410) | **+2.2%** [−1.5%, +13.5%] | 29/40 | 0.493 | 481,506 | 89.5 |

Tuning years 2019–2023, same 40 draws: P1 −3.2% [−5.9%, −0.3%]; P2 +1.6% [−1.1%, +11.4%], better than P0 in 31/40 draws.

**Autoresearch ratchet** (`autoresearch/results.tsv`; tuning metric = mean escaped kg over 20 draws, 2019–2023):
- Baseline P2: 1,039,816.6 kg. Best after the ratchet: 1,034,784.9 kg (−0.48%), with `w_arrival` 0.5 → 0.25.
- Ablating tide-aware timing makes it **+3.7% worse** (1,078,082.6 kg).
- Removing all forecast terms makes it +0.23% worse. No single forecast-weight change cleared the 0.1% keep threshold.

**Reading.**
1. In this twin, crews are capacity-bound: they clear about 45–50% of the load. The useful lever is clearing more kg per crew-hour by timing shifts to low-water and slack windows. Day-ahead rain forecasts add at most about 0.5%. That is because boom capacity (9 t nominal at Mithi) is overwhelmed within hours in big events whatever was cleared beforehand, and flood bypass is rare on the ERA5 rain scale.
2. Sensor-triggered dispatch by fill **fraction** (P1) is worse than an area-weighted fixed schedule. It sends crews to small booms that look full but hold little mass. Ranking by **kg at risk** fixes this.
3. The P2 gain is uncertain: its 90% interval includes zero. Treat it as a design direction, not a demonstrated saving.

## 5. Limitations and next steps
- No field calibration: every plastic-process parameter is an ASSUMPTION. The Monte Carlo covers parameter uncertainty, not structural model error.
- ERA5 smooths convective extremes. IMD/BMC gauge data would sharpen the bypass and overflow dynamics.
- Tide comes from a model fit (residual RMSE 8 cm vs the model series), with no storm surge. UHSLC and Survey of India predictions were not checked.
- There is no crew travel time, and shift length is fixed. The idea backlog (crew-hour banking for storm surges, split shifts, learned value function) is in `autoresearch/program.md`.
