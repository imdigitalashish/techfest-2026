#!/usr/bin/env bash
# Clean-room dry run of the submission package: build -> fresh venv with pinned deps -> offline, timed batch
# -> schema check + sanity accuracy + licence list -> deliverables/dry_run_report.md
# Usage (from anywhere): bash apctt-trl-assessor/submission/dry_run.sh
set -euo pipefail
cd "$(dirname "$0")/.."
PY=$(command -v python3)
DIST=.data/dist/trl_assessor_v0
DR=.data/dryrun
"$PY" submission/build.py
rm -rf "$DR" && mkdir -p "$DR/in" "$DR/out"
"$PY" submission/make_dryrun_inputs.py "$DR/in"
uv venv -q -p "$PY" "$DR/venv"
t0=$(date +%s); uv pip install -q -p "$DR/venv/bin/python" -r "$DIST/requirements.txt"; t1=$(date +%s)
ABS_DR=$(cd "$DR" && pwd)
( cd "$DIST" && /usr/bin/time -l "$ABS_DR/venv/bin/python" run.py --in "$ABS_DR/in" --out "$ABS_DR/out" --offline \
    > "$ABS_DR/run.log" 2> "$ABS_DR/time.txt" )
"$PY" -m submission.report --dist "$DIST" --dryrun "$DR" --install-s $((t1 - t0)) > deliverables/dry_run_report.md
echo "report -> deliverables/dry_run_report.md"
