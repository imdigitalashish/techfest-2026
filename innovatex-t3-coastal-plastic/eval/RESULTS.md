# Results — every number with its reproduce command

Generated 2026-10-04 17:05 IST at commit `88b92ff` by `python3 innovatex-t3-coastal-plastic/eval/collect_results.py`. Values are copied verbatim from each component's `results/metrics.json`. Labels such as SIMULATED and SYNTHETIC are part of the component's output; read them before quoting a number.

## detection — flux_synthetic.json

Source: [`components/detection/results/flux_synthetic.json`](../components/detection/results/flux_synthetic.json)  
Reproduce: `python -m t3det.synth --out ../../.data/detection/synth/seq02 --frames 120 --items 12 --seed 11 --speed 6.0 12.0 && python -m t3det.run_flux --weights ../../.data/detection/runs/baseline_yolo11n_640/weights/best.pt --seq ../../.data/detection/synth/seq02`

| Metric | Value |
|---|---|
| label | SYNTHETIC |
| sequence | seq02 |
| frames | 120 |
| fps | 5 |
| gt_crossings | 12 |
| items_crossed | 16 |
| count_error_pct | 33.33 |
| detector_model_id | baseline_yolo11n_640/best.pt#sha256:a5157292e2c0 |
| device | mps |
| tracker | bytetrack.yaml (ultralytics defaults) |
| conf | 0.1 |
| imgsz | 640 |
| flux_estimate.site_id | SYNTHETIC-seq01 |
| flux_estimate.t_start | 2026-10-04T00:00:00Z |
| flux_estimate.t_end | 2026-10-04T00:00:24Z |
| flux_estimate.items_crossed | 16 |
| flux_estimate.items_per_min | 40 |
| flux_estimate.by_label.litter | 16 |
| flux_estimate.est_kg | 0.304 |
| flux_estimate.est_kg_ci90 | [0.0605, 0.5475] |
| flux_estimate.method | YOLO detector + ByteTrack (ultralytics, conf>=0.1) + line-crossing count, one count per track id; mass = items x 19.0 g/item (sd 37.0 g; assumption: van Emmerik et al. 2019 Sci Rep (Saigon), PMC6753078: 1.9e-2 kg per visually counted item, sd 3.7e-2; transfer to Mumbai assumed); CI90 = n*mean +/- 1.645*sd*sqrt(n) |
| flux_estimate.provenance.kind | synthetic |
| flux_estimate.provenance.source | component:detection/t3det.synth seed=11 |
| flux_estimate.provenance.retrieved_at | 2026-10-04T11:31:01.042373Z |
| flux_estimate.provenance.notes | SYNTHETIC: real TUD-GV test-split litter crops pasted on an inpainted TUD-GV water frame; mass factor is an ASSUMPTION transferred from the Saigon River (van Emmerik et al. 2019) |

## detection — flux_synthetic_seq01.json

Source: [`components/detection/results/flux_synthetic_seq01.json`](../components/detection/results/flux_synthetic_seq01.json)  
Reproduce: `python -m t3det.synth --out ../../.data/detection/synth/seq01 --frames 300 --items 24 --seed 7 --speed 4.0 9.0 && python -m t3det.run_flux --weights ../../.data/detection/runs/baseline_yolo11n_640/weights/best.pt --seq ../../.data/detection/synth/seq01`

| Metric | Value |
|---|---|
| label | SYNTHETIC |
| sequence | seq01 |
| frames | 300 |
| fps | 5 |
| gt_crossings | 24 |
| items_crossed | 28 |
| count_error_pct | 16.67 |
| detector_model_id | baseline_yolo11n_640/best.pt#sha256:a5157292e2c0 |
| device | mps |
| tracker | bytetrack.yaml (ultralytics defaults) |
| conf | 0.1 |
| imgsz | 640 |
| flux_estimate.site_id | SYNTHETIC-seq01 |
| flux_estimate.t_start | 2026-10-04T00:00:00Z |
| flux_estimate.t_end | 2026-10-04T00:01:00Z |
| flux_estimate.items_crossed | 28 |
| flux_estimate.items_per_min | 28 |
| flux_estimate.by_label.litter | 28 |
| flux_estimate.est_kg | 0.532 |
| flux_estimate.est_kg_ci90 | [0.2099, 0.8541] |
| flux_estimate.method | YOLO detector + ByteTrack (ultralytics, conf>=0.1) + line-crossing count, one count per track id; mass = items x 19.0 g/item (sd 37.0 g; assumption: van Emmerik et al. 2019 Sci Rep (Saigon), PMC6753078: 1.9e-2 kg per visually counted item, sd 3.7e-2; transfer to Mumbai assumed); CI90 = n*mean +/- 1.645*sd*sqrt(n) |
| flux_estimate.provenance.kind | synthetic |
| flux_estimate.provenance.source | component:detection/t3det.synth seed=7 |
| flux_estimate.provenance.retrieved_at | 2026-10-04T11:31:16.461334Z |
| flux_estimate.provenance.notes | SYNTHETIC: real TUD-GV test-split litter crops pasted on an inpainted TUD-GV water frame; mass factor is an ASSUMPTION transferred from the Saigon River (van Emmerik et al. 2019) |

## detection — flux_synthetic_zeroshot.json

Source: [`components/detection/results/flux_synthetic_zeroshot.json`](../components/detection/results/flux_synthetic_zeroshot.json)  
Reproduce: `python -m t3det.synth --out ../../.data/detection/synth/seq02 --frames 120 --items 12 --seed 11 --speed 6.0 12.0 && python -m t3det.run_flux --weights ../../.data/detection/weights/yolo11n.pt --seq ../../.data/detection/synth/seq02`

