#!/bin/bash
# P6 demo: one command. Starts the live backend (committed code, 127.0.0.1 only) and opens the page.
# Without the venv it opens the same page OFFLINE (precomputed grid), so the first visual never waits for Numba.
# One-time setup from a fresh clone (from perceptron-p06-stat-arb/):
#   uv venv .venv --python 3.11 && uv pip install --python .venv/bin/python -r requirements.lock
# Usage: perceptron-p06-stat-arb/demo/run.sh [--no-browser]    (PORT=8766 by default)
set -u
cd "$(dirname "$0")/.." || exit 2
PORT=${PORT:-8766}
PY=.venv/bin/python
open_url() { if [ "${1:-}" = "" ]; then return; fi; if command -v open >/dev/null 2>&1; then open "$1"; elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$1"; else echo "open $1 in a browser"; fi; }
NOBROWSER=0; [ "${1:-}" = "--no-browser" ] && NOBROWSER=1
if [ ! -x "$PY" ]; then
  echo "No .venv: opening the OFFLINE page (precomputed grid). For live mode run the one-time setup in this script's header."
  [ $NOBROWSER -eq 1 ] || open_url "file://$PWD/demo/index.html"
  exit 0
fi
PF=$(mktemp -t p6demo.XXXXXX)
"$PY" -m demo.server --port "$PORT" --port-file "$PF" &
SRV=$!
trap 'kill $SRV 2>/dev/null; rm -f "$PF"; exit 0' INT TERM
for _ in $(seq 1 150); do
  if [ -s "$PF" ] && curl -s -o /dev/null "http://127.0.0.1:$(cat "$PF")/index.html"; then break; fi
  if ! kill -0 $SRV 2>/dev/null; then echo "backend failed to start: opening the OFFLINE page"; [ $NOBROWSER -eq 1 ] || open_url "file://$PWD/demo/index.html"; exit 0; fi
  sleep 0.2
done
URL="http://127.0.0.1:$(cat "$PF")/"
echo "P6 demo at $URL (live mode upgrades as soon as Numba has compiled). Ctrl-C to stop."
[ $NOBROWSER -eq 1 ] || open_url "$URL"
wait $SRV
