"""LLM-gap experiments — pre-registered in eval/llm_gap_protocol.md (read that first).

Parts
  real_negatives  REAL Kaggle Eedi 2024 distractors: 5 pack categories + NONE, incl. same-domain negatives
  inversion       SYNTHETIC items: which set (0-2) of pack misconceptions produced an answer, by expression depth
  tracing         SYNTHETIC learners: which misconceptions a learner holds after 12 answers
Usage (from the project folder; Azure endpoint in env, key fetched at runtime via `az`, never stored):
  AZURE_OPENAI_ENDPOINT=https://tf26-p08-aoai-1004.openai.azure.com/ \
    nice -n 10 .venv/bin/python -m eval.run_llm_gaps --part real_negatives --models gpt-4.1-mini,gpt-5.4-mini,gpt-5.5
  --dry      build items + executable/tracer results only (no API calls)
  --offline  score from the committed responses file (no API calls): reproduces the committed metrics
  --limit N  smoke test on the first N items per model
Outputs: eval/results/llm_gaps_<part>.json (metrics, decisions, tokens, cost) and
         eval/results/llm_gaps_<part>_responses.jsonl (raw model responses + usage)
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import pathlib
import random
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from math import gcd

import numpy as np
import pandas as pd

from architecture.contracts import Response
from components.bugs.eedi_parse import executable_match
from components.bugs.school_math import CODES, EEDI_LINKS, Num, SchoolMathBugs, canon, decode, safe_eval, show
from components.generator import item_bank
from components.learner_model import SetBayesTracer
from components.simulator import sample_population

ROOT = pathlib.Path(__file__).resolve().parents[1]
RES = pathlib.Path(__file__).parent / "results"
DATA = ROOT / ".data"

MODELS = {  # price: USD per 1M tokens (input, output)
    "gpt-4.1-mini": {"effort": None, "max_tokens": 300, "price": (0.40, 1.60)},
    "gpt-5.4-mini": {"effort": "medium", "max_tokens": 8000, "price": (0.75, 4.50)},
    "gpt-5.5": {"effort": "high", "max_tokens": 16000, "price": (5.00, 30.00)},
}
PRICE_SOURCE = ("Azure Retail Prices API, serviceName 'Foundry Models', swedencentral, Global meters "
                "(gpt 4.1 mini Inp/Outp glbl; 5.4 mini Inp/Opt Gl; 5.5 ShortCo inp/opt Gl), accessed 2026-10-04. "
                "Reasoning tokens are assumed to be billed as output tokens (assumption).")
SPEND_CAP_USD = 60.0
WORKERS = 4
N_BOOT = 2000

RULES = """- LTR: evaluates +, −, ×, ÷ strictly from left to right, ignoring that × and ÷ come before + and − (brackets and squares are still done first).
- SQ_DOUBLE: computes x² as 2 × x.
- SUB_NEG: when a negative number written in the question is subtracted, computes a − (−n) as a − n.
- FRAC_ADD: when two fractions written in the question are added directly, computes a/b + c/d as (a + c)/(b + d).
- NEG_TIMES_NEG: when both factors are negative, gives a negative product: (−a) × (−b) = −ab and (−a)² = −a²."""

P_REAL = """A student answered a maths question incorrectly. Decide whether ONE of the five misconceptions below explains this exact wrong answer. If none of them explains it, answer NONE.

{query}

Misconceptions (each is a precise rule):
{rules}
- NONE: none of the five explains this exact wrong answer (it comes from a different misconception or a careless slip).

Reply with JSON only: {{"code": "<LTR|SQ_DOUBLE|SUB_NEG|FRAC_ADD|NEG_TIMES_NEG|NONE>"}}"""

P_INV = """A student evaluated an arithmetic expression and got a wrong answer. The student may hold one or two of the five misconceptions below (applied consistently and together), or may have made a careless slip that none of them explains.

Expression: {expr}
Correct answer: {key}
Student's answer: {answer}

Misconceptions (each is a precise rule):
{rules}

Which misconception(s) produced exactly the student's answer? Give the smallest set that explains it. Reply with JSON only: {{"codes": [...]}} listing one or two codes, or [] if it is a careless slip that no one or two of these rules explain."""

