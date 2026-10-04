#!/usr/bin/env bash
# Headless smoke test: no browser, no GPU, under nice -n 10 (about 1-3 min with the live checks). Exit 0 = pass.
# Without the project venv only the committed-results checks can run, and the script exits 1 unless
# SMOKE_REPLAY_ONLY=1 is set (then: replay + server checks only, live path explicitly unchecked).
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ "${SMOKE_REPLAY_ONLY:-0}" == "1" ]]; then
  exec nice -n 10 python3 demo/smoke_checks.py --replay-only
fi
if [[ ! -x .venv/bin/python ]]; then
  echo "no .venv: run demo/fetch.sh first (or SMOKE_REPLAY_ONLY=1 demo/smoke.sh for the replay checks only)"
  exit 1
fi
exec nice -n 10 .venv/bin/python demo/smoke_checks.py
