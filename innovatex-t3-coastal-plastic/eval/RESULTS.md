# Results — every number with its reproduce command

Generated 2026-10-04 09:51 IST at commit `d144a33` by `python3 innovatex-t3-coastal-plastic/eval/collect_results.py`. Values are copied verbatim from each component's `results/metrics.json`. Labels such as SIMULATED and SYNTHETIC are part of the component's output; read them before quoting a number.

## detection — flux_synthetic.json

Source: [`components/detection/results/flux_synthetic.json`](../components/detection/results/flux_synthetic.json)  
Reproduce: `python -m t3det.synth --out ../../.data/detection/synth/seq02 --frames 120 --items 12 --seed 11 --speed 6.0 12.0 && python -m t3det.run_flux --weights ../../.data/detection/weights/yolo11n.pt --seq ../../.data/detection/synth/seq02`

| Metric | Value |
|---|---|
| label | SYNTHETIC |
| sequence | seq02 |
| frames | 120 |
| fps | 5 |
| gt_crossings | 12 |
| items_crossed | 3 |
| count_error_pct | 75 |
| detector_weights | yolo11n.pt |
| tracker | bytetrack.yaml (ultralytics defaults) |
| conf | 0.1 |
| imgsz | 640 |
| flux_estimate.site_id | SYNTHETIC-seq01 |
| flux_estimate.t_start | 2026-10-04T00:00:00Z |
| flux_estimate.t_end | 2026-10-04T00:00:24Z |
| flux_estimate.items_crossed | 3 |
| flux_estimate.items_per_min | 7.5 |
| flux_estimate.by_label.traffic light | 1 |
| flux_estimate.by_label.bird | 1 |
| flux_estimate.by_label.kite | 1 |
| flux_estimate.est_kg | 0.057 |
| flux_estimate.est_kg_ci90 | [0.0, 0.1624] |
| flux_estimate.method | YOLO detector + ByteTrack (ultralytics, conf>=0.1) + line-crossing count, one count per track id; mass = items x 19.0 g/item (sd 37.0 g; assumption: van Emmerik et al. 2019 Sci Rep (Saigon), PMC6753078: 1.9e-2 kg per visually counted item, sd 3.7e-2; transfer to Mumbai assumed); CI90 = n*mean +/- 1.645*sd*sqrt(n) |
| flux_estimate.provenance.kind | synthetic |
| flux_estimate.provenance.source | component:detection/t3det.synth seed=11 |
| flux_estimate.provenance.retrieved_at | 2026-10-04T02:24:00.379100Z |
| flux_estimate.provenance.notes | SYNTHETIC: real TUD-GV test-split litter crops pasted on an inpainted TUD-GV water frame; mass factor is an ASSUMPTION transferred from the Saigon River (van Emmerik et al. 2019) |

## detection — metrics.json

Source: [`components/detection/results/metrics.json`](../components/detection/results/metrics.json)  
Reproduce: `cd innovatex-t3-coastal-plastic && bash components/detection/data/fetch_data.sh && cd components/detection && python3.11 -m t3det.prepare && curl -sSL -o ../../.data/detection/weights/yolo11n.pt https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt && python3.11 -m t3det.zeroshot --weights ../../.data/detection/weights/yolo11n.pt --split test`

