"""Walk-forward (expanding-window) eval of next-day daily-mean PM2.5/PM10 at 4 Delhi CPCB/DPCC monitors.

Why: the OpenAQ archive for these stations starts Feb 2025, so a fixed 'train 2024-25 / test 2025-26' split
has no winter in training (see results/forecast_baseline.json, where tree models collapse in winter). Here,
for each test month M (Nov 2025 .. Sep 2026), models train on all days before M (strictly time-ordered; no leakage:
features use data up to day D, the target is day D+1, and training targets end before M starts).
GBM variants predict log(y[D+1]/y[D]) (a scale-free change from persistence), so they work in unseen regimes.

Run: OMP_NUM_THREADS=1 python forecast_walkforward.py  → results/forecast_walkforward.json + printed table
"""
import json, os
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from forecast_eval import build, metrics, STATIONS, HERE

TEST_MONTHS = pd.period_range("2025-11", "2026-09", freq="M")
WINTER = [11, 12, 1, 2]


def fit_predict(tr, te, cols, logratio):
    cats = {s: i for i, s in enumerate(STATIONS)}
    Xtr, Xte = tr[cols].copy(), te[cols].copy()
    Xtr["station"], Xte["station"] = Xtr["station"].map(cats), Xte["station"].map(cats)
    for X in (Xtr, Xte):
        for c in ("lag0", "lag1", "lag2", "lag6", "eve0"):
            X[c] = np.log1p(X[c])
    y = np.log1p(tr["y_next"]) - np.log1p(tr["lag0"]) if logratio else tr["y_next"]
    mdl = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=20,
                                        l2_regularization=1.0, categorical_features=[cols.index("station")], random_state=0)
    mdl.fit(Xtr, y)
    p = mdl.predict(Xte)
    return np.expm1(np.log1p(te["lag0"].values) + p) if logratio else p


def run(target):
    df = build(target)
    base = ["lag0", "lag1", "lag2", "lag6", "eve0", "trend", "doy_s", "doy_c", "dow_next", "month_next", "station"] + \
           [c for c in df.columns if c.startswith("met0_")]
    pp = base + [c for c in df.columns if c.startswith("met1_")]
    preds = {k: [] for k in ("persistence", "gbm_level_no_future_met", "gbm_logratio_no_future_met", "gbm_logratio_perfect_prog_met")}
    ys, idx, cams = [], [], []
    for M in TEST_MONTHS:
        start = M.start_time
        # the training target is day D+1, so require D+1 < start  ⇔  D < start - 1 day
        tr = df[df.index < start - pd.Timedelta(days=1)]
        te = df[(df.index >= start - pd.Timedelta(days=1)) & (df.index < M.end_time.normalize())]
        if len(te) == 0:
            continue
        preds["persistence"].append(te["lag0"].values)
        preds["gbm_level_no_future_met"].append(fit_predict(tr, te, base, False))
        preds["gbm_logratio_no_future_met"].append(fit_predict(tr, te, base, True))
        preds["gbm_logratio_perfect_prog_met"].append(fit_predict(tr, te, pp, True))
        ys.append(te["y_next"].values); idx.append(te.index); cams.append(te["cams_next"].values)
    y = np.concatenate(ys); ix = pd.DatetimeIndex(np.concatenate([i.values for i in idx]))
    winter = ((ix + pd.Timedelta(days=1)).month.isin(WINTER))
    out = {"target": target, "scheme": "monthly expanding window, Nov 2025–Sep 2026", "n_test": int(len(y)),
           "n_test_winter": int(winter.sum()), "models": {}}
    for k, v in preds.items():
        v = np.concatenate(v)
        out["models"][k] = {"all": metrics(y, v, target), "winter_nov_feb": metrics(y[winter], v[winter], target)}
    c = np.concatenate(cams); ok = ~np.isnan(c)
    out["models"]["cams_as_served_reference"] = {"all": metrics(y[ok], c[ok], target), "winter_nov_feb": metrics(y[ok & winter], c[ok & winter], target),
                                                  "note": "one central-Delhi grid point; lead time not controlled; reference only"}
    pm = out["models"]["persistence"]["all"]["MAE"]; pw = out["models"]["persistence"]["winter_nov_feb"]["MAE"]
    for k, v in out["models"].items():
        v["skill_vs_persistence_MAE"] = 1 - v["all"]["MAE"] / pm
        v["winter_skill_vs_persistence_MAE"] = 1 - v["winter_nov_feb"]["MAE"] / pw
    return out


def main():
    res = {"stations": STATIONS, "results": [run("pm25"), run("pm10")]}
    with open(os.path.join(HERE, "results", "forecast_walkforward.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=str)
    for r in res["results"]:
        print(f"\n== {r['target']} D+1 daily mean · walk-forward · n_test={r['n_test']} (winter {r['n_test_winter']})")
        print(f"{'model':32s} {'MAE':>6s} {'RMSE':>6s} {'r':>5s} {'skill':>6s} | wMAE  wSkill | severe POD FAR CSI")
        for k, v in r["models"].items():
            a, w, s = v["all"], v["winter_nov_feb"], v["all"]["severe"]
            print(f"{k:32s} {a['MAE']:6.1f} {a['RMSE']:6.1f} {a['r']:5.2f} {v['skill_vs_persistence_MAE']:6.2f} | "
                  f"{w['MAE']:5.1f} {v['winter_skill_vs_persistence_MAE']:6.2f} | {s['POD']:.2f} {s['FAR']:.2f} {s['CSI']:.2f} (ev={s['events']})")


if __name__ == "__main__":
    main()
