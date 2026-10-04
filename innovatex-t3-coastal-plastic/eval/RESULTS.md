# Results — every number with its reproduce command

Generated 2026-10-04 17:09 IST at commit `cc59273` by `python3 innovatex-t3-coastal-plastic/eval/collect_results.py`. Values are copied verbatim from each component's `results/metrics.json`. Labels such as SIMULATED and SYNTHETIC are part of the component's output; read them before quoting a number.

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
| git_sha_at_run | 330c689 |
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
| definitions.range | median and p05/p95 = central 90% scenario range across 40 sampled parameter settings (Monte Carlo draws of the ASSUMPTION ranges); not a confidence interval |
| definitions.paired_rel_diff | (a - b) / b per sampled parameter setting (same setting and sensor noise); negative = a lets less escape; draws_a_lower = number of the 40 settings where a < b |
| definitions.policies.P0 | assumed fixed roster (area-weighted rotation, fixed 08:30 IST shift; not BMC's roster) |
| definitions.policies.P1 | fill-fraction-ranked fixed-shift rule |
| definitions.policies.P2 | mass/risk-ranked, tide- and forecast-timed policy |
| definitions.policies.P1m | ablation: sensor-only mass-ranked fixed-shift rule (greedy on sensed kg, P1's shift) |
| definitions.policies.P2_notide | ablation: P2 with tide-aware timing off (fixed 08:30 IST start) |
| definitions.policies.P2_nofc | ablation: P2 with forecast terms off (sensed kg only; timing from tide-only access) |
| definitions.mass_boundary | unique input = catchment wash-off reaching the outfall (re-arrivals excluded) = escaped + cleared by crews (removal) + stored in boom at 30 Sep (temporary retention) + held upstream at 30 Sep; generic floating debris, not flexible packaging specifically |
| definitions.arrived_at_boom | contract arrived_kg: includes re-arrivals of re-floated/released debris |
| definitions.fwce | (cleared + stored at 30 Sep) / unique input (catchment load); each kg counted once; stored is temporary retention, cleared_share is removal |
| definitions.gross_captured_over_arrived | captured_kg / arrived_kg (double-counts re-captures) |
| definitions.tidal_refloat | stored debris lifted on flood tide into the upstream pool; it re-arrives on the ebb (re-exposure flux, not an escape term) |
| definitions.flood_release | stored debris released during bypass/high head (current hardware), into the pool |
| definitions.fuse | SENSITIVITY: at release only the arriving flux passes; the pocket keeps its catch |
| definitions.refloat_mult | SENSITIVITY: one-way pocket scales tidal re-float; x1 with the fuse equals variant b |
| definitions.sin_theta | SENSITIVITY: boom at angle theta to the flow; e(v) uses the normal component /v/*sin(theta), e_max unchanged; boom length (W/sin theta), capacity, cost and loads not modelled; P2's forecaster still assumes theta=90 (policy unchanged) |
| definitions.ent_floor | (1 - e_max) * arrived outside bypass: leaks even at slack water (ASSUMPTION e_max 0.70-0.95) |
| definitions.ent_vel | (e_max - e(v)) * arrived outside bypass: velocity-driven entrainment |
| definitions.exposure | P2, nominal parameters, held-out years: share of site-hours and of arrived kg with /v/*sin(theta) > v50 (0.45 m/s nominal) |
| caveats | ['SIMULATED: escaped_kg is computed by the same assumed process model that the policies act on, so results show relative value under stated assumptions, not field evidence; field calibration comes in Round 2.', 'Fuse/pocket rows are SENSITIVITY runs (assumption-driven), not evidence about real hardware.', 'Boom-angle rows are SENSITIVITY runs (assumption-driven): boom angle is not field evidence. Angle acts only through the assumed capture curve e(/v/ sin theta), so it cannot independently confirm that mechanism; v50 is transferred from oil-boom practice (UNVERIFIED ASSUMPTION).', 'Assumed capture losses dominate this twin; boom angle and retention are candidate field experiments.', 'No retuning: P2 knobs, draws, seeds and crew budget identical to results/metrics.json.'] |
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
| entrainment_split.P0.floor_1_minus_emax.kg.median | 1.793e+05 |
| entrainment_split.P0.floor_1_minus_emax.kg.p05 | 6.605e+04 |
| entrainment_split.P0.floor_1_minus_emax.kg.p95 | 5.437e+05 |
| entrainment_split.P0.floor_1_minus_emax.share_of_escaped.median | 0.5145 |
| entrainment_split.P0.floor_1_minus_emax.share_of_escaped.p05 | 0.1443 |
| entrainment_split.P0.floor_1_minus_emax.share_of_escaped.p95 | 0.7998 |
| entrainment_split.P0.floor_1_minus_emax.share_of_entrainment.median | 0.5617 |
| entrainment_split.P0.floor_1_minus_emax.share_of_entrainment.p05 | 0.1593 |
| entrainment_split.P0.floor_1_minus_emax.share_of_entrainment.p95 | 0.8878 |
| entrainment_split.P0.velocity_driven.kg.median | 1.549e+05 |
| entrainment_split.P0.velocity_driven.kg.p05 | 1.997e+04 |
| entrainment_split.P0.velocity_driven.kg.p95 | 4.39e+05 |
| entrainment_split.P0.velocity_driven.share_of_escaped.median | 0.3788 |
| entrainment_split.P0.velocity_driven.share_of_escaped.p05 | 0.0903 |
| entrainment_split.P0.velocity_driven.share_of_escaped.p95 | 0.8001 |
| entrainment_split.P0.velocity_driven.share_of_entrainment.median | 0.4383 |
| entrainment_split.P0.velocity_driven.share_of_entrainment.p05 | 0.1122 |
| entrainment_split.P0.velocity_driven.share_of_entrainment.p95 | 0.8407 |
| entrainment_split.P1.floor_1_minus_emax.kg.median | 1.839e+05 |
| entrainment_split.P1.floor_1_minus_emax.kg.p05 | 6.684e+04 |
| entrainment_split.P1.floor_1_minus_emax.kg.p95 | 5.593e+05 |
| entrainment_split.P1.floor_1_minus_emax.share_of_escaped.median | 0.5111 |
| entrainment_split.P1.floor_1_minus_emax.share_of_escaped.p05 | 0.1433 |
| entrainment_split.P1.floor_1_minus_emax.share_of_escaped.p95 | 0.7984 |
| entrainment_split.P1.floor_1_minus_emax.share_of_entrainment.median | 0.5598 |
| entrainment_split.P1.floor_1_minus_emax.share_of_entrainment.p05 | 0.159 |
| entrainment_split.P1.floor_1_minus_emax.share_of_entrainment.p95 | 0.8886 |
| entrainment_split.P1.velocity_driven.kg.median | 1.595e+05 |
| entrainment_split.P1.velocity_driven.kg.p05 | 2.102e+04 |
| entrainment_split.P1.velocity_driven.kg.p95 | 4.622e+05 |
| entrainment_split.P1.velocity_driven.share_of_escaped.median | 0.3781 |
| entrainment_split.P1.velocity_driven.share_of_escaped.p05 | 0.0894 |
| entrainment_split.P1.velocity_driven.share_of_escaped.p95 | 0.8009 |
| entrainment_split.P1.velocity_driven.share_of_entrainment.median | 0.4402 |
| entrainment_split.P1.velocity_driven.share_of_entrainment.p05 | 0.1114 |
| entrainment_split.P1.velocity_driven.share_of_entrainment.p95 | 0.841 |
| entrainment_split.P2.floor_1_minus_emax.kg.median | 1.79e+05 |
| entrainment_split.P2.floor_1_minus_emax.kg.p05 | 6.697e+04 |
| entrainment_split.P2.floor_1_minus_emax.kg.p95 | 4.946e+05 |
| entrainment_split.P2.floor_1_minus_emax.share_of_escaped.median | 0.513 |
| entrainment_split.P2.floor_1_minus_emax.share_of_escaped.p05 | 0.1449 |
| entrainment_split.P2.floor_1_minus_emax.share_of_escaped.p95 | 0.8149 |
| entrainment_split.P2.floor_1_minus_emax.share_of_entrainment.median | 0.5634 |
| entrainment_split.P2.floor_1_minus_emax.share_of_entrainment.p05 | 0.1593 |
| entrainment_split.P2.floor_1_minus_emax.share_of_entrainment.p95 | 0.8888 |
| entrainment_split.P2.velocity_driven.kg.median | 1.485e+05 |
| entrainment_split.P2.velocity_driven.kg.p05 | 1.969e+04 |
| entrainment_split.P2.velocity_driven.kg.p95 | 4.357e+05 |
| entrainment_split.P2.velocity_driven.share_of_escaped.median | 0.3836 |
| entrainment_split.P2.velocity_driven.share_of_escaped.p05 | 0.0913 |
| entrainment_split.P2.velocity_driven.share_of_escaped.p95 | 0.798 |
| entrainment_split.P2.velocity_driven.share_of_entrainment.median | 0.4366 |
| entrainment_split.P2.velocity_driven.share_of_entrainment.p05 | 0.1112 |
| entrainment_split.P2.velocity_driven.share_of_entrainment.p95 | 0.8407 |
| boom_angle_sensitivity_P2.a_current_release.theta90.sin_theta | 1 |
| boom_angle_sensitivity_P2.a_current_release.theta90.boom_length_factor_1_over_sin_theta | 1 |
| boom_angle_sensitivity_P2.a_current_release.theta90.escaped_kg.median | 4.116e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta90.escaped_kg.p05 | 1.475e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta90.escaped_kg.p95 | 9.178e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta90.escaped_rel_vs_theta90.median | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.escaped_rel_vs_theta90.p05 | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.escaped_rel_vs_theta90.p95 | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.escaped_rel_vs_theta90.draws_a_lower | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.escaped_rel_vs_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta90.escaped_rel_vs_current_a_theta90.median | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.escaped_rel_vs_current_a_theta90.p05 | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.escaped_rel_vs_current_a_theta90.p95 | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.escaped_rel_vs_current_a_theta90.draws_a_lower | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.escaped_rel_vs_current_a_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta90.fwce.median | 0.4907 |
| boom_angle_sensitivity_P2.a_current_release.theta90.fwce.p05 | 0.3088 |
| boom_angle_sensitivity_P2.a_current_release.theta90.fwce.p95 | 0.7013 |
| boom_angle_sensitivity_P2.a_current_release.theta90.fwce_delta_pp_vs_theta90.median | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.fwce_delta_pp_vs_theta90.p05 | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.fwce_delta_pp_vs_theta90.p95 | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.fwce_delta_pp_vs_current_a_theta90.median | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.fwce_delta_pp_vs_current_a_theta90.p05 | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.fwce_delta_pp_vs_current_a_theta90.p95 | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.velocity_entrainment_share_of_escaped.median | 0.3836 |
| boom_angle_sensitivity_P2.a_current_release.theta90.velocity_entrainment_share_of_escaped.p05 | 0.0913 |
| boom_angle_sensitivity_P2.a_current_release.theta90.velocity_entrainment_share_of_escaped.p95 | 0.798 |
| boom_angle_sensitivity_P2.a_current_release.theta45.sin_theta | 0.7071 |
| boom_angle_sensitivity_P2.a_current_release.theta45.boom_length_factor_1_over_sin_theta | 1.414 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_kg.median | 3.803e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_kg.p05 | 1.305e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_kg.p95 | 8.862e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_theta90.median | -0.104 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_theta90.p05 | -0.2103 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_theta90.p95 | -0.0078 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_current_a_theta90.median | -0.104 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_current_a_theta90.p05 | -0.2103 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_current_a_theta90.p95 | -0.0078 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_current_a_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_current_a_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta45.fwce.median | 0.5459 |
| boom_angle_sensitivity_P2.a_current_release.theta45.fwce.p05 | 0.3875 |
| boom_angle_sensitivity_P2.a_current_release.theta45.fwce.p95 | 0.7558 |
| boom_angle_sensitivity_P2.a_current_release.theta45.fwce_delta_pp_vs_theta90.median | 5.58 |
| boom_angle_sensitivity_P2.a_current_release.theta45.fwce_delta_pp_vs_theta90.p05 | 0.34 |
| boom_angle_sensitivity_P2.a_current_release.theta45.fwce_delta_pp_vs_theta90.p95 | 12.43 |
| boom_angle_sensitivity_P2.a_current_release.theta45.fwce_delta_pp_vs_current_a_theta90.median | 5.58 |
| boom_angle_sensitivity_P2.a_current_release.theta45.fwce_delta_pp_vs_current_a_theta90.p05 | 0.34 |
| boom_angle_sensitivity_P2.a_current_release.theta45.fwce_delta_pp_vs_current_a_theta90.p95 | 12.43 |
| boom_angle_sensitivity_P2.a_current_release.theta45.velocity_entrainment_share_of_escaped.median | 0.2099 |
| boom_angle_sensitivity_P2.a_current_release.theta45.velocity_entrainment_share_of_escaped.p05 | 0.02 |
| boom_angle_sensitivity_P2.a_current_release.theta45.velocity_entrainment_share_of_escaped.p95 | 0.7311 |
| boom_angle_sensitivity_P2.a_current_release.theta30.sin_theta | 0.5 |
| boom_angle_sensitivity_P2.a_current_release.theta30.boom_length_factor_1_over_sin_theta | 2 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_kg.median | 3.774e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_kg.p05 | 1.237e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_kg.p95 | 8.661e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_theta90.median | -0.1502 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_theta90.p05 | -0.3758 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_theta90.p95 | -0.0077 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_current_a_theta90.median | -0.1502 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_current_a_theta90.p05 | -0.3758 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_current_a_theta90.p95 | -0.0077 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_current_a_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_current_a_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta30.fwce.median | 0.5916 |
| boom_angle_sensitivity_P2.a_current_release.theta30.fwce.p05 | 0.3946 |
| boom_angle_sensitivity_P2.a_current_release.theta30.fwce.p95 | 0.7696 |
| boom_angle_sensitivity_P2.a_current_release.theta30.fwce_delta_pp_vs_theta90.median | 7.69 |
| boom_angle_sensitivity_P2.a_current_release.theta30.fwce_delta_pp_vs_theta90.p05 | 0.32 |
| boom_angle_sensitivity_P2.a_current_release.theta30.fwce_delta_pp_vs_theta90.p95 | 23.07 |
| boom_angle_sensitivity_P2.a_current_release.theta30.fwce_delta_pp_vs_current_a_theta90.median | 7.69 |
| boom_angle_sensitivity_P2.a_current_release.theta30.fwce_delta_pp_vs_current_a_theta90.p05 | 0.32 |
| boom_angle_sensitivity_P2.a_current_release.theta30.fwce_delta_pp_vs_current_a_theta90.p95 | 23.07 |
| boom_angle_sensitivity_P2.a_current_release.theta30.velocity_entrainment_share_of_escaped.median | 0.098 |
| boom_angle_sensitivity_P2.a_current_release.theta30.velocity_entrainment_share_of_escaped.p05 | 0.0035 |
| boom_angle_sensitivity_P2.a_current_release.theta30.velocity_entrainment_share_of_escaped.p95 | 0.5108 |
| boom_angle_sensitivity_P2.a_current_release.theta20.sin_theta | 0.342 |
| boom_angle_sensitivity_P2.a_current_release.theta20.boom_length_factor_1_over_sin_theta | 2.924 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_kg.median | 3.767e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_kg.p05 | 1.084e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_kg.p95 | 8.501e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_theta90.median | -0.1717 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_theta90.p05 | -0.4965 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_theta90.p95 | -0.007 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_current_a_theta90.median | -0.1717 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_current_a_theta90.p05 | -0.4965 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_current_a_theta90.p95 | -0.007 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_current_a_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_current_a_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta20.fwce.median | 0.6189 |
| boom_angle_sensitivity_P2.a_current_release.theta20.fwce.p05 | 0.3962 |
| boom_angle_sensitivity_P2.a_current_release.theta20.fwce.p95 | 0.7863 |
| boom_angle_sensitivity_P2.a_current_release.theta20.fwce_delta_pp_vs_theta90.median | 8.57 |
| boom_angle_sensitivity_P2.a_current_release.theta20.fwce_delta_pp_vs_theta90.p05 | 0.28 |
| boom_angle_sensitivity_P2.a_current_release.theta20.fwce_delta_pp_vs_theta90.p95 | 28.8 |
| boom_angle_sensitivity_P2.a_current_release.theta20.fwce_delta_pp_vs_current_a_theta90.median | 8.57 |
| boom_angle_sensitivity_P2.a_current_release.theta20.fwce_delta_pp_vs_current_a_theta90.p05 | 0.28 |
| boom_angle_sensitivity_P2.a_current_release.theta20.fwce_delta_pp_vs_current_a_theta90.p95 | 28.8 |
| boom_angle_sensitivity_P2.a_current_release.theta20.velocity_entrainment_share_of_escaped.median | 0.0472 |
| boom_angle_sensitivity_P2.a_current_release.theta20.velocity_entrainment_share_of_escaped.p05 | 0.0011 |
| boom_angle_sensitivity_P2.a_current_release.theta20.velocity_entrainment_share_of_escaped.p95 | 0.3585 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.sin_theta | 1 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.boom_length_factor_1_over_sin_theta | 1 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_kg.median | 3.855e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_kg.p05 | 1.281e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_kg.p95 | 8.895e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_theta90.median | 0 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_theta90.p05 | 0 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_theta90.p95 | 0 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_theta90.draws_a_lower | 0 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_current_a_theta90.median | -0.0503 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_current_a_theta90.p05 | -0.0987 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_current_a_theta90.p95 | -0.0137 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_current_a_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_current_a_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.fwce.median | 0.5149 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.fwce.p05 | 0.3284 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.fwce.p95 | 0.731 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.fwce_delta_pp_vs_theta90.median | 0 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.fwce_delta_pp_vs_theta90.p05 | 0 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.fwce_delta_pp_vs_theta90.p95 | 0 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.fwce_delta_pp_vs_current_a_theta90.median | 2.58 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.fwce_delta_pp_vs_current_a_theta90.p05 | 0.93 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.fwce_delta_pp_vs_current_a_theta90.p95 | 3.99 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.velocity_entrainment_share_of_escaped.median | 0.3734 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.velocity_entrainment_share_of_escaped.p05 | 0.0844 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.velocity_entrainment_share_of_escaped.p95 | 0.802 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.sin_theta | 0.7071 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.boom_length_factor_1_over_sin_theta | 1.414 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_kg.median | 3.545e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_kg.p05 | 1.198e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_kg.p95 | 8.623e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_theta90.median | -0.1091 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_theta90.p05 | -0.2175 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_theta90.p95 | -0.0044 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_current_a_theta90.median | -0.1666 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_current_a_theta90.p05 | -0.2803 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_current_a_theta90.p95 | -0.0479 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_current_a_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_current_a_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.fwce.median | 0.5783 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.fwce.p05 | 0.3979 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.fwce.p95 | 0.7835 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.fwce_delta_pp_vs_theta90.median | 5.29 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.fwce_delta_pp_vs_theta90.p05 | 0.21 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.fwce_delta_pp_vs_theta90.p95 | 12.49 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.fwce_delta_pp_vs_current_a_theta90.median | 8.48 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.fwce_delta_pp_vs_current_a_theta90.p05 | 2.34 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.fwce_delta_pp_vs_current_a_theta90.p95 | 15.47 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.velocity_entrainment_share_of_escaped.median | 0.2099 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.velocity_entrainment_share_of_escaped.p05 | 0.0195 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.velocity_entrainment_share_of_escaped.p95 | 0.725 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.sin_theta | 0.5 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.boom_length_factor_1_over_sin_theta | 2 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_kg.median | 3.468e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_kg.p05 | 1.131e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_kg.p95 | 8.266e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_theta90.median | -0.1646 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_theta90.p05 | -0.4044 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_theta90.p95 | -0.0062 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_current_a_theta90.median | -0.2163 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_current_a_theta90.p05 | -0.4209 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_current_a_theta90.p95 | -0.0473 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_current_a_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_current_a_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.fwce.median | 0.6191 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.fwce.p05 | 0.4013 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.fwce.p95 | 0.7964 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.fwce_delta_pp_vs_theta90.median | 7.59 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.fwce_delta_pp_vs_theta90.p05 | 0.22 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.fwce_delta_pp_vs_theta90.p95 | 22.87 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.fwce_delta_pp_vs_current_a_theta90.median | 10.66 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.fwce_delta_pp_vs_current_a_theta90.p05 | 2.59 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.fwce_delta_pp_vs_current_a_theta90.p95 | 24.97 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.velocity_entrainment_share_of_escaped.median | 0.0916 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.velocity_entrainment_share_of_escaped.p05 | 0.0033 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.velocity_entrainment_share_of_escaped.p95 | 0.5151 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.sin_theta | 0.342 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.boom_length_factor_1_over_sin_theta | 2.924 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_kg.median | 3.457e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_kg.p05 | 1.023e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_kg.p95 | 8.106e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_theta90.median | -0.1879 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_theta90.p05 | -0.5299 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_theta90.p95 | -0.0071 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_current_a_theta90.median | -0.2342 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_current_a_theta90.p05 | -0.5512 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_current_a_theta90.p95 | -0.0482 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_current_a_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_current_a_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.fwce.median | 0.661 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.fwce.p05 | 0.4012 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.fwce.p95 | 0.8106 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.fwce_delta_pp_vs_theta90.median | 8.61 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.fwce_delta_pp_vs_theta90.p05 | 0.25 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.fwce_delta_pp_vs_theta90.p95 | 27.89 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.fwce_delta_pp_vs_current_a_theta90.median | 11.68 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.fwce_delta_pp_vs_current_a_theta90.p05 | 2.68 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.fwce_delta_pp_vs_current_a_theta90.p95 | 30.66 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.velocity_entrainment_share_of_escaped.median | 0.044 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.velocity_entrainment_share_of_escaped.p05 | 0.0011 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.velocity_entrainment_share_of_escaped.p95 | 0.362 |
| ablations.paired_escaped_rel_diff.P2_vs_P1m.median | -0.0271 |
| ablations.paired_escaped_rel_diff.P2_vs_P1m.p05 | -0.1264 |
| ablations.paired_escaped_rel_diff.P2_vs_P1m.p95 | 0.0122 |
| ablations.paired_escaped_rel_diff.P2_vs_P1m.draws_a_lower | 34 |
| ablations.paired_escaped_rel_diff.P2_vs_P1m.n_draws | 40 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_notide.median | -0.0318 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_notide.p05 | -0.1197 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_notide.p95 | 0.0057 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_notide.draws_a_lower | 34 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_notide.n_draws | 40 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_nofc.median | -0.0042 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_nofc.p05 | -0.0188 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_nofc.p95 | 0.0099 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_nofc.draws_a_lower | 29 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_nofc.n_draws | 40 |
| ablations.paired_escaped_rel_diff.P1m_vs_P1.median | -0.0203 |
| ablations.paired_escaped_rel_diff.P1m_vs_P1.p05 | -0.0414 |
| ablations.paired_escaped_rel_diff.P1m_vs_P1.p95 | 0.0016 |
| ablations.paired_escaped_rel_diff.P1m_vs_P1.draws_a_lower | 37 |
| ablations.paired_escaped_rel_diff.P1m_vs_P1.n_draws | 40 |
| ablations.paired_escaped_rel_diff.P1m_vs_P0.median | 0.006 |
| ablations.paired_escaped_rel_diff.P1m_vs_P0.p05 | -0.0058 |
| ablations.paired_escaped_rel_diff.P1m_vs_P0.p95 | 0.0275 |
| ablations.paired_escaped_rel_diff.P1m_vs_P0.draws_a_lower | 10 |
| ablations.paired_escaped_rel_diff.P1m_vs_P0.n_draws | 40 |
| ablations.paired_escaped_rel_diff.P2_notide_vs_P1m.median | -0.0038 |
| ablations.paired_escaped_rel_diff.P2_notide_vs_P1m.p05 | -0.0164 |
| ablations.paired_escaped_rel_diff.P2_notide_vs_P1m.p95 | 0.0644 |
| ablations.paired_escaped_rel_diff.P2_notide_vs_P1m.draws_a_lower | 26 |
| ablations.paired_escaped_rel_diff.P2_notide_vs_P1m.n_draws | 40 |
| ablations.paired_escaped_rel_diff.P2_nofc_vs_P1m.median | -0.0223 |
| ablations.paired_escaped_rel_diff.P2_nofc_vs_P1m.p05 | -0.1292 |
| ablations.paired_escaped_rel_diff.P2_nofc_vs_P1m.p95 | 0.0035 |
| ablations.paired_escaped_rel_diff.P2_nofc_vs_P1m.draws_a_lower | 33 |
| ablations.paired_escaped_rel_diff.P2_nofc_vs_P1m.n_draws | 40 |
| ablations.paired_escaped_rel_diff.P2_vs_P1.median | -0.0557 |
| ablations.paired_escaped_rel_diff.P2_vs_P1.p05 | -0.1575 |
| ablations.paired_escaped_rel_diff.P2_vs_P1.p95 | -0.0033 |
| ablations.paired_escaped_rel_diff.P2_vs_P1.draws_a_lower | 39 |
| ablations.paired_escaped_rel_diff.P2_vs_P1.n_draws | 40 |
| ablations.escaped_kg.P0.median | 4.283e+05 |
| ablations.escaped_kg.P0.p05 | 1.444e+05 |
| ablations.escaped_kg.P0.p95 | 9.615e+05 |
| ablations.escaped_kg.P1.median | 4.55e+05 |
| ablations.escaped_kg.P1.p05 | 1.512e+05 |
| ablations.escaped_kg.P1.p95 | 9.809e+05 |
| ablations.escaped_kg.P1m.median | 4.29e+05 |
| ablations.escaped_kg.P1m.p05 | 1.477e+05 |
| ablations.escaped_kg.P1m.p95 | 9.688e+05 |
| ablations.escaped_kg.P2_notide.median | 4.485e+05 |
| ablations.escaped_kg.P2_notide.p05 | 1.554e+05 |
| ablations.escaped_kg.P2_notide.p95 | 9.654e+05 |
| ablations.escaped_kg.P2_nofc.median | 4.154e+05 |
| ablations.escaped_kg.P2_nofc.p05 | 1.506e+05 |
| ablations.escaped_kg.P2_nofc.p95 | 9.212e+05 |
| ablations.escaped_kg.P2.median | 4.116e+05 |
| ablations.escaped_kg.P2.p05 | 1.475e+05 |
| ablations.escaped_kg.P2.p95 | 9.178e+05 |
| ablations.fwce.P0.median | 0.4603 |
| ablations.fwce.P0.p05 | 0.307 |
| ablations.fwce.P0.p95 | 0.6992 |
| ablations.fwce.P1.median | 0.4425 |
| ablations.fwce.P1.p05 | 0.3 |
| ablations.fwce.P1.p95 | 0.6926 |
| ablations.fwce.P1m.median | 0.457 |
| ablations.fwce.P1m.p05 | 0.3058 |
| ablations.fwce.P1m.p95 | 0.698 |
| ablations.fwce.P2_notide.median | 0.462 |
| ablations.fwce.P2_notide.p05 | 0.3104 |
| ablations.fwce.P2_notide.p95 | 0.6974 |
| ablations.fwce.P2_nofc.median | 0.4884 |
| ablations.fwce.P2_nofc.p05 | 0.3078 |
| ablations.fwce.P2_nofc.p95 | 0.7014 |
| ablations.fwce.P2.median | 0.4907 |
| ablations.fwce.P2.p05 | 0.3088 |
| ablations.fwce.P2.p95 | 0.7013 |
| ablations.cleared_share_of_unique_input.P0.median | 0.4579 |
| ablations.cleared_share_of_unique_input.P0.p05 | 0.2977 |
| ablations.cleared_share_of_unique_input.P0.p95 | 0.6962 |
| ablations.cleared_share_of_unique_input.P1.median | 0.4408 |
| ablations.cleared_share_of_unique_input.P1.p05 | 0.2906 |
| ablations.cleared_share_of_unique_input.P1.p95 | 0.6905 |
| ablations.cleared_share_of_unique_input.P1m.median | 0.4554 |
| ablations.cleared_share_of_unique_input.P1m.p05 | 0.2938 |
| ablations.cleared_share_of_unique_input.P1m.p95 | 0.6957 |
| ablations.cleared_share_of_unique_input.P2_notide.median | 0.4591 |
| ablations.cleared_share_of_unique_input.P2_notide.p05 | 0.2985 |
| ablations.cleared_share_of_unique_input.P2_notide.p95 | 0.695 |
| ablations.cleared_share_of_unique_input.P2_nofc.median | 0.4719 |
| ablations.cleared_share_of_unique_input.P2_nofc.p05 | 0.3067 |
| ablations.cleared_share_of_unique_input.P2_nofc.p95 | 0.6981 |
| ablations.cleared_share_of_unique_input.P2.median | 0.4796 |
| ablations.cleared_share_of_unique_input.P2.p05 | 0.3075 |
| ablations.cleared_share_of_unique_input.P2.p95 | 0.6988 |
| mass_boundary.P0.unique_input_kg.median | 9.644e+05 |
| mass_boundary.P0.unique_input_kg.p05 | 3.496e+05 |
| mass_boundary.P0.unique_input_kg.p95 | 1.388e+06 |
| mass_boundary.P0.cleared_kg.median | 4.357e+05 |
| mass_boundary.P0.cleared_kg.p05 | 1.521e+05 |
| mass_boundary.P0.cleared_kg.p95 | 7.747e+05 |
| mass_boundary.P0.stored_at_season_end_kg.median | 2936 |
| mass_boundary.P0.stored_at_season_end_kg.p05 | 758 |
| mass_boundary.P0.stored_at_season_end_kg.p95 | 3.386e+04 |
| mass_boundary.P0.held_upstream_at_season_end_kg.median | 1199 |
| mass_boundary.P0.held_upstream_at_season_end_kg.p05 | 332 |
| mass_boundary.P0.held_upstream_at_season_end_kg.p95 | 4266 |
| mass_boundary.P0.escaped_kg.median | 4.283e+05 |
| mass_boundary.P0.escaped_kg.p05 | 1.444e+05 |
| mass_boundary.P0.escaped_kg.p95 | 9.615e+05 |
| mass_boundary.P0.cleared_share.median | 0.4579 |
| mass_boundary.P0.cleared_share.p05 | 0.2977 |
| mass_boundary.P0.cleared_share.p95 | 0.6962 |
| mass_boundary.P0.retained_share.median | 0.0028 |
| mass_boundary.P0.retained_share.p05 | 0.0016 |
| mass_boundary.P0.retained_share.p95 | 0.0326 |
| mass_boundary.P0.escaped_share.median | 0.5388 |
| mass_boundary.P0.escaped_share.p05 | 0.2994 |
| mass_boundary.P0.escaped_share.p95 | 0.691 |
| mass_boundary.P1.unique_input_kg.median | 9.644e+05 |
| mass_boundary.P1.unique_input_kg.p05 | 3.496e+05 |
| mass_boundary.P1.unique_input_kg.p95 | 1.388e+06 |
| mass_boundary.P1.cleared_kg.median | 4.25e+05 |
| mass_boundary.P1.cleared_kg.p05 | 1.435e+05 |
| mass_boundary.P1.cleared_kg.p95 | 7.637e+05 |
| mass_boundary.P1.stored_at_season_end_kg.median | 3045 |
| mass_boundary.P1.stored_at_season_end_kg.p05 | 509 |
| mass_boundary.P1.stored_at_season_end_kg.p95 | 3.405e+04 |
| mass_boundary.P1.held_upstream_at_season_end_kg.median | 1305 |
| mass_boundary.P1.held_upstream_at_season_end_kg.p05 | 363 |
| mass_boundary.P1.held_upstream_at_season_end_kg.p95 | 4096 |
| mass_boundary.P1.escaped_kg.median | 4.55e+05 |
| mass_boundary.P1.escaped_kg.p05 | 1.512e+05 |
| mass_boundary.P1.escaped_kg.p95 | 9.809e+05 |
| mass_boundary.P1.cleared_share.median | 0.4408 |
| mass_boundary.P1.cleared_share.p05 | 0.2906 |
| mass_boundary.P1.cleared_share.p95 | 0.6905 |
| mass_boundary.P1.retained_share.median | 0.0029 |
| mass_boundary.P1.retained_share.p05 | 0.0014 |
| mass_boundary.P1.retained_share.p95 | 0.0311 |
| mass_boundary.P1.escaped_share.median | 0.5563 |
| mass_boundary.P1.escaped_share.p05 | 0.306 |
| mass_boundary.P1.escaped_share.p95 | 0.6989 |
| mass_boundary.P2.unique_input_kg.median | 9.644e+05 |
| mass_boundary.P2.unique_input_kg.p05 | 3.496e+05 |
| mass_boundary.P2.unique_input_kg.p95 | 1.388e+06 |
| mass_boundary.P2.cleared_kg.median | 4.804e+05 |
| mass_boundary.P2.cleared_kg.p05 | 1.477e+05 |
| mass_boundary.P2.cleared_kg.p95 | 7.85e+05 |
| mass_boundary.P2.stored_at_season_end_kg.median | 2692 |
| mass_boundary.P2.stored_at_season_end_kg.p05 | 642 |
| mass_boundary.P2.stored_at_season_end_kg.p95 | 2.523e+04 |
| mass_boundary.P2.held_upstream_at_season_end_kg.median | 1213 |
| mass_boundary.P2.held_upstream_at_season_end_kg.p05 | 350 |
| mass_boundary.P2.held_upstream_at_season_end_kg.p95 | 3812 |
| mass_boundary.P2.escaped_kg.median | 4.116e+05 |
| mass_boundary.P2.escaped_kg.p05 | 1.475e+05 |
| mass_boundary.P2.escaped_kg.p95 | 9.178e+05 |
| mass_boundary.P2.cleared_share.median | 0.4796 |
| mass_boundary.P2.cleared_share.p05 | 0.3075 |
| mass_boundary.P2.cleared_share.p95 | 0.6988 |
| mass_boundary.P2.retained_share.median | 0.0026 |
| mass_boundary.P2.retained_share.p05 | 0.0013 |
| mass_boundary.P2.retained_share.p95 | 0.0255 |
| mass_boundary.P2.escaped_share.median | 0.5084 |
| mass_boundary.P2.escaped_share.p05 | 0.2973 |
| mass_boundary.P2.escaped_share.p95 | 0.69 |
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
| per_draw.P1m.escaped_kg | [list of 40] |
| per_draw.P1m.fwce | [list of 40] |
| per_draw.P2.escaped_kg | [list of 40] |
| per_draw.P2.fwce | [list of 40] |
| per_draw.P2_nofc.escaped_kg | [list of 40] |
| per_draw.P2_nofc.fwce | [list of 40] |
| per_draw.P2_notide.escaped_kg | [list of 40] |
| per_draw.P2_notide.fwce | [list of 40] |
| per_draw.P2|a_current_release.escaped_kg | [list of 40] |
| per_draw.P2|a_current_release.fwce | [list of 40] |
| per_draw.P2|a_current_release|theta20.escaped_kg | [list of 40] |
| per_draw.P2|a_current_release|theta20.fwce | [list of 40] |
| per_draw.P2|a_current_release|theta30.escaped_kg | [list of 40] |
| per_draw.P2|a_current_release|theta30.fwce | [list of 40] |
| per_draw.P2|a_current_release|theta45.escaped_kg | [list of 40] |
| per_draw.P2|a_current_release|theta45.fwce | [list of 40] |
| per_draw.P2|b_fail_open_fuse.escaped_kg | [list of 40] |
| per_draw.P2|b_fail_open_fuse.fwce | [list of 40] |
| per_draw.P2|c_fuse_refloat_x0.2.escaped_kg | [list of 40] |
| per_draw.P2|c_fuse_refloat_x0.2.fwce | [list of 40] |
| per_draw.P2|c_fuse_refloat_x0.5.escaped_kg | [list of 40] |
| per_draw.P2|c_fuse_refloat_x0.5.fwce | [list of 40] |
| per_draw.P2|c_fuse_refloat_x0.5|theta20.escaped_kg | [list of 40] |
| per_draw.P2|c_fuse_refloat_x0.5|theta20.fwce | [list of 40] |
| per_draw.P2|c_fuse_refloat_x0.5|theta30.escaped_kg | [list of 40] |
| per_draw.P2|c_fuse_refloat_x0.5|theta30.fwce | [list of 40] |
| per_draw.P2|c_fuse_refloat_x0.5|theta45.escaped_kg | [list of 40] |
| per_draw.P2|c_fuse_refloat_x0.5|theta45.fwce | [list of 40] |
| exposure_P2_nominal.v50_ms_nominal | 0.45 |
| exposure_P2_nominal.hours_per_site | 5856 |
| exposure_P2_nominal.theta90.share_of_hours | 0.1322 |
| exposure_P2_nominal.theta90.share_of_arrived_kg | 0.132 |
| exposure_P2_nominal.theta90.by_site.mithi_mahim.share_of_hours | 0.1387 |
| exposure_P2_nominal.theta90.by_site.mithi_mahim.share_of_arrived_kg | 0.1331 |
| exposure_P2_nominal.theta90.by_site.oshiwara_malad.share_of_hours | 0.1928 |
| exposure_P2_nominal.theta90.by_site.oshiwara_malad.share_of_arrived_kg | 0.1431 |
| exposure_P2_nominal.theta90.by_site.dahisar_mouth.share_of_hours | 0.1918 |
| exposure_P2_nominal.theta90.by_site.dahisar_mouth.share_of_arrived_kg | 0.1614 |
| exposure_P2_nominal.theta90.by_site.trombay_mahul.share_of_hours | 0.0056 |
| exposure_P2_nominal.theta90.by_site.trombay_mahul.share_of_arrived_kg | 0.005 |
| exposure_P2_nominal.theta45.share_of_hours | 0.0417 |
| exposure_P2_nominal.theta45.share_of_arrived_kg | 0.0359 |
| exposure_P2_nominal.theta30.share_of_hours | 0.0066 |
| exposure_P2_nominal.theta30.share_of_arrived_kg | 0.0038 |
| exposure_P2_nominal.theta20.share_of_hours | 0.0003 |
| exposure_P2_nominal.theta20.share_of_arrived_kg | 0.0001 |

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

