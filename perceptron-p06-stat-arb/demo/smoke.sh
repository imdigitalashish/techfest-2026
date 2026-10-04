#!/bin/bash
# Headless smoke test for the P6 demo: static checks, committed-number reproduction, live backend vs exported grid.
# Usage (from anywhere): perceptron-p06-stat-arb/demo/smoke.sh      Exit code 0 = all assertions passed.
set -u
cd "$(dirname "$0")/.." || exit 2
PY=.venv/bin/python
if [ ! -x "$PY" ]; then
  echo "smoke: no .venv. Set up once: uv venv .venv --python 3.11 && uv pip install --python .venv/bin/python -r requirements.lock" >&2
  exit 2
fi
if command -v node >/dev/null 2>&1; then
  node -e "new Function(require('fs').readFileSync('demo/app.js','utf8'))" && echo "PASS  app.js parses (node)" || { echo "FAIL  app.js does not parse"; exit 1; }
fi
exec "$PY" -m demo.smoke
