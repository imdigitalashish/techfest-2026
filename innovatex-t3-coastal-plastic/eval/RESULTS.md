# Results — every number with its reproduce command

Generated 2026-10-04 17:57 IST at commit `88ee99b` by `python3 innovatex-t3-coastal-plastic/eval/collect_results.py`. Values are copied verbatim from each component's `results/metrics.json`. Labels such as SIMULATED and SYNTHETIC are part of the component's output; read them before quoting a number.

## detection — flux_synthetic.json

Source: [`components/detection/results/flux_synthetic.json`](../components/detection/results/flux_synthetic.json)  
Reproduce: `cd innovatex-t3-coastal-plastic/components/detection && T3DET_DEVICE=cpu nice -n 10 python3.11 -m t3det.run_flux --weights ../../.data/detection/runs/baseline_yolo11n_640/weights/best.pt --sequences all --imgsz 640 --conf 0.1 --legacy-diagnostic   (sequences are regenerated deterministically by t3det.synth from SUITE in t3det/run_flux.py)`

| Metric | Value |
|---|---|
| label | SYNTHETIC |
| what | C6 count accuracy on SYNTHETIC clips: real TUD-GV test-split litter crops drift left to right over an inpainted TUD-GV water frame, with exact ground-truth line crossings |
| detector | trained baseline |
| detector_model_id | baseline_yolo11n_640/best.pt#sha256:a5157292e2c0 |
| device | cpu |
| imgsz | 640 |
| conf | 0.1 |
| tracker | ByteTrack (ultralytics bytetrack.yaml defaults), persistent across frames, reset per clip |
| counter_direction.line | [[640.0, 0], [640.0, 720]] |
| counter_direction.gt_direction | left_to_right |
| counter_direction.flow_vector | [1.0, 0.0] |
| counter_direction.direction_sign | -1 |
| counter_direction.rule | derived from the ground truth via CountingLine.direction_for_flow, so the counter counts exactly the crossings the ground truth counts |
| matching.tolerance_s | 1 |
| matching.tolerance_frames | 5 |
| matching.y_gate | /dy/ <= max(16 px, 0.5 x item height) |
| matching.assignment | one-to-one, Hungarian (scipy linear_sum_assignment) minimising /dt//tol + /dy//gate over admissible pairs |
| matching.false_duplicate | an admissible GT crossing exists but is already matched |
| matching.false_spurious | no GT crossing within the tolerance |
| headline.sequences | 10 |
| headline.gt_crossings | 132 |
| headline.predicted | 153 |
| headline.matched | 128 |
| headline.false | 25 |
| headline.false_duplicate | 23 |
| headline.false_spurious | 2 |
| headline.missed | 4 |
| headline.duplicates_on_multi_box_crops | 5 |
| headline.crossing_precision | 0.8366 |
| headline.crossing_recall | 0.9697 |
| headline.signed_count_error_pct | 15.91 |
| headline.signed_count_error_ci95_pct | [6.06, 28.03] |
| headline.ci_method | percentile bootstrap over 10 sequences, 2000 resamples, seed 0 |
| headline.abs_count_error_pct | 15.91 |
| sensitivity_pooled.0.4s.matched | 128 |
| sensitivity_pooled.0.4s.false | 25 |
| sensitivity_pooled.0.4s.missed | 4 |
| sensitivity_pooled.1.0s.matched | 128 |
| sensitivity_pooled.1.0s.false | 25 |
| sensitivity_pooled.1.0s.missed | 4 |
| sensitivity_pooled.2.0s.matched | 128 |
| sensitivity_pooled.2.0s.false | 25 |
| sensitivity_pooled.2.0s.missed | 4 |
| diagnostics.both_directions_same_tracks.label | DIAGNOSTIC - counts crossings in either direction; the ground truth counts left-to-right only |
| diagnostics.both_directions_same_tracks.predicted | 153 |
| diagnostics.both_directions_same_tracks.matched | 128 |
| diagnostics.both_directions_same_tracks.false | 25 |
| diagnostics.both_directions_same_tracks.missed | 4 |
| diagnostics.both_directions_same_tracks.signed_count_error_pct | 15.91 |
| diagnostics.both_directions_same_tracks.signed_count_error_ci95_pct | [6.06, 28.03] |
| diagnostics.both_directions_same_tracks.ci_method | percentile bootstrap over 10 sequences, 2000 resamples, seed 0 |
| diagnostics.legacy_overnight_config.label | DIAGNOSTIC - configuration published before the fix (tracker re-initialised every frame by persist=False on the first call; both directions counted). Not a valid C6 result. |
| diagnostics.legacy_overnight_config.sequence | seq02 |
| diagnostics.legacy_overnight_config.gt_crossings | 12 |
| diagnostics.legacy_overnight_config.predicted | 16 |
| diagnostics.legacy_overnight_config.unique_track_ids | 17 |
| diagnostics.legacy_overnight_config.matched | 6 |
| diagnostics.legacy_overnight_config.false | 10 |
| diagnostics.legacy_overnight_config.missed | 6 |
| sequence | seq02 |
| frames | 120 |
| fps | 5 |
| gt_crossings | 12 |
| items_crossed | 13 |
| count_error_pct | 8.33 |
| signed_count_error_pct | 8.33 |
| matched | 11 |
| false | 2 |
| missed | 1 |
| per_sequence | [list of 10] |
| flux_estimate.site_id | SYNTHETIC-seq02 |
| flux_estimate.t_start | 2026-10-04T00:00:00Z |
| flux_estimate.t_end | 2026-10-04T00:00:24Z |
| flux_estimate.items_crossed | 13 |
| flux_estimate.items_per_min | 32.5 |
| flux_estimate.by_label.litter | 13 |
| flux_estimate.est_kg | 0.247 |
| flux_estimate.est_kg_ci90 | [0.0275, 0.4665] |
| flux_estimate.method | YOLO detector + ByteTrack (ultralytics, persistent across frames, conf>=0.1) + line-crossing count, one count per track id, direction into side -1 only; mass = items x 19.0 g/item (sd 37.0 g; assumption: van Emmerik et al. 2019 Sci Rep (Saigon), PMC6753078: 1.9e-2 kg per visually counted item, sd 3.7e-2; transfer to Mumbai assumed); CI90 = n*mean +/- 1.645*sd*sqrt(n) |
| flux_estimate.provenance.kind | synthetic |
| flux_estimate.provenance.source | component:detection/t3det.synth seed=11 |
| flux_estimate.provenance.retrieved_at | 2026-10-04T12:13:49.769968Z |
| flux_estimate.provenance.notes | SYNTHETIC: real TUD-GV test-split litter crops pasted on an inpainted TUD-GV water frame; mass factor is an ASSUMPTION transferred from the Saigon River (van Emmerik et al. 2019) |
| evaluated_at | 2026-10-04T17:44:58+05:30 |

## detection — flux_synthetic_zeroshot.json

Source: [`components/detection/results/flux_synthetic_zeroshot.json`](../components/detection/results/flux_synthetic_zeroshot.json)  
Reproduce: `cd innovatex-t3-coastal-plastic/components/detection && T3DET_DEVICE=cpu nice -n 10 python3.11 -m t3det.run_flux --weights ../../.data/detection/weights/yolo11n.pt --sequences seq02 --imgsz 640 --conf 0.1 --detector-kind "ZERO-SHOT COCO-pretrained YOLO11n (not trained on TUD-GV)" --out results/flux_synthetic_zeroshot.json   (sequences are regenerated deterministically by t3det.synth from SUITE in t3det/run_flux.py)`

| Metric | Value |
|---|---|
| label | SYNTHETIC |
| what | C6 count accuracy on SYNTHETIC clips: real TUD-GV test-split litter crops drift left to right over an inpainted TUD-GV water frame, with exact ground-truth line crossings |
| detector | ZERO-SHOT COCO-pretrained YOLO11n (not trained on TUD-GV) |
| detector_model_id | detection/yolo11n.pt#sha256:0ebbc80d4a76 |
| device | cpu |
| imgsz | 640 |
| conf | 0.1 |
| tracker | ByteTrack (ultralytics bytetrack.yaml defaults), persistent across frames, reset per clip |
| counter_direction.line | [[640.0, 0], [640.0, 720]] |
| counter_direction.gt_direction | left_to_right |
| counter_direction.flow_vector | [1.0, 0.0] |
| counter_direction.direction_sign | -1 |
| counter_direction.rule | derived from the ground truth via CountingLine.direction_for_flow, so the counter counts exactly the crossings the ground truth counts |
| matching.tolerance_s | 1 |
| matching.tolerance_frames | 5 |
| matching.y_gate | /dy/ <= max(16 px, 0.5 x item height) |
| matching.assignment | one-to-one, Hungarian (scipy linear_sum_assignment) minimising /dt//tol + /dy//gate over admissible pairs |
| matching.false_duplicate | an admissible GT crossing exists but is already matched |
| matching.false_spurious | no GT crossing within the tolerance |
| headline.sequences | 1 |
| headline.gt_crossings | 12 |
| headline.predicted | 0 |
| headline.matched | 0 |
| headline.false | 0 |
| headline.false_duplicate | 0 |
| headline.false_spurious | 0 |
| headline.missed | 12 |
| headline.duplicates_on_multi_box_crops | 0 |
| headline.crossing_precision | 0 |
| headline.crossing_recall | 0 |
| headline.signed_count_error_pct | -100 |
| headline.signed_count_error_ci95_pct | None |
| headline.ci_method | not computed (fewer than 3 sequences) |
| headline.abs_count_error_pct | 100 |
| sensitivity_pooled.0.4s.matched | 0 |
| sensitivity_pooled.0.4s.false | 0 |
| sensitivity_pooled.0.4s.missed | 12 |
| sensitivity_pooled.1.0s.matched | 0 |
| sensitivity_pooled.1.0s.false | 0 |
| sensitivity_pooled.1.0s.missed | 12 |
| sensitivity_pooled.2.0s.matched | 0 |
| sensitivity_pooled.2.0s.false | 0 |
| sensitivity_pooled.2.0s.missed | 12 |
| diagnostics.both_directions_same_tracks.label | DIAGNOSTIC - counts crossings in either direction; the ground truth counts left-to-right only |
| diagnostics.both_directions_same_tracks.predicted | 0 |
| diagnostics.both_directions_same_tracks.matched | 0 |
| diagnostics.both_directions_same_tracks.false | 0 |
| diagnostics.both_directions_same_tracks.missed | 12 |
| diagnostics.both_directions_same_tracks.signed_count_error_pct | -100 |
| diagnostics.both_directions_same_tracks.signed_count_error_ci95_pct | None |
| diagnostics.both_directions_same_tracks.ci_method | not computed (fewer than 3 sequences) |
| sequence | seq02 |
| frames | 120 |
| fps | 5 |
| gt_crossings | 12 |
| items_crossed | 0 |
| count_error_pct | 100 |
| signed_count_error_pct | -100 |
| matched | 0 |
| false | 0 |
| missed | 12 |
| per_sequence | [{'sequence': 'seq02', 'seed': 11, 'frames': 120, 'gt_crossings': 12, 'predicted': 0, 'matched': 0, 'false': 0, 'false_duplicate': 0, 'false_spurious': 0, 'missed': 12, 'signed_count_error_pct': -100.0, 'duplicates_on_multi_box_crops': 0, 'unique_track_ids': 2, 'both_directions': {'predicted': 0, 'matched': 0, 'false': 0, 'missed': 12}, 'sensitivity': {'0.4s': {'matched': 0, 'false': 0, 'missed': 12}, '1.0s': {'matched': 0, 'false': 0, 'missed': 12}, '2.0s': {'matched': 0, 'false': 0, 'missed': 12}}, 'missed_item_crop_h': [36, 42, 44, 46, 49, 50, 52, 58, 62, 64, 65, 93], 'matched_item_crop_h': []}] |
| flux_estimate.site_id | SYNTHETIC-seq02 |
| flux_estimate.t_start | 2026-10-04T00:00:00Z |
| flux_estimate.t_end | 2026-10-04T00:00:24Z |
| flux_estimate.items_crossed | 0 |
| flux_estimate.items_per_min | 0 |
| flux_estimate.est_kg | 0 |
| flux_estimate.est_kg_ci90 | [0.0, 0.0] |
| flux_estimate.method | YOLO detector + ByteTrack (ultralytics, persistent across frames, conf>=0.1) + line-crossing count, one count per track id, direction into side -1 only; mass = items x 19.0 g/item (sd 37.0 g; assumption: van Emmerik et al. 2019 Sci Rep (Saigon), PMC6753078: 1.9e-2 kg per visually counted item, sd 3.7e-2; transfer to Mumbai assumed); CI90 = n*mean +/- 1.645*sd*sqrt(n) |
| flux_estimate.provenance.kind | synthetic |
| flux_estimate.provenance.source | component:detection/t3det.synth seed=11 |
| flux_estimate.provenance.retrieved_at | 2026-10-04T12:15:04.550088Z |
| flux_estimate.provenance.notes | SYNTHETIC: real TUD-GV test-split litter crops pasted on an inpainted TUD-GV water frame; mass factor is an ASSUMPTION transferred from the Saigon River (van Emmerik et al. 2019) |
| evaluated_at | 2026-10-04T17:45:08+05:30 |

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
Reproduce: `cd innovatex-t3-coastal-plastic/components && nice -n 10 python3 -m mrv_ledger.evaluate`

