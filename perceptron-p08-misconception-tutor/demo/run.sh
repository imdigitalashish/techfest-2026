#!/usr/bin/env bash
# P8 demo: one command from a fresh clone. Run from anywhere:
#   perceptron-p08-misconception-tutor/demo/run.sh [--fetch] [--port N] [--no-browser] [--local-text]
#
# 1. Creates the project venv (.venv, Python 3.11, CPU only) if it is missing or incomplete.
# 2. --fetch (optional): downloads the pinned public data into the gitignored .data/. The demo does NOT need it;
#    it is only for --local-text (internal verification) and for re-running demo/export.py.
# 3. Starts the demo server on 127.0.0.1 and opens the browser. No LLM or other API is ever called.
#
# --local-text is INTERNAL VERIFICATION ONLY: it shows Eedi item text from .data/. Never in front of judges,
# in recordings or in screenshots (Kaggle Eedi competition rules §7.B; CC BY-NC 4.0).
set -euo pipefail
cd "$(dirname "$0")/.."
source demo/_venv.sh

ARGS=()
for a in "$@"; do
  if [[ "$a" == "--fetch" ]]; then
    nice -n 10 .venv/bin/python -m eval.data.fetch
  else
    ARGS+=("$a")
  fi
done
exec .venv/bin/python -m demo.server ${ARGS[@]+"${ARGS[@]}"}
