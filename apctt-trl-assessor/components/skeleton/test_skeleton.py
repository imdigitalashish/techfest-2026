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
        assert doc["sections"][0]["text"][e["char_start"]:e["char_end"]] == e["quote"]


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
            sup = {c["level"] for c in a["gap_analysis"]["criteria"] if c["status"] == "supported"}
            assert not any(m["criterion_id"].startswith(f"L{l}_") for m in a["gap_analysis"]["missing_for_next_level"] for l in sup)
            if name == "syn_empty.txt":
                assert a["decision"]["abstain"] and a["error"] and a["distribution"]["model_id"].endswith(":prior")
                assert a["gap_analysis"]["next_level"] is None and not a["gap_analysis"]["missing_for_next_level"]



def _dist(trl_probs):
    p = np.asarray(trl_probs, dtype=float); p = p / p.sum()
    return {"p": list(p), "p_gt": list(1 - np.cumsum(p)[:-1]), "model_id": "t"}


def test_gap_is_evidence_led():
    doc = {"sections": [{"section_id": "s0", "heading": "", "text":
           "The breadboard was validated in the laboratory. The unit has not yet been qualified."}]}
    ev = evidence.extract(doc)
    dist = _dist([1, 1, 2, 6, 2, 1, 1, 1, 1])
    dec = decode.decide(dist, "median", n_chars=500)
    g = gap.analyse(dec, dist, ev)
    st = {c["level"]: c["status"] for c in g["criteria"]}
    assert st[4] == "supported" and st[8] == "contradicted" and st[2] == "not_evidenced", st
    assert all(0 <= c["model_p_ge"] <= 1 for c in g["criteria"])
    # next level (5) is not supported -> listed once, with actions to REACH level 5
    assert [m["criterion_id"] for m in g["missing_for_next_level"]] == ["L5_relevant_env_validation"]
    assert "relevant" in g["missing_for_next_level"][0]["suggested_actions"][0]
    ab = gap.analyse(decode.decide(dist, "median", n_chars=0), dist, ev)
    assert ab["next_level"] is None and all(c["status"] == "not_evidenced" for c in ab["criteria"])


def test_decode_rejects_unknown_rule():
    try:
        decode.decide(_dist([1] * 9), "thresholds")
    except ValueError:
        return
    raise AssertionError("unknown rule must raise")


def test_validator_fail_closed_on_unknown_keyword():
    try:
        emit.validate("abc", {"type": "string", "pattern": "^x"}, {})
    except NotImplementedError:
        return
    raise AssertionError("unsupported keyword must raise")


def test_docx_parse_stdlib():
    import zipfile
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "a.docx"
        with zipfile.ZipFile(p, "w") as z:
            z.writestr("word/document.xml", "<w:document><w:body><w:p><w:r><w:t>Prototype validated in the laboratory.</w:t></w:r></w:p>"
                       "<w:p><w:r><w:t>Second paragraph.</w:t></w:r></w:p></w:body></w:document>")
        d = ingest.parse(p)
        assert d["parser"] == "docx-xml" and len(d["sections"]) == 2 and "laboratory" in d["sections"][0]["text"]


def test_runner_isolates_failures():
    if not ordinal.DEFAULT_MODEL.exists():
        return
    model, schema = ordinal.Model(), emit.load_schema()
    orig = evidence.extract
    evidence.extract = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
    try:
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "x.txt"; f.write_text("Some text " * 50)
            a = runner.assess_safe(f, model, "median", schema, timeout_s=5)
    finally:
        evidence.extract = orig
    assert a["error"].startswith("RuntimeError") and a["decision"]["abstain"] and not emit.check_assessment(a, schema)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for f in fns:
        f(); print("PASS", f.__name__)
    print(f"{len(fns)} tests passed")
