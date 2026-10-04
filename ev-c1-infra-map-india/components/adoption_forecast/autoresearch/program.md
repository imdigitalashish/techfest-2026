# Auto-research program — C9 `adoption_forecast` (Spike 2)

## Goal
Forecast BEV registrations by state (later district/RTO, by segment) one year ahead, and to 2030 under scenarios. These forecasts drive the requirement estimates (C11).

## Metric (frozen in `eval.py`, lower is better)
`dev_wape`: registration-weighted absolute error, Σ|F−A| / ΣA across the 36 states/UTs, averaged over two rolling one-step origins (2022→2023, 2023→2024). The HOLDOUT origin 2024→2025 is lead-only (`--holdout`). Keep a change only if it beats the best DEV WAPE by > 0.01. Data: VAHAN State × Fuel by calendar year 2020–2025, BEV = `ELECTRIC(BOV)` + `PURE EV`.

## Rules
Edit only `../forecaster.py`; never look at years after the origin; runtime < 30 s.

## Lead holdout check (4 Oct 2026, 09:55 IST)
| Model | DEV WAPE | HOLDOUT WAPE (2024→2025) | Holdout national error |
|---|---|---|---|
| naive | 0.281 | 0.150 | −14.0% |
| pooled growth, national only, damped 0.5 | 0.244 | **0.101** | −2.0% |
| EV-share logit trend k = 2, pooled 50:50, damped 0.5 (DEV best) | **0.178** | 0.110 | +2.0% |

Both pooled models beat naive by 27–33% on the holdout. The holdout does **not** confirm the DEV winner over pooled growth (difference 0.009, inside the noise margin). Prefer an ensemble, or more origins, before claiming a winner.

## Idea backlog
1. Monthly data (VAHAN Month Wise) → more origins, seasonality, and 2026 nowcasting from year-to-date data.
2. Segment-level forecasts (2W/3W/4W/bus) with segment-specific pooling; e-rickshaw dynamics differ.
3. Hierarchical Bayesian partial pooling (state slope ~ national slope + covariates such as income, urbanisation, state EV policy, charger density) with prediction intervals; score interval coverage.
4. Bass diffusion on EV share with a market-potential prior from policy targets; scenario layer (BAU / policy / high) for 2030.
5. Gaussian-process neighbourhood disaggregation (Nature Communications 2026 per `research/sota-methods.md`; UNVERIFIED until fact-checked) for RTO/district level.

## v2 — monthly data (4 Oct 2026, 13:30 IST)
- **Frozen eval:** `eval_monthly.py`. VAHAN State × Month Wise, Jan 2019 – Sep 2026, BEV = fuel filter `ELECTRIC(BOV)` + `PURE EV`; the filtered 2025 monthly totals reconcile exactly with the yearly State × Fuel table (2,356,971). Task: next-12-month BEV registrations per state from quarterly origins. DEV = 8 origins (2022-12 … 2024-09); HOLDOUT = 4 (2024-12 … 2025-09). Metric: mean WAPE. Ledger: `results_monthly.tsv`.
- **Ratchet (9 hypotheses):** naive12 0.232 → pooled national growth (damped 0.5) 0.173 → **share-logit k = 2, pooled 50:50, damped 0.5: 0.147 (kept, −36%)**. The ensemble (pooled growth + share-logit) scored 0.158, so it was not kept. Undamped variants: 0.42–0.44.
- **Lead holdout:**

  | Model | HOLDOUT WAPE |
  |---|---|
  | naive12 | 0.223 |
  | pooled growth | 0.166 |
  | **share-logit** | **0.157** |
  | ensemble | 0.161 |

  The DEV winner is confirmed on the holdout this time (−29% vs naive). The by-origin errors grow towards 2025-09 (0.11 → 0.23) because 2026 accelerated (national error −22% at the last origin).
- **2026 nowcast** (`../nowcast.py`): Jan–Sep actuals + completion, backtested on 2023–2025.

  | Method | Mean state WAPE | Mean \|national error\| | 2026 national |
  |---|---|---|---|
  | **YoY scaling** | **0.072** | **3.0%** | **3,598,002** |
  | ensemble | 0.073 | 5.3% | 3,577,786 |
  | seasonal | 0.095 | 8.3% | 3,557,572 |

  Jan–Sep 2026 = 2,533,727; CY2025 = 2,356,971.
