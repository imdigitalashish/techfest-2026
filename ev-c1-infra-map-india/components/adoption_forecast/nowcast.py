"""C9 2026 nowcast: full-calendar-year BEV registrations per state from Jan-Sep actuals, with a backtest.

Methods (all use only data available at the end of September of the target year):
  seasonal: full = YTD / (1 - f), f = share of annual registrations in Oct-Dec over the previous 3 years,
            state profile shrunk toward the national profile (weight w_state = 0.5).
  yoy:      full = annual(y-1) * YTD(y) / YTD(y-1), state ratio shrunk 50:50 toward the national ratio.
  ensemble: mean of seasonal and yoy.
Backtest years: 2023, 2024, 2025 (actuals known). Reports WAPE across states and national error per year.
Usage: .venv/bin/python -W ignore components/adoption_forecast/nowcast.py
Writes eval/results/c9_nowcast_2026.csv and eval/results/c9_summary.json (with the 12-month forecast holdout too).
"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "autoresearch")); sys.path.insert(0, HERE)
import eval_monthly as E  # noqa: E402
import forecaster  # noqa: E402
bev = E.load_monthly("bev")
def P(y, m): return pd.Period(f"{y}-{m:02d}", "M")
def ytd(y, upto=9): return bev.loc[:, P(y, 1):P(y, upto)].sum(1)
def annual(y): return bev.loc[:, P(y, 1):P(y, 12)].sum(1)
def nowcast(y, method, w_state=0.5):
    if method == "seasonal":
        fs = [(annual(t) - ytd(t)) / annual(t).replace(0, np.nan) for t in (y - 3, y - 2, y - 1)]
        fn = np.mean([(annual(t).sum() - ytd(t).sum()) / annual(t).sum() for t in (y - 3, y - 2, y - 1)])
        f = (w_state * pd.concat(fs, axis=1).mean(1).fillna(fn) + (1 - w_state) * fn).clip(0, 0.6)
        return ytd(y) / (1 - f)
    if method == "yoy":
        r_s = (ytd(y) + 1) / (ytd(y - 1) + 1); r_n = ytd(y).sum() / ytd(y - 1).sum()
        return annual(y - 1) * (0.5 * r_s + 0.5 * r_n)
    if method == "ensemble":
        return 0.5 * nowcast(y, "seasonal") + 0.5 * nowcast(y, "yoy")
    raise ValueError(method)
rows = []
for m in ("seasonal", "yoy", "ensemble"):
    for y in (2023, 2024, 2025):
        f, a = nowcast(y, m), annual(y)
        rows.append({"method": m, "year": y, "wape": round(float((f - a).abs().sum() / a.sum()), 4),
                     "national_err": round(float(f.sum() / a.sum() - 1), 4), "nowcast_national": int(f.sum()), "actual_national": int(a.sum())})
bt = pd.DataFrame(rows)
summ = bt.groupby("method").agg(mean_wape=("wape", "mean"), mean_abs_nat_err=("national_err", lambda s: float(np.mean(np.abs(s)))),
                                 max_abs_nat_err=("national_err", lambda s: float(np.max(np.abs(s))))).round(4)
best = summ.mean_wape.idxmin()
now = pd.DataFrame({m: nowcast(2026, m) for m in ("seasonal", "yoy", "ensemble")}).round(0)
now["ytd_jan_sep_2026"] = ytd(2026); now["actual_2025"] = annual(2025)
now = now.sort_values("ensemble", ascending=False)
os.makedirs(f"{R}/eval/results", exist_ok=True)
now.to_csv(f"{R}/eval/results/c9_nowcast_2026.csv", index_label="state")
bt.to_csv(f"{R}/eval/results/c9_nowcast_backtest.csv", index=False)
# 12-month forecast: DEV/HOLDOUT for the main candidates (frozen eval functions)
allv = E.load_monthly("all")
cands = {"naive12": {"method": "naive12"}, "pooled_growth_nat_0.5": {"method": "pooled_growth", "w": 0.0, "phi": 0.5},
         "share_logit_k2_0.5": {"method": "share_logit", "k": 2, "w": 0.5, "phi": 0.5},
         "ensemble_pg+sl": {"method": "ensemble", "members": [{"method": "pooled_growth", "w": 0.0, "phi": 0.5},
                                                              {"method": "share_logit", "k": 2, "w": 0.5, "phi": 0.5}]}}
fc = {k: {"dev_wape": round(float(np.mean([E.score(bev, allv, o, p)[0] for o in E.DEV])), 4),
          "holdout_wape": round(float(np.mean([E.score(bev, allv, o, p)[0] for o in E.HOLD])), 4)} for k, p in cands.items()}
s = {"nowcast_backtest_by_method": summ.to_dict(orient="index"), "nowcast_best_method": best,
     "nowcast_2026_national": {m: int(now[m].sum()) for m in ("seasonal", "yoy", "ensemble")},
     "ytd_jan_sep_2026_national": int(ytd(2026).sum()), "actual_2025_national": int(annual(2025).sum()),
     "forecast_12m_dev_holdout": fc, "forecast_12m_selected": "share_logit_k2_0.5"}
json.dump(s, open(f"{R}/eval/results/c9_summary.json", "w"), indent=1)
print(bt.to_string(index=False)); print(summ.to_string()); print(json.dumps({k: s[k] for k in ("nowcast_best_method", "nowcast_2026_national", "ytd_jan_sep_2026_national", "actual_2025_national", "forecast_12m_dev_holdout")}, indent=1))
print(now.head(8).to_string())
