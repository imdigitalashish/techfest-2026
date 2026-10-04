"""Generators: template-discriminative (spike) + an untargeted item bank."""
from __future__ import annotations

import random
from typing import Optional

from architecture.contracts import GeneratedItem, GenerationRequest
from components.bugs.school_math import (
    CODES, PATTERNS, SchoolMathBugs, build_item, can_fire, code_of, nice, predictions, safe_eval, sample_tokens,
)
from components.verifier import SympyVerifier


class TemplateGenerator:
    """Samples problem parameters until the target bug fires (and, if competitors are given,
    until every firing competitor gives a different wrong answer), then verifies with SymPy."""

    name = "template-discriminative-v0"

    def __init__(self, library: Optional[SchoolMathBugs] = None, verifier: Optional[SympyVerifier] = None,
                 max_tries: int = 4000):
        self.library = library or SchoolMathBugs()
        self.verifier = verifier or SympyVerifier()
        self.max_tries = max_tries
        self.stats = {"tries": 0, "rejected_verification": 0, "accepted": 0}

    def generate(self, req: GenerationRequest) -> list[GeneratedItem]:
        rng = random.Random(req.seed)
        target = code_of(req.target_misconception_id)
        if target not in CODES:
            raise ValueError(f"unknown misconception {req.target_misconception_id}")
        comps = [c for c in (code_of(x) for x in req.competitor_ids) if c != target and c in CODES]
        pats = [req.family] if req.family else [p for p in PATTERNS if target in can_fire()[p]]
        out: list[GeneratedItem] = []
        seen = set(req.exclude_item_ids)
        tries = 0
        while len(out) < req.n and tries < self.max_tries * max(1, req.n):
            tries += 1
            pat = rng.choice(pats)
            toks = sample_tokens(pat, rng)
            key = safe_eval(toks)
            if not nice(key):
                continue
            preds = predictions(toks)
            if not nice(preds.get(target)):
                continue
            firing = {c: v for c, v in preds.items() if v is not None}
            if comps:
                group = [firing[c] for c in [target] + comps if c in firing]
                if len(set(group)) != len(group):
                    continue
            elif len(firing) > 1 and tries < self.max_tries // 2:
                continue  # practice items: prefer isolating the target misconception
            item = build_item(toks, target=target, as_mcq=req.as_mcq, rng=rng, pattern=pat)
            if item.item_id in seen:
                continue
            predicted = self.library.predict(item)
            rep = self.verifier.verify(item, predicted)
            if not rep.passed:
                self.stats["rejected_verification"] += 1
                continue
            seen.add(item.item_id)
            out.append(GeneratedItem(item=item, predicted=predicted, verification=rep, generator=self.name))
        self.stats["tries"] += tries
        self.stats["accepted"] += len(out)
        return out


def item_bank(n: int, seed: int, as_mcq: bool = False, library: Optional[SchoolMathBugs] = None) -> list[GeneratedItem]:
    """Untargeted practice items drawn uniformly over patterns (the 'random practice' baseline)."""
    rng = random.Random(seed)
    lib, ver = library or SchoolMathBugs(), SympyVerifier()
    out, seen = [], set()
    while len(out) < n:
        pat = rng.choice(list(PATTERNS))
        toks = sample_tokens(pat, rng)
        if not nice(safe_eval(toks)):
            continue
        item = build_item(toks, as_mcq=as_mcq, rng=rng, pattern=pat)
        if item.item_id in seen:
            continue
        predicted = lib.predict(item)
        rep = ver.verify(item, predicted)
        if rep.key_verified and rep.well_formed:
            seen.add(item.item_id)
            out.append(GeneratedItem(item=item, predicted=predicted, verification=rep, generator="bank-uniform-v0"))
    return out
