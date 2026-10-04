"""POST-HOC analyses requested by the 4 Oct cross-model reviews (reviews/2026-10-04-*.md). Offline; no API calls.

Everything here is labelled post hoc: it re-analyses committed responses and does not change any registered decision.
1. Exact (Clopper-Pearson) 95% intervals for headline proportions, including 0/n and n/n cases, where the
   registered percentile bootstrap degenerates to [0, 0] or [1, 1].
2. Cascade cost and latency from the items actually routed to the LLM (summed per-item usage and measured
   per-item latency), replacing the earlier all-item-average x routed-fraction approximation.
3. Question-clustered bootstrap for H1/H2 on real data (options of the same Eedi question resampled together),
   plus an exact sign test for the HYB-vs-LLM discordant pairs.
4. Tracing sensitivity: learners who hold both SQ_DOUBLE and NEG_TIMES_NEG and saw a squared negative (a
   rule-composition precedence the prompt does not specify) excluded.
5. Engine determinism measured (two passes over all real items) and median engine latency.
6. Retry accounting: responses that needed a second attempt (first-attempt usage was not retained) and an upper
   bound on their unrecorded cost.
Run: nice -n 10 .venv/bin/python -m eval.analyze_gaps     Out: eval/results/llm_gaps_posthoc.json
"""
from __future__ import annotations

import json
import random
import statistics
import time
from math import comb

import numpy as np
from scipy.stats import beta

from components.bugs.eedi_parse import executable_match
from eval.run_llm_gaps import MODELS, RES, build_real, build_tracing, load_store, parse_real, r4, sha, split_query

N_BOOT = 2000


def cp(k: int, n: int) -> list[float]:
    lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    return [r4(lo), r4(hi)]


def prop(k: int, n: int) -> dict:
    return {"k": k, "n": n, "p": r4(k / n) if n else None, "exact_ci95": cp(k, n)}


def cost(u: dict | None, model: str) -> float:
    if not u:
        return 0.0
    pin, pout = MODELS[model]["price"]
    return u.get("prompt_tokens", 0) / 1e6 * pin + u.get("completion_tokens", 0) / 1e6 * pout


def exact_cis() -> dict:
    out = {}
    real = json.loads((RES / "llm_gaps_real_negatives.json").read_text())
    items = build_real()
    store = load_store("real_negatives")
    groups = {g: [it for it in items if it["group"] == g] for g in ("P", "N")}
    preds = {"EXEC": {it["item_id"]: it["exec"] for it in items}}
    for m in real["usage"]:
        preds[f"LLM:{m}"] = {it["item_id"]: (parse_real(store[(m, it["item_id"], sha(it["prompt"]))]["content"]) or "NONE") for it in items}
    for name, pr in preds.items():
        k_fc = sum(pr[it["item_id"]] != "NONE" for it in groups["N"])
        k_ok = sum(pr[it["item_id"]] == it["gold"] for it in groups["P"])
        out[f"real.{name}.fcr_N"] = prop(k_fc, len(groups["N"]))
        out[f"real.{name}.acc_P"] = prop(k_ok, len(groups["P"]))
    inv = json.loads((RES / "llm_gaps_inversion.json").read_text())
    for name, m in inv["methods"].items():
        if "L3" in m and name.startswith("LLM:"):
            k = round(m["L3"]["exact_set_acc"] * m["L3"]["n"])
            out[f"inv.{name}.L3"] = prop(k, m["L3"]["n"])
    pg = json.loads((RES / "llm_gaps_prob_pack.json").read_text())
    for name, m in pg["methods"].items():
        if name.startswith("LLM:"):
            out[f"prob.{name}.both"] = prop(round(m["both_correct"] * m["n"]), m["n"])
            out[f"prob.{name}.key"] = prop(round(m["key_correct"] * m["n"]), m["n"])
    return out


