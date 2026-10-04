"""Live engine for the P8 demo: what the LIVE tab computes, using the project's committed components only.

No LLM is called here and nothing touches the network. Every function returns plain JSON-able dicts.

- certify()     Does one pack rule (or a pair of rules acting together) reproduce this exact answer? If so, a
                certificate with step-by-step traces; otherwise an abstention ("would route to the LLM").
- predict()     A new, SymPy-verified question on which every surviving hypothesis gives a different answer.
                The conditional predictions ("if you hold X you will answer Y") are sealed with sha256 before
                the learner answers ...
- reveal()      ... then revealed, checked against the seal, and fed to the set-level Bayesian tracer.
- rerun()       The same input N times: the outputs must be identical.
- slip_storm()  Small random slips on the untargeted item bank: how many abstain, how many collide with a rule.
- RealText      INTERNAL VERIFICATION ONLY (local-text mode): Eedi text read at runtime from .data/, kept in
                memory, never written anywhere. Not for display in front of judges (Kaggle rules §7.B).
"""
from __future__ import annotations

import hashlib
import itertools
import json
import re
import secrets
import statistics
import threading
import time
from collections import OrderedDict
from fractions import Fraction
from pathlib import Path
from typing import Optional, Sequence

from architecture.contracts import GenerationRequest, Response
from components.bugs.school_math import (
    CODES, MISCONCEPTIONS, SchoolMathBugs, Token, _Eval, build_item, canon, decode, encode, evaluate, mid, parse_dsl,
    safe_eval, show,
)
from components.generator import TemplateGenerator, item_bank
from components.learner_model import SetBayesTracer
from components.normalizer import NORMALIZER

MINUS = "\u2212"
OPSYM = {"+": "+", "-": MINUS, "*": "\u00d7", "/": "\u00f7"}
SETS = [frozenset([c]) for c in CODES] + [frozenset(p) for p in itertools.combinations(CODES, 2)]
SLIP_DELTAS = (-10, -3, -2, -1, 1, 2, 3, 10)  # the registered slip offsets (eval/llm_gap_protocol.md §2.2)
# Short patterns for follow-up questions, so a person can work them out in their head (components/bugs/school_math.PATTERNS).
# Each pattern listed here can fire its rule (checked against school_math.can_fire() in demo/smoke.py).
SIMPLE = {"LTR": ("ops3",), "SQ_DOUBLE": ("sq2", "sq1"), "SUB_NEG": ("subneg1",),
          "FRAC_ADD": ("frac1",), "NEG_TIMES_NEG": ("negmul1", "negmul2")}
PRESETS = [
    {"expr": "1/8 + 1/8", "note": "the example in our abstract"},
    {"expr": "3 + 4 \u00d7 2", "note": "order of operations"},
    {"expr": "5\u00b2 + 3", "note": "squaring"},
    {"expr": "7 \u2212 (\u22122)", "note": "subtracting a negative"},
    {"expr": "(\u22123) \u00d7 (\u22124) + 2", "note": "negative \u00d7 negative"},
    {"expr": "2 + 3 \u00d7 4\u00b2", "note": "two rules can act together"},
]
MAX_EXPR_CHARS = 80
MAX_TOKENS = 31

LIB = SchoolMathBugs()
_GEN = TemplateGenerator(LIB)
_LOCK = threading.RLock()


def rule_info() -> dict:
    return {c: {"name": MISCONCEPTIONS[c].name, "description": MISCONCEPTIONS[c].description} for c in CODES}


# ---- display ------------------------------------------------------------------------------------------------------
def fmt(v: Fraction) -> str:
    s = canon(abs(v))
    return MINUS + s if v < 0 else s


def fmt_operand(v: Fraction) -> str:
    return f"({fmt(v)})" if v < 0 else fmt(v)


def canon_display(value: str) -> str:
    return value.replace("-", MINUS)


