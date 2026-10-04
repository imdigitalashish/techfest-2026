#!/usr/bin/env bash
# Headless smoke test for the P3 demo: exits 0 only if every check passes. Offline; needs no .data and no network.
#   perceptron-p03-off-policy-eval/demo/smoke.sh
# Python: $P3_PYTHON, else perceptron-p03-off-policy-eval/.venv/bin/python if present, else python3 (needs numpy for
# the knob recompute). The checks are listed at the top of demo/smoke_check.py.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ="$(cd "$HERE/.." && pwd)"
if [ -n "${P3_PYTHON:-}" ]; then PY="$P3_PYTHON"
elif [ -x "$PROJ/.venv/bin/python" ]; then PY="$PROJ/.venv/bin/python"
else PY="$(command -v python3 || true)"; fi
[ -n "$PY" ] || { echo "smoke: no Python found (set P3_PYTHON)"; exit 1; }
"$PY" -c "import numpy" 2>/dev/null || { echo "smoke: $PY has no numpy (needed to recompute the knob); set P3_PYTHON"; exit 1; }
echo "smoke: python $PY"
exec nice -n 10 "$PY" "$HERE/smoke_check.py"
