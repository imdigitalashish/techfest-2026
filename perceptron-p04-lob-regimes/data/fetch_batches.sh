#!/usr/bin/env bash
# Grow the dataset in small sequential batches (each batch <= 5 files, < 200 MB), round-robin across
# years so coverage stays even if the network stalls. Usage (from perceptron-p04-lob-regimes/):
#   data/fetch_batches.sh book_snapshot_5
set -uo pipefail
TYPE="${1:-book_snapshot_5}"
have() { test -f ".data/raw/tardis/binance-futures/$TYPE/$1_BTCUSDT.csv.gz"; }
days=()
for m in 01 02 03 04 05 06 07 08 09 10 11 12; do
  for y in 2023 2024 2025 2026; do
    d="$y-$m-01"
    [[ "$d" > "2026-10-01" ]] && continue
    have "$d" || days+=("$d")
  done
done
echo "missing ${#days[@]} days"
for ((i=0; i<${#days[@]}; i+=5)); do
  batch=("${days[@]:i:5}")
  echo "batch $((i/5+1)): ${batch[*]}"
  python3 data/fetch_tardis.py --types "$TYPE" --workers 2 --days "${batch[@]}"
done
