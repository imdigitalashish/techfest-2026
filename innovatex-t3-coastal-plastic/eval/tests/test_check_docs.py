"""Adversarial tests for eval/check_docs.py (review gpt-6-sol #5): each case must be caught, or must pass, as stated.

Run: cd innovatex-t3-coastal-plastic && python3 -m pytest eval/tests -q
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_docs as cd  # noqa: E402

ROWS = {"F01": "| 5 million kg/yr | https://example.org | 15,000 t quoted |",
        "F02": "| ₹14.5 crore for 2 years at 6 sites | https://example.org |",
        "F03": "| 9 booms with conveyors, 1.5 t/day | https://example.org |"}


def test_substring_number_does_not_match_a_longer_token():
    assert cd.check_binding("t.md", "{{f:F01|5,000 t}}", ROWS)  # '5,000' is not a whole token of '15,000'
    assert not cd.check_binding("t.md", "{{f:F01|15,000 t}}", ROWS)


def test_rupee_and_small_numbers_in_fact_text_are_checked():
    assert cd.check_binding("t.md", "{{f:F02|₹15.5 crore}}", ROWS)
    assert cd.check_binding("t.md", "{{f:F02|₹14.5 crore for 3 years}}", ROWS)
    assert not cd.check_binding("t.md", "{{f:F02|₹14.5 crore for 2 years at 6 sites}}", ROWS)


def test_unknown_alias_and_fact_id_are_caught():
    assert cd.check_binding("t.md", "{{r:no_such_alias}}", ROWS)
    assert cd.check_binding("t.md", "{{f:F99|anything}}", ROWS)


def test_malformed_or_unbalanced_placeholders_are_caught():
    assert cd.check_placeholders("t.md", "x {{ r:det_map50}} y")
    assert cd.check_placeholders("t.md", "x {{q:det_map50}} y")
    assert cd.check_placeholders("t.md", "x {{r:det_map50} y")
    assert cd.check_placeholders("t.md", "ok", rendered="left {{r:x}} behind")
    assert not cd.check_placeholders("t.md", "x {{r:det_map50}} and {{f:F01|5 million}}", rendered="x 0.857 and 5 million")


def test_unbound_small_quantities_and_numbers_are_caught():
    assert cd.check_unmarked("t.md", "BMC runs 9 booms today.")
    assert cd.check_unmarked("t.md", "Across 40 draws the plan wins.")
    assert cd.check_unmarked("t.md", "It captures 3 t per day.")
    assert cd.check_unmarked("t.md", "Recall was 71.6% in tests.")


def test_scoped_exceptions_still_pass():
    assert not cd.check_unmarked("t.md", "{{f:F03|9 booms}} with a 24 h forecast, crews 08:30–16:30, Theme 3, in 2026.")
    assert not cd.check_unmarked("t.md", "a central 90% scenario range; see https://x.org/a/123.45")
    assert not cd.check_unmarked("t.md", "UNVERIFIED: maybe 12 booms")
    assert not cd.check_unmarked("t.md", "Use 1 crew; data CC BY 4.0")
