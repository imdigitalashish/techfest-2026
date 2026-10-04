# C5 autoresearch program (ratchet)

**Goal.** Raise C5 floating-litter detection quality on the TUD-GV **val** split without touching the test split.
**Metric (frozen).** `autoresearch/eval.py` prints one scalar: val mAP50 (IoU 0.5, COCO-style 101-point AP, class `litter`),
computed by our own frozen matcher (not ultralytics), with a bootstrap SE over val images on stderr.
**Keep rule.** Keep a change only if `delta > max(0.01, boot_se)` over the incumbent (ASSUMPTION: 0.01 absolute mAP50
noise floor; boot_se is the image-resampling SE of the candidate). Otherwise revert. Every run is logged in `results.tsv`.
**What may change.** `autoresearch/config.json` (C5 inference pipeline in `t3det/infer.py`: test-time resolution,
SAHI-style tiling, TTA, NMS) and, compute permitting, the training recipe (`t3det/train.py` hyper-parameters).
`eval.py`, the splits and the contracts never change. Contract tests (`tests/`) must pass.
**Final check.** The final kept configuration is evaluated ONCE on the held-out test split; both numbers are reported
in `results/metrics.json` under `autoresearch`.

## Budget
Each experiment = one full pass of eval.py over the 278 val images (inference-only ideas), or a fixed 0.15 h training
budget (training ideas). The shared M5 was swapping during this run (A1 in README), so training ideas are queued.

## Idea backlog (ordered by expected gain for small floating objects)
1. Test-time resolution 960 / 1280: TUD-GV boxes are small (median box = 0.22% of the frame), so more pixels per item.
2. SAHI-style tiling (2x2 tiles at 640 + full frame, NMS merge): slicing-aided inference for small objects
   (Akyon et al. 2022, SAHI).
3. Ultralytics TTA (`augment=True`: flips + scales).
4. NMS IoU 0.5 vs 0.7 (dense accumulations near booms).
5. Training (queued, compute-bound): imgsz 960 training; YOLO11s; mosaic + copy-paste; longer schedule.
6. Domain ideas for Mumbai (not testable on TUD-GV): black-water/low-contrast photometric augmentation, glare and rain
   synthetic augmentation, a "mat" class for dense accumulation, and flexible film vs bottle sub-classes.
