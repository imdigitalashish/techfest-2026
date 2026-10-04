#!/usr/bin/env bash
# P8 demo smoke test: headless (no browser, no LLM, no network). Exit 0 = pass.
#   perceptron-p08-misconception-tutor/demo/smoke.sh
# Starts the backend in no-text mode and checks the key outputs against the committed results. If the local .data/
# copy exists, it also checks local-text mode (live engine on all 304 real items = the export) and runs the leak guard.
set -euo pipefail
cd "$(dirname "$0")/.."
source demo/_venv.sh
exec nice -n 10 .venv/bin/python -m demo.smoke "$@"
