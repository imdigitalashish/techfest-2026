"""Share of hours with light/calm 10-m wind over Delhi (ERA5 via Open-Meteo, central Delhi point), by season.
ERA5 is a ~25 km grid: it smooths out site-level calms, so these shares are LOWER BOUNDS for what a site vane sees.
Run: python calm_wind.py  → results/calm_wind.json
"""
import json, os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
m = pd.read_parquet(os.path.join(HERE, "..", ".data", "openmeteo", "era5_28.61_77.21.parquet"))
ws = m["wind_speed_10m"] / 3.6
ws = ws[(ws.index >= "2023-10-01") & (ws.index < "2026-10-01")]
out = {"source": "ERA5 via archive-api.open-meteo.com, 28.61N 77.21E, hourly, 2023-10-01..2026-09-30", "n_hours": int(ws.notna().sum())}
for name, months in {"all": list(range(1, 13)), "nov_jan": [11, 12, 1], "oct_feb": [10, 11, 12, 1, 2], "mar_sep": [3, 4, 5, 6, 7, 8, 9]}.items():
    w = ws[ws.index.month.isin(months)].dropna()
    out[name] = {"n": int(len(w)), "share_lt_0_5": round(float((w < 0.5).mean()), 4), "share_lt_1_0": round(float((w < 1.0).mean()), 4),
                 "share_lt_1_5": round(float((w < 1.5).mean()), 4), "median_ms": round(float(w.median()), 2)}
w = ws[ws.index.month.isin([11, 12, 1])].dropna()
night = w[(w.index.hour >= 20) | (w.index.hour < 8)]
day = w[(w.index.hour >= 8) & (w.index.hour < 20)]
out["nov_jan_work_hours_08_20"] = {"share_lt_0_5": round(float((day < 0.5).mean()), 4), "share_lt_1_0": round(float((day < 1.0).mean()), 4)}
out["nov_jan_night_20_08"] = {"share_lt_0_5": round(float((night < 0.5).mean()), 4), "share_lt_1_0": round(float((night < 1.0).mean()), 4)}
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "results", "calm_wind.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
