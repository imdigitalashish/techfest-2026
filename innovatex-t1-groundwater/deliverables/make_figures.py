"""Figures for the zonal deck. Real data where labelled REAL; simulated pits labelled SIMULATED.

Run: innovatex-t1-groundwater/.venv/bin/python innovatex-t1-groundwater/deliverables/make_figures.py
Out: innovatex-t1-groundwater/deliverables/figures/*.png
"""
from __future__ import annotations

import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "components" / "twin_simulator"))
sys.path.insert(0, str(ROOT / "components" / "recharge_verifier"))
import simulate as sim  # noqa: E402
import verifier  # noqa: E402

plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})


def fig_dwlr_quality() -> None:
    lv = pd.read_csv(ROOT / "eval/data/delhi_gw_levels.csv.gz", low_memory=False)
    tel = lv[lv["mode"] == "Telemetric"].copy()
    tel["t"] = pd.to_datetime(tel["datetime_ist"])
    g = tel.groupby("station_id")
    st = pd.DataFrame({"lat": g.latitude.first(), "lon": g.longitude.first(),
                       "zero_share": g.value_m.apply(lambda v: float((v == 0).mean())),
                       "last": g.t.max()})
    st["live2026"] = st["last"] >= "2026-01-01"
    bad = ~(st.lat.between(28.3, 29.0) & st.lon.between(76.8, 77.5))
    n_bad = int(bad.sum())
    st = st[~bad]
    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    sc = ax.scatter(st.lon, st.lat, c=st.zero_share * 100, cmap="RdYlGn_r", vmin=0, vmax=100, s=36,
                    edgecolors=np.where(st.live2026, "black", "none"), linewidths=0.8)
    cb = fig.colorbar(sc, ax=ax, shrink=0.8)
    cb.set_label("% of readings exactly 0.000 m")
    ax.set_xlabel("longitude")
    ax.set_ylabel("latitude")
    ax.set_title(f"REAL · India-WRIS, fetched 4 Oct 2026\n{len(st)} of {len(st) + n_bad} telemetric DWLRs mapped · "
                 f"ringed = reported in 2026 ({int(st.live2026.sum())})", fontsize=10)
    ax.set_aspect(1 / np.cos(np.deg2rad(28.6)))
    fig.tight_layout()
    fig.savefig(OUT / "dwlr_quality_map.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_pit_story() -> None:
    rng = np.random.default_rng(7)
    rain_h = sim.load_rain("2025-07-01", "2025-08-31 23:00")
    rain_m = sim.minute_rain(rain_h, rng)
    p = sim.PitTruth(structure_id="SIM-PIT-DEMO", kind="clogging", catchment_m2=250, runoff_coeff=0.8,
                     pit_area_m2=2.25, overflow_stage_m=1.5, k0_per_h=0.4, clog_rate_per_m3=0.008,
                     inlet_blocked_from=None,
                     fakes=[(pd.Timestamp("2025-08-20 15:00"), 1.2)])
    obs, truth = sim.simulate_pit(p, rain_m, rng)
    reg = {"structure_id": p.structure_id, "pit_area_m2": 2.25, "catchment_m2": 250, "runoff_coeff": 0.75,
           "overflow_stage_m": 1.5, "k_as_built_per_h": 0.4}
    ev = verifier.verify(obs["stage_m"], rain_m, reg)
    colors = {"verified": "tab:green", "clogged": "tab:orange", "no_inflow": "tab:gray", "implausible": "tab:red"}
    fig, (a1, a2, a3) = plt.subplots(3, 1, figsize=(10, 7.2), sharex=True,
                                     gridspec_kw={"height_ratios": [1, 2, 1.2]})
    a1.bar(rain_h.index, rain_h.values, width=0.04, color="tab:blue")
    a1.set_ylabel("rain\nmm/h")
    a1.set_title("Rain: REAL (ERA5 hourly, central Delhi, Jul–Aug 2025).  Pit: SIMULATED (250 m² roof, 2.25 m² pit)", fontsize=10)
    o = obs["stage_m"].resample("10min").mean()
    a2.plot(o.index, o.values, color="black", lw=0.8)
    for e in ev:
        a2.axvspan(e["t_start"], e["t_end"], color=colors[e["verdict"]], alpha=0.25, lw=0)
    a2.set_ylabel("pit water\ncolumn (m)")
    for k_, c_ in colors.items():
        a2.plot([], [], color=c_, lw=8, alpha=0.4, label=k_)
    a2.legend(loc="upper left", ncol=4, fontsize=9, frameon=False)
    ci = [(e["t_end"], e["clogging_index"]) for e in ev if e["clogging_index"] is not None and e["verdict"] != "no_inflow"]
    if ci:
        t_, c_ = zip(*ci)
        a3.plot(t_, c_, "o-", color="tab:orange", ms=3)
    a3.axhline(0.5, color="tab:red", ls="--", lw=1)
    a3.text(rain_h.index[0], 0.52, "maintenance threshold", color="tab:red", fontsize=9)
    a3.set_ylabel("clogging\nindex")
    a3.set_ylim(0, 1.2)
    import matplotlib.dates as mdates
    a3.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    fig.tight_layout()
    fig.savefig(OUT / "pit_event_story.png", dpi=150)
    plt.close(fig)
    tot_true = truth["infil_m3"].sum()
    tot_est = sum(e["recharged_m3"] for e in ev if e["verdict"] != "no_inflow")
    print(f"demo pit: events={len(ev)} verdicts={pd.Series([e['verdict'] for e in ev]).value_counts().to_dict()} "
          f"infiltrated true={tot_true:.1f} m3 est={tot_est:.1f} m3")


if __name__ == "__main__":
    fig_dwlr_quality()
    fig_pit_story()
    print("figures in", OUT)
