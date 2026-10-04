"""C5 policy engine implements the governance matrix and its audit log detects tampering."""
import runpy
import json
import pathlib


def test_policy_engine_scenarios_and_tamper():
    root = pathlib.Path(__file__).resolve().parents[1]
    runpy.run_path(str(root / "eval" / "policy_engine_eval.py"))
    r = json.loads((root / "eval" / "results" / "policy_engine.json").read_text())
    assert r["correct"] == r["n_scenarios"] and r["false_allows"] == 0
    assert r["mutations_detected"] == r["n_mutations"]
