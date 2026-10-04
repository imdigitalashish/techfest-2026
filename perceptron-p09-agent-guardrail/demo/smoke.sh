#!/usr/bin/env bash
# Headless smoke test for the P9 demo (fresh clone OK; no τ-bench download, no model, no API):
#   bash perceptron-p09-agent-guardrail/demo/smoke.sh
# 1) engine assertions (smoke_test.py): live Tier 0 == committed on 300/300 calls for every config, on-screen numbers
#    == committed files, every curated injection stopped and benign tickets allowed, desk == mvp-demo-output.txt
# 2) starts the server and checks every endpoint
# 3) renders the page in headless Chrome and checks the live content appeared (skipped with a warning if no Chrome)
set -euo pipefail
source "$(dirname "$0")/_env.sh"
resolve_python
wait_for_memory
cd "$PROJ"
FAIL=0
echo "== 1/3 engine assertions (python: $PY)"
nice -n 10 "$PY" "$DEMO/smoke_test.py" || FAIL=1

echo "== 2/3 server endpoints"
PORT=$(free_port 8890); URL="http://127.0.0.1:$PORT"
nice -n 10 "$PY" "$DEMO/server.py" --port "$PORT" > "$DEMO/smoke_server.log" 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null || true' EXIT INT TERM
T0=$(now)
for _ in $(seq 1 300); do curl -sf -o /dev/null "$URL/api/health" && break; sleep 0.2; done
echo "server ready in $(perl -e "printf '%.1f', $(now) - $T0") s"
nice -n 10 "$PY" - "$URL" <<'PYEOF' || FAIL=1
import gzip, json, sys, urllib.request, urllib.error
B = sys.argv[1]
fails = []
def call(path, body=None):
    req = urllib.request.Request(B + path, None if body is None else json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            data = gzip.decompress(data)
    return data if path == "/" else json.loads(data)
def ok(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + (f"  [{detail}]" if detail else ""), flush=True)
    if not cond: fails.append(name)
page = call("/").decode()
ok("GET / serves the offline page (no CDN, no external URL)", "Cite-Before-Act" in page and "<script>" in page and "cdn" not in page.lower() and "https://" not in page)
ok("GET /api/health", call("/api/health")["ready"])
b = call("/api/bundle"); ok("GET /api/bundle (gzip)", len(b["items"]) == 300)
for c in ("t0_strict", "t0_balanced", "t0_v0", "t0_lenient", "none"):
    s = call(f"/api/sweep?config={c}"); ok(f"GET /api/sweep?config={c}: live == committed", s["mode"] == "live" and s["matches_committed"] == 300)
s = call("/api/sweep?config=cascade_aoai"); ok("GET /api/sweep?config=cascade_aoai: replayed 53/120", s["mode"] == "replayed" and s["counts"]["harmful_stopped"] == 53)
it = call("/api/item?id=gpt-4o/t75/r2/m20.0&config=t0_strict"); ok("GET /api/item hero -> HOLD with evidence list", it["decision"] == "escalate" and len(it["checks"]) >= 5)
h = call("/api/hijack", {"scenario": "cancel", "ticket": b["scenarios"][2]["ticket"]}); ok("POST /api/hijack cancel-swap -> BLOCK", h["verdict"]["decision"] == "block" and h["control"]["decision"] == "allow")
d = call("/api/desk"); ok("GET /api/desk -> 6 live cases", len(d["cases"]) == 6)
try:
    call("/api/hijack", {"scenario": "nope", "ticket": "x"}); ok("rejects an unknown scenario", False)
except urllib.error.HTTPError as e:
    ok("rejects an unknown scenario", e.code == 400)
sys.exit(1 if fails else 0)
PYEOF

echo "== 3/3 headless page render"
CHROME=""
for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" "$(command -v google-chrome || true)" "$(command -v chromium || true)"; do
  [ -n "$c" ] && [ -x "$c" ] && CHROME="$c" && break
done
render() {  # url -> rendered DOM (Chrome writes it, then may linger: poll the file, then stop Chrome)
  local prof out cpid
  prof=$(mktemp -d); out=$(mktemp)
  "$CHROME" --headless --disable-gpu --no-first-run --no-default-browser-check --user-data-dir="$prof" \
    --virtual-time-budget=10000 --dump-dom "$1" > "$out" 2>/dev/null &
  cpid=$!
  for _ in $(seq 1 120); do grep -q "</html>" "$out" 2>/dev/null && break; kill -0 $cpid 2>/dev/null || break; sleep 0.5; done
  kill $cpid 2>/dev/null || true
  wait $cpid 2>/dev/null || true
  cat "$out"; rm -rf "$prof" "$out" 2>/dev/null || true
}
if [ -n "$CHROME" ]; then
  DOM=$(render "$URL/#1")
  if grep -q "61/120" <<< "$DOM" && grep -q "✓ identical" <<< "$DOM"; then echo "PASS  page renders screen 1 (claim 61/120; live Tier 0 identical to committed)"; else echo "FAIL  page render screen 1"; FAIL=1; fi
  DOM=$(render "$URL/#3")
  if grep -q "300/300 decisions and reasons identical" <<< "$DOM"; then echo "PASS  page renders screen 3 (live sweep 300/300 identical to committed)"; else echo "FAIL  page render screen 3"; FAIL=1; fi
else
  echo "WARN  no Chrome found; page render not checked"
fi
[ $FAIL -eq 0 ] && echo "SMOKE: ALL PASS" || { echo "SMOKE: FAILURES"; exit 1; }
