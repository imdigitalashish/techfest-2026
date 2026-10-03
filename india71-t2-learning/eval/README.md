# SYNTHETIC FLN evaluation harness

This harness runs the Techfest 2026 Theme 2 decision-support spike on synthetic simulator worlds only.

Command:

```bash
python3 eval/run_eval.py
```

Seeds are fixed at `1,2,3,4,5`; summary statistics are reported as mean ± sample standard deviation. Outputs are written to `eval/results/baseline.json`, `eval/results/summary.md`, and `deliverables/demo/block_dashboard.html`.

Metrics:
- trust/audit: block-level MAE in percentage points at 5%, 10%, and 20% audit budgets; frozen scalar `block_mae_pp_at_10pct_budget`; inflation-school risk AUC; 90% interval coverage.
- area estimation: block RMSE, 90% CI coverage, and absolute difference between benchmarked district aggregate and the PARAKH/ASER-like anchor.
- allocation: expected additional children meeting goal under raw targeting, audit-adjusted targeting, and oracle targeting, evaluated against hidden synthetic truth.

All generated figures are labelled **SYNTHETIC** and are not real child, school, district, ASER, PARAKH, or UDISE+ results.