| Metric | Value |
|---|---|
| data | SYNTHETIC (mrv_ledger/synth.py); parameters are ASSUMPTIONS (reconcile.Params) |
| params.wet_bulk_density_kg_m3 | 150 |
| params.moisture_fraction | 0.4 |
| params.sigma_fill_abs | 0.03 |
| params.sigma_density_rel | 0.25 |
| params.sigma_claim_rel | 0.1 |
| params.z_review | 2.142 |
| params.z_reject | 2.326 |
| params.max_wet_density_kg_m3 | 450 |
| params_json.z_review | 2.142 |
| params_json.meaning | reconcile() flags 'review' when z > z_review (z_reject stays the N(0,1) 1% ASSUMPTION) |
| params_json.calibration.target_false_flag_rate | 0.05 |
| params_json.calibration.calibration_target_fpr | 0.04746 |
| params_json.calibration.n_cal | 20000 |
| params_json.calibration.seed_cal | 11 |
| params_json.calibration.data | SYNTHETIC honest trips from mrv_ledger.synth.make_trips |
| params_json.calibration.model_params.wet_bulk_density_kg_m3 | 150 |
| params_json.calibration.model_params.moisture_fraction | 0.4 |
| params_json.calibration.model_params.sigma_fill_abs | 0.03 |
| params_json.calibration.model_params.sigma_density_rel | 0.25 |
| params_json.calibration.model_params.sigma_claim_rel | 0.1 |
| params_json.calibration.model_params.z_reject | 2.326 |
| params_json.calibration.model_params.max_wet_density_kg_m3 | 450 |
| params_json.code_commit | 11b895405ea1220812b9415b7633f1394be0f24f |
| params_json.worktree_clean_at_calibration | True |
| params_json.calibrated_at_ist | 2026-10-04T17:29:05+05:30 |
| params_json.reproduce | cd innovatex-t3-coastal-plastic/components && nice -n 10 python3 -m mrv_ledger.evaluate |
| params_json.code_commit_note | calibrated at local commit 0a13367; rebased onto main as this commit with identical mrv_ledger code |
| params_json_rewritten_by_this_run | False |
| reconciliation.shipped_z_review | 2.142 |
| reconciliation.params_source | innovatex-t3-coastal-plastic/components/mrv_ledger/params.json |
| reconciliation.calibration_target_fpr | 0.0475 |
| reconciliation.ratio_threshold_baseline | 1.768 |
| reconciliation.honest_reject_rate_at_z_reject | 0.037 |
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
| reconciliation.methods.uncalibrated_prior_z1.645.recall_all_fraud | 0.7824 |
| reconciliation.methods.uncalibrated_prior_z1.645.false_flag_rate_honest | 0.0902 |
| reconciliation.methods.uncalibrated_prior_z1.645.precision_at_5pct_prevalence | 0.3134 |
| reconciliation.methods.uncalibrated_prior_z1.645.precision_at_10pct_prevalence | 0.4908 |
| reconciliation.methods.uncalibrated_prior_z1.645.recall_inflated | 0.769 |
| reconciliation.methods.uncalibrated_prior_z1.645.recall_phantom | 1 |
| reconciliation.methods.uncalibrated_prior_z1.645.recall_wetted | 0.605 |
| reconciliation.methods.uncalibrated_prior_z1.645.recall_inflated_x1.2-1.5 | 0.3609 |
| reconciliation.methods.uncalibrated_prior_z1.645.recall_inflated_x1.5-2.0 | 0.6987 |
| reconciliation.methods.uncalibrated_prior_z1.645.recall_inflated_x2.0-3.0 | 0.9266 |
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
| tamper.insider_resign_suffix.trials | 200 |
| tamper.insider_resign_suffix.detected_with_anchor | 1 |
| tamper.insider_resign_suffix.detected_by_signatures | 1 |
| tamper.insider_resign_suffix.note | signatures miss it only if every rewritten record is the insider's own |
| tamper.all_detected_with_anchor | True |
| git_sha_at_run | 6564f17 |

## mrv_ledger — metrics.json

Source: [`components/mrv_ledger/results/metrics.json`](../components/mrv_ledger/results/metrics.json)  
Reproduce: `cd innovatex-t3-coastal-plastic/components && nice -n 10 python3 -m mrv_ledger.evaluate`

| Metric | Value |
|---|---|
| data | SYNTHETIC |
| z_review_shipped | 2.142 |
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
| insider_resign_detected_by_signatures | 1 |

## twin_sim — analysis.json

Source: [`components/twin_sim/results/analysis.json`](../components/twin_sim/results/analysis.json)  
Reproduce: `cd innovatex-t3-coastal-plastic/components && python -m twin_sim.analysis`

