#!/usr/bin/env bash
# Build the Round-1 package: render templates, draw figures, export deck (PDF + PPTX) and presenter card, then check.
# Usage: bash innovatex-t3-coastal-plastic/deliverables/build.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$HERE")"
MARP="${MARP:-$HOME/.npm/_npx/e4e1ce22f3be2d81/node_modules/@marp-team/marp-cli/marp-cli.js}"  # marp-cli 4.5.1
export CHROME_PATH="${CHROME_PATH:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"

python3 "$ROOT/eval/render_docs.py"
python3 "$HERE/make_figures.py"
cd "$HERE"
nice -n 10 node "$MARP" zonal-deck.md --allow-local-files --pdf -o zonal-deck.pdf
nice -n 10 node "$MARP" zonal-deck.md --allow-local-files --pptx -o zonal-deck.pptx
python3 "$HERE/make_presenter_card.py"
python3 "$ROOT/eval/export_manifest.py"
python3 "$ROOT/eval/collect_results.py"
python3 "$ROOT/eval/check_docs.py"
