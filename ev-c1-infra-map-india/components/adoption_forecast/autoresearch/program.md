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
