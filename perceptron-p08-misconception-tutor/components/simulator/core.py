"""Simulated learners (SYNTHETIC) that hold executable misconceptions.

Assumptions (all parameters are explicit and swept in eval/run_simulation.py):
- A learner holding set H applies all firing held bugs together with probability `consistency`,
  otherwise answers correctly, or slips (non-systematic wrong answer) with probability `slip`.
- After a wrong answer caused by misconception m, feedback removes m with probability
  p_learn_targeted when the feedback names m, else p_learn_generic ("the answer is X").
- Remediated misconceptions relapse at the start of a later session with probability p_relapse.
These are modelling assumptions, not measured learning rates.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Optional

from architecture.contracts import Diagnosis, Item, PredictedAnswer, Response


@dataclass
class ProgramLearner:
    learner_id: str
    held: set[str]
    consistency: float
    slip: float
    library: object
    p_learn_targeted: float = 0.3
    p_learn_generic: float = 0.1
    p_relapse: float = 0.05
    remediated: set[str] = field(default_factory=set)
    _last: Optional[tuple[str, str, frozenset[str]]] = None

    def holds(self) -> set[str]:
        return set(self.held)

    def answer(self, item: Item, predicted: list[PredictedAnswer], rng: random.Random, session_id: str = "s0") -> Response:
        pv = {p.misconception_id: p.value for p in predicted}
        firing = sorted(m for m in self.held if pv.get(m) is not None)
        val: Optional[str] = None
        cause: frozenset[str] = frozenset()
        if firing and rng.random() < self.consistency:
            val = self.library.predict_set(item, firing)
            cause = frozenset(firing)
        if val is None:
            cause = frozenset()
            if rng.random() < self.slip:
                avoid = {v for v in pv.values() if v is not None} | {item.answer_key}
                key = Fraction(item.answer_key)
                for k in rng.sample(range(1, 8), 7):
                    cand = key + (k if rng.random() < 0.5 else -k)
                    s = str(cand.numerator) if cand.denominator == 1 else f"{cand.numerator}/{cand.denominator}"
                    if s not in avoid:
                        val = s
                        break
            if val is None:
                val = item.answer_key
        self._last = (item.item_id, val, cause)
        return Response(learner_id=self.learner_id, session_id=session_id, item_id=item.item_id, answer_raw=val)

    def receive_feedback(self, item: Item, diagnosis: Optional[Diagnosis], targeted: bool, rng: random.Random) -> None:
        if not self._last or self._last[0] != item.item_id or self._last[1] == item.answer_key:
            return
        named = diagnosis.hypotheses[0].misconception_id if (diagnosis and diagnosis.hypotheses) else None
        for m in sorted(self._last[2]):
            p = self.p_learn_targeted if (targeted and named == m) else self.p_learn_generic
            if m in self.held and rng.random() < p:
                self.held.discard(m)
                self.remediated.add(m)

    def new_session(self, rng: random.Random) -> None:
        for m in sorted(self.remediated):
            if rng.random() < self.p_relapse:
                self.held.add(m)
                self.remediated.discard(m)


def sample_population(n: int, seed: int, ids: list[str], library, base_rate: float = 0.35, single: bool = False,
                      **kw) -> list[ProgramLearner]:
    rng = random.Random(seed)
    out = []
    for i in range(n):
        if single:
            held = {rng.choice(ids)}
        else:
            held = {m for m in ids if rng.random() < base_rate} or {rng.choice(ids)}
        out.append(ProgramLearner(learner_id=f"sim-{seed}-{i}", held=held, consistency=rng.betavariate(8, 2),
                                  slip=rng.uniform(0.03, 0.15), library=library, **kw))
    return out
