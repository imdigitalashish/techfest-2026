#!/usr/bin/env bash
# Headless smoke test for the Poshan Setu demo. Exits non-zero on any failure.
#   1. data file vs committed eval/results and REAL source files      (python3, stdlib only)
#   2. the page's ledger.js reproduces Python's audit-ledger hashes    (node)
#   3. no external URL / network call in the page's code or data       (grep)
#   4. exporter re-derivation: re-runs the committed linkage cell, the gap/district sections and the
#      Python ledger verdicts against demo_data.js                     (project .venv)
#   5. headless page load from file://, key values on screen           (Python Playwright; skipped if absent)
# Usage (from anywhere): india71-t1-nutrition/demo/smoke.sh
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 2
fail=0
step() { printf '\n== %s\n' "$*"; }

step "1/5 data file invariants (demo/check_data.py)"
python3 demo/check_data.py || fail=1

step "2/5 ledger parity: page JS == Python (node demo/js/check_ledger.cjs)"
NODE="$(command -v node || echo /opt/homebrew/bin/node)"
if [ -x "$NODE" ]; then "$NODE" demo/js/check_ledger.cjs | tail -n 4 || fail=1
else echo "  FAIL node not found"; fail=1; fi

step "3/5 offline: no external URLs or network APIs"
hits="$(grep -nE 'https?://|//cdn\.|@import|fetch\(|XMLHttpRequest|WebSocket|EventSource|navigator\.sendBeacon' demo/index.html demo/js/*.js demo/data/demo_data.js || true)"
if [ -n "$hits" ]; then echo "  FAIL"; echo "$hits"; fail=1; else echo "  ok   index.html, js/*.js and data/demo_data.js reference nothing outside the folder"; fi

step "4/5 exporter re-derivation (.venv/bin/python -m demo.export --check)"
if [ -x .venv/bin/python ]; then .venv/bin/python -m demo.export --check || fail=1
else echo "  FAIL .venv missing: uv venv .venv --python 3.11 && uv pip install --python .venv/bin/python -r requirements.txt"; fail=1; fi

step "5/5 headless page load (demo/check_page.py)"
if python3 -c "import playwright" 2>/dev/null; then python3 demo/check_page.py || fail=1
else echo "  SKIP Python Playwright not installed (python3 -m pip install -r demo/requirements-demo.txt)"; fi

echo
if [ "$fail" -eq 0 ]; then echo "SMOKE: PASS"; else echo "SMOKE: FAIL"; fi
exit "$fail"
