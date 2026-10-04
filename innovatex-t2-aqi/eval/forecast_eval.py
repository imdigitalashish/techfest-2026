"""Walking-skeleton forecast eval: next-day (D+1) daily-mean PM2.5 / PM10 at Delhi CPCB/DPCC monitors.

REAL data only: OpenAQ public S3 archive (CPCB/DPCC hourly) + ERA5 via Open-Meteo (central Delhi point).
Forecast issued at the end of day D (IST) using data up to D. Time-ordered split:
  train 2024-10-01..2025-09-30 · test 2025-10-01..2026-09-30 (plus a winter subset Oct–Feb).
Models: persistence · station×month climatology · HistGradientBoosting (no future met) ·
        HistGradientBoosting + ERA5 for D+1 ("perfect-prog" upper bound, i.e. as if the met forecast were perfect).
CAMS (Open-Meteo, as served) is reported for reference only: its forecast lead time is not controlled here.

Run (from this folder):  python forecast_eval.py   → prints a table and writes results/forecast_baseline.json
"""
import json, os
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", ".data")
STATIONS = {235: "Anand Vihar (DPCC)", 17: "R K Puram (DPCC)", 5613: "ITO (CPCB)", 6929: "Major Dhyan Chand Natl Stadium (DPCC)"}
TRAIN = ("2024-10-01", "2025-09-30")
TEST = ("2025-10-01", "2026-09-30")
CAP = {"pm25": 1000.0, "pm10": 1500.0}  # drop physically implausible hourly values (sensor faults)
MIN_HOURS = 18
# Severe-day thresholds on the 24-h mean, following the CPCB NAQI breakpoints as commonly published
# (PM2.5 > 250, PM10 > 430 µg/m³; 'very poor' from 120 / 350) — UNVERIFIED against the CPCB document in this session.
SEVERE = {"pm25": 250.0, "pm10": 430.0}
VERY_POOR = {"pm25": 120.0, "pm10": 350.0}


def daily_station(loc):
    h = pd.read_parquet(os.path.join(DATA, "openaq", f"station_{loc}.parquet"))
    out = {}
    for p in ("pm25", "pm10"):
        if p not in h:
            continue
        s = h[p].where((h[p] > 0) & (h[p] < CAP[p]))
        g = s.groupby(s.index.floor("D"))
        out[p] = g.mean().where(g.count() >= MIN_HOURS)
        eve = s[s.index.hour >= 18]
        out[p + "_eve"] = eve.groupby(eve.index.floor("D")).mean()
    d = pd.DataFrame(out)
    d.index.name = "date"
    return d


def met_daily():
    m = pd.read_parquet(os.path.join(DATA, "openmeteo", "era5_28.61_77.21.parquet"))
    day = m.index.floor("D")
    d = m.groupby(day).agg({"temperature_2m": "mean", "relative_humidity_2m": "mean", "wind_speed_10m": "mean",
                            "boundary_layer_height": "mean", "precipitation": "sum", "surface_pressure": "mean"})
    blh_min = m["boundary_layer_height"].groupby(day).min().rename("blh_min")
    vent = (m["boundary_layer_height"] * m["wind_speed_10m"] / 3.6).groupby(day).mean().rename("vent_coef")
    return pd.concat([d, blh_min, vent], axis=1)


def cams_daily():
    c = pd.read_parquet(os.path.join(DATA, "openmeteo", "cams_28.61_77.21.parquet"))
    return c[["pm2_5", "pm10"]].groupby(c.index.floor("D")).mean().rename(columns={"pm2_5": "cams_pm25", "pm10": "cams_pm10"})


def build(target):
    met, cams = met_daily(), cams_daily()
    rows = []
    for loc in STATIONS:
        d = daily_station(loc)
        if target not in d:
            continue
        y = d[target]
        f = pd.DataFrame(index=d.index)
        f["y_next"] = y.shift(-1, freq="D").reindex(d.index)
        for k in (0, 1, 2, 6):
            f[f"lag{k}"] = y.shift(k, freq="D").reindex(d.index)
        f["eve0"] = d[target + "_eve"]
        f["trend"] = f["lag0"] - f["lag1"]
        doy = d.index.dayofyear
        f["doy_s"], f["doy_c"] = np.sin(2 * np.pi * doy / 365.25), np.cos(2 * np.pi * doy / 365.25)
        nxt = d.index + pd.Timedelta(days=1)
        f["dow_next"], f["month_next"] = nxt.dayofweek, nxt.month
        m0 = met.reindex(d.index)
        m1 = met.reindex(nxt)
        for c in met.columns:
            f[f"met0_{c}"] = m0[c].values
            f[f"met1_{c}"] = m1[c].values  # D+1 reanalysis: only used in the 'perfect-prog' variant
        f["cams_next"] = cams[f"cams_{target}"].reindex(nxt).values
        f["station"] = loc
        rows.append(f)
    return pd.concat(rows).dropna(subset=["y_next", "lag0"])


