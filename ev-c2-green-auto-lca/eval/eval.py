"""FROZEN end-to-end evaluation for the Green Auto India LCA skeleton. Do not edit inside a ratchet loop.

Reproduce (from ev-c2-green-auto-lca/):  python3 eval/eval.py
Writes eval/results/latest.json and eval/results/summary.md; prints the headline scalar:
  replication_mape = mean absolute % error of per-vehicle totals vs ICCT (2021) Table 1, scenario icct2021_implied.
Secondary metrics: per-stage absolute errors, reduction error, stated-input inconsistency, India-2026 results with
paired Monte Carlo (n=10000, seed 20261004), data-quality index and data-gap ranking.
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
STAGE_MAP = {"vehicle_production": "vehicle_production", "battery_production": "battery_production",
             "fuel_production_wtt": "wtt", "electricity_production_wtt": "wtt", "tailpipe_ttw": "ttw"}


def replication(res: dict, ref: dict, ice_ref: str, bev_ref: str) -> dict:
    rows = {r["vehicle"]: r for r in ref["results"]}
    out = {"vehicles": {}}
    errs = []
    for pid, rid in (("ice_scooter", ice_ref), ("ev_scooter", bev_ref)):
        p, r = res["products"][pid], rows[rid]
        stage_err = {s: round(v - r[STAGE_MAP[s]], 3) for s, v in p["stages"].items()}
        pct = (p["total"] - r["total"]) / r["total"]
        errs.append(abs(pct))
        out["vehicles"][pid] = {"ours": round(p["total"], 3), "published": r["total"], "pct_error": round(100 * pct, 2),
                                "stage_abs_error_g_per_km": stage_err,
                                "published_inside_our_90pct": p["mc_total"]["p05"] <= r["total"] <= p["mc_total"]["p95"]}
    out["mape_pct"] = round(100 * sum(errs) / len(errs), 3)
    pub_red = rows[bev_ref]["saving_vs_ice"]
    out["reduction"] = {"ours": round(res["comparison"]["reduction_central"], 4), "published": pub_red,
                        "abs_error_pp": round(100 * (res["comparison"]["reduction_central"] - pub_red), 2)}
    return out


def main() -> None:
    db = FactorDB.load()
    scenarios = load_scenarios()
    ref = yaml.safe_load((ROOT / "data/benchmarks/icct_2w_india_2021_table1.yaml").read_text())
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    results = {sid: run_scenario(db, sc, n=N, seed=SEED) for sid, sc in scenarios.items()}
    report = {"commit": commit, "n": N, "seed": SEED, "db": db.summary(), "replication": {}, "india_2026": {}}
    for sid in ("icct2021_implied", "icct2021_stated"):
        report["replication"][sid] = replication(results[sid], ref, "ice_scooter", "ev_scooter_2p9kwh")
    for sid in [s for s in results if s.startswith("in2026")]:
        r = results[sid]
        c = r["comparison"]
        report["india_2026"][sid] = {
            "label": r["label"],
            "ice_total": round(r["products"]["ice_scooter"]["total"], 2),
            "ice_90pct": [round(r["products"]["ice_scooter"]["mc_total"][k], 2) for k in ("p05", "p95")],
            "bev_total": round(r["products"]["ev_scooter"]["total"], 2),
            "bev_90pct": [round(r["products"]["ev_scooter"]["mc_total"][k], 2) for k in ("p05", "p95")],
            "reduction_central": round(c["reduction_central"], 4),
            "reduction_90pct": [round(c["reduction_mc"][k], 4) for k in ("p05", "p95")],
            "p_bev_lower": round(c["p_bev_lower"], 4),
            "dqi_ice": round(r["products"]["ice_scooter"]["dqi"], 2),
            "dqi_bev": round(r["products"]["ev_scooter"]["dqi"], 2),
            "top_variance_drivers_of_reduction": [[k, round(v, 3)] for k, v in list(c["variance_share_of_reduction"].items())[:5]],
        }
    headline = report["replication"]["icct2021_implied"]["mape_pct"]
    report["headline"] = {"replication_mape_pct": headline}
    out = ROOT / "eval" / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "latest.json").write_text(json.dumps(report, indent=2))
    (out / "scenarios_full.json").write_text(json.dumps(results, indent=1, default=float))
    lines = [f"# Eval results (commit {commit}, n={N}, seed={SEED})", "",
             "Reproduce: `python3 eval/eval.py` from `ev-c2-green-auto-lca/`. Units: g CO2e per vehicle-km.", "",
             "## Replication of ICCT (2021) Table 1 — Indian scooters", "",
             "| Scenario | ICE ours / published | BEV ours / published | MAPE % | Reduction ours / published |", "|---|---|---|---|---|"]
    for sid, rp in report["replication"].items():
        v = rp["vehicles"]
        lines.append(f"| {sid} | {v['ice_scooter']['ours']:.2f} / {v['ice_scooter']['published']} | "
                     f"{v['ev_scooter']['ours']:.2f} / {v['ev_scooter']['published']} | {rp['mape_pct']} | "
                     f"{100*rp['reduction']['ours']:.1f}% / {100*rp['reduction']['published']:.1f}% |")
    lines += ["", "## India 2026 case study (paired Monte Carlo, 90% intervals)", "",
              "| Scenario | ICE total [90%] | BEV total [90%] | Reduction [90%] | P(BEV<ICE) | DQI ICE / BEV |", "|---|---|---|---|---|---|"]
    for sid, x in report["india_2026"].items():
        lines.append(f"| {sid} | {x['ice_total']} [{x['ice_90pct'][0]}–{x['ice_90pct'][1]}] | {x['bev_total']} "
                     f"[{x['bev_90pct'][0]}–{x['bev_90pct'][1]}] | {100*x['reduction_central']:.1f}% "
                     f"[{100*x['reduction_90pct'][0]:.1f}–{100*x['reduction_90pct'][1]:.1f}%] | {x['p_bev_lower']} | "
                     f"{x['dqi_ice']} / {x['dqi_bev']} |")
    lines += ["", "DQI = elasticity-weighted mean pedigree score (1 best … 5 worst).", "",
              "## Top variance drivers of the reduction (in2026_cea_average)", ""]
    for k, v in report["india_2026"]["in2026_cea_average"]["top_variance_drivers_of_reduction"]:
        lines.append(f"- `{k}` — {100*v:.1f}% of rank-variance")
    (out / "summary.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(report["headline"]))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