| Metric | Value |
|---|---|
| label | SYNTHETIC |
| detector | ZERO-SHOT COCO-pretrained YOLO11n (not trained on TUD-GV) |
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
Reproduce: `cd innovatex-t3-coastal-plastic && bash components/detection/data/fetch_data.sh && cd components/detection && /opt/homebrew/bin/python3.11 -m t3det.prepare && curl -sSL -o ../../.data/detection/weights/yolo11n.pt https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt && T3DET_DEVICE=mps nice -n 10 /opt/homebrew/bin/python3.11 -m t3det.train --model yolo11n.pt --device mps --imgsz 640 --epochs 100 --time 0.9 --batch 8 --workers 2 --cache disk --name baseline_yolo11n_640 && IMGSZ=640 T3DET_DEVICE=mps bash run_after_train.sh A ../../.data/detection/runs/baseline_yolo11n_640/weights/best.pt`

| Metric | Value |
|---|---|
| dataset | TUD-GV floating-litter subset (Jia et al. 2024, Water Research 266:122405), doi:10.5281/zenodo.13730228, CC BY 4.0 |
| split | test (grouped by experiment id, seed 42; components/detection/data/splits/test.txt; held out: evaluated once, never used for training or selection) |
| n_test_images | 254 |
| mAP50 | 0.8574 |
| mAP50_95 | 0.5726 |
| precision | 0.8452 |
| recall | 0.7838 |
| per_class.litter.AP50 | 0.8574 |
| per_class.litter.AP50_95 | 0.5726 |
| latency_ms_mps.median | 71.38 |
| latency_ms_mps.p90 | 145.7 |
| latency_ms_mps.n | 50 |
| latency_ms_mps.batch | 1 |
| latency_ms_mps.imgsz | 640 |
| latency_ms_mps.device | mps |
| latency_ms_mps.note | shared Apple M5 (1-min load avg 10 on 10 cores, process niced +10, another app using the GPU); includes JPEG decode of a 1280x720 image: an upper bound |
| model_id | baseline_yolo11n_640/best.pt#sha256:a5157292e2c0 |
| device | mps |
| evaluated_at | 2026-10-04T17:00:19+05:30 |
| code_commit | 9f861a0 |
| machine | arm64 macOS 26.2 (Apple M5, 24 GB, shared) |
| eval_settings.imgsz | 640 |
| eval_settings.conf | 0.001 |
| eval_settings.iou_nms | 0.7 |
| eval_settings.nms_time_limit | lifted (see mps_patch.py) |
| eval_settings.ap | ultralytics COCO-style 101-point; P/R at ultralytics' max-F1 confidence |
| ultralytics_speed_ms.preprocess | 0.61 |
| ultralytics_speed_ms.inference | 12.44 |
| ultralytics_speed_ms.loss | 0 |
| ultralytics_speed_ms.postprocess | 54.61 |
| other_splits.val.split | val |
| other_splits.val.n_images | 278 |
| other_splits.val.mAP50 | 0.9288 |
| other_splits.val.mAP50_95 | 0.6355 |
| other_splits.val.precision | 0.9168 |
| other_splits.val.recall | 0.8259 |
| other_splits.val.per_class.litter.AP50 | 0.9288 |
| other_splits.val.per_class.litter.AP50_95 | 0.6355 |
| other_splits.val.ultralytics_speed_ms.preprocess | 0.63 |
| other_splits.val.ultralytics_speed_ms.inference | 10.56 |
| other_splits.val.ultralytics_speed_ms.loss | 0 |
| other_splits.val.ultralytics_speed_ms.postprocess | 38.78 |
| other_splits.groningen.split | groningen |
| other_splits.groningen.n_images | 63 |
| other_splits.groningen.mAP50 | 0.5237 |
| other_splits.groningen.mAP50_95 | 0.2596 |
| other_splits.groningen.precision | 0.9008 |
| other_splits.groningen.recall | 0.4491 |
| other_splits.groningen.per_class.litter.AP50 | 0.5237 |
| other_splits.groningen.per_class.litter.AP50_95 | 0.2596 |
| other_splits.groningen.ultralytics_speed_ms.preprocess | 2.29 |
| other_splits.groningen.ultralytics_speed_ms.inference | 23.63 |
| other_splits.groningen.ultralytics_speed_ms.loss | 0 |
| other_splits.groningen.ultralytics_speed_ms.postprocess | 26.95 |
| training.device | mps |
| training.imgsz | 640 |
| training.epochs_completed | 9 |
| training.epoch_time_s.median | 386.9 |
| training.epoch_time_s.mean | 361.5 |
| training.epoch_time_s.first | 170 |
| training.epoch_time_s.last | 327.9 |
| training.train_loop_s | 3254 |
| training.total_wall_clock_s | 3366 |
| training.total_wall_clock_note | trainer process start to exit: dataset cache build + training + ultralytics' final val of best.pt; includes any guard pauses |
| training.paused_s_approx | 210 |
| training.hard_capped | 0 |
| training.start_ist | 2026-10-04T16:03:26+05:30 |
| training.end_ist | 2026-10-04T16:59:33+05:30 |
| training.exit_code | 0 |
| training.val_from_training_log.last_epoch.epoch | 9 |
| training.val_from_training_log.last_epoch.mAP50 | 0.9288 |
| training.val_from_training_log.last_epoch.mAP50_95 | 0.6354 |
| training.val_from_training_log.max_mAP50_95_epoch.epoch | 9 |
| training.val_from_training_log.max_mAP50_95_epoch.mAP50 | 0.9288 |
| training.val_from_training_log.max_mAP50_95_epoch.mAP50_95 | 0.6354 |
| training.recipe | yolo11n.pt (COCO-pretrained, ultralytics assets v8.3.0) fine-tuned on the TUD-GV grouped train split (969 images). ultralytics 8.4.12 defaults (SGD/AdamW auto, mosaic 1.0 with close_mosaic 10, warmup 3 epochs, hsv/flip augmentations) except: batch 8, workers 2, cache=disk, seed 42 deterministic, wall-clock budget `time` (ultralytics re-plans epochs and the LR schedule to fit). best.pt = best val fitness. MPS runs use the CPU label-assigner patch (README A3); NMS time limit lifted. |
| training.command | nice -n 10 /opt/homebrew/bin/python3.11 -m t3det.train --model yolo11n.pt --device mps --imgsz 640 --epochs 100 --time 0.9 --batch 8 --workers 2 --cache disk --name baseline_yolo11n_640 |
| frozen_matcher_test.what | test scored with autoresearch/eval.py (greedy IoU>=0.5 match, COCO-style 101-point AP) - the same code as results/metrics_zeroshot.json |
| frozen_matcher_test.trained.mAP50 | 0.8559 |
| frozen_matcher_test.trained.boot_se | 0.0112 |
| frozen_matcher_test.trained.precision@0.25 | 0.7017 |
| frozen_matcher_test.trained.recall@0.25 | 0.8571 |
| frozen_matcher_test.trained.n_gt | 1309 |
| frozen_matcher_test.zero_shot.mAP50 | 0.3935 |
| frozen_matcher_test.zero_shot.precision@0.25 | 0.7562 |
| frozen_matcher_test.zero_shot.recall@0.25 | 0.1398 |
| frozen_matcher_test.zero_shot.file | results/metrics_zeroshot.json |
| frozen_matcher_test.config.imgsz | 640 |
| frozen_matcher_test.config.conf | 0.001 |
| frozen_matcher_test.config.iou | 0.7 |
| frozen_matcher_test.config.augment | False |
| frozen_matcher_test.config.tiles | [1, 1] |
| frozen_matcher_test.config.tile_overlap | 0.2 |
| frozen_matcher_test.config.tile_plus_full | True |
| frozen_matcher_test.config.merge_iou | 0.5 |
| frozen_matcher_test.config.max_det | 300 |

