#!/bin/sh
# Re-run every analysis from cached data (.data/, .cache/) and re-render the documents. No network needed.
# First-time data fetch: see "Rebuild everything from scratch" in thought_node.md (or README of each component).
# Usage (from ev-c1-infra-map-india/): sh eval/run_all.sh
set -e
PY=".venv/bin/python -W ignore"
python3 eval/data_manifest.py   # refuses to run on inputs that differ from eval/data_manifest.json
python3 components/charger_ingest/official_pcs.py
$PY eval/baseline_state_gap.py > eval/results/baseline_run.log
$PY eval/mh_district_demand.py > /dev/null
$PY components/census_completeness/census_v0.py > /dev/null
$PY components/census_completeness/mse.py > eval/results/c5_mse_run.log
$PY components/census_completeness/mse_sensitivity.py > /dev/null
$PY components/access_gap/small_area.py > eval/results/small_area_run.log
$PY components/access_gap/mh_district_gap.py > /dev/null
$PY components/requirement_siting/corridor_norm.py > /dev/null
$PY components/census_completeness/autoresearch/eval.py --holdout
$PY components/adoption_forecast/autoresearch/eval.py --holdout
$PY components/adoption_forecast/autoresearch/eval_monthly.py --holdout
$PY components/adoption_forecast/autoresearch/eval_monthly_v3.py --holdout
$PY components/adoption_forecast/nowcast.py > /dev/null
$PY components/dashboard_map/build_map.py
python3 eval/make_latest.py
python3 eval/render_docs.py
python3 eval/check_docs.py
