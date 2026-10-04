# OBD sample check — Random logs → BTS policy value (REAL data, small sample)

Reproduce: `bash eval/fetch_obd_sample.sh && .venv/bin/python eval/run_obd.py` (from `perceptron-p03-off-policy-eval/`).

Rows: Random 10,000 (clicks 38), BTS 10,000 (clicks 42). Campaign: All (80 items, 3 positions).
Evaluation-policy check: our Monte-Carlo BTS propensities vs the BTS logs' own propensities: MAE 0.08787, correlation 0.0743.
Importance weights on Random logs: mean 0.953, max 19.6, ESS 1644 of 10,000.

**Ground truth (BTS on-policy CTR):** 0.00420 (95% Wald CI 0.00293–0.00547).
No-change baseline (Random's own CTR used as the guess for BTS): 0.00380.

| estimator | V̂(BTS) | 95% bootstrap CI | relative error vs on-policy CTR |
|---|---|---|---|
| IPW | 0.00455 | 0.00156–0.00970 | 8.2% |
| SNIPW | 0.00477 | 0.00160–0.01017 | 13.5% |
| DM | 0.00389 | 0.00387–0.00391 | 7.4% |
| DR | 0.00477 | 0.00177–0.00992 | 13.7% |

Caveat: with about 40 clicks per 10k rows, the sampling error of both the estimates and the ground truth is large (±15–30%). Use the full dataset (about 26M rows) for conclusive numbers.
