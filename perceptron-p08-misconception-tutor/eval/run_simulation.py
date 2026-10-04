"""Stretch-goal eval (SYNTHETIC learners): does targeted practice reduce the targeted error types?

Run:  .venv/bin/python -m eval.run_simulation --seeds 3 --learners 150
Out:  eval/results/simulation.json
2x2 factorial + oracle: item selection {uniform random, EIG diagnose-then-target (ours)} x feedback
{generic "the answer is X", names the diagnosed misconception}. Learners are programs holding
executable misconceptions (components/simulator); their learning rates are ASSUMPTIONS, swept in
two settings. Metrics per session: share of initially-held misconceptions still held (ground truth),
expected error rate on those misconception types, and tracer diagnosis accuracy (MAP set == truth).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import random
import statistics
import time

from architecture.contracts import DiagnosisRequest, NextItemRequest
from components.bugs.school_math import SchoolMathBugs
from components.diagnoser import BugBayesDiagnoser
from components.generator import TemplateGenerator, item_bank
from components.learner_model import SetBayesTracer
from components.policy import EIGPolicy, OraclePolicy, RandomPolicy
from components.simulator import sample_population

OUT = pathlib.Path(__file__).parent / "results"
LIB = SchoolMathBugs()
ARMS = {  # name: (selection, feedback names the misconception?)
    "random+generic": ("random", False),
    "random+named": ("random", True),
    "eig+generic": ("eig", False),
    "eig+named (ours)": ("eig", True),
    "oracle+named": ("oracle", True),
}


def run_arm(arm: str, seed: int, n: int, S: int, T: int, pool, setting: dict) -> list[dict]:
    sel, named = ARMS[arm]
    learners = sample_population(n, seed, LIB.ids(), LIB, **setting)
    truth = {lr.learner_id: lr for lr in learners}
    tracer, gen, diag = SetBayesTracer(LIB), TemplateGenerator(), BugBayesDiagnoser()
    policy = {"random": lambda: RandomPolicy(pool, seed), "eig": lambda: EIGPolicy(tracer, gen, pool, seed=seed),
              "oracle": lambda: OraclePolicy(gen, lambda lid: truth[lid].holds(), seed)}[sel]()
    rng = random.Random(f"{arm}|{seed}")
    out = []
    for lr in learners:
        init = set(lr.held)
        state = tracer.init_state(lr.learner_id)
        rec = {"n_init": len(init), "remaining": [], "err": [], "diag_ok": []}
        for s in range(S):
            if s:
                lr.new_session(rng)
            state = tracer.start_session(state, f"s{s}")
            for _ in range(T):
                g = policy.next_item(NextItemRequest(state=state)).item
                resp = lr.answer(g.item, g.predicted, rng, f"s{s}")
                prior = {m: max(1e-3, b.p_holds) for m, b in state.beliefs.items()}
                d = diag.diagnose(DiagnosisRequest(item=g.item, response=resp, predicted=g.predicted, prior=prior))
                state = tracer.update(state, g.item, resp, d, g.predicted)
                lr.receive_feedback(g.item, d, targeted=named, rng=rng)
            held = lr.holds()
            rec["remaining"].append(len(held & init) / len(init))
            rec["err"].append(statistics.mean(lr.consistency if m in held else lr.slip for m in init))
            rec["diag_ok"].append(tracer.map_set(state) == held)
        out.append(rec)
    return out


def summarise(recs: list[dict], S: int) -> dict:
    res = {}
    for key in ("remaining", "err", "diag_ok"):
        per = []
        for s in range(S):
            xs = [float(r[key][s]) for r in recs]
            mu = statistics.mean(xs)
            se = statistics.pstdev(xs) / len(xs) ** 0.5
            per.append([round(mu, 4), round(1.96 * se, 4)])
        res[key] = per
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--learners", type=int, default=150)
    ap.add_argument("--sessions", type=int, default=4)
    ap.add_argument("--items", type=int, default=8)
    a = ap.parse_args()
    pool = item_bank(300, seed=7)
    settings = {
        "main (targeted feedback 0.30, generic 0.10)": {"p_learn_targeted": 0.3, "p_learn_generic": 0.1},
        "pessimistic (named feedback no better: 0.10/0.10)": {"p_learn_targeted": 0.1, "p_learn_generic": 0.1},
    }
    res = {"command": f"python -m eval.run_simulation --seeds {a.seeds} --learners {a.learners} --sessions {a.sessions} --items {a.items}",
           "label": "SYNTHETIC learners; learning/relapse rates are assumptions", "settings": {}}
    t0 = time.time()
    for sname, setting in settings.items():
        res["settings"][sname] = {}
        for arm in ARMS:
            recs = []
            for seed in range(a.seeds):
                recs += run_arm(arm, seed, a.learners, a.sessions, a.items, pool, setting)
            res["settings"][sname][arm] = summarise(recs, a.sessions)
            r = res["settings"][sname][arm]
            print(f"{sname[:12]:12s} | {arm:18s} | remaining {r['remaining'][-1]} | err {r['err'][-1]} | diag {r['diag_ok'][-1]} | {time.time() - t0:.0f}s", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "simulation.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
