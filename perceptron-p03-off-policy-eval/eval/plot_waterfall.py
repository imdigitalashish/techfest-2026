"""Waterfall of the before/after decomposition (demo asset) from the committed simulator-bank runs.

Reproduce: cd perceptron-p03-off-policy-eval && .venv/bin/python eval/plot_waterfall.py [S1_drift_masks_gain]
Reads eval/results/sim_bank_runs.csv (SYNTHETIC data); writes deliverables/figures/<scenario>_waterfall.png.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main(scenario: str = "S1_drift_masks_gain"):
    df = pd.read_csv(ROOT / "eval" / "results" / "sim_bank_runs.csv")
    d = df[(df.scenario == scenario) & (df.estimator == "DECOMP")]
    est = {"policy effect\n(OPE, DR)": d.delta.mean(), "user-mix\nshift": d.mix_hat.mean(), "response drift\n(season)": d.drift_hat.mean()}
    tru = {"policy effect\n(OPE, DR)": d.truth.iloc[0], "user-mix\nshift": d.mix_true.iloc[0], "response drift\n(season)": d.drift_true.iloc[0]}
    naive = d.naive.mean()
    fig, ax = plt.subplots(figsize=(8, 4.2))
    x, cum = 0, 0.0
    labels = []
    for k, v in est.items():
        ax.bar(x, v, bottom=cum, color="#2b8a3e" if v > 0 else "#c92a2a", width=0.6)
        ax.plot([x - 0.3, x + 0.3], [cum + tru[k]] * 2, color="black", lw=2, ls="--")
        top, bot = max(cum, cum + v), min(cum, cum + v)
        ax.text(x + 0.33, (top + bot) / 2, f"{v:+.3f}\n(truth {tru[k]:+.3f})", ha="left", va="center", fontsize=8)
        cum += v
        labels.append(k)
        x += 1
    ax.bar(x, naive, color="#495057", width=0.6)
    ax.text(x + 0.33, naive / 2, f"{naive:+.3f}", ha="left", va="center", fontsize=8)
    lo = min(0, naive, *[sum(list(est.values())[:i + 1]) for i in range(len(est))])
    hi = max(0, naive, *[sum(list(est.values())[:i + 1]) for i in range(len(est))])
    ax.set_ylim(lo - 0.15 * (hi - lo), hi + 0.15 * (hi - lo))
    ax.set_xlim(-0.5, x + 1.0)
    labels.append("dashboard\n(naive after − before)")
    ax.axhline(0, color="grey", lw=0.8)
    ax.set_xticks(range(len(labels)), labels, fontsize=8)
    ax.set_ylabel("change in click-through rate")
    ax.set_title(f"{scenario}: what the before/after number is made of", fontsize=10)
    fig.text(0.01, 0.01, f"SYNTHETIC simulator, mean of {d.seed.nunique()} seeds; bars = our estimates, dashed lines = ground truth", fontsize=7)
    out = ROOT / "deliverables" / "figures"
    out.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(out / f"{scenario}_waterfall.png", dpi=130)
    print(out / f"{scenario}_waterfall.png")


if __name__ == "__main__":
    main(*sys.argv[1:])