| Metric | Value |
|---|---|
| dataset | TUD-GV floating-litter subset (Jia et al. 2024, Water Research 266:122405), doi:10.5281/zenodo.13730228, CC BY 4.0 |
| split | test (grouped by experiment id, seed 42; components/detection/data/splits/test.txt; held out) |
| n_test_images | 254 |
| n_test_boxes | 1309 |
| mAP50 | 0.3935 |
| mAP50_95 | 0.2091 |
| precision | 0.7562 |
| recall | 0.1398 |
| precision_recall_at_score | 0.25 |
| per_class.litter.AP50 | 0.3935 |
| per_class.litter.AP50_95 | 0.2091 |
| latency_ms_mps.median | 1087 |
| latency_ms_mps.p90 | 4470 |
| latency_ms_mps.n | 251 |
| latency_ms_mps.batch | 1 |
| latency_ms_mps.imgsz | 640 |
| latency_ms_mps.note | end-to-end predict() on a shared, thrashing Apple M5 (load avg 63 on 10 cores, swap full): an upper bound, not the model's real speed |
| model_id | yolo11n.pt#sha256:0ebbc80d4a76 (COCO-pretrained, zero-shot, class-agnostic) |
| baseline_kind | ZERO-SHOT (no training on TUD-GV): COCO-pretrained YOLO11n, class-agnostic NMS, every COCO class counted as a litter candidate. The trained YOLO11n baseline was blocked by machine thrash (README A1); its command is in README. |
| metric_impl | frozen matcher of autoresearch/eval.py: greedy IoU match, COCO-style 101-point AP; mAP50_95 = mean AP over IoU 0.50:0.05:0.95; precision/recall at score >= 0.25 |
| evaluated_at | 2026-10-04T02:33:22+00:00 |
| machine | arm64 macOS 26.2 (Apple M5, MPS) |
| ap_by_iou.0.5 | 0.3935 |
| ap_by_iou.0.55 | 0.3763 |
| ap_by_iou.0.6 | 0.3463 |
| ap_by_iou.0.65 | 0.3205 |
| ap_by_iou.0.7 | 0.2725 |
| ap_by_iou.0.75 | 0.2026 |
| ap_by_iou.0.8 | 0.1219 |
| ap_by_iou.0.85 | 0.0473 |
| ap_by_iou.0.9 | 0.0104 |
| ap_by_iou.0.95 | 0.0001 |

## detection — zeroshot_groningen_eval.json

Source: [`components/detection/results/zeroshot_groningen_eval.json`](../components/detection/results/zeroshot_groningen_eval.json)  
Reproduce: `cd innovatex-t3-coastal-plastic/components/detection && python3.11 autoresearch/eval.py --weights ../../.data/detection/weights/yolo11n.pt --split groningen --boot 20`

| Metric | Value |
|---|---|
| what | Smoke test of the FROZEN autoresearch/eval.py on the Groningen cross-site split with COCO-pretrained YOLO11n (zero-shot, class-aware NMS, any COCO class = litter candidate). Values transcribed verbatim from the run's stdout/stderr (2026-10-04 ~07:41 IST). |
| split | groningen |
| n_images | 63 |
| n_gt | 383 |
| mAP50 | 0.4053 |
| boot_se | 0.026 |
| boot_reps | 20 |
| precision@0.25 | 1 |
| recall@0.25 | 0.0104 |
| ms_per_img_median | 3156 |
| config.imgsz | 640 |
| config.conf | 0.001 |
| config.iou | 0.7 |
| config.augment | False |
| config.tiles | [1, 1] |
| note | ms/img measured while the machine was thrashing (swap full, load avg ~85): an upper bound |

## mrv_ledger — eval_detail.json

Source: [`components/mrv_ledger/results/eval_detail.json`](../components/mrv_ledger/results/eval_detail.json)  
Reproduce: `cd innovatex-t3-coastal-plastic/components && python3 -m mrv_ledger.evaluate`

