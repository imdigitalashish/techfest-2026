"""C6 v0.3 evaluation (fixes code-review issues 1, 3-7, 10, 12) — SYNTHETIC worlds.

Cohort: Jan Dhan holders (persons with >= 1 PMJDY account) not yet in meaningful use; the simulator calibrates the 23%
inoperative target on PMJDY accounts. Policies see only bank-observable proxies (eval/pipeline.py). The pilot is split
once (policy_v03.fit_and_gate): effects + model fitted on 70%, gate on 30%; deployment uses the same fitted objects.
A 10% randomised holdout gets standard service only (no extra outreach, no spend). Value = expected incremental
persons in meaningful use over six months (true potential outcomes, each person counted once); normalised value =
(V - V_random) / (V_reference - V_random), where the reference uses true effects (heuristic, not a certified optimum).
Linkage sensitivity: the rule-vs-challenger difference is recomputed with perfect person linkage.
Usage (from india71-t3-finance/): nice -n 10 .venv/bin/python -u eval/targeting_v03_eval.py --seeds 0 1 2 --tag dev
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
from components.targeting import policy_v03 as pv  # noqa: E402
from eval.pipeline import build  # noqa: E402
from eval.reference_allocate import reference_allocate  # noqa: E402
from eval.targeting_eval import person_value as person_value_slow  # noqa: E402,F401

ARMS = engine.ARMS


def person_value(pid: np.ndarray, arms: np.ndarray, pot: pd.DataFrame) -> float:
    """Vectorised equivalent of eval.targeting_eval.person_value: sum over true persons of the best true uplift among
    the arms they received (each person counted once; see code-review issue 12)."""
    arms = np.asarray(arms, dtype=object)
    m = arms != "none"
    if not m.any():
        return 0.0
    P = pot.set_index("person_id")
    d = pd.DataFrame({"pid": pid[m], "arm": arms[m]})
    up = np.zeros(len(d))
    for a in ARMS:
        sel = (d["arm"] == a).to_numpy()
        if sel.any():
            up[sel] = (P.loc[d.loc[sel, "pid"], f"p_{a}"].to_numpy() - P.loc[d.loc[sel, "pid"], "p_none"].to_numpy())
    return float(pd.Series(up).groupby(d["pid"].to_numpy()).max().sum())

POLICIES = ["random", "status_quo", "risk_bc", "best_arm_only", "rule", "challenger", "gated", "reference"]


def run(seed: int, n: int = 20000, bpe: float = 10.0, seeded_share: float = 0.97, pilot_fraction: float = 0.2) -> dict:
    t0 = time.time()
    b = build(seed=seed, n_persons=n, seeded_share=seeded_share, observable=True, pilot_fraction=pilot_fraction)
    w, pu = b["world"], b["persons_usage"]
    pot, pilot = w["potential"], w["pilot"].set_index("person_id")
    costs = w["config"].calibration["arm_costs_inr"]
    pu = pu[pu["has_pmjdy"]].copy()
    pu["in_pilot"] = pu["person_id"].map(pilot["in_pilot"])
    elig = pu["best_state"] != "meaningful"
    pil = pu[pu["in_pilot"] & elig].copy()
    pil["arm"], pil["y"] = pil["person_id"].map(pilot["arm"]), pil["person_id"].map(pilot["y"])
    test = pu[~pu["in_pilot"] & elig].reset_index(drop=True)
    budget = bpe * len(test)
    fem = test["female"].to_numpy()
    floor = float(fem.mean())
    fg = pv.fit_and_gate(pil, costs, bpe, seed)
    ate, model = fg["ate"], fg["model"]
    rp = pv.rule_plan(len(test), ate, costs, budget, fem, floor, np.random.default_rng(seed + 6), holdout_frac=0.10)
    hold = rp["holdout"]
    U = engine.predict_uplift(model, test)
    pol, spend_override = {"rule": rp["arms"], "challenger": pv.challenger_plan(rp, U, fem, floor)}, {}
    pol["gated"] = pol["challenger"] if fg["gate"]["pass"] else pol["rule"]
    rng = np.random.default_rng(seed + 5)
    avail = np.flatnonzero(~hold)

    arms = np.full(len(test), "none", dtype=object)
    order, arm_r = rng.permutation(avail), rng.choice(ARMS, size=len(avail))
    cum = np.cumsum([costs[a] for a in arm_r])
    arms[order[cum <= budget]] = arm_r[cum <= budget]
    pol["random"] = arms

    acc = w["accounts"].merge(b["usage"][["account_token", "state"]], on="account_token")
    acc = acc[acc["is_pmjdy"] & acc["person_id"].isin(set(test.loc[~hold, "person_id"]))]
    sev = {"no_use_24m": 0, "dormant_risk": 1, "pass_through": 2}
    acc = acc[acc["state"].isin(sev)].copy()
    acc["s"], acc["r"] = acc["state"].map(sev), rng.random(len(acc))
    k = int(budget // costs["bc_visit"])
    visited = set(acc.sort_values(["s", "r"])["person_id"].head(k))
    pol["status_quo"] = np.where(test["person_id"].isin(visited), "bc_visit", "none").astype(object)
    spend_override["status_quo"] = min(k, len(acc)) * costs["bc_visit"]

    ctrl = pil[pil["arm"] == "none"]
    rm = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, random_state=seed).fit(engine.design(ctrl), ctrl["y"])
    risk = np.where(hold, -np.inf, 1 - rm.predict_proba(engine.design(test))[:, 1])
    arms = np.full(len(test), "none", dtype=object)
    arms[np.argsort(-risk)[:k]] = "bc_visit"
    pol["risk_bc"] = arms

    eff = {a: ate[a][0] / costs[a] for a in ARMS}
    a_best = max(eff, key=eff.get)
    arms = np.full(len(test), "none", dtype=object)
    arms[rng.permutation(avail)[: int(budget // costs[a_best])]] = a_best
    pol["best_arm_only"] = arms

    P = pot.set_index("person_id")
    Ut = pd.DataFrame({a: (P.loc[test["person_id"], f"p_{a}"] - P.loc[test["person_id"], "p_none"]).to_numpy() for a in ARMS})
    Ut.loc[hold, :] = -1.0
    pol["reference"] = reference_allocate(Ut, costs, budget, fem, floor)

    pid = test["person_id"].to_numpy()
    out = {"seed": seed, "seeded_share": seeded_share, "eligible": int(len(test)), "holdout": int(hold.sum()),
           "budget_inr": budget, "pilot_train": fg["gate"]["n_train"], "info": rp["info"], "gate": fg["gate"], "policies": {}}
    for name in POLICIES:
        arms = np.asarray(pol[name], dtype=object)
        treated = arms != "none"
        spend = spend_override.get(name, float(sum(costs[a] for a in arms[treated])))
        out["policies"][name] = {"value": round(person_value(pid, arms, pot), 3), "spend": round(spend), "treated": int(treated.sum()),
                                 "holdout_treated": int((treated & hold).sum()),
                                 "women_share": round(float(fem[treated].mean()) if treated.any() else 0.0, 4),
                                 "floor_ok": pv.floor_ok(arms, fem, floor, ~hold) if name in ("rule", "challenger", "gated") else None,
                                 "within_budget": bool(spend <= budget + 1e-6),
                                 "mix": {a: int((arms == a).sum()) for a in ARMS if (arms == a).any()}}
    vr, vo = out["policies"]["random"]["value"], out["policies"]["reference"]["value"]
    for name in POLICIES:
        r = out["policies"][name]
        r["normalised"] = round((r["value"] - vr) / (vo - vr), 4) if vo > vr else None
    out["secs"] = round(time.time() - t0, 1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--pilot", type=float, default=0.2)
    ap.add_argument("--tag", default="dev")
    a = ap.parse_args()
    runs = []
    for s in a.seeds:
        r = run(s, a.n, pilot_fraction=a.pilot)
        r_link = run(s, a.n, seeded_share=1.0, pilot_fraction=a.pilot)
        r["linkage_sensitivity"] = {"perfect_linkage_challenger_minus_rule":
                                    r_link["policies"]["challenger"]["normalised"] - r_link["policies"]["rule"]["normalised"]}
        runs.append(r)
        print(f"seed {s} ({r['secs']}s) k1={r['info']['k1']} k2={r['info']['k2']} up={r['info']['upgrade']} gate={r['gate']['pass']} | " +
              " ".join(f"{p}={r['policies'][p]['normalised']}" for p in POLICIES) +
              f" | floors {[r['policies'][p]['floor_ok'] for p in ('rule', 'challenger', 'gated')]}"
              f" | link-sens {r['linkage_sensitivity']['perfect_linkage_challenger_minus_rule']:+.4f}", flush=True)
    summ = {p: {"normalised_mean": float(np.mean([r["policies"][p]["normalised"] for r in runs])),
                "normalised_sd": float(np.std([r["policies"][p]["normalised"] for r in runs], ddof=1)) if len(runs) > 1 else 0.0,
                "value_mean": float(np.mean([r["policies"][p]["value"] for r in runs]))} for p in POLICIES}
    out = ROOT / "eval" / "results" / f"c6_v03_{a.tag}.json"
    out.write_text(json.dumps({"args": vars(a), "summary": summ, "runs": runs}, indent=1, default=str))
    for p in POLICIES:
        print(f"  {p:14s} {summ[p]['normalised_mean']:+.4f} ± {summ[p]['normalised_sd']:.4f}")
    print("wrote", out)


if __name__ == "__main__":
    main()
