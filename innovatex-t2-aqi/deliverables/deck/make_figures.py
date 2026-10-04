"""Figures for the zonal deck, generated from committed results (no hand-typed numbers).
Run: cd deliverables/deck && OMP_NUM_THREADS=1 python make_figures.py   → fig_*.png
"""
import csv, json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
plt.rcParams.update({"font.size": 13, "axes.spines.top": False, "axes.spines.right": False})
INK, ACCENT, GREY, WARN = "#1f2937", "#0f766e", "#9ca3af", "#b45309"


def fig_forecast():
    r = json.load(open(os.path.join(ROOT, "eval", "results", "forecast_walkforward.json")))
    pm25 = next(x for x in r["results"] if x["target"] == "pm25")
    keys = ["persistence", "gbm_logratio_no_future_met", "gbm_logratio_perfect_prog_met", "cams_as_served_reference"]
    labels = ["Yesterday's value\n(persistence)", "ML, no future weather\n(retrospective ERA5)", "ML + tomorrow's actual\nweather (ORACLE)", "Global model, one grid\npoint (CAMS, as served)"]
    vals = [pm25["models"][k]["all"]["MAE"] for k in keys]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    bars = ax.bar(labels, vals, color=[ACCENT, GREY, GREY, WARN])
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.1f}", ha="center", fontsize=14, color=INK)
    ax.set_ylabel("Mean absolute error, µg/m³")
    ax.set_title(f"Next-day PM2.5 (24-h mean) at 4 Delhi monitors, Nov 2025–Sep 2026 (n={pm25['n_test']})", fontsize=13)
    fig.text(0.01, 0.01, "Real CPCB/DPCC data (OpenAQ archive) + ERA5. Walk-forward, time-ordered. eval/forecast_walkforward.py", fontsize=9, color=GREY)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(os.path.join(HERE, "fig_forecast.png"), dpi=200)


def fig_attribution():
    bd = json.load(open(os.path.join(ROOT, "components", "attribution", "autoresearch", "breakdown_v21.json")))["methods"]
    keys = ["pair_fixed", "ring", "ring_refcal", "ring_refcal14", "ring_selfcal"]
    labels = ["Fixed upwind/\ndownwind pair", "Wind-resolved\nring", "Ring + weekly\nreference visit", "Ring + 14-day median\nof reference visits", "Ring + idle-hour\nself-calibration"]
    allh = [bd[k]["mae_all"] for k in keys]
    work = [bd[k]["mae_work"] for k in keys]
    x = np.arange(len(keys)); wdt = 0.38
    fig, ax = plt.subplots(figsize=(11, 5.2))
    b1 = ax.bar(x - wdt / 2, allh, wdt, color=[GREY] * 4 + [ACCENT], label="all hours (abstentions scored 0)")
    b2 = ax.bar(x + wdt / 2, work, wdt, color="white", edgecolor=[GREY] * 4 + [ACCENT], hatch="//", label="work hours only (08–18, Mon–Sat)")
    for b, v in list(zip(b1, allh)) + list(zip(b2, work)):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, f"{v:.1f}", ha="center", fontsize=11, color=INK)
    ax.set_xticks(x, labels)
    ax.set_ylabel("Error in the site's own PM10, µg/m³ (MAE)")
    ax.set_ylim(0, max(work + allh) * 1.18)
    ax.legend(frameon=False, fontsize=11, loc="upper right")
    ax.set_title("Simulated sites on real Delhi background + wind · held-out Jan–Sep 2026, fresh seeds (not blind)", fontsize=12)
    fig.text(0.01, 0.01, "REAL background PM10 (CPCB monitor) + REAL ERA5 wind; SIMULATED site, plumes, sensors and faults. "
             "eval_v2.py v2.1 via breakdown_v21.py; abstain below 0.5 m/s", fontsize=9, color=WARN)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(os.path.join(HERE, "fig_attribution.png"), dpi=200)


