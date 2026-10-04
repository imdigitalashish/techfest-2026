"""Generation eval: template-discriminative generator (ours) vs LLM-only generation (baseline).

Run:  .venv/bin/python -m eval.run_generation --n 40 --llm-n 8
Out:  eval/results/generation.json
Every generated item is re-checked by an independent SymPy verifier. "Targets the misconception"
is judged against the executable definition of that misconception (components/bugs/school_math.py).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import time

from architecture.contracts import GenerationRequest
from components.bugs.school_math import CODES, MISCONCEPTIONS, canon, evaluate, mid, parse_dsl, predictions
from components.generator import TemplateGenerator
from components.normalizer import NORMALIZER
from components.verifier import SympyVerifier

OUT = pathlib.Path(__file__).parent / "results"
LLM_MODEL = "openai/gpt-4.1-mini"
PROMPT = """You are writing practice problems for a maths tutor.
Misconception: {name}. {desc}
Write ONE new arithmetic expression to evaluate that a student holding this misconception would get WRONG, so that the problem reveals the misconception.
Rules: use only whole numbers, negative numbers written in brackets like (-3), fractions written a/b, the operators + - × ÷, brackets, and ² for squaring.
Return JSON only: {{"expression": "...", "correct_answer": "...", "misconception_answer": "..."}} where both answers are integers or fractions a/b."""


def template_eval(n: int, seed: int) -> dict:
    ver, rows = SympyVerifier(), {}
    for code in CODES:
        for mode in ("isolated", "discriminative"):
            gen = TemplateGenerator()
            comps = [mid(c) for c in CODES if c != code] if mode == "discriminative" else []
            t0 = time.perf_counter()
            out = gen.generate(GenerationRequest(target_misconception_id=mid(code), competitor_ids=comps, n=n, seed=seed, as_mcq=True))
            dt = time.perf_counter() - t0
            reps = [ver.verify(g.item, g.predicted) for g in out]
            firing = [sum(p.value is not None for p in g.predicted) for g in out]
            rows[f"{code}/{mode}"] = {
                "requested": n, "accepted": len(out),
                "key_verified": sum(r.key_verified for r in reps) / max(1, len(reps)),
                "target_fires": sum(r.target_fires for r in reps) / max(1, len(reps)),
                "discriminative": sum(r.discriminative for r in reps) / max(1, len(reps)),
                "mean_bugs_firing": statistics.mean(firing) if firing else 0.0,
                "unique_items": len({g.item.item_id for g in out}),
                "tries_per_item": gen.stats["tries"] / max(1, len(out)),
                "ms_per_item": 1e3 * dt / max(1, len(out)),
                "example": out[0].item.stem if out else None,
            }
    return rows


def llm_eval(n: int) -> dict:
    from components import llm

    rows, examples, stopped = {}, [], None
    for code in CODES:
        m = MISCONCEPTIONS[code]
        stats = {"calls": 0, "parse_ok": 0, "key_correct": 0, "target_fires": 0, "llm_bug_answer_matches": 0,
                 "valid_targeted": 0, "discriminative": 0}
        for k in range(n):
            try:
                txt = llm.chat([{"role": "user", "content": PROMPT.format(name=m.name, desc=m.description)}],
                               model=LLM_MODEL, temperature=0.8, seed=k, json_mode=True, max_tokens=120)
            except llm.RateLimited as exc:
                stopped = str(exc)
                break
            stats["calls"] += 1
            try:
                d = json.loads(txt)
                toks = parse_dsl(str(d["expression"]).replace("x", "×"))
                key = evaluate(toks)
            except Exception as exc:  # unparseable or invalid expression
                examples.append({"code": code, "fail": f"parse: {type(exc).__name__}", "raw": txt[:160]})
                continue
            stats["parse_ok"] += 1
            key_ok = NORMALIZER.normalize(str(d.get("correct_answer", ""))).value == canon(key)
            preds = predictions(toks)
            fires = preds[code] is not None
            matches = fires and NORMALIZER.normalize(str(d.get("misconception_answer", ""))).value == canon(preds[code])
            vals = [v for v in preds.values() if v is not None]
            stats["key_correct"] += key_ok
            stats["target_fires"] += fires
            stats["llm_bug_answer_matches"] += matches
            stats["valid_targeted"] += key_ok and fires
            stats["discriminative"] += fires and len(set(vals)) == len(vals)
            if not (key_ok and fires) and len(examples) < 12:
                examples.append({"code": code, "expression": d.get("expression"), "llm_key": d.get("correct_answer"),
                                 "true_key": canon(key), "fires": fires})
        rows[code] = stats
        if stopped:
            break
    tot = {k: sum(r[k] for r in rows.values()) for k in next(iter(rows.values()))} if rows else {}
    rates = {k: (v / tot["calls"] if tot.get("calls") else None) for k, v in tot.items() if k != "calls"}
    return {"model": LLM_MODEL, "per_code": rows, "totals": tot, "rates": rates, "failure_examples": examples,
            "stopped_early": stopped}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--llm-n", type=int, default=8)
    a = ap.parse_args()
    res = {"command": f"python -m eval.run_generation --n {a.n} --seed {a.seed} --llm-n {a.llm_n}",
           "template": template_eval(a.n, a.seed)}
    if a.llm_n > 0:
        res["llm_only"] = llm_eval(a.llm_n)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "generation.json").write_text(json.dumps(res, indent=1, default=str))
    t = res["template"]
    print("| target/mode | accepted | key verified | target fires | discriminative | bugs firing | ms/item |")
    print("|---|---|---|---|---|---|---|")
    for k, r in t.items():
        print(f"| {k} | {r['accepted']}/{r['requested']} | {r['key_verified']:.2f} | {r['target_fires']:.2f} | "
              f"{r['discriminative']:.2f} | {r['mean_bugs_firing']:.2f} | {r['ms_per_item']:.1f} |")
    if "llm_only" in res:
        print("LLM-only:", json.dumps(res["llm_only"]["totals"]), json.dumps(res["llm_only"]["rates"]))


if __name__ == "__main__":
    main()
