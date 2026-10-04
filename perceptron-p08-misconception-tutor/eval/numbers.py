"""Numbers registry: every number a deliverable may cite, rendered from committed results.

- `allowed()`  — strings of every numeric leaf in eval/results/*.json (+ the C3 autoresearch ledger), rendered
  as percent with one decimal ("86.0"), and as raw decimals with 2–4 places ("0.326"). Used by check_docs.py
  to flag numbers in deliverables that come from no committed result.
- `claims()`   — named headline claims (exact strings) that specific documents must contain.
Run: .venv/bin/python -m eval.numbers   (prints the headline claims)
"""
from __future__ import annotations

import csv
import json
import pathlib

RES = pathlib.Path(__file__).parent / "results"
ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "components/bugs/autoresearch/results.tsv"


def _load(name: str) -> dict:
    p = RES / name
    return json.loads(p.read_text()) if p.exists() else {}


def pct(x: float) -> str:
    return f"{100 * x:.1f}"


def _walk(o, out: set) -> None:
    if isinstance(o, bool) or o is None:
        return
    if isinstance(o, (int, float)):
        x = float(o)
        if 0 <= abs(x) <= 1:
            out.add(pct(abs(x)))
            for d in (2, 3, 4):
                out.add(f"{abs(x):.{d}f}")
        out.add(f"{abs(x):.1f}")
        out.add(f"{abs(x):.2f}")
        return
    if isinstance(o, dict):
        for v in o.values():
            _walk(v, out)
    elif isinstance(o, (list, tuple)):
        for v in o:
            _walk(v, out)


def allowed() -> set:
    out: set = set()
    for p in sorted(RES.glob("*.json")):
        _walk(json.loads(p.read_text()), out)
    if LEDGER.exists():
        for row in csv.DictReader(LEDGER.open(), delimiter="\t"):
            for k in ("metric(reproduction_dev)",):
                try:
                    _walk(float(row[k]), out)
                except (KeyError, ValueError):
                    pass
            for part in row.get("notes", "").replace(";", " ").split():
                if "=" in part or part.replace(".", "").isdigit():
                    try:
                        _walk(float(part.split("=")[-1].rstrip(")")), out)
                    except ValueError:
                        pass
    return out


