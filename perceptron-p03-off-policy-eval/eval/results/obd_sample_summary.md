# OBD sample check — Random logs → BTS policy value (REAL data, small sample)

Reproduce: `bash eval/fetch_obd_sample.sh && .venv/bin/python eval/run_obd.py` (from `perceptron-p03-off-policy-eval/`).

Rows: Random 10,000 (clicks 38), BTS 10,000 (clicks 42). Campaign: All (80 items, 3 positions).
Evaluation-policy check: our Monte-Carlo BTS propensities vs the BTS logs' own propensities: MAE 0.08787, correlation 0.0743.
Logged BTS propensity quantiles (10/50/90/99%): [0.0071, 0.0645, 0.2408, 0.7146] vs static-prior MC at the same (item, position): [0.0021, 0.0187, 0.0806, 0.2449]. Correlation of the empirical BTS (item, position) frequencies with the static-prior MC: 0.595. Reading (our hypothesis, UNVERIFIED against the OBP paper): the deployed BTS updated its posterior during the week, so the static prior only approximates it; the week-average policy is the closer match if CTRs are stable within the week.

**Ground truth (BTS on-policy CTR):** 0.00420 (95% Wald CI 0.00293–0.00547).
No-change baseline (Random's own CTR used as the guess for BTS): 0.00380.

| evaluation policy | estimator | V̂(BTS) | 95% bootstrap CI | relative error vs on-policy CTR | ESS of weights |
|---|---|---|---|---|---|
| BTS static prior (obp protocol) | IPW | 0.00455 | 0.00156–0.00970 | 8.2% | 1644 |
| BTS static prior (obp protocol) | SNIPW | 0.00477 | 0.00160–0.01017 | 13.5% | 1644 |
| BTS static prior (obp protocol) | DM | 0.00389 | 0.00387–0.00391 | 7.4% | 1644 |
| BTS static prior (obp protocol) | DR | 0.00477 | 0.00177–0.00992 | 13.7% | 1644 |
| BTS week-average (empirical from BTS logs) | IPW | 0.00504 | 0.00271–0.00780 | 19.9% | 2639 |
| BTS week-average (empirical from BTS logs) | SNIPW | 0.00525 | 0.00284–0.00816 | 25.1% | 2639 |
| BTS week-average (empirical from BTS logs) | DM | 0.00393 | 0.00392–0.00395 | 6.3% | 2639 |
| BTS week-average (empirical from BTS logs) | DR | 0.00521 | 0.00289–0.00801 | 24.0% | 2639 |

Caveat: with about 40 clicks per 10k rows, the sampling error of both the estimates and the ground truth is large (±15–30%). Use the full dataset (about 26M rows) for conclusive numbers.