P_TRACE = """A student answered the arithmetic questions below in one session. The student may hold any number of the five misconceptions listed. A student who holds a misconception applies it on most, but not all, questions where it changes the answer, and may also make occasional careless slips.

Misconceptions (each is a precise rule):
{rules}

Questions (expression | correct answer | student's answer):
{lines}

For each misconception, estimate the probability that this student holds it. Reply with JSON only: {{"LTR": p, "SQ_DOUBLE": p, "SUB_NEG": p, "FRAC_ADD": p, "NEG_TIMES_NEG": p}} with each p between 0 and 1."""

# ---- pre-registered label groups for the real-data part (see protocol §2.1) -----------------------
LINK = {i: cd for cd in CODES for i in EEDI_LINKS[cd]["kaggle2024"]}
S_EQUIV = {1072: "SQ_DOUBLE"}  # "Multiplies by the index" == doubling on a square
S_RELATED = {15: "LTR", 328: "LTR", 1862: "LTR", 2532: "LTR", 27: "SQ_DOUBLE", 1282: "SUB_NEG",
             1400: "NEG_TIMES_NEG", 172: "FRAC_ADD", 1909: "FRAC_ADD", 1980: "FRAC_ADD", 907: "FRAC_ADD"}
GPT55_SUBSET = {"real_negatives": "all", "inversion": "L3 only", "tracing": "first 50 learners"}


def show_llm(toks) -> str:
    """Display for LLM prompts: every fraction literal is bracketed, e.g. (1/4), so it reads as one number."""
    parts = []
    for t in toks:
        if isinstance(t, Num) and t.frac and t.value > 0:
            parts.append(f"({t.frac[0]}/{t.frac[1]})")
        else:
            parts.append(show([t]))
    return "".join(parts)


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def split_query(q: str):
    m = re.match(r"### Question:(.*?)### Correct:(.*?)### Incorrect:(.*)", q, re.S)
    return tuple(x.strip() for x in m.groups()) if m else (q, "", "")


def parse_json(txt: str):
    try:
        return json.loads(txt)
    except (TypeError, ValueError):
        m = re.search(r"\{.*\}", txt or "", re.S)
        try:
            return json.loads(m.group(0)) if m else None
        except ValueError:
            return None


def ci(vals, seed=0) -> list[float]:
    v = np.asarray(vals, dtype=float)
    if len(v) == 0:
        return [float("nan"), float("nan")]
    rng = np.random.default_rng(seed)
    m = v[rng.integers(0, len(v), (N_BOOT, len(v)))].mean(1)
    return [round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)]


def r4(x) -> float:
    return round(float(x), 4)


# ---- querying -------------------------------------------------------------------------------------
def load_store(part: str) -> dict:
    p = RES / f"llm_gaps_{part}_responses.jsonl"
    store = {}
    if p.exists():
        for line in p.read_text().splitlines():
            d = json.loads(line)
            store[(d["model"], d["item_id"], d["prompt_sha256"])] = d
    return store


