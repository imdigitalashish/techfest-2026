"""POST-HOC diagnostic (not pre-registered), run after the pre-registered balance check flagged TVD ~0.36 in every user feature.

Question: are the Random and BTS user populations really different, or do the two files hash a category differently?
Compares, within W2 and per user feature: (a) shares of categories present in both files, and (b) the label-free TVD
between the sorted share vectors. Reproduce: .venv/bin/python eval/obd_balance_posthoc.py -> eval/results/obd_balance_posthoc.md
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "eval"))
from run_obd_slice import HOUR, S, load  # noqa: E402

R, B = load(S / "random" / "all" / "all.npz"), load(S / "bts" / "all" / "all.npz")
t0, t_end = max(R["ts"].min(), B["ts"].min()), (B["ts"].max() // HOUR) * HOUR
t_mid = t0 + (t_end - t0) // 2
R2 = {k: v[(R["ts"] >= t_mid) & (R["ts"] < t_end)] for k, v in R.items()}
B2 = {k: v[(B["ts"] >= t_mid) & (B["ts"] < t_end)] for k, v in B.items()}
L = ["# POST-HOC balance diagnostic (W2; not pre-registered)", "",
     "The pre-registered check (TVD over hashed categories) flagged ~0.36 for every user feature. This diagnostic asks whether that is a population difference or a labelling difference between the two files.", "",
     "| feature | categories R / B / shared | TVD on shared labels (+ other) | label-free TVD (sorted shares) | sorted shares R | sorted shares B |", "|---|---|---|---|---|---|"]
for j in range(4):
    x, y = R2[f"uf{j}"], B2[f"uf{j}"]
    ux, cx = np.unique(x, return_counts=True)
    uy, cy = np.unique(y, return_counts=True)
    shared = np.intersect1d(ux, uy)
    px = np.array([np.mean(x == c) for c in shared] + [np.mean(~np.isin(x, shared))])
    py = np.array([np.mean(y == c) for c in shared] + [np.mean(~np.isin(y, shared))])
    sx, sy = np.sort(cx / cx.sum())[::-1], np.sort(cy / cy.sum())[::-1]
    m = max(len(sx), len(sy))
    sx, sy = np.pad(sx, (0, m - len(sx))), np.pad(sy, (0, m - len(sy)))
    L.append(f"| user_feature_{j} | {len(ux)} / {len(uy)} / {len(shared)} | {0.5 * np.abs(px - py).sum():.4f} | {0.5 * np.abs(sx - sy).sum():.4f} | "
             f"{np.round(sx, 3).tolist()} | {np.round(sy, 3).tolist()} |")
L += ["", "Reading: if the label-free TVD is near 0 while the hashed TVD is ~0.36, one category carries a different hash in each file, and the populations match in distribution. The pre-registered caveat is then a data-labelling artefact rather than an imbalance; the pre-registered result is still reported as is."]
(ROOT / "eval" / "results" / "obd_balance_posthoc.md").write_text("\n".join(L) + "\n")
print("\n".join(L))
