"""School-math domain pack (MVP): five executable misconceptions on one exact interpreter.

The clean interpreter evaluates an arithmetic expression exactly (Fractions,
standard precedence). Each misconception is a *bug switch* that changes one rule
of the interpreter, so evaluating an item with the switch on reproduces the wrong
answer a learner holding that misconception would give. Switches compose, so a
learner holding several misconceptions is modelled by turning several on.

Names are linked to Eedi's catalogue: the Kaggle 2024 "Eedi - Mining
Misconceptions in Mathematics" misconception list (ids 0-2586, via the
cdtmc/eedi-ir mirror) and the Eedi Misconceptions Graph v1.0 (CC BY 4.0,
https://huggingface.co/datasets/Eedi/Eedi-Misconceptions-Graph).
"""
from __future__ import annotations

import hashlib
import random
import re
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from math import gcd
from typing import Iterable, Optional, Sequence, Union

from architecture.contracts import Domain, Item, Misconception, Option, PredictedAnswer

FAMILY = "sm_expr_v0"
CODES = ("LTR", "SQ_DOUBLE", "SUB_NEG", "FRAC_ADD", "NEG_TIMES_NEG")
GRAPH_URL = "https://huggingface.co/datasets/Eedi/Eedi-Misconceptions-Graph"

# Exact Eedi names (verified against the downloaded files on 2026-10-04).
EEDI_LINKS = {
    "LTR": {
        "kaggle2024": {1507: "Carries out operations from left to right regardless of priority order",
                       1005: "Carries out operations from left to right regardless of priority order, unless brackets are used"},
        "graph": {21551: "Believes that mathematical operations should be performed strictly from left to right, ignoring the conventional or..."},
    },
    "SQ_DOUBLE": {
        "kaggle2024": {2316: "Mixes up squaring and multiplying by 2 or doubling",
                       2175: "Mixes up squaring and multiplying by 2 or doubling, and not square rooted"},
        "graph": {15012: "Mixes up squaring and multiplying by 2 or doubling, and not square rooted"},
    },
    "SUB_NEG": {
        "kaggle2024": {2566: "When subtracting a negative number, subtracts the absolute value rather than adding it",
                       1805: "Does not realise that subtracting a negative is the same as adding it's additive inverse"},
        "graph": {},
    },
    "FRAC_ADD": {
        "kaggle2024": {217: "When adding fractions, adds the numerators and denominators"},
        "graph": {},
    },
    "NEG_TIMES_NEG": {
        "kaggle2024": {1597: "Believes multiplying two negatives gives a negative answer"},
        "graph": {14310: "Believes multiplying two negatives gives a negative answer"},
    },
}

_DESCRIPTIONS = {
    "LTR": ("Ignores the order of operations", "Evaluates + − × ÷ strictly left to right (brackets and powers still first)."),
    "SQ_DOUBLE": ("Thinks squaring means doubling", "Treats n² as 2 × n."),
    "SUB_NEG": ("Subtracting a negative = subtracting a positive", "Treats a − (−n) as a − n instead of a + n."),
    "FRAC_ADD": ("Adds tops and bottoms of fractions", "Computes a/b + c/d as (a + c)/(b + d)."),
    "NEG_TIMES_NEG": ("Negative × negative is negative", "Gives a negative result when multiplying (or squaring) negatives."),
}


def mid(code: str) -> str:
    return f"pack:{code}"


def code_of(misconception_id: str) -> str:
    return misconception_id.split(":", 1)[1] if misconception_id.startswith("pack:") else misconception_id


MISCONCEPTIONS: dict[str, Misconception] = {
    c: Misconception(
        misconception_id=mid(c),
        name=_DESCRIPTIONS[c][0],
        description=_DESCRIPTIONS[c][1],
        domain=Domain.SCHOOL_MATH,
        category=c,
        eedi_ids=sorted(EEDI_LINKS[c]["graph"]),
        executable=True,
        source=GRAPH_URL,
    )
    for c in CODES
}


@dataclass(frozen=True)
class Num:
    value: Fraction
    frac: Optional[tuple[int, int]] = None  # displayed numerator/denominator for fraction literals

    @property
    def frac_literal(self) -> bool:
        return self.frac is not None


Token = Union[Num, str]
_OPS = ("+", "-", "*", "/")


