"""Cascade + consistency analyses (pre-registered in eval/llm_gap_protocol.md, Addendum B).

Tasks
  consistency   REAL items: 40 fixed real_negatives items (20 P + 20 N, chosen by sha256 of item_id).
                gpt-5.5 re-asked 2x and gpt-4.1-mini / gpt-5.4-mini 1x each (fresh calls, no cache);
                the main-run response is run 1. Measures run-to-run agreement and wall-clock latency.
  cascade_real  POST HOC on committed real_negatives responses: engine claims when exactly one bug reproduces
                the answer on an evaluable item, else the LLM decides (= pre-registered secondary method HYB).
                Accuracy, false claims, LLM calls / cost / latency per 1,000 diagnoses vs LLM-only.
Run: AZURE_OPENAI_ENDPOINT=... nice -n 10 .venv/bin/python -m eval.run_cascade --task consistency
     nice -n 10 .venv/bin/python -m eval.run_cascade --task cascade_real        (offline)
Out: eval/results/llm_consistency.json (+ _responses.jsonl), eval/results/cascade_real.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from components.bugs.eedi_parse import executable_match
from eval.run_llm_gaps import MODELS, RES, build_real, cost_of, load_store, parse_real, r4, sha, split_query, usage_summary

SUBSET_PER_GROUP = 20
REPEATS = {"gpt-5.5": 2, "gpt-4.1-mini": 1, "gpt-5.4-mini": 1}


def subset(items: list[dict]) -> list[dict]:
    key = lambda it: hashlib.sha256(it["item_id"].encode()).hexdigest()
    p = sorted([it for it in items if it["group"] == "P"], key=key)[:SUBSET_PER_GROUP]
    n = sorted([it for it in items if it["group"] == "N"], key=key)[:SUBSET_PER_GROUP]
    return p + n


def fresh_call(model: str, prompt: str) -> dict:
    from components import llm

    cfg = MODELS[model]
    try:
        r = llm.chat_full([{"role": "user", "content": prompt}], model=f"openai/{model}", json_mode=True,
                          max_tokens=cfg["max_tokens"], reasoning_effort=cfg["effort"], use_cache=False)
        return {"content": r["content"], "usage": r["usage"], "latency_s": r.get("latency_s"), "error": None}
    except Exception as exc:  # recorded; scored as invalid
        return {"content": "", "usage": None, "latency_s": None, "error": f"{type(exc).__name__}: {str(exc)[:160]}"}


def run_consistency() -> dict:
    items = subset(build_real())
    store = load_store("real_negatives")
    by_main = {(k[0], k[1]): v for k, v in store.items()}
    rows, out = [], {"n_items": len(items), "subset_rule": "first 20 P and first 20 N by sha256(item_id)", "models": {}}
    for m, reps in REPEATS.items():
        jobs = [(it, rep) for rep in range(2, 2 + reps) for it in items]
        with ThreadPoolExecutor(max_workers=4) as ex:
            res = list(ex.map(lambda j: (j[0], j[1], fresh_call(m, j[0]["prompt"])), jobs))
        runs = {1: {it["item_id"]: parse_real(by_main[(m, it["item_id"])]["content"]) or "NONE" for it in items}}
        lat = []
        for it, rep, r in res:
            runs.setdefault(rep, {})[it["item_id"]] = parse_real(r["content"]) or "NONE"
            rows.append({"model": m, "item_id": it["item_id"], "run": rep, **r})
            if r.get("latency_s") is not None:
                lat.append(r["latency_s"])
        same = [len({runs[k][it["item_id"]] for k in runs}) == 1 for it in items]
        acc = {k: r4(np.mean([v[it["item_id"]] == it["gold"] for it in items])) for k, v in runs.items()}
        u = usage_summary([r for _, _, r in res], m)
        out["models"][m] = {"runs": len(runs), "all_runs_agree": r4(np.mean(same)), "n_disagree": int(len(same) - sum(same)),
                            "accuracy_by_run": acc, "latency_s_median": r4(statistics.median(lat)) if lat else None,
                            "latency_s_p90": r4(float(np.percentile(lat, 90))) if lat else None, "usage_fresh_calls": u}
    (RES / "llm_consistency_responses.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
    # engine timing on the same items (one pass); determinism is measured in eval/analyze_gaps.py (two passes, 304 items)
    t = []
    for it in items:
        q = it["prompt"]
        t0 = time.perf_counter()
        executable_match(*split_query(q[q.index("### Question:"):q.index("\n\nMisconceptions")]))
        t.append(time.perf_counter() - t0)
    out["engine"] = {"deterministic": "see eval/results/llm_gaps_posthoc.json engine_determinism", "latency_ms_median": r4(1e3 * statistics.median(t)), "latency_ms_p90": r4(1e3 * float(np.percentile(t, 90)))}
    out["total_cost_usd_estimate"] = round(sum(v["usage_fresh_calls"]["cost_usd_estimate"] for v in out["models"].values()), 4)
    return out


def run_cascade_real() -> dict:
    real = json.loads((RES / "llm_gaps_real_negatives.json").read_text())
    cons = json.loads((RES / "llm_consistency.json").read_text()) if (RES / "llm_consistency.json").exists() else {}
    items = build_real()
    n = len(items)
    engine_claims = sum(1 for it in items if it["exec"] != "NONE")
    out = {"label": "POST HOC (items seen before this analysis); cascade = pre-registered secondary method HYB",
           "n_items": n, "composition": real["counts"], "engine_answers": engine_claims,
           "llm_calls_per_1000": r4(1000 * (n - engine_claims) / n), "models": {}}
    store = load_store("real_negatives")
    for m, u in real["usage"].items():
        usage = {it["item_id"]: store[(m, it["item_id"], sha(it["prompt"]))].get("usage") for it in items}
        cost_all = sum(cost_of(usage[it["item_id"]], m) for it in items)
        cost_routed = sum(cost_of(usage[it["item_id"]], m) for it in items if it["exec"] == "NONE")
        out["models"][m] = {
            "llm_only": {k: real["methods"][f"LLM:{m}"][k] for k in ("acc_P", "fcr_N", "ba")},
            "cascade": {k: real["methods"][f"HYB:{m}"][k] for k in ("acc_P", "fcr_N", "ba")},
            "cost_usd_per_1000_llm_only": r4(1000 * cost_all / n),
            "cost_usd_per_1000_cascade": r4(1000 * cost_routed / n),
            "cost_saving_share": r4(1 - cost_routed / cost_all) if cost_all else None,
            "latency_s_median_llm_call": (cons.get("models", {}).get(m) or {}).get("latency_s_median"),
            "latency_note": "per-item latency was not recorded in the main run; median call latency is from the 40-item consistency subset",
        }
    return out


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True, choices=["consistency", "cascade_real"])
    a = ap.parse_args(argv)
    res = run_consistency() if a.task == "consistency" else run_cascade_real()
    res["command"] = "python -m eval.run_cascade " + " ".join(argv if argv is not None else sys.argv[1:])
    name = "llm_consistency.json" if a.task == "consistency" else "cascade_real.json"
    (RES / name).write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps(res, default=str)[:1500])


if __name__ == "__main__":
    main()
