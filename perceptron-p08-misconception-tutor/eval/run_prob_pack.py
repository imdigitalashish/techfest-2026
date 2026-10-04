"""Part 4 `prob_pack` (pre-registered: eval/llm_gap_protocol.md Addendum A = task gen; Addendum B = task diag).

task gen  — can an LLM produce the exact answer key AND the targeted misconception's wrong answer for a
            probability / expected-value practice problem? The executable pack (components/bugs/probability.py)
            computes both exactly, so it is correct by construction.
task diag — CONFIRMATORY cascade check on engine-native items: each problem is paired with (a) the targeted
            misconception's answer and (b) a careless-slip answer. ENGINE claims a misconception iff its
            executable answer equals the student's answer, else abstains; CASCADE:m = ENGINE, else LLM:m.
All items are SYNTHETIC.
Run: AZURE_OPENAI_ENDPOINT=... nice -n 10 .venv/bin/python -m eval.run_prob_pack --task gen|diag [--offline] [--dry] [--limit N]
Out: eval/results/llm_gaps_prob_pack.json | llm_gaps_prob_diag.json (+ _responses.jsonl)
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction

import numpy as np

from components.bugs.probability import CODES, DESCRIPTIONS, build, canon
from eval.run_llm_gaps import MODELS, PRICE_SOURCE, RES, ci, load_store, parse_json, r4, save_store, sha, usage_summary

P_PROB = """You are writing the answer key for a probability practice problem that targets a known misconception.

Problem: {stem}
Misconception: {desc}

Give (1) the exact correct answer and (2) the exact answer that a student holding this misconception would give. Write each as an integer or a fraction a/b in lowest terms.
Reply with JSON only: {{"correct": "...", "misconception_answer": "..."}}"""

P_PDIAG = """A student answered a probability problem incorrectly. Decide whether ONE of the five misconceptions below explains this exact wrong answer. If none of them explains it, answer NONE.

Problem: {stem}
Correct answer: {key}
Student's answer: {answer}

Misconceptions:
{descs}
- NONE: none of the five explains this exact wrong answer (a different misconception or a careless slip).