def claims() -> dict:
    """Headline claims (name -> exact string). Only keys whose source results exist are returned."""
    c: dict = {}
    d = _load("diagnosis.json")
    dd = _load("diagnosis_derived.json")
    if dd:
        acc = dd["accuracy"]
        c["closed5.majority"] = pct(acc["majority"]) + "%"
        c["closed5.tfidf"] = pct(acc["tfidf"]) + "%"
        c["closed5.exec_tfidf"] = pct(acc["exec_then_tfidf"]) + "%"
        c["closed5.llm41"] = pct(acc["llm"]) + "%"
        c["closed5.exec_llm41"] = pct(acc["exec_then_llm"]) + "%"
        c["closed5.exec_precision"] = f"{dd['exec_correct_when_fires']}/{dd['exec_fires_unique']}"
    if d:
        a = d["A_open_set"]
        c["open.map25_knn"] = f"{a['knn_train_labels']['MAP@25']:.3f}"
        c["open.unseen_share"] = pct(a["test_misconceptions_unseen_in_train"]) + "%"
    s = _load("simulation.json")
    if s:
        main = s["settings"]["main (targeted feedback 0.30, generic 0.10)"]
        pess = s["settings"]["pessimistic (named feedback no better: 0.10/0.10)"]
        c["sim.ours_left"] = pct(main["eig+named (ours)"]["remaining"][-1][0]) + "%"
        c["sim.random_left"] = pct(main["random+generic"]["remaining"][-1][0]) + "%"
        c["sim.pess_ours_left"] = pct(pess["eig+named (ours)"]["remaining"][-1][0]) + "%"
    g = _load("generation.json")
    if g.get("llm_only"):
        t = g["llm_only"]["totals"]
        c["gen.llm_valid"] = f"{t['valid_targeted']}/{t['calls']}"
    r = _load("llm_gaps_real_negatives.json")
    if r.get("methods"):
        m = r["methods"]
        c["real.exec_fcr"] = pct(m["EXEC"]["fcr_N"]) + "%"
        c["real.exec_accP"] = pct(m["EXEC"]["acc_P"]) + "%"
        c["real.n_neg"] = str(r["counts"]["N"])
        c["real.n_pos"] = str(r["counts"]["P"])
        for k in r.get("decisions", {}):
            c[f"real.{k}.fcr"] = pct(m[f"LLM:{k}"]["fcr_N"]) + "%"
            c[f"real.{k}.accP"] = pct(m[f"LLM:{k}"]["acc_P"]) + "%"
            c[f"real.{k}.ba"] = pct(m[f"LLM:{k}"]["ba"]) + "%"
            c[f"real.gated.{k}.ba"] = pct(m[f"GATED:{k}"]["ba"]) + "%"
            c[f"real.gated.{k}.accP"] = pct(m[f"GATED:{k}"]["acc_P"]) + "%"
    inv = _load("llm_gaps_inversion.json")
    if inv.get("methods"):
        for k in inv.get("decisions", {}):
            mm = inv["methods"][f"LLM:{k}"]
            if "L3" in mm:
                c[f"inv.{k}.L3"] = pct(mm["L3"]["exact_set_acc"]) + "%"
            if "ALL" in mm and mm["ALL"].get("slip_false_attribution") is not None:
                c[f"inv.{k}.slipfa"] = pct(mm["ALL"]["slip_false_attribution"]) + "%"
    tr = _load("llm_gaps_tracing.json")
    if tr.get("methods"):
        c["trace.tracer_exact"] = pct(tr["methods"]["TRACER"]["exact_set_acc"]) + "%"
        c["trace.tracer_brier"] = f"{tr['methods']['TRACER']['brier']:.3f}"
        for k in tr.get("decisions", {}):
            c[f"trace.{k}.exact"] = pct(tr["methods"][f"LLM:{k}"]["exact_set_acc"]) + "%"
            c[f"trace.{k}.brier"] = f"{tr['methods'][f'LLM:{k}']['brier']:.3f}"
            d = tr["decisions"][k]
            c[f"trace.{k}.paired_tracer"] = pct(d["tracer_exact_on_same"]) + "%"
            c[f"trace.{k}.paired_llm"] = pct(d["llm_exact"]) + "%"
    if inv.get("methods"):
        for k in inv.get("decisions", {}):
            mm = inv["methods"][f"LLM:{k}"]
            c[f"inv.{k}.all"] = pct(mm["ALL"]["exact_set_acc"]) + "%"
            u = inv["usage"][k]
            c[f"inv.{k}.cost_per_item"] = f"${u['cost_usd_estimate'] / max(1, u['calls']):.3f}"
            c[f"inv.{k}.reasoning_per_item"] = f"{round(u['reasoning_tokens'] / max(1, u['calls'])):,}"
    if r.get("usage"):
        for k, u in r["usage"].items():
            c[f"real.{k}.cost1000"] = f"${1000 * u['cost_usd_estimate'] / max(1, u['calls']):.2f}"
    pg = _load("llm_gaps_prob_pack.json")
    if pg.get("decisions"):
        for k in pg["decisions"]:
            mm = pg["methods"][f"LLM:{k}"]
            c[f"prob.gen.{k}.key"] = pct(mm["key_correct"]) + "%"
            c[f"prob.gen.{k}.bug"] = pct(mm["bug_correct"]) + "%"
            c[f"prob.gen.{k}.both"] = pct(mm["both_correct"]) + "%"
    pdg = _load("llm_gaps_prob_diag.json")
    if pdg.get("decisions"):
        c["diag.engine_coverage"] = pct(pdg["engine_coverage"]) + "%"
        for k, d in pdg["decisions"].items():
            c[f"diag.{k}.llm_acc_all"] = pct(pdg["methods"][f"LLM:{k}"]["acc_all"]) + "%"
            c[f"diag.{k}.cascade_acc_all"] = pct(pdg["methods"][f"CASCADE:{k}"]["acc_all"]) + "%"
            c[f"diag.{k}.llm_acc_bug"] = pct(pdg["methods"][f"LLM:{k}"]["acc_bug"]) + "%"
            c[f"diag.{k}.llm_slip_fa"] = pct(pdg["methods"][f"LLM:{k}"]["false_attribution_slip"]) + "%"
            c[f"diag.{k}.cost1000_llm"] = f"${d['cost_usd_per_1000_llm_only']:.2f}"
            c[f"diag.{k}.cost1000_cascade"] = f"${d['cost_usd_per_1000_cascade']:.2f}"
            if d.get("cost_saving_share") is not None:
                c[f"diag.{k}.saving"] = pct(d["cost_saving_share"]) + "%"
            if d.get("latency_s_median_llm_call") is not None:
                c[f"diag.{k}.latency_llm"] = f"{d['latency_s_median_llm_call']:.1f} s"
            if d.get("latency_s_mean_llm_only") is not None:
                c[f"diag.{k}.lat_mean_llm"] = f"{d['latency_s_mean_llm_only']:.1f} s"
                c[f"diag.{k}.lat_mean_cascade"] = f"{d['latency_s_mean_cascade']:.1f} s"
    cons = _load("llm_consistency.json")
    if cons.get("models"):
        for k, v in cons["models"].items():
            c[f"cons.{k}.agree"] = pct(v["all_runs_agree"]) + "%"
            c[f"cons.{k}.disagree"] = str(v["n_disagree"])
            if v.get("latency_s_median") is not None:
                c[f"cons.{k}.latency"] = f"{v['latency_s_median']:.1f} s"
        c["cons.n"] = str(cons["n_items"])
        c["cons.engine_ms"] = f"{cons['engine']['latency_ms_median']:.2f} ms"
    cr = _load("cascade_real.json")
    if cr.get("models"):
        c["casc.real.engine_answers"] = str(cr["engine_answers"])
        c["casc.real.n"] = str(cr["n_items"])
        for k, v in cr["models"].items():
            c[f"casc.real.{k}.ba"] = pct(v["cascade"]["ba"]) + "%"
            c[f"casc.real.{k}.cost1000_llm"] = f"${v['cost_usd_per_1000_llm_only']:.2f}"
            c[f"casc.real.{k}.cost1000_cascade"] = f"${v['cost_usd_per_1000_cascade']:.2f}"
            if v.get("cost_saving_share") is not None:
                c[f"casc.real.{k}.saving"] = pct(v["cost_saving_share"]) + "%"
    if r.get("counts"):
        c["real.p_eval"] = str(r["counts"]["P_evaluable"])
    if inv.get("ops_per_level"):
        lo, mean, hi = inv["ops_per_level"]["L3"]
        c["inv.L3.ops"] = f"{lo}–{hi}"
        c["inv.L3.ops_mean"] = f"{mean:.1f}"
    if s:
        pess = s["settings"]["pessimistic (named feedback no better: 0.10/0.10)"]
        c["sim.pess_random_left"] = pct(pess["random+generic"]["remaining"][-1][0]) + "%"
    ph = _load("llm_gaps_posthoc.json")
    if ph:
        e = ph["exact_cis"]
        for name, key in (("real.gpt-5.5.fcr_hi", "real.LLM:gpt-5.5.fcr_N"), ("real.exec.fcr_hi", "real.EXEC.fcr_N"),
                          ("real.gpt-5.4-mini.fcr_hi", "real.LLM:gpt-5.4-mini.fcr_N")):
            c[name] = pct(e[key]["exact_ci95"][1]) + "%"
        c["prob.gpt-5.5.both_lo"] = pct(e["prob.LLM:gpt-5.5.both"]["exact_ci95"][0]) + "%"
        c["inv.gpt-5.5.L3_lo"] = pct(e["inv.LLM:gpt-5.5.L3"]["exact_ci95"][0]) + "%"
        ed = ph["engine_determinism"]
        c["ph.engine_ms"] = f"{ed['latency_ms_median']:.2f} ms"
        c["ph.engine_identical"] = f"{ed['identical_outputs']}/{ed['n_items']}"
        c["ph.retry_upper"] = f"${ph['retries']['total_unrecorded_upper_bound_usd']:.2f}"
        c["ph.clusters"] = str(ph["clustered_real"]["n_clusters"])
        c["ph.trace_excluded"] = str(ph["tracing_sensitivity"]["excluded_learners"])
    spend = [_load(n).get("total_cost_usd_estimate", 0) for n in
             ("llm_gaps_real_negatives.json", "llm_gaps_inversion.json", "llm_gaps_tracing.json",
              "llm_gaps_prob_pack.json", "llm_gaps_prob_diag.json", "llm_consistency.json")]
    if all(spend):
        c["total.spend"] = f"${sum(spend):.2f}"
    return c


if __name__ == "__main__":
    for k, v in claims().items():
        print(f"{k:28s} {v}")
