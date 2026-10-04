#!/usr/bin/env bash
# Post-training pipeline. Usage (from components/detection/):  bash run_after_train.sh A|B <weights.pt>
#   env: T3DET_DEVICE (mps|cpu, default mps) · IMGSZ (default 640) · TRAIN_CMD (training command, for `reproduce`)
#        RUN_JSON (guard record from baseline_when_calm.sh: device, wall-clock, pauses)
#   A: results/metrics.json (held-out test ONCE + val + Groningen cross-site; latency; training record)
#      -> results/sample_detections.json + samples/*.jpg -> SYNTHETIC flux suite (10 clips -> flux_synthetic.json)
#      -> frozen-matcher test score next to the zero-shot one (results/metrics_zeroshot.json)
#   B: autoresearch ratchet on val (frozen eval.py), then the kept config once on test
set -uo pipefail
cd "$(dirname "$0")"
PY=/opt/homebrew/bin/python3.11
W="$2"; IMGSZ="${IMGSZ:-640}"; export T3DET_DEVICE="${T3DET_DEVICE:-mps}"
D=../../.data/detection
if [ "$1" = A ]; then
  EXTRA=$($PY -m t3det.train_summary "$W" "${RUN_JSON:-}") || EXTRA='{}'
  REPRO="cd innovatex-t3-coastal-plastic && bash components/detection/data/fetch_data.sh && cd components/detection && $PY -m t3det.prepare && curl -sSL -o ../../.data/detection/weights/yolo11n.pt https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt && T3DET_DEVICE=$T3DET_DEVICE nice -n 10 ${TRAIN_CMD:-<training command: see README>} && IMGSZ=$IMGSZ T3DET_DEVICE=$T3DET_DEVICE bash run_after_train.sh A $W"
  $PY -m t3det.evaluate --weights "$W" --imgsz "$IMGSZ" --also val groningen --reproduce "$REPRO" --extra "$EXTRA" || exit 1
  $PY -m t3det.samples --weights "$W" --imgsz "$IMGSZ" --n 5
  $PY -m t3det.run_flux --weights "$W" --imgsz "$IMGSZ" --legacy-diagnostic     # SYNTHETIC suite -> flux_synthetic.json
  $PY -m t3det.frozen_compare "$W" "$IMGSZ"
  $PY -m pytest -q tests -p no:cacheprovider 2>&1 | tail -1
else
  $PY autoresearch/ratchet.py --weights "$W" --candidates autoresearch/candidates.json
  $PY autoresearch/eval.py --weights "$W" --config autoresearch/config.json --split test > results/autoresearch_test.txt 2>&1
  tail -2 results/autoresearch_test.txt
fi
