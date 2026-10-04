"""The proposal quotes only numbers that match committed results."""
from eval.check_docs import main


def test_docs_match_results():
    assert main() == 0