Reply with JSON only: {{"code": "<EQUIPROB|INDEP|ADD_PROB|INVERSE|JENSEN|NONE>"}}"""

DESCS = "\n".join(f"- {c}: {d}" for c, d in DESCRIPTIONS.items())


def to_frac(x):
    try:
        return Fraction(str(x).strip().replace(" ", ""))
    except (ValueError, ZeroDivisionError):
        return None


def slip_of(it) -> Fraction:
    for d in (1, -1, 2, -2):
        s = Fraction(it.key.numerator + d, it.key.denominator)
        if s not in (it.key, it.bug) and s > 0:
            return s
    raise ValueError(it.item_id)


def query_timed(rows: list[dict], model: str, store: dict, offline: bool) -> list[dict]:
    from components import llm

    cfg = MODELS[model]

    def one(it):
        k = (model, it["item_id"], sha(it["prompt"]))
        if k in store:
            return store[k]
        if offline:
            return {"model": model, "item_id": it["item_id"], "prompt_sha256": k[2], "content": "", "usage": None,
                    "latency_s": None, "error": "missing in committed responses", "attempts": 0}
        budget, rec = cfg["max_tokens"], None
        for attempt in (1, 2):
            try:
                r = llm.chat_full([{"role": "user", "content": it["prompt"]}], model=f"openai/{model}", json_mode=True,
                                  max_tokens=budget, reasoning_effort=cfg["effort"])
                rec = {"content": r["content"], "usage": r["usage"], "latency_s": r.get("latency_s"), "error": None}
            except Exception as exc:
                rec = {"content": "", "usage": None, "latency_s": None, "error": f"{type(exc).__name__}: {str(exc)[:160]}"}
            rec["attempts"] = attempt
            if rec["content"].strip():
                break
            budget *= 2
        out = {"model": model, "item_id": it["item_id"], "prompt_sha256": k[2], **rec}
        store[k] = out
        return out

    with ThreadPoolExecutor(max_workers=4) as ex:
        return list(ex.map(one, rows))


def task_gen(models, offline, dry, limit) -> dict:
    items = build()
    rows_in = [{"item_id": it.item_id, "prompt": P_PROB.format(stem=it.stem, desc=DESCRIPTIONS[it.code])} for it in items]
    res = {"part": "prob_pack", "task": "gen", "protocol": "eval/llm_gap_protocol.md (Addendum A)",
           "counts": {c: sum(1 for it in items if it.code == c) for c in CODES}, "methods": {}, "usage": {}, "invalid": {}, "decisions": {}}
    res["methods"]["EXEC"] = {"key_correct": 1.0, "bug_correct": 1.0, "both_correct": 1.0, "note": "exact by construction"}
    store = load_store("prob_pack")
    for m in ([] if dry else models):
        sub = rows_in[:limit] if limit else rows_in
        out = {r["item_id"]: r for r in query_timed(sub, m, store, offline)}
        key_ok, bug_ok, both, inv, per = [], [], [], 0, {c: [] for c in CODES}
        for it in items:
            r = out.get(it.item_id)
            if r is None:
                continue
            d = parse_json(r["content"])
            k = to_frac(d.get("correct")) if isinstance(d, dict) else None
            b = to_frac(d.get("misconception_answer")) if isinstance(d, dict) else None
            inv += k is None or b is None
            key_ok.append(k == it.key)
            bug_ok.append(b == it.bug)
            both.append(k == it.key and b == it.bug)
            per[it.code].append(k == it.key and b == it.bug)
        res["methods"][f"LLM:{m}"] = {"n": len(both), "key_correct": r4(np.mean(key_ok)), "key_ci": ci(key_ok),
                                      "bug_correct": r4(np.mean(bug_ok)), "bug_ci": ci(bug_ok),
                                      "both_correct": r4(np.mean(both)), "both_ci": ci(both),
                                      "both_by_code": {c: r4(np.mean(v)) for c, v in per.items() if v}}
        res["usage"][m] = usage_summary(list(out.values()), m)
        res["invalid"][m] = inv
        ci_b = res["methods"][f"LLM:{m}"]["both_ci"]
        res["decisions"][m] = {"H7_both_correct": res["methods"][f"LLM:{m}"]["both_correct"], "H7_ci": ci_b, "H7_gap": bool(ci_b[1] < 0.95)}
    if not dry and not offline:
        save_store("prob_pack", store)
    return res


def task_diag(models, offline, dry, limit) -> dict:
    probs = build()
    items = []
    for it in probs:
        for kind, ans, gold in (("bug", it.bug, it.code), ("slip", slip_of(it), "NONE")):
            items.append({"item_id": f"{it.item_id}-{kind}", "kind": kind, "gold": gold, "answer": ans, "code": it.code, "bug": it.bug,
                          "prompt": P_PDIAG.format(stem=it.stem, key=canon(it.key), answer=canon(ans), descs=DESCS)})
    t = []
    eng = []
    for x in items:
        t0 = time.perf_counter()
        eng.append(x["code"] if x["answer"] == x["bug"] else None)  # None = abstain
        t.append(time.perf_counter() - t0)
    res = {"part": "prob_pack", "task": "diag", "label": "CONFIRMATORY (Addendum B); SYNTHETIC engine-native items",
           "protocol": "eval/llm_gap_protocol.md (Addendum B)", "n_items": len(items),
           "engine_coverage": r4(np.mean([e is not None for e in eng])),
           "engine_latency_ms_median": r4(1e3 * statistics.median(t)), "methods": {}, "usage": {}, "invalid": {}, "decisions": {}}

    def score(pred):
        bug = [p == x["gold"] for p, x in zip(pred, items) if x["kind"] == "bug"]
        slip_fa = [p != "NONE" for p, x in zip(pred, items) if x["kind"] == "slip"]
        allok = [p == x["gold"] for p, x in zip(pred, items)]
        return {"acc_bug": r4(np.mean(bug)), "false_attribution_slip": r4(np.mean(slip_fa)), "acc_all": r4(np.mean(allok)),
                "acc_all_ci": ci(allok)}

    res["methods"]["ENGINE(abstain->NONE)"] = score([e or "NONE" for e in eng])
    store = load_store("prob_diag")
    for m in ([] if dry else models):
        sub = items[:limit] if limit else items
        out = {r["item_id"]: r for r in query_timed(sub, m, store, offline)}
        llm_pred, inv, lat = [], 0, []
        for x in items:
            r = out.get(x["item_id"])
            d = parse_json(r["content"]) if r else None
            code = str(d.get("code", "")).strip().upper() if isinstance(d, dict) else ""
            ok = code in CODES or code == "NONE"
            inv += r is not None and not ok
            llm_pred.append(code if ok else "NONE")
            if r and r.get("latency_s") is not None:
                lat.append(r["latency_s"])
        casc = [e if e is not None else lp for e, lp in zip(eng, llm_pred)]
        u = usage_summary(list(out.values()), m)
        cost_call = u["cost_usd_estimate"] / max(1, u["calls"])
        frac_llm = 1 - res["engine_coverage"]
        lat_med = statistics.median(lat) if lat else None
        res["methods"][f"LLM:{m}"] = score(llm_pred)
        res["methods"][f"CASCADE:{m}"] = score(casc)
        res["usage"][m] = u
        res["invalid"][m] = inv
        s_l, s_c = res["methods"][f"LLM:{m}"], res["methods"][f"CASCADE:{m}"]
        res["decisions"][m] = {
            "H8a_cascade_acc_all_ge_llm": bool(s_c["acc_all"] >= s_l["acc_all"]),
            "H8b_llm_calls_per_1000_cascade": r4(1000 * frac_llm), "H8b_le_550": bool(1000 * frac_llm <= 550),
            "H8_confirmed": bool(s_c["acc_all"] >= s_l["acc_all"] and 1000 * frac_llm <= 550),
            "llm_errors_on_bug_items_removed": r4(1 - s_l["acc_bug"]),
            "cost_usd_per_1000_llm_only": r4(1000 * cost_call), "cost_usd_per_1000_cascade": r4(1000 * cost_call * frac_llm),
            "latency_s_median_llm_call": r4(lat_med) if lat_med is not None else None,
            "latency_s_per_diagnosis_cascade": r4(frac_llm * lat_med) if lat_med is not None else None,
        }
    if not dry and not offline:
        save_store("prob_diag", store)
    return res


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=["gen", "diag"], default="gen")
    ap.add_argument("--models", default="gpt-4.1-mini,gpt-5.4-mini,gpt-5.5")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args(argv)
    models = [m for m in a.models.split(",") if m]
    res = (task_gen if a.task == "gen" else task_diag)(models, a.offline, a.dry, a.limit)
    res["price_source"] = PRICE_SOURCE
    res["command"] = "python -m eval.run_prob_pack " + " ".join(argv if argv is not None else sys.argv[1:])
    res["total_cost_usd_estimate"] = round(sum(u["cost_usd_estimate"] for u in res["usage"].values()), 4)
    name = "llm_gaps_prob_pack.json" if a.task == "gen" else "llm_gaps_prob_diag.json"
    if not a.dry and not a.limit:
        (RES / name).write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps({k: res.get(k) for k in ("counts", "n_items", "engine_coverage", "decisions", "invalid", "usage", "total_cost_usd_estimate")}, default=str)[:1500])
    for n_, mtr in res["methods"].items():
        print(n_, json.dumps(mtr)[:300])


if __name__ == "__main__":
    main()
