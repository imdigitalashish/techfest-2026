"""(L, P) phase diagram — where does look-ahead, and where does forecast/detector information, pay end-to-end?

L = reallocation lead time per repositioning hop (steps); P = patience (steps before a request abandons).
For every (L, P) cell and frozen test seed, all policies replay the identical request stream (CRN).
Reported paired differences in served fraction (mean, 95% paired-bootstrap CI, seeds won):
  mpc_vs_rule       mpc-ewma     - best rule-based allocator (chosen per cell by mean)
  detector_vs_ewma  mpc-cusum-v1 - mpc-ewma        (value of the change detector = spike H1)
  oracle_vs_ewma    oracle       - mpc-ewma        (true-rate forecast in the same planner: a reference, NOT an upper
                                                     bound - it can be negative when the planner over-trusts forecasts)
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
from scipy.stats import wilcoxon

from eval.stats import boot_ci, holm

POLICIES = ["greedy", "reactive", "mpc-ewma", "mpc-cusum-v1", "oracle"]
RULES = ["greedy", "reactive"]
PAIRS = [("mpc_vs_rule", "mpc-ewma", None), ("detector_vs_ewma", "mpc-cusum-v1", "mpc-ewma"),
         ("oracle_vs_ewma", "oracle", "mpc-ewma"), ("queue_vs_ewma", "mpc-queue", "mpc-ewma"),
         ("myopic_vs_ewma", "mpc-myopic", "mpc-ewma"),
         ("detector_vs_matched_alpha", "mpc-cusum-v1", "mpc-ewma@alpha=0.01"),
         ("detector_vs_ewma_fixedH", "mpc-cusum-v1@horizon=14", "mpc-ewma@horizon=14")]
LABEL = {"mpc_vs_rule": "look-ahead vs best rule", "detector_vs_ewma": "detector vs EWMA",
         "oracle_vs_ewma": "true-rate forecast vs EWMA", "queue_vs_ewma": "queue-only (no forecast) vs EWMA",
         "myopic_vs_ewma": "myopic (H=L+1) vs EWMA", "detector_vs_matched_alpha": "detector vs EWMA(α=0.01)",
         "detector_vs_ewma_fixedH": "detector vs EWMA, both H=14"}


def summarise(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (L, P), g in df.groupby(["hop_steps", "patience"]):
        sv = g.pivot(index="seed", columns="policy", values="served_frac").dropna()
        lo_ = g.pivot(index="seed", columns="policy", values="shock_lost").reindex(sv.index)
        rule = sv[[r for r in RULES if r in sv]].mean().idxmax()
        r = dict(L=int(L), P=int(P), n=len(sv), best_rule=rule, rule_served=sv[rule].mean(),
                 **{f"{p}_served": sv[p].mean() for p in sv.columns})
        for name, a, b in PAIRS:
            if a not in sv or (b is not None and b not in sv):
                continue
            b = b or rule
            d = (sv[a] - sv[b]).to_numpy(float)
            lo, hi = boot_ci(d)
            r.update({name: d.mean(), f"{name}_lo": lo, f"{name}_hi": hi, f"{name}_wins": int((d > 0).sum()),
                      f"{name}_shock_lost": float((lo_[a] - lo_[b]).mean())})
        # share of the true-rate forecast's gain over EWMA that an arm captures: ratio of MEAN paired gains, joint
        # bootstrap over seeds; suppressed (NaN) unless the denominator's 95% CI is strictly positive.
        for arm, key in (("mpc-cusum-v1", "capture"), ("mpc-ewma@alpha=0.01", "capture_matched_alpha")):
            if {arm, "oracle", "mpc-ewma"} <= set(sv):
                num = (sv[arm] - sv["mpc-ewma"]).to_numpy(float)
                den = (sv["oracle"] - sv["mpc-ewma"]).to_numpy(float)
                idx = np.random.default_rng(0).integers(0, len(num), size=(10_000, len(num)))
                nm, dm = num[idx].mean(1), den[idx].mean(1)
                ok = np.percentile(dm, 2.5) > 0
                r[key] = num.mean() / den.mean() if ok else np.nan
                r[key + "_lo"], r[key + "_hi"] = (np.percentile(nm / dm, [2.5, 97.5]) if ok else (np.nan, np.nan))
        rows.append(r)
    return pd.DataFrame(rows).sort_values(["P", "L"])


def write_report(out: str, df: pd.DataFrame, summ: pd.DataFrame) -> None:
    lines = [f"# (L, P) phase diagram — `{out}`", "",
             f"Scenario: {df.scenario.iloc[0]} · horizon {int(df.horizon.iloc[0])} steps · units {int(df.n_agents.iloc[0])} · "
             f"seeds {sorted(df.seed.unique().tolist())} (frozen test seeds; CRN). Served-fraction differences in "
             "percentage points, mean [95% paired bootstrap CI] (seeds won / n).", "",
             ]
    keys = [k for k, _, _ in PAIRS if f"{k}_wins" in summ]
    lines += ["| L | P | best rule (served) | mpc-ewma | " + " | ".join(LABEL[k] for k in keys) + " |",
              "|---|---|---|---|" + "---|" * len(keys)]
    f = lambda r, k: f"{100*r[k]:+.2f} [{100*r[k+'_lo']:+.2f}, {100*r[k+'_hi']:+.2f}] ({int(r[k+'_wins'])}/{int(r['n'])})"
    for _, r in summ.iterrows():
        lines.append(f"| {r.L} | {r.P} | {r.best_rule} ({r.rule_served:.3f}) | {r['mpc-ewma_served']:.3f} | "
                     + " | ".join(f(r, k) for k in keys) + " |")
    lines += ["", "Requests lost in the 120 steps after shock onset, mean paired difference (negative = fewer lost):", "",
              "| L | P | " + " | ".join(LABEL[k] for k in keys) + " |", "|---|---|" + "---|" * len(keys)]
    for _, r in summ.iterrows():
        lines.append(f"| {r.L} | {r.P} | " + " | ".join(f"{r[k + '_shock_lost']:+.1f}" for k in keys) + " |")
    if {"mpc-cusum-v1", "mpc-ewma"} <= set(df.policy):  # pre-registered H1 family (eval/preregistration.md, Addendum A)
        rows = []
        for (L, P), g in df.groupby(["hop_steps", "patience"]):
            pv = g.pivot(index="seed", columns="policy", values="shock_lost")
            d = (pv["mpc-cusum-v1"] - pv["mpc-ewma"]).dropna().to_numpy(float)
            lo, hi = boot_ci(d)
            pval = float(wilcoxon(d).pvalue) if np.any(d != 0) else 1.0
            rows.append((int(L), int(P), d.mean(), lo, hi, int((d < 0).sum()), len(d), pval))
        adj = holm([r[-1] for r in rows])
        lines += ["", "**Pre-registered H1 family** — detector (`mpc-cusum-v1`) − EWMA, requests lost in the 120 steps after "
                  "shock onset (negative = detector loses fewer); paired bootstrap 95% CI; Wilcoxon; Holm over the 8 cells:", "",
                  "| L | P | Δ lost per shock [95% CI] | seeds where detector lost fewer | Wilcoxon p | Holm p |",
                  "|---|---|---|---|---|---|"]
        for r, a in sorted(zip(rows, adj), key=lambda x: (x[0][1], x[0][0])):
            lines.append(f"| {r[0]} | {r[1]} | {r[2]:+.1f} [{r[3]:+.1f}, {r[4]:+.1f}] | {r[5]}/{r[6]} | {r[7]:.2g} | {a:.2g} |")
    if "capture" in summ:
        lines += ["", "Share of the true-rate forecast's served-fraction gain over EWMA captured by an arm (ratio of mean paired "
                  "gains, joint seed bootstrap 95% CI; '—' where that gain is not reliably positive, i.e. forecasting does not pay):",
                  "", "| L | P | true-rate − EWMA (pp) | detector arm captures | matched-α EWMA captures |", "|---|---|---|---|---|"]
        cap = lambda r, k: (f"{100*r[k]:.0f}% [{100*r[k+'_lo']:.0f}%, {100*r[k+'_hi']:.0f}%]"
                            if k in r and pd.notna(r[k]) else "—")
        for _, r in summ.iterrows():
            lines.append(f"| {r.L} | {r.P} | {100*r.oracle_vs_ewma:+.2f} | {cap(r, 'capture')} | {cap(r, 'capture_matched_alpha')} |")
    with open(os.path.join(out, "summary.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        Ls, Ps = sorted(summ.L.unique()), sorted(summ.P.unique())
        keys = [k for k, _, _ in PAIRS if k in summ]
        fig, axes = plt.subplots(1, len(keys), figsize=(4.4 * len(keys), 3.6))
        for ax, k in zip(np.atleast_1d(axes), keys):
            title = LABEL[k]
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
    ap.add_argument("--legacy", action="store_true", help="reproduce phase-v1 (scipy backend, never-abandoning LP backlog)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    csv = os.path.join(a.out, "episodes.csv")
    if not a.summarise_only:
        jobs = [dict(policy=p, scenario=a.scenario, seed=s, n_agents=a.n_agents, patience=P, horizon=a.horizon,
                     hop_steps=L, legacy=a.legacy) for L in a.hops for P in a.patience for s in parse_seeds(a.seeds) for p in a.policies]
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
