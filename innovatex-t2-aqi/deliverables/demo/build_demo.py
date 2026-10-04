"""Build the offline DustLedger demo: deliverables/demo/dustledger-demo.html (self-contained, no internet needed).

Provenance (also shown on screen):
  REAL       hourly PM10 at 4 CPCB/DPCC monitors (OpenAQ public archive) and ERA5 wind/rain (Open-Meteo), central Delhi.
  SIMULATED  six construction sites, their emissions, plumes and sensor faults — the same physics and fault model as the
             frozen evaluator v2.1 ('medium' scenario), but each site gets its own emission level (demo-only code below;
             the evaluator itself is untouched). Attribution = methods.ring_selfcal (the current candidate).
  DEMO RULE  misting turns on in an hour when the site estimate is > 50 µg/m³, the wind isn't calm and it isn't raining.
             The effect of misting on dust is NOT modelled; the demo only counts misting-on hours vs a timer schedule.
Also computes a ranking check over the held-out period (Jan–Sep 2026) for 20 simulated sites → demo/ranking_check.json.
Run (from innovatex-t2-aqi/): OMP_NUM_THREADS=1 nice -n 10 python3 deliverables/demo/build_demo.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "components" / "attribution" / "autoresearch"))
sys.path.insert(0, str(ROOT / "components" / "attribution"))
import eval_v2 as ev  # noqa: E402  (frozen evaluator: load(), plume(), SCENARIOS)
import methods  # noqa: E402

HERE = Path(__file__).resolve().parent
NODES = ["N", "E", "S", "W"]
WEEK = ("2025-11-17", "2025-11-24")
THRESH = 50.0


def sim_site(df, rng, sc, scale):
    """eval_v2.simulate with an emission multiplier `scale` (demo only). Returns obs, true site contribution (max node), geom."""
    n, idx = len(df), df.index
    hx, hy = sc["half"]
    geom = {"N": (0.0, hy), "E": (hx, 0.0), "S": (0.0, -hy), "W": (-hx, 0.0)}
    sources = [(x, y) for x in (-hx / 2, 0, hx / 2) for y in (-hy / 2, 0, hy / 2)]
    days = idx.normalize(); uday = days.unique()
    work_day = (idx.hour >= 8) & (idx.hour < 18) & (idx.dayofweek < 6)
    nightw = pd.Series(rng.random(len(uday)) < sc["night_work"], index=uday).reindex(days).values
    work = work_day | (nightw & (idx.hour < 5))
    unc = rng.random(len(uday)) < 0.3
    qd = pd.Series(np.where(unc, rng.lognormal(np.log(0.6), 0.4, len(uday)), rng.lognormal(np.log(0.1), 0.4, len(uday))), index=uday)
    Q = np.where(work, qd.reindex(days).values * rng.lognormal(0, 0.5, n), 0.0) * 1e6 * scale
    ws = df["ws"].values
    decor = np.where(ws < 1.0, sc["decor"] * 2, sc["decor"])
    wd_true = (df["wind_direction_10m"].values + rng.normal(0, 1, n) * decor) % 360
    u = np.maximum(ws, 0.5)
    to = np.deg2rad((wd_true + 180) % 360); ue, un = np.sin(to), np.cos(to)
    site = {k: ev.plume(Q, sources, geom[k], ue, un, u) for k in NODES}
    pool = np.where(ws < 0.5, Q / (0.5 * 2 * max(hx, hy) * 10.0) * 0.3, 0.0)
    S = np.stack([site[k] + pool for k in NODES], 1)
    truth = S.max(1)
    ang = rng.uniform(0, 2 * np.pi); dist = rng.uniform(150, 250)
    nb_on = pd.Series(rng.random(len(uday)) < sc["neighbour"], index=uday).reindex(days).values & work_day
    Qn = np.where(nb_on, rng.lognormal(np.log(0.6), 0.4, n), 0.0) * 1e6
    road = NODES[rng.integers(4)]
    traffic = np.where(np.isin(idx.hour, [8, 9, 10, 17, 18, 19, 20]), 1.0, np.where((idx.hour >= 23) | (idx.hour < 6), 0.3, 0.6))
    rh = np.clip(df["relative_humidity_2m"].values, 0, 98)
    tdays = (idx - idx[0]).total_seconds().values / 86400
    obs = pd.DataFrame(index=idx)
    for j, k in enumerate(NODES):
        amb = df["bg"].values * (1 + rng.normal(0, 0.03, n)) + rng.uniform(*sc["gradient"]) + ev.plume(Qn, [(dist * np.sin(ang), dist * np.cos(ang))], geom[k], ue, un, u)
        if k == road:
            amb = amb + 20.0 * traffic
        g = rng.uniform(0.95, 1.05) * np.clip(1 + rng.normal(0, 0.10) * tdays / 365, 0.5, 1.5)
        for _ in range(sc["fouling"]):
            t0 = rng.uniform(0, tdays[-1]); g = g * np.where(tdays >= t0, 1 - rng.uniform(*sc["foul_drop"]), 1.0)
        hum = 1 + 0.05 * rng.uniform(0.8, 1.2) * rh / (100 - rh)
        meas = g * amb * hum + g * rng.uniform(*sc["dust_gain"]) * S[:, j] * hum + rng.uniform(-sc["offset"], sc["offset"]) \
            + rng.normal(0, 1, n) * (0.05 * (amb + S[:, j]) + 2)
        obs[f"raw_{k}"] = np.clip(meas, 0, rng.choice(sc["cap"]))
    obs["rh"] = rh
    obs["ws_meas"] = ws * (1 + rng.normal(0, 0.1, n))
    obs["wd_meas"] = (wd_true + sc["vane_bias"] + rng.normal(0, 10, n)) % 360
    return obs, truth, geom, work


def main():
    met = pd.read_parquet(ROOT / ".data" / "openmeteo" / "era5_28.61_77.21.parquet")
    df = ev.load()
    rain = met["precipitation"].reindex(df.index).fillna(0).values
    sc = ev.SCENARIOS["medium"]
    sites = [("Site A", 2.0, 101), ("Site B", 1.0, 102), ("Site C", 0.5, 103), ("Site D", 0.25, 104), ("Site E", 1.2, 105), ("Site F", 0.1, 106)]
    wk = (df.index >= WEEK[0]) & (df.index < WEEK[1])
    out_sites = []
    for name, scale, seed in sites:
        obs, truth, geom, work = sim_site(df, np.random.default_rng(seed), sc, scale)
        est, ab = methods.ring_selfcal(obs, geom)
        est = np.asarray(est, float)
        mist = (~ab) & (est > THRESH) & (rain <= 0.0)
        w = wk
        covered = w & ~ab
        out_sites.append({
            "name": name, "est_mean_work": round(float(np.mean(est[covered & work])), 1) if (covered & work).any() else None,
            "true_mean_work": round(float(np.mean(truth[w & work])), 1), "hours_gt50_est": int(((est > THRESH) & covered).sum()),
            "inconclusive_pct": round(100 * float(ab[w].mean()), 1), "mist_hours": int(mist[w].sum()),
            "timer_hours": int((w & (df.index.hour >= 8) & (df.index.hour < 18) & (df.index.dayofweek < 6)).sum()),
            "t": [str(x)[5:16] for x in df.index[w]], "est": [None if (a or not np.isfinite(e)) else round(float(e), 1) for e, a in zip(est[w], ab[w])],
            "truth": [round(float(x), 1) for x in truth[w]], "mist": [int(x) for x in mist[w]],
        })
    rank_est = sorted(out_sites, key=lambda s: -(s["est_mean_work"] or 0))
    rank_true = sorted(out_sites, key=lambda s: -s["true_mean_work"])
    for i, s in enumerate(rank_est):
        s["rank_est"] = i + 1
    for i, s in enumerate(rank_true):
        s["rank_true"] = i + 1
    bg_week = {"t": [str(x)[5:16] for x in df.index[wk]], "pm10_6929": [round(float(x), 1) for x in df["bg"].values[wk]],
               "wind_ms": [round(float(x), 2) for x in df["ws"].values[wk]]}
    stations = {235: "Anand Vihar", 17: "R K Puram", 5613: "ITO", 6929: "Major Dhyan Chand Stadium"}
    daily = {}
    for sid, nm in stations.items():
        h = pd.read_parquet(ROOT / ".data" / "openaq" / f"station_{sid}.parquet")["pm10"]
        h = h.where((h > 0) & (h < 1500))
        d = h[(h.index >= "2025-10-01") & (h.index < "2026-03-01")].groupby(h.index[(h.index >= "2025-10-01") & (h.index < "2026-03-01")].floor("D")).mean()
        daily[nm] = {"t": [str(x)[:10] for x in d.index], "v": [None if not np.isfinite(x) else round(float(x), 1) for x in d.values]}
    # ranking check on the held-out period (Jan–Sep 2026): 20 simulated sites, emission scales log-uniform 0.1–3
    rng = np.random.default_rng(777)
    scales = np.exp(rng.uniform(np.log(0.1), np.log(3.0), 20))
    ho = (df.index >= "2026-01-01") & (df.index < "2026-10-01")
    est_m, true_m = [], []
    for i, scale in enumerate(scales):
        obs, truth, geom, work = sim_site(df, np.random.default_rng(5000 + i), sc, float(scale))
        est, ab = methods.ring_selfcal(obs, geom)
        cov = ho & work & ~np.asarray(ab, bool) & np.isfinite(np.asarray(est, float))
        est_m.append(float(np.mean(np.asarray(est, float)[cov])))
        true_m.append(float(np.mean(truth[ho & work])))
    est_m, true_m = np.array(est_m), np.array(true_m)
    rho = float(pd.Series(est_m).rank().corr(pd.Series(true_m).rank()))
    top5_true = set(np.argsort(-true_m)[:5]); top5_est = set(np.argsort(-est_m)[:5])
    check = {"what": "Rank 20 simulated sites (emission scale log-uniform 0.1–3, 'medium' scenario) by mean estimated increment in work hours, Jan–Sep 2026 (held out)",
             "spearman_rho": round(rho, 3), "top5_overlap": len(top5_true & top5_est), "provenance": "SIMULATED sites on REAL background + wind"}
    (HERE / "ranking_check.json").write_text(json.dumps(check, indent=1))
    data = {"sites": out_sites, "bg_week": bg_week, "daily": daily, "ranking_check": check, "thresh": THRESH}
    html = (HERE / "template.html").read_text().replace("/*DATA*/null", json.dumps(data))
    (HERE / "dustledger-demo.html").write_text(html)
    print(json.dumps({"ranking_check": check, "week": [(s["name"], s["rank_est"], s["rank_true"], s["est_mean_work"], s["true_mean_work"], s["inconclusive_pct"], s["mist_hours"], s["timer_hours"]) for s in out_sites]}))


if __name__ == "__main__":
    main()
