#!/usr/bin/env bash
# Restart command for the GPU queue (Supervisor rules, 4 Oct 11:10 IST): one training run at a time under
# `nice -n 10`, paused while kern.memorystatus_level < 25 % and resumed above 30 %.
# Work list: eval/queue.txt (edit any time; finished runs are skipped, so restarting is safe).
# `scripts/handover_to_queue.sh <pid>` first waits for <pid> to exit; `scripts/handover_to_queue.sh 0` starts now.
set -uo pipefail
cd "$(dirname "$0")/.."
PID=${1:-0}
if [ "$PID" != "0" ]; then
  echo "$(date '+%H:%M') waiting for PID $PID to exit"
  while kill -0 "$PID" 2>/dev/null; do sleep 30; done
fi
exec nice -n 10 .venv/bin/python -m eval.queue_runner
