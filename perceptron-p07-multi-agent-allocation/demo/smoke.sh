#!/usr/bin/env bash
# Headless smoke test of the P7 demo (no browser):  perceptron-p07-multi-agent-allocation/demo/smoke.sh [--quick]
set -euo pipefail
cd "$(dirname "$0")/.."
bash demo/setup_venv.sh
exec .venv/bin/python -m demo.smoke "$@"
