#!/usr/bin/env bash
# P7 demo, one command:  perceptron-p07-multi-agent-allocation/demo/run.sh  [--no-open] [--port N] [--no-prewarm]
# A fresh clone first creates .venv once (needs network once: demo/setup_venv.sh). After that everything runs
# offline on CPU and http://127.0.0.1:8707/ opens in the default browser on the July 4th (real trips) tab.
set -euo pipefail
now() { python3 -c 'import time; print(time.time())' 2>/dev/null || date +%s; }
T0=$(now)                  # time to first visual counts from here (or from the end of the one-time setup)
cd "$(dirname "$0")/.."    # the project folder (perceptron-p07-multi-agent-allocation)
if [ ! -x .venv/bin/python ]; then bash demo/setup_venv.sh; T0=$(now); fi
for f in demo/data/evidence.js demo/data/nyc_jul03-04_r200.npz demo/data/recorded_live.js; do
  [ -f "$f" ] || { echo "[P7 demo] missing committed export: $f"; exit 1; }
done
exec .venv/bin/python -m demo.server --t0 "$T0" "$@"
