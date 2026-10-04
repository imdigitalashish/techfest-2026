"""Answer normaliser: raw learner input -> canonical exact value (same format as bugs.canon)."""
from __future__ import annotations

import re
from fractions import Fraction
from typing import Optional

from architecture.contracts import Item, NormalizedAnswer

_MIXED = re.compile(r"^(-?)(\d+)\s+(\d+)/(\d+)$")


def _canon(v: Fraction) -> str:
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


class AnswerNormalizer:
    def normalize(self, raw: str, item: Optional[Item] = None) -> NormalizedAnswer:
        s = (raw or "").strip().replace("−", "-").replace("–", "-")
        s = re.sub(r"^[a-zA-Z]\s*=\s*", "", s)
        if item is not None and item.options and s.upper() in {o.label for o in item.options}:
            opt = next(o for o in item.options if o.label == s.upper())
            return NormalizedAnswer(raw=raw, value=opt.value, parse_ok=opt.value is not None, kind="option")
        while s.startswith("(") and s.endswith(")"):
            s = s[1:-1].strip()
        m = _MIXED.match(s)
        try:
            if m:
                sign = -1 if m.group(1) else 1
                f = sign * (int(m.group(2)) + Fraction(int(m.group(3)), int(m.group(4))))
            else:
                f = Fraction(s.replace(" ", ""))
        except (ValueError, ZeroDivisionError):
            return NormalizedAnswer(raw=raw, value=None, parse_ok=False, kind="text")
        return NormalizedAnswer(raw=raw, value=_canon(f), parse_ok=True,
                                kind="number" if f.denominator == 1 else "fraction")


NORMALIZER = AnswerNormalizer()
