#!/usr/bin/env bash
# Headless smoke test for the P10 demo (fresh clone OK; no StockNet fetch needed):
#   bash perceptron-p10-trusted-text-signal/demo/smoke.sh
# 1) engine-level assertions against eval/results/text_minilm_v2.json (smoke_test.py, within 1e-9)
# 2) starts the server, checks every endpoint and the typed-post scoring path
# 3) loads the page in headless Chrome (skipped with a warning if Chrome is absent)
# Set P10_ALLOW_VADER=1 to accept the VADER fallback when the MiniLM encoder is not cached.
set -euo pipefail
source "$(dirname "$0")/_env.sh"
resolve_python
wait_for_memory
cd "$PROJ"
FAIL=0
echo "== 1/3 engine assertions (python: $PY)"
nice -n 10 "$PY" "$DEMO/smoke_test.py" || FAIL=1

echo "== 2/3 server endpoints"
PORT=$(free_port 8790); URL="http://127.0.0.1:$PORT"
P10_T0=$(now) nice -n 10 "$PY" "$DEMO/server.py" --port "$PORT" > "$DEMO/smoke_server.log" 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null || true' EXIT INT TERM
T0=$(now)
for _ in $(seq 1 600); do curl -sf -o /dev/null "$URL/api/meta" && break; sleep 0.2; done
echo "server ready in $(perl -e "printf '%.1f', $(now) - $T0") s"
for _ in $(seq 1 240); do curl -sf "$URL/api/health" | grep -q '"ready": true' && break; sleep 0.5; done
nice -n 10 "$PY" - "$URL" <<'PYEOF' || FAIL=1
import json, os, sys, urllib.request
B = sys.argv[1]
committed = json.load(open("eval/results/text_minilm_v2.json"))
fails = []
def call(path, body=None):
    req = urllib.request.Request(B + path, None if body is None else json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        assert r.status == 200, (path, r.status)
        data = r.read()
    return data if path == "/" else json.loads(data)
def ok(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name, detail, flush=True)
    if not cond: fails.append(name)
page = call("/").decode()
ok("GET / serves the page", "Break the band" in page and "<script>" in page and "cdn" not in page.lower())
h = call("/api/health"); ok("GET /api/health", h["engine_ready"] and h["scorer"]["ready"], h["scorer"]["label"])
m = call("/api/meta"); ok("GET /api/meta: live ACI = committed", abs(m["aci_clean_live"]["coverage"] - committed["ablation"]["fusion"]["cqr_aci"]["coverage"]) <= 1e-9,
                         f'{m["aci_clean_live"]["coverage"]:.12f}')
r = call("/api/random?seed=3"); ok("GET /api/random", "row" in r)
d0 = m["showcase_days"][0]
d = call("/api/day", {"ticker": d0["ticker"], "date": d0["date"]}); ok("POST /api/day", d["ticker"] == d0["ticker"])
tpl = m["pump_template"]
s = call("/api/score", {"texts": [tpl, "terrible quarter, sell everything"]})
pump = committed["attack"]["pump"]["pump_sentiment"]
if s["scorer"] == "minilm":
    ok("POST /api/score (MiniLM, typed post) ~ committed pump sentiment", abs(s["compound"][0] - pump) <= 1e-4, f'{s["compound"][0]:.10f} vs {pump:.10f}')
else:
    ok("POST /api/score uses VADER fallback", os.environ.get("P10_ALLOW_VADER") == "1", "set P10_ALLOW_VADER=1 to accept")
ok("typed posts: bullish > bearish", s["compound"][0] > s["compound"][1], str(s["compound"]))
t = call("/api/trust", {"followers": 0, "age_days": 1, "verified": False, "n_cashtags": 1})
ok("POST /api/trust = committed pump trust", abs(t["trust"] - committed["attack"]["pump"]["pump_trust"]) <= 1e-12)
row = d["row"]
a = call("/api/attack", {"row": row, "posts": [{"sentiment": s["compound"][0], "trust": t["trust"], "copies": 3}], "k": 3})
ok("POST /api/attack: certified contains clean within budget", a["within_budget"] and a["certified"]["contains_clean"])
f = call("/api/flips", {"row": row, "k": 3}); ok("POST /api/flips: showcase day is flippable, certified survives", f["n_flipping"] > 0 and f["n_flipping_cert_survives"] == f["n_flipping"], f'{f["n_flipping"]}/{f["n_variants"]}')
rt = call("/api/redteam", {"row": row, "k": 3, "n": 500, "seed": 7}); ok("POST /api/redteam: 0 violations within budget", rt["within"]["cert_containment_violations"] == 0, f'plain broken {rt["within"]["plain_broken"]}/500')
P = call("/api/population", {"posts": [{"sentiment": pump, "trust": committed["attack"]["pump"]["pump_trust"], "copies": 3}], "k": 3})
ok("POST /api/population: pump CR-ACI = committed", abs(P["cr_aci"]["coverage"] - committed["spike"]["cr_aci"]["cr_aci_pump"]["coverage"]) <= 1e-9)
for bad in ({"row": -1}, {"row": row, "k": 99}):
    try:
        call("/api/attack", {**bad, "posts": []}); ok(f"rejects {bad}", False)
    except urllib.error.HTTPError as ex:
        ok(f"rejects {bad}", ex.code == 400)
sys.exit(1 if fails else 0)
PYEOF

echo "== 3/3 headless page load"
CHROME=""
for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" "$(command -v google-chrome || true)" "$(command -v chromium || true)"; do
  [ -n "$c" ] && [ -x "$c" ] && CHROME="$c" && break
done
run_selftest() {  # base_url wait_s -> prints the JSON the page POSTed to /api/selftest ('' if none)
  local prof cpid res=""
  prof=$(mktemp -d)
  "$CHROME" --headless=new --disable-gpu --no-first-run --no-default-browser-check --user-data-dir="$prof" \
    --remote-debugging-port=0 "$1/#selftest" > /dev/null 2>&1 &
  cpid=$!
  for _ in $(seq 1 $(( $2 * 2 ))); do
    res=$(curl -sf "$1/api/selftest" 2>/dev/null || true)
    echo "$res" | grep -q '"status": "' && break
    sleep 0.5
  done
  kill $cpid 2>/dev/null || true
  wait $cpid 2>/dev/null || true
  rm -rf "$prof" 2>/dev/null || true
  echo "$res"
}
if [ -n "$CHROME" ]; then
  # the page's own #selftest drives the real UI (inject a typed post, plain broken / certified guaranteed, grey badge
  # past k, red-team, stale-result regression) and POSTs its log; a page that never boots posts nothing
  RES=$(run_selftest "$URL" 90)
  echo "$RES" | "$PY" -c "import json,sys; d=json.loads(sys.stdin.read() or '{}'); print('\n'.join('    '+l for l in (d.get('log') or 'no self-test result').splitlines()))" || true
  if echo "$RES" | grep -q '"status": "pass"'; then
    echo "PASS  page self-test in headless Chrome"
  else
    echo "FAIL  page self-test in headless Chrome"; FAIL=1
  fi
  # negative control: the same page served without the backend must NOT report a pass
  NPORT=$(free_port 8890)
  "$PY" -m http.server "$NPORT" --bind 127.0.0.1 --directory "$DEMO/static" > /dev/null 2>&1 &
  NSRV=$!
  sleep 1
  NRES=$(run_selftest "http://127.0.0.1:$NPORT" 10)
  kill $NSRV 2>/dev/null || true
  if echo "$NRES" | grep -q '"status": "pass"'; then
    echo "FAIL  negative control: page self-test passed with the API unreachable"; FAIL=1
  else
    echo "PASS  negative control: with the API unreachable no self-test pass is recorded"
  fi
else
  echo "WARN  no Chrome found; page render not checked"
fi
[ $FAIL -eq 0 ] && echo "SMOKE: ALL PASS" || { echo "SMOKE: FAILURES"; exit 1; }