| Metric | Value |
|---|---|
| label | SIMULATED |
| what | digital-twin analysis, held-out monsoons Jun-Sep 2024+2025, 4 sites summed; real forcing (ERA5 rain, archived JMA day-ahead forecast, harmonic tide), ASSUMPTION process parameters |
| git_sha_at_run | ffe7d44 |
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
| escape_split.P0.escaped_kg.median | 4.273e+05 |
| escape_split.P0.escaped_kg.p05 | 1.44e+05 |
| escape_split.P0.escaped_kg.p95 | 9.592e+05 |
| escape_split.P0.arrived_at_boom_kg.median | 1.362e+06 |
| escape_split.P0.arrived_at_boom_kg.p05 | 4.122e+05 |
| escape_split.P0.arrived_at_boom_kg.p95 | 2.703e+06 |
| escape_split.P0.catchment_load_kg.median | 9.644e+05 |
| escape_split.P0.catchment_load_kg.p05 | 3.496e+05 |
| escape_split.P0.catchment_load_kg.p95 | 1.388e+06 |
| escape_split.P0.by_cause.entrainment.kg.median | 4.031e+05 |
| escape_split.P0.by_cause.entrainment.kg.p05 | 1.115e+05 |
| escape_split.P0.by_cause.entrainment.kg.p95 | 8.033e+05 |
| escape_split.P0.by_cause.entrainment.share_of_escaped.median | 0.921 |
| escape_split.P0.by_cause.entrainment.share_of_escaped.p05 | 0.6582 |
| escape_split.P0.by_cause.entrainment.share_of_escaped.p95 | 0.9998 |
| escape_split.P0.by_cause.entrainment.share_of_arrived.median | 0.333 |
| escape_split.P0.by_cause.entrainment.share_of_arrived.p05 | 0.1387 |
| escape_split.P0.by_cause.entrainment.share_of_arrived.p95 | 0.5847 |
| escape_split.P0.by_cause.entrainment.share_of_load.median | 0.4863 |
| escape_split.P0.by_cause.entrainment.share_of_load.p05 | 0.2173 |
| escape_split.P0.by_cause.entrainment.share_of_load.p95 | 0.6837 |
| escape_split.P0.by_cause.overtopping.kg.median | 3.548e+04 |
| escape_split.P0.by_cause.overtopping.kg.p05 | 0 |
| escape_split.P0.by_cause.overtopping.kg.p95 | 1.953e+05 |
| escape_split.P0.by_cause.overtopping.share_of_escaped.median | 0.0617 |
| escape_split.P0.by_cause.overtopping.share_of_escaped.p05 | 0 |
| escape_split.P0.by_cause.overtopping.share_of_escaped.p95 | 0.3301 |
| escape_split.P0.by_cause.overtopping.share_of_arrived.median | 0.0231 |
| escape_split.P0.by_cause.overtopping.share_of_arrived.p05 | 0 |
| escape_split.P0.by_cause.overtopping.share_of_arrived.p95 | 0.1072 |
| escape_split.P0.by_cause.overtopping.share_of_load.median | 0.0323 |
| escape_split.P0.by_cause.overtopping.share_of_load.p05 | 0 |
| escape_split.P0.by_cause.overtopping.share_of_load.p95 | 0.1414 |
| escape_split.P0.by_cause.bypass_release.kg.median | 1446 |
| escape_split.P0.by_cause.bypass_release.kg.p05 | 0 |
| escape_split.P0.by_cause.bypass_release.kg.p95 | 4.135e+04 |
| escape_split.P0.by_cause.bypass_release.share_of_escaped.median | 0.0035 |
| escape_split.P0.by_cause.bypass_release.share_of_escaped.p05 | 0 |
| escape_split.P0.by_cause.bypass_release.share_of_escaped.p95 | 0.0837 |
| escape_split.P0.by_cause.bypass_release.share_of_arrived.median | 0.0011 |
| escape_split.P0.by_cause.bypass_release.share_of_arrived.p05 | 0 |
| escape_split.P0.by_cause.bypass_release.share_of_arrived.p95 | 0.0366 |
| escape_split.P0.by_cause.bypass_release.share_of_load.median | 0.0015 |
| escape_split.P0.by_cause.bypass_release.share_of_load.p05 | 0 |
| escape_split.P0.by_cause.bypass_release.share_of_load.p95 | 0.0477 |
| escape_split.P0.refloated_kg.tidal_refloat.median | 2.994e+05 |
| escape_split.P0.refloated_kg.tidal_refloat.p05 | 5.193e+04 |
| escape_split.P0.refloated_kg.tidal_refloat.p95 | 1.3e+06 |
| escape_split.P0.refloated_kg.flood_release.median | 654 |
| escape_split.P0.refloated_kg.flood_release.p05 | 0 |
| escape_split.P0.refloated_kg.flood_release.p95 | 2.378e+04 |
| escape_split.P0.refloated_kg.tidal_refloat_share_of_arrived.median | 0.2454 |
| escape_split.P0.refloated_kg.tidal_refloat_share_of_arrived.p05 | 0.0575 |
| escape_split.P0.refloated_kg.tidal_refloat_share_of_arrived.p95 | 0.4797 |
| escape_split.P0.held_upstream_at_season_end_kg.median | 1198 |
| escape_split.P0.held_upstream_at_season_end_kg.p05 | 332 |
| escape_split.P0.held_upstream_at_season_end_kg.p95 | 4314 |
| escape_split.P1.escaped_kg.median | 4.488e+05 |
| escape_split.P1.escaped_kg.p05 | 1.5e+05 |
| escape_split.P1.escaped_kg.p95 | 9.795e+05 |
| escape_split.P1.arrived_at_boom_kg.median | 1.404e+06 |
| escape_split.P1.arrived_at_boom_kg.p05 | 4.196e+05 |
| escape_split.P1.arrived_at_boom_kg.p95 | 2.77e+06 |
| escape_split.P1.catchment_load_kg.median | 9.644e+05 |
| escape_split.P1.catchment_load_kg.p05 | 3.496e+05 |
| escape_split.P1.catchment_load_kg.p95 | 1.388e+06 |
| escape_split.P1.by_cause.entrainment.kg.median | 4.103e+05 |
| escape_split.P1.by_cause.entrainment.kg.p05 | 1.136e+05 |
| escape_split.P1.by_cause.entrainment.kg.p95 | 8.227e+05 |
| escape_split.P1.by_cause.entrainment.share_of_escaped.median | 0.9173 |
| escape_split.P1.by_cause.entrainment.share_of_escaped.p05 | 0.6481 |
| escape_split.P1.by_cause.entrainment.share_of_escaped.p95 | 0.9998 |
| escape_split.P1.by_cause.entrainment.share_of_arrived.median | 0.3341 |
| escape_split.P1.by_cause.entrainment.share_of_arrived.p05 | 0.138 |
| escape_split.P1.by_cause.entrainment.share_of_arrived.p95 | 0.588 |
| escape_split.P1.by_cause.entrainment.share_of_load.median | 0.5036 |
| escape_split.P1.by_cause.entrainment.share_of_load.p05 | 0.2206 |
| escape_split.P1.by_cause.entrainment.share_of_load.p95 | 0.7021 |
| escape_split.P1.by_cause.overtopping.kg.median | 3.297e+04 |
| escape_split.P1.by_cause.overtopping.kg.p05 | 0 |
| escape_split.P1.by_cause.overtopping.kg.p95 | 2.015e+05 |
| escape_split.P1.by_cause.overtopping.share_of_escaped.median | 0.0644 |
| escape_split.P1.by_cause.overtopping.share_of_escaped.p05 | 0 |
| escape_split.P1.by_cause.overtopping.share_of_escaped.p95 | 0.331 |
| escape_split.P1.by_cause.overtopping.share_of_arrived.median | 0.0209 |
| escape_split.P1.by_cause.overtopping.share_of_arrived.p05 | 0 |
| escape_split.P1.by_cause.overtopping.share_of_arrived.p95 | 0.1052 |
| escape_split.P1.by_cause.overtopping.share_of_load.median | 0.031 |
| escape_split.P1.by_cause.overtopping.share_of_load.p05 | 0 |
| escape_split.P1.by_cause.overtopping.share_of_load.p95 | 0.1445 |
| escape_split.P1.by_cause.bypass_release.kg.median | 1768 |
| escape_split.P1.by_cause.bypass_release.kg.p05 | 0 |
| escape_split.P1.by_cause.bypass_release.kg.p95 | 4.528e+04 |
| escape_split.P1.by_cause.bypass_release.share_of_escaped.median | 0.0039 |
| escape_split.P1.by_cause.bypass_release.share_of_escaped.p05 | 0 |
| escape_split.P1.by_cause.bypass_release.share_of_escaped.p95 | 0.0901 |
| escape_split.P1.by_cause.bypass_release.share_of_arrived.median | 0.0011 |
| escape_split.P1.by_cause.bypass_release.share_of_arrived.p05 | 0 |
| escape_split.P1.by_cause.bypass_release.share_of_arrived.p95 | 0.0398 |
| escape_split.P1.by_cause.bypass_release.share_of_load.median | 0.0017 |
| escape_split.P1.by_cause.bypass_release.share_of_load.p05 | 0 |
| escape_split.P1.by_cause.bypass_release.share_of_load.p95 | 0.052 |
| escape_split.P1.refloated_kg.tidal_refloat.median | 3.417e+05 |
| escape_split.P1.refloated_kg.tidal_refloat.p05 | 5.046e+04 |
| escape_split.P1.refloated_kg.tidal_refloat.p95 | 1.367e+06 |
| escape_split.P1.refloated_kg.flood_release.median | 1056 |
| escape_split.P1.refloated_kg.flood_release.p05 | 0 |
| escape_split.P1.refloated_kg.flood_release.p95 | 4.059e+04 |
| escape_split.P1.refloated_kg.tidal_refloat_share_of_arrived.median | 0.2731 |
| escape_split.P1.refloated_kg.tidal_refloat_share_of_arrived.p05 | 0.0683 |
| escape_split.P1.refloated_kg.tidal_refloat_share_of_arrived.p95 | 0.4926 |
| escape_split.P1.held_upstream_at_season_end_kg.median | 1283 |
| escape_split.P1.held_upstream_at_season_end_kg.p05 | 361 |
| escape_split.P1.held_upstream_at_season_end_kg.p95 | 4189 |
| escape_split.P2.escaped_kg.median | 4.11e+05 |
| escape_split.P2.escaped_kg.p05 | 1.446e+05 |
| escape_split.P2.escaped_kg.p95 | 9.143e+05 |
| escape_split.P2.arrived_at_boom_kg.median | 1.299e+06 |
| escape_split.P2.arrived_at_boom_kg.p05 | 4.163e+05 |
| escape_split.P2.arrived_at_boom_kg.p95 | 2.553e+06 |
| escape_split.P2.catchment_load_kg.median | 9.644e+05 |
| escape_split.P2.catchment_load_kg.p05 | 3.496e+05 |
| escape_split.P2.catchment_load_kg.p95 | 1.388e+06 |
| escape_split.P2.by_cause.entrainment.kg.median | 3.968e+05 |
| escape_split.P2.by_cause.entrainment.kg.p05 | 1.129e+05 |
| escape_split.P2.by_cause.entrainment.kg.p95 | 7.591e+05 |
| escape_split.P2.by_cause.entrainment.share_of_escaped.median | 0.9307 |
| escape_split.P2.by_cause.entrainment.share_of_escaped.p05 | 0.6573 |
| escape_split.P2.by_cause.entrainment.share_of_escaped.p95 | 0.9996 |
| escape_split.P2.by_cause.entrainment.share_of_arrived.median | 0.3318 |
| escape_split.P2.by_cause.entrainment.share_of_arrived.p05 | 0.1381 |
| escape_split.P2.by_cause.entrainment.share_of_arrived.p95 | 0.5805 |
| escape_split.P2.by_cause.entrainment.share_of_load.median | 0.4594 |
| escape_split.P2.by_cause.entrainment.share_of_load.p05 | 0.2176 |
| escape_split.P2.by_cause.entrainment.share_of_load.p95 | 0.6923 |
| escape_split.P2.by_cause.overtopping.kg.median | 2.94e+04 |
| escape_split.P2.by_cause.overtopping.kg.p05 | 0 |
| escape_split.P2.by_cause.overtopping.kg.p95 | 1.817e+05 |
| escape_split.P2.by_cause.overtopping.share_of_escaped.median | 0.055 |
| escape_split.P2.by_cause.overtopping.share_of_escaped.p05 | 0 |
| escape_split.P2.by_cause.overtopping.share_of_escaped.p95 | 0.3152 |
| escape_split.P2.by_cause.overtopping.share_of_arrived.median | 0.0159 |
| escape_split.P2.by_cause.overtopping.share_of_arrived.p05 | 0 |
| escape_split.P2.by_cause.overtopping.share_of_arrived.p95 | 0.1073 |
| escape_split.P2.by_cause.overtopping.share_of_load.median | 0.0265 |
| escape_split.P2.by_cause.overtopping.share_of_load.p05 | 0 |
| escape_split.P2.by_cause.overtopping.share_of_load.p95 | 0.1334 |
| escape_split.P2.by_cause.bypass_release.kg.median | 1812 |
| escape_split.P2.by_cause.bypass_release.kg.p05 | 0 |
| escape_split.P2.by_cause.bypass_release.kg.p95 | 3.998e+04 |
| escape_split.P2.by_cause.bypass_release.share_of_escaped.median | 0.0046 |
| escape_split.P2.by_cause.bypass_release.share_of_escaped.p05 | 0 |
| escape_split.P2.by_cause.bypass_release.share_of_escaped.p95 | 0.0855 |
| escape_split.P2.by_cause.bypass_release.share_of_arrived.median | 0.0014 |
| escape_split.P2.by_cause.bypass_release.share_of_arrived.p05 | 0 |
| escape_split.P2.by_cause.bypass_release.share_of_arrived.p95 | 0.0373 |
| escape_split.P2.by_cause.bypass_release.share_of_load.median | 0.002 |
| escape_split.P2.by_cause.bypass_release.share_of_load.p05 | 0 |
| escape_split.P2.by_cause.bypass_release.share_of_load.p95 | 0.0475 |
| escape_split.P2.refloated_kg.tidal_refloat.median | 2.585e+05 |
| escape_split.P2.refloated_kg.tidal_refloat.p05 | 5.265e+04 |
| escape_split.P2.refloated_kg.tidal_refloat.p95 | 1.148e+06 |
| escape_split.P2.refloated_kg.flood_release.median | 1102 |
| escape_split.P2.refloated_kg.flood_release.p05 | 0 |
| escape_split.P2.refloated_kg.flood_release.p95 | 2.38e+04 |
| escape_split.P2.refloated_kg.tidal_refloat_share_of_arrived.median | 0.2304 |
| escape_split.P2.refloated_kg.tidal_refloat_share_of_arrived.p05 | 0.0594 |
| escape_split.P2.refloated_kg.tidal_refloat_share_of_arrived.p95 | 0.4495 |
| escape_split.P2.held_upstream_at_season_end_kg.median | 1213 |
| escape_split.P2.held_upstream_at_season_end_kg.p05 | 349 |
| escape_split.P2.held_upstream_at_season_end_kg.p95 | 3890 |
| paired_escaped_rel_diff.P2_vs_P1.median | -0.0522 |
| paired_escaped_rel_diff.P2_vs_P1.p05 | -0.1588 |
| paired_escaped_rel_diff.P2_vs_P1.p95 | -0.0076 |
| paired_escaped_rel_diff.P2_vs_P1.draws_a_lower | 39 |
| paired_escaped_rel_diff.P2_vs_P1.n_draws | 40 |
| paired_escaped_rel_diff.P2_vs_P0.median | -0.0195 |
| paired_escaped_rel_diff.P2_vs_P0.p05 | -0.1254 |
| paired_escaped_rel_diff.P2_vs_P0.p95 | 0.0132 |
| paired_escaped_rel_diff.P2_vs_P0.draws_a_lower | 28 |
| paired_escaped_rel_diff.P2_vs_P0.n_draws | 40 |
| paired_escaped_rel_diff.P1_vs_P0.median | 0.03 |
| paired_escaped_rel_diff.P1_vs_P0.p05 | -0.0007 |
| paired_escaped_rel_diff.P1_vs_P0.p95 | 0.0574 |
| paired_escaped_rel_diff.P1_vs_P0.draws_a_lower | 3 |
| paired_escaped_rel_diff.P1_vs_P0.n_draws | 40 |
| fwce.P0.fwce.median | 0.4577 |
| fwce.P0.fwce.p05 | 0.3131 |
| fwce.P0.fwce.p95 | 0.6969 |
| fwce.P0.gross_captured_over_arrived.median | 0.6391 |
| fwce.P0.gross_captured_over_arrived.p05 | 0.4146 |
| fwce.P0.gross_captured_over_arrived.p95 | 0.8277 |
| fwce.P1.fwce.median | 0.4442 |
| fwce.P1.fwce.p05 | 0.2964 |
| fwce.P1.fwce.p95 | 0.6935 |
| fwce.P1.gross_captured_over_arrived.median | 0.6353 |
| fwce.P1.gross_captured_over_arrived.p05 | 0.4112 |
| fwce.P1.gross_captured_over_arrived.p95 | 0.829 |
| fwce.P2.fwce.median | 0.4897 |
| fwce.P2.fwce.p05 | 0.3059 |
| fwce.P2.fwce.p95 | 0.6986 |
| fwce.P2.gross_captured_over_arrived.median | 0.6418 |
| fwce.P2.gross_captured_over_arrived.p05 | 0.4187 |
| fwce.P2.gross_captured_over_arrived.p95 | 0.8343 |
| fuse_sensitivity_P2.a_current_release.escaped_kg.median | 4.11e+05 |
| fuse_sensitivity_P2.a_current_release.escaped_kg.p05 | 1.446e+05 |
| fuse_sensitivity_P2.a_current_release.escaped_kg.p95 | 9.143e+05 |
| fuse_sensitivity_P2.a_current_release.escaped_rel_vs_a.median | 0 |
| fuse_sensitivity_P2.a_current_release.escaped_rel_vs_a.p05 | 0 |
| fuse_sensitivity_P2.a_current_release.escaped_rel_vs_a.p95 | 0 |
| fuse_sensitivity_P2.a_current_release.escaped_rel_vs_a.draws_a_lower | 0 |
| fuse_sensitivity_P2.a_current_release.escaped_rel_vs_a.n_draws | 40 |
| fuse_sensitivity_P2.a_current_release.fwce.median | 0.4897 |
| fuse_sensitivity_P2.a_current_release.fwce.p05 | 0.3059 |
| fuse_sensitivity_P2.a_current_release.fwce.p95 | 0.6986 |
| fuse_sensitivity_P2.a_current_release.fwce_delta_pp_vs_a.median | 0 |
| fuse_sensitivity_P2.a_current_release.fwce_delta_pp_vs_a.p05 | 0 |
| fuse_sensitivity_P2.a_current_release.fwce_delta_pp_vs_a.p95 | 0 |
| fuse_sensitivity_P2.a_current_release.by_cause_kg.entrainment.median | 3.968e+05 |
| fuse_sensitivity_P2.a_current_release.by_cause_kg.entrainment.p05 | 1.129e+05 |
| fuse_sensitivity_P2.a_current_release.by_cause_kg.entrainment.p95 | 7.591e+05 |
| fuse_sensitivity_P2.a_current_release.by_cause_kg.overtopping.median | 2.94e+04 |
| fuse_sensitivity_P2.a_current_release.by_cause_kg.overtopping.p05 | 0 |
| fuse_sensitivity_P2.a_current_release.by_cause_kg.overtopping.p95 | 1.817e+05 |
| fuse_sensitivity_P2.a_current_release.by_cause_kg.bypass_release.median | 1812 |
| fuse_sensitivity_P2.a_current_release.by_cause_kg.bypass_release.p05 | 0 |
| fuse_sensitivity_P2.a_current_release.by_cause_kg.bypass_release.p95 | 3.998e+04 |
| fuse_sensitivity_P2.a_current_release.flood_release_kg.median | 1102 |
| fuse_sensitivity_P2.a_current_release.flood_release_kg.p05 | 0 |
| fuse_sensitivity_P2.a_current_release.flood_release_kg.p95 | 2.38e+04 |
| fuse_sensitivity_P2.a_current_release.tidal_refloat_kg.median | 2.585e+05 |
| fuse_sensitivity_P2.a_current_release.tidal_refloat_kg.p05 | 5.265e+04 |
| fuse_sensitivity_P2.a_current_release.tidal_refloat_kg.p95 | 1.148e+06 |
| fuse_sensitivity_P2.b_fail_open_fuse.escaped_kg.median | 4.108e+05 |
| fuse_sensitivity_P2.b_fail_open_fuse.escaped_kg.p05 | 1.371e+05 |
| fuse_sensitivity_P2.b_fail_open_fuse.escaped_kg.p95 | 9.142e+05 |
| fuse_sensitivity_P2.b_fail_open_fuse.escaped_rel_vs_a.median | -0.0008 |
| fuse_sensitivity_P2.b_fail_open_fuse.escaped_rel_vs_a.p05 | -0.0139 |
| fuse_sensitivity_P2.b_fail_open_fuse.escaped_rel_vs_a.p95 | 0 |
| fuse_sensitivity_P2.b_fail_open_fuse.escaped_rel_vs_a.draws_a_lower | 30 |
| fuse_sensitivity_P2.b_fail_open_fuse.escaped_rel_vs_a.n_draws | 40 |
| fuse_sensitivity_P2.b_fail_open_fuse.fwce.median | 0.4936 |
| fuse_sensitivity_P2.b_fail_open_fuse.fwce.p05 | 0.3065 |
| fuse_sensitivity_P2.b_fail_open_fuse.fwce.p95 | 0.6991 |
| fuse_sensitivity_P2.b_fail_open_fuse.fwce_delta_pp_vs_a.median | 0.04 |
| fuse_sensitivity_P2.b_fail_open_fuse.fwce_delta_pp_vs_a.p05 | 0 |
| fuse_sensitivity_P2.b_fail_open_fuse.fwce_delta_pp_vs_a.p95 | 0.71 |
| fuse_sensitivity_P2.b_fail_open_fuse.by_cause_kg.entrainment.median | 3.949e+05 |
| fuse_sensitivity_P2.b_fail_open_fuse.by_cause_kg.entrainment.p05 | 1.106e+05 |
| fuse_sensitivity_P2.b_fail_open_fuse.by_cause_kg.entrainment.p95 | 7.598e+05 |
| fuse_sensitivity_P2.b_fail_open_fuse.by_cause_kg.overtopping.median | 2.94e+04 |
| fuse_sensitivity_P2.b_fail_open_fuse.by_cause_kg.overtopping.p05 | 0 |
| fuse_sensitivity_P2.b_fail_open_fuse.by_cause_kg.overtopping.p95 | 1.817e+05 |
| fuse_sensitivity_P2.b_fail_open_fuse.by_cause_kg.bypass_release.median | 1124 |
| fuse_sensitivity_P2.b_fail_open_fuse.by_cause_kg.bypass_release.p05 | 0 |
| fuse_sensitivity_P2.b_fail_open_fuse.by_cause_kg.bypass_release.p95 | 3.834e+04 |
| fuse_sensitivity_P2.b_fail_open_fuse.flood_release_kg.median | 0 |
| fuse_sensitivity_P2.b_fail_open_fuse.flood_release_kg.p05 | 0 |
| fuse_sensitivity_P2.b_fail_open_fuse.flood_release_kg.p95 | 0 |
| fuse_sensitivity_P2.b_fail_open_fuse.tidal_refloat_kg.median | 2.586e+05 |
| fuse_sensitivity_P2.b_fail_open_fuse.tidal_refloat_kg.p05 | 5.327e+04 |
| fuse_sensitivity_P2.b_fail_open_fuse.tidal_refloat_kg.p95 | 1.153e+06 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.escaped_kg.median | 3.863e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.escaped_kg.p05 | 1.256e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.escaped_kg.p95 | 8.846e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.escaped_rel_vs_a.median | -0.0515 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.escaped_rel_vs_a.p05 | -0.0962 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.escaped_rel_vs_a.p95 | -0.0151 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.escaped_rel_vs_a.draws_a_lower | 40 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.escaped_rel_vs_a.n_draws | 40 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.fwce.median | 0.5122 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.fwce.p05 | 0.3293 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.fwce.p95 | 0.7278 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.fwce_delta_pp_vs_a.median | 2.62 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.fwce_delta_pp_vs_a.p05 | 0.9 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.fwce_delta_pp_vs_a.p95 | 4.07 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.by_cause_kg.entrainment.median | 3.546e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.by_cause_kg.entrainment.p05 | 1.005e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.by_cause_kg.entrainment.p95 | 7.052e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.by_cause_kg.overtopping.median | 4.212e+04 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.by_cause_kg.overtopping.p05 | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.by_cause_kg.overtopping.p95 | 1.95e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.by_cause_kg.bypass_release.median | 1082 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.by_cause_kg.bypass_release.p05 | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.by_cause_kg.bypass_release.p95 | 3.62e+04 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.flood_release_kg.median | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.flood_release_kg.p05 | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.flood_release_kg.p95 | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.tidal_refloat_kg.median | 1.439e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.tidal_refloat_kg.p05 | 2.75e+04 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.5.tidal_refloat_kg.p95 | 8.818e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.escaped_kg.median | 3.698e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.escaped_kg.p05 | 1.176e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.escaped_kg.p95 | 8.583e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.escaped_rel_vs_a.median | -0.0927 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.escaped_rel_vs_a.p05 | -0.1614 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.escaped_rel_vs_a.p95 | -0.0243 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.escaped_rel_vs_a.draws_a_lower | 40 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.escaped_rel_vs_a.n_draws | 40 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.fwce.median | 0.5374 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.fwce.p05 | 0.3584 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.fwce.p95 | 0.7475 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.fwce_delta_pp_vs_a.median | 4.48 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.fwce_delta_pp_vs_a.p05 | 1.32 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.fwce_delta_pp_vs_a.p95 | 7.03 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.by_cause_kg.entrainment.median | 3.315e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.by_cause_kg.entrainment.p05 | 9.289e+04 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.by_cause_kg.entrainment.p95 | 6.704e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.by_cause_kg.overtopping.median | 4.835e+04 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.by_cause_kg.overtopping.p05 | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.by_cause_kg.overtopping.p95 | 2.213e+05 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.by_cause_kg.bypass_release.median | 1041 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.by_cause_kg.bypass_release.p05 | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.by_cause_kg.bypass_release.p95 | 2.63e+04 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.flood_release_kg.median | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.flood_release_kg.p05 | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.flood_release_kg.p95 | 0 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.tidal_refloat_kg.median | 6.452e+04 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.tidal_refloat_kg.p05 | 1.121e+04 |
| fuse_sensitivity_P2.c_fuse_refloat_x0.2.tidal_refloat_kg.p95 | 4.631e+05 |
| entrainment_split.P0.floor_1_minus_emax.kg.median | 1.792e+05 |
| entrainment_split.P0.floor_1_minus_emax.kg.p05 | 6.596e+04 |
| entrainment_split.P0.floor_1_minus_emax.kg.p95 | 5.38e+05 |
| entrainment_split.P0.floor_1_minus_emax.share_of_escaped.median | 0.5107 |
| entrainment_split.P0.floor_1_minus_emax.share_of_escaped.p05 | 0.1421 |
| entrainment_split.P0.floor_1_minus_emax.share_of_escaped.p95 | 0.799 |
| entrainment_split.P0.floor_1_minus_emax.share_of_entrainment.median | 0.555 |
| entrainment_split.P0.floor_1_minus_emax.share_of_entrainment.p05 | 0.1574 |
| entrainment_split.P0.floor_1_minus_emax.share_of_entrainment.p95 | 0.8826 |
| entrainment_split.P0.velocity_driven.kg.median | 1.578e+05 |
| entrainment_split.P0.velocity_driven.kg.p05 | 2.084e+04 |
| entrainment_split.P0.velocity_driven.kg.p95 | 4.482e+05 |
| entrainment_split.P0.velocity_driven.share_of_escaped.median | 0.3903 |
| entrainment_split.P0.velocity_driven.share_of_escaped.p05 | 0.0975 |
| entrainment_split.P0.velocity_driven.share_of_escaped.p95 | 0.8024 |
| entrainment_split.P0.velocity_driven.share_of_entrainment.median | 0.445 |
| entrainment_split.P0.velocity_driven.share_of_entrainment.p05 | 0.1174 |
| entrainment_split.P0.velocity_driven.share_of_entrainment.p95 | 0.8426 |
| entrainment_split.P1.floor_1_minus_emax.kg.median | 1.84e+05 |
| entrainment_split.P1.floor_1_minus_emax.kg.p05 | 6.687e+04 |
| entrainment_split.P1.floor_1_minus_emax.kg.p95 | 5.504e+05 |
| entrainment_split.P1.floor_1_minus_emax.share_of_escaped.median | 0.5073 |
| entrainment_split.P1.floor_1_minus_emax.share_of_escaped.p05 | 0.1412 |
| entrainment_split.P1.floor_1_minus_emax.share_of_escaped.p95 | 0.7983 |
| entrainment_split.P1.floor_1_minus_emax.share_of_entrainment.median | 0.5531 |
| entrainment_split.P1.floor_1_minus_emax.share_of_entrainment.p05 | 0.1556 |
| entrainment_split.P1.floor_1_minus_emax.share_of_entrainment.p95 | 0.8836 |
| entrainment_split.P1.velocity_driven.kg.median | 1.623e+05 |
| entrainment_split.P1.velocity_driven.kg.p05 | 2.185e+04 |
| entrainment_split.P1.velocity_driven.kg.p95 | 4.716e+05 |
| entrainment_split.P1.velocity_driven.share_of_escaped.median | 0.3902 |
| entrainment_split.P1.velocity_driven.share_of_escaped.p05 | 0.0964 |
| entrainment_split.P1.velocity_driven.share_of_escaped.p95 | 0.8031 |
| entrainment_split.P1.velocity_driven.share_of_entrainment.median | 0.4469 |
| entrainment_split.P1.velocity_driven.share_of_entrainment.p05 | 0.1164 |
| entrainment_split.P1.velocity_driven.share_of_entrainment.p95 | 0.8444 |
| entrainment_split.P2.floor_1_minus_emax.kg.median | 1.786e+05 |
| entrainment_split.P2.floor_1_minus_emax.kg.p05 | 6.67e+04 |
| entrainment_split.P2.floor_1_minus_emax.kg.p95 | 4.853e+05 |
| entrainment_split.P2.floor_1_minus_emax.share_of_escaped.median | 0.5067 |
| entrainment_split.P2.floor_1_minus_emax.share_of_escaped.p05 | 0.1439 |
| entrainment_split.P2.floor_1_minus_emax.share_of_escaped.p95 | 0.8161 |
| entrainment_split.P2.floor_1_minus_emax.share_of_entrainment.median | 0.5566 |
| entrainment_split.P2.floor_1_minus_emax.share_of_entrainment.p05 | 0.1573 |
| entrainment_split.P2.floor_1_minus_emax.share_of_entrainment.p95 | 0.8833 |
| entrainment_split.P2.velocity_driven.kg.median | 1.514e+05 |
| entrainment_split.P2.velocity_driven.kg.p05 | 2.064e+04 |
| entrainment_split.P2.velocity_driven.kg.p95 | 4.449e+05 |
| entrainment_split.P2.velocity_driven.share_of_escaped.median | 0.3974 |
| entrainment_split.P2.velocity_driven.share_of_escaped.p05 | 0.0988 |
| entrainment_split.P2.velocity_driven.share_of_escaped.p95 | 0.8005 |
| entrainment_split.P2.velocity_driven.share_of_entrainment.median | 0.4434 |
| entrainment_split.P2.velocity_driven.share_of_entrainment.p05 | 0.1167 |
| entrainment_split.P2.velocity_driven.share_of_entrainment.p95 | 0.8427 |
| boom_angle_sensitivity_P2.a_current_release.theta90.sin_theta | 1 |
| boom_angle_sensitivity_P2.a_current_release.theta90.boom_length_factor_1_over_sin_theta | 1 |
| boom_angle_sensitivity_P2.a_current_release.theta90.escaped_kg.median | 4.11e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta90.escaped_kg.p05 | 1.446e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta90.escaped_kg.p95 | 9.143e+05 |
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
| boom_angle_sensitivity_P2.a_current_release.theta90.fwce.median | 0.4897 |
| boom_angle_sensitivity_P2.a_current_release.theta90.fwce.p05 | 0.3059 |
| boom_angle_sensitivity_P2.a_current_release.theta90.fwce.p95 | 0.6986 |
| boom_angle_sensitivity_P2.a_current_release.theta90.fwce_delta_pp_vs_theta90.median | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.fwce_delta_pp_vs_theta90.p05 | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.fwce_delta_pp_vs_theta90.p95 | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.fwce_delta_pp_vs_current_a_theta90.median | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.fwce_delta_pp_vs_current_a_theta90.p05 | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.fwce_delta_pp_vs_current_a_theta90.p95 | 0 |
| boom_angle_sensitivity_P2.a_current_release.theta90.velocity_entrainment_share_of_escaped.median | 0.3974 |
| boom_angle_sensitivity_P2.a_current_release.theta90.velocity_entrainment_share_of_escaped.p05 | 0.0988 |
| boom_angle_sensitivity_P2.a_current_release.theta90.velocity_entrainment_share_of_escaped.p95 | 0.8005 |
| boom_angle_sensitivity_P2.a_current_release.theta45.sin_theta | 0.7071 |
| boom_angle_sensitivity_P2.a_current_release.theta45.boom_length_factor_1_over_sin_theta | 1.414 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_kg.median | 3.79e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_kg.p05 | 1.315e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_kg.p95 | 8.809e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_theta90.median | -0.1046 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_theta90.p05 | -0.2085 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_theta90.p95 | -0.0072 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_current_a_theta90.median | -0.1046 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_current_a_theta90.p05 | -0.2085 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_current_a_theta90.p95 | -0.0072 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_current_a_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta45.escaped_rel_vs_current_a_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta45.fwce.median | 0.5489 |
| boom_angle_sensitivity_P2.a_current_release.theta45.fwce.p05 | 0.3851 |
| boom_angle_sensitivity_P2.a_current_release.theta45.fwce.p95 | 0.7557 |
| boom_angle_sensitivity_P2.a_current_release.theta45.fwce_delta_pp_vs_theta90.median | 5.69 |
| boom_angle_sensitivity_P2.a_current_release.theta45.fwce_delta_pp_vs_theta90.p05 | 0.42 |
| boom_angle_sensitivity_P2.a_current_release.theta45.fwce_delta_pp_vs_theta90.p95 | 12.41 |
| boom_angle_sensitivity_P2.a_current_release.theta45.fwce_delta_pp_vs_current_a_theta90.median | 5.69 |
| boom_angle_sensitivity_P2.a_current_release.theta45.fwce_delta_pp_vs_current_a_theta90.p05 | 0.42 |
| boom_angle_sensitivity_P2.a_current_release.theta45.fwce_delta_pp_vs_current_a_theta90.p95 | 12.41 |
| boom_angle_sensitivity_P2.a_current_release.theta45.velocity_entrainment_share_of_escaped.median | 0.2216 |
| boom_angle_sensitivity_P2.a_current_release.theta45.velocity_entrainment_share_of_escaped.p05 | 0.0224 |
| boom_angle_sensitivity_P2.a_current_release.theta45.velocity_entrainment_share_of_escaped.p95 | 0.7415 |
| boom_angle_sensitivity_P2.a_current_release.theta30.sin_theta | 0.5 |
| boom_angle_sensitivity_P2.a_current_release.theta30.boom_length_factor_1_over_sin_theta | 2 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_kg.median | 3.731e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_kg.p05 | 1.198e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_kg.p95 | 8.623e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_theta90.median | -0.1528 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_theta90.p05 | -0.3832 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_theta90.p95 | -0.0061 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_current_a_theta90.median | -0.1528 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_current_a_theta90.p05 | -0.3832 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_current_a_theta90.p95 | -0.0061 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_current_a_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta30.escaped_rel_vs_current_a_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta30.fwce.median | 0.5917 |
| boom_angle_sensitivity_P2.a_current_release.theta30.fwce.p05 | 0.4004 |
| boom_angle_sensitivity_P2.a_current_release.theta30.fwce.p95 | 0.7717 |
| boom_angle_sensitivity_P2.a_current_release.theta30.fwce_delta_pp_vs_theta90.median | 8.08 |
| boom_angle_sensitivity_P2.a_current_release.theta30.fwce_delta_pp_vs_theta90.p05 | 0.35 |
| boom_angle_sensitivity_P2.a_current_release.theta30.fwce_delta_pp_vs_theta90.p95 | 22.88 |
| boom_angle_sensitivity_P2.a_current_release.theta30.fwce_delta_pp_vs_current_a_theta90.median | 8.08 |
| boom_angle_sensitivity_P2.a_current_release.theta30.fwce_delta_pp_vs_current_a_theta90.p05 | 0.35 |
| boom_angle_sensitivity_P2.a_current_release.theta30.fwce_delta_pp_vs_current_a_theta90.p95 | 22.88 |
| boom_angle_sensitivity_P2.a_current_release.theta30.velocity_entrainment_share_of_escaped.median | 0.1019 |
| boom_angle_sensitivity_P2.a_current_release.theta30.velocity_entrainment_share_of_escaped.p05 | 0.0038 |
| boom_angle_sensitivity_P2.a_current_release.theta30.velocity_entrainment_share_of_escaped.p95 | 0.5192 |
| boom_angle_sensitivity_P2.a_current_release.theta20.sin_theta | 0.342 |
| boom_angle_sensitivity_P2.a_current_release.theta20.boom_length_factor_1_over_sin_theta | 2.924 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_kg.median | 3.719e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_kg.p05 | 1.089e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_kg.p95 | 8.466e+05 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_theta90.median | -0.1775 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_theta90.p05 | -0.4974 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_theta90.p95 | -0.0079 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_current_a_theta90.median | -0.1775 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_current_a_theta90.p05 | -0.4974 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_current_a_theta90.p95 | -0.0079 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_current_a_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta20.escaped_rel_vs_current_a_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.a_current_release.theta20.fwce.median | 0.6246 |
| boom_angle_sensitivity_P2.a_current_release.theta20.fwce.p05 | 0.4016 |
| boom_angle_sensitivity_P2.a_current_release.theta20.fwce.p95 | 0.7903 |
| boom_angle_sensitivity_P2.a_current_release.theta20.fwce_delta_pp_vs_theta90.median | 8.88 |
| boom_angle_sensitivity_P2.a_current_release.theta20.fwce_delta_pp_vs_theta90.p05 | 0.45 |
| boom_angle_sensitivity_P2.a_current_release.theta20.fwce_delta_pp_vs_theta90.p95 | 29.47 |
| boom_angle_sensitivity_P2.a_current_release.theta20.fwce_delta_pp_vs_current_a_theta90.median | 8.88 |
| boom_angle_sensitivity_P2.a_current_release.theta20.fwce_delta_pp_vs_current_a_theta90.p05 | 0.45 |
| boom_angle_sensitivity_P2.a_current_release.theta20.fwce_delta_pp_vs_current_a_theta90.p95 | 29.47 |
| boom_angle_sensitivity_P2.a_current_release.theta20.velocity_entrainment_share_of_escaped.median | 0.0481 |
| boom_angle_sensitivity_P2.a_current_release.theta20.velocity_entrainment_share_of_escaped.p05 | 0.0011 |
| boom_angle_sensitivity_P2.a_current_release.theta20.velocity_entrainment_share_of_escaped.p95 | 0.3667 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.sin_theta | 1 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.boom_length_factor_1_over_sin_theta | 1 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_kg.median | 3.863e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_kg.p05 | 1.256e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_kg.p95 | 8.846e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_theta90.median | 0 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_theta90.p05 | 0 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_theta90.p95 | 0 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_theta90.draws_a_lower | 0 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_current_a_theta90.median | -0.0515 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_current_a_theta90.p05 | -0.0962 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_current_a_theta90.p95 | -0.0151 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_current_a_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.escaped_rel_vs_current_a_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.fwce.median | 0.5122 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.fwce.p05 | 0.3293 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.fwce.p95 | 0.7278 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.fwce_delta_pp_vs_theta90.median | 0 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.fwce_delta_pp_vs_theta90.p05 | 0 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.fwce_delta_pp_vs_theta90.p95 | 0 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.fwce_delta_pp_vs_current_a_theta90.median | 2.62 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.fwce_delta_pp_vs_current_a_theta90.p05 | 0.9 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.fwce_delta_pp_vs_current_a_theta90.p95 | 4.07 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.velocity_entrainment_share_of_escaped.median | 0.3845 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.velocity_entrainment_share_of_escaped.p05 | 0.0934 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta90.velocity_entrainment_share_of_escaped.p95 | 0.8042 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.sin_theta | 0.7071 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.boom_length_factor_1_over_sin_theta | 1.414 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_kg.median | 3.536e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_kg.p05 | 1.209e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_kg.p95 | 8.568e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_theta90.median | -0.1109 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_theta90.p05 | -0.2198 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_theta90.p95 | -0.0054 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_current_a_theta90.median | -0.1696 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_current_a_theta90.p05 | -0.2881 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_current_a_theta90.p95 | -0.0483 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_current_a_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.escaped_rel_vs_current_a_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.fwce.median | 0.5799 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.fwce.p05 | 0.4029 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.fwce.p95 | 0.784 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.fwce_delta_pp_vs_theta90.median | 5.47 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.fwce_delta_pp_vs_theta90.p05 | 0.24 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.fwce_delta_pp_vs_theta90.p95 | 12.45 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.fwce_delta_pp_vs_current_a_theta90.median | 8.76 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.fwce_delta_pp_vs_current_a_theta90.p05 | 2.23 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.fwce_delta_pp_vs_current_a_theta90.p95 | 15.45 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.velocity_entrainment_share_of_escaped.median | 0.2194 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.velocity_entrainment_share_of_escaped.p05 | 0.0219 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta45.velocity_entrainment_share_of_escaped.p95 | 0.7363 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.sin_theta | 0.5 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.boom_length_factor_1_over_sin_theta | 2 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_kg.median | 3.432e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_kg.p05 | 1.103e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_kg.p95 | 8.211e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_theta90.median | -0.1667 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_theta90.p05 | -0.4021 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_theta90.p95 | -0.0085 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_current_a_theta90.median | -0.22 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_current_a_theta90.p05 | -0.4183 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_current_a_theta90.p95 | -0.0548 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_current_a_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.escaped_rel_vs_current_a_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.fwce.median | 0.6214 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.fwce.p05 | 0.4058 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.fwce.p95 | 0.7989 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.fwce_delta_pp_vs_theta90.median | 7.75 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.fwce_delta_pp_vs_theta90.p05 | 0.38 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.fwce_delta_pp_vs_theta90.p95 | 23.45 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.fwce_delta_pp_vs_current_a_theta90.median | 10.98 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.fwce_delta_pp_vs_current_a_theta90.p05 | 2.52 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.fwce_delta_pp_vs_current_a_theta90.p95 | 24.99 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.velocity_entrainment_share_of_escaped.median | 0.0954 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.velocity_entrainment_share_of_escaped.p05 | 0.0039 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta30.velocity_entrainment_share_of_escaped.p95 | 0.5231 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.sin_theta | 0.342 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.boom_length_factor_1_over_sin_theta | 2.924 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_kg.median | 3.422e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_kg.p05 | 1.031e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_kg.p95 | 8.021e+05 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_theta90.median | -0.1924 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_theta90.p05 | -0.528 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_theta90.p95 | -0.0101 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_current_a_theta90.median | -0.2388 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_current_a_theta90.p05 | -0.5492 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_current_a_theta90.p95 | -0.0558 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_current_a_theta90.draws_a_lower | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.escaped_rel_vs_current_a_theta90.n_draws | 40 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.fwce.median | 0.6619 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.fwce.p05 | 0.4099 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.fwce.p95 | 0.8125 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.fwce_delta_pp_vs_theta90.median | 8.9 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.fwce_delta_pp_vs_theta90.p05 | 0.45 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.fwce_delta_pp_vs_theta90.p95 | 28.92 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.fwce_delta_pp_vs_current_a_theta90.median | 12.13 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.fwce_delta_pp_vs_current_a_theta90.p05 | 2.61 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.fwce_delta_pp_vs_current_a_theta90.p95 | 31.57 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.velocity_entrainment_share_of_escaped.median | 0.0449 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.velocity_entrainment_share_of_escaped.p05 | 0.0011 |
| boom_angle_sensitivity_P2.c_fuse_refloat_x0.5.theta20.velocity_entrainment_share_of_escaped.p95 | 0.3702 |
| ablations.paired_escaped_rel_diff.P2_vs_P1m.median | -0.0277 |
| ablations.paired_escaped_rel_diff.P2_vs_P1m.p05 | -0.1252 |
| ablations.paired_escaped_rel_diff.P2_vs_P1m.p95 | 0.0085 |
| ablations.paired_escaped_rel_diff.P2_vs_P1m.draws_a_lower | 34 |
| ablations.paired_escaped_rel_diff.P2_vs_P1m.n_draws | 40 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_notide.median | -0.0364 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_notide.p05 | -0.1507 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_notide.p95 | 0.0046 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_notide.draws_a_lower | 34 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_notide.n_draws | 40 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_nofc.median | -0.0066 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_nofc.p05 | -0.0199 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_nofc.p95 | 0.0099 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_nofc.draws_a_lower | 29 |
| ablations.paired_escaped_rel_diff.P2_vs_P2_nofc.n_draws | 40 |
| ablations.paired_escaped_rel_diff.P1m_vs_P1.median | -0.0206 |
| ablations.paired_escaped_rel_diff.P1m_vs_P1.p05 | -0.0404 |
| ablations.paired_escaped_rel_diff.P1m_vs_P1.p95 | 0.0017 |
| ablations.paired_escaped_rel_diff.P1m_vs_P1.draws_a_lower | 37 |
| ablations.paired_escaped_rel_diff.P1m_vs_P1.n_draws | 40 |
| ablations.paired_escaped_rel_diff.P1m_vs_P0.median | 0.0044 |
| ablations.paired_escaped_rel_diff.P1m_vs_P0.p05 | -0.0062 |
| ablations.paired_escaped_rel_diff.P1m_vs_P0.p95 | 0.0273 |
| ablations.paired_escaped_rel_diff.P1m_vs_P0.draws_a_lower | 12 |
| ablations.paired_escaped_rel_diff.P1m_vs_P0.n_draws | 40 |
| ablations.paired_escaped_rel_diff.P2_notide_vs_P1m.median | -0.0053 |
| ablations.paired_escaped_rel_diff.P2_notide_vs_P1m.p05 | -0.0138 |
| ablations.paired_escaped_rel_diff.P2_notide_vs_P1m.p95 | 0.0621 |
| ablations.paired_escaped_rel_diff.P2_notide_vs_P1m.draws_a_lower | 25 |
| ablations.paired_escaped_rel_diff.P2_notide_vs_P1m.n_draws | 40 |
| ablations.paired_escaped_rel_diff.P2_nofc_vs_P1m.median | -0.0224 |
| ablations.paired_escaped_rel_diff.P2_nofc_vs_P1m.p05 | -0.1259 |
| ablations.paired_escaped_rel_diff.P2_nofc_vs_P1m.p95 | 0.0039 |
| ablations.paired_escaped_rel_diff.P2_nofc_vs_P1m.draws_a_lower | 34 |
| ablations.paired_escaped_rel_diff.P2_nofc_vs_P1m.n_draws | 40 |
| ablations.paired_escaped_rel_diff.P2_vs_P1.median | -0.0522 |
| ablations.paired_escaped_rel_diff.P2_vs_P1.p05 | -0.1588 |
| ablations.paired_escaped_rel_diff.P2_vs_P1.p95 | -0.0076 |
| ablations.paired_escaped_rel_diff.P2_vs_P1.draws_a_lower | 39 |
| ablations.paired_escaped_rel_diff.P2_vs_P1.n_draws | 40 |
| ablations.escaped_kg.P0.median | 4.273e+05 |
| ablations.escaped_kg.P0.p05 | 1.44e+05 |
| ablations.escaped_kg.P0.p95 | 9.592e+05 |
| ablations.escaped_kg.P1.median | 4.488e+05 |
| ablations.escaped_kg.P1.p05 | 1.5e+05 |
| ablations.escaped_kg.P1.p95 | 9.795e+05 |
| ablations.escaped_kg.P1m.median | 4.265e+05 |
| ablations.escaped_kg.P1m.p05 | 1.45e+05 |
| ablations.escaped_kg.P1m.p95 | 9.675e+05 |
| ablations.escaped_kg.P2_notide.median | 4.468e+05 |
| ablations.escaped_kg.P2_notide.p05 | 1.581e+05 |
| ablations.escaped_kg.P2_notide.p95 | 9.62e+05 |
| ablations.escaped_kg.P2_nofc.median | 4.146e+05 |
| ablations.escaped_kg.P2_nofc.p05 | 1.475e+05 |
| ablations.escaped_kg.P2_nofc.p95 | 9.2e+05 |
| ablations.escaped_kg.P2.median | 4.11e+05 |
| ablations.escaped_kg.P2.p05 | 1.446e+05 |
| ablations.escaped_kg.P2.p95 | 9.143e+05 |
| ablations.fwce.P0.median | 0.4577 |
| ablations.fwce.P0.p05 | 0.3131 |
| ablations.fwce.P0.p95 | 0.6969 |
| ablations.fwce.P1.median | 0.4442 |
| ablations.fwce.P1.p05 | 0.2964 |
| ablations.fwce.P1.p95 | 0.6935 |
| ablations.fwce.P1m.median | 0.4565 |
| ablations.fwce.P1m.p05 | 0.3078 |
| ablations.fwce.P1m.p95 | 0.6989 |
| ablations.fwce.P2_notide.median | 0.4606 |
| ablations.fwce.P2_notide.p05 | 0.3105 |
| ablations.fwce.P2_notide.p95 | 0.697 |
| ablations.fwce.P2_nofc.median | 0.4864 |
| ablations.fwce.P2_nofc.p05 | 0.3041 |
| ablations.fwce.P2_nofc.p95 | 0.6997 |
| ablations.fwce.P2.median | 0.4897 |
| ablations.fwce.P2.p05 | 0.3059 |
| ablations.fwce.P2.p95 | 0.6986 |
| ablations.cleared_share_of_unique_input.P0.median | 0.4547 |
| ablations.cleared_share_of_unique_input.P0.p05 | 0.3015 |
| ablations.cleared_share_of_unique_input.P0.p95 | 0.6938 |
| ablations.cleared_share_of_unique_input.P1.median | 0.4399 |
| ablations.cleared_share_of_unique_input.P1.p05 | 0.295 |
| ablations.cleared_share_of_unique_input.P1.p95 | 0.6914 |
| ablations.cleared_share_of_unique_input.P1m.median | 0.4537 |
| ablations.cleared_share_of_unique_input.P1m.p05 | 0.2992 |
| ablations.cleared_share_of_unique_input.P1m.p95 | 0.6966 |
| ablations.cleared_share_of_unique_input.P2_notide.median | 0.4583 |
| ablations.cleared_share_of_unique_input.P2_notide.p05 | 0.3046 |
| ablations.cleared_share_of_unique_input.P2_notide.p95 | 0.6948 |
| ablations.cleared_share_of_unique_input.P2_nofc.median | 0.4842 |
| ablations.cleared_share_of_unique_input.P2_nofc.p05 | 0.303 |
| ablations.cleared_share_of_unique_input.P2_nofc.p95 | 0.6976 |
| ablations.cleared_share_of_unique_input.P2.median | 0.4867 |
| ablations.cleared_share_of_unique_input.P2.p05 | 0.3046 |
| ablations.cleared_share_of_unique_input.P2.p95 | 0.6961 |
| mass_boundary.P0.unique_input_kg.median | 9.644e+05 |
| mass_boundary.P0.unique_input_kg.p05 | 3.496e+05 |
| mass_boundary.P0.unique_input_kg.p95 | 1.388e+06 |
| mass_boundary.P0.cleared_kg.median | 4.389e+05 |
| mass_boundary.P0.cleared_kg.p05 | 1.504e+05 |
| mass_boundary.P0.cleared_kg.p95 | 7.741e+05 |
| mass_boundary.P0.stored_at_season_end_kg.median | 2922 |
| mass_boundary.P0.stored_at_season_end_kg.p05 | 755 |
| mass_boundary.P0.stored_at_season_end_kg.p95 | 3.326e+04 |
| mass_boundary.P0.held_upstream_at_season_end_kg.median | 1198 |
| mass_boundary.P0.held_upstream_at_season_end_kg.p05 | 332 |
| mass_boundary.P0.held_upstream_at_season_end_kg.p95 | 4314 |
| mass_boundary.P0.escaped_kg.median | 4.273e+05 |
| mass_boundary.P0.escaped_kg.p05 | 1.44e+05 |
| mass_boundary.P0.escaped_kg.p95 | 9.592e+05 |
| mass_boundary.P0.cleared_share.median | 0.4547 |
| mass_boundary.P0.cleared_share.p05 | 0.3015 |
| mass_boundary.P0.cleared_share.p95 | 0.6938 |
| mass_boundary.P0.retained_share.median | 0.0028 |
| mass_boundary.P0.retained_share.p05 | 0.0016 |
| mass_boundary.P0.retained_share.p95 | 0.0324 |
| mass_boundary.P0.escaped_share.median | 0.5411 |
| mass_boundary.P0.escaped_share.p05 | 0.3017 |
| mass_boundary.P0.escaped_share.p95 | 0.6848 |
| mass_boundary.P1.unique_input_kg.median | 9.644e+05 |
| mass_boundary.P1.unique_input_kg.p05 | 3.496e+05 |
| mass_boundary.P1.unique_input_kg.p95 | 1.388e+06 |
| mass_boundary.P1.cleared_kg.median | 4.283e+05 |
| mass_boundary.P1.cleared_kg.p05 | 1.418e+05 |
| mass_boundary.P1.cleared_kg.p95 | 7.627e+05 |
| mass_boundary.P1.stored_at_season_end_kg.median | 2941 |
| mass_boundary.P1.stored_at_season_end_kg.p05 | 509 |
| mass_boundary.P1.stored_at_season_end_kg.p95 | 3.386e+04 |
| mass_boundary.P1.held_upstream_at_season_end_kg.median | 1283 |
| mass_boundary.P1.held_upstream_at_season_end_kg.p05 | 361 |
| mass_boundary.P1.held_upstream_at_season_end_kg.p95 | 4189 |
| mass_boundary.P1.escaped_kg.median | 4.488e+05 |
| mass_boundary.P1.escaped_kg.p05 | 1.5e+05 |
| mass_boundary.P1.escaped_kg.p95 | 9.795e+05 |
| mass_boundary.P1.cleared_share.median | 0.4399 |
| mass_boundary.P1.cleared_share.p05 | 0.295 |
| mass_boundary.P1.cleared_share.p95 | 0.6914 |
| mass_boundary.P1.retained_share.median | 0.0029 |
| mass_boundary.P1.retained_share.p05 | 0.0014 |
| mass_boundary.P1.retained_share.p95 | 0.0313 |
| mass_boundary.P1.escaped_share.median | 0.5545 |
| mass_boundary.P1.escaped_share.p05 | 0.3051 |
| mass_boundary.P1.escaped_share.p95 | 0.7025 |
| mass_boundary.P2.unique_input_kg.median | 9.644e+05 |
| mass_boundary.P2.unique_input_kg.p05 | 3.496e+05 |
| mass_boundary.P2.unique_input_kg.p95 | 1.388e+06 |
| mass_boundary.P2.cleared_kg.median | 4.836e+05 |
| mass_boundary.P2.cleared_kg.p05 | 1.464e+05 |
| mass_boundary.P2.cleared_kg.p95 | 7.887e+05 |
| mass_boundary.P2.stored_at_season_end_kg.median | 2694 |
| mass_boundary.P2.stored_at_season_end_kg.p05 | 637 |
| mass_boundary.P2.stored_at_season_end_kg.p95 | 2.458e+04 |
| mass_boundary.P2.held_upstream_at_season_end_kg.median | 1213 |
| mass_boundary.P2.held_upstream_at_season_end_kg.p05 | 349 |
| mass_boundary.P2.held_upstream_at_season_end_kg.p95 | 3890 |
| mass_boundary.P2.escaped_kg.median | 4.11e+05 |
| mass_boundary.P2.escaped_kg.p05 | 1.446e+05 |
| mass_boundary.P2.escaped_kg.p95 | 9.143e+05 |
| mass_boundary.P2.cleared_share.median | 0.4867 |
| mass_boundary.P2.cleared_share.p05 | 0.3046 |
| mass_boundary.P2.cleared_share.p95 | 0.6961 |
| mass_boundary.P2.retained_share.median | 0.0026 |
| mass_boundary.P2.retained_share.p05 | 0.0013 |
| mass_boundary.P2.retained_share.p95 | 0.0253 |
| mass_boundary.P2.escaped_share.median | 0.5094 |
| mass_boundary.P2.escaped_share.p05 | 0.3 |
| mass_boundary.P2.escaped_share.p95 | 0.6929 |
| checks.mass_balance_max_abs_err_kg | 0 |
| checks.equal_crew_hours | True |
| checks.escaped_median_matches_metrics_json | True |
| checks.metrics_json_escaped_median.P0 | 4.273e+05 |
| checks.metrics_json_escaped_median.P1 | 4.488e+05 |
| checks.metrics_json_escaped_median.P2 | 4.11e+05 |
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
| exposure_P2_nominal.theta90.share_of_hours | 0.139 |
| exposure_P2_nominal.theta90.share_of_arrived_kg | 0.1415 |
| exposure_P2_nominal.theta90.by_site.mithi_mahim.share_of_hours | 0.1475 |
| exposure_P2_nominal.theta90.by_site.mithi_mahim.share_of_arrived_kg | 0.1455 |
| exposure_P2_nominal.theta90.by_site.oshiwara_malad.share_of_hours | 0.2008 |
| exposure_P2_nominal.theta90.by_site.oshiwara_malad.share_of_arrived_kg | 0.1487 |
| exposure_P2_nominal.theta90.by_site.dahisar_mouth.share_of_hours | 0.2008 |
| exposure_P2_nominal.theta90.by_site.dahisar_mouth.share_of_arrived_kg | 0.1692 |
| exposure_P2_nominal.theta90.by_site.trombay_mahul.share_of_hours | 0.0068 |
| exposure_P2_nominal.theta90.by_site.trombay_mahul.share_of_arrived_kg | 0.0059 |
| exposure_P2_nominal.theta45.share_of_hours | 0.0453 |
| exposure_P2_nominal.theta45.share_of_arrived_kg | 0.0414 |
| exposure_P2_nominal.theta30.share_of_hours | 0.0079 |
| exposure_P2_nominal.theta30.share_of_arrived_kg | 0.0044 |
| exposure_P2_nominal.theta20.share_of_hours | 0.0003 |
| exposure_P2_nominal.theta20.share_of_arrived_kg | 0.0002 |

