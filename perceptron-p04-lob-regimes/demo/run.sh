#!/usr/bin/env bash
# P4 demo, "the alarm that cries wolf". One command from a fresh clone:
#   perceptron-p04-lob-regimes/demo/run.sh            # fetch missing data -> serve page -> build live replay cache
#   demo/run.sh --no-open                             # do not open a browser tab
#   demo/run.sh --build-only                          # fetch + build the replay cache, no server (used by smoke.sh)
#   PORT=8765 demo/run.sh
# The page (scoreboard + 22-day dial sweep, committed) appears at once; replay panels fill in as each day is built.
set -euo pipefail
cd "$(dirname "$0")/.."                      # project folder: perceptron-p04-lob-regimes/
PY="${PYTHON:-python3}"
OPEN=1; SERVE=1
for a in "$@"; do
  case "$a" in
    --no-open) OPEN=0 ;;
    --build-only) SERVE=0; OPEN=0 ;;
    *) echo "unknown option $a"; exit 2 ;;
  esac
done
T0=$(date +%s)
mkdir -p demo/.cache

"$PY" - <<'EOF' || { echo "Missing Python packages: pip install numpy scipy polars scikit-learn matplotlib"; exit 1; }
import numpy, scipy, polars, sklearn  # noqa: F401
EOF

# 1. Data: the 12 training days (2023) + the replay days; only missing files are downloaded (free first-of-month
#    Tardis.dev files, no API key, ~473 MB total; MD5 checked against the x-md5 header and data/manifest.csv).
mapfile_days() {
  "$PY" -c "import json;print(' '.join([f'2023-{m:02d}-01' for m in range(1,13)]+[r['day'] for r in json.load(open('demo/results/scoreboard.json'))['replay_days']]))"
}
NEED=$(mapfile_days)
MISSING=()
for d in $NEED; do
  [[ -f ".data/raw/tardis/binance-futures/book_snapshot_5/${d}_BTCUSDT.csv.gz" ]] || MISSING+=("$d")
done
if (( ${#MISSING[@]} )); then
  echo "[run.sh] fetching ${#MISSING[@]} missing day(s): ${MISSING[*]}"
  "$PY" data/fetch_tardis.py --types book_snapshot_5 --workers 2 --days "${MISSING[@]}"
  "$PY" - "${MISSING[@]}" <<'EOF'
import csv, hashlib, sys
man = {r["day"]: r["md5"] for r in csv.DictReader(open("data/manifest.csv")) if r["dtype"] == "book_snapshot_5"}
for d in sys.argv[1:]:
    h = hashlib.md5(open(f".data/raw/tardis/binance-futures/book_snapshot_5/{d}_BTCUSDT.csv.gz", "rb").read()).hexdigest()
    if man.get(d) and h != man[d]:
        sys.exit(f"MD5 mismatch for {d}: {h} != manifest {man[d]}")
print("[run.sh] MD5s match data/manifest.csv")
EOF
else
  echo "[run.sh] all $(echo $NEED | wc -w | tr -d ' ') needed days present; running offline"
fi

# 2. Serve the page right away (committed scoreboard + sweep render instantly).
SERVER_PID=""
cleanup() { [[ -n "$SERVER_PID" ]] && kill "$SERVER_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM
if (( SERVE )); then
  PORT="${PORT:-$("$PY" -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1])')}"
  "$PY" -m http.server "$PORT" --bind 127.0.0.1 --directory demo >demo/.cache/server.log 2>&1 &
  SERVER_PID=$!
  for _ in $(seq 50); do curl -fs "http://127.0.0.1:$PORT/index.html" >/dev/null 2>&1 && break; sleep 0.1; done
  URL="http://127.0.0.1:$PORT/index.html"
  echo "[run.sh] page live at $URL  ($(( $(date +%s) - T0 )) s after start)"
  (( OPEN )) && { open "$URL" 2>/dev/null || xdg-open "$URL" 2>/dev/null || true; }
fi

# 3. Live replay cache (committed code, CPU only, nice'd, <= 3 workers, memory guard inside).
nice -n 10 "$PY" demo/build_replay.py --workers "${WORKERS:-3}"
echo "[run.sh] replay cache ready ($(( $(date +%s) - T0 )) s after start)"

if (( SERVE )); then
  echo "[run.sh] serving $URL. Press Ctrl-C to stop."
  wait "$SERVER_PID"
fi
