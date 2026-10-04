#!/usr/bin/env bash
# Headless smoke test for the Ghost Market demo:  perceptron-p05-impact-execution/demo/smoke.sh
# 1-4. demo/smoke_check.py: data loads (<5 MB, no CDN), key numbers == eval/results/claims.json, exported T1 gaps
#      == committed E7/E4/E8 CSV rows, recomputed means/slope/stds == committed results.
# 5.   run.sh with DEMO_NO_OPEN=1 prints READY within 60 s and serves the page and data.
# 6.   If the live lane is available: one live run (seed 101, 4,000 shares) returns pre-trade identity true and
#      reproduces the committed E7/E8 rows; skipped with a message when the memory guard trips.
set -euo pipefail
cd "$(dirname "$0")"
PY=../.venv/bin/python
[ -x "$PY" ] || PY=python3
fail() { echo "  FAIL $*"; exit 1; }

echo "== 1-4. data, key numbers, integrity, recomputed statistics"
"$PY" smoke_check.py

echo "== 5. run.sh: time to first visual"
LOG="$(mktemp -t p5smoke.XXXXXX)"
T0=$("$PY" -c 'import time; print(time.time())')
DEMO_NO_OPEN=1 DEMO_PORT="${SMOKE_PORT:-8670}" ./run.sh >"$LOG" 2>&1 &
RPID=$!
trap 'kill $RPID 2>/dev/null || true; rm -f "$LOG" "$LOG.json" "$LOG.html"' EXIT
for _ in $(seq 1 600); do grep -q '^READY: ' "$LOG" && break; sleep 0.1; done
URL="$(sed -n 's/^READY: //p' "$LOG" | head -1)"
EL=$("$PY" -c "import time; print(f'{time.time() - $T0:.1f}')")
[ -n "$URL" ] || fail "run.sh printed no READY line within 60 s"
"$PY" -c "import sys; sys.exit(0 if $EL <= 60 else 1)" || fail "READY after ${EL}s (> 60 s)"
echo "  ok   READY in ${EL}s: $URL"
case "$URL" in http*) ;; *) echo "  skip server checks: static mode"; echo "SMOKE PASSED"; exit 0 ;; esac
curl -fsS -o "$LOG.html" "$URL" && grep -q 'SIMULATED (ABIDES' "$LOG.html" || fail "page not served"
curl -fsS -o "$LOG.html" "${URL}data/summary.js" && grep -q '^window.P5 = ' "$LOG.html" || fail "data not served"
echo "  ok   page and data served with the SIMULATED (ABIDES) label"

echo "== 6. live lane"
S=""
for _ in $(seq 1 60); do
  S="$(curl -fsS "${URL}api/status" || true)"
  case "$S" in *warming*) sleep 0.5 ;; *) break ;; esac
done
case "$S" in
  *'"live":true'*)
    if printf '%s' "$S" | grep -q '"paused":true'; then echo "  skip live run: live paused (memory guard)"; echo "SMOKE PASSED"; exit 0; fi
    T1=$("$PY" -c 'import time; print(time.time())')
    curl -fsS --max-time 120 "${URL}api/run?seed=101&qty=4000" >"$LOG.json" || fail "live run request failed"
    "$PY" - "$LOG.json" "$T1" <<'EOF' || exit 1
import csv, json, sys, time
j = json.load(open(sys.argv[1]))
if j.get("paused"):
    print("  skip live run: live paused (memory guard)"); sys.exit(0)
row = lambda f, lab: next(r for r in csv.DictReader(open("../eval/results/" + f)) if r["seed"] == "101" and r["label"] == lab)
tw, ia = j["worlds"]["twap"]["stats"], j["worlds"]["ia"]["stats"]
ok = tw["ident_ok"] and ia["ident_ok"] and tw["top1_exact"] and ia["top1_exact"]
ok &= tw["t1"] == float(row("E7_size_q4000.csv", "TWAP")["impact_end_cents"])
ok &= ia["t1"] == float(row("E8_ablation_val.csv", "IA_sched_only")["impact_end_cents"])
print(f"  {'ok  ' if ok else 'FAIL'} live seed 101 in {time.time() - float(sys.argv[2]):.1f}s: pre-trade top-5 identity "
      f"{tw['ident'][0]}/{tw['ident'][1]} (TWAP) {ia['ident'][0]}/{ia['ident'][1]} (IA); T1 gaps {tw['t1']:+.1f}c / {ia['t1']:+.1f}c "
      f"== E7_size_q4000.csv / E8_ablation_val.csv")
sys.exit(0 if ok else 1)
EOF
    ;;
  *) echo "  skip live run: $(printf '%s' "$S" | sed -n 's/.*"reason":"\([^"]*\)".*/\1/p')" ;;
esac
echo "SMOKE PASSED"