class _Eval:
    __slots__ = ("t", "i", "b")

    def __init__(self, toks: Sequence[Token], bugs: frozenset[str]):
        self.t, self.i, self.b = toks, 0, bugs

    def _peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def _take(self):
        if self.i >= len(self.t):
            raise SyntaxError("unexpected end of expression")
        tok = self.t[self.i]
        self.i += 1
        return tok

    def run(self) -> Fraction:
        v = self.expr()
        if self.i != len(self.t):
            raise SyntaxError("trailing tokens")
        return v

    def expr(self) -> Fraction:
        if "LTR" in self.b:
            v, lit = self.atom()
            while self._peek() in _OPS:
                op = self._take()
                w, wl = self.atom()
                v, lit = self.apply(op, v, lit, w, wl), None
            return v
        v, lit = self.term()
        while self._peek() in ("+", "-"):
            op = self._take()
            w, wl = self.term()
            v, lit = self.apply(op, v, lit, w, wl), None
        return v

    def term(self):
        v, lit = self.atom()
        while self._peek() in ("*", "/"):
            op = self._take()
            w, wl = self.atom()
            v, lit = self.apply(op, v, lit, w, wl), None
        return v, lit

    def atom(self):
        tok = self._take()
        if isinstance(tok, Num):
            v, lit = tok.value, tok
        elif tok == "(":
            v, lit = self.expr(), None
            if self._take() != ")":
                raise SyntaxError("expected )")
        else:
            raise SyntaxError(f"unexpected token {tok!r}")
        while self._peek() == "^2":
            self._take()
            v, lit = self.square(v), None
        return v, lit

    def square(self, v: Fraction) -> Fraction:
        if "SQ_DOUBLE" in self.b:
            return 2 * v
        if v < 0 and "NEG_TIMES_NEG" in self.b:
            return -(v * v)
        return v * v

    def apply(self, op: str, a: Fraction, alit: Optional[Num], b: Fraction, blit: Optional[Num]) -> Fraction:
        if op == "+":
            if "FRAC_ADD" in self.b and alit is not None and blit is not None and alit.frac and blit.frac:
                return Fraction(alit.frac[0] + blit.frac[0], alit.frac[1] + blit.frac[1])
            return a + b
        if op == "-":
            if "SUB_NEG" in self.b and blit is not None and blit.value < 0:
                return a + b  # a − (−n) treated as a − n
            return a - b
        if op == "*":
            if "NEG_TIMES_NEG" in self.b and a < 0 and b < 0:
                return -(a * b)
            return a * b
        if b == 0:
            raise ZeroDivisionError("division by zero")
        return a / b


def evaluate(toks: Sequence[Token], bugs: Iterable[str] = ()) -> Fraction:
    return _Eval(toks, frozenset(code_of(b) for b in bugs)).run()


def safe_eval(toks: Sequence[Token], bugs: Iterable[str] = ()) -> Optional[Fraction]:
    try:
        return evaluate(toks, bugs)
    except (ZeroDivisionError, SyntaxError):
        return None


def canon(v: Fraction) -> str:
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def show(toks: Sequence[Token]) -> str:
    out = []
    for t in toks:
        if isinstance(t, Num):
            if t.frac:
                s = f"{abs(t.frac[0])}/{t.frac[1]}"
            else:
                s = str(abs(t.value.numerator))
            out.append(f"(−{s})" if t.value < 0 else s)
        elif t == "^2":
            out.append("²")
        elif t in _OPS:
            out.append({"+": " + ", "-": " − ", "*": " × ", "/": " ÷ "}[t])
        else:
            out.append(t)
    return "".join(out)


def to_sympy(toks: Sequence[Token]) -> str:
    parts = []
    for t in toks:
        if isinstance(t, Num):
            if t.frac:
                sign = "-" if t.value < 0 else ""
                parts.append(f"({sign}Rational({abs(t.frac[0])},{t.frac[1]}))")
            else:
                parts.append(f"({t.value.numerator})")
        elif t == "^2":
            parts.append("**2")
        else:
            parts.append(t)
    return " ".join(parts)


def encode(toks: Sequence[Token]) -> list[str]:
    out = []
    for t in toks:
        if isinstance(t, Num):
            out.append(f"f:{t.frac[0]}/{t.frac[1]}:{'-' if t.value < 0 else '+'}" if t.frac else f"n:{t.value.numerator}")
        else:
            out.append(t)
    return out


