# Results — every number with its reproduce command

Generated 2026-10-04 07:29 IST at commit `e7430e9` by `python3 innovatex-t3-coastal-plastic/eval/collect_results.py`. Values are copied verbatim from each component's `results/metrics.json`. Labels such as SIMULATED and SYNTHETIC are part of the component's output; read them before quoting a number.

## mrv_ledger

Source: [`components/mrv_ledger/results/metrics.json`](../components/mrv_ledger/results/metrics.json)  
Reproduce: `cd innovatex-t3-coastal-plastic/components && python3 -m mrv_ledger.evaluate`

| Metric | Value |
|---|---|
| data | SYNTHETIC |
| recall_fraud_at_5pct_false_flags | 0.7164 |
| false_flag_rate_test | 0.047 |
| recall_inflated_x1.2-3 | 0.694 |
| recall_inflated_x1.2-1.5 | 0.244 |
| recall_phantom | 1 |
| recall_wetted_or_silted | 0.5 |
| precision_at_5pct_prevalence | 0.4451 |
| precision_at_10pct_prevalence | 0.6288 |
| baseline_ratio_recall_at_5pct | 0.6748 |
| status_quo_slip_check_recall | 0 |
| tamper_detection_rate_with_anchor | 1 |

## twin_sim

Source: [`components/twin_sim/results/metrics.json`](../components/twin_sim/results/metrics.json)  
Reproduce: `cd innovatex-t3-coastal-plastic/components && python -m twin_sim.run`

