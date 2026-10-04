"""Next-item policies: EIG diagnose-then-remediate (ours), random practice, oracle targeting."""
from __future__ import annotations

import random
from typing import Optional

from architecture.contracts import GeneratedItem, GenerationRequest, NextItemDecision, NextItemRequest
from components.generator import TemplateGenerator


class EIGPolicy:
    def __init__(self, tracer, generator: TemplateGenerator, pool: list[GeneratedItem],
                 remediate_at: float = 0.75, n_candidates: int = 30, seed: int = 0):
        self.tracer, self.gen, self.pool = tracer, generator, pool
        self.remediate_at, self.n_candidates, self.seed = remediate_at, n_candidates, seed

    def _rng(self, req: NextItemRequest) -> random.Random:
        return random.Random(f"{self.seed}|{req.state.learner_id}|{len(req.state.history)}")

    def next_item(self, req: NextItemRequest) -> NextItemDecision:
        state, rng = req.state, self._rng(req)
        seen = {o.item_id for o in state.history}
        marg = {m: b.p_holds for m, b in state.beliefs.items()}
        top_m, top_p = max(marg.items(), key=lambda kv: kv[1])
        mode = req.mode
        if mode == "auto":
            mode = "remediate" if top_p >= self.remediate_at else "diagnose"
        if mode == "remediate":
            items = self.gen.generate(GenerationRequest(target_misconception_id=top_m, n=1, seed=rng.randrange(1 << 30),
                                                        as_mcq=False, exclude_item_ids=sorted(seen)))
            if items:
                return NextItemDecision(item=items[0], mode="remediate", expected_info_gain=self.tracer.eig(state, items[0].item),
                                        rationale=f"P({top_m})={top_p:.2f} >= {self.remediate_at}: targeted practice")
        cands = req.candidate_items or [g for g in rng.sample(self.pool, min(len(self.pool), self.n_candidates * 2))
                                        if g.item.item_id not in seen][: self.n_candidates]
        best: Optional[tuple[float, GeneratedItem]] = None
        for g in cands:
            e = self.tracer.eig(state, g.item)
            if best is None or e > best[0]:
                best = (e, g)
        assert best is not None, "empty candidate pool"
        return NextItemDecision(item=best[1], mode="diagnose", expected_info_gain=best[0],
                                rationale="maximum expected information gain about which misconceptions are held")


class RandomPolicy:
    def __init__(self, pool: list[GeneratedItem], seed: int = 0):
        self.pool, self.seed = pool, seed

    def next_item(self, req: NextItemRequest) -> NextItemDecision:
        rng = random.Random(f"{self.seed}|{req.state.learner_id}|{len(req.state.history)}")
        return NextItemDecision(item=rng.choice(self.pool), mode="diagnose", rationale="uniform random practice")


class OraclePolicy:
    """Upper bound: knows the learner's true misconceptions and practises one of them."""

    def __init__(self, generator: TemplateGenerator, truth_fn, seed: int = 0):
        self.gen, self.truth_fn, self.seed = generator, truth_fn, seed

    def next_item(self, req: NextItemRequest) -> NextItemDecision:
        rng = random.Random(f"{self.seed}|{req.state.learner_id}|{len(req.state.history)}")
        held = sorted(self.truth_fn(req.state.learner_id)) or sorted(req.state.beliefs)
        target = rng.choice(held)
        g = self.gen.generate(GenerationRequest(target_misconception_id=target, n=1, seed=rng.randrange(1 << 30), as_mcq=False))[0]
        return NextItemDecision(item=g, mode="remediate", rationale=f"oracle: learner holds {target}")