| Metric | Value |
|---|---|
| data | SYNTHETIC (mrv_ledger/synth.py); parameters are ASSUMPTIONS (reconcile.Params) |
| params.wet_bulk_density_kg_m3 | 150 |
| params.moisture_fraction | 0.4 |
| params.sigma_fill_abs | 0.03 |
| params.sigma_density_rel | 0.25 |
| params.sigma_claim_rel | 0.1 |
| params.z_review | 1.645 |
| params.z_reject | 2.326 |
| params.max_wet_density_kg_m3 | 450 |
| reconciliation.calibration_target_fpr | 0.0475 |
| reconciliation.z_threshold_review | 2.142 |
| reconciliation.ratio_threshold_baseline | 1.768 |
| reconciliation.methods.proposed_z.recall_all_fraud | 0.7164 |
| reconciliation.methods.proposed_z.false_flag_rate_honest | 0.047 |
| reconciliation.methods.proposed_z.precision_at_5pct_prevalence | 0.4451 |
| reconciliation.methods.proposed_z.precision_at_10pct_prevalence | 0.6288 |
| reconciliation.methods.proposed_z.recall_inflated | 0.694 |
| reconciliation.methods.proposed_z.recall_phantom | 1 |
| reconciliation.methods.proposed_z.recall_wetted | 0.5 |
| reconciliation.methods.proposed_z.recall_inflated_x1.2-1.5 | 0.244 |
| reconciliation.methods.proposed_z.recall_inflated_x1.5-2.0 | 0.5801 |
| reconciliation.methods.proposed_z.recall_inflated_x2.0-3.0 | 0.8862 |
| reconciliation.methods.proposed_z.auc | 0.9255 |
| reconciliation.methods.baseline_ratio.recall_all_fraud | 0.6748 |
| reconciliation.methods.baseline_ratio.false_flag_rate_honest | 0.0479 |
| reconciliation.methods.baseline_ratio.precision_at_5pct_prevalence | 0.4258 |
| reconciliation.methods.baseline_ratio.precision_at_10pct_prevalence | 0.6102 |
| reconciliation.methods.baseline_ratio.recall_inflated | 0.6487 |
| reconciliation.methods.baseline_ratio.recall_phantom | 1 |
| reconciliation.methods.baseline_ratio.recall_wetted | 0.428 |
| reconciliation.methods.baseline_ratio.recall_inflated_x1.2-1.5 | 0.2056 |
| reconciliation.methods.baseline_ratio.recall_inflated_x1.5-2.0 | 0.503 |
| reconciliation.methods.baseline_ratio.recall_inflated_x2.0-3.0 | 0.8549 |
| reconciliation.methods.baseline_ratio.auc | 0.9174 |
| reconciliation.methods.status_quo_slip_check.recall_all_fraud | 0 |
| reconciliation.methods.status_quo_slip_check.false_flag_rate_honest | 0 |
| reconciliation.methods.status_quo_slip_check.precision_at_5pct_prevalence | 0 |
| reconciliation.methods.status_quo_slip_check.precision_at_10pct_prevalence | 0 |
| reconciliation.methods.status_quo_slip_check.recall_inflated | 0 |
| reconciliation.methods.status_quo_slip_check.recall_phantom | 0 |
| reconciliation.methods.status_quo_slip_check.recall_wetted | 0 |
| reconciliation.methods.status_quo_slip_check.recall_inflated_x1.2-1.5 | 0 |
| reconciliation.methods.status_quo_slip_check.recall_inflated_x1.5-2.0 | 0 |
| reconciliation.methods.status_quo_slip_check.recall_inflated_x2.0-3.0 | 0 |
| reconciliation.sensitivity.false_flag_rate_if_true_density_x0.8 | 0.0075 |
| reconciliation.sensitivity.false_flag_rate_if_true_density_x1.25 | 0.178 |
| reconciliation.n_test.honest | 10000 |
| reconciliation.n_test.inflated | 3000 |
| reconciliation.n_test.phantom | 1000 |
| reconciliation.n_test.wetted | 1000 |
| tamper.edit.trials | 200 |
| tamper.edit.detected_with_anchor | 1 |
| tamper.edit.detected_chain_only | 1 |
| tamper.delete.trials | 200 |
| tamper.delete.detected_with_anchor | 1 |
| tamper.delete.detected_chain_only | 0.995 |
| tamper.reorder.trials | 200 |
| tamper.reorder.detected_with_anchor | 1 |
| tamper.reorder.detected_chain_only | 1 |
| tamper.insert.trials | 200 |
| tamper.insert.detected_with_anchor | 1 |
| tamper.insert.detected_chain_only | 1 |
| tamper.truncate_tail.trials | 200 |
| tamper.truncate_tail.detected_with_anchor | 1 |
| tamper.truncate_tail.detected_chain_only | 0 |
| tamper.rewrite_suffix.trials | 200 |
| tamper.rewrite_suffix.detected_with_anchor | 1 |
| tamper.rewrite_suffix.detected_chain_only | 0 |
| tamper.rewrite_suffix.detected_by_signatures | 1 |
| tamper.all_detected_with_anchor | True |
| git_sha_at_run | 57938df |

## mrv_ledger — metrics.json

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

## twin_sim — metrics.json

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

