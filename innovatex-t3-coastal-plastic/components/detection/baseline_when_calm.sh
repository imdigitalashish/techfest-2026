#!/usr/bin/env bash
# Lead follow-up (2026-10-04): train the YOLO11n baseline only while the shared machine is calm, then evaluate once.
#   start when the 1-min load average < 20; pause the trainer (SIGSTOP) when load > 40 on two consecutive 30-s checks,
#   continue (SIGCONT) when < 20. Wall-clock cap 0.9 h (ultralytics `time`, includes pauses), so <= 60 min in total.
# Usage (from components/detection/): bash baseline_when_calm.sh
set -uo pipefail
cd "$(dirname "$0")"
PY=/opt/homebrew/bin/python3.11
D=../../.data/detection
LOG=$D/logs/baseline_calm.log
G=$D/logs/baseline_calm.guard
W=$D/runs/baseline_yolo11n_640/weights/best.pt
load1() { sysctl -n vm.loadavg | awk '{print $2}'; }
lt() { awk -v a="$1" -v b="$2" 'BEGIN{exit !(a<b)}'; }
note() { echo "$(date +%T) $*" >> "$G"; }

note "waiting for load<20 (now $(load1))"
until lt "$(load1)" 20; do sleep 60; done
note "start training (load $(load1))"
rm -rf $D/runs/baseline_yolo11n_640
$PY -m t3det.train --model yolo11n.pt --imgsz 640 --epochs 100 --time 0.9 --batch 8 --name baseline_yolo11n_640 > "$LOG" 2>&1 &
TP=$!
hi=0; paused=0
while kill -0 $TP 2>/dev/null; do
  sleep 30
  l=$(load1)
  if [ $paused = 0 ]; then
    if lt 40 "$l"; then hi=$((hi + 1)); else hi=0; fi
    if [ $hi -ge 2 ]; then kill -STOP $TP; paused=1; note "paused (load $l)"; fi
  elif lt "$l" 20; then
    kill -CONT $TP; paused=0; hi=0; note "resumed (load $l)"
  fi
done
wait $TP; rc=$?
note "training exited rc=$rc"
[ -f "$W" ] || { note "no best.pt"; exit 1; }

# keep the overnight zero-shot artefacts next to the trained-baseline ones
cp -n results/metrics.json results/metrics_zeroshot.json 2>/dev/null
cp -n results/sample_detections.json results/sample_detections_zeroshot.json 2>/dev/null
cp -n results/flux_synthetic.json results/flux_synthetic_zeroshot.json 2>/dev/null

REPRO="cd innovatex-t3-coastal-plastic && bash components/detection/data/fetch_data.sh && cd components/detection && $PY -m t3det.prepare && $PY -m t3det.train --model yolo11n.pt --imgsz 640 --epochs 100 --time 0.9 --batch 8 --name baseline_yolo11n_640 && $PY -m t3det.evaluate --weights ../../.data/detection/runs/baseline_yolo11n_640/weights/best.pt --also val groningen"
EXTRA=$($PY - "$W" "$G" <<'EOF'
import json, sys, pathlib
run = pathlib.Path(sys.argv[1]).parents[1]
meta = json.loads((run / "train_meta.json").read_text()) if (run / "train_meta.json").exists() else {}
rows = (run / "results.csv").read_text().strip().splitlines() if (run / "results.csv").exists() else []
print(json.dumps({"training": {
  "wall_s": meta.get("wall_s"), "epochs_completed": max(len(rows) - 1, 0),
  "recipe": "yolo11n.pt (COCO-pretrained) fine-tuned on the TUD-GV grouped train split; ultralytics 8.4.12 defaults "
            "(mosaic 1.0, warmup 3 ep, close_mosaic 10, optimizer auto) except batch 8 and a 0.9 h wall-clock cap "
            "(`time`, epochs re-planned by ultralytics); seed 42, deterministic; best.pt selected on val; MPS with the "
            "CPU label-assigner patch (README A3)",
  "load_guard_log": pathlib.Path(sys.argv[2]).read_text().strip().splitlines()}}))
EOF
)
$PY -m t3det.evaluate --weights "$W" --also val groningen --reproduce "$REPRO" --extra "$EXTRA" > $D/logs/eval_calm.log 2>&1
$PY autoresearch/eval.py --weights "$W" --split test 2> $D/logs/frozen_test.json > $D/logs/frozen_test.txt
$PY - <<'EOF'
import json, pathlib
m = pathlib.Path("results/metrics.json"); d = json.loads(m.read_text())
fz = json.loads([l for l in pathlib.Path("../../.data/detection/logs/frozen_test.json").read_text().splitlines() if l.startswith("{")][-1])
d["frozen_eval_test"] = {k: fz[k] for k in ("mAP50", "boot_se", "precision@0.25", "recall@0.25", "ms_per_img_median")}
d["frozen_eval_test"]["note"] = "same matcher/AP as the zero-shot metrics_zeroshot.json (autoresearch/eval.py): apples-to-apples"
m.write_text(json.dumps(d, indent=1) + "\n")
EOF
$PY -m t3det.samples --weights "$W" --n 5 >> $D/logs/eval_calm.log 2>&1
$PY -m t3det.run_flux --weights "$W" --seq $D/synth/seq02 >> $D/logs/eval_calm.log 2>&1
$PY -m pytest -q tests -p no:cacheprovider 2>&1 | tail -1
note "done"
tail -4 $D/logs/eval_calm.log
