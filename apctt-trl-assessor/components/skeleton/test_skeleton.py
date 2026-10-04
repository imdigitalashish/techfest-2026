"""Contract tests for the walking skeleton. Run from apctt-trl-assessor/:
    python -m components.skeleton.test_skeleton        (or: python -m pytest components/skeleton)
Synthetic inputs below are written by us for testing only (labelled SYNTHETIC); they are not evaluation data.
"""
from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path

import numpy as np

from . import decode, emit, evidence, gap, ingest, ordinal, runner

ROOT = Path(__file__).resolve().parents[2]
SYNTHETIC = {
    "syn_concept.txt": "A new concept for a membrane filter is formulated. A feasibility study of practical applications is planned.",
    "syn_lab.txt": "Abstract\n\nThe breadboard was validated in the laboratory. Components were integrated and tested together.\n\nReferences\n\n[1] x",
    "syn_flight.txt": "The instrument is flight proven after a successful mission. It is now commercially available.",
    "syn_empty.txt": "",
    "syn_nonenglish.txt": "Ce prototype a été démontré dans un environnement pertinent. 这是一个测试。",
    "syn_huge.txt": "The prototype was demonstrated in a relevant environment. " * 4000,
}


def test_rubric_loads():
    r = evidence.load_rubric()
    assert [lv["level"] for lv in r["levels"]] == list(range(1, 10))


def test_evidence_polarity_and_signal():
    doc = {"sections": [{"section_id": "s0", "heading": "", "text":
           "The prototype was demonstrated in a relevant environment. We will conduct a field test next year. "
           "The system has not yet been qualified."}]}
    ev = evidence.extract(doc)
    got = {(e["signal"], e["polarity"]) for e in ev}
    assert ("relevant_env_demo", "achieved") in got, got
    assert ("operational_prototype", "planned") in got, got
    assert ("qualified_system", "negated") in got, got
    for e in ev:  # offsets point at the quoted text
        assert doc["sections"][0]["text"][e["char_start"]:e["char_end"]].strip() == e["quote"]


def test_featurize_matches_eval_baseline():
    spec = importlib.util.spec_from_file_location("bn", ROOT / "eval" / "baseline_numpy.py")
    bn = importlib.util.module_from_spec(spec); spec.loader.exec_module(bn)
    t = ["Laboratory validation of a breadboard heat exchanger; flight test planned."]
    assert np.array_equal(bn.featurize(t, 512), ordinal.featurize(t, 512))


def test_validator_catches_errors():
    bad = {"doc_id": "x", "decision": {"trl": 10}}
    errs = emit.check_assessment(bad)
    assert any("missing" in e for e in errs) and any("> 9" in e for e in errs), errs


def test_decode_rules():
    p = [0.05, 0.1, 0.3, 0.3, 0.15, 0.05, 0.03, 0.01, 0.01]
    d = {"p": p, "p_gt": list(1 - np.cumsum(p)[:-1]), "model_id": "t"}
    assert decode.decide(d, "mode")["trl"] == 3
    assert decode.decide(d, "median")["trl"] == 4
    assert decode.decide(d, "expectation")["trl"] == 4
    lo, hi = decode.decide(d)["interval80"]
    assert lo <= 4 <= hi


def test_end_to_end_schema_valid():
    if not ordinal.DEFAULT_MODEL.exists():
        print("SKIP end-to-end: train first (python -m components.skeleton.runner --train)")
        return
    model, schema = ordinal.Model(), emit.load_schema()
    with tempfile.TemporaryDirectory() as td:
        for name, text in SYNTHETIC.items():
            (Path(td) / name).write_text(text)
        for name in SYNTHETIC:
            a = runner.assess(Path(td) / name, model, "median", schema)  # raises on any schema violation
            p = np.asarray(a["distribution"]["p"]); pg = np.asarray(a["distribution"]["p_gt"])
            assert abs(p.sum() - 1) < 1e-6 and np.all(np.diff(pg) <= 1e-9)
            assert a["gap_analysis"]["next_level"] in (None, a["decision"]["trl"] + 1)
            if name == "syn_empty.txt":
                assert a["decision"]["abstain"] and a["error"]


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for f in fns:
        f(); print("PASS", f.__name__)
    print(f"{len(fns)} tests passed")