## twin_sim — metrics.json

Source: [`components/twin_sim/results/metrics.json`](../components/twin_sim/results/metrics.json)  
Reproduce: `cd innovatex-t3-coastal-plastic/components && python -m twin_sim.run`

| Metric | Value |
|---|---|
| metric | escaped_kg summed over 4 sites and the held-out monsoons (Jun-Sep 2024+2025); relative reduction vs P0 per sampled parameter setting (Monte Carlo draw); median and central 90% scenario range across sampled parameter settings (p05-p95; not a confidence interval) |
| n_draws | 40 |
| seed | 20261004 |
| crew_budget | 2 crews x 8 h/day, all policies |
| heldout_2024_2025.P0.escaped_kg_median | 4.273e+05 |
| heldout_2024_2025.P0.escaped_kg_p05 | 1.44e+05 |
| heldout_2024_2025.P0.escaped_kg_p95 | 9.592e+05 |
| heldout_2024_2025.P0.reduction_vs_P0_median | 0 |
| heldout_2024_2025.P0.reduction_vs_P0_p05 | 0 |
| heldout_2024_2025.P0.reduction_vs_P0_p95 | 0 |
| heldout_2024_2025.P0.draws_better_than_P0 | 0 |
| heldout_2024_2025.P0.captured_fraction_median | 0.4589 |
| heldout_2024_2025.P0.cleared_kg_median | 4.389e+05 |
| heldout_2024_2025.P0.overflow_site_hours_median | 87 |
| heldout_2024_2025.P0.bypass_site_hours_median | 10 |
| heldout_2024_2025.P0.crew_hours | 3904 |
| heldout_2024_2025.P0.load_kg_median | 9.644e+05 |
| heldout_2024_2025.P1.escaped_kg_median | 4.488e+05 |
| heldout_2024_2025.P1.escaped_kg_p05 | 1.5e+05 |
| heldout_2024_2025.P1.escaped_kg_p95 | 9.795e+05 |
| heldout_2024_2025.P1.reduction_vs_P0_median | -0.03 |
| heldout_2024_2025.P1.reduction_vs_P0_p05 | -0.0574 |
| heldout_2024_2025.P1.reduction_vs_P0_p95 | 0.0007 |
| heldout_2024_2025.P1.draws_better_than_P0 | 3 |
| heldout_2024_2025.P1.captured_fraction_median | 0.4455 |
| heldout_2024_2025.P1.cleared_kg_median | 4.283e+05 |
| heldout_2024_2025.P1.overflow_site_hours_median | 70.5 |
| heldout_2024_2025.P1.bypass_site_hours_median | 10 |
| heldout_2024_2025.P1.crew_hours | 3904 |
| heldout_2024_2025.P1.load_kg_median | 9.644e+05 |
| heldout_2024_2025.P2.escaped_kg_median | 4.11e+05 |
| heldout_2024_2025.P2.escaped_kg_p05 | 1.446e+05 |
| heldout_2024_2025.P2.escaped_kg_p95 | 9.143e+05 |
| heldout_2024_2025.P2.reduction_vs_P0_median | 0.0195 |
| heldout_2024_2025.P2.reduction_vs_P0_p05 | -0.0132 |
| heldout_2024_2025.P2.reduction_vs_P0_p95 | 0.1254 |
| heldout_2024_2025.P2.draws_better_than_P0 | 28 |
| heldout_2024_2025.P2.captured_fraction_median | 0.4906 |
| heldout_2024_2025.P2.cleared_kg_median | 4.836e+05 |
| heldout_2024_2025.P2.overflow_site_hours_median | 88 |
| heldout_2024_2025.P2.bypass_site_hours_median | 10 |
| heldout_2024_2025.P2.crew_hours | 3904 |
| heldout_2024_2025.P2.load_kg_median | 9.644e+05 |
| tuning_2019_2023.P0.escaped_kg_median | 1.117e+06 |
| tuning_2019_2023.P0.escaped_kg_p05 | 3.731e+05 |
| tuning_2019_2023.P0.escaped_kg_p95 | 2.413e+06 |
| tuning_2019_2023.P0.reduction_vs_P0_median | 0 |
| tuning_2019_2023.P0.reduction_vs_P0_p05 | 0 |
| tuning_2019_2023.P0.reduction_vs_P0_p95 | 0 |
| tuning_2019_2023.P0.draws_better_than_P0 | 0 |
| tuning_2019_2023.P0.captured_fraction_median | 0.4414 |
| tuning_2019_2023.P0.cleared_kg_median | 1.104e+06 |
| tuning_2019_2023.P0.overflow_site_hours_median | 243.5 |
| tuning_2019_2023.P0.bypass_site_hours_median | 147 |
| tuning_2019_2023.P0.crew_hours | 9760 |
| tuning_2019_2023.P0.load_kg_median | 2.407e+06 |
| tuning_2019_2023.P1.escaped_kg_median | 1.152e+06 |
| tuning_2019_2023.P1.escaped_kg_p05 | 4.001e+05 |
| tuning_2019_2023.P1.escaped_kg_p95 | 2.473e+06 |
| tuning_2019_2023.P1.reduction_vs_P0_median | -0.0305 |
| tuning_2019_2023.P1.reduction_vs_P0_p05 | -0.0582 |
| tuning_2019_2023.P1.reduction_vs_P0_p95 | -0.005 |
| tuning_2019_2023.P1.draws_better_than_P0 | 2 |
| tuning_2019_2023.P1.captured_fraction_median | 0.4217 |
| tuning_2019_2023.P1.cleared_kg_median | 1.058e+06 |
| tuning_2019_2023.P1.overflow_site_hours_median | 229.5 |
| tuning_2019_2023.P1.bypass_site_hours_median | 147 |
| tuning_2019_2023.P1.crew_hours | 9760 |
| tuning_2019_2023.P1.load_kg_median | 2.407e+06 |
| tuning_2019_2023.P2.escaped_kg_median | 1.063e+06 |
| tuning_2019_2023.P2.escaped_kg_p05 | 3.8e+05 |
| tuning_2019_2023.P2.escaped_kg_p95 | 2.308e+06 |
| tuning_2019_2023.P2.reduction_vs_P0_median | 0.0143 |
| tuning_2019_2023.P2.reduction_vs_P0_p05 | -0.0087 |
| tuning_2019_2023.P2.reduction_vs_P0_p95 | 0.1028 |
| tuning_2019_2023.P2.draws_better_than_P0 | 31 |
| tuning_2019_2023.P2.captured_fraction_median | 0.4668 |
| tuning_2019_2023.P2.cleared_kg_median | 1.179e+06 |
| tuning_2019_2023.P2.overflow_site_hours_median | 284 |
| tuning_2019_2023.P2.bypass_site_hours_median | 147 |
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
| tide_fit.mithi_mahim.fit_period | ['2022-11-23 00:00:00+00:00', '2023-12-31 23:00:00+00:00'] |
| tide_fit.mithi_mahim.variance_explained | 0.9949 |
| tide_fit.mithi_mahim.rmse_m | 0.065 |
| tide_fit.mithi_mahim.flat_keys_are | in-sample fit residual (fit window); see out_of_sample_2024_2025 |
| tide_fit.mithi_mahim.in_sample.n_hours | 9696 |
| tide_fit.mithi_mahim.in_sample.rmse_m | 0.0651 |
| tide_fit.mithi_mahim.in_sample.variance_explained | 0.9949 |
| tide_fit.mithi_mahim.in_sample.bias_m | -0 |
| tide_fit.mithi_mahim.in_sample.label | in-sample fit residual vs Open-Meteo Marine MODEL sea level (fit window) |
| tide_fit.mithi_mahim.out_of_sample_2024_2025.n_hours | 14904 |
| tide_fit.mithi_mahim.out_of_sample_2024_2025.rmse_m | 0.0945 |
| tide_fit.mithi_mahim.out_of_sample_2024_2025.variance_explained | 0.9903 |
| tide_fit.mithi_mahim.out_of_sample_2024_2025.bias_m | 0.0305 |
| tide_fit.mithi_mahim.out_of_sample_2024_2025.period | ['2024-01-01 00:00:00+00:00', '2025-09-30 23:00:00+00:00'] |
| tide_fit.mithi_mahim.out_of_sample_2024_2025.label | out-of-sample vs Open-Meteo Marine MODEL sea level (not a tide gauge); fit never saw these hours |
| tide_fit.mithi_mahim.out_of_sample_jjas_2024_2025.n_hours | 5688 |
| tide_fit.mithi_mahim.out_of_sample_jjas_2024_2025.rmse_m | 0.1101 |
| tide_fit.mithi_mahim.out_of_sample_jjas_2024_2025.variance_explained | 0.9887 |
| tide_fit.mithi_mahim.out_of_sample_jjas_2024_2025.bias_m | 0.0547 |
| tide_fit.mithi_mahim.out_of_sample_jjas_2024_2025.label | out-of-sample vs Open-Meteo Marine MODEL sea level (not a tide gauge); fit never saw these hours; Jun-Sep only |
| tide_fit.oshiwara_malad.fit_period | ['2022-11-23 00:00:00+00:00', '2023-12-31 23:00:00+00:00'] |
| tide_fit.oshiwara_malad.variance_explained | 0.9954 |
| tide_fit.oshiwara_malad.rmse_m | 0.065 |
| tide_fit.oshiwara_malad.flat_keys_are | in-sample fit residual (fit window); see out_of_sample_2024_2025 |
| tide_fit.oshiwara_malad.in_sample.n_hours | 9696 |
| tide_fit.oshiwara_malad.in_sample.rmse_m | 0.065 |
| tide_fit.oshiwara_malad.in_sample.variance_explained | 0.9954 |
| tide_fit.oshiwara_malad.in_sample.bias_m | -0 |
| tide_fit.oshiwara_malad.in_sample.label | in-sample fit residual vs Open-Meteo Marine MODEL sea level (fit window) |
| tide_fit.oshiwara_malad.out_of_sample_2024_2025.n_hours | 14904 |
| tide_fit.oshiwara_malad.out_of_sample_2024_2025.rmse_m | 0.0934 |
| tide_fit.oshiwara_malad.out_of_sample_2024_2025.variance_explained | 0.9913 |
| tide_fit.oshiwara_malad.out_of_sample_2024_2025.bias_m | 0.0302 |
| tide_fit.oshiwara_malad.out_of_sample_2024_2025.period | ['2024-01-01 00:00:00+00:00', '2025-09-30 23:00:00+00:00'] |
| tide_fit.oshiwara_malad.out_of_sample_2024_2025.label | out-of-sample vs Open-Meteo Marine MODEL sea level (not a tide gauge); fit never saw these hours |
| tide_fit.oshiwara_malad.out_of_sample_jjas_2024_2025.n_hours | 5688 |
| tide_fit.oshiwara_malad.out_of_sample_jjas_2024_2025.rmse_m | 0.1079 |
| tide_fit.oshiwara_malad.out_of_sample_jjas_2024_2025.variance_explained | 0.9901 |
| tide_fit.oshiwara_malad.out_of_sample_jjas_2024_2025.bias_m | 0.0543 |
| tide_fit.oshiwara_malad.out_of_sample_jjas_2024_2025.label | out-of-sample vs Open-Meteo Marine MODEL sea level (not a tide gauge); fit never saw these hours; Jun-Sep only |
| tide_fit.dahisar_mouth.fit_period | ['2022-11-23 00:00:00+00:00', '2023-12-31 23:00:00+00:00'] |
| tide_fit.dahisar_mouth.variance_explained | 0.9954 |
| tide_fit.dahisar_mouth.rmse_m | 0.067 |
| tide_fit.dahisar_mouth.flat_keys_are | in-sample fit residual (fit window); see out_of_sample_2024_2025 |
| tide_fit.dahisar_mouth.in_sample.n_hours | 9696 |
| tide_fit.dahisar_mouth.in_sample.rmse_m | 0.0665 |
| tide_fit.dahisar_mouth.in_sample.variance_explained | 0.9954 |
| tide_fit.dahisar_mouth.in_sample.bias_m | -0 |
| tide_fit.dahisar_mouth.in_sample.label | in-sample fit residual vs Open-Meteo Marine MODEL sea level (fit window) |
| tide_fit.dahisar_mouth.out_of_sample_2024_2025.n_hours | 14904 |
| tide_fit.dahisar_mouth.out_of_sample_2024_2025.rmse_m | 0.0953 |
| tide_fit.dahisar_mouth.out_of_sample_2024_2025.variance_explained | 0.9914 |
| tide_fit.dahisar_mouth.out_of_sample_2024_2025.bias_m | 0.0305 |
| tide_fit.dahisar_mouth.out_of_sample_2024_2025.period | ['2024-01-01 00:00:00+00:00', '2025-09-30 23:00:00+00:00'] |
| tide_fit.dahisar_mouth.out_of_sample_2024_2025.label | out-of-sample vs Open-Meteo Marine MODEL sea level (not a tide gauge); fit never saw these hours |
| tide_fit.dahisar_mouth.out_of_sample_jjas_2024_2025.n_hours | 5688 |
| tide_fit.dahisar_mouth.out_of_sample_jjas_2024_2025.rmse_m | 0.111 |
| tide_fit.dahisar_mouth.out_of_sample_jjas_2024_2025.variance_explained | 0.99 |
| tide_fit.dahisar_mouth.out_of_sample_jjas_2024_2025.bias_m | 0.055 |
| tide_fit.dahisar_mouth.out_of_sample_jjas_2024_2025.label | out-of-sample vs Open-Meteo Marine MODEL sea level (not a tide gauge); fit never saw these hours; Jun-Sep only |
| tide_fit.trombay_mahul.fit_period | ['2022-11-23 00:00:00+00:00', '2023-12-31 23:00:00+00:00'] |
| tide_fit.trombay_mahul.variance_explained | 0.9949 |
| tide_fit.trombay_mahul.rmse_m | 0.065 |
| tide_fit.trombay_mahul.flat_keys_are | in-sample fit residual (fit window); see out_of_sample_2024_2025 |
| tide_fit.trombay_mahul.in_sample.n_hours | 9696 |
| tide_fit.trombay_mahul.in_sample.rmse_m | 0.0651 |
| tide_fit.trombay_mahul.in_sample.variance_explained | 0.9949 |
| tide_fit.trombay_mahul.in_sample.bias_m | -0 |
| tide_fit.trombay_mahul.in_sample.label | in-sample fit residual vs Open-Meteo Marine MODEL sea level (fit window) |
| tide_fit.trombay_mahul.out_of_sample_2024_2025.n_hours | 14904 |
| tide_fit.trombay_mahul.out_of_sample_2024_2025.rmse_m | 0.0945 |
| tide_fit.trombay_mahul.out_of_sample_2024_2025.variance_explained | 0.9903 |
| tide_fit.trombay_mahul.out_of_sample_2024_2025.bias_m | 0.0305 |
| tide_fit.trombay_mahul.out_of_sample_2024_2025.period | ['2024-01-01 00:00:00+00:00', '2025-09-30 23:00:00+00:00'] |
| tide_fit.trombay_mahul.out_of_sample_2024_2025.label | out-of-sample vs Open-Meteo Marine MODEL sea level (not a tide gauge); fit never saw these hours |
| tide_fit.trombay_mahul.out_of_sample_jjas_2024_2025.n_hours | 5688 |
| tide_fit.trombay_mahul.out_of_sample_jjas_2024_2025.rmse_m | 0.1101 |
| tide_fit.trombay_mahul.out_of_sample_jjas_2024_2025.variance_explained | 0.9887 |
| tide_fit.trombay_mahul.out_of_sample_jjas_2024_2025.bias_m | 0.0547 |
| tide_fit.trombay_mahul.out_of_sample_jjas_2024_2025.label | out-of-sample vs Open-Meteo Marine MODEL sea level (not a tide gauge); fit never saw these hours; Jun-Sep only |
| tide_fit_note | UTide fit on Open-Meteo Marine model sea level 2022-11-23..2023-12-31 only (no held-out-year data); P2 knobs were tuned on 2019-2023 with the superseded fit (2022-11..2025-09) and are kept unchanged |
| git_sha_at_run | ffe7d44 |