def decode(enc: Sequence[str]) -> list[Token]:
    out: list[Token] = []
    for s in enc:
        if s.startswith("n:"):
            out.append(Num(Fraction(int(s[2:]))))
        elif s.startswith("f:"):
            _, nd, sign = s.split(":")
            n, d = (int(x) for x in nd.split("/"))
            v = Fraction(n, d) * (-1 if sign == "-" else 1)
            out.append(Num(v, (n, d)))
        else:
            out.append(s)
    return out


_TOK = re.compile(
    r"\s*(?:(?P<neg>\(\s*[-−]\s*(?P<negv>\d+(?:/\d+)?)\s*\))|(?P<frac>\d+/\d+)|(?P<int>\d+)"
    r"|(?P<sq>\^\s*2|²|\*\*\s*2)|(?P<op>[-−+×*÷/:])|(?P<par>[()]))"
)
_OPMAP = {"-": "-", "−": "-", "+": "+", "×": "*", "*": "*", "÷": "/", "/": "/", ":": "/"}


def parse_dsl(s: str) -> list[Token]:
    """Parse the display DSL (also accepts ASCII): ints, (−n), a/b fraction literals, + − × ÷, brackets, ^2."""
    s = s.strip().rstrip("=").strip()
    pos, toks = 0, []
    while pos < len(s):
        m = _TOK.match(s, pos)
        if not m or m.end() == pos:
            if s[pos:].strip() == "":
                break
            raise SyntaxError(f"cannot parse near {s[pos:pos + 12]!r}")
        pos = m.end()
        if m.group("neg"):
            v = m.group("negv")
            if "/" in v:
                n, d = (int(x) for x in v.split("/"))
                toks.append(Num(-Fraction(n, d), (n, d)))
            else:
                toks.append(Num(-Fraction(int(v))))
        elif m.group("frac"):
            n, d = (int(x) for x in m.group("frac").split("/"))
            if d == 0:
                raise SyntaxError("zero denominator")
            toks.append(Num(Fraction(n, d), (n, d)))
        elif m.group("int"):
            toks.append(Num(Fraction(int(m.group("int")))))
        elif m.group("sq"):
            toks.append("^2")
        elif m.group("op"):
            toks.append(_OPMAP[m.group("op")])
        else:
            toks.append(m.group("par"))
    if not toks:
        raise SyntaxError("empty expression")
    return toks


def predictions(toks: Sequence[Token]) -> dict[str, Optional[Fraction]]:
    """Single-bug predicted answers; None where the bug does not change the answer."""
    key = evaluate(toks)
    out: dict[str, Optional[Fraction]] = {}
    for c in CODES:
        v = safe_eval(toks, (c,))
        out[c] = v if (v is not None and v != key) else None
    return out


PATTERNS: dict[str, list[str]] = {
    "ops3": ["I", "+-", "I", "*/", "I"],
    "ops3b": ["I", "*/", "I", "+-", "I"],
    "ops4": ["I", "+-", "I", "*/", "I", "+-", "I"],
    "sq1": ["I", "+-", "I", "*", "S"],
    "sq2": ["S", "+-", "I"],
    "subneg1": ["I", "-", "N"],
    "subneg2": ["I", "-", "N", "*/", "I"],
    "negmul1": ["N", "*", "N", "+-", "I"],
    "negmul2": ["NS", "+-", "I"],
    "negmul3": ["I", "-", "N", "*", "N"],
    "frac1": ["F", "+", "F"],
    "frac2": ["(", "F", "+", "F", ")", "*", "I"],
    "mix1": ["I", "-", "N", "*", "S"],
    "mix2": ["NS", "-", "N", "*", "I"],
}


def _rand_frac(rng: random.Random) -> Num:
    while True:
        b = rng.randint(2, 9)
        a = rng.randint(1, b - 1)
        if gcd(a, b) == 1:
            return Num(Fraction(a, b), (a, b))