def save_store(part: str, store: dict) -> None:
    rows = sorted(store.values(), key=lambda d: (d["model"], d["item_id"]))
    (RES / f"llm_gaps_{part}_responses.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))


def query(items: list[dict], model: str, store: dict, offline: bool) -> list[dict]:
    from components import llm

    cfg = MODELS[model]

    def one(it):
        k = (model, it["item_id"], sha(it["prompt"]))
        if k in store:
            return store[k]
        if offline:
            return {"model": model, "item_id": it["item_id"], "prompt_sha256": k[2], "content": "", "usage": None,
                    "finish_reason": "missing_offline", "error": "missing in committed responses", "attempts": 0}
        budget, rec = cfg["max_tokens"], None
        for attempt in (1, 2):  # protocol §4: one retry with double budget if the visible answer is empty
            try:
                r = llm.chat_full([{"role": "user", "content": it["prompt"]}], model=f"openai/{model}", json_mode=True,
                                  max_tokens=budget, reasoning_effort=cfg["effort"])
                rec = {"content": r["content"], "usage": r["usage"], "finish_reason": r["finish_reason"], "error": None}
            except Exception as exc:  # recorded, scored as invalid
                rec = {"content": "", "usage": None, "finish_reason": "error", "error": f"{type(exc).__name__}: {str(exc)[:160]}"}
            rec["attempts"] = attempt
            if rec["content"].strip():
                break
            budget *= 2
        out = {"model": model, "item_id": it["item_id"], "prompt_sha256": k[2], **rec}
        store[k] = out
        return out

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        return list(ex.map(one, items))


def usage_summary(rows: list[dict], model: str) -> dict:
    pin, pout = MODELS[model]["price"]
    pt = sum((r.get("usage") or {}).get("prompt_tokens", 0) for r in rows)
    ct = sum((r.get("usage") or {}).get("completion_tokens", 0) for r in rows)
    rt = sum(((r.get("usage") or {}).get("completion_tokens_details") or {}).get("reasoning_tokens", 0) for r in rows)
    return {"calls": len(rows), "errors": sum(1 for r in rows if r.get("error")), "prompt_tokens": pt,
            "completion_tokens": ct, "reasoning_tokens": rt, "cost_usd_estimate": round(pt / 1e6 * pin + ct / 1e6 * pout, 4)}


# ---- part 1: real_negatives -------------------------------------------------------------------------
def build_real() -> list[dict]:
    q = pd.read_parquet(DATA / "eedi2024/queries_w_rels.parquet")
    items = []
    for qid, query_text, m in zip(q.qid.astype(str), q["query"], q.mid.astype(int)):
        parsed, key_ok, matched = executable_match(*split_query(query_text))
        evaluable = bool(parsed and key_ok)
        if m in LINK:
            group, gold, rel = "P", LINK[m], None
        elif m in S_EQUIV and evaluable:
            group, gold, rel = "P", S_EQUIV[m], None
        elif m in S_EQUIV or not evaluable:
            continue
        elif m in S_RELATED:
            group, gold, rel = "S_related", "NONE", S_RELATED[m]
        else:
            group, gold, rel = "N", "NONE", None
        exec_pred = matched[0] if (evaluable and len(matched) == 1) else "NONE"
        items.append({"item_id": qid, "group": group, "gold": gold, "related": rel, "mid": m, "evaluable": evaluable,
                      "exec": exec_pred, "n_matched": len(matched), "prompt": P_REAL.format(query=query_text.strip(), rules=RULES)})
    return items


def parse_real(txt: str):
    d = parse_json(txt)
    code = str((d or {}).get("code", "")).strip().upper() if isinstance(d, dict) else ""
    return code if (code in CODES or code == "NONE") else None


def real_metrics(items, pred) -> dict:
    g = np.array([it["group"] for it in items])
    gold = np.array([it["gold"] for it in items])
    ev = np.array([it["evaluable"] for it in items])
    pr = np.array(pred)
    P, N, S = g == "P", g == "N", g == "S_related"
    claim = pr != "NONE"
    PN = P | N
    tp = claim & (pr == gold) & PN
    labels = list(CODES) + ["NONE"]
    f1s = []
    for lab in labels:
        t = (pr[PN] == lab) & (gold[PN] == lab)
        prec = t.sum() / max(1, (pr[PN] == lab).sum())
        rec = t.sum() / max(1, (gold[PN] == lab).sum())
        f1s.append(0.0 if prec + rec == 0 else 2 * prec * rec / (prec + rec))
    rel = np.array([it["related"] or "" for it in items])
    return {
        "acc_P": r4((pr[P] == gold[P]).mean()), "acc_P_ci": ci(pr[P] == gold[P]),
        "claim_rate_P": r4(claim[P].mean()),
        "fcr_N": r4(claim[N].mean()), "fcr_N_ci": ci(claim[N]),
        "ba": r4(((pr[P] == gold[P]).mean() + 1 - claim[N].mean()) / 2),
        "claim_precision_PN": r4(tp.sum() / max(1, (claim & PN).sum())),
        "macro_f1_PN": r4(np.mean(f1s)),
        "acc_P_evaluable": r4((pr[P & ev] == gold[P & ev]).mean()) if (P & ev).any() else None,
        "claim_precision_evaluable": r4((tp & ev).sum() / max(1, (claim & PN & ev).sum())),
        "fcr_S_related": r4(claim[S].mean()) if S.any() else None,
        "related_code_rate_S": r4((pr[S] == rel[S]).mean()) if S.any() else None,
    }


def run_real(models, offline, dry, limit) -> dict:
    items = build_real()
    g = [it["group"] for it in items]
    counts = {k: g.count(k) for k in ("P", "N", "S_related")}
    counts["P_evaluable"] = sum(1 for it in items if it["group"] == "P" and it["evaluable"])
    preds = {"EXEC": [it["exec"] for it in items]}
    out = {"counts": counts, "methods": {}, "usage": {}, "invalid": {}, "decisions": {}}
    store = load_store("real_negatives")
    for m in ([] if dry else models):
        sub = items[:limit] if limit else items
        rows = query(sub, m, store, offline)
        by_id = {r["item_id"]: r for r in rows}
        llm_pred, invalid = [], 0
        for it in items:
            r = by_id.get(it["item_id"])
            code = parse_real(r["content"]) if r else None
            invalid += r is not None and code is None
            llm_pred.append(code or "NONE")  # protocol §4: invalid -> no claim
        preds[f"LLM:{m}"] = llm_pred
        preds[f"GATED:{m}"] = [it["exec"] if it["evaluable"] else lp for it, lp in zip(items, llm_pred)]
        preds[f"HYB:{m}"] = [it["exec"] if it["exec"] != "NONE" else lp for it, lp in zip(items, llm_pred)]
        out["usage"][m] = usage_summary(rows, m)
        out["invalid"][m] = invalid
    if not dry and not offline:
        save_store("real_negatives", store)
    if limit:
        keep = set(it["item_id"] for it in items[:limit])
        idx = [i for i, it in enumerate(items) if it["item_id"] in keep]
        items = [items[i] for i in idx]
        preds = {k: [v[i] for i in idx] for k, v in preds.items()}
    for k, v in preds.items():
        out["methods"][k] = real_metrics(items, v)
    # pre-registered decisions (protocol §3)
    gr = np.array([it["group"] for it in items])
    iP, iN = np.where(gr == "P")[0], np.where(gr == "N")[0]
    gold = np.array([it["gold"] for it in items])
    rng = np.random.default_rng(0)
    bp = rng.integers(0, len(iP), (N_BOOT, len(iP))) if len(iP) else None
    bn = rng.integers(0, len(iN), (N_BOOT, len(iN))) if len(iN) else None
    ex_claim = np.array(preds["EXEC"]) != "NONE"
    for m in ([] if dry else models):
        llm_claim = np.array(preds[f"LLM:{m}"]) != "NONE"
        d_fcr = (llm_claim[iN].astype(float) - ex_claim[iN].astype(float))
        d_ci = [r4(np.percentile(d_fcr[bn].mean(1), 2.5)), r4(np.percentile(d_fcr[bn].mean(1), 97.5))] if bn is not None else None

        def ba(name):
            pr = np.array(preds[name])
            accP = (pr[iP] == gold[iP]).astype(float)
            spec = (pr[iN] == "NONE").astype(float)
            return (accP[bp].mean(1) + spec[bn].mean(1)) / 2, (accP.mean() + spec.mean()) / 2

        ba_g, ba_g0 = ba(f"GATED:{m}")
        ba_l, ba_l0 = ba(f"LLM:{m}")
        ba_h, ba_h0 = ba(f"HYB:{m}")
        diff = ba_g - ba_l
        diff_h = ba_h - ba_l
        out["decisions"][m] = {
            "H1_fcr_llm_minus_exec": r4(d_fcr.mean()), "H1_ci": d_ci, "H1_gap": bool(d_ci and d_ci[0] > 0),
            "H2_ba_gated_minus_llm": r4(ba_g0 - ba_l0),
            "H2_ci": [r4(np.percentile(diff, 2.5)), r4(np.percentile(diff, 97.5))],
            "H2_hybrid_adds_value": bool(np.percentile(diff, 2.5) > 0),
            "secondary_ba_hyb_minus_llm": r4(ba_h0 - ba_l0),
            "secondary_ci": [r4(np.percentile(diff_h, 2.5)), r4(np.percentile(diff_h, 97.5))],
        }
    return out


# ---- part 2: inversion (SYNTHETIC) -----------------------------------------------------------------
SUBSETS_12 = [frozenset([c]) for c in CODES] + [frozenset(p) for p in itertools.combinations(CODES, 2)]
ALL_SUBSETS = [frozenset(s) for k in range(1, 6) for s in itertools.combinations(CODES, k)]
LEVELS = {"L1": (3, 3), "L2": (5, 6), "L3": (7, 8)}
PER_CELL = 20


def _frac_lit(rng):
    while True:
        b = rng.randint(2, 9)
        a = rng.randint(1, b - 1)
        if gcd(a, b) == 1:
            return Num(Fraction(a, b), (a, b))


def _operand(rng):
    r = rng.random()
    if r < 0.38:
        return [Num(Fraction(rng.randint(2, 12)))]
    if r < 0.60:
        return [Num(Fraction(-rng.randint(2, 9)))]
    if r < 0.78:
        return [_frac_lit(rng)]
    if r < 0.90:
        return [Num(Fraction(rng.randint(2, 7))), "^2"]
    return [Num(Fraction(-rng.randint(2, 6))), "^2"]


def rand_expr(rng, n_ops: int):
    opnds = [_operand(rng) for _ in range(n_ops + 1)]
    ops = [rng.choice("+-*/") for _ in range(n_ops)]
    lo = hi = None
    if n_ops >= 2 and rng.random() < 0.5:
        lo = rng.randrange(0, n_ops)
        hi = min(n_ops, lo + rng.choice([1, 2]))
    toks = []
    for i, o in enumerate(opnds):
        if i == lo:
            toks.append("(")
        toks += o
        if i == hi:
            toks.append(")")
        if i < n_ops:
            toks.append(ops[i])
    return toks


def _has_neg_square(toks) -> bool:
    return any(isinstance(t, Num) and t.value < 0 and j + 1 < len(toks) and toks[j + 1] == "^2" for j, t in enumerate(toks))


_TRIGGERS = {  # protocol §2.2: each generating bug gets one injected trigger sub-expression
    "LTR": lambda rng: [Num(Fraction(rng.randint(2, 9))), "+", Num(Fraction(rng.randint(2, 9))), "*", Num(Fraction(rng.randint(2, 9)))],
    "SQ_DOUBLE": lambda rng: [Num(Fraction(rng.randint(3, 7))), "^2"],
    "SUB_NEG": lambda rng: [Num(Fraction(rng.randint(2, 12))), "-", Num(Fraction(-rng.randint(2, 9)))],
    "FRAC_ADD": lambda rng: [_frac_lit(rng), "+", _frac_lit(rng)],
    "NEG_TIMES_NEG": lambda rng: [Num(Fraction(-rng.randint(2, 9))), "*", Num(Fraction(-rng.randint(2, 9)))],
}


def inject(rng, toks, codes) -> list:
    """Replace random top-level operands with bracketed trigger sub-expressions for each code."""
    out = list(toks)
    for c in codes:
        pos = [j for j, t in enumerate(out) if isinstance(t, Num) and (j == 0 or out[j - 1] != "(") and
               (j + 1 >= len(out) or out[j + 1] != "^2")]
        if not pos:
            return out
        j = rng.choice(pos)
        trig = _TRIGGERS[c](rng)
        out = out[:j] + (["("] + trig + [")"] if c != "SQ_DOUBLE" else trig) + out[j + 1:]
    return out


def build_inversion(seed: int = 2026) -> list[dict]:
    rng = random.Random(seed)
    items = []
    for lv, (a, b) in LEVELS.items():
        for cond in ("single", "pair", "slip"):
            got = 0
            while got < PER_CELL:
                T0 = None
                if cond != "slip":
                    T0 = frozenset([rng.choice(CODES)]) if cond == "single" else frozenset(rng.sample(CODES, 2))
                n_ops = rng.randint(a, b)
                toks = rand_expr(rng, max(1, n_ops - (2 * len(T0) if T0 else 0)))
                if T0:
                    toks = inject(rng, toks, sorted(T0))
                key = safe_eval(toks)
                if key is None or key.denominator > 60 or abs(key) > 1000:
                    continue
                vals = {T: safe_eval(toks, sorted(T)) for T in ALL_SUBSETS}
                if cond == "slip":
                    y = key + rng.choice([-10, -3, -2, -1, 1, 2, 3, 10])
                    if any(v == y for v in vals.values()):
                        continue
                    truth = frozenset()
                else:
                    if T0 == frozenset({"SQ_DOUBLE", "NEG_TIMES_NEG"}) and _has_neg_square(toks):
                        continue
                    y = vals[T0]
                    if y is None or y == key or y.denominator > 1000 or abs(y) > 10 ** 5:
                        continue
                    if minimal_sets(vals, y) != [T0]:
                        continue  # protocol §2.2: the generating set must be the unique minimal 1-2 set reproducing y
                    truth = T0
                expr = show_llm(toks)
                items.append({"item_id": f"inv-{lv}-{cond}-{got:02d}", "level": lv, "cond": cond, "expr": expr,
                              "n_ops": sum(1 for t in toks if t in ("+", "-", "*", "/")),
                              "key": canon(key), "answer": canon(y), "truth": sorted(truth),
                              "vals": {"+".join(sorted(T)): (canon(v) if v is not None else None) for T, v in vals.items() if len(T) <= 2},
                              "prompt": P_INV.format(expr=expr, key=canon(key), answer=canon(y), rules=RULES)})
                got += 1
    return items


def minimal_sets(vals: dict, y) -> list:
    reps = [T for T in SUBSETS_12 if vals[T] == y]
    return [T for T in reps if not any(U < T for U in reps)]


def parse_inv(txt: str):
    d = parse_json(txt)
    if not isinstance(d, dict) or not isinstance(d.get("codes"), list):
        return None
    codes = sorted({str(c).strip().upper() for c in d["codes"]})
    if any(c not in CODES for c in codes) or len(codes) > 2:
        return None
    return codes


def run_inversion(models, offline, dry, limit) -> dict:
    items = build_inversion()
    out = {"counts": {f"{lv}/{c}": sum(1 for it in items if it["level"] == lv and it["cond"] == c)
                      for lv in LEVELS for c in ("single", "pair", "slip")}, "methods": {}, "usage": {}, "invalid": {}, "decisions": {}}
    out["ops_per_level"] = {lv: [min(it["n_ops"] for it in items if it["level"] == lv), r4(np.mean([it["n_ops"] for it in items if it["level"] == lv])),
                                 max(it["n_ops"] for it in items if it["level"] == lv)] for lv in LEVELS}
    exec_pred = []
    for it in items:
        reps = [frozenset(k.split("+")) for k, v in it["vals"].items() if v == it["answer"]]
        mins = [T for T in reps if not any(U < T for U in reps)]
        exec_pred.append(sorted(mins[0]) if len(mins) == 1 else ([] if not mins else ["AMBIGUOUS"]))
    preds = {"EXEC": exec_pred}
    store = load_store("inversion")
    for m in ([] if dry else models):
        sub = [it for it in items if (m != "gpt-5.5" or it["level"] == "L3")]
        sub = sub[:limit] if limit else sub
        rows = query(sub, m, store, offline)
        by_id = {r["item_id"]: r for r in rows}
        pr, inv = [], 0
        for it in items:
            r = by_id.get(it["item_id"])
            if r is None:
                pr.append(None)
                continue
            c = parse_inv(r["content"])
            inv += c is None
            pr.append(c if c is not None else ["INVALID"])
        preds[f"LLM:{m}"] = pr
        out["usage"][m] = usage_summary(rows, m)
        out["invalid"][m] = inv
    if not dry and not offline:
        save_store("inversion", store)
    for name, pr in preds.items():
        res = {}
        for lv in list(LEVELS) + ["ALL"]:
            idx = [i for i, it in enumerate(items) if (lv == "ALL" or it["level"] == lv) and pr[i] is not None]
            if not idx:
                continue
            ok = [pr[i] == items[i]["truth"] for i in idx]
            row = {"n": len(idx), "exact_set_acc": r4(np.mean(ok)), "ci": ci(ok)}
            for cond in ("single", "pair", "slip"):
                ii = [i for i in idx if items[i]["cond"] == cond]
                if ii:
                    row[f"acc_{cond}"] = r4(np.mean([pr[i] == items[i]["truth"] for i in ii]))
            slips = [i for i in idx if items[i]["cond"] == "slip"]
            fa = [bool(pr[i]) and pr[i] != ["INVALID"] for i in slips]
            row["slip_false_attribution"] = r4(np.mean(fa)) if fa else None
            row["slip_false_attribution_ci"] = ci(fa) if fa else None
            claims = [i for i in idx if pr[i] and pr[i] not in (["INVALID"], ["AMBIGUOUS"])]
            row["claim_consistency"] = r4(np.mean([items[i]["vals"].get("+".join(pr[i])) == items[i]["answer"] for i in claims])) if claims else None
            res[lv] = row
        out["methods"][name] = res
    for m in ([] if dry else models):
        r = out["methods"][f"LLM:{m}"]
        l3 = r.get("L3")
        out["decisions"][m] = {
            "H3_L3_exact_set_acc": l3["exact_set_acc"] if l3 else None, "H3_ci": l3["ci"] if l3 else None,
            "H3_gap": bool(l3 and l3["ci"][1] < 0.95),
            "H4_slip_false_attribution": r["ALL"]["slip_false_attribution"], "H4_ci": r["ALL"]["slip_false_attribution_ci"],
            "H4_gap": bool(r["ALL"]["slip_false_attribution_ci"] and r["ALL"]["slip_false_attribution_ci"][0] > 0.05),
        }
    return out


# ---- part 3: tracing (SYNTHETIC) ------------------------------------------------------------------
def build_tracing(n: int = 100, k: int = 12, seed: int = 2026) -> list[dict]:
    lib = SchoolMathBugs()
    learners = sample_population(n, seed, lib.ids(), lib)
    bank = item_bank(300, seed=seed)
    tracer = SetBayesTracer(lib)
    items = []
    for i, lr in enumerate(learners):
        rng = random.Random(f"trace|{seed}|{i}")
        qs = rng.sample(bank, k)
        st = tracer.start_session(tracer.init_state(lr.learner_id), "s1")
        lines = []
        for j, g in enumerate(qs):
            resp = lr.answer(g.item, g.predicted, rng, "s1")
            st = tracer.update(st, g.item, Response(learner_id=lr.learner_id, session_id="s1", item_id=g.item.item_id,
                                                     answer_raw=resp.answer_raw), None, g.predicted)
            lines.append(f"{j + 1}. {show_llm(decode(g.item.params['tokens']))} | {g.item.answer_key} | {resp.answer_raw}")
        items.append({"item_id": f"trace-{seed}-{i:03d}", "truth": sorted(c.split(':')[1] for c in lr.holds()),
                      "consistency": round(lr.consistency, 3), "slip": round(lr.slip, 3),
                      "tracer_p": {c: round(st.beliefs[f"pack:{c}"].p_holds, 6) for c in CODES},
                      "prompt": P_TRACE.format(rules=RULES, lines="\n".join(lines))})
    return items


def parse_trace(txt: str):
    d = parse_json(txt)
    if not isinstance(d, dict):
        return None
    try:
        p = {c: float(d[c]) for c in CODES}
    except (KeyError, TypeError, ValueError):
        return None
    return p if all(0.0 <= v <= 1.0 for v in p.values()) else None


def trace_metrics(items, probs, idx) -> dict:
    exact, brier, f1s = [], [], []
    for i in idx:
        p, t = probs[i], set(items[i]["truth"])
        exact.append({c for c in CODES if p[c] >= 0.5} == t)
        brier.append(np.mean([(p[c] - (c in t)) ** 2 for c in CODES]))
    for c in CODES:
        tp = sum(1 for i in idx if probs[i][c] >= 0.5 and c in items[i]["truth"])
        fp = sum(1 for i in idx if probs[i][c] >= 0.5 and c not in items[i]["truth"])
        fn = sum(1 for i in idx if probs[i][c] < 0.5 and c in items[i]["truth"])
        f1s.append(0.0 if tp == 0 else 2 * tp / (2 * tp + fp + fn))
    return {"n": len(idx), "exact_set_acc": r4(np.mean(exact)), "exact_ci": ci(exact), "brier": r4(np.mean(brier)),
            "brier_ci": ci(brier), "macro_f1": r4(np.mean(f1s)), "_exact": exact, "_brier": brier}


def run_tracing(models, offline, dry, limit) -> dict:
    items = build_tracing()
    out = {"counts": {"learners": len(items), "mean_held": r4(np.mean([len(it["truth"]) for it in items]))},
           "methods": {}, "usage": {}, "invalid": {}, "decisions": {}}
    probs = {"TRACER": [it["tracer_p"] for it in items]}
    store = load_store("tracing")
    for m in ([] if dry else models):
        sub = items[:50] if m == "gpt-5.5" else items
        sub = sub[:limit] if limit else sub
        rows = query(sub, m, store, offline)
        by_id = {r["item_id"]: r for r in rows}
        pr, inv = [], 0
        for it in items:
            r = by_id.get(it["item_id"])
            if r is None:
                pr.append(None)
                continue
            p = parse_trace(r["content"])
            inv += p is None
            pr.append(p if p is not None else {c: 0.5 for c in CODES})  # protocol §4: invalid -> 0.5 each
        probs[f"LLM:{m}"] = pr
        out["usage"][m] = usage_summary(rows, m)
        out["invalid"][m] = inv
    if not dry and not offline:
        save_store("tracing", store)
    full = {}
    for name, pr in probs.items():
        idx = [i for i in range(len(items)) if pr[i] is not None]
        full[name] = trace_metrics(items, pr, idx)
        out["methods"][name] = {k: v for k, v in full[name].items() if not k.startswith("_")}
    rng = np.random.default_rng(0)
    for m in ([] if dry else models):
        idx = [i for i in range(len(items)) if probs[f"LLM:{m}"][i] is not None]
        tr = trace_metrics(items, probs["TRACER"], idx)
        lm = trace_metrics(items, probs[f"LLM:{m}"], idx)
        de = np.array(tr["_exact"], float) - np.array(lm["_exact"], float)
        db = np.array(lm["_brier"]) - np.array(tr["_brier"])
        b = rng.integers(0, len(idx), (N_BOOT, len(idx)))
        out["decisions"][m] = {
            "n_paired": len(idx), "tracer_exact_on_same": tr["exact_set_acc"], "llm_exact": lm["exact_set_acc"],
            "H5_exact_tracer_minus_llm": r4(de.mean()), "H5_ci": [r4(np.percentile(de[b].mean(1), 2.5)), r4(np.percentile(de[b].mean(1), 97.5))],
            "H6_brier_llm_minus_tracer": r4(db.mean()), "H6_ci": [r4(np.percentile(db[b].mean(1), 2.5)), r4(np.percentile(db[b].mean(1), 97.5))],
        }
        d = out["decisions"][m]
        d["H5_gap"] = d["H5_ci"][0] > 0
        d["H6_gap"] = d["H6_ci"][0] > 0
    return out


PARTS = {"real_negatives": run_real, "inversion": run_inversion, "tracing": run_tracing}


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", required=True, choices=list(PARTS))
    ap.add_argument("--models", default="gpt-4.1-mini,gpt-5.4-mini,gpt-5.5")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args(argv)
    models = [m for m in a.models.split(",") if m]
    res = PARTS[a.part](models, a.offline, a.dry, a.limit)
    res.update({"part": a.part, "protocol": "eval/llm_gap_protocol.md", "price_source": PRICE_SOURCE,
                "gpt55_subset": GPT55_SUBSET[a.part], "models": {m: {k: v for k, v in MODELS[m].items()} for m in models},
                "command": "python -m eval.run_llm_gaps " + " ".join(argv if argv is not None else sys.argv[1:])})
    res["total_cost_usd_estimate"] = round(sum(u["cost_usd_estimate"] for u in res["usage"].values()), 4)
    if not a.dry and not a.limit:
        RES.mkdir(parents=True, exist_ok=True)
        (RES / f"llm_gaps_{a.part}.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: res[k] for k in ("counts", "decisions", "invalid", "usage", "total_cost_usd_estimate")}, default=str))
    for name, mtr in res["methods"].items():
        print(name, json.dumps(mtr, default=str)[:400])


if __name__ == "__main__":
    main()
