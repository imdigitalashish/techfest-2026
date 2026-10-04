"""Set-Bayes misconception tracer (spike #2).

Exact Bayesian filter over *sets* of held misconceptions (2^K states for a K-misconception
pack). Emission: a learner holding set H answers an item with the composite buggy answer
(all held bugs that fire, applied together) with probability c; otherwise correctly with
probability 1-s, or with a non-systematic slip. Between sessions each misconception
independently remits (r) or is (re)acquired (a). This is BKT generalised from one binary
skill to a set of interacting, executable bugs.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import numpy as np

from architecture.contracts import (
    Diagnosis, Item, LearnerState, MisconceptionBelief, Observation, PredictedAnswer, Response,
)
from components.normalizer import NORMALIZER


class SetBayesTracer:
    def __init__(self, library, ids: Optional[list[str]] = None, consistency: float = 0.8, slip: float = 0.1,
                 eps: float = 0.02, base_rate: float = 0.3, p_remit: float = 0.03, p_acquire: float = 0.01):
        self.library = library
        self.ids = list(ids or library.ids())
        self.K = len(self.ids)
        self.N = 1 << self.K
        self.c, self.s, self.eps = consistency, slip, eps
        self.base_rate, self.r, self.a = base_rate, p_remit, p_acquire
        self.bits = np.array([[(m >> j) & 1 for j in range(self.K)] for m in range(self.N)], dtype=float)
        self._cache: dict[str, list[Optional[str]]] = {}

    def init_state(self, learner_id: str) -> LearnerState:
        b = self.base_rate
        joint = np.prod(np.where(self.bits == 1, b, 1 - b), axis=1)
        st = LearnerState(learner_id=learner_id, model_state={"ids": self.ids, "joint": joint.tolist()})
        return self._with_marginals(st, joint)

    def joint(self, state: LearnerState) -> np.ndarray:
        if not state.model_state.get("joint"):
            return np.asarray(self.init_state(state.learner_id).model_state["joint"])
        return np.asarray(state.model_state["joint"], dtype=float)

    def marginals(self, joint: np.ndarray) -> np.ndarray:
        return joint @ self.bits

    def _with_marginals(self, state: LearnerState, joint: np.ndarray, touched: Optional[set[str]] = None) -> LearnerState:
        now = datetime.now(timezone.utc)
        marg = self.marginals(joint)
        beliefs = dict(state.beliefs)
        for j, m in enumerate(self.ids):
            old = beliefs.get(m)
            n = (old.n_evidence if old else 0) + (1 if touched and m in touched else 0)
            beliefs[m] = MisconceptionBelief(misconception_id=m, p_holds=float(np.clip(marg[j], 0, 1)), n_evidence=n,
                                             last_updated=now if (touched and m in touched) else (old.last_updated if old else None))
        ms = dict(state.model_state)
        ms["joint"] = joint.tolist()
        ms["ids"] = self.ids
        return state.model_copy(update={"beliefs": beliefs, "model_state": ms})

    def map_set(self, state: LearnerState) -> set[str]:
        j = self.joint(state)
        best = int(np.argmax(j))
        return {m for k, m in enumerate(self.ids) if (best >> k) & 1}

    def mask_values(self, item: Item) -> list[Optional[str]]:
        hit = self._cache.get(item.item_id)
        if hit is not None:
            return hit
        vals: list[Optional[str]] = [None] * self.N
        for mask in range(1, self.N):
            held = [self.ids[j] for j in range(self.K) if (mask >> j) & 1]
            vals[mask] = self.library.predict_set(item, held)
        if len(self._cache) > 50000:
            self._cache.clear()
        self._cache[item.item_id] = vals
        return vals

    def likelihood(self, item: Item, value: Optional[str]) -> np.ndarray:
        vals = self.mask_values(item)
        is_key = value is not None and value == item.answer_key
        base = (1 - self.s) if is_key else self.s * self.eps
        out = np.full(self.N, base)
        for mask in range(1, self.N):
            y = vals[mask]
            if y is not None:
                out[mask] = self.c * (1.0 if value == y else 0.0) + (1 - self.c) * base
        return out

    def start_session(self, state: LearnerState, session_id: str) -> LearnerState:
        joint = self.joint(state)
        if state.sessions:  # transition only between sessions
            t = joint.reshape((2,) * self.K)
            for j in range(self.K):
                axis = self.K - 1 - j
                p0, p1 = np.take(t, 0, axis=axis), np.take(t, 1, axis=axis)
                n0 = (1 - self.a) * p0 + self.r * p1
                n1 = self.a * p0 + (1 - self.r) * p1
                t = np.stack([n0, n1], axis=axis)
            joint = t.reshape(-1)
        st = state.model_copy(update={"sessions": state.sessions + [session_id]})
        return self._with_marginals(st, joint)

    def update(self, state: LearnerState, item: Item, response: Response, diagnosis: Optional[Diagnosis],
               predicted: list[PredictedAnswer]) -> LearnerState:
        v = NORMALIZER.normalize(response.answer_raw, item).value
        joint = self.joint(state) * self.likelihood(item, v)
        z = joint.sum()
        joint = joint / z if z > 0 else self.joint(state)
        matched = [p.misconception_id for p in predicted if p.value is not None and p.value == v]
        touched = {p.misconception_id for p in predicted if p.value is not None}
        obs = Observation(item_id=item.item_id, session_id=response.session_id,
                          correct=(v == item.answer_key), answer_value=v, matched_misconceptions=matched)
        st = state.model_copy(update={"history": state.history + [obs]})
        return self._with_marginals(st, joint, touched)

    def eig(self, state: LearnerState, item: Item) -> float:
        """Mutual information (nats) between the next response and the held-misconception set."""
        joint = self.joint(state)
        vals = self.mask_values(item)
        outs = sorted({y for y in vals if y is not None})
        col = {y: i + 1 for i, y in enumerate(outs)}
        W = len(outs) + 2
        P = np.zeros((self.N, W))
        for mask in range(self.N):
            y = vals[mask]
            if y is not None:
                P[mask, col[y]] += self.c
                P[mask, 0] += (1 - self.c) * (1 - self.s)
                P[mask, W - 1] += (1 - self.c) * self.s
            else:
                P[mask, 0] = 1 - self.s
                P[mask, W - 1] = self.s
        pw = joint @ P
        with np.errstate(divide="ignore", invalid="ignore"):
            h_marg = -np.nansum(np.where(pw > 0, pw * np.log(pw), 0.0))
            h_cond = -np.nansum(joint[:, None] * np.where(P > 0, P * np.log(P), 0.0))
        return float(h_marg - h_cond)