def routed_cascade() -> dict:
    out = {}
    # probability diagnosis (engine-native; routing by construction)
    d = json.loads((RES / "llm_gaps_prob_diag.json").read_text())
    st = load_store("prob_diag")
    rows = {}
    for (m, iid, _), r in st.items():
        rows.setdefault(m, {})[iid] = r
    eng_ms = d["engine_latency_ms_median"]
    for m, by in rows.items():
        n = len(by)
        routed = [r for iid, r in by.items() if iid.endswith("-slip")]
        all_cost = sum(cost(r.get("usage"), m) for r in by.values())
        routed_cost = sum(cost(r.get("usage"), m) for r in routed)
        lat_llm = [r["latency_s"] for r in by.values() if r.get("latency_s") is not None]
        lat_cascade = [(r["latency_s"] if iid.endswith("-slip") else eng_ms / 1e3) for iid, r in by.items() if r.get("latency_s") is not None]
        out[f"prob_diag.{m}"] = {
            "label": "engine-native items; routing and accuracy guaranteed by construction (see protocol Clarifications)",
            "n_items": n, "routed": len(routed), "llm_calls_per_1000_cascade": r4(1000 * len(routed) / n),
            "cost_usd_per_1000_llm_only": r4(1000 * all_cost / n), "cost_usd_per_1000_cascade": r4(1000 * routed_cost / n),
            "cost_saving_share": r4(1 - routed_cost / all_cost) if all_cost else None,
            "latency_s_mean_llm_only": r4(statistics.mean(lat_llm)), "latency_s_median_llm_only": r4(statistics.median(lat_llm)),
            "latency_s_mean_cascade": r4(statistics.mean(lat_cascade)), "latency_s_median_cascade": r4(statistics.median(lat_cascade)),
            "engine_hit_latency_ms_median": eng_ms,
        }
    # real data (post hoc): routed = items where the engine does not claim
    items = build_real()
    store = load_store("real_negatives")
    real = json.loads((RES / "llm_gaps_real_negatives.json").read_text())
    for m in real["usage"]:
        by = {it["item_id"]: store[(m, it["item_id"], sha(it["prompt"]))] for it in items}
        routed = [it for it in items if it["exec"] == "NONE"]
        all_cost = sum(cost(by[it["item_id"]].get("usage"), m) for it in items)
        routed_cost = sum(cost(by[it["item_id"]].get("usage"), m) for it in routed)
        out[f"real.{m}"] = {
            "label": "POST HOC; latency not measured per item in the main run",
            "n_items": len(items), "engine_answers": len(items) - len(routed),
            "cost_usd_per_1000_llm_only": r4(1000 * all_cost / len(items)), "cost_usd_per_1000_cascade": r4(1000 * routed_cost / len(items)),
            "cost_saving_share": r4(1 - routed_cost / all_cost) if all_cost else None,
        }
    return out


def clustered_real() -> dict:
    items = build_real()
    store = load_store("real_negatives")
    real = json.loads((RES / "llm_gaps_real_negatives.json").read_text())
    cl = np.array([it["item_id"].split("_")[0] for it in items])
    g = np.array([it["group"] for it in items])
    gold = np.array([it["gold"] for it in items])
    ex = np.array([it["exec"] for it in items])
    ev = np.array([it["evaluable"] for it in items])
    uniq = np.array(sorted(set(cl)))
    idx_by = {c: np.where(cl == c)[0] for c in uniq}
    rng = np.random.default_rng(0)
    out = {"n_clusters": int(len(uniq)), "n_items": len(items)}
    for m in real["usage"]:
        lp = np.array([parse_real(store[(m, it["item_id"], sha(it["prompt"]))]["content"]) or "NONE" for it in items])
        gated = np.where(ev, ex, lp)
        hyb = np.where(ex != "NONE", ex, lp)
        d_fcr, d_ba = [], []
        for _ in range(N_BOOT):
            pick = np.concatenate([idx_by[c] for c in rng.choice(uniq, len(uniq))])
            P, N = pick[g[pick] == "P"], pick[g[pick] == "N"]
            if len(P) == 0 or len(N) == 0:
                continue
            d_fcr.append((lp[N] != "NONE").mean() - (ex[N] != "NONE").mean())
            ba = lambda pr: ((pr[P] == gold[P]).mean() + (pr[N] == "NONE").mean()) / 2
            d_ba.append(ba(gated) - ba(lp))
        Pm = g == "P"
        wins = int(((hyb == gold) & (lp != gold) & Pm).sum())
        losses = int(((hyb != gold) & (lp == gold) & Pm).sum())
        nd = wins + losses
        p_sign = min(1.0, 2 * sum(comb(nd, k) for k in range(0, min(wins, losses) + 1)) / 2 ** nd) if nd else 1.0
        out[m] = {"H1_cluster_ci": [r4(np.percentile(d_fcr, 2.5)), r4(np.percentile(d_fcr, 97.5))],
                  "H2_cluster_ci": [r4(np.percentile(d_ba, 2.5)), r4(np.percentile(d_ba, 97.5))],
                  "hyb_vs_llm_positives": {"wins": wins, "losses": losses, "exact_sign_test_p": r4(p_sign)}}
    return out


