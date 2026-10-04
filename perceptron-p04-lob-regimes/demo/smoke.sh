#!/usr/bin/env bash
# Headless smoke test for the P4 demo. From a fresh clone it fetches the 16 needed days if missing, builds the live
# replay cache with the committed code, serves the page once over HTTP, and asserts the key outputs
# (live == committed, sweep anchors on all 22 held-out days, aggregates-only outputs, page wiring).
# Exits non-zero on failure.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
T0=$(date +%s)
echo "[smoke] build (fetch if missing, replay cache)"
demo/run.sh --build-only
echo "[smoke] serve once and fetch the page and its data over HTTP"
PORT=$("$PY" -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1])')
"$PY" -m http.server "$PORT" --bind 127.0.0.1 --directory demo >/dev/null 2>&1 &
SP=$!
trap 'kill $SP 2>/dev/null || true' EXIT
for _ in $(seq 50); do curl -fs "http://127.0.0.1:$PORT/index.html" >/dev/null 2>&1 && break; sleep 0.1; done
for u in index.html results/scoreboard.json results/alarm_dial_sweep.json .cache/status.json; do
  curl -fs -o /dev/null "http://127.0.0.1:$PORT/$u" && echo "  ok   GET /$u" || { echo "  FAIL GET /$u"; exit 1; }
done
echo "[smoke] assertions"
"$PY" demo/smoke_check.py
echo "[smoke] total $(( $(date +%s) - T0 )) s"
