# Component research: site-level digital twin + dispatch (C1–C4, C9, C10)

Code: [`components/twin_sim/`](../../components/twin_sim/README.md). All web sources were accessed on **2026-10-04**. Labels: **REAL** means agency, model or reanalysis data we downloaded. **SIMULATED** means twin output. **ASSUMPTION** means a chosen parameter with a stated range. **UNVERIFIED** means a figure seen but not confirmed at a primary source.

## 1. What is real and what is simulated

| Layer | Status | Source (opened / fetched 2026-10-04) |
|---|---|---|
| Site coordinates | REAL (OSM) | Overpass API `way[waterway][name~"Mithi\|Dahisar\|Oshiwara\|…"](18.88,72.75,19.32,73.05); out geom;`. The downstream end node of the named way is used, because OSM waterways are drawn in the direction of flow. Ways used: [420108354](https://www.openstreetmap.org/way/420108354) (Mithi), [257443428](https://www.openstreetmap.org/way/257443428) (Oshiwara), [420108348](https://www.openstreetmap.org/way/420108348) (Dahisar). Trombay: Nominatim `q=Trombay` gave node [1366794662](https://www.openstreetmap.org/node/1366794662) (a bus station), used as an **approximate** anchor for a creek-shore nullah outfall. Nominatim found no "Mahim Creek" or "Mahul Creek" objects. |
| Hourly rain 2019–2025 (Jun–Sep) | REAL (ERA5 reanalysis) | `https://archive-api.open-meteo.com/v1/archive?latitude=…&longitude=…&start_date=2019-06-01&end_date=2025-09-30&hourly=precipitation&models=era5&timezone=UTC`. The fetched seasons have no gaps. |
| Day-ahead rain forecast | REAL archived NWP | Open-Meteo Previous Runs API, `hourly=precipitation_previous_day1&models=jma_gsm` The [Previous Runs API docs](https://open-meteo.com/en/docs/previous-runs-api) (opened 2026-10-04) say `_previous_day1` "returns the value predicted 24 hours before valid time". So for valid hours t0..t0+23, the value was predicted at or before t0−1 h, before the 00 UTC decision at t0. Hours from t0+24 onward would come from predictions made after the decision, so only the first 24 hours are used. Model publication latency of a few hours may mean the last of those hours were not yet public at 00 UTC; this is minor and UNVERIFIED. Probes for 15 Jul 2019: `jma_gsm` had data; `ecmwf_ifs025`, `gfs_seamless` and `best_match` `previous_day1` were empty. `ecmwf_ifs025` did have data on 15 Jul 2024. JMA GSM was chosen because it is the only model probed that covers both the tuning and held-out years. Skill at Mithi, daily totals over Jun–Sep 2019–2025: correlation with ERA5 0.658, total bias ×1.02 (computed from the committed `data/forcing_jjas.csv.gz`). The [Historical Forecast API docs](https://open-meteo.com/en/docs/historical-forecast-api) (opened 2026-10-04) describe a series built by "stitching the first hours of each successive model run", with coverage starting around 2021–2022. That makes it a near-nowcast rather than a day-ahead forecast, and it does not cover the 2019–2020 tuning years, so it was not used. (An earlier version of this file wrongly said this API was not checked.) |
| Tide | REAL model data → harmonic prediction | Open-Meteo Marine API `hourly=sea_level_height_msl`. Probe at 19.04 N 72.80 E, July 2025: clear semidiurnal signal, daily ranges 1.67–3.99 m (neap to spring). The series is empty for 2019, 2021 and mid-2022 probes; the first value is 2022-11-23. We fitted constituents with the `utide` Python package (v0.4.0; OLS, nodal corrections) on **2022-11-23 → 2023-12-31 only** (9,696 h). This resolves 67 constituents including P1, K2, SA and SSA. M2 is 1.06–1.16 m and S2 0.43–0.46 m. The frozen fit predicts 2019–2025 (`data/tide_fit.json`). Skill and the change note are below the table. UHSLC was **not checked** (time). |
| Plastic load, hydraulics, boom, sensors, crews | SIMULATED with ASSUMPTION parameters | Parameter table in §3. |
| City-wide plastic flux | Brief | `_briefs/innovatex.txt` line 121: about 5 million kg per year from Mumbai's waterways. |

**Tide fit skill and change.** Skill, all against Open-Meteo Marine **model** sea level (not a tide gauge):
- In-sample (fit window): RMSE 0.065–0.067 m, variance explained 0.995.
- **Out-of-sample**, Jan 2024 – Sep 2025 (14,904 h the fit never saw): RMSE 0.093–0.095 m, variance explained 0.990–0.991.
- Out-of-sample Jun–Sep 2024+2025 only: RMSE 0.108–0.111 m, variance explained 0.989–0.990, bias +5.5 cm. Monsoon sea level sits above the fitted seasonal cycle.

**Changed 2026-10-04 17:25 IST** (code review gpt-6-sol, issue 2). The earlier fit used sea level through 2025-09-30, so held-out-year data leaked into the held-out tide. Its in-sample RMSE was 0.078–0.080 m. All tide-dependent results were re-run with the frozen fit: `metrics.json`, `analysis.json` and `bundle_part.json`. Nothing was retuned, and the P2 knobs (tuned on 2019–2023 with the old fit) are kept. The predicted tide moved by 4.2 cm RMS in every year.

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
- **C9 risk forecaster.** Issued daily at 00 UTC (05:30 IST). The twin is run with **nominal** parameters, starting from the state implied by past rain and driven by the archived JMA forecast and the harmonic tide. Outputs, over a causal 24-hour horizon (see the disclosure in §4): arrivals, P(bypass), predicted access per hour, and p_overflow = 1−(1−σ((E[fill]−1)/0.15))·(1−P(bypass)). The policy never sees a draw's true parameters or the observed future rain.
- **C10 dispatch.** All policies use the same crew-hours: 2 crews × 8 h/day, one site per crew-shift (asserted).
  - P0, **assumed fixed roster**: crew 1 at Mithi daily, crew 2 on a weekly area-weighted rotation, 08:30–16:30 IST. This is our proxy, not BMC's actual roster.
  - P1, **fill-fraction-ranked fixed-shift rule**: crews go to the two highest simulated-sensor fill fractions; fixed shift.
  - P2, **mass/risk-ranked, tide- and forecast-timed policy**: greedy allocation by kg-at-risk = (sensed kg + w_arr·E[capture of 24 h forecast arrivals]) × (w_stock + w_bypass·P(bypass) + w_over·p_overflow). The shift start (06:30–10:30 IST) maximises predicted access, which targets low-water and slack/ebb windows.

## 3. Parameters

Every parameter, with nominal value, Monte Carlo range, unit and source or reasoning. This table is generated from `components/twin_sim/params.py`. The Monte Carlo uses 40 independent uniform draws over the ASSUMPTION ranges (seed 20261004). Each draw is one sampled parameter setting, not a season.

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

Metric: escaped_kg summed over the 4 sites. Each of the 40 Monte Carlo draws is one sampled parameter setting. For each setting we compute the relative reduction vs P0. The table shows the median and the **central 90% scenario range across sampled parameter settings** (p05–p95). This range is not a confidence interval. P2 was tuned only on 2019–2023, and no tuning used 2024–2025. The held-out comparison was computed three times in total (see the disclosure below); the later analyses (§6–§8) reuse the same settings without retuning.

<!-- twin_sim.report:heldout_meta -->

**Held-out Jun–Sep 2024 + 2025** (`results/metrics.json`). Crew-hours: 3,904 per policy. Load median 964 t. Bypass 10 site-hours (median; policy-independent).

<!-- /twin_sim.report:heldout_meta -->

<!-- twin_sim.report:heldout -->

| policy | escaped kg, median (p05–p95) | reduction vs P0, median [central 90% scenario range] | parameter settings (of 40) better than P0 | captured fraction | cleared kg | overflow site-hours |
|---|---|---|---|---|---|---|
| P0 assumed fixed roster | 427,312 (144,044–959,175) | — | — | 0.459 | 438,862 | 87 |
| P1 fill-fraction-ranked fixed-shift rule | 448,760 (150,020–979,493) | **−3.0%** [−5.7%, +0.1%] | 3/40 | 0.446 | 428,278 | 70.5 |
| P2 mass/risk-ranked, tide- and forecast-timed | 410,977 (144,559–914,316) | **+1.9%** [−1.3%, +12.5%] | 28/40 | 0.491 | 483,638 | 88 |

<!-- /twin_sim.report:heldout -->

<!-- twin_sim.report:tuning_line -->

Tuning years 2019–2023, same 40 sampled parameter settings: P1 −3.0% [−5.8%, −0.5%]; P2 +1.4% [−0.9%, +10.3%], better than P0 in 31 of 40 parameter settings.

<!-- /twin_sim.report:tuning_line -->

**Disclosure: the held-out evaluation was run three times.** The first run (+2.2% [−1.5%, +13.5%], better in 29 of 40 parameter settings) had a look-ahead bug. The forecaster's 48-hour horizon used `precipitation_previous_day1` for hours 24–47, and those forecasts were issued after the 00 UTC decision. We cut the horizon to a causal 24 hours and changed nothing else (no knobs, no logic), then re-ran. The table shows the corrected numbers. On the tuning metric, the fix cost +0.1% (1,034,784.9 → 1,035,830.4 kg; logged in `results.tsv`). The third run (2026-10-04 17:25 IST) replaced the tide fit with one that excludes held-out-year sea level (§1). Nothing else changed, and no knobs were retuned. The tables here show the third run. Its effect on the main numbers: P2 vs P1 went from −5.6% to −5.2%, P2 vs P0 from −2.1% to −1.9%, and the tuning metric from 1,035,830.4 to 1,036,493.6 kg. The qualitative statements in §8 still hold.

**Autoresearch ratchet** (`autoresearch/results.tsv`; tuning metric = mean escaped kg over 20 draws, 2019–2023). The ledger values below were computed with the superseded tide fit; with the refit tide the frozen eval prints 1,036,493.6 kg for the same knobs:
- Baseline P2: 1,039,816.6 kg. Best after the ratchet: 1,034,784.9 kg (−0.48%), with `w_arrival` 0.5 → 0.25.
- Ablating tide-aware timing makes it **+3.7% worse** (1,078,082.6 kg).
- Removing all forecast terms makes it +0.23% worse. No single forecast-weight change cleared the 0.1% keep threshold.

**Reading** (revised after the held-out ablations in §8).
<!-- twin_sim.report:reading -->

1. In this twin, crews are capacity-bound: they clear about 44–49% of the unique input. P2's full gain over P1 splits into mass ranking instead of fill fraction (−2.1%, P1m vs P1) and everything else P2 adds (−2.8%, P2 vs P1m). Within P2, tide-aware timing gives −3.6% (vs P2_notide) and day-ahead forecasts −0.7% (vs P2_nofc). The largest single lever by median is tide-aware timing (P2 vs P2_notide). Each component's central 90% scenario range includes zero. The complete P2-vs-P1 comparison (−5.2% [−15.9%, −0.8%]) excludes zero.
2. Fill-**fraction** ranking (P1) is worse than the assumed fixed roster (+3.0% [−0.1%, +5.7%]), because it sends crews to small booms that look full but hold little mass. A sensor-only **mass**-ranked rule (P1m) is about level with the roster: +0.4% [−0.6%, +2.7%]. The roster is itself mass-aware, since one crew is at the largest site every day.
3. The P2 gain vs P0 is uncertain: its central 90% scenario range includes zero (−1.9% [−12.5%, +1.3%]). Treat it as a design direction, not a demonstrated saving.

<!-- /twin_sim.report:reading -->

## 5. Limitations and next steps
- No field calibration: every plastic-process parameter is an ASSUMPTION. The Monte Carlo covers parameter uncertainty, not structural model error.
- ERA5 smooths convective extremes. IMD/BMC gauge data would sharpen the bypass and overflow dynamics.
- Tide comes from a harmonic fit to model sea level (2022-11-23 → 2023-12-31), with no storm surge. Its error is 6.5 cm in-sample and 9.5 cm out-of-sample (11 cm in Jun–Sep) against the model series. This is not gauge validation. The twin's "true" water level is the prediction itself, so policy and world share the tide. UHSLC and Survey of India predictions were not checked.
- There is no crew travel time, and shift length is fixed. The idea backlog (crew-hour banking for storm surges, split shifts, learned value function) is in `autoresearch/program.md`.

## 6. Held-out analysis: escape causes, paired comparisons, FWCE, fail-open fuse SENSITIVITY (SIMULATED)

Source: `components/twin_sim/results/analysis.json` (label SIMULATED), reproduced with `cd innovatex-t3-coastal-plastic/components && python -m twin_sim.analysis`.

Setup: held-out Jun–Sep 2024+2025, 4 sites summed. The 40 sampled parameter settings, seed, P2 knobs and crew budget (2 crews × 8 h/day) are the same as `metrics.json`, and nothing was retuned. The analysis checks that its escaped-kg medians equal `metrics.json` and that the mass-balance error is 0 kg.

Notation: values are median [p05–p95], the central 90% scenario range across the 40 sampled parameter settings. "Arrived" is the contract's `arrived_kg` at the boom, which also counts re-arrivals of re-floated debris.

**Escape by cause** (kg; share of escaped / share of arrived, medians):

<!-- twin_sim.report:causes -->

| policy | entrainment | overtopping | bypass / release | escaped total |
|---|---|---|---|---|
| P0 | 403,136 [111,511–803,330]; 92.1% / 33.3% | 35,475 [0–195,298]; 6.2% / 2.3% | 1,446 [0–41,351]; 0.4% / 0.1% | 427,312 [144,044–959,175] |
| P1 | 410,344 [113,606–822,685]; 91.7% / 33.4% | 32,970 [0–201,474]; 6.4% / 2.1% | 1,768 [0–45,285]; 0.4% / 0.1% | 448,760 [150,020–979,493] |
| P2 | 396,849 [112,910–759,069]; 93.1% / 33.2% | 29,396 [0–181,670]; 5.5% / 1.6% | 1,812 [0–39,976]; 0.5% / 0.1% | 410,977 [144,559–914,316] |

<!-- /twin_sim.report:causes -->

<!-- twin_sim.report:causes_note -->

The central 90% scenario ranges of the shares are in the JSON. For entrainment's share of escaped they span about [65–100%]. The P2 figure (93.1%) is the P2 scenario with the current release behaviour and the boom normal to the flow (θ = 90°). "Entrainment" here includes the assumed slack-water floor (1 − e_max); §7 splits it.

<!-- /twin_sim.report:causes_note -->

**Re-floating** is a re-exposure flux, not an escape term: the debris re-arrives at the boom on the ebb.
<!-- twin_sim.report:refloat -->

- Tidal re-float: P0 299,408 kg (24.5% of arrived), P1 341,731 kg (27.3% of arrived), P2 258,452 kg (23.0% of arrived).
- Flood release: 654, 1,056, 1,102 kg respectively (P0, P1, P2).

<!-- /twin_sim.report:refloat -->

**Paired per-draw difference in escaped kg** (same draw, same sensor noise):

<!-- twin_sim.report:paired -->

| comparison | median | central 90% scenario range | parameter settings (of 40) where the first is lower |
|---|---|---|---|
| P2 vs P1 | −5.2% | [−15.9%, −0.8%] | 39 |
| P2 vs P0 (matches §4) | −1.9% | [−12.5%, +1.3%] | 28 |
| P1 vs P0 | +3.0% | [−0.1%, +5.7%] | 3 |

<!-- /twin_sim.report:paired -->

**FWCE** = (cleared + stored at 30 Sep) ÷ catchment load, counting each kg once:

<!-- twin_sim.report:fwce -->

| policy | FWCE | for comparison: gross captured ÷ arrived |
|---|---|---|
| P0 | 45.8% [31.3%–69.7%] | 63.9% |
| P1 | 44.4% [29.6%–69.3%] | 63.5% |
| P2 | 49.0% [30.6%–69.9%] | 64.2% |

<!-- /twin_sim.report:fwce -->

**Fail-open fuse / one-way pocket: SENSITIVITY, assumption-driven, not evidence.** All rows use policy P2. Variants:
- (a) current release behaviour;
- (b) fuse: at release, only the arriving flux passes and the pocket keeps its catch;
- (c) fuse plus tidal re-float × 0.5 or × 0.2. Re-float × 1 is identical to (b) by construction.

<!-- twin_sim.report:fuse -->

| variant | escaped kg | Δ escaped vs (a), paired | settings (of 40) lower than (a) | FWCE | Δ FWCE vs (a), pp |
|---|---|---|---|---|---|
| (a) current release | 410,977 [144,559–914,316] | — | — | 49.0% [30.6%–69.9%] | — |
| (b) fuse | 410,782 [137,115–914,239] | −0.1% [−1.4%, +0.0%] | 30 | 49.4% [30.6%–69.9%] | +0.0 [+0.0, +0.7] |
| (c) fuse + re-float × 0.5 | 386,302 [125,616–884,583] | −5.1% [−9.6%, −1.5%] | 40 | 51.2% [32.9%–72.8%] | +2.6 [+0.9, +4.1] |
| (c) fuse + re-float × 0.2 | 369,801 [117,574–858,345] | −9.3% [−16.1%, −2.4%] | 40 | 53.7% [35.8%–74.8%] | +4.5 [+1.3, +7.0] |

<!-- /twin_sim.report:fuse -->

**Caveats.**
<!-- twin_sim.report:s6_caveats -->

- **Circularity.** escaped_kg is computed by the same assumed process model that the policies act on. These results show relative value under the stated assumptions; they are not field evidence. Field calibration comes in Round 2.
- **The cause split is set by assumptions.**
  - "Entrainment" means every non-captured arrival outside bypass hours. That includes the (1 − e_max) share assumed to pass under the boom even at slack water.
  - Overtopping depends on the assumed boom capacity and debris bulk density.
- **The fuse matters little here** (−0.1% median). Release is rare: on the ERA5 0.25° rain scale there are 10 bypass site-hours in 2024–2025 (median). With gauge-scale rain peaks the fuse could matter more (UNTESTED).
- **The pocket rows scale the assumed tidal re-float rate** (k_refloat 0.01–0.08 /h). Keeping more catch changes overtopping (P2 median 29.4 t → 42.1 t → 48.3 t), and the net figures above include this.
- **Still omitted from the twin:** travel time between sites, minimum clearance duration, gated (flap-gate) outfalls and a perfect-foresight oracle policy. Boom angle is covered only as a sensitivity (§7).

<!-- /twin_sim.report:s6_caveats -->

## 7. Entrainment split, exposure and boom angle (SIMULATED; angle = SENSITIVITY)

Source: `results/analysis.json`, keys `entrainment_split`, `exposure_P2_nominal` and `boom_angle_sensitivity_P2`. Reproduce with `cd innovatex-t3-coastal-plastic/components && python -m twin_sim.analysis`.

Setup: held-out Jun–Sep 2024+2025, 40 sampled parameter settings, nothing retuned. Values are median [central 90% scenario range across sampled parameter settings].

**Assumed capture losses dominate this twin; boom angle and retention are candidate field experiments, not findings.**

**Entrainment split** (current boom, θ = 90°):

<!-- twin_sim.report:split -->

| policy | slack-water floor (1 − e_max)·arrived: kg; share of escaped | velocity-driven (e_max − e)·arrived: kg; share of escaped |
|---|---|---|
| P0 | 179.2 t; 51.1% [14.2–79.9] | 157.8 t; 39.0% [9.8–80.2] |
| P1 | 184.0 t; 50.7% [14.1–79.8] | 162.3 t; 39.0% [9.6–80.3] |
| P2 | 178.6 t; 50.7% [14.4–81.6] | 151.4 t; 39.7% [9.9–80.0] |

<!-- /twin_sim.report:split -->

<!-- twin_sim.report:split_summary -->

In this twin, 50.7% of what escapes (P2, median) is the assumed floor: items assumed to pass under the boom even at slack water (e_max 0.70–0.95, an ASSUMPTION). Velocity-driven entrainment is 39.7%. The deck should not present the 93.1% entrainment share as velocity entrainment.

<!-- /twin_sim.report:split_summary -->

**Exposure** (P2, nominal parameters): the share of site-hours and of arrived kg with |v|·sin θ > v50 = 0.45 m/s.

<!-- twin_sim.report:exposure -->

| θ | share of site-hours | share of arrived kg |
|---|---|---|
| 90° (current) | 13.9% | 14.1% |
| 45° | 4.5% | 4.1% |
| 30° | 0.79% | 0.44% |
| 20° | 0.03% | 0.02% |

<!-- /twin_sim.report:exposure -->

<!-- twin_sim.report:exposure_sites -->

By site at 90° (hours / kg): Mithi 14.8% / 14.5%, Oshiwara 20.1% / 14.9%, Dahisar 20.1% / 16.9%, Trombay 0.7% / 0.6%. Velocity loss is not confined to |v| > v50: the assumed logistic curve already loses about 12% of e_max at v50 − 2w, so the velocity-driven share of escape (39.7%) is larger than the exposure share of arrived kg (14.1%).

<!-- /twin_sim.report:exposure_sites -->

**Boom angle θ (SENSITIVITY, P2).** e(v) uses |v|·sin θ, with e_max unchanged. Each row is a paired comparison with θ = 90° on the same hardware.

<!-- twin_sim.report:angle -->

| hardware | θ | escaped (t) | Δ escaped vs θ = 90° | settings (of 40) lower | Δ escaped vs current boom (a, θ = 90°) | FWCE | Δ FWCE vs θ = 90° (pp) | velocity share of escaped |
|---|---|---|---|---|---|---|---|---|
| (a) current release | 90° | 411.0 [144.6–914.3] | — | — | — | 49.0% [30.6%–69.9%] | — | 39.7% |
|  | 45° | 379.0 [131.5–880.9] | −10.5% [−20.8%, −0.7%] | 40 | −10.5% | 54.9% [38.5%–75.6%] | +5.7 [+0.4, +12.4] | 22.2% |
|  | 30° | 373.1 [119.8–862.3] | −15.3% [−38.3%, −0.6%] | 40 | −15.3% | 59.2% [40.0%–77.2%] | +8.1 [+0.3, +22.9] | 10.2% |
|  | 20° | 371.9 [108.9–846.6] | −17.8% [−49.7%, −0.8%] | 40 | −17.8% | 62.5% [40.2%–79.0%] | +8.9 [+0.5, +29.5] | 4.8% |
| (c) fuse + re-float ×0.5 | 90° | 386.3 [125.6–884.6] | — | — | −5.1% [−9.6%, −1.5%] | 51.2% [32.9%–72.8%] | — | 38.5% |
|  | 45° | 353.6 [120.9–856.8] | −11.1% [−22.0%, −0.5%] | 40 | −17.0% [−28.8%, −4.8%] | 58.0% [40.3%–78.4%] | +5.5 [+0.2, +12.4] | 21.9% |
|  | 30° | 343.2 [110.3–821.1] | −16.7% [−40.2%, −0.9%] | 40 | −22.0% [−41.8%, −5.5%] | 62.1% [40.6%–79.9%] | +7.8 [+0.4, +23.4] | 9.5% |
|  | 20° | 342.2 [103.1–802.1] | −19.2% [−52.8%, −1.0%] | 40 | −23.9% [−54.9%, −5.6%] | 66.2% [41.0%–81.2%] | +8.9 [+0.5, +28.9] | 4.5% |

<!-- /twin_sim.report:angle -->

**Caveats.**
<!-- twin_sim.report:s7_caveats -->

- **Not independent confirmation.** Angle acts only through the same assumed capture curve e(|v|·sin θ). Its benefit is the velocity-driven share by construction, so it cannot confirm that mechanism.
- **v50 is borrowed.** It is transferred from oil-boom practice (UNVERIFIED ASSUMPTION, 0.30–0.70 m/s).
- **Diminishing returns.** −10.5% at 45° vs −17.8% at 20° (median, current hardware). Boom length grows as 1/sin θ (×1.41 at 45°, ×2 at 30°, ×2.92 at 20°). Capacity, cost and mooring loads are held fixed or not modelled, and P2's forecaster still assumes θ = 90°.
- **The floor is untouched.** The slack-water floor does not change with angle or dispatch. Testing e_max at slack water is the first field experiment.
- **Circularity** (§6) applies.

<!-- /twin_sim.report:s7_caveats -->

## 8. Held-out ablations and the mass boundary (SIMULATED; review findings 3 and 11)

Source: `results/analysis.json`, keys `ablations` and `mass_boundary`. Same setup as §7; nothing was retuned, and all policies spend the same crew-hours.

Ablation policies:
- **P1m**, sensor-only mass-ranked fixed-shift rule. Greedy on sensed kg (fill × design capacity), with P1's 08:30 IST shift; no tide, no forecast.
- **P2_notide**: P2 with tide-aware timing off (fixed 08:30 IST start; allocation unchanged).
- **P2_nofc**: P2 with forecast terms off. It ranks on sensed kg only, and takes timing from tide-only predicted access.

Paired escaped kg:

<!-- twin_sim.report:ablations -->

| comparison | isolates | median | central 90% scenario range | settings (of 40) where the first is lower |
|---|---|---|---|---|
| P1m vs P1 | mass vs fill-fraction ranking (sensor-only, fixed shift) | −2.1% | [−4.0%, +0.2%] | 37 |
| P1m vs P0 | sensor-only mass ranking vs assumed fixed roster | +0.4% | [−0.6%, +2.7%] | 12 |
| P2 vs P1m | everything P2 adds beyond mass-ranked sensors | −2.8% | [−12.5%, +0.9%] | 34 |
| P2 vs P2_notide | tide-aware timing, within P2 | −3.6% | [−15.1%, +0.5%] | 34 |
| P2 vs P2_nofc | forecast terms, within P2 | −0.7% | [−2.0%, +1.0%] | 29 |
| P2_nofc vs P1m | tide timing on top of mass ranking, no forecasts | −2.2% | [−12.6%, +0.4%] | 34 |
| P2_notide vs P1m | forecast/risk terms without timing | −0.5% | [−1.4%, +6.2%] | 25 |
| P2 vs P1 | the complete policy comparison | −5.2% | [−15.9%, −0.8%] | 39 |

<!-- /twin_sim.report:ablations -->

<!-- twin_sim.report:ablation_policies -->

| policy | escaped (t) | FWCE | cleared share of unique input |
|---|---|---|---|
| P0 assumed fixed roster | 427.3 [144.0–959.2] | 45.8% | 45.5% |
| P1 fill-fraction-ranked fixed-shift rule | 448.8 [150.0–979.5] | 44.4% | 44.0% |
| P1m sensor-only mass-ranked | 426.5 [145.0–967.5] | 45.6% | 45.4% |
| P2_notide | 446.8 [158.1–962.0] | 46.1% | 45.8% |
| P2_nofc | 414.6 [147.5–920.0] | 48.6% | 48.4% |
| P2 mass/risk-ranked, tide- and forecast-timed | 411.0 [144.6–914.3] | 49.0% | 48.7% |

<!-- /twin_sim.report:ablation_policies -->

**What can be claimed.**
<!-- twin_sim.report:claims -->

- The complete P2 policy vs the fill-fraction rule: −5.2% [−15.9%, −0.8%], lower in 39 of 40 settings; the range excludes zero.
- Against the assumed roster: −1.9% [−12.5%, +1.3%]; the range includes zero, so this is uncertain.
- The largest single held-out lever by median is tide-aware timing (P2 vs P2_notide). Tide timing within P2: −3.6% [−15.1%, +0.5%], lower in 34 of 40 settings; **not separately established** (range includes zero).
- Sensors alone vs the assumed roster: ranked by fraction +3.0% [−0.1%, +5.7%], by mass +0.4% [−0.6%, +2.7%]. This may differ with more sites or a roster that is not mass-aware (UNTESTED).

<!-- /twin_sim.report:claims -->

**Mass boundary** (finding 11). Each kg is counted once and re-arrivals are excluded. Unique input = escaped + cleared + stored in the boom at 30 Sep + held upstream at 30 Sep. Values are summed over the two monsoons.

<!-- twin_sim.report:boundary -->

| policy | unique input (t) | cleared = removal (t) | stored at 30 Sep = temporary retention (t) | held upstream at 30 Sep (t) | escaped (t) |
|---|---|---|---|---|---|
| P0 | 964.4 [349.6–1,388.1] | 438.9 [150.4–774.1] | 2.9 [0.8–33.3] | 1.2 [0.3–4.3] | 427.3 [144.0–959.2] |
| P1 | 964.4 [349.6–1,388.1] | 428.3 [141.8–762.7] | 2.9 [0.5–33.9] | 1.3 [0.4–4.2] | 448.8 [150.0–979.5] |
| P2 | 964.4 [349.6–1,388.1] | 483.6 [146.4–788.7] | 2.7 [0.6–24.6] | 1.2 [0.3–3.9] | 411.0 [144.6–914.3] |

<!-- /twin_sim.report:boundary -->

<!-- twin_sim.report:boundary_notes -->

- FWCE (§6) = (cleared + stored) ÷ unique input. For P2 that is 48.7% removal plus 0.3% retention, so FWCE here is almost entirely crew removal.
- Removal is not final diversion. What happens to cleared material (sorting, recycling, landfill) is outside the twin.
- Each monsoon starts with an empty boom and empty upstream pool. This is an ASSUMPTION: pre-monsoon clearance.
- The twin's mass is generic floating debris, scaled from the brief's city-wide plastic figure. It is not specific to flexible packaging, and there is no moisture correction; the wet bulk density is used only for boom volume.

<!-- /twin_sim.report:boundary_notes -->

## 9. Dashboard export (`results/bundle_part.json`, SIMULATED)

Built by `python -m twin_sim.run` (or `--bundle-only` from the committed `metrics.json`) and validated against `DashboardBundle`. It is about 3.9 MB.

- **Window.** 2025-08-14 00:00 UTC → 2025-08-20 23:00 UTC (05:30 IST on 14 Aug to 04:29 IST on 21 Aug). This is the held-out 2025 Jun–Sep 7-day window, aligned to 00 UTC days, with the most ERA5 rain: 279.3 mm, mean of the 4 sites. It is recorded in `metrics["twin_sim.window"]`.
- **Forecasts**, issued 00 UTC:
  - 24 h horizon every day. This is the P2 policy's forecaster.
  - 48 h horizon on the 7 window days. Hours 0–23 use JMA GSM `precipitation_previous_day1` and hours 24–47 use `precipitation_previous_day2`. Both are predicted at least 24 h / 48 h before their valid time, so they were issued before the decision. The 48 h export is for the dashboard only; the policies still use 24 h.
- **Plans.** P0, P1 and P2 every day, issued 00 UTC. Each comes from its own nominal-parameter run.
- **Fill.** True fill is `interceptor[].fill_fraction` (hourly). Sensed fill (simulated sensor with noise) is `telemetry[].fill.fill_fraction`: hourly inside the window, 6-hourly elsewhere. At 00 UTC the sensed value is exactly the reading the P2 dispatcher used.

