#!/usr/bin/env bash
# YOLO11n baseline under the shared-machine rules (lead, 2026-10-04 16:00 IST):
#   one heavy job at a time via the lock dir /tmp/t3-heavy.lock; everything under nice -n 10;
#   start only when kern.memorystatus_level >= 30; SIGSTOP the trainer (and its dataloader workers) below 25,
#   SIGCONT at >= 30; training <= 60 min wall-clock; dataloader workers <= 2.
# Usage (from components/detection/):  bash baseline_when_calm.sh gpu|cpu
#   gpu: MPS, imgsz 640, ultralytics wall-clock budget 0.9 h, hard cap 60 min (includes setup and pauses)
#   cpu: CPU, imgsz 480, budget 0.6 h, hard cap 40 min (fallback when the GPU is busy; labelled CPU in metrics.json)
# Then run_after_train.sh A (metrics.json, samples, SYNTHETIC flux), still holding the lock. No ratchet.
set -uo pipefail
cd "$(dirname "$0")"
MODE="${1:-gpu}"
PY=/opt/homebrew/bin/python3.11
D=../../.data/detection
LOCK=/tmp/t3-heavy.lock
if [ "$MODE" = cpu ]; then DEV=cpu; IMGSZ=480; TIME_H=0.6; CAP_S=2400; NAME=baseline_yolo11n_480_cpu
else DEV=mps; IMGSZ=640; TIME_H=0.9; CAP_S=3600; NAME=baseline_yolo11n_640; fi
G=$D/logs/$NAME.guard; LOG=$D/logs/$NAME.log; RUNJ=$D/logs/$NAME.run.json
mkdir -p $D/logs
ts() { TZ=Asia/Kolkata date +%Y-%m-%dT%H:%M:%S+05:30; }
mem() { sysctl -n kern.memorystatus_level; }
note() { echo "$(ts) $*" >> "$G"; }
sig() { kill -"$1" "$TP" 2>/dev/null; for c in $(pgrep -P "$TP"); do kill -"$1" "$c" 2>/dev/null; done; }
TP=""
cleanup() {
  if [ -n "$TP" ] && kill -0 "$TP" 2>/dev/null; then sig CONT; kill "$TP"; note "cleanup: trainer $TP terminated"; fi
  rmdir "$LOCK" 2>/dev/null && note "lock released"
}
note "mode=$MODE waiting for $LOCK"
until mkdir "$LOCK" 2>/dev/null; do sleep 60; done
trap cleanup EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
note "lock acquired; waiting for memorystatus_level>=30 (now $(mem))"
until [ "$(mem)" -ge 30 ]; do sleep 30; done
rm -rf "$D/runs/$NAME"
TRAIN="$PY -m t3det.train --model yolo11n.pt --device $DEV --imgsz $IMGSZ --epochs 100 --time $TIME_H --batch 8 --workers 2 --cache disk --name $NAME"
START=$(date +%s); START_IST=$(ts)
note "start (mem $(mem)): nice -n 10 $TRAIN"
T3DET_DEVICE=$DEV nice -n 10 $TRAIN > "$LOG" 2>&1 &
TP=$!
paused=0; paused_s=0; capped=0
while kill -0 "$TP" 2>/dev/null; do
  sleep 30
  m=$(mem); el=$(( $(date +%s) - START ))
  if [ $el -ge $CAP_S ]; then note "hard cap ${CAP_S}s reached: stopping trainer"; capped=1; sig CONT; kill "$TP"; break; fi
  if [ $paused = 0 ] && [ "$m" -lt 25 ]; then sig STOP; paused=1; note "paused (mem $m)"
  elif [ $paused = 1 ]; then
    paused_s=$((paused_s + 30))
    if [ "$m" -ge 30 ]; then sig CONT; paused=0; note "resumed (mem $m)"; fi
  fi
done
wait "$TP"; RC=$?; TP=""
END=$(date +%s)
note "trainer exited rc=$RC wall=$((END - START))s paused~${paused_s}s capped=$capped"
printf '{"mode":"%s","device":"%s","imgsz":%s,"time_budget_h":%s,"hard_cap_s":%s,"start_ist":"%s","end_ist":"%s","wall_clock_s":%s,"paused_s_approx":%s,"hard_capped":%s,"exit_code":%s,"command":"nice -n 10 %s"}\n' \
  "$MODE" "$DEV" "$IMGSZ" "$TIME_H" "$CAP_S" "$START_IST" "$(ts)" "$((END - START))" "$paused_s" "$capped" "$RC" "$TRAIN" > "$RUNJ"
W=$D/runs/$NAME/weights/best.pt
[ -f "$W" ] || { note "no best.pt: nothing to evaluate"; exit 1; }
note "evaluation start (run_after_train.sh A)"
IMGSZ=$IMGSZ T3DET_DEVICE=$DEV TRAIN_CMD="$TRAIN" RUN_JSON=$RUNJ nice -n 10 bash run_after_train.sh A "$W" > $D/logs/$NAME.eval.log 2>&1
note "evaluation exited rc=$?"