# ---- parsing --------------------------------------------------------------------------------------------------------
def tokens_from(expr: Optional[str] = None, tokens: Optional[Sequence[str]] = None) -> list[Token]:
    """Tokens from an encoded token list (generated items) or from display-DSL text typed by the presenter."""
    if tokens:
        toks = decode(list(tokens))
    else:
        if not expr or len(expr) > MAX_EXPR_CHARS:
            raise ValueError(f"type an expression of at most {MAX_EXPR_CHARS} characters")
        toks = parse_dsl(expr)
    if len(toks) > MAX_TOKENS:
        raise ValueError("expression too long for the demo")
    try:
        evaluate(toks)
    except ZeroDivisionError:
        raise ValueError("that expression divides by zero") from None
    except SyntaxError as exc:
        raise ValueError(f"cannot read that expression ({exc})") from None
    return toks


def question(toks: Sequence[Token], note: str = "") -> dict:
    key = evaluate(toks)
    return {"expression": show(toks), "tokens": encode(toks), "key": canon(key), "key_display": fmt(key), "note": note}


# ---- traces ---------------------------------------------------------------------------------------------------------
class _TraceEval(_Eval):
    """The project's interpreter (components/bugs/school_math._Eval), recording each operation it performs.
    Results are identical: only `square` and `apply` are wrapped, and they call the original methods."""

    def __init__(self, toks, bugs):
        super().__init__(toks, bugs)
        self.steps: list[dict] = []

    def square(self, v):
        r = super().square(v)
        rule = None
        if r != v * v:
            rule = "SQ_DOUBLE" if ("SQ_DOUBLE" in self.b and r == 2 * v) else "NEG_TIMES_NEG"
        self.steps.append({"text": f"{fmt_operand(v)}\u00b2 = {fmt(r)}", "sig": ["sq", str(v), str(r)], "rule": rule})
        return r

    def apply(self, op, a, alit, b, blit):
        r = super().apply(op, a, alit, b, blit)
        clean = a + b if op == "+" else a - b if op == "-" else a * b if op == "*" else a / b
        rule, shown = None, fmt(r)
        if r != clean:
            rule = {"+": "FRAC_ADD", "-": "SUB_NEG", "*": "NEG_TIMES_NEG"}[op]
            if rule == "FRAC_ADD":
                n, d = alit.frac[0] + blit.frac[0], alit.frac[1] + blit.frac[1]
                shown = f"{n}/{d}" if Fraction(n, d).denominator == d else f"{n}/{d} = {fmt(r)}"
        self.steps.append({"text": f"{fmt_operand(a)} {OPSYM[op]} {fmt_operand(b)} = {shown}",
                           "sig": ["op", op, str(a), str(b), str(r)], "rule": rule})
        return r


def trace(toks: Sequence[Token], bugs: Sequence[str] = ()) -> tuple[Fraction, list[dict]]:
    ev = _TraceEval(toks, frozenset(bugs))
    return ev.run(), ev.steps


def marked(toks: Sequence[Token], bugs: Sequence[str]) -> dict:
    """Correct working and the rule's working side by side; each rule step is marked
    same | rule (a rule changed this operation) | order (left-to-right order) | after (carries an earlier change)."""
    key, clean = trace(toks)
    val, steps = trace(toks, bugs)
    diverged_at, out = None, []
    for i, s in enumerate(steps):
        same = diverged_at is None and i < len(clean) and clean[i]["sig"] == s["sig"]
        if same:
            status = "same"
        else:
            if diverged_at is None:
                diverged_at = i
            status = "rule" if s["rule"] else ("order" if ("LTR" in bugs and i == diverged_at) else "after")
        out.append({"text": s["text"], "status": status, "rule": s["rule"] if s["rule"] else ("LTR" if status == "order" else None)})
    return {"rules": sorted(bugs, key=CODES.index), "value": canon(val), "value_display": fmt(val),
            "steps": out, "clean_steps": [{"text": s["text"], "highlight": diverged_at is not None and i == diverged_at}
                                          for i, s in enumerate(clean)],
            "key": canon(key), "key_display": fmt(key), "diverged_at": diverged_at}


