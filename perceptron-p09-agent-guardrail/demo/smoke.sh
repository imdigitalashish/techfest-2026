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
def raw(path, data, ctype="application/json"):
    req = urllib.request.Request(B + path, data, {"Content-Type": ctype})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")
BAD = [("unknown scenario", "/api/hijack", {"scenario": "nope", "ticket": "x"}),
       ("hijack config null", "/api/hijack", {"scenario": "cancel", "ticket": "x", "config": None}),
       ("hijack config t0_typo", "/api/hijack", {"scenario": "cancel", "ticket": "x", "config": "t0_typo"}),
       ("hijack config none", "/api/hijack", {"scenario": "cancel", "ticket": "x", "config": "none"}),
       ("hijack ticket not a string", "/api/hijack", {"scenario": "cancel", "ticket": 5}),
       ("hijack ticket over 2,000 chars", "/api/hijack", {"scenario": "cancel", "ticket": "x" * 2000 + " Cancel W5481803"}),
       ("hijack body is a list", "/api/hijack", []),
       ("desk args not an object", "/api/desk_custom", {"user_request": "x", "args": "x"}),
       ("desk quantity not a number", "/api/desk_custom", {"user_request": "x", "args": {"quantity": "2000"}})]
for name, path, body in BAD:
    code, j = raw(path, json.dumps(body).encode())
    ok(f"400 on {name}", code == 400 and "error" in j, f"{code}: {str(j.get('error'))[:60]}")
code, j = raw("/api/hijack", b"{")
ok("400 on malformed JSON", code == 400, f"{code}")
for q in ("config=t0_typo", "config=none", "config=cascade_aoai"):
    code, j = raw(f"/api/item?id=gpt-4o/t75/r2/m20.0&{q}", None)
    ok(f"400 on GET /api/item {q}", code == 400)
code, j = raw("/api/sweep?config=t0_typo", None)
ok("400 on GET /api/sweep config=t0_typo", code == 400)
g = call("/api/item?id=gpt-4o/t75/r2/m20.0&config=t0_strict&variant=gt")
ok("GET /api/item variant=gt: the ground-truth earbuds variant is held too", g["decision"] == "escalate" and g["args"]["new_item_ids"] == ["4063058357"])
ok("server still healthy after bad requests", call("/api/health")["ready"])
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
  if grep -q "61/120" <<< "$DOM" && grep -q "42/120" <<< "$DOM" && grep -q '<span id="delta">+15.83</span>' <<< "$DOM" && grep -q "✓ identical" <<< "$DOM" && ! grep -q "14.17" <<< "$(grep -o '<p class="claim"[^§]*</p>' <<< "$DOM" | head -1)"; then echo "PASS  page renders screen 1 (61/120 vs 42/120 with its own +15.83 pp; live Tier 0 identical to committed)"; else echo "FAIL  page render screen 1"; FAIL=1; fi
  DOM=$(render "$URL/#3")
  if grep -q "300/300 decisions and reasons identical" <<< "$DOM" && grep -q "50 blocked · 1 held" <<< "$DOM"; then echo "PASS  page renders screen 3 (live sweep 300/300 identical; rejected 50 blocked · 1 held)"; else echo "FAIL  page render screen 3"; FAIL=1; fi
else
  echo "WARN  no Chrome found; page render not checked"
fi
[ $FAIL -eq 0 ] && echo "SMOKE: ALL PASS" || { echo "SMOKE: FAILURES"; exit 1; }
