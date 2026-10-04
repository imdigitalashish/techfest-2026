"""The illustrative impact estimate must use the cited catch figures exactly (F12) and keep its label."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_docs as cd  # noqa: E402
import impact_estimate as ie  # noqa: E402


def test_catch_figures_are_whole_tokens_of_fact_row_f12():
    row = cd.fact_rows()["F12"]
    have = cd.tokens(row)
    for v in ie.CATCH_T_PER_DAY:
        assert f"{v:g}" in have, f"{v} not in F12"


def test_committed_estimate_matches_a_fresh_run_and_is_labelled():
    committed = json.loads(ie.OUT.read_text())
    fresh = ie.main()
    assert committed == fresh
    assert committed["label"].startswith("ILLUSTRATIVE ESTIMATE")