# ---- certify --------------------------------------------------------------------------------------------------------
def _decide(toks: Sequence[Token], raw: str) -> tuple:
    """The engine's decision, as a hashable tuple: (status, answer, minimal rule sets)."""
    v = NORMALIZER.normalize(raw).value
    if v is None:
        return ("unreadable", None, ())
    key = evaluate(toks)
    if v == canon(key):
        return ("correct", v, ())
    hits = []
    for s in SETS:
        y = safe_eval(toks, s)
        if y is not None and y != key and canon(y) == v:
            hits.append(s)
    minimal = [s for s in hits if not any(o < s for o in hits)]
    sets = tuple(tuple(sorted(s, key=CODES.index)) for s in minimal)
    return ("certificate" if sets else "abstain", v, sets)


def rule_table(toks: Sequence[Token]) -> list[dict]:
    key = evaluate(toks)
    rows = []
    for c in CODES:
        y = safe_eval(toks, (c,))
        rows.append({"rule": c, "value": canon(y) if (y is not None and y != key) else None,
                     "value_display": fmt(y) if (y is not None and y != key) else None})
    return rows


def certify(toks: Sequence[Token], raw: str) -> dict:
    t0 = time.perf_counter()
    status, v, sets = _decide(toks, raw)
    engine_ms = 1e3 * (time.perf_counter() - t0)
    out = {"verdict": status, "answer": v, "answer_display": canon_display(v) if v else None, "question": question(toks),
           "engine_ms": round(engine_ms, 3), "rules": rule_table(toks), "llm_calls": 0}
    if status == "certificate":
        out["certificates"] = [marked(toks, s) for s in sets]
        out["ambiguous"] = len(sets) > 1
    elif status == "abstain":
        out["route"] = "No pack rule, alone or in a pair, gives this exact answer: nothing is claimed. " \
                       "In the cascade this answer would go to the LLM (not called in this demo)."
    return out


def rerun(toks: Sequence[Token], raw: str, n: int = 1000) -> dict:
    n = max(1, min(int(n), 20000))
    first = _decide(toks, raw)
    same, ts = 0, []
    for _ in range(n):
        t0 = time.perf_counter()
        out = _decide(toks, raw)
        ts.append(time.perf_counter() - t0)
        same += out == first
    ts.sort()
    return {"n": n, "identical": same, "median_ms": round(1e3 * statistics.median(ts), 3),
            "p90_ms": round(1e3 * ts[int(0.9 * (n - 1))], 3), "max_ms": round(1e3 * ts[-1], 3),
            "total_ms": round(1e3 * sum(ts), 1), "decision": [first[0], first[1], [list(s) for s in first[2]]]}


# ---- predict / reveal -----------------------------------------------------------------------------------------------
def _seed(*parts) -> int:
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:12], 16)


def _label(h: frozenset) -> str:
    return " + ".join(sorted(h, key=CODES.index)) if h else "slip"


def _new_state(tracer: SetBayesTracer):
    return tracer.init_state("judge")


def _observe(tracer: SetBayesTracer, state, item, raw: str):
    resp = Response(learner_id="judge", session_id="s1", item_id=item.item_id, answer_raw=raw)
    return tracer.update(state, item, resp, None, LIB.predict(item))


def _posterior(tracer: SetBayesTracer, state) -> dict:
    assert tracer.ids == [mid(c) for c in CODES], "tracer bit j must be CODES[j]"
    joint = tracer.joint(state)
    marg = tracer.marginals(joint)
    best = int(joint.argmax())
    return {"marginals": {c: round(float(marg[j]), 4) for j, c in enumerate(CODES)},
            "map_set": sorted((CODES[j] for j in range(len(CODES)) if (best >> j) & 1), key=CODES.index),
            "p_map": round(float(joint[best]), 4), "p_none": round(float(joint[0]), 4)}


def _mask(h: frozenset) -> int:
    return sum(1 << CODES.index(c) for c in h)


_SEALS: "OrderedDict[str, dict]" = OrderedDict()


def _simplicity(toks: Sequence[Token], answers: Sequence[str] = ()) -> tuple:
    """Smaller is easier to work out in your head: fewer tokens, fewer negatives, integer answers, small numbers."""
    nums = [t for t in toks if not isinstance(t, str)]
    return (len(toks), sum(1 for t in nums if t.value < 0), sum(1 for a in answers if "/" in a),
            max(abs(t.value.numerator) for t in nums))


