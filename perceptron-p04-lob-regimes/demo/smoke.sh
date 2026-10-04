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
echo "[smoke] run.sh refuses an occupied port and never claims a page it does not serve"
BUSY=$("$PY" -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1])')
"$PY" -m http.server "$BUSY" --bind 127.0.0.1 --directory /tmp >/dev/null 2>&1 &
BP=$!
for _ in $(seq 50); do curl -s -o /dev/null "http://127.0.0.1:$BUSY/" && break; sleep 0.1; done
set +e
OUT=$(PORT="$BUSY" demo/run.sh --no-open 2>&1); RC=$?
set -e
kill "$BP" 2>/dev/null || true
if (( RC != 0 )) && ! grep -q "page live" <<<"$OUT" && grep -q "already in use" <<<"$OUT"; then
  echo "  ok   occupied port $BUSY -> exit $RC, no 'page live'"
else
  echo "  FAIL occupied port $BUSY -> exit $RC; output: $OUT"; exit 1
fi
echo "[smoke] assertions"
"$PY" demo/smoke_check.py
echo "[smoke] browser stage (headless Chromium)"
set +e
"$PY" demo/smoke_browser.py "http://127.0.0.1:$PORT/index.html"
rc=$?
set -e
if (( rc == 3 )); then
  echo "[smoke] WARNING: browser stage SKIPPED (Playwright/Chromium not installed); data assertions passed"
elif (( rc != 0 )); then
  exit "$rc"
fi
echo "[smoke] total $(( $(date +%s) - T0 )) s"
