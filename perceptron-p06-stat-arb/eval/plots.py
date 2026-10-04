"""Plots for the deliverables from a committed results JSON (no recomputation).

Usage: .venv/bin/python -m eval.plots eval/results/baseline_0901_to_1001.json
"""
from __future__ import annotations

import json
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

POL = [("naive", "naive: every cross > fees", "#999999"), ("threshold_pair", "tuned per-pair threshold", "#1f77b4"),
       ("ev_kmpair", "EV = S(L|pair)·net − (1−S)·λ", "#d62728"), ("ev_wait_kmpair", "EV + optimal wait Δ*", "#ff7f0e"),
       ("lev", "LEV (learned value, 1.5 ms model)", "#2ca02c")]


def main(path: str) -> None:
    res = json.load(open(path))
    rows = res["policy_frontier"]
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
    for ax, tier in zip(axes[:2], ("f0", "f1")):
        ref = next(r for r in rows if r["tier"] == tier and r["policy"] == "oracle")["pnl_usd"]
        for key, label, c in POL:
            pts = sorted((r["delta_ms"], r["pnl_usd"]) for r in rows if r["tier"] == tier and r["policy"] == key)
            ax.plot([p[0] for p in pts], [p[1] for p in pts], marker="o", ms=3, label=label, color=c)
        ax.axhline(0, color="k", lw=0.6)
        ax.axhline(ref, color="k", lw=0.6, ls=":", label="zero-latency naive")
        ax.set_xscale("log"); ax.set_xlabel("one-way latency δ (ms); order latency = feed latency = δ")
        ax.set_ylabel("simulated P&L, USD/day (0.05 BTC cap)")
        ax.set_title(f"Latency–P&L frontier, taker fee {tier[1:]} bps/leg\nheld-out day {res['meta']['test']}")
        ax.legend(fontsize=7)
    d = res["decay"]["overall_test"][0]
    ts = [float(k[2:-3]) for k in d if k.startswith("S(")]
    ss = [d[k] for k in d if k.startswith("S(")]
    axes[2].plot(ts, ss, marker="o", ms=3, color="k", label="all pairs")
    for r in res["decay"]["by_instr_group"]:
        axes[2].plot(ts, [r[f"S({t:g}ms)"] for t in ts], ms=2, marker=".", label=r["instr_group"])
    axes[2].set_xscale("log"); axes[2].set_ylim(0, 1.02)
    axes[2].set_xlabel("time since the mispricing appeared (ms, exchange clock)")
    axes[2].set_ylabel("share still open, Kaplan–Meier S(t)")
    axes[2].set_title(f"Decay: median lifetime {d['half_life_ms']:.0f} ms (n={d['n']:,})")
    axes[2].legend(fontsize=7)
    fig.tight_layout()
    out = path.replace(".json", "_frontier.png")
    fig.savefig(out, dpi=130)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1])
