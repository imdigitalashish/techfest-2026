#!/usr/bin/env bash
# One-time setup for the P9 demo (run.sh calls it if needed):
#   bash perceptron-p09-agent-guardrail/demo/setup.sh
# Creates the project's .venv from uv.lock (pydantic, numpy, rank-bm25, pyyaml; offline wheel cache first).
# The demo needs no τ-bench download, no model and no API: its data is the committed demo/data/bundle.json.gz.
set -euo pipefail
source "$(dirname "$0")/_env.sh"
wait_for_memory
TS=$(now); CREATED=0
resolve_python
if [ "$CREATED" = 1 ]; then
  echo "[demo] one-time setup took $(perl -e "printf '%.1f', $(now) - $TS") s"
else
  echo "[demo] already set up: $PY"
fi
