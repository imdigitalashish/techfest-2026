"""End-to-end targeting evaluation (C14 -> C2 -> C3 -> C6) on SYNTHETIC data with known potential outcomes.

Policies compared at the same budget (Rs per eligible person) on persons NOT in the pilot:
  random      : random eligible persons, random non-'none' arm
  status_quo  : account-level reactivation drive — inoperative, then dormant, then pass-through
                accounts get a BC visit (cost per ACCOUNT; duplicates of one person cost twice)
  risk_bc     : classifier of non-use risk (trained on pilot controls), highest risk first, BC visit
  ate_best    : the arm with the best pilot average effect per rupee, to random eligible persons
  uplift      : C6 engine (per-arm uplift model + budgeted allocation), women >= their eligible share
  oracle      : true uplift + same allocation (upper bound)
Value = expected incremental persons in MEANINGFUL use over 6 months (person-level, counted once).
Usage: python eval/targeting_eval.py --seeds 0 1 2 --n 40000 --budget-per-eligible 10
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import sakriya_paths  # noqa: F401,E402
from components.targeting import engine
from eval.pipeline import build
from eval.frozen_allocate import allocate as frozen_allocate

ROOT = pathlib.Path(__file__).resolve().parents[1]
ARMS = engine.ARMS


def person_value(pid: np.ndarray, arms: np.ndarray, pot: pd.DataFrame) -> float:
    """Sum over true persons of the best true uplift among arms they received (counted once)."""
    d = pd.DataFrame({"pid": pid, "arm": arms})
    d = d[d["arm"] != "none"]
    if d.empty:
        return 0.0
    P = pot.set_index("person_id")
    up = np.array([P.at[p, f"p_{a}"] - P.at[p, "p_none"] for p, a in zip(d["pid"], d["arm"])])
    return float(pd.Series(up).groupby(d["pid"].to_numpy()).max().sum())


def run(seed: int, n: int, budget_per_eligible: float, verbose=True) -> dict:
    t0 = time.time()
    b = build(seed=seed, n_persons=n)
    w, pu = b["world"], b["persons_usage"]
    pot, pilot = w["potential"], w["pilot"].set_index("person_id")
    costs = w["config"].calibration["arm_costs_inr"]
    pu["in_pilot"] = pu["person_id"].map(pilot["in_pilot"])
    train = pu[pu["in_pilot"]].copy()
    train["arm"] = train["person_id"].map(pilot["arm"])
    train["y"] = train["person_id"].map(pilot["y"])
    test = pu[(~pu["in_pilot"]) & (pu["best_state"] != "meaningful")].copy()
    budget = budget_per_eligible * len(test)
    rng = np.random.default_rng(seed + 5)
    res = {}

    # random
    order = rng.permutation(len(test))
    arm_r = rng.choice(ARMS, size=len(test))
    spend = np.cumsum([costs[a] for a in arm_r[order]])
    arms = np.full(len(test), "none", dtype=object)
    arms[order[spend <= budget]] = arm_r[order[spend <= budget]]
    res["random"] = (arms, None)

    # status quo: account-level BC drive by severity
    acc = w["accounts"].merge(b["usage"][["account_token", "state"]], on="account_token")
    acc = acc[acc["person_id"].isin(set(test["person_id"]))]
    sev = {"inoperative": 0, "dormant_risk": 1, "pass_through": 2}
    acc = acc[acc["state"].isin(sev)].assign(s=lambda d: d["state"].map(sev), r=rng.random(len(acc[acc["state"].isin(sev)])))
    acc = acc.sort_values(["s", "r"])
    k = int(budget // costs["bc_visit"])
    visited = set(acc["person_id"].head(k))
    res["status_quo"] = (np.where(test["person_id"].isin(visited), "bc_visit", "none"), {"accounts_visited": int(min(k, len(acc)))})

    # risk_bc
    ctrl = train[train["arm"] == "none"]
    rm = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, random_state=seed).fit(engine.design(ctrl), ctrl["y"])
    risk = 1 - rm.predict_proba(engine.design(test))[:, 1]
    k = int(budget // costs["bc_visit"])
    top = np.argsort(-risk)[:k]
    arms = np.full(len(test), "none", dtype=object); arms[top] = "bc_visit"
    res["risk_bc"] = (arms, None)

    # ate_best
    ybar = train.groupby("arm")["y"].mean()
    eff = {a: (ybar.get(a, 0) - ybar.get("none", 0)) / costs[a] for a in ARMS}
    a_best = max(eff, key=eff.get)
    k = int(budget // costs[a_best])
    arms = np.full(len(test), "none", dtype=object); arms[rng.permutation(len(test))[:k]] = a_best
    res["ate_best"] = (arms, {"arm": a_best})

    # uplift spike
    model = engine.fit(train, train["arm"], train["y"], seed=seed)
    U = engine.predict_uplift(model, test)
    share_w = float(test["female"].mean())
    res["uplift"] = (engine.allocate(U, costs, budget, test["female"].to_numpy(), min_share_women=share_w).to_numpy(), None)

    # oracle
    P = pot.set_index("person_id")
    Ut = pd.DataFrame({a: (P.loc[test["person_id"], f"p_{a}"] - P.loc[test["person_id"], "p_none"]).to_numpy() for a in ARMS}, index=test.index)
    res["oracle"] = (frozen_allocate(Ut, costs, budget, test["female"].to_numpy(), min_share_women=share_w).to_numpy(), None)

    out = {"seed": seed, "n_persons": n, "eligible": int(len(test)), "budget_inr": budget, "pilot_n": int(len(train))}
    pid = test["person_id"].to_numpy()
    fem = test["female"].to_numpy()
    for name, (arms, extra) in res.items():
        arms = np.asarray(arms, dtype=object)
        if name == "status_quo":
            spend = extra["accounts_visited"] * costs["bc_visit"]
        else:
            spend = float(sum(costs[a] for a in arms if a != "none"))
        v = person_value(pid, arms, pot)
        treated = arms != "none"
        out[name] = {"value": round(v, 2), "per_lakh": round(v / max(spend, 1) * 1e5, 2), "spend": round(spend),
                     "treated": int(treated.sum()), "women_share": round(float(fem[treated].mean()) if treated.any() else 0, 3),
                     "mix": {a: int((arms == a).sum()) for a in ARMS if (arms == a).any()}, **(extra or {})}
    vr, vo = out["random"]["value"], out["oracle"]["value"]
    for name in res:
        out[name]["normalised"] = round((out[name]["value"] - vr) / (vo - vr), 4) if vo > vr else None
    out["secs"] = round(time.time() - t0, 1)
    if verbose:
        print(f"seed {seed}: eligible {out['eligible']} budget Rs {budget:,.0f} ({out['secs']}s)")
        for name in res:
            r = out[name]
            print(f"  {name:11s} value {r['value']:8.1f}  per-lakh {r['per_lakh']:7.1f}  norm {r['normalised']}  treated {r['treated']:6d}  women {r['women_share']}  mix {r['mix']}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--n", type=int, default=40000)
    ap.add_argument("--budget-per-eligible", type=float, default=10.0)
    ap.add_argument("--out", default=str(ROOT / "eval" / "results" / "targeting_baseline.json"))
    a = ap.parse_args()
    runs = [run(s, a.n, a.budget_per_eligible) for s in a.seeds]
    names = ["random", "status_quo", "risk_bc", "ate_best", "uplift", "oracle"]
    summary = {nm: {k: round(float(np.mean([r[nm][k] for r in runs])), 3) for k in ["value", "per_lakh", "normalised", "women_share"]} for nm in names}
    print("\nMEAN over seeds", a.seeds)
    for nm in names:
        s = summary[nm]
        print(f"  {nm:11s} incremental meaningful users per Rs 1 lakh {s['per_lakh']:7.1f} | normalised {s['normalised']:.3f} | women share {s['women_share']}")
    pathlib.Path(a.out).write_text(json.dumps({"args": vars(a), "summary": summary, "runs": runs}, indent=1, default=str))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