def metrics(y, yhat, target):
    y, yhat = np.asarray(y, float), np.asarray(yhat, float)
    m = {"n": int(len(y)), "MAE": float(np.mean(np.abs(y - yhat))), "RMSE": float(np.sqrt(np.mean((y - yhat) ** 2))),
         "bias": float(np.mean(yhat - y)), "r": float(np.corrcoef(y, yhat)[0, 1]) if len(y) > 2 else float("nan")}
    for name, thr in (("severe", SEVERE[target]), ("very_poor_plus", VERY_POOR[target])):
        obs, fc = y > thr, yhat > thr
        hits, misses, fa = int((obs & fc).sum()), int((obs & ~fc).sum()), int((~obs & fc).sum())
        m[name] = {"thr": thr, "events": int(obs.sum()), "predicted": int(fc.sum()),
                   "POD": hits / (hits + misses) if hits + misses else None,
                   "FAR": fa / (hits + fa) if hits + fa else None,  # undefined when nothing is predicted
                   "CSI": hits / (hits + misses + fa) if hits + misses + fa else None}
    return m


def run(target):
    df = build(target)
    tr = df[(df.index >= TRAIN[0]) & (df.index <= TRAIN[1])]
    te = df[(df.index >= TEST[0]) & (df.index <= TEST[1])]
    base = ["lag0", "lag1", "lag2", "lag6", "eve0", "trend", "doy_s", "doy_c", "dow_next", "month_next", "station"] + \
           [c for c in df.columns if c.startswith("met0_")]
    pp = base + [c for c in df.columns if c.startswith("met1_")]
    preds = {"persistence": te["lag0"].values}
    clim = tr.groupby(["station", "month_next"])["y_next"].mean()
    preds["climatology_station_month"] = np.array([clim.get((s, mo), tr["y_next"].mean()) for s, mo in zip(te["station"], te["month_next"])])
    cats = {s: i for i, s in enumerate(STATIONS)}
    for name, cols in (("gbm_no_future_met", base), ("gbm_perfect_prog_met", pp)):
        mdl = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=20,
                                            l2_regularization=1.0, categorical_features=[cols.index("station")], random_state=0)
        Xtr, Xte = tr[cols].copy(), te[cols].copy()
        Xtr["station"], Xte["station"] = Xtr["station"].map(cats), Xte["station"].map(cats)
        mdl.fit(Xtr, tr["y_next"])
        preds[name] = mdl.predict(Xte)
    winter = te.index.month.isin([10, 11, 12, 1, 2])
    out = {"target": target, "train": TRAIN, "test": TEST, "n_train": int(len(tr)), "n_test": int(len(te)),
           "n_test_winter": int(winter.sum()), "models": {}}
    for k, v in preds.items():
        out["models"][k] = {"all": metrics(te["y_next"], v, target), "winter_oct_feb": metrics(te["y_next"][winter], v[winter], target)}
    ok = te["cams_next"].notna().values
    out["models"]["cams_as_served_reference"] = {"all": metrics(te["y_next"][ok], te["cams_next"][ok], target),
                                                  "winter_oct_feb": metrics(te["y_next"][ok & winter], te["cams_next"][ok & winter], target),
                                                  "note": "Open-Meteo CAMS at one central-Delhi point; lead time not controlled; reference only"}
    pm = out["models"]["persistence"]["all"]["MAE"]
    for k in out["models"]:
        out["models"][k]["skill_vs_persistence_MAE"] = 1 - out["models"][k]["all"]["MAE"] / pm
    return out


def f2(x):
    return "  NA" if x is None else f"{x:.2f}"


def main():
    res = {"stations": STATIONS, "data": {"openaq": "s3://openaq-data-archive (public, unsigned)",
                                          "era5": "archive-api.open-meteo.com", "cams": "air-quality-api.open-meteo.com"},
           "results": [run("pm25"), run("pm10")]}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "forecast_baseline.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=str)
    for r in res["results"]:
        print(f"\n== {r['target']} D+1 daily mean · n_train={r['n_train']} n_test={r['n_test']} (winter {r['n_test_winter']})")
        print(f"{'model':28s} {'MAE':>6s} {'RMSE':>6s} {'r':>5s} {'skill':>6s} | severe POD FAR CSI | winter MAE")
        for k, v in r["models"].items():
            a, w = v["all"], v["winter_oct_feb"]
            s = a["severe"]
            print(f"{k:28s} {a['MAE']:6.1f} {a['RMSE']:6.1f} {a['r']:5.2f} {v['skill_vs_persistence_MAE']:6.2f} | "
                  f"{f2(s['POD'])} {f2(s['FAR'])} {f2(s['CSI'])} (ev={s['events']}) | {w['MAE']:6.1f}")


if __name__ == "__main__":
    main()
