"""Paired comparison vs a baseline, with 95% bootstrap CIs.

Usage:
  .venv/bin/python eval/summarize.py --exp E3_test               # from eval/results/<exp>.csv
  .venv/bin/python eval/summarize.py --exp E3_test --from-pkl    # from finished seeds of a running exp
Writes eval/results/<exp>_summary.md.
"""
import argparse, glob, os, pickle
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rows_from_pkl(exp):
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, ".data", "runs", exp, "seed_*.pkl"))):
        r = pickle.load(open(f, "rb"))
        arr = r["arrival"]
        for label, run in r["runs"].items():
            fills = run["fills"]
            q = np.array([x[2] for x in fills], float)
            p = np.array([x[1] for x in fills], float)
            if q.sum() <= 0:
                continue
            is_c = arr - (p * q).sum() / q.sum()  # SELL
            path = run["path"]
            dts = np.array(sorted(d[0] for d in run["decisions"]))
            ft = np.array([x[0] for x in fills])
            k = np.clip(np.searchsorted(dts, ft, side="right") - 1, 0, len(dts) - 1)
            idx = np.clip(((dts[k] - dts[0]) // 1_000_000_000).astype(int), 0, len(path) - 1)
            own = float(np.nansum(q * path[idx]) / q.sum())
            rows.append(dict(seed=r["seed"], label=label, filled=int(q.sum()), is_bps=1e4 * is_c / arr,
                             own_impact_bps=1e4 * own / arr, impact_end_cents=float(path[1200]),
                             impact_post10_cents=float(path[1800])))
    return pd.DataFrame(rows)


def boot_ci(x, n=10000, seed=0):
    rs = np.random.RandomState(seed)
    m = rs.choice(x, size=(n, len(x)), replace=True).mean(1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def cvar(x, a=0.95):
    s = np.sort(x)
    return float(s[int(np.floor(a * len(s))):].mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", required=True)
    ap.add_argument("--baseline", default="TWAP")
    ap.add_argument("--from-pkl", action="store_true")
    a = ap.parse_args()
    df = rows_from_pkl(a.exp) if a.from_pkl else pd.read_csv(os.path.join(ROOT, "eval", "results", f"{a.exp}.csv"))
    labels = sorted(df.label.unique())
    seeds = sorted(set.intersection(*[set(df[df.label == l].seed) for l in labels]))
    df = df[df.seed.isin(seeds)]
    piv = df.pivot(index="seed", columns="label", values="is_bps")
    lines = [f"# {a.exp}: paired comparison vs {a.baseline}", "",
             f"n = {len(seeds)} seeds ({min(seeds)}–{max(seeds)}), source = {'per-seed pkl (run in progress)' if a.from_pkl else 'CSV'}. "
             "IS = implementation shortfall vs the arrival mid, in bps (+ = cost). 1 bp = 10¢/share at $1,000. "
             "ΔIS = label − baseline on the same seed; 95% CI = bootstrap over seeds (10k resamples).", "",
             "| policy | mean IS (bps) | 95% CI | std | CVaR95 | own impact (bps) | ΔIS vs " + a.baseline + " (bps) | 95% CI | win rate |",
             "|---|---|---|---|---|---|---|---|---|"]
    for l in labels:
        x = piv[l].values
        own = df[df.label == l].set_index("seed").loc[seeds, "own_impact_bps"].values
        lo, hi = boot_ci(x)
        if l == a.baseline:
            d = ("—", "—", "—")
        else:
            dx = x - piv[a.baseline].values
            dlo, dhi = boot_ci(dx)
            d = (f"{dx.mean():+.3f}", f"[{dlo:+.3f}, {dhi:+.3f}]", f"{(dx < 0).mean():.0%}")
        lines.append(f"| {l} | {x.mean():.3f} | [{lo:.3f}, {hi:.3f}] | {x.std(ddof=1):.3f} | {cvar(x):.3f} | "
                     f"{np.nanmean(own):.3f} | {d[0]} | {d[1]} | {d[2]} |")
    extra = [c for c in ("instant_bps", "drift_bps") if c in df.columns]
    if extra:
        lines += ["", "Decomposition means (bps): " + "; ".join(
            f"{l}: drift {df[df.label == l].drift_bps.mean():+.3f}, own {df[df.label == l].own_impact_bps.mean():+.3f}, "
            f"instant {df[df.label == l].instant_bps.mean():+.3f}" for l in labels)]
    out = os.path.join(ROOT, "eval", "results", f"{a.exp}_summary.md")
    open(out, "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