def _candidates(hyps: list[frozenset], toks, raw, exclude: list[str]) -> list:
    out, seen = [], set(exclude)
    targets = sorted({c for h in hyps for c in h}, key=CODES.index)
    for t in targets:
        fams = list(SIMPLE[t]) + [None]
        for fam in fams:
            for k in range(3):
                req = GenerationRequest(target_misconception_id=mid(t), competitor_ids=[mid(c) for c in CODES if c != t],
                                        family=fam, n=1, seed=_seed(show(toks), raw, t, fam, k), as_mcq=False,
                                        exclude_item_ids=sorted(seen))
                for g in _GEN.generate(req):
                    if g.item.item_id not in seen:
                        seen.add(g.item.item_id)
                        out.append(g)
    return out


def predict(toks: Sequence[Token], raw: str) -> dict:
    """Seal conditional predictions for a new discriminating question, given the learner's first answer."""
    with _LOCK:
        t0 = time.perf_counter()
        status, v, sets = _decide(toks, raw)
        if status != "certificate":
            return {"ok": False, "verdict": status,
                    "reason": "Nothing to predict: no pack rule reproduces this answer, so the engine claims nothing."
                    if status == "abstain" else "Answer a question wrongly first (a correct answer needs no diagnosis)."}
        hyps = [frozenset(s) for s in sets] + [frozenset()]
        tracer = SetBayesTracer(LIB)
        item1 = build_item(toks, as_mcq=False)
        state = _observe(tracer, _new_state(tracer), item1, raw)
        joint = tracer.joint(state)
        cands = _candidates(hyps[:-1], toks, raw, [item1.item_id])
        scored = []
        for g in cands:
            if not (g.verification.key_verified and g.verification.target_fires):
                continue
            preds, every_rule_acts = {}, True
            for h in hyps:
                y = LIB.predict_set(g.item, [mid(c) for c in h]) if h else None
                preds[_label(h)] = y if y is not None else g.item.answer_key
                for c in h:  # does each rule of this hypothesis change the answer here?
                    rest = [mid(x) for x in h if x != c]
                    without = (LIB.predict_set(g.item, rest) if rest else None) or g.item.answer_key
                    every_rule_acts &= preds[_label(h)] != without
            if len(set(preds.values())) != len(preds):
                continue  # some hypotheses would give the same answer here: not discriminating
            toks2 = decode(g.item.params["tokens"])
            simplicity = _simplicity(toks2, list(preds.values()))
            scored.append((every_rule_acts, simplicity, tracer.eig(state, g.item), g, preds))
        if not scored:
            return {"ok": False, "verdict": status, "reason": "No discriminating follow-up found for these hypotheses."}
        strong = [s for s in scored if s[0]] or scored
        # the simplest question that separates the hypotheses (a person answers it live); then the most informative
        _, _, eig, g, preds = min(strong, key=lambda s: (s[1], -s[2], s[3].item.item_id))
        lead = max(hyps[:-1], key=lambda h: (float(joint[_mask(h)]), -_mask(h)))
        toks2 = decode(g.item.params["tokens"])
        nonce = secrets.token_hex(8)
        committed = json.dumps({"question": show(toks2), "if_you_hold": preds, "lead": _label(lead), "nonce": nonce},
                               sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        digest = hashlib.sha256(committed.encode("utf-8")).hexdigest()
        token = secrets.token_urlsafe(9)
        _SEALS[token] = {"committed": committed, "hash": digest, "item": g.item, "preds": preds, "lead": _label(lead),
                         "state": state, "tracer": tracer, "first": {"question": show(toks), "answer": v}}
        while len(_SEALS) > 256:
            _SEALS.popitem(last=False)
        rep = g.verification
        return {"ok": True, "question": question(toks2), "hash": digest, "token": token, "lead": _label(lead),
                "lead_rules": sorted(lead, key=CODES.index), "hypotheses": [_label(h) for h in hyps],
                "eig_nats": round(eig, 4), "posterior": _posterior(tracer, state),
                "verification": {"key_verified_by": rep.key_method, "key_verified": rep.key_verified,
                                 "target_fires": rep.target_fires, "discriminative": rep.discriminative},
                "engine_ms": round(1e3 * (time.perf_counter() - t0), 2), "llm_calls": 0}


def practice(code: str, n: int = 3, seed: int = 0) -> list[dict]:
    items = _GEN.generate(GenerationRequest(target_misconception_id=mid(code), n=n, seed=_seed("practice", code, seed),
                                            as_mcq=False))
    out = []
    for g in items:
        toks = decode(g.item.params["tokens"])
        trap = LIB.predict_set(g.item, [mid(code)])
        out.append({"expression": show(toks), "key_display": canon_display(g.item.answer_key),
                    "trap_display": canon_display(trap) if trap else None,
                    "key_verified_by": g.verification.key_method, "key_verified": g.verification.key_verified,
                    "target_fires": g.verification.target_fires})
    return out


def reveal(token: str, raw: str) -> dict:
    with _LOCK:
        s = _SEALS.pop(token, None)
        if s is None:
            return {"ok": False, "reason": "Unknown or already revealed prediction."}
        v = NORMALIZER.normalize(raw).value
        item, preds, lead = s["item"], s["preds"], s["lead"]
        tracer, state = s["tracer"], s["state"]
        matched = [h for h, y in preds.items() if v is not None and y == v]
        if v is not None:
            state = _observe(tracer, state, item, raw)
        if v is None:
            verdict = "unreadable"
        elif preds[lead] == v:
            verdict = "match"
        elif matched and matched[0] != "slip":
            verdict = "other"
        elif v == item.answer_key:
            verdict = "correct"
        else:
            verdict = "none"
        post = _posterior(tracer, state)
        out = {"ok": True, "committed": s["committed"], "hash": s["hash"], "answer": v,
               "answer_display": canon_display(v) if v else None, "verdict": verdict, "matched": matched, "lead": lead,
               "predictions": {h: canon_display(y) for h, y in preds.items()}, "key_display": canon_display(item.answer_key),
               "first": s["first"], "posterior": post, "llm_calls": 0}
        if verdict in ("match", "other") and post["map_set"]:
            codes = post["map_set"][:2]
            out["practice"] = [dict(p, rule=c) for c in codes for p in practice(c, n=3 if len(codes) == 1 else 2,
                                                                                  seed=s["hash"][:8])]
            out["practice_for"] = codes
        return out


# ---- new questions and stress ------------------------------------------------------------------------------------------
def new_question(k: int = 0) -> dict:
    """A fresh tutor-native question (generated, SymPy-verified), cycling through the five rules: the simplest of a
    few generated candidates on which every rule that fires gives a different wrong answer."""
    code = CODES[k % len(CODES)]
    fams = SIMPLE[code]
    req = GenerationRequest(target_misconception_id=mid(code), competitor_ids=[mid(c) for c in CODES if c != code],
                            family=fams[(k // len(CODES)) % len(fams)], n=6, seed=_seed("new", k), as_mcq=False)
    with _LOCK:
        gs = _GEN.generate(req)
    if not gs:
        raise RuntimeError(f"no question generated for {code}")

    def ease(g):
        toks = decode(g.item.params["tokens"])
        vals = [p.value for p in g.predicted if p.value is not None]
        return _simplicity(toks, vals), g.item.item_id

    g = min(gs, key=ease)
    q = question(decode(g.item.params["tokens"]), note="generated now · key verified by SymPy")
    q["verified"] = g.verification.key_verified
    return q


_BANK: dict = {}


def slip_storm(n_items: int = 300, seed: int = 2026) -> dict:
    if (n_items, seed) not in _BANK:
        with _LOCK:
            _BANK[(n_items, seed)] = item_bank(n_items, seed=seed)
    t0 = time.perf_counter()
    abstain, collide, examples = 0, 0, []
    for g in _BANK[(n_items, seed)]:
        toks = decode(g.item.params["tokens"])
        key = evaluate(toks)
        for d in SLIP_DELTAS:
            status, v, sets = _decide(toks, canon(key + d))
            if status == "certificate":
                collide += 1
                if len(examples) < 3:
                    examples.append({"expression": show(toks), "key": fmt(key), "slip": fmt(key + d),
                                     "rules": [" + ".join(s) for s in sets]})
            else:
                abstain += 1
    total = abstain + collide
    return {"items": n_items, "seed": seed, "deltas": list(SLIP_DELTAS), "slips": total, "abstain": abstain,
            "collide": collide, "collide_share": round(collide / total, 4), "examples": examples,
            "ms": round(1e3 * (time.perf_counter() - t0), 1), "llm_calls": 0}


def warm() -> None:
    """Warm caches (imports, regexes, SymPy, the item bank) so the first live timing shown is representative."""
    toks = tokens_from(PRESETS[1]["expr"])
    for _ in range(200):
        _decide(toks, "14")
    p = predict(toks, "14")
    _SEALS.pop(p.get("token"), None)
    new_question(0)
    slip_storm()


# ---- REAL items, local text (internal verification only) ----------------------------------------------------------------
class RealText:
    """Eedi text for the 304 benchmark items, read from the local .data/ copy at runtime and kept in memory only.
    Kaggle competition data (CC BY-NC 4.0; rules §7.B): internal verification only, never committed or recorded."""

    def __init__(self, data_dir: Path, ids: Sequence[str]):
        import pandas as pd

        from eval.run_llm_gaps import split_query

        self._split = split_query
        q = pd.read_parquet(data_dir / "eedi2024" / "queries_w_rels.parquet")
        wanted = set(ids)
        self.rows = {qid: query for qid, query in zip(q.qid.astype(str), q["query"]) if qid in wanted}
        missing = wanted - set(self.rows)
        if missing:
            raise RuntimeError(f"{len(missing)} benchmark items missing from the local data, e.g. {sorted(missing)[:3]}")

    @staticmethod
    def _render(text: str) -> str:
        from components.bugs.eedi_parse import latex_to_dsl

        return re.sub(r"\\[\(\[](.*?)\\[\)\]]", lambda m: latex_to_dsl(m.group(1)), text, flags=re.S).strip()

    def decide(self, item_id: str) -> str:
        from components.bugs.eedi_parse import executable_match

        parsed, key_ok, matched = executable_match(*self._split(self.rows[item_id]))
        return matched[0] if (parsed and key_ok and len(matched) == 1) else "NONE"

    def item(self, item_id: str) -> dict:
        from components.bugs.eedi_parse import answer_value, latex_to_dsl, math_segments

        question_text, correct, incorrect = self._split(self.rows[item_id])
        t0 = time.perf_counter()
        claim = self.decide(item_id)
        engine_ms = 1e3 * (time.perf_counter() - t0)
        out = {"item_id": item_id, "question": self._render(question_text), "correct": self._render(correct),
               "incorrect": self._render(incorrect), "engine": claim, "engine_ms": round(engine_ms, 4),
               "notice": "LOCAL TEXT: Kaggle Eedi competition data from your own .data/ copy. Internal verification only."}
        for seg in math_segments(question_text):  # the first evaluable segment, exactly as eedi_parse does
            try:
                toks = parse_dsl(latex_to_dsl(seg))
            except SyntaxError:
                continue
            if safe_eval(toks) is None:
                continue
            out["expression"] = show(toks)
            out["wrong_value"] = answer_value(incorrect)
            if claim != "NONE":
                out["certificate"] = marked(toks, [claim])
            break
        return out

    def rerun_all(self, n: int = 2) -> dict:
        t0 = time.perf_counter()
        passes = [{i: self.decide(i) for i in sorted(self.rows)} for _ in range(max(1, int(n)))]
        same = sum(1 for i in passes[0] if all(p[i] == passes[0][i] for p in passes))
        return {"passes": len(passes), "items": len(passes[0]), "identical": same, "codes": passes[0],
                "ms": round(1e3 * (time.perf_counter() - t0), 1)}
