#!/usr/bin/env bash
# Usage (from perceptron-p04-lob-regimes/): components/shift_detector/autoresearch/run_candidate.sh <candidate.json> "<hypothesis>"
# Runs the frozen eval.py and appends one ledger row to results.tsv (kept? is decided by the lead per program.md).
set -euo pipefail
A=components/shift_detector/autoresearch
log=".data/ar_$(basename "$1" .json).log"
python3 "$A/eval.py" "$1" > "$log" 2>&1
score=$(grep '^SCORE' "$log" | awk '{print $2}')
detail=$(grep '^{' "$log" | tail -1 | tr '\t' ' ')
printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$(TZ=Asia/Kolkata date '+%Y-%m-%d %H:%M')" "$(git rev-parse --short HEAD)" \
  "$(basename "$1")" "$2" "$score" "pending" "pending (lead review)" "$detail" >> "$A/results.tsv"
