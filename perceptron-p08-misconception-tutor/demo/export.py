"""Export the demo's data (demo/web/data.js) from committed results: DERIVED OUTCOMES ONLY.

Licence rule (Kaggle "Eedi - Mining Misconceptions in Mathematics", CC BY-NC 4.0, competition rules §7.B):
no Eedi item text (questions, answers, distractors, or expressions parsed from them) and no Kaggle label ids or
names are written here. Real items carry only: item id, group (P/N/S), our pack code for the gold label, the
engine's claim, evaluable / n_matched flags, each model's code per run, and per-item token counts and cost.
Probability items are our own (components/bugs/probability.py), so their text is included.

Run (from the project folder; the real items' derived fields need the local .data/ copy once):
    .venv/bin/python -m demo.export            # writes demo/web/data.js
    .venv/bin/python -m demo.export --check    # rebuild in memory and compare with the committed data.js
Every aggregate is checked against the committed result files before writing (raises on any mismatch).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from pathlib import Path

from components.bugs import probability as prob
from components.bugs.school_math import CODES
from demo import live
from eval import numbers
from eval.run_llm_gaps import MODELS, RES, RULES, cost_of, load_store, parse_json, parse_real, r4, sha

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "demo" / "web" / "data.js"
PREFIX = "window.P8 = "
MODEL_ORDER = ("gpt-5.5", "gpt-5.4-mini", "gpt-4.1-mini")
INPUTS = ("llm_gaps_real_negatives.json", "llm_gaps_real_negatives_responses.jsonl", "llm_consistency.json",
          "llm_consistency_responses.jsonl", "cascade_real.json", "llm_gaps_posthoc.json", "llm_gaps_prob_diag.json",
          "llm_gaps_prob_diag_responses.jsonl", "llm_gaps_prob_pack.json", "llm_gaps_inversion.json",
          "llm_gaps_tracing.json", "simulation.json", "generation.json")
ILLUSTRATIONS = {"LTR": ("3 + 4 \u00d7 2", "14"), "SQ_DOUBLE": ("5\u00b2 + 3", "13"), "SUB_NEG": ("7 \u2212 (\u22122)", "5"),
                 "FRAC_ADD": ("1/8 + 1/8", "2/16"), "NEG_TIMES_NEG": ("(\u22123) \u00d7 (\u22124) + 2", "-10")}


def _json(name: str):
    return json.loads((RES / name).read_text())


def _code(content: str) -> str:
    return parse_real(content) or "NONE"


def _reasoning(u) -> int:
    return int(((u or {}).get("completion_tokens_details") or {}).get("reasoning_tokens", 0) or 0)


def _check(label: str, got, want, tol: float = 5e-5) -> None:
    if isinstance(want, float) or isinstance(got, float):
        ok = abs(float(got) - float(want)) <= tol
    else:
        ok = got == want
    if not ok:
        raise AssertionError(f"export check failed: {label}: computed {got!r} != committed {want!r}")


# ---- REAL items (needs .data/ for group/gold/engine; outputs derived fields only) -----------------------------------
def real_rows() -> list[dict]:
    from eval.run_llm_gaps import build_real

    items = build_real()
    store = load_store("real_negatives")
    rows = []
    for it in items:
        row = {"id": it["item_id"], "g": {"P": "P", "N": "N", "S_related": "S"}[it["group"]], "gold": it["gold"],
               "rel": it["related"], "ev": bool(it["evaluable"]), "nm": int(it["n_matched"]), "eng": it["exec"],
               "llm": {}, "usd": {}, "rt": {}}
        for m in MODEL_ORDER:
            r = store[(m, it["item_id"], sha(it["prompt"]))]
            row["llm"][m] = _code(r["content"])
            row["usd"][m] = round(cost_of(r.get("usage"), m), 7)
            row["rt"][m] = _reasoning(r.get("usage"))
        rows.append(row)
    rows.sort(key=lambda r: ({"P": 0, "N": 1, "S": 2}[r["g"]], r["id"]))
    return rows


def consistency(rows: list[dict]) -> dict:
    by = {r["id"]: r for r in rows}
    runs: dict = {}
    lat: dict = {}
    for line in (RES / "llm_consistency_responses.jsonl").read_text().splitlines():
        d = json.loads(line)
        runs.setdefault(d["item_id"], {}).setdefault(d["model"], {})[d["run"]] = _code(d["content"])
        lat.setdefault(d["item_id"], {}).setdefault(d["model"], {})[d["run"]] = d.get("latency_s")
    out = {}
    for iid in sorted(runs):
        out[iid] = {}
        for m in MODEL_ORDER:
            rr = {1: by[iid]["llm"][m], **runs[iid][m]}
            out[iid][m] = {"codes": [rr[k] for k in sorted(rr)],
                           "latency_s": [None] + [round(lat[iid][m][k], 2) if lat[iid][m][k] is not None else None
                                                  for k in sorted(runs[iid][m])]}
    committed = _json("llm_consistency.json")
    for m in MODEL_ORDER:
        n_dis = sum(1 for iid in out if len(set(out[iid][m]["codes"])) > 1)
        _check(f"consistency {m} n_disagree", n_dis, committed["models"][m]["n_disagree"])
        _check(f"consistency {m} runs", len(out[next(iter(out))][m]["codes"]), committed["models"][m]["runs"])
    _check("consistency n_items", len(out), committed["n_items"])
    return out


def _metrics(rows, pred) -> dict:
    P = [r for r in rows if r["g"] == "P"]
    N = [r for r in rows if r["g"] == "N"]
    k_pos = sum(1 for r in P if pred[r["id"]] == r["gold"])
    k_fc = sum(1 for r in N if pred[r["id"]] != "NONE")
    acc, fcr = k_pos / len(P), k_fc / len(N)
    return {"k_pos": k_pos, "n_pos": len(P), "acc_pos": r4(acc), "k_fc": k_fc, "n_neg": len(N), "fcr": r4(fcr),
            "ba": r4((acc + 1 - fcr) / 2)}


ROUTINGS_REAL = ("llm", "cascade", "gated", "engine")


def real_grid(rows: list[dict]) -> list[dict]:
    real = _json("llm_gaps_real_negatives.json")
    casc = _json("cascade_real.json")
    n = len(rows)
    out = []
    for m in MODEL_ORDER:
        for rt in ROUTINGS_REAL:
            pred, called = {}, {}
            for r in rows:
                e, llm = r["eng"], r["llm"][m]
                pred[r["id"]], called[r["id"]] = {
                    "llm": (llm, True), "cascade": (e if e != "NONE" else llm, e == "NONE"),
                    "gated": (e if r["ev"] else llm, not r["ev"]), "engine": (e, False)}[rt]
            met = _metrics(rows, pred)
            cost = sum(r["usd"][m] for r in rows if called[r["id"]])
            calls = sum(1 for r in rows if called[r["id"]])
            cell = {"workload": "real", "model": m, "routing": rt, **met, "calls": calls,
                    "calls1000": r4(1000 * calls / n), "usd1000": r4(1000 * cost / n),
                    "no_diagnosis": sum(1 for r in rows if pred[r["id"]] == "NONE"), "n": n}
            committed = {"llm": f"LLM:{m}", "cascade": f"HYB:{m}", "gated": f"GATED:{m}", "engine": "EXEC"}[rt]
            for k_ours, k_c in (("acc_pos", "acc_P"), ("fcr", "fcr_N"), ("ba", "ba")):
                _check(f"real {m} {rt} {k_ours}", cell[k_ours], real["methods"][committed][k_c])
            cell["source"] = f"llm_gaps_real_negatives.json methods['{committed}']"
            if rt == "llm":
                _check(f"real {m} llm usd1000", cell["usd1000"], casc["models"][m]["cost_usd_per_1000_llm_only"])
                cell["usd_source"] = "cascade_real.json cost_usd_per_1000_llm_only"
            elif rt == "cascade":
                _check(f"real {m} cascade usd1000", cell["usd1000"], casc["models"][m]["cost_usd_per_1000_cascade"])
                _check("real cascade calls1000", cell["calls1000"], casc["llm_calls_per_1000"])
                cell["usd_source"] = "cascade_real.json cost_usd_per_1000_cascade"
            elif rt == "gated":
                cell["usd_source"] = "computed by demo/export.py from per-item committed usage (not a committed aggregate)"
            else:
                cell["usd_source"] = "no LLM call"
            out.append(cell)
    _check("engine answers", sum(1 for r in rows if r["eng"] != "NONE"), casc["engine_answers"])
    return out


# ---- tutor-native probability items (ours; SYNTHETIC; Addendum B) ---------------------------------------------------
def prob_rows() -> tuple[list[dict], float]:
    from eval.run_prob_pack import slip_of

    diag = _json("llm_gaps_prob_diag.json")
    store = load_store("prob_diag")
    by_key = {(k[0], k[1]): v for k, v in store.items()}
    rows = []
    for it in prob.build():
        for kind, ans, gold in (("bug", it.bug, it.code), ("slip", slip_of(it), "NONE")):
            iid = f"{it.item_id}-{kind}"
            row = {"id": iid, "code": it.code, "family": it.family, "kind": kind, "gold": gold, "stem": it.stem,
                   "key": prob.canon(it.key), "answer": prob.canon(ans), "eng": it.code if ans == it.bug else "NONE",
                   "llm": {}, "usd": {}, "lat": {}, "rt": {}}
            for m in MODEL_ORDER:
                r = by_key[(m, iid)]
                d = parse_json(r["content"])
                code = str(d.get("code", "")).strip().upper() if isinstance(d, dict) else ""
                row["llm"][m] = code if (code in prob.CODES or code == "NONE") else "NONE"
                row["usd"][m] = round(cost_of(r.get("usage"), m), 7)
                row["lat"][m] = r.get("latency_s")
                row["rt"][m] = _reasoning(r.get("usage"))
            rows.append(row)
    _check("prob n_items", len(rows), diag["n_items"])
    return rows, diag["engine_latency_ms_median"]


ROUTINGS_PROB = ("llm", "cascade", "engine")


def prob_grid(rows: list[dict], engine_ms: float) -> list[dict]:
    diag = _json("llm_gaps_prob_diag.json")
    n = len(rows)
    out = []
    for m in MODEL_ORDER:
        for rt in ROUTINGS_PROB:
            pred, called = {}, {}
            for r in rows:
                e, llm = r["eng"], r["llm"][m]
                pred[r["id"]], called[r["id"]] = {"llm": (llm, True), "cascade": (e if e != "NONE" else llm, e == "NONE"),
                                                  "engine": (e, False)}[rt]
            bug = [r for r in rows if r["kind"] == "bug"]
            slip = [r for r in rows if r["kind"] == "slip"]
            k_pos = sum(1 for r in bug if pred[r["id"]] == r["gold"])
            k_fc = sum(1 for r in slip if pred[r["id"]] != "NONE")
            acc_all = sum(1 for r in rows if pred[r["id"]] == r["gold"]) / n
            calls = sum(1 for r in rows if called[r["id"]])
            cost = sum(r["usd"][m] for r in rows if called[r["id"]])
            lats = [(r["lat"][m] if called[r["id"]] else engine_ms / 1e3) for r in rows]
            cell = {"workload": "prob", "model": m, "routing": rt, "k_pos": k_pos, "n_pos": len(bug),
                    "acc_pos": r4(k_pos / len(bug)), "k_fc": k_fc, "n_neg": len(slip), "fcr": r4(k_fc / len(slip)),
                    "ba": r4(acc_all), "calls": calls, "calls1000": r4(1000 * calls / n), "usd1000": r4(1000 * cost / n),
                    "lat_mean_s": r4(statistics.mean(lats)), "no_diagnosis": sum(1 for r in rows if pred[r["id"]] == "NONE"),
                    "n": n}
            committed = {"llm": f"LLM:{m}", "cascade": f"CASCADE:{m}", "engine": "ENGINE(abstain->NONE)"}[rt]
            cm = diag["methods"][committed]
            _check(f"prob {m} {rt} acc_all", cell["ba"], cm["acc_all"])
            _check(f"prob {m} {rt} acc_bug", cell["acc_pos"], cm["acc_bug"])
            _check(f"prob {m} {rt} slip_fa", cell["fcr"], cm["false_attribution_slip"])
            cell["source"] = f"llm_gaps_prob_diag.json methods['{committed}']"
            dec = diag["decisions"][m]
            if rt == "llm":
                _check(f"prob {m} llm usd1000", cell["usd1000"], dec["cost_usd_per_1000_llm_only"])
                _check(f"prob {m} llm latency", cell["lat_mean_s"], dec["latency_s_mean_llm_only"], tol=1e-3)
                cell["usd_source"] = "llm_gaps_prob_diag.json decisions cost_usd_per_1000_llm_only"
            elif rt == "cascade":
                _check(f"prob {m} cascade usd1000", cell["usd1000"], dec["cost_usd_per_1000_cascade"])
                _check(f"prob {m} cascade latency", cell["lat_mean_s"], dec["latency_s_mean_cascade"], tol=1e-3)
                _check(f"prob {m} cascade calls1000", cell["calls1000"], dec["H8b_llm_calls_per_1000_cascade"])
                cell["usd_source"] = "llm_gaps_prob_diag.json decisions cost_usd_per_1000_cascade"
            else:
                cell["usd_source"] = "no LLM call"
            out.append(cell)
    return out


# ---- SYNTHETIC summaries --------------------------------------------------------------------------------------------
def synthetic() -> dict:
    inv, tr, sim, pp = _json("llm_gaps_inversion.json"), _json("llm_gaps_tracing.json"), _json("simulation.json"), \
        _json("llm_gaps_prob_pack.json")
    inversion = {"ops_per_level": inv["ops_per_level"], "exec": {lv: inv["methods"]["EXEC"][lv]["exact_set_acc"]
                                                                 for lv in ("L1", "L2", "L3")}, "models": {}}
    for m in MODEL_ORDER:
        mm, u = inv["methods"][f"LLM:{m}"], inv["usage"][m]
        inversion["models"][m] = {
            "levels": {lv: {"acc": mm[lv]["exact_set_acc"], "n": mm[lv]["n"]} for lv in ("L1", "L2", "L3") if lv in mm},
            "slip_false_attribution": mm["ALL"].get("slip_false_attribution"),
            "reasoning_per_call": round(u["reasoning_tokens"] / max(1, u["calls"])),
            "usd_per_call": round(u["cost_usd_estimate"] / max(1, u["calls"]), 4), "calls": u["calls"]}
    tracing = {"tracer": tr["methods"]["TRACER"]["exact_set_acc"], "n": tr["methods"]["TRACER"]["n"],
               "models": {m: {"exact": tr["methods"][f"LLM:{m}"]["exact_set_acc"], "n": tr["methods"][f"LLM:{m}"]["n"],
                              "paired_tracer": tr["decisions"][m]["tracer_exact_on_same"],
                              "paired_llm": tr["decisions"][m]["llm_exact"]} for m in MODEL_ORDER}}
    keep = ("random+generic", "eig+named (ours)")
    simulation = {"label": sim["label"], "settings": {
        name: {pol: [round(x[0], 4) for x in v["remaining"]] for pol, v in s.items() if pol in keep}
        for name, s in sim["settings"].items()
        if name.startswith("main") or name.startswith("pessimistic")}}
    gen = {m: {"both": pp["methods"][f"LLM:{m}"]["both_correct"], "key": pp["methods"][f"LLM:{m}"]["key_correct"],
               "n": pp["methods"][f"LLM:{m}"]["n"]} for m in MODEL_ORDER}
    return {"inversion": inversion, "tracing": tracing, "simulation": simulation, "prob_gen": gen}


def illustrations() -> dict:
    out = {}
    for code, (expr, ans) in ILLUSTRATIONS.items():
        toks = live.tokens_from(expr)
        c = live.certify(toks, ans)
        assert c["verdict"] == "certificate" and [code] in [x["rules"] for x in c["certificates"]], (code, c["verdict"])
        cert = next(x for x in c["certificates"] if x["rules"] == [code])
        out[code] = {"expression": c["question"]["expression"], "answer": live.canon_display(ans) if "/" not in ans else ans,
                     "key": c["question"]["key_display"], "steps": cert["steps"], "clean_steps": cert["clean_steps"]}
    return out


def build() -> dict:
    rows = real_rows()
    prows, engine_ms = prob_rows()
    posthoc = _json("llm_gaps_posthoc.json")
    real = _json("llm_gaps_real_negatives.json")
    cons = _json("llm_consistency.json")
    data = {
        "schema": 1,
        "notice": "Derived outcomes only. No Eedi item text, no Kaggle label ids or names (CC BY-NC 4.0; rules \u00a77.B).",
        "provenance": {"command": "python -m demo.export",
                       "inputs_sha256": {n: hashlib.sha256((RES / n).read_bytes()).hexdigest()[:16] for n in INPUTS}},
        "claims": numbers.claims(),
        "rules": live.rule_info(),
        "prompt_rules": RULES,
        "models": {m: {"effort": MODELS[m]["effort"], "price_per_1m": list(MODELS[m]["price"])} for m in MODEL_ORDER},
        "real": {"counts": real["counts"], "items": rows, "consistency": consistency(rows),
                 "consistency_summary": {m: {k: cons["models"][m][k] for k in ("runs", "all_runs_agree", "n_disagree",
                                                                               "latency_s_median")} for m in MODEL_ORDER},
                 "engine_determinism": posthoc["engine_determinism"],
                 "exact_cis": {k: v for k, v in posthoc["exact_cis"].items() if k.startswith("real.")}},
        "prob": {"items": prows, "engine_latency_ms_median": engine_ms,
                 "label": "SYNTHETIC tutor-native items (ours); engine routing guaranteed by construction (Addendum B)"},
        "grid": real_grid(rows) + prob_grid(prows, engine_ms),
        "synthetic": synthetic(),
        "illustrations": illustrations(),
    }
    return data


def render(data: dict) -> str:
    return PREFIX + json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + ";\n"


def load(path: Path = OUT) -> dict:
    txt = path.read_text(encoding="utf-8")
    assert txt.startswith(PREFIX)
    return json.loads(txt[len(PREFIX):].rstrip().rstrip(";"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="rebuild in memory and compare with the committed data.js")
    a = ap.parse_args(argv)
    txt = render(build())
    if a.check:
        same = OUT.exists() and OUT.read_text(encoding="utf-8") == txt
        print("data.js matches a fresh export" if same else "data.js DIFFERS from a fresh export")
        return 0 if same else 1
    OUT.write_text(txt, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(txt.encode()) / 1e3:.0f} kB); all aggregates match committed results")
    return 0


if __name__ == "__main__":
    sys.exit(main())
