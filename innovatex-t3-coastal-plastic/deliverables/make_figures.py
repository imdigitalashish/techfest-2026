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
    pols = [("P0", "Assumed roster"), ("P1", "Fill-fraction rule"), ("P2", "Full policy")]
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
    fig.text(0.01, 0.01, "'Under the boom' includes the still-water leak the twin assumes. Medians of shares need not sum to 100%. "
             "Source: components/twin_sim/results/analysis.json", fontsize=8, color="#555")
    fig.tight_layout()
    fig.savefig(FIG / "fig_escape_split.png", dpi=160)
    plt.close(fig)


def levers() -> None:
    pair = AN["paired_escaped_rel_diff"]
    abl = AN.get("ablations", {}).get("paired_escaped_rel_diff", {})
    fs = AN["fuse_sensitivity_P2"]
    ang = AN.get("boom_angle_sensitivity_P2", {})
    rows = [
        ("Full policy vs fill-fraction rule", pair["P2_vs_P1"], "SIMULATED"),
        ("Full policy vs assumed fixed roster", pair["P2_vs_P0"], "SIMULATED"),
    ]
    if "P2_vs_P2_notide" in abl:
        rows.append(("Tide timing alone", abl["P2_vs_P2_notide"], "SIMULATED"))
    if "P1m_vs_P1" in abl:
        rows.append(("Ranking by kg alone", abl["P1m_vs_P1"], "SIMULATED"))
    rows += [
        ("Fail-open section alone", fs["b_fail_open_fuse"]["escaped_rel_vs_a"], "SENSITIVITY"),
        ("One-way pocket (re-float ×0.5)", fs["c_fuse_refloat_x0.5"]["escaped_rel_vs_a"], "SENSITIVITY"),
    ]
    if "theta30" in ang.get("a_current_release", {}):
        rows.append(("Boom angled at 30° (vs square-on)", ang["a_current_release"]["theta30"]["escaped_rel_vs_theta90"], "SENSITIVITY"))
    if "theta20" in ang.get("c_fuse_refloat_x0.5", {}):
        rows.append(("20° + fuse + pocket (vs today)", ang["c_fuse_refloat_x0.5"]["theta20"]["escaped_rel_vs_current_a_theta90"], "SENSITIVITY"))
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
    ax.set_xlabel("change in escaped plastic (%)\ndot = median · bar = central 90% scenario range · left is better", fontsize=12)
    ax.set_title("Where the leverage is (digital twin)\nblue = SIMULATED policy comparison · purple = SENSITIVITY (assumed)", fontsize=12)
    fig.text(0.01, 0.01, f"Paired over the same {AN['n_draws']} sampled parameter settings of one model, held-out 2024–25. Rows are separate what-ifs: do not add them. Source: components/twin_sim/results/analysis.json",
             fontsize=8, color="#555")
    fig.tight_layout()
    fig.savefig(FIG / "fig_levers.png", dpi=160)
    plt.close(fig)


def retrofit_concept() -> None:
    """Top-view concept sketch of the retrofit. Not to scale; PLANNED; untested."""
    from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle, Wedge
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 10, 0.8, color="#b9a98c"))
    ax.add_patch(Rectangle((0, 5.2), 10, 0.8, color="#b9a98c"))
    ax.add_patch(Rectangle((0, 0.8), 10, 4.4, color="#d7e9f2"))
    ax.text(0.15, 0.3, "near bank: crew access, existing conveyor", fontsize=10)
    ax.text(0.15, 5.5, "far bank", fontsize=10)
    ax.add_patch(FancyArrowPatch((0.6, 3.6), (2.4, 3.6), arrowstyle="-|>", mutation_scale=18, color="#1f6f8b", lw=2))
    ax.text(0.6, 3.85, "ebb / storm flow → sea", fontsize=10, color="#1f6f8b")
    ax.add_patch(FancyArrowPatch((2.4, 2.4), (0.6, 2.4), arrowstyle="-|>", mutation_scale=18, color="#7f8c8d", lw=2, ls="--"))
    ax.text(0.6, 2.0, "flood tide (reverses)", fontsize=10, color="#7f8c8d")
    ax.plot([8.6, 8.6], [0.8, 5.2], color="#999", lw=3, ls=":")
    ax.text(8.7, 4.6, "today:\nsquare-on\nsteel-net boom", fontsize=9, color="#666")
    ax.plot([3.6, 7.6], [5.2, 1.7], color="#c0392b", lw=4)
    ax.text(5.9, 3.9, "retrofit: angled boom\n(normal velocity = u·sin θ)", fontsize=10, color="#c0392b", rotation=-41)
    ax.plot([5.0, 5.75], [3.98, 3.32], color="#8e44ad", lw=6)
    ax.add_patch(Wedge((5.0, 3.98), 0.75, 220, 300, color="#8e44ad", alpha=0.25))
    ax.text(3.25, 3.0, "fail-open section:\nhinged, counterweighted;\nintended to open at a set head\n(opening head, delay, reset: to test)",
            fontsize=9, color="#8e44ad")
    ax.add_patch(Polygon([[7.6, 1.7], [9.4, 1.7], [9.4, 0.8], [7.6, 0.8]], closed=True, color="#f5cba7", ec="#e67e22", lw=2))
    ax.text(7.7, 1.05, "bank pocket", fontsize=10)
    for x in (7.65, 7.75, 7.85):
        ax.plot([x, x + 0.18], [1.7, 1.95], color="#e67e22", lw=2)
    ax.text(5.2, 0.95, "one-way flaps (retention\nunder reversal: to test)", fontsize=9, color="#e67e22")
    ax.plot([9.6], [0.4], "s", color="#333", ms=10)
    ax.add_patch(Wedge((9.6, 0.4), 1.6, 100, 160, color="#2c3e50", alpha=0.12))
    ax.text(8.9, 0.62, "sensor pole", fontsize=8.5)
    ax.text(4.55, 0.06, "camera: mat area in pocket (fill) · ultrasonic over open water (stage)\nif the camera is degraded: fill = unknown → crews follow the roster", fontsize=8.5, color="#2c3e50")
    ax.text(0.15, 4.75, "CONCEPT · NOT TO SCALE · PLANNED · UNTESTED", fontsize=12, weight="bold", color="#555")
    fig.tight_layout()
    fig.savefig(FIG / "fig_retrofit_concept.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    escape_split()
    levers()
    retrofit_concept()
    print("wrote", ", ".join(p.name for p in sorted(FIG.glob("*.png"))))
