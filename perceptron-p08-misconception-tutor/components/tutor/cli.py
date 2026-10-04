"""Tutor orchestrator (C11) + template feedback (C9): one end-to-end session, state persisted per learner.

Interactive:  .venv/bin/python -m components.tutor.cli --learner ashish --items 6
Scripted demo with a simulated learner holding given misconceptions (SYNTHETIC):
              .venv/bin/python -m components.tutor.cli --learner demo --simulate SUB_NEG,FRAC_ADD --items 8 --seed 1
State lives in .data/learners/<learner>.json (gitignored); rerun to start the next session.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
import sys

from architecture.contracts import DiagnosisRequest, LearnerState, NextItemRequest, Response
from components.bugs.school_math import SchoolMathBugs, code_of
from components.diagnoser import BugBayesDiagnoser
from components.generator import TemplateGenerator, item_bank
from components.learner_model import SetBayesTracer
from components.policy import EIGPolicy
from components.simulator import ProgramLearner

ROOT = pathlib.Path(__file__).resolve().parents[2]
STORE = ROOT / ".data" / "learners"


_YOU = {
    "LTR": "work strictly left to right, ignoring that × and ÷ come before + and −",
    "SQ_DOUBLE": "double the number instead of squaring it",
    "SUB_NEG": "treat subtracting a negative as subtracting a positive",
    "FRAC_ADD": "add the numerators and add the denominators",
    "NEG_TIMES_NEG": "make negative × negative negative",
}


def feedback(diag, item) -> str:
    if diag.is_correct:
        return "Correct."
    if diag.abstained or not diag.hypotheses:
        return f"Not quite — the answer is {item.answer_key}. Let's look at the steps together."
    code = code_of(diag.hypotheses[0].misconception_id)
    return (f"Not quite. Your answer is exactly what you get if you {_YOU[code]}. "
            f"Check that step: what does the rule really say? (Correct answer: {item.answer_key}.)")


def load(tracer: SetBayesTracer, learner: str) -> LearnerState:
    p = STORE / f"{learner}.json"
    return LearnerState.model_validate_json(p.read_text()) if p.exists() else tracer.init_state(learner)


def save(state: LearnerState) -> None:
    STORE.mkdir(parents=True, exist_ok=True)
    (STORE / f"{state.learner_id}.json").write_text(state.model_dump_json())


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--learner", required=True)
    ap.add_argument("--items", type=int, default=6)
    ap.add_argument("--simulate", default="", help="comma-separated pack codes the simulated learner holds")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)
    lib = SchoolMathBugs()
    tracer, diag = SetBayesTracer(lib), BugBayesDiagnoser()
    policy = EIGPolicy(tracer, TemplateGenerator(), item_bank(200, seed=7), seed=a.seed)
    state = load(tracer, a.learner)
    session = f"s{len(state.sessions) + 1}"
    state = tracer.start_session(state, session)
    rng = random.Random(a.seed)
    sim = None
    if a.simulate:
        held = {f"pack:{c.strip()}" for c in a.simulate.split(",") if c.strip()}
        sim = ProgramLearner(learner_id=a.learner, held=held, consistency=0.9, slip=0.05, library=lib)
        print(f"[simulated learner, SYNTHETIC] holds: {sorted(held)}")
    print(f"Session {session} for {a.learner}")
    for t in range(a.items):
        dec = policy.next_item(NextItemRequest(state=state))
        g = dec.item
        print(f"\nQ{t + 1} [{dec.mode}; EIG={dec.expected_info_gain or 0:.2f} nats] {g.item.stem}")
        if sim:
            resp = sim.answer(g.item, g.predicted, rng, session)
            print(f"  answer: {resp.answer_raw}")
        else:
            raw = input("  your answer: ")
            resp = Response(learner_id=a.learner, session_id=session, item_id=g.item.item_id, answer_raw=raw)
        prior = {m: max(1e-3, b.p_holds) for m, b in state.beliefs.items()}
        d = diag.diagnose(DiagnosisRequest(item=g.item, response=resp, predicted=g.predicted, prior=prior))
        state = tracer.update(state, g.item, resp, d, g.predicted)
        if sim:
            sim.receive_feedback(g.item, d, targeted=True, rng=rng)
        print("  " + feedback(d, g.item))
        if not d.is_correct and d.hypotheses:
            print("  diagnosis: " + ", ".join(f"{code_of(h.misconception_id)} {h.prob:.2f}" for h in d.hypotheses[:3])
                  + f", slip {d.p_slip:.2f}")
        top = sorted(state.beliefs.values(), key=lambda b: -b.p_holds)[:3]
        print("  beliefs: " + ", ".join(f"{code_of(b.misconception_id)} {b.p_holds:.2f}" for b in top))
    save(state)
    print(f"\nSaved {STORE / (a.learner + '.json')} — sessions so far: {state.sessions}")
    if sim:
        print(json.dumps({"truth_still_held": sorted(sim.holds()), "tracer_map_set": sorted(tracer.map_set(state))}))


if __name__ == "__main__":
    main(sys.argv[1:])
