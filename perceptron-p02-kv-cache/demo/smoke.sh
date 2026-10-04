#!/usr/bin/env bash
# Headless smoke test for the P2 demo (perceptron-p02-kv-cache/demo/smoke.sh). Exit 0 = every check ran and passed.
#  1. REPLAY: demo/web/replay.js equals a fresh export of the committed rows; its tables and verdicts equal
#     eval/RESULTS.md verbatim; every regenerated context matches its rows (export_replay.py --check).
#  2. PAGE: no external URLs (no CDN), the inline JS and replay.js parse, the server serves both, replay-only refuses live.
#  3. LIVE (SMOKE_LIVE=0 skips): plant a fact in a ~3k-token document, compress at 10%, ask. Asserts well-formed answers,
#     exact byte accounting, the full cache recalls the planted fact, and the X-ray scores pick RoD's recalled blocks
#     (RoD's own outcome is not asserted). Then re-runs committed T1 context 0 (Full, StreamingLLM, RoD at 10%/25%)
#     and requires the live engine to reproduce every committed row exactly (SMOKE_REPRO=0 skips; ~2 min).
# Live checks need demo/fetch.sh's data (run automatically if missing) and kern.memorystatus_level >= 30;
# under memory pressure they are skipped and the script exits 2.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
P="$(dirname "$HERE")"
cd "$P"
export HF_HUB_OFFLINE="${HF_HUB_OFFLINE:-1}"
ok() { echo "PASS  $*"; }
die() { echo "FAIL  $*" >&2; exit 1; }
T0=$(date +%s)

# ---- 1. replay export ----
[ -s .data/haystack.txt ] || python3 eval/fetch_haystack.py >/dev/null
python3 demo/export_replay.py --check || die "replay export does not match the committed rows / eval/RESULTS.md"
ok "replay export == committed rows and eval/RESULTS.md"

# ---- 2. page ----
if grep -Eiq '(src|href)="(https?:)?//|@import|fetch\("https?:|cdn\.' demo/web/index.html; then die "external URL in demo/web/index.html"; fi
ok "no external URLs in the page (no CDN; no third-party JS at all)"
if command -v node >/dev/null; then
  node -e '
const fs = require("fs"), h = fs.readFileSync("demo/web/index.html", "utf8");
new Function(h.split("<script>")[1].split("</script>")[0]);
const r = fs.readFileSync("demo/web/replay.js", "utf8"); new Function(r);
if (!r.startsWith("window.REPLAY={")) throw new Error("replay.js prefix");' || die "page JS does not parse"
  ok "inline page JS and replay.js parse (node)"
