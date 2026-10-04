"""C6 v0.2 evaluation — transparent default rule vs learned challenger vs gated deployment (SYNTHETIC worlds).

Same simulator, pipeline, budget (Rs 10 per eligible person), value function and oracle as eval/targeting_eval.py.
Value = expected incremental persons in meaningful use over 6 months (true potential outcomes, person counted once).
Normalised value = (policy - random) / (oracle - random).
Usage (from india71-t3-finance/): nice -n 10 .venv/bin/python eval/targeting_v02_eval.py --seeds 0 1 2 --tag dev
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "1")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: E402

import sakriya_paths  # noqa: F401,E402
from components.targeting import engine  # noqa: E402
from components.targeting import policy_v02 as pv  # noqa: E402
from eval.frozen_allocate import allocate as frozen_allocate  # noqa: E402
from eval.pipeline import build  # noqa: E402
from eval.targeting_eval import person_value  # noqa: E402

ARMS = engine.ARMS
POLICIES = ["random", "status_quo", "risk_bc", "best_arm_only", "rule", "uplift_v01", "challenger", "challenger_who", "gated", "oracle"]


def run(seed: int, n: int = 20000, bpe: float = 10.0) -> dict:
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
    budget = bpe * len(test)
    rng = np.random.default_rng(seed + 5)
    fem = test["female"].to_numpy()
    share_w = float(fem.mean())
    pol, spend_override = {}, {}

    order, arm_r = rng.permutation(len(test)), rng.choice(ARMS, size=len(test))
    cum = np.cumsum([costs[a] for a in arm_r[order]])
    arms = np.full(len(test), "none", dtype=object)
    arms[order[cum <= budget]] = arm_r[order[cum <= budget]]
    pol["random"] = arms

    acc = w["accounts"].merge(b["usage"][["account_token", "state"]], on="account_token")
    acc = acc[acc["person_id"].isin(set(test["person_id"]))]
    sev = {"inoperative": 0, "dormant_risk": 1, "pass_through": 2}
    acc = acc[acc["state"].isin(sev)].copy()
    acc["s"], acc["r"] = acc["state"].map(sev), rng.random(len(acc))
    k = int(budget // costs["bc_visit"])
    visited = set(acc.sort_values(["s", "r"])["person_id"].head(k))
    pol["status_quo"] = np.where(test["person_id"].isin(visited), "bc_visit", "none").astype(object)
    spend_override["status_quo"] = min(k, len(acc)) * costs["bc_visit"]

    ctrl = train[train["arm"] == "none"]
    rm = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, random_state=seed).fit(engine.design(ctrl), ctrl["y"])
    risk = 1 - rm.predict_proba(engine.design(test))[:, 1]
    arms = np.full(len(test), "none", dtype=object)
    arms[np.argsort(-risk)[:k]] = "bc_visit"
    pol["risk_bc"] = arms

    ate = pv.arm_ate(train["arm"], train["y"])
    eff = {a: ate[a][0] / costs[a] for a in ARMS}
    a_best = max(eff, key=eff.get)
    arms = np.full(len(test), "none", dtype=object)
    arms[rng.permutation(len(test))[: int(budget // costs[a_best])]] = a_best
    pol["best_arm_only"] = arms

    pol["rule"] = pv.rule_policy(len(test), ate, costs, budget, np.random.default_rng(seed + 6))

    U = engine.predict_uplift(engine.fit(train, train["arm"], train["y"], seed=seed), test)
    pol["uplift_v01"] = engine.allocate(U, costs, budget, fem, min_share_women=share_w).to_numpy()
    pol["challenger"] = pv.two_stage(U, ate, costs, budget, fem, share_w)
    pol["challenger_who"] = pv.two_stage(U, ate, costs, budget, fem, share_w, arm_choice="rule")

    g = pv.gate(train[train["best_state"] != "meaningful"], costs, bpe, seed)
    pol["gated"] = pol["challenger_who"] if g["pass"] else pol["rule"]

    P = pot.set_index("person_id")
    Ut = pd.DataFrame({a: (P.loc[test["person_id"], f"p_{a}"] - P.loc[test["person_id"], "p_none"]).to_numpy() for a in ARMS},
                      index=test.index)
    pol["oracle"] = frozen_allocate(Ut, costs, budget, fem, min_share_women=share_w).to_numpy()

    pid = test["person_id"].to_numpy()
    out = {"seed": seed, "n_persons": n, "eligible": int(len(test)), "budget_inr": budget, "pilot_n": int(len(train)),
           "stage1_arm": pv.stage1_arm(ate, costs), "upgrade_arm": pv.upgrade_arm(ate, costs, pv.stage1_arm(ate, costs)) if pv.stage1_arm(ate, costs) else None,
           "gate": g, "policies": {}}
    for name in POLICIES:
        arms = np.asarray(pol[name], dtype=object)
        treated = arms != "none"
        spend = spend_override.get(name, float(sum(costs[a] for a in arms[treated])))
        out["policies"][name] = {"value": round(person_value(pid, arms, pot), 3), "spend": round(spend),
                                 "treated": int(treated.sum()),
                                 "women_share": round(float(fem[treated].mean()) if treated.any() else 0.0, 4),
                                 "mix": {a: int((arms == a).sum()) for a in ARMS if (arms == a).any()}}
    vr, vo = out["policies"]["random"]["value"], out["policies"]["oracle"]["value"]
    for name in POLICIES:
        r = out["policies"][name]
        r["normalised"] = round((r["value"] - vr) / (vo - vr), 4) if vo > vr else None
        r["per_lakh"] = round(r["value"] / max(r["spend"], 1) * 1e5, 2)
    out["secs"] = round(time.time() - t0, 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--tag", default="dev")
    a = ap.parse_args()
    runs = []
    for s in a.seeds:
        r = run(s, a.n)
        runs.append(r)
        print(f"seed {s} ({r['secs']}s) gate pass={r['gate']['pass']} lb={r['gate']['lower_bound_90']:+.4f} | " +
              " ".join(f"{p}={r['policies'][p]['normalised']}" for p in POLICIES), flush=True)
    summ = {p: {"normalised_mean": float(np.mean([r["policies"][p]["normalised"] for r in runs])),
                "normalised_sd": float(np.std([r["policies"][p]["normalised"] for r in runs], ddof=1)) if len(runs) > 1 else 0.0,
                "value_mean": float(np.mean([r["policies"][p]["value"] for r in runs])),
                "women_share_mean": float(np.mean([r["policies"][p]["women_share"] for r in runs]))} for p in POLICIES}
    out = ROOT / "eval" / "results" / f"c6_v02_{a.tag}.json"
    out.write_text(json.dumps({"args": vars(a), "summary": summ, "runs": runs}, indent=1, default=str))
    for p in POLICIES:
        print(f"  {p:14s} {summ[p]['normalised_mean']:+.4f} ± {summ[p]['normalised_sd']:.4f}")
    print("wrote", out)


if __name__ == "__main__":
    main()
