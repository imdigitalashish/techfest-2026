"""Deck figures, drawn only from committed results. Run: python3 innovatex-t3-coastal-plastic/deliverables/make_figures.py"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "deliverables" / "figures"
AN = json.loads((ROOT / "components/twin_sim/results/analysis.json").read_text())
plt.rcParams.update({"font.size": 13, "axes.spines.top": False, "axes.spines.right": False})


def escape_split() -> None:
    causes = [("entrainment", "under / through the boom", "#c0392b"), ("overtopping", "overflow of a full pocket", "#e67e22"),
              ("bypass_release", "flood release", "#7f8c8d")]
    pols = [("P0", "Fixed schedule"), ("P1", "Clear when full"), ("P2", "Tide-aware dispatch")]
    fig, ax = plt.subplots(figsize=(7.6, 5.6))
    for y, (p, label) in enumerate(pols):
        left = 0.0
        for key, name, col in causes:
            v = AN["escape_split"][p]["by_cause"][key]["share_of_escaped"]["median"] * 100
            ax.barh(y, v, left=left, color=col, label=name if y == 0 else None, height=0.55)
            if v >= 4:
                ax.text(left + v / 2, y, f"{v:.0f}%", ha="center", va="center", color="white", fontsize=12, weight="bold")
            left += v
    ax.set_yticks(range(len(pols)), [lab for _, lab in pols])
    ax.set_xlim(0, 100)
    ax.set_xlabel("share of escaped plastic (median of draws, %)")
    ax.set_title("Why plastic gets past the boom\nSIMULATED · held-out monsoons 2024–25", fontsize=14)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=1, frameon=False, fontsize=11)
    fig.text(0.01, 0.01, "'Under the boom' includes the leak the twin assumes even in still water. "
             "Source: components/twin_sim/results/analysis.json", fontsize=8, color="#555")
    fig.tight_layout()
    fig.savefig(FIG / "fig_escape_split.png", dpi=160)
    plt.close(fig)


def levers() -> None:
    pair = AN["paired_escaped_rel_diff"]
    fs = AN["fuse_sensitivity_P2"]
    rows = [
        ("Tide-aware vs clear-when-full", pair["P2_vs_P1"], "SIMULATED"),
        ("Tide-aware vs fixed schedule", pair["P2_vs_P0"], "SIMULATED"),
        ("Clear-when-full vs fixed schedule", pair["P1_vs_P0"], "SIMULATED"),
        ("Fail-open fuse alone", fs["b_fail_open_fuse"]["escaped_rel_vs_a"], "SENSITIVITY"),
        ("Fuse + one-way pocket (re-float ×0.5)", fs["c_fuse_refloat_x0.5"]["escaped_rel_vs_a"], "SENSITIVITY"),
        ("Fuse + one-way pocket (re-float ×0.2)", fs["c_fuse_refloat_x0.2"]["escaped_rel_vs_a"], "SENSITIVITY"),
    ]
    angle = AN.get("boom_angle_sensitivity_P2")
    if isinstance(angle, dict):
        for key, label in (("theta_30", "Boom angled at 30°"), ("theta_20", "Boom angled at 20°")):
            r = angle.get(key, {}).get("escaped_rel_vs_90") if isinstance(angle.get(key), dict) else None
            if isinstance(r, dict):
                rows.append((label, r, "SENSITIVITY"))
    fig, ax = plt.subplots(figsize=(8.8, 6.0))
    for i, (label, r, kind) in enumerate(rows):
        y = len(rows) - 1 - i
        col = "#1f6f8b" if kind == "SIMULATED" else "#8e44ad"
        med, lo, hi = 100 * r["median"], 100 * r["p05"], 100 * r["p95"]
        ax.plot([lo, hi], [y, y], color=col, lw=3, solid_capstyle="round")
        ax.plot(med, y, "o", color=col, ms=9)
        ax.text(max(hi, med) + 0.6, y, f"{med:+.1f}%".replace("-", "−"), va="center", fontsize=11, color=col)
    ax.axvline(0, color="#333", lw=1)
    ax.set_yticks(range(len(rows)), [r[0] for r in reversed(rows)], fontsize=11)
    ax.set_xlabel("change in escaped plastic (%)\ndot = median · bar = 90% interval · left is better", fontsize=12)
    ax.set_title("Where the leverage is (digital twin)\nblue = SIMULATED policy comparison · purple = SENSITIVITY (assumed)", fontsize=12)
    fig.text(0.01, 0.01, "Paired over the same Monte Carlo draws, held-out 2024–25. Source: components/twin_sim/results/analysis.json",
             fontsize=8, color="#555")
    fig.tight_layout()
    fig.savefig(FIG / "fig_levers.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    escape_split()
    levers()
    print("wrote", ", ".join(p.name for p in sorted(FIG.glob("*.png"))))
