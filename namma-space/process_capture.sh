#!/usr/bin/env bash
# Drop-in: process a phone capture the moment it lands.
#   ./process_capture.sh <capture_folder> [name] [extra run_pipeline.py flags]
# <capture_folder> holds the original videos (.MOV/.mp4) and/or photos plus capture.json (deliverables/capture-sop.md §8).
# Output: .data/work/<name>/ (report.json, site/ = deployable viewer). Re-running resumes from the last finished stage.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
IN="$(cd "$1" && pwd)"; shift
NAME="${1:-$(basename "$IN")}"; [ $# -gt 0 ] && shift
cd "$HERE"
[ -x .venv/bin/python ] && [ -x .cache/brush/brush-app-aarch64-apple-darwin/brush_app ] || ./setup.sh
[ -f "$IN/capture.json" ] || echo "WARNING: no capture.json — scale falls back to an ASSUMED 1.5 m camera height"
nice -n 10 .venv/bin/python components/orchestrator/run_pipeline.py --input "$IN" --name "$NAME" "$@"
echo
echo "Next: view locally ->  cd .data/work/$NAME/site && python3 -m http.server 8080   (open http://127.0.0.1:8080/)"
echo "      tag POIs in the viewer (P), or deploy -> components/orchestrator/deploy_azure.sh .data/work/$NAME/site <storage-account-name>"
