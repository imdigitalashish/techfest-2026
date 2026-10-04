"""Spike B evaluation: does the accountability metric rank implementers by their TRUE causal contribution, even
when some implementers game the numbers? (SYNTHETIC world; every parameter below is an ASSUMPTION.)

World: D districts × U implementer units (e.g. branch + its BCs) per district, ~P persons per unit. Each unit has
  - a baseline meaningful-use propensity p0 driven by district and customer mix (not the unit's merit),
  - a true contribution tau (incremental meaningful use among the persons it reaches),
  - enrolment counts (new accounts opened) unrelated to tau,
  - with probability g it games: token credits on inactive accounts (inflate account-level 'operative' share)
    and duplicate account openings (inflate enrolments).
Sakriya keeps a randomised 10% holdout per unit; outcomes are person-level meaningful use (C2; token credits
do not count).
Metrics ranked against tau (Spearman rho, higher is better):
  M1 enrolments · M2 account-level operative share · M3 person meaningful-use rate · M4 Sakriya incremental
  (treated − holdout) · M5 M4 + empirical-Bayes shrinkage.
DP: M3 released per unit and per district with the Laplace mechanism at epsilon = 1 → MAE in percentage points.
Usage (from india71-t3-finance/): python eval/scorecard_eval.py --seeds 0 1 2 3 4
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from components.dp_publisher.dp import Ledger, release_rates  # noqa: E402
from components.scorecard.scorecard import eb_shrink, gaming_flags, incremental  # noqa: E402

CFG = {"districts": 20, "units_per_district": 10, "persons_per_unit": 3000, "holdout": 0.10, "quarters": 4,
       "tau_mean": 0.04, "tau_sd": 0.03, "gaming_share": 0.2, "token_share": 0.35, "dup_accounts": 400}


def world(seed: int, quarters: int):
    c = CFG
    rng = np.random.default_rng(seed)
    D, U, P = c["districts"], c["units_per_district"], c["persons_per_unit"]
    n_units = D * U
    district = np.repeat(np.arange(D), U)
    d_eff = rng.normal(0, 0.6, D)[district]
    mix = rng.normal(0, 0.5, n_units)
    p0 = 1 / (1 + np.exp(-(-0.6 + d_eff + mix)))
    tau = np.clip(rng.normal(c["tau_mean"], c["tau_sd"], n_units), -0.02, None)
    games = rng.random(n_units) < c["gaming_share"]
    enrol = rng.poisson(300 + 200 * (mix > 0), n_units) + games * c["dup_accounts"]
    rows = []
    n = P * quarters
    for u in range(n_units):
        hold = rng.random(n) < c["holdout"]
        p = np.clip(p0[u] + np.where(hold, 0.0, tau[u]), 0, 1)
        y = rng.random(n) < p
        acct_op = y | (games[u] & (rng.random(n) < c["token_share"]))
        rows.append(pd.DataFrame({"unit_id": u, "district": district[u], "holdout": hold, "meaningful": y.astype(float),
                                  "acct_operative": acct_op.astype(float)}))
    df = pd.concat(rows, ignore_index=True)
    truth = pd.DataFrame({"tau": tau, "p0": p0, "games": games, "enrol": enrol, "district": district})
    return df, truth


def run(seed: int, quarters: int) -> dict:
    df, truth = world(seed, quarters)
    inc = incremental(df)
    m = pd.DataFrame(index=truth.index)
    m["M1_enrolments"] = truth["enrol"]
    m["M2_account_operative_share"] = df.groupby("unit_id")["acct_operative"].mean()
    m["M3_person_meaningful_rate"] = df.groupby("unit_id")["meaningful"].mean()
    m["M4_sakriya_incremental"] = inc["incremental"]
    m["M5_sakriya_incremental_EB"] = eb_shrink(inc, truth["district"])
    rho = {k: float(spearmanr(m[k], truth["tau"]).statistic) for k in m.columns}
    rho_gamers_top = {k: float(truth.loc[m[k].rank(ascending=False) <= 20, "games"].mean()) for k in m.columns}
    flags = gaming_flags(df)
    tp = int(((flags != "") & truth["games"]).sum()); fp = int(((flags != "") & ~truth["games"]).sum())
    coverage = float(((inc["ci_low"] <= truth["tau"]) & (truth["tau"] <= inc["ci_high"])).mean())
    # DP release of person meaningful-use rate: per unit and per district, epsilon = 1 each (separate ledgers)
    out_dp = {}
    ledger = Ledger(1.0)  # ONE budget for both overlapping tables (code-review issue 9): epsilon 0.5 each
    for level, key in (("unit", "unit_id"), ("district", "district")):
        cnt = df.groupby(key)["meaningful"].agg(["sum", "count"]).rename(columns={"sum": "numerator", "count": "denominator"})
        rel = release_rates(cnt, eps=0.5, ledger=ledger, table=level, seed=seed)  # seeded: simulation only
        out_dp[level] = {"mae_pp": float((rel["rate"] - cnt["numerator"] / cnt["denominator"]).abs().mean() * 100),
                         "persons_per_cell": float(cnt["denominator"].mean())}
    return {"seed": seed, "quarters": quarters, "spearman_rho": rho, "share_of_gamers_in_top20": rho_gamers_top,
            "gaming_flags": {"true_pos": tp, "false_pos": fp, "gamers": int(truth["games"].sum())},
            "ci95_coverage_M4": coverage, "dp_eps_total1_half_each": out_dp}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    ap.add_argument("--quarters", type=int, nargs="+", default=[1, 4])
    a = ap.parse_args()
    allres = {}
    for q in a.quarters:
        runs = [run(s, q) for s in a.seeds]
        allres[q] = runs
        keys = runs[0]["spearman_rho"].keys()
        print(f"\nSYNTHETIC accountability world, {q} quarter(s) of data, seeds {a.seeds}: Spearman rho with true contribution (mean ± sd)")
        for k in keys:
            v = [r["spearman_rho"][k] for r in runs]; gtop = np.mean([r["share_of_gamers_in_top20"][k] for r in runs])
            print(f"  {k:28s} rho {np.mean(v):+.3f} ± {np.std(v, ddof=1):.3f} | gamers among top-20 units {gtop:.0%}")
        print(f"  gaming flag: TP {np.mean([r['gaming_flags']['true_pos'] for r in runs]):.1f} / {runs[0]['gaming_flags']['gamers']} gamers (seed 0), FP {np.mean([r['gaming_flags']['false_pos'] for r in runs]):.1f}"
              f" | M4 95% CI coverage {np.mean([r['ci95_coverage_M4'] for r in runs]):.3f}")
        for lvl in ("unit", "district"):
            print(f"  DP eps=0.5 of a total 1.0 {lvl:8s}: MAE {np.mean([r['dp_eps_total1_half_each'][lvl]['mae_pp'] for r in runs]):.3f} pp at ~{runs[0]['dp_eps_total1_half_each'][lvl]['persons_per_cell']:,.0f} persons per cell")
    out = ROOT / "eval" / "results" / "scorecard_spikeB.json"
    out.write_text(json.dumps({"config": CFG, "runs": {str(k): v for k, v in allres.items()}}, indent=1))
    print("wrote", out)


if __name__ == "__main__":
    main()
