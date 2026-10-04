"""Confirmatory analysis exactly as pre-registered in eval/preregistration.md (+ eval/prereg.json).

python -m eval.confirm eval/results/mvp-v2   -> writes <run>/confirm.md
Primary family: primary policy vs the pre-registered reference rule, served fraction, one test per scenario,
Holm across scenarios. Secondary families S1-S3 (Holm within family, across scenarios x pairs). Also reports
empty hops per served request, the per-shock lost requests, and recovery with censoring made explicit.
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

from eval.stats import boot_ci, holm


def paired(df, sc, a, b, metric="served_frac"):
    g = df[df.scenario == sc].pivot(index="seed", columns="policy", values=metric)
    assert g[[a, b]].notna().all().all(), f"incomplete paired grid for {sc}: {a} vs {b}"
    d = (g[a] - g[b]).to_numpy(float)
    lo, hi = boot_ci(d)
    p = float(wilcoxon(d).pvalue) if np.any(d != 0) else 1.0
    return d.mean(), lo, hi, int((d > 0).sum()), len(d), p


def main(run: str) -> str:
    pre = json.load(open("eval/prereg.json"))
    df = pd.read_csv(f"{run}/episodes.csv")
    scen = [s for s in pre["reference_rule"] if s in set(df.scenario)]
    P = pre["primary"]
    out = [f"# Confirmatory analysis — `{run}` (pre-registered: eval/preregistration.md)", "",
           f"Seeds {df.seed.min()}–{df.seed.max()} ({df.seed.nunique()} fresh test seeds) · {len(df)} episodes · "
           f"horizon {int(df.horizon.iloc[0])} · K={int(df.n_agents.iloc[0])} · P={int(df.patience.iloc[0])} · "
           f"planner backend {df.planner_backend.dropna().unique().tolist()}", "",
           "## Served fraction by policy (mean over seeds)", "",
           "| scenario | " + " | ".join(sorted(df.policy.unique())) + " |", "|---|" + "---|" * df.policy.nunique()]
    for sc in scen:
        m = df[df.scenario == sc].groupby("policy").served_frac.mean()
        out.append(f"| {sc} | " + " | ".join(f"{m[p]:.4f}" for p in sorted(df.policy.unique())) + " |")
    out += ["", f"## Primary family — `{P}` vs pre-registered reference rule (Holm over {len(scen)} scenarios)", "",
            "| scenario | reference | Δ served (pp) [95% paired CI] | seeds won | Wilcoxon p | Holm p |", "|---|---|---|---|---|---|"]
    rows = [(sc, pre["reference_rule"][sc], *paired(df, sc, P, pre["reference_rule"][sc])) for sc in scen]
    for r, a in zip(rows, holm([r[-1] for r in rows])):
        out.append(f"| {r[0]} | {r[1]} | {100*r[2]:+.2f} [{100*r[3]:+.2f}, {100*r[4]:+.2f}] | {r[5]}/{r[6]} | {r[7]:.2g} | {a:.2g} |")
    for fam, pairs in pre["secondary"].items():
        for metric, scale, unit in (("served_frac", 100, "Δ served (pp)"), ("shock_lost", 1, "Δ lost per shock")):
            out += ["", f"## Secondary family {fam} — {metric} (Holm within family and endpoint)", "",
                    f"| scenario | comparison | {unit} [95% paired CI] | seeds with increase | Wilcoxon p | Holm p |",
                    "|---|---|---|---|---|---|"]
            rows = []
            for sc in scen:
                if metric == "shock_lost" and not df[df.scenario == sc].shock_lost.notna().any():
                    continue
                for a, b in pairs:
                    if {a, b} <= set(df.policy):
                        rows.append((sc, f"{a} − {b}", *paired(df, sc, a, b, metric)))
            adj = holm([r[7] for r in rows]) if rows else []
            for r, a in zip(rows, adj):
                out.append(f"| {r[0]} | {r[1]} | {scale*r[2]:+.2f} [{scale*r[3]:+.2f}, {scale*r[4]:+.2f}] | {r[5]}/{r[6]} | "
                           f"{r[7]:.2g} | {a:.2g} |")
    out += ["", "## Movement cost and shock recovery (means over seeds)", "",
            "| scenario | policy | empty hops / served | lost per shock (120 steps) | recovered ≤120 steps | recover steps (censored at 120) |",
            "|---|---|---|---|---|---|"]
    for sc in scen:
        g = df[df.scenario == sc].groupby("policy")
        for p, gp in g:
            rec = f"{gp.recovered_frac.mean():.2f}" if "recovered_frac" in gp and gp.recovered_frac.notna().any() else "—"
            rs = f"{gp.recover_steps.mean():.1f}" if gp.recover_steps.notna().any() else "—"
            sl = f"{gp.shock_lost.mean():.1f}" if gp.shock_lost.notna().any() else "—"
            out.append(f"| {sc} | {p} | {gp.empty_per_srv.mean():.3f} | {sl} | {rec} | {rs} |")
    txt = "\n".join(out) + "\n"
    open(f"{run}/confirm.md", "w").write(txt)
    return txt


if __name__ == "__main__":
    print(main(sys.argv[1])[:4000])
