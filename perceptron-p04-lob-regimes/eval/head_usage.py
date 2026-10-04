"""Post-hoc: how often each volatility-regime head is active on each split (exploratory, 2026-10-04).

    cd perceptron-p04-lob-regimes && nice -n 10 python eval/head_usage.py

The regime edges are the 1/3 and 2/3 quantiles of trailing 10-minute realised volatility (rv_600s) on the
2023 training days, exactly as in components/adapter.build_context. Per day, it reports the share of 1-s steps
on which the gate selects each head. Writes eval/results/head_usage.md (aggregates only).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "eval"))

from config_v2 import SPLIT_V2, STEP_S  # noqa: E402

from components.features import build_features  # noqa: E402
from components.ingest import load_book_day  # noqa: E402


def rv(day: str) -> np.ndarray:
    f = build_features(load_book_day(day), step_s=STEP_S)
    return f.col("rv_600s_bps")


def main() -> int:
    train = np.concatenate([rv(d) for d in SPLIT_V2["train"]])
    edges = np.quantile(train, [1 / 3, 2 / 3])
    L = ["# Regime-head usage per day (post-hoc, exploratory)", "",
         "- Command: `nice -n 10 python eval/head_usage.py` · edges = 2023 terciles of trailing 10-min realised volatility: "
         f"{edges[0]:.2f} and {edges[1]:.2f} bps", "- Share of 1-s steps on which the gate selects each head.", ""]
    for split in ("dev", "holdout"):
        L += [f"## {split}", "", "| day | low-vol head | mid-vol head | high-vol head |", "|---|---|---|---|"]
        tot = np.zeros(3)
        for d in SPLIT_V2[split]:
            r = np.searchsorted(edges, rv(d), side="right")
            share = np.bincount(r, minlength=3) / len(r)
            tot += np.bincount(r, minlength=3)
            L.append(f"| {d} | {share[0]:.1%} | {share[1]:.1%} | {share[2]:.1%} |")
        t = tot / tot.sum()
        L += [f"| **all {split} days** | **{t[0]:.1%}** | **{t[1]:.1%}** | **{t[2]:.1%}** |", ""]
    (ROOT / "eval" / "results" / "head_usage.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:4]))
    print([l for l in L if "all " in l])
    return 0


if __name__ == "__main__":
    sys.exit(main())