| Metric | Value |
|---|---|
| metric | escaped_kg summed over 4 sites and the held-out monsoons (Jun-Sep 2024+2025); relative reduction vs P0 per Monte Carlo draw; median and 90% interval (p05-p95) |
| n_draws | 40 |
| seed | 20261004 |
| crew_budget | 2 crews x 8 h/day, all policies |
| heldout_2024_2025.P0.escaped_kg_median | 4.283e+05 |
| heldout_2024_2025.P0.escaped_kg_p05 | 1.444e+05 |
| heldout_2024_2025.P0.escaped_kg_p95 | 9.615e+05 |
| heldout_2024_2025.P0.reduction_vs_P0_median | 0 |
| heldout_2024_2025.P0.reduction_vs_P0_p05 | 0 |
| heldout_2024_2025.P0.reduction_vs_P0_p95 | 0 |
| heldout_2024_2025.P0.draws_better_than_P0 | 0 |
| heldout_2024_2025.P0.captured_fraction_median | 0.4612 |
| heldout_2024_2025.P0.cleared_kg_median | 4.357e+05 |
| heldout_2024_2025.P0.overflow_site_hours_median | 90.5 |
| heldout_2024_2025.P0.bypass_site_hours_median | 13 |
| heldout_2024_2025.P0.crew_hours | 3904 |
| heldout_2024_2025.P0.load_kg_median | 9.644e+05 |
| heldout_2024_2025.P1.escaped_kg_median | 4.55e+05 |
| heldout_2024_2025.P1.escaped_kg_p05 | 1.512e+05 |
| heldout_2024_2025.P1.escaped_kg_p95 | 9.809e+05 |
| heldout_2024_2025.P1.reduction_vs_P0_median | -0.0314 |
| heldout_2024_2025.P1.reduction_vs_P0_p05 | -0.0602 |
| heldout_2024_2025.P1.reduction_vs_P0_p95 | -0.0001 |
| heldout_2024_2025.P1.draws_better_than_P0 | 2 |
| heldout_2024_2025.P1.captured_fraction_median | 0.4437 |
| heldout_2024_2025.P1.cleared_kg_median | 4.25e+05 |
| heldout_2024_2025.P1.overflow_site_hours_median | 74.5 |
| heldout_2024_2025.P1.bypass_site_hours_median | 13 |
| heldout_2024_2025.P1.crew_hours | 3904 |
| heldout_2024_2025.P1.load_kg_median | 9.644e+05 |
| heldout_2024_2025.P2.escaped_kg_median | 4.116e+05 |
| heldout_2024_2025.P2.escaped_kg_p05 | 1.475e+05 |
| heldout_2024_2025.P2.escaped_kg_p95 | 9.178e+05 |
| heldout_2024_2025.P2.reduction_vs_P0_median | 0.0214 |
| heldout_2024_2025.P2.reduction_vs_P0_p05 | -0.0149 |
| heldout_2024_2025.P2.reduction_vs_P0_p95 | 0.1251 |
| heldout_2024_2025.P2.draws_better_than_P0 | 28 |
| heldout_2024_2025.P2.captured_fraction_median | 0.4916 |
| heldout_2024_2025.P2.cleared_kg_median | 4.804e+05 |
| heldout_2024_2025.P2.overflow_site_hours_median | 87 |
| heldout_2024_2025.P2.bypass_site_hours_median | 13 |
| heldout_2024_2025.P2.crew_hours | 3904 |
| heldout_2024_2025.P2.load_kg_median | 9.644e+05 |
| tuning_2019_2023.P0.escaped_kg_median | 1.121e+06 |
| tuning_2019_2023.P0.escaped_kg_p05 | 3.8e+05 |
| tuning_2019_2023.P0.escaped_kg_p95 | 2.42e+06 |
| tuning_2019_2023.P0.reduction_vs_P0_median | 0 |
| tuning_2019_2023.P0.reduction_vs_P0_p05 | 0 |
| tuning_2019_2023.P0.reduction_vs_P0_p95 | 0 |
| tuning_2019_2023.P0.draws_better_than_P0 | 0 |
| tuning_2019_2023.P0.captured_fraction_median | 0.4432 |
| tuning_2019_2023.P0.cleared_kg_median | 1.091e+06 |
| tuning_2019_2023.P0.overflow_site_hours_median | 249.5 |
| tuning_2019_2023.P0.bypass_site_hours_median | 158 |
| tuning_2019_2023.P0.crew_hours | 9760 |
| tuning_2019_2023.P0.load_kg_median | 2.407e+06 |
| tuning_2019_2023.P1.escaped_kg_median | 1.168e+06 |
| tuning_2019_2023.P1.escaped_kg_p05 | 4.079e+05 |
| tuning_2019_2023.P1.escaped_kg_p95 | 2.474e+06 |
| tuning_2019_2023.P1.reduction_vs_P0_median | -0.0315 |
| tuning_2019_2023.P1.reduction_vs_P0_p05 | -0.0588 |
| tuning_2019_2023.P1.reduction_vs_P0_p95 | -0.0032 |
| tuning_2019_2023.P1.draws_better_than_P0 | 1 |
| tuning_2019_2023.P1.captured_fraction_median | 0.4224 |
| tuning_2019_2023.P1.cleared_kg_median | 1.055e+06 |
| tuning_2019_2023.P1.overflow_site_hours_median | 231 |
| tuning_2019_2023.P1.bypass_site_hours_median | 158 |
| tuning_2019_2023.P1.crew_hours | 9760 |
| tuning_2019_2023.P1.load_kg_median | 2.407e+06 |
| tuning_2019_2023.P2.escaped_kg_median | 1.067e+06 |
| tuning_2019_2023.P2.escaped_kg_p05 | 3.853e+05 |
| tuning_2019_2023.P2.escaped_kg_p95 | 2.315e+06 |
| tuning_2019_2023.P2.reduction_vs_P0_median | 0.0152 |
| tuning_2019_2023.P2.reduction_vs_P0_p05 | -0.0111 |
| tuning_2019_2023.P2.reduction_vs_P0_p95 | 0.1083 |
| tuning_2019_2023.P2.draws_better_than_P0 | 30 |
| tuning_2019_2023.P2.captured_fraction_median | 0.4642 |
| tuning_2019_2023.P2.cleared_kg_median | 1.177e+06 |
| tuning_2019_2023.P2.overflow_site_hours_median | 285 |
| tuning_2019_2023.P2.bypass_site_hours_median | 158 |
| tuning_2019_2023.P2.crew_hours | 9760 |
| tuning_2019_2023.P2.load_kg_median | 2.407e+06 |
| p2_knobs.starts_utc | [1, 2, 3, 4, 5] |
| p2_knobs.tide_aware | True |
| p2_knobs.w_stock | 1 |
| p2_knobs.w_bypass | 2 |
| p2_knobs.w_over | 1 |
| p2_knobs.w_arrival | 0.25 |
| p2_knobs.loss_weight | 0 |
| p2_knobs.arr_horizon | 24 |
| tide_fit.mithi_mahim.variance_explained | 0.9924 |
| tide_fit.mithi_mahim.rmse_m | 0.079 |
| tide_fit.oshiwara_malad.variance_explained | 0.9932 |
| tide_fit.oshiwara_malad.rmse_m | 0.078 |
| tide_fit.dahisar_mouth.variance_explained | 0.9933 |
| tide_fit.dahisar_mouth.rmse_m | 0.08 |
| tide_fit.trombay_mahul.variance_explained | 0.9924 |
| tide_fit.trombay_mahul.rmse_m | 0.079 |
| git_sha_at_run | 312eae6 |

