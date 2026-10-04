#!/usr/bin/env bash
# Sequential v2 evaluation queue (one heavy job at a time, niced). Run from the project folder:
#   bash eval/run_v2_queue.sh
# Waits for the pre-registered mvp-v2 grid to finish, then runs the remaining confirmatory/stretch experiments.
set -u
PY=".venv/bin/python"
NICE="nice -n 10"
W=8
until grep -q "episodes in" eval/results/mvp-v2.log 2>/dev/null; do sleep 20; done
$PY -m eval.confirm eval/results/mvp-v2 > /dev/null

# (L,P) phase diagram with the abandonment-aware planner + same-solver ablations (fresh seeds 200-219)
$NICE $PY -m eval.phase --hops 1 2 4 8 --patience 3 10 --seeds 200-219 --horizon 720 --workers $W \
  --policies greedy reactive mpc-myopic mpc-queue mpc-ewma mpc-cusum-v1 oracle --out eval/results/phase-v2 > eval/results/phase-v2.log 2>&1

# Real-trace replay: NYC TLC July 3-4 2025 (Manhattan, thinned; 20 thinning replicates)
$NICE $PY -m eval.harness --scenarios nyc-jul03-04 --policies static greedy reactive mpc-queue mpc-ewma mpc-cusum-v1 oracle \
  --seeds 200-219 --workers $W --out eval/results/nyc-v2 > eval/results/nyc-v2.log 2>&1

# Long horizons: one week (7 shocks + drift + spikes), 10 seeds; one month (30 shocks), 5 seeds
$NICE $PY -m eval.harness --scenarios long-week --policies static greedy reactive mpc-queue mpc-ewma mpc-cusum-v1 oracle \
  --seeds 200-209 --workers $W --out eval/results/long-week-v2 > eval/results/long-week-v2.log 2>&1
$PY -m eval.long eval/results/long-week-v2 > /dev/null
# Pareto: service vs movement (same seeds as mvp-v2, shock scenario)
$NICE $PY -m eval.harness --scenarios shock --policies "mpc-ewma@c_move=0.2" "mpc-ewma@c_move=0.5" "mpc-ewma@c_move=1.0" \
  "mpc-queue@c_move=0.5" --seeds 200-229 --horizon 1440 --workers $W --out eval/results/pareto-v2 > eval/results/pareto-v2.log 2>&1

$NICE $PY -m eval.harness --scenarios long-month --policies greedy reactive mpc-ewma mpc-cusum-v1 \
  --seeds 200-203 --workers $W --out eval/results/long-month-v2 > eval/results/long-month-v2.log 2>&1
$PY -m eval.long eval/results/long-month-v2 > /dev/null
echo "QUEUE DONE $(date)" > eval/results/v2-queue.done
