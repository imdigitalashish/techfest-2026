"""Long-horizon analysis (stretch goal 2): whole-run paired CIs + per-day batch means.

python -m eval.long eval/results/long-week   -> writes summary.md + daily.png in that folder
- Across seeds: mean served fraction per policy [95% bootstrap CI]; paired differences vs the best
  rule-based allocator, mpc-cusum-v1 vs mpc-ewma, and every policy vs the oracle (regret).
- Within runs: per-day served fraction, descriptive only (days within a run share drift and are not
  independent); inference is over whole seed trajectories (gpt-6-sol review, item 8).
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd
from scipy import stats as st

from eval.stats import boot_ci

RULES = ["static", "greedy", "reactive"]


def main(run: str) -> str:
    df = pd.read_csv(f"{run}/episodes.csv")
    sv = df.pivot(index="seed", columns="policy", values="served_frac").dropna()
    sl = df.pivot(index="seed", columns="policy", values="shock_lost").reindex(sv.index)
    rule = sv[[r for r in RULES if r in sv]].mean().idxmax()
    days = int(df.horizon.iloc[0]) // 1440
    out = [f"# Long-horizon summary — `{run}`", "",
           f"Scenario {df.scenario.iloc[0]} · {days} simulated days ({int(df.horizon.iloc[0])} steps) · "
           f"{int(df.n_shocks.iloc[0]) if 'n_shocks' in df else 0} shocks per run · seeds {sorted(sv.index.tolist())} "
           f"(frozen, CRN) · units {int(df.n_agents.iloc[0])} · P={int(df.patience.iloc[0])} · L={int(df.hop_steps.iloc[0])}.", "",
           "| policy | served fraction [95% CI over seeds] | lost per shock (120-step window) | recover steps | mean wait |",
           "|---|---|---|---|---|"]
    for p in sv.columns:
        g = df[df.policy == p]
        lo, hi = boot_ci(g.served_frac.to_numpy(float))
        out.append(f"| {p} | {g.served_frac.mean():.4f} [{lo:.4f}, {hi:.4f}] | {g.shock_lost.mean():.1f} | "
                   f"{g.recover_steps.mean():.1f} | {g.mean_wait.mean():.2f} |")
    out += ["", f"Best rule-based allocator (by mean): **{rule}**", "",
            "| comparison | Δ served (pp) [95% paired CI] | seeds won | Δ lost per shock | Wilcoxon p |", "|---|---|---|---|---|"]
    comps = [(p, rule) for p in sv.columns if p.startswith("mpc") or p == "oracle"]
    comps += [("mpc-cusum-v1", "mpc-ewma")] if {"mpc-cusum-v1", "mpc-ewma"} <= set(sv) else []
    comps += [(p, "oracle") for p in sv.columns if p != "oracle" and "oracle" in sv]
    for a, b in comps:
        d = (sv[a] - sv[b]).to_numpy(float)
        lo, hi = boot_ci(d)
        p = float(st.wilcoxon(d).pvalue) if len(d) > 1 and np.any(d != 0) else float("nan")
        out.append(f"| {a} − {b} | {100*d.mean():+.2f} [{100*lo:+.2f}, {100*hi:+.2f}] | {int((d > 0).sum())}/{len(d)} | "
                   f"{(sl[a] - sl[b]).mean():+.1f} | {p:.3g} |")
    if "daily_served" in df:
        out += ["", "## Per-day served fraction (descriptive; 95% CI = bootstrap over whole seed trajectories)", "",
                "| policy | " + " | ".join(f"d{k+1}" for k in range(days)) + " | whole-run mean [95% CI over seeds] |",
                "|---|" + "---|" * (days + 1)]
        traj = {}
        for p in sv.columns:
            M = np.array([json.loads(x) for x in df[df.policy == p].sort_values("seed").daily_served])  # seeds x days
            traj[p] = M
            lo, hi = boot_ci(M.mean(1))
            out.append(f"| {p} | " + " | ".join(f"{x:.3f}" for x in M.mean(0)) + f" | {M.mean():.4f} [{lo:.4f}, {hi:.4f}] |")
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(8, 3.6))
            for p, M in traj.items():
                m, lo, hi = M.mean(0), np.percentile(M, 2.5, 0), np.percentile(M, 97.5, 0)
                x = np.arange(1, days + 1)
                ax.plot(x, m, marker="o", ms=3, label=p)
                if M.shape[0] > 1:
                    ax.fill_between(x, lo, hi, alpha=0.15)
            ax.set_xlabel("simulated day"); ax.set_ylabel("served fraction")
            ax.set_title(f"{df.scenario.iloc[0]}: one shock per day + week-long drift + spikes", fontsize=10)
            ax.legend(fontsize=8, ncol=3); fig.tight_layout(); fig.savefig(f"{run}/daily.png", dpi=110)
        except Exception as e:
            print("plot failed:", e)
    txt = "\n".join(out) + "\n"
    open(f"{run}/summary.md", "w").write(txt)
    return txt


if __name__ == "__main__":
    print(main(sys.argv[1])[:3000])
