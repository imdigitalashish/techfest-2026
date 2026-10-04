"""Contract tests: every component accepts and returns the typed contracts, plus core invariants."""
from __future__ import annotations

import random

from architecture.contracts import (
    Diagnosis, DiagnosisRequest, GeneratedItem, GenerationRequest, LearnerState, NextItemDecision, NextItemRequest,
    Response, VerificationReport,
)
from architecture.contracts import interfaces as I
from components.bugs.school_math import SchoolMathBugs, build_item, evaluate, mid, parse_dsl, canon
from components.diagnoser import BugBayesDiagnoser
from components.generator import TemplateGenerator, item_bank
from components.learner_model import SetBayesTracer
from components.normalizer import NORMALIZER
from components.policy import EIGPolicy
from components.simulator import sample_population
from components.verifier import SympyVerifier

LIB = SchoolMathBugs()


def test_protocols():
    assert isinstance(LIB, I.BugLibrary) and isinstance(LIB, I.ComposableBugLibrary)
    assert isinstance(SympyVerifier(), I.Verifier)
    assert isinstance(TemplateGenerator(), I.Generator)
    assert isinstance(BugBayesDiagnoser(), I.Diagnoser)
    assert isinstance(NORMALIZER, I.Normalizer)
    assert isinstance(SetBayesTracer(LIB), I.LearnerModel)


def test_bugs_reproduce_textbook_errors():
    cases = {
        "1/2 + 1/3": ("5/6", {"FRAC_ADD": "2/5"}),
        "7 − (−3)": ("10", {"SUB_NEG": "4"}),
        "2 + 3 × 4": ("14", {"LTR": "20"}),
        "5²": ("25", {"SQ_DOUBLE": "10"}),
        "(−3) × (−4)": ("12", {"NEG_TIMES_NEG": "-12"}),
        "(−3)²": ("9", {"NEG_TIMES_NEG": "-9", "SQ_DOUBLE": "-6"}),
    }
    for expr, (key, bugs) in cases.items():
        toks = parse_dsl(expr)
        assert canon(evaluate(toks)) == key, expr
        for code, wrong in bugs.items():
            assert canon(evaluate(toks, [code])) == wrong, (expr, code)


def test_generator_contract_and_verification():
    gen = TemplateGenerator()
    for code in ["LTR", "SQ_DOUBLE", "SUB_NEG", "FRAC_ADD", "NEG_TIMES_NEG"]:
        out = gen.generate(GenerationRequest(target_misconception_id=mid(code), n=3, seed=1))
        assert len(out) == 3
        for g in out:
            assert isinstance(g, GeneratedItem) and isinstance(g.verification, VerificationReport)
            assert g.verification.passed and g.verification.key_method == "sympy"
            assert any(p.misconception_id == mid(code) and p.value not in (None, g.item.answer_key) for p in g.predicted)


def test_discriminative_generation():
    gen = TemplateGenerator()
    comps = [mid("SQ_DOUBLE"), mid("SUB_NEG")]
    out = gen.generate(GenerationRequest(target_misconception_id=mid("LTR"), competitor_ids=comps, n=5, seed=3))
    for g in out:
        vals = [p.value for p in g.predicted if p.value is not None]
        assert len(vals) == len(set(vals)) and g.item.answer_key not in vals


def test_verifier_catches_wrong_key():
    g = TemplateGenerator().generate(GenerationRequest(target_misconception_id=mid("FRAC_ADD"), n=1, seed=5))[0]
    bad = g.item.model_copy(update={"answer_key": "999", "options": []})
    rep = SympyVerifier().verify(bad, g.predicted)
    assert not rep.key_verified and not rep.passed


def test_diagnoser_contract():
    g = TemplateGenerator().generate(GenerationRequest(target_misconception_id=mid("SUB_NEG"), n=1, seed=7))[0]
    wrong = next(p.value for p in g.predicted if p.misconception_id == mid("SUB_NEG"))
    d = BugBayesDiagnoser().diagnose(DiagnosisRequest(item=g.item, predicted=g.predicted,
                                                      response=Response(learner_id="t", session_id="s", item_id=g.item.item_id, answer_raw=wrong)))
    assert isinstance(d, Diagnosis) and not d.is_correct
    assert d.hypotheses[0].misconception_id == mid("SUB_NEG")
    assert abs(sum(h.prob for h in d.hypotheses) + d.p_slip - 1) < 1e-9


def test_tracer_and_policy_contract():
    tracer = SetBayesTracer(LIB)
    st = tracer.start_session(tracer.init_state("t"), "s1")
    assert isinstance(st, LearnerState) and abs(sum(st.model_state["joint"]) - 1) < 1e-9
    pool = item_bank(20, seed=1)
    dec = EIGPolicy(tracer, TemplateGenerator(), pool).next_item(NextItemRequest(state=st))
    assert isinstance(dec, NextItemDecision) and dec.expected_info_gain is not None
    learner = sample_population(1, 0, LIB.ids(), LIB)[0]
    rng = random.Random(0)
    resp = learner.answer(dec.item.item, dec.item.predicted, rng, "s1")
    st2 = tracer.update(st, dec.item.item, resp, None, dec.item.predicted)
    assert len(st2.history) == 1 and abs(sum(st2.model_state["joint"]) - 1) < 1e-6


def test_normalizer():
    for raw, val in [("5/6", "5/6"), (" -3 ", "-3"), ("−3", "-3"), ("0.5", "1/2"), ("x = 4", "4"), ("1 1/2", "3/2"), ("(-2)", "-2")]:
        assert NORMALIZER.normalize(raw).value == val, raw
    assert not NORMALIZER.normalize("banana").parse_ok
