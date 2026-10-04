#!/usr/bin/env bash
# Planner-sensitivity (exploratory, added 10:42 IST after phase-v2 reversed phase-v1): the legacy never-abandoning LP
# backlog on the same fresh seeds as phase-v2 (highspy backend), so both planner variants are compared paired by seed.
set -u
PY=".venv/bin/python"; NICE="nice -n 10"; W=8
until [ -f eval/results/v2-followup.done ]; do sleep 20; done
$NICE $PY -m eval.phase --hops 1 2 4 8 --patience 3 10 --seeds 200-219 --horizon 720 --workers $W \
  --policies "mpc-ewma@abandon_aware=0" "oracle@abandon_aware=0" "mpc-cusum-v1@abandon_aware=0" \
  --out eval/results/phase-v2c > eval/results/phase-v2c.log 2>&1 || true
echo "SENS DONE $(date)" > eval/results/v2-sensitivity.done