def sample_tokens(pattern: str, rng: random.Random) -> list[Token]:
    toks: list[Token] = []
    for slot in PATTERNS[pattern]:
        if slot == "I":
            toks.append(Num(Fraction(rng.randint(2, 12))))
        elif slot == "N":
            toks.append(Num(Fraction(-rng.randint(2, 9))))
        elif slot == "S":
            toks += [Num(Fraction(rng.randint(3, 7))), "^2"]
        elif slot == "NS":
            toks += [Num(Fraction(-rng.randint(2, 6))), "^2"]
        elif slot == "F":
            toks.append(_rand_frac(rng))
        elif slot == "+-":
            toks.append(rng.choice("+-"))
        elif slot == "*/":
            toks.append(rng.choice("*/"))
        else:
            toks.append(slot)
    # make integer divisions exact under the clean reading: dividend = divisor × k
    for j, t in enumerate(toks):
        if t == "/" and 0 < j < len(toks) - 1:
            left, right = toks[j - 1], toks[j + 1]
            if isinstance(left, Num) and isinstance(right, Num) and not left.frac and not right.frac and right.value != 0:
                sign = -1 if left.value < 0 else 1
                toks[j - 1] = Num(Fraction(sign * abs(right.value.numerator) * rng.randint(2, 6)))
    return toks


def nice(v: Optional[Fraction]) -> bool:
    return v is not None and v.denominator <= 12 and abs(v) <= 500


@lru_cache(maxsize=1)
def can_fire() -> dict[str, frozenset[str]]:
    rng = random.Random(12345)
    out = {}
    for p in PATTERNS:
        fired: set[str] = set()
        for _ in range(120):
            toks = sample_tokens(p, rng)
            if safe_eval(toks) is None:
                continue
            fired |= {c for c, v in predictions(toks).items() if v is not None}
        out[p] = frozenset(fired)
    return out


def build_item(toks: Sequence[Token], *, target: Optional[str] = None, as_mcq: bool = True,
               rng: Optional[random.Random] = None, pattern: Optional[str] = None,
               provenance: str = "template") -> Item:
    key = evaluate(toks)
    expr = show(toks)
    item_id = "sm-" + hashlib.sha1(expr.encode()).hexdigest()[:10]
    options: list[Option] = []
    if as_mcq:
        preds = predictions(toks)
        vals: list[tuple[str, Optional[str], bool]] = [(canon(key), None, True)]
        seen = {canon(key)}
        order = ([target] if target else []) + [c for c in CODES if c != target]
        for c in order:
            v = preds.get(c)
            if v is not None and canon(v) not in seen and len(vals) < 4:
                vals.append((canon(v), mid(c), False))
                seen.add(canon(v))
        k = 1
        while len(vals) < 4:
            for cand in (key + k, key - k, -key - k):
                s = canon(cand)
                if s not in seen and len(vals) < 4:
                    vals.append((s, None, False))
                    seen.add(s)
            k += 1
        (rng or random.Random(item_id)).shuffle(vals)
        options = [Option(label="ABCD"[i], text=v, value=v, misconception_id=m, is_key=isk)
                   for i, (v, m, isk) in enumerate(vals)]
    return Item(
        item_id=item_id,
        domain=Domain.SCHOOL_MATH,
        family=FAMILY,
        params={"tokens": encode(toks), "pattern": pattern, "expression": expr},
        stem=f"Work out {expr}",
        answer_key=canon(key),
        options=options,
        target_misconception_id=mid(target) if target else None,
        provenance=provenance,  # type: ignore[arg-type]
        construct_name="Arithmetic with integers, negatives, powers and fractions",
    )


class SchoolMathBugs:
    """BugLibrary + ComposableBugLibrary for the school-math pack."""

    domain = Domain.SCHOOL_MATH

    def misconceptions(self) -> list[Misconception]:
        return list(MISCONCEPTIONS.values())

    def ids(self) -> list[str]:
        return [mid(c) for c in CODES]

    @staticmethod
    def tokens(item: Item) -> Optional[list[Token]]:
        enc = item.params.get("tokens") if item.family == FAMILY else None
        return decode(enc) if enc else None

    def predict(self, item: Item) -> list[PredictedAnswer]:
        toks = self.tokens(item)
        if toks is None or safe_eval(toks) is None:
            return [PredictedAnswer(misconception_id=mid(c), value=None) for c in CODES]
        p = predictions(toks)
        return [PredictedAnswer(misconception_id=mid(c), value=canon(p[c]) if p[c] is not None else None) for c in CODES]

    def predict_set(self, item: Item, misconception_ids: list[str]) -> Optional[str]:
        toks = self.tokens(item)
        if toks is None or not misconception_ids:
            return None
        key, v = safe_eval(toks), safe_eval(toks, [code_of(m) for m in misconception_ids])
        if key is None or v is None or v == key:
            return None
        return canon(v)
