"""C1 isolated metric (pre-registered E7): realism scorecard for impact in the simulator.

TWAP size sweep over the same window and the same seeds:
- peak own impact I(Q) = mean twin gap at the end of execution (T1 = 1,200 s after 09:35);
- participation Q/V, where V = mean null-twin volume traded in the window;
- delta = OLS slope of log I(Q) on log(Q/V), with a 95% CI from a paired bootstrap over seeds
  (seed indices resampled jointly across sizes);
- decay ratio = mean gap at T1 + 600 s / mean gap at T1.
Square-root law: delta ~ 0.5 (TSE survey, arXiv:2411.13965; ABM benchmark 0.489, arXiv:2607.04280).

Usage: .venv/bin/python eval/realism.py --qs 1000 2000 4000 8000 16000
Writes eval/results/realism_scorecard.md and .json.
"""
import argparse, glob, json, os, pickle
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T1, T_POST = 1200, 1800


def load(exp):
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, ".data", "runs", exp, "seed_*.pkl"))):
        r = pickle.load(open(f, "rb"))
        p = r["runs"]["TWAP"]["path"]
        out[int(r["seed"])] = (float(p[T1]), float(p[T_POST]), float(np.sum(r["slot_vol"])))
    return out


def slope(x, y):
    return float(np.polyfit(x, y, 1)[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qs", nargs="+", type=int, required=True)
    ap.add_argument("--prefix", default="E7_size_q")
    ap.add_argument("--boot", type=int, default=5000)
    a = ap.parse_args()
    data = {q: load(f"{a.prefix}{q}") for q in a.qs}
    seeds = sorted(set.intersection(*[set(d) for d in data.values()]))
    peak = np.array([[data[q][s][0] for s in seeds] for q in a.qs])   # sizes x seeds
    post = np.array([[data[q][s][1] for s in seeds] for q in a.qs])
    vol = np.array([data[a.qs[0]][s][2] for s in seeds])               # null twin: same for every size
    part = np.array(a.qs, float) / vol.mean()
    m = peak.mean(1)
    rs = np.random.RandomState(0)
    idx = rs.randint(0, len(seeds), size=(a.boot, len(seeds)))
    bm = peak[:, idx].mean(2)                                         # sizes x boot
    deltas = []
    for b in range(a.boot):
        if (bm[:, b] > 0).all():
            deltas.append(slope(np.log(part), np.log(bm[:, b])))
    deltas = np.array(deltas)
    res = dict(n_seeds=len(seeds), seeds=[seeds[0], seeds[-1]], qs=a.qs, window_volume_mean=float(vol.mean()),
               participation=[float(x) for x in part], peak_mean_cents=[float(x) for x in m],
               peak_ci95=[[float(np.percentile(bm[i], 2.5)), float(np.percentile(bm[i], 97.5))] for i in range(len(a.qs))],
               decay_ratio=[float(post[i].mean() / m[i]) if m[i] != 0 else None for i in range(len(a.qs))],
               delta=slope(np.log(part), np.log(m)) if (m > 0).all() else None,
               delta_ci95=[float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))] if len(deltas) else None,
               boot_valid_frac=float(len(deltas) / a.boot))
    lo, hi = res["delta_ci95"] or (np.nan, np.nan)
    if res["delta"] is None or len(deltas) == 0:
        verdict = "impact saturates or is unresolved (flag)"
    elif hi < 0.3:
        verdict = "impact saturates or is unresolved (flag)"
    elif lo > 0.7:
        verdict = "near-linear impact, not square-root-like (flag)"
    else:
        verdict = "consistent with concave, square-root-like impact"
    res["verdict"] = verdict
    # POST HOC (not pre-registered), labelled as such in every output:
    resolved = [i for i in range(len(a.qs)) if res["peak_ci95"][i][0] > 0]
    res["post_hoc"] = dict(
        note="not pre-registered; added after seeing E7",
        resolved_sizes=[a.qs[i] for i in resolved],
        delta_resolved=slope(np.log(part[resolved]), np.log(m[resolved])) if len(resolved) >= 2 else None,
        delta_resolved_ci95=(lambda ds: [float(np.percentile(ds, 2.5)), float(np.percentile(ds, 97.5))] if len(ds) else None)(
            np.array([slope(np.log(part[resolved]), np.log(bm[resolved, b])) for b in range(a.boot) if (bm[resolved, b] > 0).all()])),
        delta_resolved_valid_frac=float(np.mean([(bm[resolved, b] > 0).all() for b in range(a.boot)])),
        doubling_ratios=[float(m[i + 1] / m[i]) if m[i] > 0 else None for i in range(len(a.qs) - 1)],
        sqrt_law_doubling_ratio=float(np.sqrt(2)),
        post_gap_mean_cents=[float(post[i].mean()) for i in range(len(a.qs))],
        post_gap_ci95=[[float(np.percentile(post[i, idx].mean(1), 2.5)), float(np.percentile(post[i, idx].mean(1), 97.5))]
                       for i in range(len(a.qs))])
    json.dump(res, open(os.path.join(ROOT, "eval", "results", "realism_scorecard.json"), "w"), indent=1)
    lines = ["# Realism scorecard (pre-registered E7): impact vs size, TWAP, synced twins", "",
             f"Seeds {seeds[0]}–{seeds[-1]} (n = {len(seeds)} per size, same seeds at every size); "
             f"window volume V = {vol.mean():.0f} shares (null twin). Peak impact = mean twin gap at T1 (end of execution).", "",
             "| Q (shares) | Q/V | peak impact @T1 (¢) | 95% CI | decay ratio (T1+10 min / T1) |", "|---|---|---|---|---|"]
    for i, q in enumerate(a.qs):
        d = res["decay_ratio"][i]
        lines.append(f"| {q} | {part[i]:.3f} | {m[i]:+.2f} | [{res['peak_ci95'][i][0]:+.2f}, {res['peak_ci95'][i][1]:+.2f}] | "
                     f"{'n/a' if d is None else f'{d:.2f}'} |")
    dtxt = "n/a" if res["delta"] is None else f"{res['delta']:.3f}"
    lines += ["", f"**δ = {dtxt}**, 95% paired-bootstrap CI [{lo:.3f}, {hi:.3f}] "
              f"({res['boot_valid_frac']:.0%} of resamples had positive impact at every size). "
              f"Square-root law: δ ≈ 0.5. **Verdict (pre-registered rule): {verdict}.**"]
    ph = res["post_hoc"]
    dr = ", ".join("n/a" if r is None else f"×{r:.2f}" for r in ph["doubling_ratios"])
    pg = ", ".join(f"{q}: {g:+.2f} [{c[0]:+.2f}, {c[1]:+.2f}]" for q, g, c in zip(a.qs, ph["post_gap_mean_cents"], ph["post_gap_ci95"]))
    dres = "n/a" if ph["delta_resolved"] is None else f"{ph['delta_resolved']:.2f}"
    lines += ["", "**Post hoc (not pre-registered).** The rule above is lenient: it accepts any CI overlapping [0.3, 0.7]. "
              f"Impact ratio per size doubling: {dr} (square-root law: ×{ph['sqrt_law_doubling_ratio']:.2f}; linear: ×2). "
              f"Slope over the sizes whose peak CI excludes 0 ({ph['resolved_sizes']}): δ = {dres}, 95% CI "
              f"[{ph['delta_resolved_ci95'][0]:.2f}, {ph['delta_resolved_ci95'][1]:.2f}] ({ph['delta_resolved_valid_frac']:.0%} of draws valid). "
              f"Twin gap 10 min after completion, ¢ (mean [95% CI]): {pg}."]
    open(os.path.join(ROOT, "eval", "results", "realism_scorecard.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
