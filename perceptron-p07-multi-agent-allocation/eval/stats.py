"""C10 — Statistics for paired policy comparisons (common random numbers => pair by seed).

python -m eval.stats eval/results/<run>  ->  writes <run>/summary.md
For each scenario and metric: per-policy mean with 95% bootstrap CI and IQM; paired difference
vs the reference policy (default: the best rule-based baseline by served_frac in that scenario)
with a 95% paired-bootstrap CI, Wilcoxon signed-rank p, Holm correction across the family,
and win-rate across seeds.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

RULES = ["static", "greedy", "reactive"]
METRICS = [("served_frac", +1), ("lost_frac", -1), ("mean_wait", -1), ("empty_per_srv", -1),
           ("shock_lost", -1), ("shock_served", +1), ("recover_steps", -1)]


def boot_ci(x: np.ndarray, n: int = 10_000, seed: int = 0) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    m = rng.choice(x, size=(n, x.size), replace=True).mean(1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def iqm(x: np.ndarray) -> float:
    q1, q3 = np.percentile(x, [25, 75])
    sel = x[(x >= q1) & (x <= q3)]
    return float(sel.mean()) if sel.size else float(np.mean(x))


def holm(p: list[float]) -> list[float]:
    order = np.argsort(p)
    m, adj, run = len(p), [0.0] * len(p), 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (m - r) * p[i]))
        adj[i] = run
    return adj


def summarise(run_dir: str) -> str:
    df = pd.read_csv(f"{run_dir}/episodes.csv")
    out = [f"# Summary — `{run_dir}`", "",
           f"Episodes: {len(df)} · seeds per cell: {df.groupby(['scenario', 'policy']).size().min()}–"
           f"{df.groupby(['scenario', 'policy']).size().max()} · horizon: {int(df['horizon'].iloc[0])} steps · "
           f"units: {int(df['n_agents'].iloc[0])}", "",
           "Mean [95% bootstrap CI] over seeds; IQM in the last column of each block. "
           "Paired tests pair episodes by seed (common random numbers).", ""]
    tests = []
    for sc, g in df.groupby("scenario", sort=False):
        out += [f"## {sc}", ""]
        mets = [m for m, _ in METRICS if m in g and g[m].notna().all()]
        hdr = "| policy | " + " | ".join(mets) + " | IQM served |"
        out += [hdr, "|" + "---|" * (len(mets) + 2)]
        for p, gp in g.groupby("policy", sort=False):
            cells = []
            for m in mets:
                x = gp[m].to_numpy(float)
                lo, hi = boot_ci(x)
                cells.append(f"{x.mean():.4g} [{lo:.4g}, {hi:.4g}]")
            out.append(f"| {p} | " + " | ".join(cells) + f" | {iqm(gp['served_frac'].to_numpy(float)):.4f} |")
        rules = g[g.policy.isin(RULES)].groupby("policy")["served_frac"].mean()
        ref = rules.idxmax() if len(rules) else None
        out += ["", f"Reference (best rule-based by mean served_frac): **{ref}**", ""]
        if ref is None:
            continue
        piv = {m: g.pivot(index="seed", columns="policy", values=m) for m in mets}
        out += ["| policy vs ref | metric | mean diff [95% paired CI] | win-rate | Wilcoxon p | Holm p |",
                "|---|---|---|---|---|---|"]
        rows = []
        for p in [q for q in g.policy.unique() if q != ref]:
            for m, sign in METRICS:
                if m not in piv:
                    continue
                d = (piv[m][p] - piv[m][ref]).dropna().to_numpy(float)
                if d.size < 2:
                    continue
                lo, hi = boot_ci(d)
                pv = float(wilcoxon(d).pvalue) if np.any(d != 0) else 1.0
                win = float(np.mean(sign * d > 0))
                rows.append([p, m, d.mean(), lo, hi, win, pv])
        adj = holm([r[-1] for r in rows]) if rows else []
        for r, a in zip(rows, adj):
            out.append(f"| {r[0]} | {r[1]} | {r[2]:+.4g} [{r[3]:+.4g}, {r[4]:+.4g}] | {r[5]:.2f} | {r[6]:.2g} | {a:.2g} |")
            tests.append((sc, *r, a))
        out.append("")
    txt = "\n".join(out)
    with open(f"{run_dir}/summary.md", "w") as f:
        f.write(txt)
    return txt


if __name__ == "__main__":
    print(summarise(sys.argv[1])[:3000])