def tracing_sensitivity() -> dict:
    from components.bugs.school_math import Num, decode

    t = json.loads((RES / "llm_gaps_tracing.json").read_text())
    items = build_tracing()
    store = load_store("tracing")
    amb = set()
    for it in items:
        lines = it["prompt"].split("student's answer):\n", 1)[1]
        has_neg_sq = "(−" in lines and ")²" in lines
        if {"SQ_DOUBLE", "NEG_TIMES_NEG"} <= set(it["truth"]) and has_neg_sq:
            amb.add(it["item_id"])
    keep = [i for i, it in enumerate(items) if it["item_id"] not in amb]
    out = {"excluded_learners": len(amb), "kept": len(keep)}

    def exact(p, truth):
        return {c for c, v in p.items() if v >= 0.5} == set(truth)

    tr = [exact(items[i]["tracer_p"], items[i]["truth"]) for i in keep]
    out["TRACER"] = r4(np.mean(tr))
    from eval.run_llm_gaps import parse_trace
    for m in t["usage"]:
        ks = [i for i in keep if (m, items[i]["item_id"], sha(items[i]["prompt"])) in store]
        lm = [exact(parse_trace(store[(m, items[i]["item_id"], sha(items[i]["prompt"]))]["content"]) or {c: 0.5 for c in items[i]["tracer_p"]}, items[i]["truth"]) for i in ks]
        trs = [exact(items[i]["tracer_p"], items[i]["truth"]) for i in ks]
        diff = np.array(trs, float) - np.array(lm, float)
        rng = np.random.default_rng(0)
        b = rng.integers(0, len(ks), (N_BOOT, len(ks)))
        out[m] = {"n": len(ks), "tracer": r4(np.mean(trs)), "llm": r4(np.mean(lm)),
                  "diff_ci": [r4(np.percentile(diff[b].mean(1), 2.5)), r4(np.percentile(diff[b].mean(1), 97.5))]}
    return out


def engine_determinism() -> dict:
    items = build_real()
    outs, times = [], []
    for rep in range(2):
        o = []
        for it in items:
            q = it["prompt"]
            t0 = time.perf_counter()
            o.append(executable_match(*split_query(q[q.index("### Question:"):q.index("\n\nMisconceptions")])))
            times.append(time.perf_counter() - t0)
        outs.append(o)
    agree = sum(a == b for a, b in zip(*outs))
    return {"n_items": len(items), "passes": 2, "identical_outputs": agree,
            "latency_ms_median": r4(1e3 * statistics.median(times)), "latency_ms_p90": r4(1e3 * float(np.percentile(times, 90)))}


def retries() -> dict:
    out = {}
    for part in ("real_negatives", "inversion", "tracing", "prob_pack", "prob_diag"):
        st = load_store(part)
        for (m, _, _), r in st.items():
            if r.get("attempts", 1) > 1:
                o = out.setdefault(f"{part}.{m}", {"items_with_retry": 0, "unrecorded_cost_upper_bound_usd": 0.0})
                o["items_with_retry"] += 1
                # the discarded first attempt used at most max_completion_tokens output tokens plus the same prompt
                pin, pout = MODELS[m]["price"]
                pt = (r.get("usage") or {}).get("prompt_tokens", 0)
                o["unrecorded_cost_upper_bound_usd"] = r4(o["unrecorded_cost_upper_bound_usd"] + pt / 1e6 * pin + MODELS[m]["max_tokens"] / 1e6 * pout)
    out["total_unrecorded_upper_bound_usd"] = r4(sum(v["unrecorded_cost_upper_bound_usd"] for v in out.values() if isinstance(v, dict)))
    return out


def main() -> None:
    res = {"label": "POST HOC analyses requested by the 4 Oct reviews; no registered decision is changed",
           "command": "python -m eval.analyze_gaps",
           "exact_cis": exact_cis(), "routed_cascade": routed_cascade(), "clustered_real": clustered_real(),
           "tracing_sensitivity": tracing_sensitivity(), "engine_determinism": engine_determinism(), "retries": retries()}
    (RES / "llm_gaps_posthoc.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k not in ("exact_cis",)}, indent=1)[:4000])
    print({k: v for k, v in res["exact_cis"].items() if "fcr_N" in k or "gpt-5.5" in k})


if __name__ == "__main__":
    main()
