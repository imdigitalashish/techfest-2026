"""(L, P) phase diagram — where does look-ahead, and where does forecast/detector information, pay end-to-end?

L = reallocation lead time per repositioning hop (steps); P = patience (steps before a request abandons).
For every (L, P) cell and frozen test seed, all policies replay the identical request stream (CRN).
Reported paired differences in served fraction (mean, 95% paired-bootstrap CI, seeds won):
  mpc_vs_rule       mpc-ewma     - best rule-based allocator (chosen per cell by mean)
  detector_vs_ewma  mpc-cusum-v1 - mpc-ewma        (value of the change detector = spike H1)
  oracle_vs_ewma    oracle       - mpc-ewma        (upper bound on the value of ANY better forecast)
Usage: python -m eval.phase --hops 1 2 4 8 --patience 3 10 --seeds 100-109 --horizon 720 --out eval/results/phase-v1
       python -m eval.phase --summarise-only --out eval/results/phase-v1
"""
from __future__ import annotations

import argparse
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd

from eval.harness import parse_seeds, run_episode
from eval.stats import boot_ci

POLICIES = ["greedy", "reactive", "mpc-ewma", "mpc-cusum-v1", "oracle"]
RULES = ["greedy", "reactive"]
PAIRS = [("mpc_vs_rule", "mpc-ewma", None), ("detector_vs_ewma", "mpc-cusum-v1", "mpc-ewma"),
         ("oracle_vs_ewma", "oracle", "mpc-ewma")]


def summarise(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (L, P), g in df.groupby(["hop_steps", "patience"]):
        sv = g.pivot(index="seed", columns="policy", values="served_frac").dropna()
        lo_ = g.pivot(index="seed", columns="policy", values="shock_lost").reindex(sv.index)
        rule = sv[RULES].mean().idxmax()
        r = dict(L=int(L), P=int(P), n=len(sv), best_rule=rule, rule_served=sv[rule].mean(),
                 **{f"{p}_served": sv[p].mean() for p in POLICIES if p in sv})
        for name, a, b in PAIRS:
            b = b or rule
            d = (sv[a] - sv[b]).to_numpy(float)
            lo, hi = boot_ci(d)
            r.update({name: d.mean(), f"{name}_lo": lo, f"{name}_hi": hi, f"{name}_wins": int((d > 0).sum()),
                      f"{name}_shock_lost": float((lo_[a] - lo_[b]).mean())})
        rows.append(r)
    return pd.DataFrame(rows).sort_values(["P", "L"])


def write_report(out: str, df: pd.DataFrame, summ: pd.DataFrame) -> None:
    lines = [f"# (L, P) phase diagram — `{out}`", "",
             f"Scenario: {df.scenario.iloc[0]} · horizon {int(df.horizon.iloc[0])} steps · units {int(df.n_agents.iloc[0])} · "
             f"seeds {sorted(df.seed.unique().tolist())} (frozen test seeds; CRN). Served-fraction differences in "
             "percentage points, mean [95% paired bootstrap CI] (seeds won / n).", "",
             "| L | P | best rule (served) | mpc-ewma | look-ahead vs best rule | detector vs EWMA | oracle vs EWMA |",
             "|---|---|---|---|---|---|---|"]
    f = lambda r, k: f"{100*r[k]:+.2f} [{100*r[k+'_lo']:+.2f}, {100*r[k+'_hi']:+.2f}] ({r[k+'_wins']}/{r['n']})"
    for _, r in summ.iterrows():
        lines.append(f"| {r.L} | {r.P} | {r.best_rule} ({r.rule_served:.3f}) | {r['mpc-ewma_served']:.3f} | "
                     f"{f(r, 'mpc_vs_rule')} | {f(r, 'detector_vs_ewma')} | {f(r, 'oracle_vs_ewma')} |")
    lines += ["", "Requests lost in the 120 steps after shock onset, mean paired difference (negative = fewer lost):", "",
              "| L | P | look-ahead vs best rule | detector vs EWMA | oracle vs EWMA |", "|---|---|---|---|---|"]
    for _, r in summ.iterrows():
        lines.append(f"| {r.L} | {r.P} | {r.mpc_vs_rule_shock_lost:+.1f} | {r.detector_vs_ewma_shock_lost:+.1f} | "
                     f"{r.oracle_vs_ewma_shock_lost:+.1f} |")
    with open(os.path.join(out, "summary.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        Ls, Ps = sorted(summ.L.unique()), sorted(summ.P.unique())
        fig, axes = plt.subplots(1, 3, figsize=(13, 3.6))
        for ax, (k, title) in zip(axes, [("mpc_vs_rule", "look-ahead MPC − best rule"),
                                         ("detector_vs_ewma", "change detector − EWMA (spike)"),
                                         ("oracle_vs_ewma", "clairvoyant forecast − EWMA")]):
            M = np.full((len(Ps), len(Ls)), np.nan)
            for _, r in summ.iterrows():
                M[Ps.index(r.P), Ls.index(r.L)] = 100 * r[k]
            v = np.nanmax(np.abs(M)) or 1.0
            im = ax.imshow(M, cmap="RdBu", vmin=-v, vmax=v, origin="lower", aspect="auto")
            for i in range(len(Ps)):
                for j in range(len(Ls)):
                    ax.text(j, i, f"{M[i, j]:+.1f}", ha="center", va="center", fontsize=9)
            ax.set_xticks(range(len(Ls)), Ls); ax.set_yticks(range(len(Ps)), Ps)
            ax.set_xlabel("lead time L (steps per hop)"); ax.set_ylabel("patience P (steps)")
            ax.set_title(title + " (pp served)", fontsize=10)
            fig.colorbar(im, ax=ax, shrink=0.8)
        fig.tight_layout()
        fig.savefig(os.path.join(out, "phase.png"), dpi=110)
    except Exception as e:  # plotting must never kill the numbers
        print("plot failed:", e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hops", nargs="+", type=int, default=[1, 2, 4, 8])
    ap.add_argument("--patience", nargs="+", type=int, default=[3, 10])
    ap.add_argument("--policies", nargs="+", default=POLICIES)
    ap.add_argument("--scenario", default="shock")
    ap.add_argument("--seeds", default="100-109")
    ap.add_argument("--horizon", type=int, default=720)
    ap.add_argument("--n-agents", type=int, default=40)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", default="eval/results/phase-v1")
    ap.add_argument("--summarise-only", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    csv = os.path.join(a.out, "episodes.csv")
    if not a.summarise_only:
        jobs = [dict(policy=p, scenario=a.scenario, seed=s, n_agents=a.n_agents, patience=P, horizon=a.horizon,
                     hop_steps=L) for L in a.hops for P in a.patience for s in parse_seeds(a.seeds) for p in a.policies]
        jobs.sort(key=lambda j: -j["hop_steps"])  # longest LPs first for better packing
        t0, rows = time.time(), []
        with ProcessPoolExecutor(a.workers) as ex:
            for fut in as_completed([ex.submit(run_episode, j) for j in jobs]):
                rows.append(fut.result())
                pd.DataFrame(rows).to_csv(csv, index=False)
        with open(os.path.join(a.out, "config.json"), "w") as fh:
            json.dump(dict(vars(a), n_jobs=len(jobs), wall_s=time.time() - t0), fh, indent=1)
    df = pd.read_csv(csv)
    summ = summarise(df)
    summ.to_csv(os.path.join(a.out, "phase_summary.csv"), index=False)
    write_report(a.out, df, summ)
    print(open(os.path.join(a.out, "summary.md")).read()[:2500])


if __name__ == "__main__":
    main()
