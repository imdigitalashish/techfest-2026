#!/usr/bin/env bash
# Hand-over to the single sequential GPU queue (Supervisor memory rule, 4 Oct 09:08 IST: one heavy job at a
# time, under nice -n 10). Waits for the one surviving overnight run (dropout anchor_full seed 1, PID given
# as $1, default 19612) to exit, then runs scripts/gpu_queue.sh. The queue skips runs already in the jsonl,
# so this is safe to restart: `scripts/handover_to_queue.sh 0` starts the queue immediately.
set -uo pipefail
cd "$(dirname "$0")/.."
PID=${1:-19612}
if [ "$PID" != "0" ]; then
  echo "$(date '+%H:%M') waiting for PID $PID to exit"
  while kill -0 "$PID" 2>/dev/null; do sleep 30; done
  echo "$(date '+%H:%M') PID $PID exited"
fi
exec scripts/gpu_queue.sh
