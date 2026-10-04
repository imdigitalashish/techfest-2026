# C5 recharge-verifier (spike ★1)

Per-storm water balance for an RWH recharge pit: detects events, fits the recession constant k, estimates infiltrated volume (k·A·∫h dt), computes a clogging index (k / k_as_built) and a verdict (verified / clogged / no_inflow / implausible). Contract: `RechargeEvent` in `architecture/contracts/gwcontracts.py`.

- Baseline: `verifier.py`. Frozen evaluator: `autoresearch/eval.py`. Ledger: `autoresearch/results.tsv`. Program: `autoresearch/program.md`.
- Reproduce the baseline: `innovatex-t1-groundwater/.venv/bin/python innovatex-t1-groundwater/components/recharge_verifier/autoresearch/eval.py --split dev --out innovatex-t1-groundwater/eval/results/recharge_baseline_dev.json` (needs `.data/delhi_weather_hourly.csv` from `components/data-ingest/fetch_delhi.py`).
- **Baseline (dev = monsoon 2025, 40 SIMULATED pits on REAL ERA5 Delhi rain):** event MdAPE 11.8 %, p90 95.8 %, season-total error 61.0 %, coverage 0.975, clogging precision/recall 1.0/1.0, fake recall 0.2 (n=10), false-implausible rate 0.307, blocked recall 1.0 (n=1). Runtime 176 s.
