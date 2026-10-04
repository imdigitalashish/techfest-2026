#!/usr/bin/env bash
# P9 "Cite-Before-Act" demo: one command from a fresh clone, offline, CPU only.
#   bash perceptron-p09-agent-guardrail/demo/run.sh
# If the one-time setup (setup.sh) has not run yet, the browser first shows the RECORDED fallback screenshots and
# switches to the live page by itself when it is ready.
# Env: P9_PYTHON (interpreter), P9_PORT (default 8790), P9_NO_OPEN=1 (do not open a browser).
set -euo pipefail
source "$(dirname "$0")/_env.sh"
T0=$(now); export P9_T0="$T0"
wait_for_memory
PORT=$(free_port "${P9_PORT:-8790}")
URL="http://127.0.0.1:$PORT/"
open_url() { [ -n "${P9_NO_OPEN:-}" ] || (open "$1" 2>/dev/null || xdg-open "$1" 2>/dev/null || true); }
GAL=""
if ! find_python; then
  # setup still needed: serve the recorded gallery right away with any bare Python (stdlib only)
  BARE=$(command -v python3 || uv python find 3.11 2>/dev/null || true)
  if [ -n "$BARE" ]; then
    "$BARE" -m http.server "$PORT" --bind 127.0.0.1 --directory "$DEMO" > /dev/null 2>&1 &
    GAL=$!
    for _ in $(seq 1 100); do curl -sf -o /dev/null "${URL}static/setup.html" && break; sleep 0.1; done
    if curl -sf -o /dev/null "${URL}static/setup.html"; then
      echo "[demo] first visual (recorded fallback gallery) in $(perl -e "printf '%.1f', $(now) - $T0") s: ${URL}static/setup.html"
      open_url "${URL}static/setup.html"
    else
      echo "[demo] recorded gallery did not start; screenshots are in $DEMO/fallback/"
    fi
  fi
  bash "$DEMO/setup.sh"
  find_python
  if [ -n "$GAL" ]; then kill $GAL 2>/dev/null || true; wait $GAL 2>/dev/null || true; fi
fi
cd "$PROJ"
echo "[demo] python: $PY"
nice -n 10 "$PY" "$DEMO/server.py" --port "$PORT" > "$DEMO/server.log" 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null || true' EXIT INT TERM
for _ in $(seq 1 300); do
  curl -sf -o /dev/null "${URL}api/health" && break
  kill -0 $SRV 2>/dev/null || { echo "[demo] server died:"; cat "$DEMO/server.log"; exit 1; }
  sleep 0.2
done
curl -sf -o /dev/null "${URL}api/health" || { echo "[demo] server not ready after 60 s"; cat "$DEMO/server.log"; exit 1; }
echo "[demo] live first visual ready in $(perl -e "printf '%.1f', $(now) - $T0") s since launch"
grep -h "^\[demo\]" "$DEMO/server.log" || true
echo "[demo] OPEN  $URL"
[ -n "$GAL" ] || open_url "$URL"
echo "[demo] Ctrl-C to stop."
wait $SRV
