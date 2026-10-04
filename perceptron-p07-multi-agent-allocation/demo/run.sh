#!/usr/bin/env bash
# P7 demo — one command:  perceptron-p07-multi-agent-allocation/demo/run.sh  [--no-open] [--port N]
# First run on a fresh clone: creates .venv once (needs network once; documented in demo/README.md).
# After that everything runs offline on CPU: http://127.0.0.1:8707/ opens in the default browser.
set -euo pipefail
T0=$(python3 -c 'import time; print(time.time())' 2>/dev/null || date +%s)
cd "$(dirname "$0")/.."    # the project folder (perceptron-p07-multi-agent-allocation)

if [ ! -x .venv/bin/python ]; then
  echo "[P7 demo] one-time setup: creating .venv (Python 3.11 + requirements.txt + highspy 1.15.1) ..."
  if command -v uv >/dev/null 2>&1; then
    uv venv .venv --python 3.11 --system-site-packages
    uv pip install --python .venv/bin/python --compile-bytecode -r requirements.txt "highspy==1.15.1"
  else
    python3.11 -m venv --system-site-packages .venv
    .venv/bin/python -m pip install -q -r requirements.txt "highspy==1.15.1"
  fi
  T0=$(python3 -c 'import time; print(time.time())' 2>/dev/null || date +%s)   # time-to-first-visual counts from here
fi
if [ ! -f demo/data/evidence.js ] || [ ! -f demo/data/nyc_jul03-04_r200.npz ]; then
  echo "[P7 demo] missing committed exports in demo/data (evidence.js, nyc_jul03-04_r200.npz)"; exit 1
fi
exec .venv/bin/python -m demo.server --t0 "$T0" "$@"
