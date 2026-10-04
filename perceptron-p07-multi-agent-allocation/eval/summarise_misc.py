"""Summaries for runs without a dedicated report: NYC real-trace replay and the movement Pareto curve.

python -m eval.summarise_misc nyc eval/results/nyc-v2
python -m eval.summarise_misc pareto eval/results/pareto-v2 eval/results/mvp-v2
python -m eval.summarise_misc trust eval/results/trust-v2 eval/results/mvp-v2
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

from eval.stats import boot_ci

RULES = ["static", "greedy", "reactive"]


def _paired(sv, a, b, scale=100):
    x = (sv[a] - sv[b]).dropna().to_numpy(float)
    lo, hi = boot_ci(x)
    p = float(wilcoxon(x).pvalue) if np.any(x != 0) else 1.0
    return f"{scale*x.mean():+.2f} [{scale*lo:+.2f}, {scale*hi:+.2f}] | {int((x > 0).sum())}/{len(x)} | {p:.2g}"


def nyc(run: str) -> str:
    d = pd.read_csv(f"{run}/episodes.csv")
    cols = [c for c in ["served_frac", "lost_frac", "mean_wait", "empty_per_srv", "event_lost", "event_served", "pending_frac"]
            if c in d]
    t = d.groupby("policy")[cols].mean()
    sv = d.pivot(index="seed", columns="policy", values="served_frac")
    ev = d.pivot(index="seed", columns="policy", values="event_lost") if "event_lost" in d else None
    best = sv[[r for r in RULES if r in sv]].mean().idxmax()
    days = {"nyc-jul03-04": "July 3–4 2025 (train July 1–2)", "nyc-jul10-11": "July 10–11 2025 (train July 8–9)"}
    out = [f"# NYC TLC real-trace replay — `{run}`", "",
           f"{days.get(d.scenario.iloc[0], d.scenario.iloc[0])} yellow-taxi trips, Manhattan-internal, thinned to ~10 requests/min; "
           f"{d.seed.nunique()} thinning replicates (seeds {d.seed.min()}–{d.seed.max()}); K={int(d.n_agents.iloc[0])}, "
           f"P={int(d.patience.iloc[0])}, L=1; mean arrivals per run {int(d.arrivals.mean())}. Event window = July 4 21:30–23:30 "
           "(the largest observed surge, 20.7x in one cell 22:00–22:30; cause UNVERIFIED). `oracle` here is a retrospective "
           "15-min centred smoother of realised demand (hindsight), not a forecast-value bound.", "",
           "| policy | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for p, r in t.iterrows():
        out.append(f"| {p} | " + " | ".join(f"{r[c]:.4f}" if c != "event_lost" else f"{r[c]:.1f}" for c in cols) + " |")
    out += ["", f"Best rule by mean: **{best}**", "",
            "| comparison | Δ served (pp) [95% paired CI] | replicates won | Wilcoxon p | Δ event lost [95% CI] |",
            "|---|---|---|---|---|"]
    for a, b in [("mpc-ewma", best), ("mpc-queue", best), ("mpc-cusum-v1", "mpc-ewma"), ("mpc-queue", "mpc-ewma"),
                 ("oracle", "mpc-ewma")]:
        if ev is not None:
            e = (ev[a] - ev[b]).to_numpy(float)
            lo, hi = boot_ci(e)
            out.append(f"| {a} − {b} | {_paired(sv, a, b)} | {e.mean():+.1f} [{lo:+.1f}, {hi:+.1f}] |")
        else:
            out.append(f"| {a} − {b} | {_paired(sv, a, b)} | — |")
    return "\n".join(out) + "\n"


def pareto(run: str, base: str) -> str:
    a = pd.read_csv(f"{base}/episodes.csv")
    a = a[a.scenario == "shock"]
    b = pd.read_csv(f"{run}/episodes.csv")
    d = pd.concat([a, b], ignore_index=True)
    t = d.groupby("policy")[["served_frac", "empty_per_srv", "shock_lost"]].mean().sort_values("empty_per_srv")
    out = [f"# Service vs movement (Pareto) — `{run}` + shock rows of `{base}`", "",
           f"Scenario shock, seeds {b.seed.min()}–{b.seed.max()} (paired with mvp-v2), L=1, P=10. `@c_move=x` = planner "
           "move-cost weight (default 0.05). Sorted by empty repositioning hops per served request.", "",
           "| policy | served fraction | empty hops / served | lost per shock |", "|---|---|---|---|"]
    for p, r in t.iterrows():
        out.append(f"| {p} | {r.served_frac:.4f} | {r.empty_per_srv:.3f} | {r.shock_lost:.1f} |")
    sv = d.pivot(index="seed", columns="policy", values="served_frac")
    em = d.pivot(index="seed", columns="policy", values="empty_per_srv")
    out += ["", "| comparison | Δ served (pp) [95% CI] | seeds won | Wilcoxon p | Δ empty hops / served |", "|---|---|---|---|---|"]
    for x, y in [("mpc-ewma@c_move=0.5", "reactive"), ("mpc-ewma@c_move=0.5", "greedy"), ("mpc-queue", "greedy"),
                 ("mpc-ewma@c_move=1.0", "greedy"), ("mpc-queue@c_move=0.5", "greedy")]:
        if {x, y} <= set(sv):
            out.append(f"| {x} − {y} | {_paired(sv, x, y)} | {(em[x] - em[y]).mean():+.3f} |")
    return "\n".join(out) + "\n"


def trust(run: str, base: str) -> str:
    a = pd.read_csv(f"{base}/episodes.csv")
    b = pd.read_csv(f"{run}/episodes.csv")
    sc = sorted(b.scenario.unique())
    a = a[a.scenario.isin(sc) & a.policy.isin(["mpc-ewma", "mpc-queue"])]
    d = pd.concat([a, b], ignore_index=True)
    out = [f"# Forecast-trust sweep (exploratory) — `{run}` + `{base}`", "",
           "The planner plans on trust × forecast: trust = 0 is the queue-only LP (`mpc-queue`), trust = 1 is `mpc-ewma`. "
           f"L=1, P=10, seeds {b.seed.min()}–{b.seed.max()} (paired, CRN). Exploratory: no correction across the sweep.", "",
           "| scenario | trust 0 | 0.25 | 0.5 | 0.75 | 1 | best | best − max(trust 0, trust 1) (pp) [95% CI] |", "|---|---|---|---|---|---|---|---|"]
    order = ["mpc-queue", "mpc-ewma@trust=0.25", "mpc-ewma@trust=0.5", "mpc-ewma@trust=0.75", "mpc-ewma"]
    for s in sc:
        g = d[d.scenario == s]
        sv = g.pivot(index="seed", columns="policy", values="served_frac")
        m = sv[order].mean()
        best = m.idxmax()
        ends = "mpc-queue" if m["mpc-queue"] >= m["mpc-ewma"] else "mpc-ewma"
        x = (sv[best] - sv[ends]).to_numpy(float)
        lo, hi = boot_ci(x)
        out.append(f"| {s} | " + " | ".join(f"{m[o]:.4f}" for o in order) +
                   f" | {best} | {100*x.mean():+.2f} [{100*lo:+.2f}, {100*hi:+.2f}] |")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    kind, run = sys.argv[1], sys.argv[2]
    txt = {"nyc": lambda: nyc(run), "pareto": lambda: pareto(run, sys.argv[3]),
           "trust": lambda: trust(run, sys.argv[3])}[kind]()
    open(f"{run}/summary.md", "w").write(txt)
    print(txt[:3000])
