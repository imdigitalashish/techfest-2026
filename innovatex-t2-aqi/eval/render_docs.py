"""Render the Round-1 deliverables from templates + committed results (single source of truth for every run number).

Templates: deliverables/src/*.md → deliverables/*.md. Placeholders:
  {{n:KEY}}        a number from our committed runs (KEYS below)
  {{v:ID|text}}    cited text; every number in `text` must appear in row ID of research/fact-check.md (checked by check_docs.py)
  {{table:NAME}}   a table rendered from committed data (bom, power)
Run (from innovatex-t2-aqi/): python3 eval/render_docs.py        → writes the rendered docs
                              python3 eval/render_docs.py --keys → prints every KEY = value
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "deliverables" / "src"
OUT = ROOT / "deliverables"
TEMPLATES = ["zonal-deck.md", "qa-prep.md", "presenter-card.md", "zonal-pitch.md", "prototype-plan.md"]
PH = re.compile(r"\{\{(n|v|table):([^}|]+)(?:\|([^}]*))?\}\}")


def f1(x):
    return f"{x:.1f}"


def pct0(x):
    return f"{round(100 * x):.0f}"


def sgn1(x):
    return f"{x:.1f}".replace("-", "−")


def inr(x):
    return f"{int(round(x)):,}"


def keys() -> dict[str, str]:
    k: dict[str, str] = {}
    fw = json.loads((ROOT / "eval" / "results" / "forecast_walkforward.json").read_text())
    for r in fw["results"]:
        t = r["target"]
        m = r["models"]
        k[f"fc_n_{t}"] = f"{r['n_test']:,}"
        k[f"fc_persist_{t}"] = f1(m["persistence"]["all"]["MAE"])
        k[f"fc_persist_r_{t}"] = f"{m['persistence']['all']['r']:.2f}"
        k[f"fc_persist_winter_{t}"] = f1(m["persistence"]["winter_nov_feb"]["MAE"])
        k[f"fc_cams_{t}"] = f1(m["cams_as_served_reference"]["all"]["MAE"])
        nf = ("gbm_level_no_future_met", "gbm_logratio_no_future_met")
        best_nf = max(nf, key=lambda x: m[x]["skill_vs_persistence_MAE"])
        k[f"fc_nofuture_best_pct_{t}"] = sgn1(100 * m[best_nf]["skill_vs_persistence_MAE"])
        k[f"fc_nofuture_worst_pct_{t}"] = sgn1(100 * min(m[x]["skill_vs_persistence_MAE"] for x in nf))
        k[f"fc_nofuture_best_winter_pct_{t}"] = sgn1(100 * m[best_nf]["winter_skill_vs_persistence_MAE"])
        k[f"fc_oracle_pct_{t}"] = sgn1(100 * m["gbm_logratio_perfect_prog_met"]["skill_vs_persistence_MAE"])
        k[f"fc_nofuture_mae_{t}"] = f1(m["gbm_logratio_no_future_met"]["all"]["MAE"])
        k[f"fc_oracle_mae_{t}"] = f1(m["gbm_logratio_perfect_prog_met"]["all"]["MAE"])
        k[f"fc_persist_csi_{t}"] = f"{m['persistence']['all']['severe']['CSI']:.2f}"
    bd = json.loads((ROOT / "components" / "attribution" / "autoresearch" / "breakdown_v21.json").read_text())["methods"]
    short = {"pair_fixed": "pair", "ring": "ring", "ring_refcal": "refcal", "ring_refcal14": "refcal14", "ring_selfcal": "selfcal"}
    for meth, sh in short.items():
        v = bd[meth]
        k[f"at_{sh}"] = f1(v["mae_all"])
        k[f"at_work_{sh}"] = f1(v["mae_work"])
        k[f"at_diff_{sh}"] = f1(v["mae_diff_cov"])
        k[f"at_csi_{sh}"] = f"{v['csi_gt50']:.2f}"
        k[f"at_cov_{sh}"] = f"{v['coverage']:.2f}"
        k[f"at_covwork_{sh}"] = f"{v['coverage_work']:.2f}"
        k[f"at_pod_{sh}"] = f"{v['pod_gt50']:.3f}"
        k[f"at_far_{sh}"] = f"{v['far_gt50']:.3f}"
        for sc, val in v["per_scenario_mae_all"].items():
            k[f"at_{sh}_{sc.replace('-', '')}"] = f1(val)
    k["at_cov"] = k["at_cov_selfcal"]
    k["at_gain_selfcal_vs_refcal14_pct"] = pct0(1 - bd["ring_selfcal"]["mae_all"] / bd["ring_refcal14"]["mae_all"])
    k["at_gain_selfcal_vs_refcal_pct"] = pct0(1 - bd["ring_selfcal"]["mae_all"] / bd["ring_refcal"]["mae_all"])
    k["at_gain_ring_vs_pair_pct"] = pct0(1 - bd["ring"]["mae_all"] / bd["pair_fixed"]["mae_all"])
    k["at_gain_work_selfcal_vs_refcal14_pct"] = sgn1(100 * (1 - bd["ring_selfcal"]["mae_work"] / bd["ring_refcal14"]["mae_work"]))
    cw = json.loads((ROOT / "eval" / "results" / "calm_wind.json").read_text())
    k["calm_lt05_winter_pct"] = f1(100 * cw["nov_jan"]["share_lt_0_5"])
    k["calm_lt10_winter_pct"] = f1(100 * cw["nov_jan"]["share_lt_1_0"])
    k["calm_lt15_winter_pct"] = f1(100 * cw["nov_jan"]["share_lt_1_5"])
    k["calm_lt10_all_pct"] = f1(100 * cw["all"]["share_lt_1_0"])
    k["calm_median_winter"] = f1(cw["nov_jan"]["median_ms"])
    bt = json.loads((ROOT / "deliverables" / "bom" / "bom_total.json").read_text())
    k["bom_kit"] = inr(bt["kit_total_inr"])
    k["bom_node"] = inr(bt["per_node_inr"])
    k["bom_nodes4"] = inr(bt["by_subsystem_inr"]["node"])
    k["bom_wind"] = inr(bt["by_subsystem_inr"]["wind"])
    k["bom_gateway"] = inr(bt["by_subsystem_inr"]["gateway"])
    k["bom_actuator"] = inr(bt["by_subsystem_inr"]["actuator"])
    k["bom_wind_share_pct"] = pct0(bt["wind_share_of_total"])
    rc = json.loads((ROOT / "deliverables" / "demo" / "ranking_check.json").read_text())
    k["demo_rho"] = f"{rc['spearman_rho']:.2f}"
    k["demo_top5"] = str(rc["top5_overlap"])
    pw = json.loads((ROOT / "deliverables" / "bom" / "power_budget.json").read_text())
    k["pw_load"] = f1(pw["load_wh_per_day"])
    k["pw_margin"] = f1(pw["worst_month_margin"])
    k["pw_autonomy"] = f1(pw["autonomy_days_no_sun"])
    k["pw_dec_gen"] = f1(pw["solar_wh_per_day_by_month"]["DEC"])
    return k


def table_bom() -> str:
    rows = list(csv.DictReader(open(ROOT / "deliverables" / "bom" / "bom.csv")))
    out = ["| Subsystem | Item | Part as listed | Qty | ₹ each (incl. GST) | Line ₹ | Stock seen | Vendor (link) |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        q, u = int(r["qty_per_kit"]), int(r["unit_inr_incl_gst"])
        alt = r["subsystem"].startswith("alt") or r["subsystem"].endswith("_option")
        out.append(f"| {r['subsystem']}{' (not in total)' if alt else ''} | {r['item']} | {r['part_as_listed']} | {q} | {u:,} | {q * u:,} | {r['stock_seen']} | [{r['vendor']}]({r['url']}) |")
    return "\n".join(out)


def table_power() -> str:
    pw = json.loads((ROOT / "deliverables" / "bom" / "power_budget.json").read_text())
    out = ["| Load | W (average) |", "|---|---|"]
    out += [f"| {k} | {v:.3f} |" for k, v in pw["loads_w"].items()]
    a = pw["assumptions"]
    out += ["", f"Daily energy at the battery (÷ {a['dc_dc_eff']} DC-DC efficiency, ASSUMPTION): **{pw['load_wh_per_day']} Wh/day**. "
            f"10 W panel, solar derate {a['solar_derate']} (ASSUMPTION): December {pw['solar_wh_per_day_by_month']['DEC']} Wh/day → "
            f"**{pw['worst_month_margin']}×** the load in the worst month. Battery {pw['battery_wh_nominal']:.1f} Wh nominal, {a['battery_dod']:.0%} usable "
            f"(ASSUMPTION) → **{pw['autonomy_days_no_sun']} days** with no sun. {pw['caveat']}"]
    return "\n".join(out)


TABLES = {"bom": table_bom, "power": table_power}


def render_text(text: str, k: dict[str, str]) -> str:
    def sub(m):
        kind, key, rest = m.group(1), m.group(2).strip(), m.group(3)
        if kind == "n":
            if key not in k:
                raise KeyError(f"unknown n-key {key}")
            return k[key]
        if kind == "v":
            return rest if rest is not None else ""
        return TABLES[key]()
    return PH.sub(sub, text)


def render_all() -> dict[str, str]:
    k = keys()
    return {name: render_text((SRC / name).read_text(), k) for name in TEMPLATES if (SRC / name).exists()}


if __name__ == "__main__":
    if "--keys" in sys.argv:
        for kk, vv in sorted(keys().items()):
            print(f"{kk} = {vv}")
        sys.exit(0)
    for name, text in render_all().items():
        (OUT / name).write_text(text)
        print("rendered", name)
