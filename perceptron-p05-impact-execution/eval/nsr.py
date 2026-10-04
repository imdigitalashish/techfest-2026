"""C2 isolated metric: noise-to-signal ratio of twin-measured own impact.

NSR(t) = std over seeds of Δmid(t) / |mean over seeds of Δmid(t)|, Δmid = sign*(twin mid - treatment mid).
Usage: .venv/bin/python eval/nsr.py E4_nsr_naive E4_nsr_sync [--label TWAP]
"""
import argparse, glob, os, pickle
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def paths(exp, label):
    P = []
    for f in sorted(glob.glob(os.path.join(ROOT, ".data", "runs", exp, "seed_*.pkl"))):
        P.append(pickle.load(open(f, "rb"))["runs"][label]["path"])
    return np.array(P, float)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("exps", nargs="+"); ap.add_argument("--label", default="TWAP")
    a = ap.parse_args()
    ts = [60, 300, 600, 1200, 1800]
    lines = ["| exp | n | " + " | ".join(f"mean/std/NSR @{t}s" for t in ts) + " |", "|---|---|" + "---|" * len(ts)]
    for e in a.exps:
        A = paths(e, a.label)
        cells = []
        for t in ts:
            m, s = np.nanmean(A[:, t]), np.nanstd(A[:, t], ddof=1)
            cells.append(f"{m:+.2f} / {s:.2f} / {s / max(abs(m), 1e-9):.1f}")
        lines.append(f"| {e} | {len(A)} | " + " | ".join(cells) + " |")
    js = {}
    for e in a.exps:
        A = paths(e, a.label)
        js[e] = {str(t): dict(mean=float(np.nanmean(A[:, t])), std=float(np.nanstd(A[:, t], ddof=1)), n=int(len(A))) for t in ts}
    import json
    json.dump(dict(label=a.label, unit="cents", exps=js), open(os.path.join(
        ROOT, "eval", "results", "nsr_" + "_vs_".join(a.exps) + ".json"), "w"), indent=1)
    out = os.path.join(ROOT, "eval", "results", "nsr_" + "_vs_".join(a.exps) + ".md")
    open(out, "w").write("Twin gap Δmid in cents (+ = adverse), label " + a.label + "\n\n" + "\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
