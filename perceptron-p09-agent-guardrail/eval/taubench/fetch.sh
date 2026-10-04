#!/usr/bin/env bash
# Fetch τ-bench (MIT) at the commit used for our replay results into the gitignored .data/ folder (~65 MB).
set -euo pipefail
cd "$(dirname "$0")/../.."
mkdir -p .data
if [ ! -d .data/tau-bench ]; then
  git clone -q https://github.com/sierra-research/tau-bench.git .data/tau-bench
fi
git -C .data/tau-bench checkout -q 59a200c
git -C .data/tau-bench log -1 --format='tau-bench at %h (%cd)'
