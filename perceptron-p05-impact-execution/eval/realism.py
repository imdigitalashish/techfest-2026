"""C1 isolated metric: realism scorecard for impact in the simulator.

Size sweep with TWAP over the same window: peak own impact I(Q) = mean twin gap at the end of
execution (T1 = 1,200 s), and the decay ratio = mean gap 10 min after T1 / mean gap at T1.
Fits I ∝ (Q/V)^delta on log-log axes (square-root law: delta ≈ 0.5; TSE survey <delta> = 0.489,
arXiv:2411.13965 / 2607.04280).

Usage:
  for q in 1000 2000 4000 8000 16000; do
    nice -n 10 .venv/bin/python eval/run_experiment.py --exp E7_size_q$q --seeds 100:140 --qty $q \
      --policies eval/policies/twap_only.json --workers 9 --rng-sync per_wakeup; done
  .venv/bin/python eval/realism.py --qs 1000 2000 4000 8000 16000
"""
import argparse, glob, os, pickle
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(exp):
    G, V = [], []
    for f in sorted(glob.glob(os.path.join(ROOT, ".data", "runs", exp, "seed_*.pkl"))):
        r = pickle.load(open(f, "rb"))
        G.append(r["runs"]["TWAP"]["path"])
        V.append(float(np.sum(r["slot_vol"])))
    return np.array(G, float), np.array(V, float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qs", nargs="+", type=int, required=True)
    ap.add_argument("--prefix", default="E7_size_q")
    a = ap.parse_args()
    rows, xs, ys = [], [], []
    rs = np.random.RandomState(0)
    for q in a.qs:
        G, V = load(f"{a.prefix}{q}")
        if len(G) == 0:
            continue
        peak = G[:, 1200]
        post = G[:, 1800]
        bm = rs.choice(peak, (5000, len(peak))).mean(1)
        part = q / V.mean()
        rows.append((q, len(G), part, peak.mean(), np.percentile(bm, 2.5), np.percentile(bm, 97.5),
                     post.mean() / peak.mean() if peak.mean() != 0 else np.nan))
        if peak.mean() > 0:
            xs.append(np.log(part)); ys.append(np.log(peak.mean()))
    lines = ["| Q (shares) | n | Q/V (window) | peak impact @T1 (¢) | 95% CI | decay ratio (+10 min / T1) |",
             "|---|---|---|---|---|---|"]
    for q, n, p, m, lo, hi, d in rows:
        lines.append(f"| {q} | {n} | {p:.3f} | {m:+.2f} | [{lo:+.2f}, {hi:+.2f}] | {d:.2f} |")
    if len(xs) >= 2:
        delta, c = np.polyfit(xs, ys, 1)
        lines += ["", f"Fitted exponent delta = {delta:.3f} (square-root law: ~0.5) over {len(xs)} sizes with positive mean impact."]
    out = os.path.join(ROOT, "eval", "results", "realism_scorecard.md")
    open(out, "w").write("# Realism scorecard: impact vs size (TWAP, synced twins)\n\n" + "\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
