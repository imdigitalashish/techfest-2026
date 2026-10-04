#!/usr/bin/env bash
# One-time setup for the P10 demo (the documented prerequisite; run.sh also calls it if needed):
#   bash perceptron-p10-trusted-text-signal/demo/setup.sh
# Creates demo/.venv with uv from requirements.txt (offline wheel cache first) and pays macOS's one-time first-load
# scan of the new native libraries. Does nothing if P10_PYTHON or a project/demo venv with the deps already exists.
set -euo pipefail
source "$(dirname "$0")/_env.sh"
wait_for_memory
TS=$(now); CREATED=0
resolve_python
if [ "$CREATED" = 1 ]; then
  echo "[demo] one-time setup took $(perl -e "printf '%.0f', $(now) - $TS") s"
else
  echo "[demo] already set up: $PY"
fi
if "$PY" -c "import torch, transformers" >/dev/null 2>&1 \
   && ls "${HF_HOME:-$HOME/.cache/huggingface}/hub" 2>/dev/null | grep -q "models--sentence-transformers--all-MiniLM-L6-v2"; then
  echo "[demo] MiniLM encoder found in the Hugging Face cache: live scorer will be the deployed one"
else
  echo "[demo] MiniLM encoder (or torch) missing: the page will use the VADER FALLBACK, labelled on screen."
  echo "       To get the deployed scorer (about 90 MB, once, online): hf download sentence-transformers/all-MiniLM-L6-v2"
fi