## detection — metrics_zeroshot.json

Source: [`components/detection/results/metrics_zeroshot.json`](../components/detection/results/metrics_zeroshot.json)  
Reproduce: `cd innovatex-t3-coastal-plastic && bash components/detection/data/fetch_data.sh && cd components/detection && python3.11 -m t3det.prepare && curl -sSL -o ../../.data/detection/weights/yolo11n.pt https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt && python3.11 -m t3det.zeroshot --weights ../../.data/detection/weights/yolo11n.pt --split test`

| Metric | Value |
|---|---|
| label | ZERO-SHOT REFERENCE - COCO-pretrained YOLO11n, NOT trained on TUD-GV; not the trained baseline (that is results/metrics.json) |
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
| baseline_kind | ZERO-SHOT (no training on TUD-GV): COCO-pretrained YOLO11n, class-agnostic NMS, every COCO class counted as a litter candidate. Computed 2026-10-04 ~08:05 IST while the trained baseline was blocked by machine load. |
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

## twin_sim — analysis.json

Source: [`components/twin_sim/results/analysis.json`](../components/twin_sim/results/analysis.json)  
Reproduce: `cd innovatex-t3-coastal-plastic/components && python -m twin_sim.analysis`

| Metric | Value |
|---|---|
| label | SIMULATED |
| what | digital-twin analysis, held-out monsoons Jun-Sep 2024+2025, 4 sites summed; real forcing (ERA5 rain, archived JMA day-ahead forecast, harmonic tide), ASSUMPTION process parameters |
| git_sha_at_run | 8b34ea5 |
| n_draws | 40 |
| seed | 20261004 |
| years | [2024, 2025] |
| crew_budget | 2 crews x 8 h/day, all runs |
| p2_knobs.starts_utc | [1, 2, 3, 4, 5] |
| p2_knobs.tide_aware | True |
| p2_knobs.w_stock | 1 |
| p2_knobs.w_bypass | 2 |
| p2_knobs.w_over | 1 |
| p2_knobs.w_arrival | 0.25 |
| p2_knobs.loss_weight | 0 |
| p2_knobs.arr_horizon | 24 |
| definitions.interval | median and p05/p95 across the 40 Monte Carlo draws |
| definitions.paired_rel_diff | (a - b) / b per draw, same draw and sensor noise; negative = a lets less escape |
| definitions.arrived_at_boom | contract arrived_kg: includes re-arrivals of re-floated/released debris |
| definitions.fwce | (cleared + stored at 30 Sep) / catchment load; each kg counted once |
| definitions.gross_captured_over_arrived | captured_kg / arrived_kg (double-counts re-captures) |
| definitions.tidal_refloat | stored debris lifted on flood tide into the upstream pool; it re-arrives on the ebb (re-exposure flux, not an escape term) |
| definitions.flood_release | stored debris released during bypass/high head (current hardware), into the pool |
| definitions.fuse | SENSITIVITY: at release only the arriving flux passes; the pocket keeps its catch |
| definitions.refloat_mult | SENSITIVITY: one-way pocket scales tidal re-float; x1 with the fuse equals variant b |
| caveats | ['SIMULATED: escaped_kg is computed by the same assumed process model that the policies act on, so results show relative value under stated assumptions, not field evidence; field calibration comes in Round 2.', 'Fuse/pocket rows are SENSITIVITY runs (assumption-driven), not evidence about real hardware.', 'No retuning: P2 knobs, draws, seeds and crew budget identical to results/metrics.json.'] |
| escape_split.P0.escaped_kg.median | 4.283e+05 |
| escape_split.P0.escaped_kg.p05 | 1.444e+05 |
| escape_split.P0.escaped_kg.p95 | 9.615e+05 |
| escape_split.P0.arrived_at_boom_kg.median | 1.368e+06 |
| escape_split.P0.arrived_at_boom_kg.p05 | 4.148e+05 |
| escape_split.P0.arrived_at_boom_kg.p95 | 2.74e+06 |
| escape_split.P0.catchment_load_kg.median | 9.644e+05 |
| escape_split.P0.catchment_load_kg.p05 | 3.496e+05 |
| escape_split.P0.catchment_load_kg.p95 | 1.388e+06 |
| escape_split.P0.by_cause.entrainment.kg.median | 4.015e+05 |
| escape_split.P0.by_cause.entrainment.kg.p05 | 1.109e+05 |
| escape_split.P0.by_cause.entrainment.kg.p95 | 7.997e+05 |
| escape_split.P0.by_cause.entrainment.share_of_escaped.median | 0.9097 |
| escape_split.P0.by_cause.entrainment.share_of_escaped.p05 | 0.6471 |
| escape_split.P0.by_cause.entrainment.share_of_escaped.p95 | 0.9996 |
| escape_split.P0.by_cause.entrainment.share_of_arrived.median | 0.3272 |
| escape_split.P0.by_cause.entrainment.share_of_arrived.p05 | 0.1362 |
| escape_split.P0.by_cause.entrainment.share_of_arrived.p95 | 0.5794 |
| escape_split.P0.by_cause.entrainment.share_of_load.median | 0.4814 |
| escape_split.P0.by_cause.entrainment.share_of_load.p05 | 0.2136 |
| escape_split.P0.by_cause.entrainment.share_of_load.p95 | 0.6796 |
| escape_split.P0.by_cause.overtopping.kg.median | 3.665e+04 |
| escape_split.P0.by_cause.overtopping.kg.p05 | 0 |
| escape_split.P0.by_cause.overtopping.kg.p95 | 1.982e+05 |
| escape_split.P0.by_cause.overtopping.share_of_escaped.median | 0.0646 |
| escape_split.P0.by_cause.overtopping.share_of_escaped.p05 | 0 |
| escape_split.P0.by_cause.overtopping.share_of_escaped.p95 | 0.3309 |
| escape_split.P0.by_cause.overtopping.share_of_arrived.median | 0.0237 |
| escape_split.P0.by_cause.overtopping.share_of_arrived.p05 | 0 |
| escape_split.P0.by_cause.overtopping.share_of_arrived.p95 | 0.1077 |
| escape_split.P0.by_cause.overtopping.share_of_load.median | 0.0339 |
| escape_split.P0.by_cause.overtopping.share_of_load.p05 | 0 |
| escape_split.P0.by_cause.overtopping.share_of_load.p95 | 0.1435 |
| escape_split.P0.by_cause.bypass_release.kg.median | 1989 |
| escape_split.P0.by_cause.bypass_release.kg.p05 | 0 |
| escape_split.P0.by_cause.bypass_release.kg.p95 | 5.17e+04 |
| escape_split.P0.by_cause.bypass_release.share_of_escaped.median | 0.0061 |
| escape_split.P0.by_cause.bypass_release.share_of_escaped.p05 | 0 |
| escape_split.P0.by_cause.bypass_release.share_of_escaped.p95 | 0.0994 |
| escape_split.P0.by_cause.bypass_release.share_of_arrived.median | 0.0014 |
| escape_split.P0.by_cause.bypass_release.share_of_arrived.p05 | 0 |
| escape_split.P0.by_cause.bypass_release.share_of_arrived.p95 | 0.0422 |
| escape_split.P0.by_cause.bypass_release.share_of_load.median | 0.0022 |
| escape_split.P0.by_cause.bypass_release.share_of_load.p05 | 0 |
| escape_split.P0.by_cause.bypass_release.share_of_load.p95 | 0.0572 |
| escape_split.P0.refloated_kg.tidal_refloat.median | 3.029e+05 |
| escape_split.P0.refloated_kg.tidal_refloat.p05 | 5.161e+04 |
| escape_split.P0.refloated_kg.tidal_refloat.p95 | 1.335e+06 |
| escape_split.P0.refloated_kg.flood_release.median | 1167 |
| escape_split.P0.refloated_kg.flood_release.p05 | 0 |
| escape_split.P0.refloated_kg.flood_release.p95 | 2.924e+04 |
| escape_split.P0.refloated_kg.tidal_refloat_share_of_arrived.median | 0.2486 |
| escape_split.P0.refloated_kg.tidal_refloat_share_of_arrived.p05 | 0.0587 |
| escape_split.P0.refloated_kg.tidal_refloat_share_of_arrived.p95 | 0.4863 |
| escape_split.P0.held_upstream_at_season_end_kg.median | 1199 |
| escape_split.P0.held_upstream_at_season_end_kg.p05 | 332 |
| escape_split.P0.held_upstream_at_season_end_kg.p95 | 4266 |
| escape_split.P1.escaped_kg.median | 4.55e+05 |
| escape_split.P1.escaped_kg.p05 | 1.512e+05 |
| escape_split.P1.escaped_kg.p95 | 9.809e+05 |
| escape_split.P1.arrived_at_boom_kg.median | 1.414e+06 |
| escape_split.P1.arrived_at_boom_kg.p05 | 4.194e+05 |
| escape_split.P1.arrived_at_boom_kg.p95 | 2.804e+06 |
| escape_split.P1.catchment_load_kg.median | 9.644e+05 |
| escape_split.P1.catchment_load_kg.p05 | 3.496e+05 |
| escape_split.P1.catchment_load_kg.p95 | 1.388e+06 |
| escape_split.P1.by_cause.entrainment.kg.median | 4.045e+05 |
| escape_split.P1.by_cause.entrainment.kg.p05 | 1.13e+05 |
| escape_split.P1.by_cause.entrainment.kg.p95 | 8.196e+05 |
| escape_split.P1.by_cause.entrainment.share_of_escaped.median | 0.9061 |
| escape_split.P1.by_cause.entrainment.share_of_escaped.p05 | 0.6365 |
| escape_split.P1.by_cause.entrainment.share_of_escaped.p95 | 0.9996 |
| escape_split.P1.by_cause.entrainment.share_of_arrived.median | 0.3284 |
| escape_split.P1.by_cause.entrainment.share_of_arrived.p05 | 0.1356 |
| escape_split.P1.by_cause.entrainment.share_of_arrived.p95 | 0.5827 |
| escape_split.P1.by_cause.entrainment.share_of_load.median | 0.5004 |
| escape_split.P1.by_cause.entrainment.share_of_load.p05 | 0.2175 |
| escape_split.P1.by_cause.entrainment.share_of_load.p95 | 0.6983 |
| escape_split.P1.by_cause.overtopping.kg.median | 3.492e+04 |
| escape_split.P1.by_cause.overtopping.kg.p05 | 0 |
| escape_split.P1.by_cause.overtopping.kg.p95 | 2.042e+05 |
| escape_split.P1.by_cause.overtopping.share_of_escaped.median | 0.0656 |
| escape_split.P1.by_cause.overtopping.share_of_escaped.p05 | 0 |
| escape_split.P1.by_cause.overtopping.share_of_escaped.p95 | 0.3318 |
| escape_split.P1.by_cause.overtopping.share_of_arrived.median | 0.0218 |
| escape_split.P1.by_cause.overtopping.share_of_arrived.p05 | 0 |
| escape_split.P1.by_cause.overtopping.share_of_arrived.p95 | 0.1049 |
| escape_split.P1.by_cause.overtopping.share_of_load.median | 0.0323 |
| escape_split.P1.by_cause.overtopping.share_of_load.p05 | 0 |
| escape_split.P1.by_cause.overtopping.share_of_load.p95 | 0.1464 |
| escape_split.P1.by_cause.bypass_release.kg.median | 2582 |
| escape_split.P1.by_cause.bypass_release.kg.p05 | 0 |
| escape_split.P1.by_cause.bypass_release.kg.p95 | 5.624e+04 |
| escape_split.P1.by_cause.bypass_release.share_of_escaped.median | 0.0068 |
| escape_split.P1.by_cause.bypass_release.share_of_escaped.p05 | 0 |
| escape_split.P1.by_cause.bypass_release.share_of_escaped.p95 | 0.1041 |
| escape_split.P1.by_cause.bypass_release.share_of_arrived.median | 0.0016 |
| escape_split.P1.by_cause.bypass_release.share_of_arrived.p05 | 0 |
| escape_split.P1.by_cause.bypass_release.share_of_arrived.p95 | 0.0454 |
| escape_split.P1.by_cause.bypass_release.share_of_load.median | 0.0024 |
| escape_split.P1.by_cause.bypass_release.share_of_load.p05 | 0 |
| escape_split.P1.by_cause.bypass_release.share_of_load.p95 | 0.0628 |
| escape_split.P1.refloated_kg.tidal_refloat.median | 3.441e+05 |
| escape_split.P1.refloated_kg.tidal_refloat.p05 | 5.04e+04 |
| escape_split.P1.refloated_kg.tidal_refloat.p95 | 1.4e+06 |
| escape_split.P1.refloated_kg.flood_release.median | 1770 |
| escape_split.P1.refloated_kg.flood_release.p05 | 0 |
| escape_split.P1.refloated_kg.flood_release.p95 | 4.78e+04 |
| escape_split.P1.refloated_kg.tidal_refloat_share_of_arrived.median | 0.2749 |
| escape_split.P1.refloated_kg.tidal_refloat_share_of_arrived.p05 | 0.069 |
| escape_split.P1.refloated_kg.tidal_refloat_share_of_arrived.p95 | 0.4986 |
| escape_split.P1.held_upstream_at_season_end_kg.median | 1305 |
| escape_split.P1.held_upstream_at_season_end_kg.p05 | 363 |
| escape_split.P1.held_upstream_at_season_end_kg.p95 | 4096 |
| escape_split.P2.escaped_kg.median | 4.116e+05 |
| escape_split.P2.escaped_kg.p05 | 1.475e+05 |
| escape_split.P2.escaped_kg.p95 | 9.178e+05 |
| escape_split.P2.arrived_at_boom_kg.median | 1.31e+06 |
| escape_split.P2.arrived_at_boom_kg.p05 | 4.201e+05 |
| escape_split.P2.arrived_at_boom_kg.p95 | 2.591e+06 |
| escape_split.P2.catchment_load_kg.median | 9.644e+05 |
| escape_split.P2.catchment_load_kg.p05 | 3.496e+05 |
| escape_split.P2.catchment_load_kg.p95 | 1.388e+06 |
| escape_split.P2.by_cause.entrainment.kg.median | 3.92e+05 |
| escape_split.P2.by_cause.entrainment.kg.p05 | 1.124e+05 |
| escape_split.P2.by_cause.entrainment.kg.p95 | 7.565e+05 |
| escape_split.P2.by_cause.entrainment.share_of_escaped.median | 0.9253 |
| escape_split.P2.by_cause.entrainment.share_of_escaped.p05 | 0.6461 |
| escape_split.P2.by_cause.entrainment.share_of_escaped.p95 | 0.9996 |
| escape_split.P2.by_cause.entrainment.share_of_arrived.median | 0.3263 |
| escape_split.P2.by_cause.entrainment.share_of_arrived.p05 | 0.1356 |
| escape_split.P2.by_cause.entrainment.share_of_arrived.p95 | 0.5751 |
| escape_split.P2.by_cause.entrainment.share_of_load.median | 0.4586 |
| escape_split.P2.by_cause.entrainment.share_of_load.p05 | 0.2138 |
| escape_split.P2.by_cause.entrainment.share_of_load.p95 | 0.6892 |
| escape_split.P2.by_cause.overtopping.kg.median | 3.156e+04 |
| escape_split.P2.by_cause.overtopping.kg.p05 | 0 |
| escape_split.P2.by_cause.overtopping.kg.p95 | 1.837e+05 |
| escape_split.P2.by_cause.overtopping.share_of_escaped.median | 0.0588 |
| escape_split.P2.by_cause.overtopping.share_of_escaped.p05 | 0 |
| escape_split.P2.by_cause.overtopping.share_of_escaped.p95 | 0.3165 |
| escape_split.P2.by_cause.overtopping.share_of_arrived.median | 0.0168 |
| escape_split.P2.by_cause.overtopping.share_of_arrived.p05 | 0 |
| escape_split.P2.by_cause.overtopping.share_of_arrived.p95 | 0.1094 |
| escape_split.P2.by_cause.overtopping.share_of_load.median | 0.028 |
| escape_split.P2.by_cause.overtopping.share_of_load.p05 | 0 |
| escape_split.P2.by_cause.overtopping.share_of_load.p95 | 0.1365 |
| escape_split.P2.by_cause.bypass_release.kg.median | 2589 |
| escape_split.P2.by_cause.bypass_release.kg.p05 | 0 |
| escape_split.P2.by_cause.bypass_release.kg.p95 | 5.077e+04 |
| escape_split.P2.by_cause.bypass_release.share_of_escaped.median | 0.0071 |
| escape_split.P2.by_cause.bypass_release.share_of_escaped.p05 | 0 |
| escape_split.P2.by_cause.bypass_release.share_of_escaped.p95 | 0.0992 |
| escape_split.P2.by_cause.bypass_release.share_of_arrived.median | 0.0017 |
| escape_split.P2.by_cause.bypass_release.share_of_arrived.p05 | 0 |
| escape_split.P2.by_cause.bypass_release.share_of_arrived.p95 | 0.0424 |
| escape_split.P2.by_cause.bypass_release.share_of_load.median | 0.0025 |
| escape_split.P2.by_cause.bypass_release.share_of_load.p05 | 0 |
| escape_split.P2.by_cause.bypass_release.share_of_load.p95 | 0.0571 |
| escape_split.P2.refloated_kg.tidal_refloat.median | 2.662e+05 |
| escape_split.P2.refloated_kg.tidal_refloat.p05 | 5.127e+04 |
| escape_split.P2.refloated_kg.tidal_refloat.p95 | 1.185e+06 |
| escape_split.P2.refloated_kg.flood_release.median | 1445 |
| escape_split.P2.refloated_kg.flood_release.p05 | 0 |
| escape_split.P2.refloated_kg.flood_release.p95 | 2.736e+04 |
| escape_split.P2.refloated_kg.tidal_refloat_share_of_arrived.median | 0.2346 |
| escape_split.P2.refloated_kg.tidal_refloat_share_of_arrived.p05 | 0.0596 |
| escape_split.P2.refloated_kg.tidal_refloat_share_of_arrived.p95 | 0.4573 |
| escape_split.P2.held_upstream_at_season_end_kg.median | 1213 |
| escape_split.P2.held_upstream_at_season_end_kg.p05 | 350 |
| escape_split.P2.held_upstream_at_season_end_kg.p95 | 3812 |
| paired_escaped_rel_diff.P2_vs_P1.median | -0.0557 |
| paired_escaped_rel_diff.P2_vs_P1.p05 | -0.1575 |
| paired_escaped_rel_diff.P2_vs_P1.p95 | -0.0033 |
| paired_escaped_rel_diff.P2_vs_P1.draws_a_lower | 39 |
| paired_escaped_rel_diff.P2_vs_P1.n_draws | 40 |
| paired_escaped_rel_diff.P2_vs_P0.median | -0.0214 |
| paired_escaped_rel_diff.P2_vs_P0.p05 | -0.1251 |
| paired_escaped_rel_diff.P2_vs_P0.p95 | 0.0149 |
| paired_escaped_rel_diff.P2_vs_P0.draws_a_lower | 28 |
| paired_escaped_rel_diff.P2_vs_P0.n_draws | 40 |
| paired_escaped_rel_diff.P1_vs_P0.median | 0.0314 |
| paired_escaped_rel_diff.P1_vs_P0.p05 | 0.0001 |
| paired_escaped_rel_diff.P1_vs_P0.p95 | 0.0602 |
| paired_escaped_rel_diff.P1_vs_P0.draws_a_lower | 2 |
| paired_escaped_rel_diff.P1_vs_P0.n_draws | 40 |
| fwce.P0.fwce.median | 0.4603 |
| fwce.P0.fwce.p05 | 0.307 |
| fwce.P0.fwce.p95 | 0.6992 |
| fwce.P0.gross_captured_over_arrived.median | 0.64 |
| fwce.P0.gross_captured_over_arrived.p05 | 0.4197 |
| fwce.P0.gross_captured_over_arrived.p95 | 0.8284 |
| fwce.P1.fwce.median | 0.4425 |
| fwce.P1.fwce.p05 | 0.3 |
| fwce.P1.fwce.p95 | 0.6926 |
| fwce.P1.gross_captured_over_arrived.median | 0.6357 |
| fwce.P1.gross_captured_over_arrived.p05 | 0.4163 |
| fwce.P1.gross_captured_over_arrived.p95 | 0.8301 |
| fwce.P2.fwce.median | 0.4907 |
| fwce.P2.fwce.p05 | 0.3088 |
| fwce.P2.fwce.p95 | 0.7013 |
| fwce.P2.gross_captured_over_arrived.median | 0.6464 |
| fwce.P2.gross_captured_over_arrived.p05 | 0.4238 |
| fwce.P2.gross_captured_over_arrived.p95 | 0.8347 |
| fuse_sensitivity_P2.a_current_release.escaped_kg.median | 4.116e+05 |
| fuse_sensitivity_P2.a_current_release.escaped_kg.p05 | 1.475e+05 |
| fuse_sensitivity_P2.a_current_release.escaped_kg.p95 | 9.178e+05 |
| fuse_sensitivity_P2.a_current_release.escaped_rel_vs_a.median | 0 |
| fuse_sensitivity_P2.a_current_release.escaped_rel_vs_a.p05 | 0 |
| fuse_sensitivity_P2.a_current_release.escaped_rel_vs_a.p95 | 0 |
| fuse_sensitivity_P2.a_current_release.escaped_rel_vs_a.draws_a_lower | 0 |
| fuse_sensitivity_P2.a_current_release.escaped_rel_vs_a.n_draws | 40 |
| fuse_sensitivity_P2.a_current_release.fwce.median | 0.4907 |
| fuse_sensitivity_P2.a_current_release.fwce.p05 | 0.3088 |
| fuse_sensitivity_P2.a_current_release.fwce.p95 | 0.7013 |
| fuse_sensitivity_P2.a_current_release.fwce_delta_pp_vs_a.median | 0 |
| fuse_sensitivity_P2.a_current_release.fwce_delta_pp_vs_a.p05 | 0 |
| fuse_sensitivity_P2.a_current_release.fwce_delta_pp_vs_a.p95 | 0 |
| fuse_sensitivity_P2.a_current_release.by_cause_kg.entrainment.median | 3.92e+05 |
| fuse_sensitivity_P2.a_current_release.by_cause_kg.entrainment.p05 | 1.124e+05 |
| fuse_sensitivity_P2.a_current_release.by_cause_kg.entrainment.p95 | 7.565e+05 |
| fuse_sensitivity_P2.a_current_release.by_cause_kg.overtopping.median | 3.156e+04 |
| fuse_sensitivity_P2.a_current_release.by_cause_kg.overtopping.p05 | 0 |
| fuse_sensitivity_P2.a_current_release.by_cause_kg.overtopping.p95 | 1.837e+05 |
| fuse_sensitivity_P2.a_current_release.by_cause_kg.bypass_release.median | 2589 |
| fuse_sensitivity_P2.a_current_release.by_cause_kg.bypass_release.p05 | 0 |
| fuse_sensitivity_P2.a_current_release.by_cause_kg.bypass_release.p95 | 5.077e+04 |
| fuse_sensitivity_P2.a_current_release.flood_release_kg.median | 1445 |
| fuse_sensitivity_P2.a_current_release.flood_release_kg.p05 | 0 |
| fuse_sensitivity_P2.a_current_release.flood_release_kg.p95 | 2.736e+04 |
| fuse_sensitivity_P2.a_current_release.tidal_refloat_kg.median | 2.662e+05 |
| fuse_sensitivity_P2.a_current_release.tidal_refloat_kg.p05 | 5.127e+04 |
| fuse_sensitivity_P2.a_current_release.tidal_refloat_kg.p95 | 1.185e+06 |
| fuse_sensitivity_P2.b_fail_open_fuse.escaped_kg.median | 4.114e+05 |
| fuse_sensitivity_P2.b_fail_open_fuse.escaped_kg.p05 | 1.394e+05 |
| fuse_sensitivity_P2.b_fail_open_fuse.escaped_kg.p95 | 9.171e+05 |
| fuse_sensitivity_P2.b_fail_open_fuse.escaped_rel_vs_a.median | -0.0009 |
| fuse_sensitivity_P2.b_fail_open_fuse.escaped_rel_vs_a.p05 | -0.015 |
| fuse_sensitivity_P2.b_fail_open_fuse.escaped_rel_vs_a.p95 | 0 |
| fuse_sensitivity_P2.b_fail_open_fuse.escaped_rel_vs_a.draws_a_lower | 31 |
| fuse_sensitivity_P2.b_fail_open_fuse.escaped_rel_vs_a.n_draws | 40 |
| fuse_sensitivity_P2.b_fail_open_fuse.fwce.median | 0.4952 |
| fuse_sensitivity_P2.b_fail_open_fuse.fwce.p05 | 0.3093 |
| fuse_sensitivity_P2.b_fail_open_fuse.fwce.p95 | 0.7019 |
| fuse_sensitivity_P2.b_fail_open_fuse.fwce_delta_pp_vs_a.median | 0.05 |
| fuse_sensitivity_P2.b_fail_open_fuse.fwce_delta_pp_vs_a.p05 | -0 |
| fuse_sensitivity_P2.b_fail_open_fuse.fwce_delta_pp_vs_a.p95 | 0.77 |
| fuse_sensitivity_P2.b_fail_open_fuse.by_cause_kg.entrainment.median | 3.887e+05 |
| fuse_sensitivity_P2.b_fail_open_fuse.by_cause_kg.entrainment.p05 | 1.099e+05 |
| fuse_sensitivity_P2.b_fail_open_fuse.by_cause_kg.entrainment.p95 | 7.567e+05 |
| fuse_sensitivity_P2.b_fail_open_fuse.by_cause_kg.overtopping.median | 3.156e+04 |
| fuse_sensitivity_P2.b_fail_open_fuse.by_cause_kg.overtopping.p05 | 0 |
| fuse_sensitivity_P2.b_fail_open_fuse.by_cause_kg.overtopping.p95 | 1.837e+05 |
| fuse_sensitivity_P2.b_fail_open_fuse.by_cause_kg.bypass_release.median | 1843 |
| fuse_sensitivity_P2.b_fail_open_fuse.by_cause_kg.bypass_release.p05 | 0 |
| fuse_sensitivity_P2.b_fail_open_fuse.by_cause_kg.bypass_release.p95 | 4.759e+04 |
| fuse_sensitivity_P2.b_fail_open_fuse.flood_release_kg.median | 0 |
| fuse_sensitivity_P2.b_fail_open_fuse.flood_release_kg.p05 | 0 |
| fuse_sensitivity_P2.b_fail_open_fuse.flood_release_kg.p95 | 0 |
| fuse_sensitivity_P2.b_fail_open_fuse.tidal_refloat_kg.median | 2.663e+05 |
| fuse_sensitivity_P2.b_fail_open_fuse.tidal_refloat_kg.p05 | 5.232e+04 |
| fuse_sensitivity_P2.b_fail_open_fuse.tidal_refloat_kg.p95 | 1.191e+06 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.escaped_kg.median | 3.855e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.escaped_kg.p05 | 1.281e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.escaped_kg.p95 | 8.895e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.escaped_rel_vs_a.median | -0.0503 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.escaped_rel_vs_a.p05 | -0.0987 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.escaped_rel_vs_a.p95 | -0.0137 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.escaped_rel_vs_a.draws_a_lower | 40 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.escaped_rel_vs_a.n_draws | 40 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.fwce.median | 0.5149 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.fwce.p05 | 0.3284 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.fwce.p95 | 0.731 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.fwce_delta_pp_vs_a.median | 2.58 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.fwce_delta_pp_vs_a.p05 | 0.93 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.fwce_delta_pp_vs_a.p95 | 3.99 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.by_cause_kg.entrainment.median | 3.529e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.by_cause_kg.entrainment.p05 | 1.002e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.by_cause_kg.entrainment.p95 | 7.037e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.by_cause_kg.overtopping.median | 4.407e+04 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.by_cause_kg.overtopping.p05 | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.by_cause_kg.overtopping.p95 | 1.977e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.by_cause_kg.bypass_release.median | 1699 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.by_cause_kg.bypass_release.p05 | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.by_cause_kg.bypass_release.p95 | 4.501e+04 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.flood_release_kg.median | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.flood_release_kg.p05 | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.flood_release_kg.p95 | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.tidal_refloat_kg.median | 1.524e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.tidal_refloat_kg.p05 | 2.697e+04 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.tidal_refloat_kg.p95 | 9.223e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.escaped_kg.median | 3.687e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.escaped_kg.p05 | 1.194e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.escaped_kg.p95 | 8.607e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.escaped_rel_vs_a.median | -0.0941 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.escaped_rel_vs_a.p05 | -0.1655 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.escaped_rel_vs_a.p95 | -0.0217 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.escaped_rel_vs_a.draws_a_lower | 40 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.escaped_rel_vs_a.n_draws | 40 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.fwce.median | 0.5323 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.fwce.p05 | 0.3599 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.fwce.p95 | 0.751 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.fwce_delta_pp_vs_a.median | 4.6 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.fwce_delta_pp_vs_a.p05 | 1.33 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.fwce_delta_pp_vs_a.p95 | 7.19 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.by_cause_kg.entrainment.median | 3.291e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.by_cause_kg.entrainment.p05 | 9.244e+04 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.by_cause_kg.entrainment.p95 | 6.613e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.by_cause_kg.overtopping.median | 5.038e+04 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.by_cause_kg.overtopping.p05 | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.by_cause_kg.overtopping.p95 | 2.228e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.by_cause_kg.bypass_release.median | 1599 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.by_cause_kg.bypass_release.p05 | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.by_cause_kg.bypass_release.p95 | 3.231e+04 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.flood_release_kg.median | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.flood_release_kg.p05 | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.flood_release_kg.p95 | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.tidal_refloat_kg.median | 6.733e+04 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.tidal_refloat_kg.p05 | 1.095e+04 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.tidal_refloat_kg.p95 | 4.696e+05 |
| checks.mass_balance_max_abs_err_kg | 0 |
| checks.equal_crew_hours | True |
| checks.escaped_median_matches_metrics_json | True |
| checks.metrics_json_escaped_median.P0 | 4.283e+05 |
| checks.metrics_json_escaped_median.P1 | 4.55e+05 |
| checks.metrics_json_escaped_median.P2 | 4.116e+05 |
| per_draw.P0.escaped_kg | [list of 40] |
| per_draw.P0.fwce | [list of 40] |
| per_draw.P1.escaped_kg | [list of 40] |
| per_draw.P1.fwce | [list of 40] |
| per_draw.P2.escaped_kg | [list of 40] |
| per_draw.P2.fwce | [list of 40] |
| per_draw.P2|a_current_release.escaped_kg | [list of 40] |
| per_draw.P2|a_current_release.fwce | [list of 40] |
| per_draw.P2|b_fail_open_fuse.escaped_kg | [list of 40] |
| per_draw.P2|b_fail_open_fuse.fwce | [list of 40] |
| per_draw.P2|c_fuse_refloat_x0.2.escaped_kg | [list of 40] |
| per_draw.P2|c_fuse_refloat_x0.2.fwce | [list of 40] |
| per_draw.P2|c_fuse_refloat_x0.5.escaped_kg | [list of 40] |
| per_draw.P2|c_fuse_refloat_x0.5.fwce | [list of 40] |

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

