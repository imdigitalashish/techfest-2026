# Prospective (blind) test of C9 — frozen 4 Oct 2026

The retrospective holdouts in `eval_monthly.py` (v2) and `eval_monthly_v3.py` have been viewed, so they cannot confirm the model (review 2026-10-04). The untouched test is the future.

**Frozen predictions:** [`prospective_predictions_2026-10-04.csv`](prospective_predictions_2026-10-04.csv), committed in the same commit as this file. They were made with data to 30 Sep 2026 and these components:
- nowcast method: `components/adoption_forecast/nowcast.py`, YoY scaling with a year-to-date floor;
- 12-month forecaster: `forecaster.py` with `PARAMS_M = {'method': 'share_logit', 'k': 2, 'w': 0.5, 'phi': 0.5}`.

| Target | Prediction column | Scored when | Metric |
|---|---|---|---|
| CY2026 BEV registrations by state (fuels ELECTRIC(BOV) + PURE EV, VAHAN calendar-year table) | `cy2026_bev_nowcast_yoy` | after 31 Dec 2026 (first VAHAN pull in Jan 2027) | WAPE across states; national relative error |
| BEV registrations Oct 2026 – Sep 2027 by state | `bev_oct2026_sep2027_forecast` | after 30 Sep 2027 | WAPE across states |

**Rules:**
- The predictions file is never edited after this commit.
- The scorer pulls fresh VAHAN tables with `fetch_vahan.py` and reports the result, whatever it is, in the thought node and the results ledger.
- Any later model change is evaluated on a new frozen prediction, not on this one.
