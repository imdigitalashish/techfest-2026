#!/usr/bin/env bash
# Post-training pipeline. Usage (from components/detection/):  bash run_after_train.sh <A|B> <weights.pt>
#   A: metrics.json (test + val + Groningen, MPS latency) -> sample detections -> SYNTHETIC flux count
#   B: autoresearch ratchet on val (frozen eval.py) -> kept config evaluated ONCE on test
set -uo pipefail
cd "$(dirname "$0")"
PY=/opt/homebrew/bin/python3.11
W="$2"
REPRO="cd innovatex-t3-coastal-plastic && bash components/detection/data/fetch_data.sh && cd components/detection && $PY -m t3det.prepare && $PY -m t3det.train --model yolo11n.pt --imgsz 640 --epochs 40 --time 0.28 --batch 8 --name baseline_yolo11n_640 --hyp warmup_epochs=0.3 mosaic=0 val=False && $PY -m t3det.evaluate --weights ../../.data/detection/runs/baseline_yolo11n_640/weights/best.pt"
if [ "$1" = A ]; then
  EXTRA=$($PY - "$W" <<'EOF'
import json, sys, pathlib
run = pathlib.Path(sys.argv[1]).parents[1]
meta = json.loads((run / "train_meta.json").read_text()) if (run / "train_meta.json").exists() else {}
csv = (run / "results.csv").read_text().strip().splitlines() if (run / "results.csv").exists() else []
print(json.dumps({"training": {"wall_s": meta.get("wall_s"), "epochs_completed": max(len(csv) - 1, 0),
  "recipe": "yolo11n.pt (COCO-pretrained) fine-tuned, imgsz 640, batch 8, seed 42, warmup 0.3 ep, mosaic 0, "
            "no per-epoch val (last epoch = model), wall-clock cap 0.28 h (ASSUMPTION A1: shared machine was swapping)"}}))
EOF
)
  $PY -m t3det.evaluate --weights "$W" --also groningen --reproduce "$REPRO" --extra "$EXTRA" && \
  $PY -m t3det.samples --weights "$W" --n 5 && \
  $PY -m t3det.run_flux --weights "$W"
else
  $PY autoresearch/ratchet.py --weights "$W" --candidates autoresearch/candidates.json
  $PY autoresearch/eval.py --weights "$W" --config autoresearch/config.json --split test > results/autoresearch_test.txt 2>&1
  tail -2 results/autoresearch_test.txt
fi
