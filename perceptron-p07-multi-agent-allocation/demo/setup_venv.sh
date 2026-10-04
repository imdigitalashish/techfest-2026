#!/usr/bin/env bash
# One-time environment for the P7 demo: creates <project>/.venv if it is missing (needs network once).
# Python 3.11 + requirements.txt + highspy 1.15.1 (the HiGHS version behind the committed results).
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -x .venv/bin/python ]; then exit 0; fi
echo "[P7 demo] one-time setup: creating .venv (Python 3.11 + requirements.txt + highspy 1.15.1) ..."
if command -v uv >/dev/null 2>&1; then
  uv venv .venv --python 3.11 --system-site-packages
  uv pip install --python .venv/bin/python --compile-bytecode -r requirements.txt "highspy==1.15.1"
else
  python3.11 -m venv --system-site-packages .venv
  .venv/bin/python -m pip install -q -r requirements.txt "highspy==1.15.1"
fi
# first load of freshly installed native libraries is slow on macOS (one-time scan); do it here, not on stage
.venv/bin/python -c "import numpy, scipy.optimize, scipy.sparse, highspy, pandas" && echo "[P7 demo] .venv ready"
