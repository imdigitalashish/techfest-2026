"""Stdlib-only checks of demo/data/demo_data.js against the committed results and REAL source files.

Runs with any Python 3.9+ (no venv): python3 demo/check_data.py   (exit 1 on any failure)
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "eval" / "results"
fails: list[str] = []


def check(ok: bool, msg: str) -> None:
    print(("  ok   " if ok else "  FAIL ") + msg)
    if not ok:
        fails.append(msg)


def load() -> dict:
    text = (ROOT / "demo" / "data" / "demo_data.js").read_text(encoding="utf-8")
    return json.loads(text[text.index("{"): text.rstrip().rstrip(";").rindex("}") + 1])


def main() -> int:
    raw = (ROOT / "demo" / "data" / "demo_data.js").read_text(encoding="utf-8")
    d = load()
    check(len(raw) < 5_000_000, f"data file size {len(raw):,} bytes (< 5 MB)")
    check(not re.search(r"https?://", raw), "data file contains no URLs")

    # committed results copied verbatim
    for name, val in d["committed"].items():
        check(val == json.loads((RESULTS / f"{name}.json").read_text()), f"committed.{name} == eval/results/{name}.json")

    # REAL: state gap equals the verified CSV
    rows = {r["state"]: r for r in csv.DictReader((ROOT / "research/sources/state_gap_verified.csv").open(encoding="utf-8"))}
    g = d["gap"]
    same = all(float(rows[x["state"]][f"nfhs5_{k}_pct"]) == x["nfhs5"][k] and float(rows[x["state"]][f"pt_jun2025_{k}_pct"]) == x["pt"][k]
               for x in g["rows"] for k in ("stunted", "wasted", "underweight"))
    check(same and len(g["rows"]) == 36, "gap: 36 State/UT rows identical to research/sources/state_gap_verified.csv")
    check(g["counts"]["wasted"] == {"pt_lower": 36, "n": 36}, "gap: Poshan Tracker wasting below NFHS-5 in 36/36")
    check(g["india"]["nfhs5"]["wasted"] == 19.3 and g["india"]["pt"]["wasted"] == 5.46, "gap: India 19.3% vs 5.46%")
    check(g["label"] == "REAL", "gap labelled REAL")

    # REAL: districts (V5 spot-check values)
    dd = d["districts"]
    check(dd["label"] == "REAL" and len(dd["rows"]) == dd["n_districts_source"] - len(dd["excluded"]), f"districts: {len(dd['rows'])} rows, {len(dd['excluded'])} excluded and listed")
    v5 = {"nandurbar": (30.7, 13.5, 45.8, 57.2), "amravati": (26.2, 10.7, 29.0, 38.0)}
    for pid, (w, s, st, u) in v5.items():
        p = dd["presets"][pid]
        check((p["wasted"], p["severe"], p["stunted"], p["underweight"]) == (w, s, st, u), f"districts: {p['district']} == V5 ({w}, {s}, {st}, {u})")

    # SYNTHETIC: linkage grid
    L = d["linkage"]
    lk = d["committed"]["identity_linkage"]
    cell = L["cells"][L["default"]]
    check(all(cell[m][k] == lk[m][k] for m in ("ids_only", "plaintext_probabilistic", "pprl_bloom") for k in ("f1", "precision", "recall", "clerical_review_share")),
          "linkage: 35% / +0% cell == eval/results/identity_linkage.json (F1, precision, recall, clerical share)")
    check(len(L["cells"]) == len(L["coverage_levels"]) * len(L["noise_levels"]) == 35, "linkage: 7 x 5 = 35 cells")
    lo = [c for c in L["cells"].values() if c["coverage"] <= 0.5]
    check(all(c["pprl_bloom"]["f1"] > c["ids_only"]["f1"] + 0.25 for c in lo), "linkage: PPRL F1 > shared-ID F1 + 0.25 whenever RCH-ID coverage <= 50%")
    zero = [c for c in L["cells"].values() if c["coverage"] == 0]
    check(all(c["ids_only"]["f1"] == 0 and c["pprl_bloom"]["f1"] >= 0.85 for c in zero), "linkage: at 0% coverage shared-ID F1 = 0 and PPRL F1 >= 0.85 at every typo level")
    check(all(c["pprl_bloom"]["f1"] > c["plaintext_probabilistic"]["f1"] for c in L["cells"].values() if c["coverage"] < 1),
          "linkage: PPRL F1 > pooled plaintext F1 in every cell below 100% coverage")
    check(L["label"] == "SYNTHETIC", "linkage labelled SYNTHETIC")

    # SYNTHETIC: reference worklist == committed eval_v1 at K = 5
    ew = d["committed"]["early_warning_v1"]
    wr = d["worklist_ref"]
    i5 = wr["K_values"].index(5)
    check(all(wr["recall"][m][i5] == ew["methods"][m]["episode_recall"] for m in ew["methods"]), "worklist_ref: recall at K = 5 == early_warning_v1.json for all 5 methods")
    check(wr["recall"]["lowest_observed_whz"][i5] == 0.429 and wr["recall"]["rule_no_gain_2m"][i5] == 0.3651, "worklist_ref: WHZ rule 0.429 vs programme rule 0.3651 at K = 5")
    check(all(wr["ci95"][m][i5] == ew["bootstrap_95ci"][m] for m in ("logistic_anthro", "logistic_anthro_plus_linked_health", "lowest_observed_whz")),
          "worklist_ref: bootstrap CIs at K = 5 == committed")

    # SIMULATED children, REAL district rates
    sim = d["sim"]
    expect = {"own_aww": "allow", "asha_referral": "allow", "other_aww": "deny", "cdpo_discipline": "deny", "fake_consent": "deny", "dpo_names": "deny"}
    for pid in sim["order"]:
        s = sim[pid]
        cal = s["calibration"]
        check(s["label"] == "SIMULATED children, REAL district rates", f"sim[{pid}] labelled 'SIMULATED children, REAL district rates'")
        check(cal["target_pct"]["wasted"] == dd["presets"][pid]["wasted"] and cal["target_pct"]["stunted"] == dd["presets"][pid]["stunted"], f"sim[{pid}] targets == REAL district values")
        check(abs(cal["achieved_pct"]["wasted"] - cal["target_pct"]["wasted"]) <= 0.15 and abs(cal["achieved_pct"]["stunted"] - cal["target_pct"]["stunted"]) <= 0.15,
              f"sim[{pid}] achieved wasting/stunting {cal['achieved_pct']['wasted']}/{cal['achieved_pct']['stunted']} == target")
        c = s["story"]["child"]
        check(c["link"]["linked_correctly"] and not c["link"]["ids_only_linked"], f"sim[{pid}] example child linked by PPRL (correct vs truth), not by shared IDs")
        check(1 <= c["lead_months"] <= 3 and c["onset"]["month_index"] - 3 <= c["first_flag_month"] <= c["onset"]["month_index"] - 1, f"sim[{pid}] example child listed {c['lead_months']} month(s) before onset")
        wl = s["worklist"]
        check(wl["recall"]["lowest_observed_whz"][i5] > wl["recall"]["rule_no_gain_2m"][i5] > wl["recall"]["random_within_awc"][i5], f"sim[{pid}] K = 5: WHZ rule > programme rule > random")
        check(max(m["chars"] for m in s["sms"]["messages"]) <= 80, f"sim[{pid}] every SMS <= 80 characters")
        check(all(r["decision"] == expect[r["id"]] for r in s["gate"]["requests"]), f"sim[{pid}] gate: 2 allows, 4 denies as expected")
        check(any(r["rule_id"] == "deny-employment-action" for r in s["gate"]["requests"]), f"sim[{pid}] gate: employment use denied by its own rule")
        pv = s["ledger"]["python_verdicts"]
        check(pv["truncate_3"]["no_checkpoint"] == [True, None] and pv["truncate_3"]["checkpoint"][0] is False, f"sim[{pid}] ledger: truncation caught only with the checkpoint")
    keys = set(re.findall(r'"([a-z_]+)":', json.dumps(sim)))
    check(not any(k in keys for k in ("worker_id", "measured_by", "credibility", "worker_type")), "no worker-level identifiers or scores in the simulated data (ADR 002)")

    print("check_data:", f"{len(fails)} FAILED" if fails else "all checks pass")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
