"""Quoted numbers in the deliverables must match committed results (see eval/check_docs.py)."""
from eval import check_docs


def test_abstract_numbers_match_results():
    assert check_docs.main() == 0
