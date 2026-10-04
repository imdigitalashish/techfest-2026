#!/usr/bin/env bash
# Ghost Market (P5 demo). One command from a fresh clone:  perceptron-p05-impact-execution/demo/run.sh
# Serves demo/ on 127.0.0.1 and opens the browser. The replays need nothing beyond python3; the live lane
# additionally needs the README's venv and scripts/fetch_abides.sh (offline after that).
#   DEMO_NO_OPEN=1   don't open a browser; print READY and keep serving until Ctrl-C
#   DEMO_STATIC=1    print READY for the offline file:// page and exit (no server, no live lane)
#   DEMO_PORT=8650   first port to try (the server scans 20 ports)
set -euo pipefail
cd "$(dirname "$0")"
DEMO="$(pwd)"
[ -f data/summary.js ] || { echo "demo/data/summary.js missing: run demo/export.py" >&2; exit 1; }
FILE_URL="file://$DEMO/index.html"

open_url() {
  [ "${DEMO_NO_OPEN:-0}" = 1 ] && return 0
  if command -v open >/dev/null 2>&1; then open "$1"
  elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$1" >/dev/null 2>&1 &
  else echo "open $1 in a browser"; fi
}

if [ "${DEMO_STATIC:-0}" = 1 ]; then echo "READY: $FILE_URL"; open_url "$FILE_URL"; exit 0; fi

PY=../.venv/bin/python
[ -x "$PY" ] || PY="$(command -v python3 || true)"
if [ -z "$PY" ]; then echo "READY: $FILE_URL"; echo "(no python3: replays only)"; open_url "$FILE_URL"; exit 0; fi

LOG="$(mktemp -t p5demo.XXXXXX)"
nice -n 10 "$PY" server.py --port "${DEMO_PORT:-8650}" >"$LOG" 2>&1 &
PID=$!
cleanup() { kill "$PID" 2>/dev/null || true; rm -f "$LOG"; }
trap cleanup EXIT
trap 'cleanup; exit 0' INT TERM

URL=""
for _ in $(seq 1 150); do
  URL="$(sed -n 's/^SERVING //p' "$LOG" | head -1)"
  if [ -n "$URL" ] && curl -fsS -o /dev/null "$URL" 2>/dev/null; then break; fi
  kill -0 "$PID" 2>/dev/null || { URL=""; break; }
  sleep 0.1
done
if [ -z "$URL" ]; then
  echo "server did not start; falling back to the offline page"; tail -3 "$LOG" || true
  echo "READY: $FILE_URL"; open_url "$FILE_URL"; exit 0
fi
echo "READY: $URL"
open_url "$URL"
for _ in $(seq 1 30); do
  S="$(curl -fsS "${URL}api/status" 2>/dev/null || true)"
  case "$S" in *warming*) sleep 0.5 ;; *) break ;; esac
done
echo "live lane: $(printf '%s' "$S" | sed -n 's/.*"reason":"\([^"]*\)".*/\1/p')  (Ctrl-C stops the server)"
wait "$PID"
