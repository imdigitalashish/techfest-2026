#!/usr/bin/env bash
# Poshan Setu demo (India@71, Theme 1): open the offline page. Needs no venv, no server and no network.
# Usage: demo/run.sh            (from india71-t1-nutrition/, or from anywhere)
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
page="$here/index.html"
if [ ! -f "$here/data/demo_data.js" ]; then
  echo "demo/data/demo_data.js is missing: regenerate it with the exporter (see demo/README.md)." >&2
  exit 1
fi
echo "Poshan Setu demo: $page"
echo "Keys: right/left arrow = next/previous screen, 1-7 = jump, on 'This week': +/- slots, r = reveal."
if [ "$(uname -s)" = "Darwin" ]; then
  open "$page"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$page" >/dev/null 2>&1 &
else
  echo "Open this file in any modern browser: $page"
fi
