"""Probability / expected-value pack: five executable misconceptions over five problem families (exact Fractions).

Each family computes the key exactly (by enumeration or closed form), and the misconception's answer by its rule.
Misconception sources (see research/notes/r7-domain-taxonomies.md; several are secondary, labelled there):
- EQUIPROB  equiprobability bias — treats every possible total as equally likely (Lecoutre; source-limited)
- INDEP     ignores dependence: draws without replacement treated as independent repeats (formal error; UNVERIFIED
            as a named misconception in the education literature)
- ADD_PROB  adds probabilities of separate attempts to get P(at least one) (formal error; UNVERIFIED as named)
- INVERSE   confusion of the inverse / base-rate neglect: answers P(+|D) for P(D|+)
- JENSEN    E[f(X)] taken as f(E[X]) (Jensen's inequality)
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from fractions import Fraction

CODES = ("EQUIPROB", "INDEP", "ADD_PROB", "INVERSE", "JENSEN")
DESCRIPTIONS = {
    "EQUIPROB": "Thinks every possible total is equally likely.",
    "INDEP": "Ignores that the first counter is not put back, treating both draws as having the same probability.",
    "ADD_PROB": "Adds the probabilities of the separate attempts to get the probability of at least one success.",
    "INVERSE": "Confuses P(positive test | has condition) with P(has condition | positive test), so answers with the test's detection rate.",
    "JENSEN": "Squares the expected value of the number shown instead of finding the expected value of the square.",
}
FAMILY_OF = {"EQUIPROB": "dice_sum", "INDEP": "no_replace", "ADD_PROB": "at_least_one", "INVERSE": "diagnostic", "JENSEN": "ev_square"}


@dataclass(frozen=True)
class ProbItem:
    item_id: str
    family: str
    code: str
    stem: str
    key: Fraction
    bug: Fraction


def canon(v: Fraction) -> str:
    return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"


def _pct(f: Fraction) -> str:
    v = f * 100
    return f"{v.numerator}%" if v.denominator == 1 else f"{float(v):g}%"


def make(code: str, rng: random.Random, idx: int) -> ProbItem:
    fam = FAMILY_OF[code]
    if fam == "dice_sum":
        n = rng.randint(4, 8)
        s = rng.choice([x for x in range(3, 2 * n) if x != n + 1])
        key = Fraction(sum(1 for i in range(1, n + 1) for j in range(1, n + 1) if i + j == s), n * n)
        bug = Fraction(1, 2 * n - 1)
        stem = f"Two fair {n}-sided dice, numbered 1 to {n}, are rolled. What is the probability that the total is {s}?"
    elif fam == "no_replace":
        r, b = rng.randint(2, 6), rng.randint(2, 8)
        t = r + b
        key, bug = Fraction(r * (r - 1), t * (t - 1)), Fraction(r, t) ** 2
        stem = (f"A bag has {r} red and {b} blue counters. Two counters are taken out at random, one after the other, "
                f"without putting the first one back. What is the probability that both are red?")
    elif fam == "at_least_one":
        while True:
            p = Fraction(rng.randint(1, 2), rng.randint(5, 10))
            k = rng.randint(2, 4)
            if k * p < 1:
                break
        key, bug = 1 - (1 - p) ** k, k * p
        stem = (f"Each attempt succeeds with probability {canon(p)}, independently of the others. "
                f"What is the probability of at least one success in {k} attempts?")
    elif fam == "diagnostic":
        prev = Fraction(1, rng.choice([20, 25, 50, 100]))
        se = rng.choice([Fraction(9, 10), Fraction(19, 20), Fraction(1)])
        fp = rng.choice([Fraction(1, 10), Fraction(1, 20), Fraction(1, 25)])
        key, bug = prev * se / (prev * se + (1 - prev) * fp), se
        stem = (f"A condition affects 1 in {prev.denominator} people. A test detects it in {_pct(se)} of people who have it, "
                f"and gives a positive result for {_pct(fp)} of people who do not have it. A randomly chosen person tests "
                f"positive. What is the probability that they have the condition?")
    else:
        n = rng.randint(3, 20)
        key, bug = Fraction((n + 1) * (2 * n + 1), 6), Fraction(n + 1, 2) ** 2
        stem = (f"A fair die with faces numbered 1 to {n} is rolled once. You win an amount equal to the square of the "
                f"number shown. What is the expected amount you win?")
    assert key != bug
    return ProbItem(item_id=f"prob-{code}-{idx:02d}", family=fam, code=code, stem=stem, key=key, bug=bug)


def build(per_code: int = 12, seed: int = 2026) -> list[ProbItem]:
    rng = random.Random(seed)
    out, seen = [], set()
    for code in CODES:
        i = 0
        while i < per_code:
            it = make(code, rng, i)
            if it.stem in seen:
                continue
            seen.add(it.stem)
            out.append(it)
            i += 1
    return out
