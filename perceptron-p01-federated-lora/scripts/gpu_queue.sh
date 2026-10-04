#!/usr/bin/env bash
# One-heavy-job-at-a-time GPU queue for the shared M5 (Supervisor rule from 4 Oct 08:30 IST: heavy jobs run
# sequentially under `nice -n 10`). Every step skips runs already present in the results jsonl, so the
# queue can be killed and restarted safely.
#
# Usage: scripts/gpu_queue.sh [phase...]   phases: replicate ratchet ablate clean   (default: all, in order)
set -uo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
NICE="nice -n 10"
RM="python -m eval.run_matrix --tag v1 --skip-existing"

phase_replicate() {  # Supervisor ask: >=3 more seeds of the spike and the starter, dropout scenario
  $NICE $RM --scenario dropout --seeds 1 2 3 4 --strategies anchor_full fedavg_ab_homo
}
phase_ratchet() {    # aggregator ratchet candidates, same dropout scenario, seeds 0-1 (= eval.py protocol)
  $NICE $RM --scenario dropout --seeds 0 1 \
    --strategies anchor_full_tauact anchor_full_seg anchor_full_decay anchor_full_sqrtn
}
phase_ablate() {     # remaining ablation rungs on the extra seeds
  $NICE $RM --scenario dropout --seeds 1 2 3 4 --strategies fedavg_ab_het anchor_naive
}
phase_clean() {      # clean scenario replicates -> robustness delta (dropout - clean) per strategy
  $NICE $RM --scenario clean --seeds 0 1 2 --strategies anchor_full fedavg_ab_homo fedavg_ab_het anchor_naive
}

phases=("$@")
[ ${#phases[@]} -eq 0 ] && phases=(replicate ratchet ablate clean)
for p in "${phases[@]}"; do
  echo "=== $(date '+%H:%M') phase $p"
  "phase_$p"
done
echo "=== $(date '+%H:%M') queue done"
