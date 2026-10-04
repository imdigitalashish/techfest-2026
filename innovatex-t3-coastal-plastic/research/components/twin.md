# Component research: site-level digital twin + dispatch (C1–C4, C9, C10)

Code: [`components/twin_sim/`](../../components/twin_sim/README.md). All web sources were accessed on **2026-10-04**. Labels: **REAL** means agency, model or reanalysis data we downloaded. **SIMULATED** means twin output. **ASSUMPTION** means a chosen parameter with a stated range. **UNVERIFIED** means a figure seen but not confirmed at a primary source.

## 1. What is real and what is simulated

| Layer | Status | Source (opened / fetched 2026-10-04) |
|---|---|---|
| Site coordinates | REAL (OSM) | Overpass API `way[waterway][name~"Mithi\|Dahisar\|Oshiwara\|…"](18.88,72.75,19.32,73.05); out geom;`. The downstream end node of the named way is used, because OSM waterways are drawn in the direction of flow. Ways used: [420108354](https://www.openstreetmap.org/way/420108354) (Mithi), [257443428](https://www.openstreetmap.org/way/257443428) (Oshiwara), [420108348](https://www.openstreetmap.org/way/420108348) (Dahisar). Trombay: Nominatim `q=Trombay` gave node [1366794662](https://www.openstreetmap.org/node/1366794662) (a bus station), used as an **approximate** anchor for a creek-shore nullah outfall. Nominatim found no "Mahim Creek" or "Mahul Creek" objects. |
| Hourly rain 2019–2025 (Jun–Sep) | REAL (ERA5 reanalysis) | `https://archive-api.open-meteo.com/v1/archive?latitude=…&longitude=…&start_date=2019-06-01&end_date=2025-09-30&hourly=precipitation&models=era5&timezone=UTC`. The fetched seasons have no gaps. |
| Day-ahead rain forecast | REAL archived NWP | Open-Meteo Previous Runs API, `hourly=precipitation_previous_day1&models=jma_gsm` The [Previous Runs API docs](https://open-meteo.com/en/docs/previous-runs-api) (opened 2026-10-04) say `_previous_day1` "returns the value predicted 24 hours before valid time". So for valid hours t0..t0+23, the value was predicted at or before t0−1 h, before the 00 UTC decision at t0. Hours from t0+24 onward would come from predictions made after the decision, so only the first 24 hours are used. Model publication latency of a few hours may mean the last of those hours were not yet public at 00 UTC; this is minor and UNVERIFIED. Probes for 15 Jul 2019: `jma_gsm` had data; `ecmwf_ifs025`, `gfs_seamless` and `best_match` `previous_day1` were empty. `ecmwf_ifs025` did have data on 15 Jul 2024. JMA GSM was chosen because it is the only model probed that covers both the tuning and held-out years. Skill at Mithi, daily totals over Jun–Sep 2019–2025: correlation with ERA5 0.658, total bias ×1.02 (computed from the committed `data/forcing_jjas.csv.gz`). The [Historical Forecast API docs](https://open-meteo.com/en/docs/historical-forecast-api) (opened 2026-10-04) describe a series built by "stitching the first hours of each successive model run", with coverage starting around 2021–2022. That makes it a near-nowcast rather than a day-ahead forecast, and it does not cover the 2019–2020 tuning years, so it was not used. (An earlier version of this file wrongly said this API was not checked.) |
| Tide | REAL model data → harmonic prediction | Open-Meteo Marine API `hourly=sea_level_height_msl`. Probe at 19.04 N 72.80 E, July 2025: clear semidiurnal signal, daily ranges 1.67–3.99 m (neap to spring). The series is empty for 2019, 2021 and mid-2022 probes; the first value is 2022-11-23. We therefore fitted constituents with the `utide` Python package (v0.4.0; OLS, nodal corrections, 2022-11-23 → 2025-09-30, 24,600 h) and predicted 2019–2025. Fit: variance explained 0.992–0.993, RMSE 0.078–0.080 m. This RMSE is an **in-sample fit residual** against Open-Meteo **model** sea level over the fit window (2022-11-23 → 2025-09-30, which overlaps the held-out years). It is not validation against a tide gauge. We treat the tide as a known astronomical prediction, as published tide tables would be. M2 is 1.06–1.16 m and S2 0.43–0.46 m (`data/tide_fit.json`). UHSLC was **not checked** (time). This is a model sea level, not a tide gauge. |
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

Metric: escaped_kg summed over the 4 sites. Each of the 40 Monte Carlo draws is one sampled parameter setting. For each setting we compute the relative reduction vs P0. The table shows the median and the **central 90% scenario range across sampled parameter settings** (p05–p95). This range is not a confidence interval. P2 was tuned only on 2019–2023, and no tuning used 2024–2025. The held-out comparison was computed twice in total (see the disclosure below); the later analyses (§6–§8) reuse the same settings without retuning.

**Held-out Jun–Sep 2024 + 2025** (`results/metrics.json`). Crew-hours: 3,904 per policy. Load median 964 t. Bypass 13 site-hours (policy-independent).

| policy | escaped kg, median (p05–p95) | reduction vs P0, median [central 90% scenario range] | parameter settings (of 40) better than P0 | captured fraction | cleared kg | overflow site-hours |
|---|---|---|---|---|---|---|
| P0 assumed fixed roster | 428,336 (144,443–961,537) | — | — | 0.461 | 435,726 | 90.5 |
| P1 fill-fraction-ranked fixed-shift rule | 455,001 (151,216–980,895) | **−3.1%** [−6.0%, −0.01%] | 2/40 | 0.444 | 424,964 | 74.5 |
| P2 mass/risk-ranked, tide- and forecast-timed | 411,619 (147,549–917,790) | **+2.1%** [−1.5%, +12.5%] | 28/40 | 0.492 | 480,425 | 87.0 |

Tuning years 2019–2023, same 40 sampled parameter settings: P1 −3.2% [−5.9%, −0.3%]; P2 +1.5% [−1.1%, +10.8%], better than P0 in 30 of 40 parameter settings.

**Disclosure: the held-out evaluation was run twice.** The first run (+2.2% [−1.5%, +13.5%], better in 29 of 40 parameter settings) had a look-ahead bug. The forecaster's 48-hour horizon used `precipitation_previous_day1` for hours 24–47, and those forecasts were issued after the 00 UTC decision. We cut the horizon to a causal 24 hours and changed nothing else (no knobs, no logic), then re-ran. The table shows the corrected numbers. On the tuning metric, the fix cost +0.1% (1,034,784.9 → 1,035,830.4 kg; logged in `results.tsv`).

**Autoresearch ratchet** (`autoresearch/results.tsv`; tuning metric = mean escaped kg over 20 draws, 2019–2023):
- Baseline P2: 1,039,816.6 kg. Best after the ratchet: 1,034,784.9 kg (−0.48%), with `w_arrival` 0.5 → 0.25.
- Ablating tide-aware timing makes it **+3.7% worse** (1,078,082.6 kg).
- Removing all forecast terms makes it +0.23% worse. No single forecast-weight change cleared the 0.1% keep threshold.

**Reading** (revised after the held-out ablations in §8).
1. In this twin, crews are capacity-bound: they clear about 45–50% of the unique input. P2's full gain over P1 comes in two parts. Ranking by mass instead of fill fraction gives −2.0% (P1m vs P1). Everything else P2 adds gives −2.7% (P2 vs P1m). Within P2, tide-aware timing is the largest single lever (−3.2% vs P2_notide), and day-ahead forecasts are small (−0.4% vs P2_nofc). Each component's central 90% scenario range includes zero. Only the complete P2-vs-P1 comparison (−5.6% [−15.8%, −0.3%]) excludes zero.
2. Fill-**fraction** ranking (P1) is worse than the assumed fixed roster, because it sends crews to small booms that look full but hold little mass. A sensor-only **mass**-ranked rule (P1m) is about level with the roster: +0.6% [−0.6%, +2.8%]. The roster is itself mass-aware, since one crew is at the largest site every day.
3. The P2 gain vs P0 is uncertain: its central 90% scenario range includes zero. Treat it as a design direction, not a demonstrated saving.

## 5. Limitations and next steps
- No field calibration: every plastic-process parameter is an ASSUMPTION. The Monte Carlo covers parameter uncertainty, not structural model error.
- ERA5 smooths convective extremes. IMD/BMC gauge data would sharpen the bypass and overflow dynamics.
- Tide comes from a harmonic fit to model sea level, with no storm surge. The 8 cm RMSE is an in-sample residual against the model series, not gauge validation. UHSLC and Survey of India predictions were not checked.
- There is no crew travel time, and shift length is fixed. The idea backlog (crew-hour banking for storm surges, split shifts, learned value function) is in `autoresearch/program.md`.

## 6. Held-out analysis: escape causes, paired comparisons, FWCE, fail-open fuse SENSITIVITY (SIMULATED)

Source: `components/twin_sim/results/analysis.json` (label SIMULATED), reproduced with `cd innovatex-t3-coastal-plastic/components && python -m twin_sim.analysis`.

Setup: held-out Jun–Sep 2024+2025, 4 sites summed. The 40 sampled parameter settings, seed, P2 knobs and crew budget (2 crews × 8 h/day) are the same as `metrics.json`, and nothing was retuned. The analysis checks that its escaped-kg medians equal `metrics.json` and that the mass-balance error is 0 kg.

Notation: values are median [p05–p95], the central 90% scenario range across the 40 sampled parameter settings. "Arrived" is the contract's `arrived_kg` at the boom, which also counts re-arrivals of re-floated debris.

**Escape by cause** (kg; share of escaped / share of arrived, medians):

| policy | entrainment | overtopping | bypass / release | escaped total |
|---|---|---|---|---|
| P0 | 401,466 [110,913–799,722]; 91.0% / 32.7% | 36,650 [0–198,187]; 6.5% / 2.4% | 1,989 [0–51,698]; 0.6% / 0.1% | 428,336 [144,443–961,537] |
| P1 | 404,459 [112,970–819,587]; 90.6% / 32.8% | 34,918 [0–204,204]; 6.6% / 2.2% | 2,582 [0–56,237]; 0.7% / 0.2% | 455,001 [151,216–980,895] |
| P2 | 391,972 [112,382–756,467]; 92.5% / 32.6% | 31,565 [0–183,725]; 5.9% / 1.7% | 2,589 [0–50,770]; 0.7% / 0.2% | 411,619 [147,549–917,790] |

The central 90% scenario ranges of the shares are in the JSON. For entrainment's share of escaped they are about [64–100%]. The 92.5% figure is the P2 scenario with the current release behaviour and the boom normal to the flow (θ = 90°). "Entrainment" here includes the assumed slack-water floor (1 − e_max); §7 splits it.

**Re-floating** is a re-exposure flux, not an escape term: the debris re-arrives at the boom on the ebb.
- Tidal re-float: P0 302,891 kg (24.9% of arrived), P1 344,104 kg (27.5%), P2 266,179 kg (23.5%).
- Flood release: 1,167, 1,770 and 1,445 kg respectively.

**Paired per-draw difference in escaped kg** (same draw, same sensor noise):

| comparison | median | central 90% scenario range | parameter settings (of 40) where the first is lower |
|---|---|---|---|
| P2 vs P1 | −5.6% | [−15.8%, −0.3%] | 39/40 |
| P2 vs P0 | −2.1% | [−12.5%, +1.5%] | 28/40 (matches §4) |
| P1 vs P0 | +3.1% | [0.0%, +6.0%] | 2/40 |

**FWCE** = (cleared + stored at 30 Sep) ÷ catchment load, counting each kg once:

| policy | FWCE | for comparison: gross captured ÷ arrived |
|---|---|---|
| P0 | 46.0% [30.7–69.9] | 64.0% |
| P1 | 44.2% [30.0–69.3] | 63.6% |
| P2 | 49.1% [30.9–70.1] | 64.6% |

**Fail-open fuse / one-way pocket: SENSITIVITY, assumption-driven, not evidence.** All rows use policy P2. Variants:
- (a) current release behaviour;
- (b) fuse: at release, only the arriving flux passes and the pocket keeps its catch;
- (c) fuse plus tidal re-float × 0.5 or × 0.2. Re-float × 1 is identical to (b) by construction.

| variant | escaped kg | Δ escaped vs (a), paired | settings (of 40) lower than (a) | FWCE | Δ FWCE vs (a), pp |
|---|---|---|---|---|---|
| (a) current release | 411,619 [147,549–917,790] | — | — | 49.1% [30.9–70.1] | — |
| (b) fuse | 411,415 [139,432–917,133] | −0.1% [−1.5%, 0.0%] | 31/40 | 49.5% [30.9–70.2] | +0.1 [0.0, +0.8] |
| (c) fuse + re-float × 0.5 | 385,505 [128,073–889,525] | −5.0% [−9.9%, −1.4%] | 40/40 | 51.5% [32.8–73.1] | +2.6 [+0.9, +4.0] |
| (c) fuse + re-float × 0.2 | 368,722 [119,354–860,655] | −9.4% [−16.6%, −2.2%] | 40/40 | 53.2% [36.0–75.1] | +4.6 [+1.3, +7.2] |

**Caveats.**
- **Circularity.** escaped_kg is computed by the same assumed process model that the policies act on. These results show relative value under the stated assumptions; they are not field evidence. Field calibration comes in Round 2.
- **The cause split is set by assumptions.**
  - "Entrainment" means every non-captured arrival outside bypass hours. That includes the (1 − e_max) share assumed to pass under the boom even at slack water.
  - Overtopping depends on the assumed boom capacity and debris bulk density.
- **The fuse matters little here because release is rare.** On the ERA5 0.25° rain scale there are only 13 bypass site-hours in 2024–2025. With gauge-scale rain peaks the fuse could matter more (UNTESTED).
- **The pocket rows scale the assumed tidal re-float rate** (k_refloat 0.01–0.08 /h). Keeping more catch raises overtopping (P2 median 31.6 t → 44.1 t → 50.4 t), and the net figures above include this.
- **Still omitted from the twin:** travel time between sites, minimum clearance duration, gated (flap-gate) outfalls, boom angle θ, and a perfect-foresight oracle policy.

## 7. Entrainment split, exposure and boom angle (SIMULATED; angle = SENSITIVITY)

Source: `results/analysis.json`, keys `entrainment_split`, `exposure_P2_nominal` and `boom_angle_sensitivity_P2`. Reproduce with `cd innovatex-t3-coastal-plastic/components && python -m twin_sim.analysis`.

Setup: held-out Jun–Sep 2024+2025, 40 sampled parameter settings, nothing retuned. Values are median [central 90% scenario range across sampled parameter settings].

**Assumed capture losses dominate this twin; boom angle and retention are candidate field experiments, not findings.**

**Entrainment split** (current boom, θ = 90°):

| policy | slack-water floor (1 − e_max)·arrived: kg; share of escaped | velocity-driven (e_max − e)·arrived: kg; share of escaped |
|---|---|---|
| P0 | 179.3 t; 51.4% [14.4–80.0] | 154.9 t; 37.9% [9.0–80.0] |
| P1 | 183.9 t; 51.1% [14.3–79.8] | 159.5 t; 37.8% [8.9–80.1] |
| P2 | 179.0 t; 51.3% [14.5–81.5] | 148.5 t; 38.4% [9.1–79.8] |

About half of what escapes in this twin is the assumed floor: items assumed to pass under the boom even at slack water (e_max 0.70–0.95, an ASSUMPTION). Velocity-driven entrainment is about 38%. The deck should not present the 92.5% as velocity entrainment.

**Exposure** (P2, nominal parameters): the share of site-hours and of arrived kg with |v|·sin θ > v50 = 0.45 m/s.

| θ | share of site-hours | share of arrived kg |
|---|---|---|
| 90° (current) | 13.2% | 13.2% |
| 45° | 4.2% | 3.6% |
| 30° | 0.7% | 0.4% |
| 20° | 0.03% | 0.01% |

By site at 90° (hours / kg): Mithi 13.9% / 13.3%, Oshiwara 19.3% / 14.3%, Dahisar 19.2% / 16.1%, Trombay 0.6% / 0.5%. Velocity loss is not confined to |v| > v50. The assumed logistic curve already loses about 12% of e_max at v50 − 2w, so the velocity-driven share of escape (≈ 38%) is larger than this exposure share.

**Boom angle θ (SENSITIVITY, P2).** e(v) uses |v|·sin θ, with e_max unchanged. Each row is a paired comparison with θ = 90° on the same hardware.

| hardware | θ | escaped (t) | Δ escaped vs θ = 90° | settings (of 40) lower | Δ escaped vs current boom (a, θ = 90°) | FWCE | Δ FWCE vs θ = 90° (pp) | velocity share of escaped |
|---|---|---|---|---|---|---|---|---|
| (a) current release | 90° | 411.6 [147.5–917.8] | — | — | — | 49.1% [30.9–70.1] | — | 38.4% |
| (a) | 45° | 380.3 [130.5–886.2] | −10.4% [−21.0, −0.8] | 40 | −10.4% | 54.6% [38.8–75.6] | +5.6 [+0.3, +12.4] | 21.0% |
| (a) | 30° | 377.4 [123.7–866.1] | −15.0% [−37.6, −0.8] | 40 | −15.0% | 59.2% [39.5–77.0] | +7.7 [+0.3, +23.1] | 9.8% |
| (a) | 20° | 376.7 [108.4–850.1] | −17.2% [−49.6, −0.7] | 40 | −17.2% | 61.9% [39.6–78.6] | +8.6 [+0.3, +28.8] | 4.7% |
| (c) fuse + re-float ×0.5 | 90° | 385.5 [128.1–889.5] | — | — | −5.0% [−9.9, −1.4] | 51.5% [32.8–73.1] | — | 37.3% |
| (c) | 45° | 354.5 [119.8–862.3] | −10.9% [−21.8, −0.4] | 40 | −16.7% [−28.0, −4.8] | 57.8% [39.8–78.3] | +5.3 [+0.2, +12.5] | 21.0% |
| (c) | 30° | 346.8 [113.1–826.6] | −16.5% [−40.4, −0.6] | 40 | −21.6% [−42.1, −4.7] | 61.9% [40.1–79.6] | +7.6 [+0.2, +22.9] | 9.2% |
| (c) | 20° | 345.7 [102.3–810.6] | −18.8% [−53.0, −0.7] | 40 | −23.4% [−55.1, −4.8] | 66.1% [40.1–81.1] | +8.6 [+0.3, +27.9] | 4.4% |

**Caveats.**
- **Not independent confirmation.** Angle acts only through the same assumed capture curve e(|v|·sin θ). Its benefit is the velocity-driven share by construction, so it cannot confirm that mechanism.
- **v50 is borrowed.** It is transferred from oil-boom practice (UNVERIFIED ASSUMPTION, 0.30–0.70 m/s).
- **Diminishing returns.** Most of the modelled gain is reached by 45°. Boom length grows as 1/sin θ (×1.41 at 45°, ×2 at 30°, ×2.92 at 20°). Capacity, cost and mooring loads are held fixed or not modelled, and P2's forecaster still assumes θ = 90°.
- **The floor is untouched.** The slack-water floor does not change with angle or dispatch. Testing e_max at slack water is the first field experiment.
- **Circularity** (§6) applies.

## 8. Held-out ablations and the mass boundary (SIMULATED; review findings 3 and 11)

Source: `results/analysis.json`, keys `ablations` and `mass_boundary`. Same setup as §7; nothing was retuned, and all policies spend the same crew-hours.

Ablation policies:
- **P1m**, sensor-only mass-ranked fixed-shift rule. Greedy on sensed kg (fill × design capacity), with P1's 08:30 IST shift; no tide, no forecast.
- **P2_notide**: P2 with tide-aware timing off (fixed 08:30 IST start; allocation unchanged).
- **P2_nofc**: P2 with forecast terms off. It ranks on sensed kg only, and takes timing from tide-only predicted access.

Paired escaped kg:

| comparison | isolates | median | central 90% scenario range | settings (of 40) where the first is lower |
|---|---|---|---|---|
| P1m vs P1 | mass vs fill-fraction ranking (sensor-only, fixed shift) | −2.0% | [−4.1%, +0.2%] | 37 |
| P1m vs P0 | sensor-only mass ranking vs assumed fixed roster | +0.6% | [−0.6%, +2.8%] | 10 |
| P2 vs P1m | everything P2 adds beyond mass-ranked sensors | −2.7% | [−12.6%, +1.2%] | 34 |
| P2 vs P2_notide | tide-aware timing, within P2 | −3.2% | [−12.0%, +0.6%] | 34 |
| P2 vs P2_nofc | forecast terms, within P2 | −0.4% | [−1.9%, +1.0%] | 29 |
| P2_nofc vs P1m | tide timing on top of mass ranking, no forecasts | −2.2% | [−12.9%, +0.4%] | 33 |
| P2_notide vs P1m | forecast/risk terms without timing | −0.4% | [−1.6%, +6.4%] | 26 |
| P2 vs P1 | the complete policy comparison | −5.6% | [−15.8%, −0.3%] | 39 |

| policy | escaped (t) | FWCE | cleared share of unique input |
|---|---|---|---|
| P0 assumed fixed roster | 428.3 [144.4–961.5] | 46.0% | 45.8% |
| P1 fill-fraction-ranked fixed-shift rule | 455.0 [151.2–980.9] | 44.2% | 44.1% |
| P1m sensor-only mass-ranked | 429.0 [147.7–968.8] | 45.7% | 45.5% |
| P2_notide | 448.5 [155.4–965.4] | 46.2% | 45.9% |
| P2_nofc | 415.4 [150.6–921.2] | 48.8% | 47.2% |
| P2 mass/risk-ranked, tide- and forecast-timed | 411.6 [147.5–917.8] | 49.1% | 48.0% |

**What can be claimed.**
- The complete P2 policy lets 5.6% less escape than the fill-fraction rule, [−15.8%, −0.3%], lower in 39 of 40 settings.
- Against the assumed roster, the result is −2.1% [−12.5%, +1.5%]: uncertain.
- Tide timing is the largest single component in the held-out ablation. This matches the tuning-year ablation (+3.7% worse without it). But it is **not separately established**: its range reaches +0.6%.
- "Sensors alone" do not beat the assumed roster in this twin, whether ranked by fraction (+3.1%) or by mass (+0.6%). This may differ with more sites or a roster that is not mass-aware (UNTESTED).

**Mass boundary** (finding 11). Each kg is counted once and re-arrivals are excluded. Unique input = escaped + cleared + stored in the boom at 30 Sep + held upstream at 30 Sep. Values are summed over the two monsoons.

| policy | unique input (t) | cleared = removal (t) | stored at 30 Sep = temporary retention (t) | held upstream at 30 Sep (t) | escaped (t) |
|---|---|---|---|---|---|
| P0 | 964.4 [349.6–1,388.1] | 435.7 [152.1–774.7] | 2.9 [0.8–33.9] | 1.2 [0.3–4.3] | 428.3 [144.4–961.5] |
| P1 | 964.4 [349.6–1,388.1] | 425.0 [143.5–763.7] | 3.0 [0.5–34.0] | 1.3 [0.4–4.1] | 455.0 [151.2–980.9] |
| P2 | 964.4 [349.6–1,388.1] | 480.4 [147.7–785.0] | 2.7 [0.6–25.2] | 1.2 [0.3–3.8] | 411.6 [147.5–917.8] |

- FWCE (§6) = (cleared + stored) ÷ unique input. For P2 that is 48.0% removal plus 0.3% retention, so FWCE here is almost entirely crew removal.
- Removal is not final diversion. What happens to cleared material (sorting, recycling, landfill) is outside the twin.
- Each monsoon starts with an empty boom and empty upstream pool. This is an ASSUMPTION: pre-monsoon clearance.
- The twin's mass is generic floating debris, scaled from the brief's city-wide plastic figure. It is not specific to flexible packaging, and there is no moisture correction; the wet bulk density is used only for boom volume.
