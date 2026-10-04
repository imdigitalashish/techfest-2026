#!/usr/bin/env bash
# P2 demo — one command from a fresh clone (perceptron-p02-kv-cache/demo/run.sh).
#   demo/run.sh          REPLAY: committed T1/T2/T3 results in the browser. Instant, offline, no model loaded.
#   demo/run.sh --live   also LIVE: plant your own fact and squeeze the KV cache on this CPU. The 1B model loads lazily
#                        on the first live request (fp16 in RAM, ~3 GB) and is freed when this script exits.
#                        One-time prerequisite: demo/fetch.sh (haystack + exported weights; then offline).
# Options: --no-open (don't open a browser) · --port=N (default 8502; the next free port is used if busy) · --fp32
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${DEMO_PORT:-8502}"; LIVE=0; OPEN=1; EXTRA=()
for a in "$@"; do
  case "$a" in
    --live) LIVE=1 ;;
    --no-open) OPEN=0 ;;
    --port=*) PORT="${a#--port=}" ;;
    --fp32) EXTRA+=(--fp32) ;;
    -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
    *) echo "unknown option $a (see --help)" >&2; exit 2 ;;
  esac
done
command -v python3 >/dev/null || { echo "run.sh: python3 is required" >&2; exit 1; }
[ -s "$HERE/web/replay.js" ] || { echo "run.sh: demo/web/replay.js missing; building it from the committed rows"; python3 "$HERE/export_replay.py"; }
ARGS=(--port "$PORT")
if [ "$LIVE" = 1 ]; then
  ARGS+=(--live "${EXTRA[@]+"${EXTRA[@]}"}")
  python3 -c "import torch, transformers, safetensors" 2>/dev/null \
    || echo "run.sh: LIVE needs torch, transformers and safetensors in python3; REPLAY still works" >&2
  python3 - "$HERE" <<'PY' || echo "run.sh: LIVE needs the one-time fetch first: demo/fetch.sh  (REPLAY works now)" >&2
import sys; sys.path.insert(0, sys.argv[1]); import common
ok, why = common.data_ready(); sys.exit(0 if ok else 1)
PY
fi
LOG="$(mktemp -t p2demo.XXXXXX)"
HF_HUB_OFFLINE=1 nice -n 10 python3 "$HERE/server.py" "${ARGS[@]}" >"$LOG" 2>&1 &
SRV=$!
TAIL=""
cleanup() { [ -n "$TAIL" ] && kill "$TAIL" 2>/dev/null; kill "$SRV" 2>/dev/null || true; wait "$SRV" 2>/dev/null || true; rm -f "$LOG"; }
trap cleanup EXIT INT TERM
URL=""
for _ in $(seq 1 100); do
  URL="$(sed -n 's/^DEMO_URL=//p' "$LOG" | head -1)"
  [ -n "$URL" ] && break
  kill -0 "$SRV" 2>/dev/null || break
  sleep 0.1
done
[ -n "$URL" ] || { cat "$LOG" >&2; echo "run.sh: server did not start" >&2; exit 1; }
[ "$LIVE" = 1 ] && URL="${URL}#live"
echo "P2 demo running at $URL  (Ctrl-C to stop$([ "$LIVE" = 1 ] && echo "; the model's memory is freed on exit"))"
if [ "$OPEN" = 1 ]; then (open "$URL" 2>/dev/null || xdg-open "$URL" 2>/dev/null || true); fi
tail -n +2 -f "$LOG" &
TAIL=$!
wait "$SRV" || true
