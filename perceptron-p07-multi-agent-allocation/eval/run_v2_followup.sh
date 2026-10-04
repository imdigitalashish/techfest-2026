#!/usr/bin/env bash
# Follow-up (exploratory, pre-announced in eval/preregistration.md Addendum A) — runs after eval/run_v2_queue.sh.
set -u
PY=".venv/bin/python"; NICE="nice -n 10"; W=8
until [ -f eval/results/v2-queue.done ]; do sleep 20; done
$NICE $PY -m eval.phase --hops 1 2 4 8 --patience 3 10 --seeds 200-219 --horizon 720 --workers $W \
  --policies "mpc-ewma@alpha=0.01" "mpc-ewma@horizon=14" "mpc-cusum-v1@horizon=14" --out eval/results/phase-v2b \
  > eval/results/phase-v2b.log 2>&1 || true
mkdir -p eval/results/phase-v2-merged
$PY - <<'PYEOF'
import pandas as pd
a = pd.read_csv("eval/results/phase-v2/episodes.csv"); b = pd.read_csv("eval/results/phase-v2b/episodes.csv")
pd.concat([a, b], ignore_index=True).to_csv("eval/results/phase-v2-merged/episodes.csv", index=False)
PYEOF
$PY -m eval.phase --summarise-only --out eval/results/phase-v2-merged > /dev/null 2>&1
# forecast-trust sweep (0 = queue-only, 1 = certainty equivalence), same seeds as mvp-v2
$NICE $PY -m eval.harness --scenarios shock drift shock+drift shock+drift+spikes \
  --policies "mpc-ewma@trust=0.25" "mpc-ewma@trust=0.5" "mpc-ewma@trust=0.75" --seeds 200-229 --horizon 1440 \
  --workers $W --out eval/results/trust-v2 > eval/results/trust-v2.log 2>&1
echo "FOLLOWUP DONE $(date)" > eval/results/v2-followup.done
