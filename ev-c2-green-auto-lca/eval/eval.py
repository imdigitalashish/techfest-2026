"""End-to-end evaluation harness for the Green Auto India LCA skeleton (v2, 4 Oct 2026).

Reproduce (from ev-c2-green-auto-lca/):  python3 eval/eval.py
Writes eval/results/latest.json, eval/results/scenarios_full.json and eval/results/summary.md.

v2 changes (after the hostile-jury review): the replication metric is reported as ARITHMETIC IMPLEMENTATION
VERIFICATION (the benchmarks come from the same source as most inputs, so they cannot validate accuracy); a car
benchmark is added; every result carries its gas-basis families and a `harmonized` flag; "variance share" and "DQI"
are renamed to what they are (rank-correlation importance; pedigree screening score).
Headline scalars: verification_mape_pct_2w (ICCT 2021 Table 1, scooters) and verification_mape_pct_car (ICCT 2021
India sedans, STEPS).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "components" / "lca_engine"))
from greenauto.db import FactorDB  # noqa: E402
from greenauto.engine import load_scenarios, run_scenario  # noqa: E402

N, SEED = 10000, 20261004


def verification(res: dict, ref: dict) -> dict:
    bench = yaml.safe_load((ROOT / ref["file"]).read_text())
    rows = {r["vehicle"]: r for r in bench["results"]}
    out, errs = {"benchmark": ref["file"], "vehicles": {}}, []
    for pid, bid in ref["map"].items():
        p, r = res["products"][pid], rows[bid]
        pub = float(r[ref.get("total_key", "total")])
        pct = (p["total"] - pub) / pub
        errs.append(abs(pct))
        out["vehicles"][pid] = {"ours": round(p["total"], 2), "published": pub, "pct_error": round(100 * pct, 2)}
    out["mape_pct"] = round(100 * sum(errs) / len(errs), 3)
    return out


INDEP_KEYS = ("derived_total_gco2e_per_km", "total_gco2e_per_km", "total_gco2eq_per_km")
PT_MAP = {"petrol": "petrol_ice", "diesel": "diesel_ice", "cng": "cng_ice", "bev": "battery_electric"}


def independent_crosscheck(res: dict) -> dict:
    """Plausibility band, NOT validation: independent (non-ICCT) Indian car LCAs cover different vehicles, lifetimes
    (150,000-200,000 km), boundaries and grid years. Reports whether our central value sits inside their range."""
    pts: dict[str, list] = {}
    for f in sorted((ROOT / "data/benchmarks").glob("*.yaml")):
        d = yaml.safe_load(f.read_text())
        if not isinstance(d, dict) or not d.get("independent_of_icct"):
            continue
        for r in d.get("results", []):
            v = next((r[k] for k in INDEP_KEYS if r.get(k) is not None), None)
            if v is not None:
                pts.setdefault(r["powertrain"], []).append({"study": f.stem, "vehicle": r["vehicle"], "g_per_km": float(v)})
    out = {}
    for pid, pt in PT_MAP.items():
        if pid not in res["products"] or pt not in pts:
            continue
        p, vals = res["products"][pid], [x["g_per_km"] for x in pts[pt]]
        lo, hi = min(vals), max(vals)
        out[pid] = {"ours": round(p["total"], 1), "ours_90pct": [round(p["mc_total"]["p05"], 1), round(p["mc_total"]["p95"], 1)],
                    "independent_range": [lo, hi], "n_independent": len(vals), "inside": lo <= p["total"] <= hi,
                    "interval_overlaps": p["mc_total"]["p05"] <= hi and p["mc_total"]["p95"] >= lo, "points": pts[pt]}
    return out


def summarise(r: dict) -> dict:
    prods = {pid: {"label": p["label"], "total": round(p["total"], 2),
                   "p05": round(p["mc_total"]["p05"], 2), "p95": round(p["mc_total"]["p95"], 2),
                   "dq_score": round(p["dq_score"], 2), "india_weighted_share": round(p["india_weighted_share"], 2),
                   "gas_basis_shares": {k: round(v, 3) for k, v in p["gas_basis_shares"].items()}}
             for pid, p in r["products"].items()}
    comps = {pid: {"vs": c["vs"], "reduction_central": round(c["reduction_central"], 4),
                   "reduction_90pct": [round(c["reduction_mc"]["p05"], 4), round(c["reduction_mc"]["p95"], 4)],
                   "p_lower": round(c["p_lower"], 4),
                   "top_importance": [[k, round(v, 3)] for k, v in list(c["importance"].items())[:4]]}
             for pid, c in r["comparisons"].items()}
    return {"label": r["label"], "case": r["case"], "kind": r["kind"], "harmonized": r["harmonized"],
            "gas_basis_families": r["gas_basis_families"], "products": prods, "comparisons": comps}


def main() -> None:
    db = FactorDB.load()
    scenarios = load_scenarios()
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    # mark the run dirty if any input (code, data, scenarios) differs from HEAD; generated outputs are excluded
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "components", "data", "eval/eval.py"],
                           capture_output=True, text=True, cwd=ROOT).stdout.strip()
    if dirty:
        commit += "-dirty"
    results = {sid: run_scenario(db, sc, n=N, seed=SEED) for sid, sc in scenarios.items()}
    report = {"harness": "v2", "commit": commit, "n": N, "seed": SEED, "db": db.summary(),
              "verification": {}, "scenarios": {}}
    for sid, sc in scenarios.items():
        if sc.kind == "replication" and sc.reference:
            report["verification"][sid] = verification(results[sid], sc.reference)
        report["scenarios"][sid] = summarise(results[sid])
    report["independent_crosscheck"] = {"scenario": "car_in2026_avg_co2e",
                                        "note": "plausibility band, not validation (different vehicles, lifetimes, boundaries, grid years)",
                                        "results": independent_crosscheck(results["car_in2026_avg_co2e"])}
    report["headline"] = {"verification_mape_pct_2w": report["verification"]["icct2021_implied"]["mape_pct"],
                          "verification_mape_pct_car": report["verification"]["car_icct2021_replication"]["mape_pct"]}
    out = ROOT / "eval" / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "latest.json").write_text(json.dumps(report, indent=2))
    (out / "scenarios_full.json").write_text(json.dumps(results, indent=1, default=float))
    d = report["db"]
    L = [f"# Eval results (harness v2, code commit {commit}, n={N}, seed={SEED})", "",
         "Reproduce: `python3 eval/eval.py` from `ev-c2-green-auto-lca/`. Unit: g per vehicle-km (GHG indicator; see gas-basis flags).",
         f"Database: {d['records']} records ({d['by_status']}), {d['sources']} sources.", "",
         "## Arithmetic implementation verification (NOT validation: same source supplies inputs and targets)", "",
         "| Scenario | Vehicle | Ours | Published | Error % |", "|---|---|---|---|---|"]
    for sid, v in report["verification"].items():
        for pid, x in v["vehicles"].items():
            L.append(f"| {sid} | {pid} | {x['ours']:.2f} | {x['published']} | {x['pct_error']:+.2f} |")
        L.append(f"| {sid} | **MAPE** | | | **{v['mape_pct']}** |")
    for case in dict.fromkeys(s["case"] for s in report["scenarios"].values()):
        L += ["", f"## {case} — decision and sensitivity scenarios (paired Monte Carlo, 90 % intervals)", ""]
        for sid, s in report["scenarios"].items():
            if s["case"] != case or s["kind"] == "replication":
                continue
            flag = "harmonized" if s["harmonized"] else f"NOT harmonized ({', '.join(s['gas_basis_families'])})"
            L += [f"**{sid}** [{s['kind']}] — {s['label']} — _{flag}_", "",
                  "| Vehicle | Total [90 %] | vs reference: reduction [90 %] | P(lower) | Pedigree score |", "|---|---|---|---|---|"]
            for pid, p in s["products"].items():
                c = s["comparisons"].get(pid)
                cmp = f"{100*c['reduction_central']:.1f} % [{100*c['reduction_90pct'][0]:.1f} – {100*c['reduction_90pct'][1]:.1f} %]" if c else "reference"
                pl = f"{c['p_lower']:.3f}" if c else ""
                L.append(f"| {p['label']} | {p['total']:.1f} [{p['p05']:.1f} – {p['p95']:.1f}] | {cmp} | {pl} | {p['dq_score']} |")
            L.append("")
    L += ["## Independent plausibility check — Indian cars (NOT validation)", "",
          "Our central sedan case (`car_in2026_avg_co2e`) against independent, non-ICCT Indian car LCAs (TERI 2026, IIT Guwahati 2025, IIT Kanpur 2023): different vehicles, lifetimes (150,000–200,000 km), boundaries and grid years.", "",
          "| Powertrain | Ours [90 %] | Independent range (n) | Central inside? |", "|---|---|---|---|"]
    for pid, x in report["independent_crosscheck"]["results"].items():
        L.append(f"| {pid} | {x['ours']} [{x['ours_90pct'][0]} – {x['ours_90pct'][1]}] | {x['independent_range'][0]} – {x['independent_range'][1]} ({x['n_independent']}) | {'yes' if x['inside'] else 'NO'} |")
    L += ["", "Pedigree score = elasticity-weighted mean pedigree score (1 best … 5 worst), a screening indicator.",
          "Importance = normalized squared Spearman rank correlation (screening, not a variance decomposition) — see latest.json."]
    (out / "summary.md").write_text("\n".join(L) + "\n")
    print(json.dumps(report["headline"]))


if __name__ == "__main__":
    main()
