# C5 recharge-verifier (spike ★1)

Per-storm water balance for an RWH recharge pit: detects events, fits the recession constant k, estimates infiltrated volume (k·A·∫h dt), computes a clogging index (k / k_as_built) and a verdict (verified / clogged / no_inflow / implausible). Contract: `RechargeEvent` in `architecture/contracts/gwcontracts.py`.

- Baseline: `verifier.py`. Frozen evaluator: `autoresearch/eval.py`. Ledger: `autoresearch/results.tsv`. Program: `autoresearch/program.md`.
- Reproduce the baseline: `innovatex-t1-groundwater/.venv/bin/python innovatex-t1-groundwater/components/recharge_verifier/autoresearch/eval.py --split dev --out innovatex-t1-groundwater/eval/results/recharge_baseline_dev.json` (needs `.data/delhi_weather_hourly.csv` from `components/data-ingest/fetch_delhi.py`).
- **Baseline (dev = monsoon 2025, 40 SIMULATED pits on REAL ERA5 Delhi rain):** event MdAPE 11.8 %, p90 95.8 %, season-total error 61.0 %, coverage 0.975, clogging precision/recall 1.0/1.0, fake recall 0.2 (n=10), false-implausible rate 0.307, blocked recall 1.0 (n=1). Runtime 176 s.

## Ratchet v1 (4 Oct 2026, ~08:13 IST; holdout confirmed ~08:16 IST) — kept, confirmed on holdout
Three hypotheses, each tested as a separate ablation on dev and logged in `autoresearch/results.tsv`:
1. Fit k **within** each recession limb (fixed-effects slope).
2. Make "implausible" a rain-consistency test.
3. One-minute jump test against rain in ±5 min.

| Metric (SIMULATED pits, REAL ERA5 rain) | dev baseline → v1 | holdout baseline → v1 |
|---|---|---|
| event MdAPE (primary) | 11.8 % → **3.9 %** | 10.3 % → **3.0 %** |
| event APE p90 | 95.8 % → 16.4 % | 97.6 % → 16.1 % |
| season-total error | 61.0 % → 4.8 % | 65.3 % → 7.6 % |
| fake recall | 0.2 → 1.0 (n=10) | 0.3 → 1.0 (n=10) |
| false-implausible rate | 0.307 → 0.000 | 0.252 → 0.000 |
| clogging precision / recall | 1.0 / 1.0 → 1.0 / 1.0 | 0.625 / 1.0 → 0.833 / 1.0 |

**Caveat:** the simulator's linear-reservoir pit matches the verifier's assumption, so these numbers are an upper bound. The physical rig in Round 2 (orifice drain, metered inflow) is the real test. Planned evaluator v2 adds non-linear (orifice, √h) drains and gauge-rain mismatch, so the ratchet can't overfit the model form.