## eval — impact_estimate.json

Source: [`eval/impact_estimate.json`](../eval/impact_estimate.json)  
Reproduce: `python3 innovatex-t3-coastal-plastic/eval/impact_estimate.py`

| Metric | Value |
|---|---|
| label | ILLUSTRATIVE ESTIMATE (REPORTED catch x SIMULATED/SENSITIVITY ratios); not a result |
| inputs.catch_t_per_day_monsoon | [2.5, 3.0] |
| inputs.catch_source | research/fact-check.md F12 |
| inputs.retained_share_f_P0_fwce | 0.4577 |
| inputs.monsoon_days | 122 |
| inputs.dispatch_rel_P2_vs_P0.median | -0.0195 |
| inputs.dispatch_rel_P2_vs_P0.p05 | -0.1254 |
| inputs.dispatch_rel_P2_vs_P0.p95 | 0.0132 |
| inputs.retrofit_rel_20deg_fuse_pocket.median | -0.2388 |
| inputs.retrofit_rel_20deg_fuse_pocket.p05 | -0.5492 |
| inputs.retrofit_rel_20deg_fuse_pocket.p95 | -0.0558 |
| escaping_t_per_day | [2.96, 3.55] |
| dispatch_avoided_t_per_monsoon.median | [7.0, 8.5] |
| dispatch_avoided_t_per_monsoon.p05 | [45.3, 54.4] |
| dispatch_avoided_t_per_monsoon.p95 | [-4.8, -5.7] |
| retrofit_avoided_t_per_monsoon.median | [86.3, 103.6] |
| retrofit_avoided_t_per_monsoon.p05 | [198.5, 238.2] |
| retrofit_avoided_t_per_monsoon.p95 | [20.2, 24.2] |
| note | per boom; ranges run over the catch range (2.5 to 3 t/day); negative = more escapes. Debris is mixed garbage, not only plastic. |

