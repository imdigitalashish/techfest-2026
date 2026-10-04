"""Diagnosers.

- BugBayesDiagnoser (spike): exact likelihood of the observed answer under each executable
  misconception, plus a 'slip' hypothesis for non-systematic errors.
- LLMClassifierDiagnoser (baseline): zero-shot LLM picks one category from descriptions.
"""
from __future__ import annotations

import json
import re
import time
from typing import Optional

from architecture.contracts import Diagnosis, DiagnosisRequest, Hypothesis, Misconception
from components.normalizer import NORMALIZER


class BugBayesDiagnoser:
    method = "bug-bayes-v0"

    def __init__(self, consistency: float = 0.8, slip: float = 0.1, eps: float = 0.02,
                 slip_prior: float = 0.2, abstain_below: float = 0.5):
        self.c, self.s, self.eps = consistency, slip, eps
        self.slip_prior, self.abstain_below = slip_prior, abstain_below

    def diagnose(self, req: DiagnosisRequest) -> Diagnosis:
        t0 = time.perf_counter()
        v = NORMALIZER.normalize(req.response.answer_raw, req.item).value
        if v is not None and v == req.item.answer_key:
            return Diagnosis(item_id=req.item.item_id, is_correct=True, hypotheses=[], p_slip=0.0,
                             method=self.method, latency_ms=(time.perf_counter() - t0) * 1e3)
        preds = {p.misconception_id: p.value for p in req.predicted}
        cands = req.candidates or list(preds)
        prior = dict(req.prior or {})
        p_slip0 = prior.pop("slip", self.slip_prior)
        raw = {m: prior.get(m, 1.0) for m in cands}
        z0 = sum(raw.values()) or 1.0
        pri = {m: (1 - p_slip0) * raw[m] / z0 for m in cands}
        lik = {m: (self.c if (preds.get(m) is not None and preds.get(m) == v) else (1 - self.c) * self.s * self.eps)
               for m in cands}
        post = {m: pri[m] * lik[m] for m in cands}
        ps = p_slip0 * self.s * self.eps
        z = sum(post.values()) + ps
        hyps = sorted(
            (Hypothesis(misconception_id=m, prob=post[m] / z,
                        evidence=[f"bug_exact:{v}"] if lik[m] == self.c else []) for m in cands),
            key=lambda h: -h.prob)
        return Diagnosis(item_id=req.item.item_id, is_correct=False, hypotheses=hyps, p_slip=ps / z,
                         abstained=(not hyps) or hyps[0].prob < self.abstain_below, method=self.method,
                         latency_ms=(time.perf_counter() - t0) * 1e3)


_LLM_PROMPT = """A student answered a maths question incorrectly. Decide which ONE misconception most likely produced this exact wrong answer.

Question: {stem}
Correct answer: {key}
Student's answer: {answer}

Misconceptions:
{options}

Reply with JSON only: {{"code": "<one code from the list, or NONE if none fits>", "confidence": <number between 0 and 1>}}"""


class LLMClassifierDiagnoser:
    def __init__(self, misconceptions: list[Misconception], model: str = "openai/gpt-4.1-mini"):
        self.ms = misconceptions
        self.model = model
        self.method = f"llm-zero-shot:{model}"

    def diagnose(self, req: DiagnosisRequest) -> Diagnosis:
        from components import llm

        t0 = time.perf_counter()
        v = NORMALIZER.normalize(req.response.answer_raw, req.item).value
        if v is not None and v == req.item.answer_key:
            return Diagnosis(item_id=req.item.item_id, is_correct=True, hypotheses=[], p_slip=0.0, method=self.method)
        cands = [m for m in self.ms if (req.candidates is None or m.misconception_id in req.candidates)]
        codes = {m.misconception_id.split(":")[-1]: m.misconception_id for m in cands}
        opts = "\n".join(f"- {m.misconception_id.split(':')[-1]}: {m.name}. {m.description}" for m in cands)
        txt = llm.chat([{"role": "user", "content": _LLM_PROMPT.format(
            stem=req.item.stem, key=req.item.answer_key, answer=req.response.answer_raw, options=opts)}],
            model=self.model, json_mode=True, max_tokens=60)
        try:
            d = json.loads(txt)
            code, conf = str(d.get("code", "NONE")).strip(), float(d.get("confidence", 0.5))
        except (json.JSONDecodeError, TypeError, ValueError):
            m = re.search(r"[A-Z_]{3,}", txt or "")
            code, conf = (m.group(0) if m else "NONE"), 0.5
        conf = min(max(conf, 0.0), 1.0)
        chosen: Optional[str] = codes.get(code)
        rest = (1 - conf) / max(1, len(cands) - (1 if chosen else 0))
        hyps = [Hypothesis(misconception_id=mid, prob=(conf if mid == chosen else rest), evidence=["llm"] if mid == chosen else [])
                for mid in codes.values()]
        hyps.sort(key=lambda h: -h.prob)
        return Diagnosis(item_id=req.item.item_id, is_correct=False, hypotheses=hyps,
                         p_slip=(1 - conf) if chosen is None else 0.0, abstained=chosen is None,
                         method=self.method, latency_ms=(time.perf_counter() - t0) * 1e3)
