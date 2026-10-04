#!/usr/bin/env bash
# P10 "Break the band" demo — one command from a fresh clone, offline, CPU only:
#   bash perceptron-p10-trusted-text-signal/demo/run.sh
# If the one-time setup (setup.sh) has not run yet, the browser first shows the RECORDED fallback screenshots and
# switches to the live page by itself when it is ready.
# Env: P10_PYTHON (interpreter), P10_PORT (default 8710), P10_NO_OPEN=1 (do not open a browser).
set -euo pipefail
source "$(dirname "$0")/_env.sh"
T0=$(now); export P10_T0="$T0"
wait_for_memory
PORT=$(free_port "${P10_PORT:-8710}")
URL="http://127.0.0.1:$PORT/"
open_url() { [ -n "${P10_NO_OPEN:-}" ] || (open "$1" 2>/dev/null || xdg-open "$1" 2>/dev/null || true); }
GAL=""
if ! find_python; then
  # setup still needed: serve the recorded gallery right away with any bare Python (stdlib only)
  BARE=$(uv python find 3.11 2>/dev/null || command -v python3 || true)
  if [ -n "$BARE" ]; then
    "$BARE" -m http.server "$PORT" --bind 127.0.0.1 --directory "$DEMO" > /dev/null 2>&1 &
    GAL=$!
    for _ in $(seq 1 50); do curl -sf -o /dev/null "${URL}static/setup.html" && break; sleep 0.1; done
    echo "[demo] recorded fallback gallery up in $(perl -e "printf '%.1f', $(now) - $T0") s: ${URL}static/setup.html"
    open_url "${URL}static/setup.html"
  fi
  bash "$DEMO/setup.sh"
  find_python
  [ -n "$GAL" ] && { kill $GAL 2>/dev/null || true; wait $GAL 2>/dev/null || true; }
fi
TL=$(now)
cd "$PROJ"
echo "[demo] python: $PY"
nice -n 10 "$PY" "$DEMO/server.py" --port "$PORT" > "$DEMO/server.log" 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null || true' EXIT INT TERM
for _ in $(seq 1 600); do
  curl -sf -o /dev/null "${URL}api/meta" && break
  kill -0 $SRV 2>/dev/null || { echo "[demo] server died:"; cat "$DEMO/server.log"; exit 1; }
  sleep 0.2
done
curl -sf -o /dev/null "${URL}api/meta" || { echo "[demo] server not ready after 120 s"; cat "$DEMO/server.log"; exit 1; }
T1=$(now)
echo "[demo] live first visual ready in $(perl -e "printf '%.1f', $T1 - $TL") s after setup ($(perl -e "printf '%.1f', $T1 - $T0") s since launch)"
echo "[demo] OPEN  $URL"
[ -n "$GAL" ] || open_url "$URL"
for _ in $(seq 1 120); do grep -q "scorer:" "$DEMO/server.log" && break; sleep 0.5; done
grep -h "^\[demo\]" "$DEMO/server.log" || true
grep -q "scorer:" "$DEMO/server.log" || echo "[demo] scorer still warming up (the page works meanwhile)"
echo "[demo] Ctrl-C to stop."
wait $SRV
