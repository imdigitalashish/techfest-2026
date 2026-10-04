#!/usr/bin/env bash
# Regenerate everything derived from the inputs, in order. Run after ANY change to components/lca_engine, data or eval,
# commit the inputs first so the inputs id is clean, then commit the regenerated outputs.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest components/lca_engine/tests -q -p no:cacheprovider --deselect components/lca_engine/tests/test_contracts.py::test_docs_do_not_drift_from_results
python3 eval/eval.py
python3 eval/render_docs.py
python3 components/dashboard/build.py
python3 eval/check_docs.py
