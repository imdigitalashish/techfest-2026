#!/bin/bash
# Run one heavy job under this Mac's shared-machine rules (Supervisor, 4 Oct):
#   start only when kern.memorystatus_level >= 30; pause (SIGSTOP) below 25; resume (SIGCONT) at >= 30;
#   always under nice -n 10. Guard events go to stderr with IST timestamps.
# Usage: eval/run_guarded.sh .venv/bin/python -m eval.falsification walkforward --days ...
set -u
lvl() { sysctl -n kern.memorystatus_level; }
ts() { TZ=Asia/Kolkata date '+%H:%M:%S'; }
while [ "$(lvl)" -lt 30 ]; do sleep 30; done
echo "$(ts) guard: start at level $(lvl)" >&2
nice -n 10 "$@" &
pid=$!
paused=0
while kill -0 "$pid" 2>/dev/null; do
  l=$(lvl)
  if [ "$paused" -eq 0 ] && [ "$l" -lt 25 ]; then kill -STOP "$pid"; paused=1; echo "$(ts) guard: paused at level $l" >&2; fi
  if [ "$paused" -eq 1 ] && [ "$l" -ge 30 ]; then kill -CONT "$pid"; paused=0; echo "$(ts) guard: resumed at level $l" >&2; fi
  sleep 15
done
wait "$pid"
rc=$?
echo "$(ts) guard: exit $rc" >&2
exit "$rc"
