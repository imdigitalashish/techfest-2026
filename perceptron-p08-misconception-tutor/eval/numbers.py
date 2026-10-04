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
        for k in tr.get("decisions", {}):
            c[f"trace.{k}.exact"] = pct(tr["methods"][f"LLM:{k}"]["exact_set_acc"]) + "%"
    return c


if __name__ == "__main__":
    for k, v in claims().items():
        print(f"{k:28s} {v}")
