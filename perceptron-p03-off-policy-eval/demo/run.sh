#!/usr/bin/env bash
# P3 live demo — one command: build the page and open it. Offline; works from a fresh clone (no .data, no network).
#
#   perceptron-p03-off-policy-eval/demo/run.sh
#
# Python (only needed to rebuild; demo/build.py uses the standard library): $P3_PYTHON, else
# perceptron-p03-off-policy-eval/.venv/bin/python if present, else python3. Without any Python, or if the build
# fails, the committed demo/index.html is opened as is. P3_NO_OPEN=1 skips opening a browser (used by smoke.sh).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ="$(cd "$HERE/.." && pwd)"
OUT="$HERE/index.html"

PY=""
if [ -n "${P3_PYTHON:-}" ]; then PY="$P3_PYTHON"
elif [ -x "$PROJ/.venv/bin/python" ]; then PY="$PROJ/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then PY="$(command -v python3)"
fi

now() { if [ -n "$PY" ]; then "$PY" -c 'import time; print(f"{time.time():.3f}")'; else date +%s; fi; }
T0="$(now)"

if [ -n "$PY" ]; then
  TMP="$(mktemp "${TMPDIR:-/tmp}/p3demo.XXXXXX")"
  if "$PY" "$HERE/build.py" --out "$TMP" >"$TMP.log" 2>&1; then
    if ! cmp -s "$TMP" "$OUT"; then cp "$TMP" "$OUT"; echo "rebuilt demo/index.html (it differs from the committed copy: inputs changed?)"; fi
    echo "built with $PY $(tail -n 1 "$TMP.log" | sed 's|^wrote [^ ]* ||')"
  else
    echo "build failed with $PY; opening the committed page. Build log:"; cat "$TMP.log"
  fi
  rm -f "$TMP" "$TMP.log"
else
  echo "no Python found; opening the committed demo/index.html"
fi
[ -f "$OUT" ] || { echo "missing $OUT"; exit 1; }

if [ "${P3_NO_OPEN:-0}" != "1" ]; then
  if command -v open >/dev/null 2>&1; then open "$OUT"
  elif command -v xdg-open >/dev/null 2>&1; then (xdg-open "$OUT" >/dev/null 2>&1 &)
  else echo "open this file in a browser:"; fi
fi
T1="$(now)"
echo "demo: $OUT"
if [ -n "$PY" ]; then "$PY" -c "print(f'page ready in {float(\"$T1\") - float(\"$T0\"):.1f} s (keys: 1-4 sheets, arrows move the knob, [ ] period, i estimator, c interval)')"; fi