def fig_timeseries():
    sys.path.insert(0, os.path.join(ROOT, "components", "attribution", "autoresearch"))
    import eval_v2 as ev  # frozen evaluator v2.1 (load + simulate)
    import methods
    df = ev.load()
    obs, tmax, tdiff, geom = ev.simulate(df, np.random.default_rng(ev.DEV_SEEDS[0]), ev.SCENARIOS["medium"])
    est_p, _ = methods.pair_fixed(obs, geom)
    est_r, ab = methods.ring_selfcal(obs, geom)
    w = (obs.index >= "2025-11-17") & (obs.index < "2025-11-24")
    t = obs.index[w]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 6.2), sharex=True, gridspec_kw={"height_ratios": [1, 1.4]})
    a1.plot(t, df["bg"].reindex(obs.index)[w], color=INK, lw=1.4)
    a1.set_ylabel("Delhi background\nPM10, µg/m³")
    a1.set_title("One week in Nov 2025: real Delhi background (top) vs a simulated site's own dust (bottom)", fontsize=13)
    a2.fill_between(t, 0, tmax[w], color=ACCENT, alpha=0.25, label="True site contribution (simulated)")
    a2.plot(t, est_p[w], color=GREY, lw=1.2, label="Fixed-pair estimate")
    a2.plot(t, np.where(ab[w], np.nan, est_r[w]), color=ACCENT, lw=1.6, label="DustLedger estimate (gaps = 'inconclusive')")
    a2.axhline(0, color=GREY, lw=0.6)
    top = 700.0
    pk = float(np.nanmax(tmax[w]))
    if pk > top:  # clip for readability and say so on the figure
        a2.set_ylim(top=top)
        tp = t[int(np.nanargmax(tmax[w]))]
        a2.annotate(f"calm-wind peak {pk:,.0f} µg/m³ (clipped)", xy=(tp, top * 0.97), xytext=(tp + (t[-1] - t[0]) * 0.12, top * 0.82),
                    fontsize=10, color=INK, ha="left", arrowprops=dict(arrowstyle="->", color=INK))
    a2.set_ylabel("Site's own PM10, µg/m³")
    a2.legend(loc="upper left", fontsize=10, frameon=False)
    fig.text(0.01, 0.01, "Background = CPCB/DPCC monitor 6929 (real); wind = ERA5 (real); site + sensors SIMULATED (eval_v2.1, 'medium' scenario, seed 11).", fontsize=9, color=WARN)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(os.path.join(HERE, "fig_timeseries.png"), dpi=200)


def fig_site():
    fig, ax = plt.subplots(figsize=(7, 6.2))
    ax.add_patch(plt.Rectangle((-60, -60), 120, 120, fill=False, lw=2, color=INK))
    ax.text(0, 0, "Construction\nsite", ha="center", va="center", fontsize=14, color=INK)
    nodes = {"N": (0, 60), "E": (60, 0), "S": (0, -60), "W": (-60, 0)}
    for n, (x, y) in nodes.items():
        c = ACCENT if n in ("E", "S") else GREY
        ax.plot(x, y, "o", ms=16, color=c)
        ax.text(x * 1.32, y * 1.32, f"node {n}", ha="center", va="center", fontsize=11)
    ax.annotate("", xy=(-55, 40), xytext=(-125, 110), arrowprops=dict(arrowstyle="-|>", lw=3, color=INK))
    ax.text(-125, 120, "wind", fontsize=12)
    ax.add_patch(plt.Polygon([(-20, 20), (130, -70), (70, -130)], color=ACCENT, alpha=0.15))
    ax.text(95, -110, "site plume", fontsize=11, color=ACCENT)
    ax.text(-150, -150, "Upwind nodes breathe Delhi.\nDownwind nodes breathe Delhi + the site.\nThe difference is the site's own dust.", fontsize=12, color=INK)
    ax.set_xlim(-160, 160); ax.set_ylim(-170, 150); ax.set_aspect("equal"); ax.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "fig_site.png"), dpi=200)


if __name__ == "__main__":
    fig_forecast(); fig_attribution(); fig_site(); fig_timeseries()
    print("figures written")
