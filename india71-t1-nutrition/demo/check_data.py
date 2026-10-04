"""Stdlib-only checks of demo/data/demo_data.js against the committed results and REAL source files.

Runs with any Python 3.9+ (no venv): python3 demo/check_data.py   (exit 1 on any failure)
"""

from __future__ import annotations

import csv
import json
import re
import sys
from datetime import date
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
    check(L["boundary_columns"] == ["source", "record_id", "clk", "block_tokens", "id_tokens", "sex_token", "synthetic"],
          "linkage: Bloom-filter runs through the encoded boundary (only CLK + keyed tokens cross)")
    cells = list(L["cells"].values())
    check(all(c[m]["true_links"] + c[m]["false_links"] == c[m]["accepted_links"] for c in cells for m in ("ids_only", "plaintext_probabilistic", "pprl_bloom", "pprl_bloom_precision_matched")),
          "linkage: correct + false links == accepted links for every method and cell")
    stress = L["cells"]["0|0.4"]
    check((stress["pprl_bloom"]["true_links"], stress["pprl_bloom"]["false_links"], stress["plaintext_probabilistic"]["true_links"], stress["plaintext_probabilistic"]["false_links"]) == (3907, 366, 2456, 34),
          "linkage: 0% IDs / +40% typos: encoded 3,907 correct / 366 false vs pooled 2,456 / 34 (review M4)")
    lo = [c for c in cells if c["coverage"] <= 0.5]
    check(all(c["pprl_bloom_precision_matched"]["reached"] and c["pprl_bloom_precision_matched"]["precision"] >= c["plaintext_probabilistic"]["precision"] and
              c["pprl_bloom_precision_matched"]["true_links"] > c["ids_only"]["true_links"] for c in lo),
          "linkage: at pooled matching's precision, encoded linkage still beats the shared-ID join whenever coverage <= 50%")
    check(all(c["ids_only"]["true_links"] == 0 for c in cells if c["coverage"] == 0), "linkage: at 0% coverage the shared-ID join finds nobody (by definition)")
    check(L["label"] == "SYNTHETIC", "linkage labelled SYNTHETIC")

    # SYNTHETIC: reference worklist == committed eval_v2 (infant gate) at K = 5
    ew = d["committed"]["early_warning_v2"]
    wr = d["worklist_ref"]
    i5 = wr["K_values"].index(5)
    check(wr.get("protocol") == "eval_v2", "worklist_ref uses the eval_v2 protocol (infant gate)")
    check(all(wr["recall"][m][i5] == ew["methods"][m]["episode_recall"] for m in ew["methods"]), "worklist_ref: recall at K = 5 == early_warning_v2.json for all 5 methods")
    check(wr["recall"]["lowest_observed_whz"][i5] == 0.4733 and wr["recall"]["rule_no_gain_2m"][i5] == 0.4128, "worklist_ref: WHZ rule 0.4733 vs programme rule 0.4128 at K = 5")
    check(all(wr["ci95"][m][i5] == v for m, v in ew["bootstrap_95ci"].items()), f"worklist_ref: all {len(ew['bootstrap_95ci'])} bootstrap CIs at K = 5 == committed")
    check(wr["n_episodes"] == ew["n_episodes_rankable"] and wr["infant_pathway_share"] == ew["infant_pathway_share"], "worklist_ref: rankable episodes and infant-pathway share == committed")

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
        check(c["link"]["linked_correctly"] and not c["link"]["ids_only_linked"], f"sim[{pid}] example child linked through the encoded boundary (correct vs truth), not by shared IDs")
        check(1 <= c["lead_months"] <= 3 and c["onset"]["month_index"] - 3 <= c["first_flag_month"] <= c["onset"]["month_index"] - 1, f"sim[{pid}] example child listed {c['lead_months']} month(s) before onset")
        before = [m for m in c["truth_wlz"] if m["month_index"] < c["onset"]["month_index"]]
        obs_before = [m for m in c["measurements"] if m["month_index"] < c["onset"]["month_index"]]
        check(c["first_ever_onset"] and all(m["wlz"] >= -2 for m in before) and all(m["status"] == "normal" for m in obs_before) and
              (date.fromisoformat(c["truth_wlz"][0]["date"]) - date.fromisoformat(c["dob_true"])).days <= 31,
              f"sim[{pid}] example child's episode is first-ever (born in window, never wasted or recorded MAM/SAM before)")
        flag_age = [m["age_days"] for m in c["measurements"] if m["month_index"] == c["first_flag_month"]]
        check(flag_age and flag_age[0] >= 183, f"sim[{pid}] example child was >= 6 months when listed (infant gate)")
        wl = s["worklist"]
        check(wl["recall"]["lowest_observed_whz"][i5] > wl["recall"]["rule_no_gain_2m"][i5] > wl["recall"]["random_within_awc"][i5], f"sim[{pid}] K = 5: WHZ rule > programme rule > random")
        ages = [k["age_m"] for e in [s["story"]["example"]] + s["examples"] for k in e["children"]]
        check(min(ages) >= 6.0, f"sim[{pid}] no child under 6 months in any ranked list (min {min(ages)} months)")
        ft = s["sms"]["featured_task"]
        check(not ft["delivered"] and ft["status"] == "blocked" and ft["blocked_reason"] == "capacity" and not ft["worker_clock"] and ft["status_day8"] == "blocked",
              f"sim[{pid}] undelivered featured task is blocked (capacity), no worker clock, not escalated on day 8")
        check(s["sms"]["capacity_exception"] and s["sms"]["capacity_exception"][0]["owner_role"] == "ls" and s["sms"]["day8"]["blocked_still_blocked"],
              f"sim[{pid}] capacity exception owned by the Lady Supervisor; all blocked tasks stay blocked on day 8")
        check(max(m["chars"] for m in s["sms"]["messages"]) <= 80, f"sim[{pid}] every exported SMS <= 80 characters")
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