fi
python3 - "$HERE" <<'PY' || die "replay-only server checks"
import json, re, subprocess, sys, time, urllib.error, urllib.request
here = sys.argv[1]
srv = subprocess.Popen([sys.executable, f"{here}/server.py", "--port", "8650"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
try:
    url = re.search(r"DEMO_URL=(\S+)", srv.stdout.readline()).group(1)
    t = time.time(); page = urllib.request.urlopen(url, timeout=10).read().decode(); ms = (time.time() - t) * 1000
    assert "Recall-on-Demand" in page and urllib.request.urlopen(url + "replay.js", timeout=10).status == 200
    st = json.load(urllib.request.urlopen(url + "api/status", timeout=10))
    assert st["state"] == "off" and not st["allow"], st
    try:
        urllib.request.urlopen(urllib.request.Request(url + "api/compress", data=b"{}", method="POST"), timeout=10)
        raise AssertionError("replay-only server accepted a live request")
    except urllib.error.HTTPError as e:
        assert e.code == 503, e.code
    print(f"PASS  replay-only server: page + replay.js served ({ms:.0f} ms), live requests refused, no model loaded")
finally:
    srv.terminate(); srv.wait(10)
PY

# ---- 3. live ----
if [ "${SMOKE_LIVE:-1}" = 0 ]; then echo "SKIP  live checks (SMOKE_LIVE=0)"; echo "smoke: OK ($(( $(date +%s) - T0 )) s)"; exit 0; fi
python3 - "$HERE" <<'PY' || { echo "smoke: data missing; running demo/fetch.sh"; "$HERE/fetch.sh"; }
import sys; sys.path.insert(0, sys.argv[1]); import common; sys.exit(0 if common.data_ready()[0] else 1)
PY
LVL="$(sysctl -n kern.memorystatus_level 2>/dev/null || echo 100)"
if [ "$LVL" -lt "${DEMO_MEM_MIN:-30}" ]; then
  echo "SKIP  live checks: memory pressure (kern.memorystatus_level $LVL < ${DEMO_MEM_MIN:-30}); re-run when memory frees" >&2
  exit 2
fi
nice -n 10 python3 - "$HERE" <<'PY' || die "live checks"
import json, os, re, subprocess, sys, time, urllib.request
here = sys.argv[1]
srv = subprocess.Popen([sys.executable, f"{here}/server.py", "--port", "8660", "--live"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
def post(path, body):
    req = urllib.request.Request(url + path, data=json.dumps(body).encode(), method="POST", headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=900))
try:
    url = re.search(r"DEMO_URL=(\S+)", srv.stdout.readline()).group(1)
    st = json.load(urllib.request.urlopen(url + "api/status", timeout=10))
    assert st["state"] == "idle", st  # lazy: nothing loaded before the first live request
    D = st["defaults"]
    t = time.time(); c = post("api/compress", {"needle": D["needle"], "expected": D["expected"], "depth": D["depth"], "doc_seed": D["doc_seed"], "ctx_tokens": 3000, "budget": 0.10})
    t_c = time.time() - t
    T, PT, B = c["T"], c["per_tok"], c["B"]
    assert PT == 32768 and 2500 <= T <= 3200 and B == max(69, round(0.10 * T)), (T, B)
    assert c["full_bytes"] == T * PT and c["budget_bytes"] == B * PT
    for m in ("streaming", "h2o", "snapkv"):
        assert c["stored"][m] == B * PT, m
    for m, sk in (("rod", True), ("rodlex", False)):
        r = c[m]
        assert r["resident_bytes"] == r["B_res"] * PT and r["ids_bytes"] == 4 * T, m
        assert r["window_bytes"] == (262144 if sk else 0) and (r["sketch_bytes"] > 0) == sk, m
        assert r["stored_bytes"] == r["resident_bytes"] + r["sketch_bytes"] + r["window_bytes"] + r["ids_bytes"] == c["stored"][m], m
        assert r["stored_bytes"] <= c["budget_bytes"] and r["m"] == r["B_rec"] // 64 and r["ev1"] == T - (r["B_res"] - 4), m
    assert c["rod"]["m"] >= 1, "10% of a 3k-token document must leave RoD at least one recall block"
    print(f"PASS  live compress: T={T}, B={B}, bytes exact (full {T}x32 KiB; baselines B x 32 KiB; RoD resident+sketch+window+ids <= budget); {t_c:.1f} s incl. lazy model load")
    q = D["question"] + " Reply in a few words."
    t = time.time(); a = post("api/ask", {"question": q, "expected": D["expected"]}); t_a = time.time() - t
    ans = {x["method"]: x for x in a["answers"]}
    assert set(ans) == {"full", "streaming", "h2o", "snapkv", "rod", "rodlex"}
    for m, x in ans.items():
        assert isinstance(x["answer"], str) and x["answer"].strip(), (m, x)
        assert x["answer_time_bytes"] <= c["budget_bytes"] or m == "full", m
    assert ans["full"]["correct"], f"full cache did not recall the planted fact: {ans['full']['answer']!r}"
    for m in ("rod", "rodlex"):
        r, lay = a["rod"][m], c[m]
        blk = lambda k: min(64, lay["ev1"] - (4 + 64 * k))
        assert len(r["chosen"]) == min(lay["m"], lay["nblk"]) and r["recalled_bytes"] == sum(blk(k) for k in r["chosen"]) * PT, m
        assert ans[m]["answer_time_bytes"] == ans[m]["stored_bytes"] + r["recalled_bytes"], m
    h = a["rod"]["rod"]
    assert len(h["heat"]) == c["rod"]["nblk"] and h["consistent"] and h["heat_top"] == h["chosen"], "X-ray scores != RoD's recalled blocks"
    print(f"PASS  live ask ({t_a:.1f} s): 6 well-formed answers; full cache recalls the planted fact ({ans['full']['answer']!r}); "
          f"RoD/RoD-lexical answer-time bytes = stored + recalled blocks <= budget; X-ray top-{c['rod']['m']} == RoD's recalled blocks {h['chosen']}"
          f" [RoD said {ans['rod']['answer']!r}, not asserted]")
    b2 = post("api/budget", {"budget": 0.25})
    assert b2["B"] == round(0.25 * T) and b2["rod"]["m"] > c["rod"]["m"] and b2["rod"]["stored_bytes"] <= b2["budget_bytes"]
    print(f"PASS  budget knob 10% -> 25%: B {B} -> {b2['B']}, RoD recall blocks m {c['rod']['m']} -> {b2['rod']['m']}, no re-prefill")
    if os.environ.get("SMOKE_REPRO", "1") != "0":
        t = time.time(); r = post("api/reproduce", {"run": "T1_literal_s0", "sample": 0, "methods": ["full", "streaming", "rod"], "fracs": [0.1, 0.25]})
        bad = [x for x in r["rows"] if not x["same"]]
        assert r["n"] == 20 and not bad, bad
        print(f"PASS  live engine reproduces committed T1 context 0 exactly: {r['n_same']}/{r['n']} rows (answer, correctness, bytes, recalled blocks), {time.time() - t:.0f} s")
    st = post("api/unload", {})
    assert st["state"] == "idle"
    print("PASS  unload frees the model (state idle)")
finally:
    srv.terminate(); srv.wait(30)
PY
echo "smoke: OK ($(( $(date +%s) - T0 )) s)"
