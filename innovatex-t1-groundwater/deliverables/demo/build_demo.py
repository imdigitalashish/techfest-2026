"""Build the 60-second OFFLINE demo: one self-contained HTML file (no network, no CDN).

Run:  innovatex-t1-groundwater/.venv/bin/python innovatex-t1-groundwater/deliverables/demo/build_demo.py
Out:  innovatex-t1-groundwater/deliverables/demo/jalsakshi-demo.html  (open in any browser, offline)

Panels (provenance is printed on every panel):
  1. REAL   — Delhi telemetric DWLR network from India-WRIS (data quality, 2026 reporting).
  2. SIM    — one recharge pit, SIMULATED, driven by Open-Meteo ARCHIVE hourly rain for central Delhi (default model,
              not pinned; minute pattern synthetic), 1 Jul–31 Aug 2025;
              verdicts computed by the kept C5 verifier (components/recharge_verifier/verifier.py).
              A bucket poured with no rain (scripted fake) is flagged "implausible"; clogging < 0.5 raises a ticket.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent / "jalsakshi-demo.html"
sys.path.insert(0, str(ROOT / "components" / "twin_simulator"))
sys.path.insert(0, str(ROOT / "components" / "recharge_verifier"))
import simulate as sim  # noqa: E402
import verifier  # noqa: E402


def stations() -> dict:
    lv = pd.read_csv(ROOT / "eval/data/delhi_gw_levels.csv.gz", low_memory=False)
    tel = lv[lv["mode"] == "Telemetric"].copy()
    tel["t"] = pd.to_datetime(tel["datetime_ist"])
    g = tel.groupby("station_id")
    st = pd.DataFrame({"name": g.stationName.first(), "agency": g.agencyName.first(), "lat": g.latitude.first(),
                       "lon": g.longitude.first(), "zero": g.value_m.apply(lambda v: float((v == 0).mean())),
                       "last": g.t.max().dt.strftime("%Y-%m-%d"), "n": g.size()})
    total = len(st)
    live = int((st["last"] >= "2026-01-01").sum())
    zero_share = float((tel.value_m == 0).mean())
    st = st[st.lat.between(28.3, 29.0) & st.lon.between(76.8, 77.5)]
    pts = [{"name": r["name"], "agency": r.agency, "lat": round(r.lat, 5), "lon": round(r.lon, 5),
            "zero": round(r.zero, 3), "last": r["last"], "n": int(r.n)} for _, r in st.iterrows()]
    return {"points": pts, "total": total, "live2026": live, "zero_share": round(zero_share, 3),
            "rows": int(len(tel)), "mapped": len(pts)}


def pit() -> dict:
    rng = np.random.default_rng(7)
    rain_h = sim.load_rain("2025-07-01", "2025-08-31 23:00")
    rain_m = sim.minute_rain(rain_h, rng)
    p = sim.PitTruth(structure_id="SIM-PIT-DEMO", kind="clogging", catchment_m2=250, runoff_coeff=0.8,
                     pit_area_m2=2.25, overflow_stage_m=1.5, k0_per_h=0.4, clog_rate_per_m3=0.008,
                     inlet_blocked_from=None, fakes=[(pd.Timestamp("2025-08-20 15:00"), 1.2)])
    p.clog_rate_per_m3 = 0.012   # scripted demo: this pit clogs steadily (SIMULATED)
    obs, truth = sim.simulate_pit(p, rain_m, rng)
    reg = {"structure_id": p.structure_id, "pit_area_m2": 2.25, "catchment_m2": 250, "runoff_coeff": 0.75,
           "overflow_stage_m": 1.5, "k_as_built_per_h": 0.4}
    t0 = obs.index[0]
    st = obs["stage_m"].resample("10min").mean().interpolate(limit=3).fillna(0.0)

    t_end_h = (obs.index[-1] - t0).total_seconds() / 3600.0

    def hrs(t) -> float:  # event windows are padded 30 min; clamp to the data range for display
        return round(min((pd.Timestamp(t) - t0).total_seconds() / 3600.0, t_end_h), 3)

    def score(rain_series: pd.Series) -> dict:
        ev = verifier.verify(obs["stage_m"], rain_series, reg)
        events = []
        for e in ev:
            if e["verdict"] == "no_inflow":
                continue
            tr = truth.loc[e["t_start"]:e["t_end"], "infil_m3"].sum()
            events.append({"t0": hrs(e["t_start"]), "t1": hrs(e["t_end"]), "verdict": e["verdict"],
                           "rain": round(e["rain_mm"], 1), "est": round(e["recharged_m3"], 2),
                           "true": round(float(tr), 2),
                           "ci": None if e["clogging_index"] is None else round(e["clogging_index"], 2),
                           "label": pd.Timestamp(e["t_start"]).strftime("%d %b %H:%M"),
                           "closed": pd.Timestamp(min(pd.Timestamp(e["t_end"]), obs.index[-1])).strftime("%d %b %H:%M"),
                           "detail": e.get("detail")})
        # C7 inspection-queue rule v0 (demo heuristic, NOT yet validated at fleet level): a maintenance ticket
        # needs a sustained trend — the volume-weighted mean clogging index of the last 3 storms with >= 0.5 m3
        # infiltrated falls below 0.5 (tiny storms give noisy recession fits). Implausible events always ticket;
        # deferred events (missing rain/stage data) never ticket.
        trend, tickets, window, raised = [], [], [], False
        for e in events:
            if e["verdict"] == "deferred":
                tickets.append({"t": e["t1"], "kind": "deferred", "label": e["label"], "closed": e["closed"],
                                "detail": e["detail"]})
                continue
            if e["verdict"] == "implausible":
                tickets.append({"t": e["t1"], "kind": "implausible", "label": e["label"], "closed": e["closed"],
                                "rain": e["rain"]})
                continue
            if e["ci"] is None or e["est"] < 0.5:
                continue
            window = (window + [(e["ci"], e["est"])])[-3:]
            med = float(sum(c * w for c, w in window) / sum(w for _, w in window))
            trend.append({"t": e["t1"], "ci": round(med, 2)})
            if len(window) == 3 and med < 0.5 and not raised:
                tickets.append({"t": e["t1"], "kind": "maintenance", "label": e["label"], "closed": e["closed"],
                                "ci": round(med, 2)})
                raised = True
        return {"events": events, "trend": trend, "tickets": tickets}

    normal = score(rain_m)
    # "Unplug the rain gauge": gauge outage 17 Aug 00:00 – 24 Aug 00:00 (rain = missing, not zero)
    rain_out = rain_m.copy()
    rain_out.loc["2025-08-17 00:00":"2025-08-23 23:59"] = np.nan
    outage = score(rain_out)
    k_true = truth["k_per_h"].resample("1D").last() / 0.4
    return {"t0": str(t0), "hours": round((obs.index[-1] - t0).total_seconds() / 3600.0, 1),
            "stage": [round(float(v), 3) for v in st.values], "stage_dt_h": 1 / 6,
            "rain": [round(float(v), 2) for v in rain_h.values], **normal,
            "outage": {**outage, "from_h": hrs(pd.Timestamp("2025-08-17 00:00")), "to_h": hrs(pd.Timestamp("2025-08-24 00:00"))},
            "k_true": [round(float(v), 3) for v in k_true.values]}


HTML = (pathlib.Path(__file__).resolve().parent / "template.html").read_text()


def main() -> None:
    s, p = stations(), pit()
    html = HTML.replace("__STATIONS__", json.dumps(s)).replace("__PIT__", json.dumps(p))
    OUT.write_text(html)
    v = pd.Series([e["verdict"] for e in p["events"]]).value_counts().to_dict()
    vo = pd.Series([e["verdict"] for e in p["outage"]["events"]]).value_counts().to_dict()
    print("outage scenario verdicts:", vo, "tickets:", [(k["kind"], k["label"]) for k in p["outage"]["tickets"]])
    est = sum(e["est"] for e in p["events"] if e["verdict"] != "implausible")
    tru = sum(e["true"] for e in p["events"] if e["verdict"] != "implausible")
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB); stations mapped {s['mapped']}/{s['total']}; "
          f"pit events {len(p['events'])} {v}; infiltrated (non-implausible events) est {est:.1f} vs sim truth {tru:.1f} m3")


if __name__ == "__main__":
    main()
