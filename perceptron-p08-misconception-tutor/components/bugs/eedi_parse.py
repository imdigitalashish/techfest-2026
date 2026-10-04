"""Map Eedi question text (LaTeX) onto the school-math bug family — the part of C3 the autoresearch loop edits.

`executable_match(question, correct, incorrect)` -> (parsed, key_agrees, matched_codes)
- parsed: an arithmetic expression in the question parsed and evaluated
- key_agrees: our clean evaluation equals Eedi's labelled correct answer
- matched_codes: pack misconceptions whose bug output equals the labelled wrong answer
"""
from __future__ import annotations

import re

from components.bugs.school_math import canon, parse_dsl, predictions, safe_eval
from components.normalizer import NORMALIZER

LATEX = [(r"\\left|\\right", ""), (r"\\times", "×"), (r"\\div", "÷"), (r"\\cdot", "×"), (r"\{\s*\}", ""),
         (r"\^\{\s*2\s*\}", "²"), (r"\^\s*2", "²")]


def latex_to_dsl(s: str) -> str:
    s = re.sub(r"\\[dt]?frac\s*\{\s*(\d+)\s*\}\s*\{\s*(\d+)\s*\}", r"\1/\2", s)
    for a, b in LATEX:
        s = re.sub(a, b, s)
    s = s.replace("−", "-").replace("\\", "").strip()
    s = re.sub(r"\s*=\s*\??\s*$|\s*\?\s*$", "", s)  # H2: drop trailing "=", "=?", "?"
    s = re.sub(r"^\s*-\s*\(", "(-1)×(", s)  # H2: leading minus before a bracket
    s = re.sub(r"\(\s*-\s*(\d+(?:/\d+)?)\s*\)", r"(−\1)", s)
    s = re.sub(r"(^|[+×÷*/(])\s*-\s*(\d+)", r"\1(−\2)", s)  # leading/inner unary minus -> bracketed negative
    return s.replace("-", "−")


def math_segments(text: str) -> list[str]:
    return [m.group(1) for m in re.finditer(r"\\[\(\[](.*?)\\[\)\]]", text, re.S)]


def answer_value(text: str):
    return NORMALIZER.normalize(latex_to_dsl(" ".join(math_segments(text)) or text).replace("−", "-")).value


def executable_match(question: str, correct: str, incorrect: str):
    wrong, corr = answer_value(incorrect), answer_value(correct)
    for seg in math_segments(question):
        try:
            toks = parse_dsl(latex_to_dsl(seg))
        except SyntaxError:
            continue
        key = safe_eval(toks)
        if key is None:
            continue
        preds = predictions(toks)
        matched = [cd for cd, v in preds.items() if v is not None and wrong is not None and canon(v) == wrong]
        return True, (corr == canon(key)), matched
    return False, False, []
