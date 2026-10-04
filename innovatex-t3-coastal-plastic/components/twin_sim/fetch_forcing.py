"""C1 data fetch: real hourly rain (ERA5 via Open-Meteo archive), archived real NWP rain forecasts
(JMA GSM via Open-Meteo Previous Runs API, issued >= 1 day ahead) and tide (Open-Meteo Marine
sea_level_height_msl, harmonically fitted with UTide on 2022-11-23..2023-12-31 ONLY, so no sea level
from the held-out years 2024-2025 enters the fit; the frozen fit predicts 2019-2025 and is scored
out-of-sample against 2024-2025 model sea level).

Run:  cd innovatex-t3-coastal-plastic/components && python -m twin_sim.fetch_forcing
Raw JSON is cached in innovatex-t3-coastal-plastic/.data/twin_sim/raw/ (gitignored).
Writes twin_sim/data/forcing_jjas.csv.gz (Jun-Sep 2019-2025, hourly UTC) and data/tide_fit.json.
"""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

from ._paths import DATA, RAW
from .sites import get_sites

YEARS = list(range(2019, 2026))
FIT_END = pd.Timestamp("2023-12-31T23:00Z")    # last sea-level hour used by the tide fit (held-out years excluded)
ARCHIVE = ("https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
           "&start_date=2019-06-01&end_date=2025-09-30&hourly=precipitation&models=era5&timezone=UTC")
MARINE = ("https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}"
          "&hourly=sea_level_height_msl&start_date=2022-01-01&end_date=2025-09-30&timezone=UTC")
PREV = ("https://previous-runs-api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&hourly=precipitation_previous_day1&models=jma_gsm&start_date={y}-06-01&end_date={y}-09-30"
        "&timezone=UTC")


PREV2 = ("https://previous-runs-api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
         "&hourly=precipitation_previous_day2&models=jma_gsm&start_date={y}-06-01&end_date={y}-09-30&timezone=UTC")


def _get(url: str, path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "techfest2026-t3-twin/0.1"})
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.loads(r.read())
            if "hourly" not in d:
                raise RuntimeError(str(d)[:200])
            path.write_text(json.dumps(d))
            return d
        except Exception as e:  # network hiccups: back off and retry
            print("retry", attempt, url[:90], e)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"failed: {url}")


def _series(d: dict, key: str) -> pd.Series:
    t = pd.to_datetime(d["hourly"]["time"], utc=True)
    v = np.array([np.nan if x is None else x for x in d["hourly"][key]], float)
    return pd.Series(v, index=t)


def skill(obs: np.ndarray, pred: np.ndarray) -> dict:
    r = obs - pred
    return {"n_hours": int(len(obs)), "rmse_m": round(float(np.sqrt(np.mean(r ** 2))), 4),
            "variance_explained": round(float(1 - r.var() / obs.var()), 4), "bias_m": round(float(r.mean()), 4)}


def fit_tide(sl: pd.Series, lat: float, t_pred: pd.DatetimeIndex, fit_end: pd.Timestamp = FIT_END):
    """Fit on sea level up to fit_end only; predict t_pred; score in-sample and out-of-sample (after fit_end)."""
    import utide
    sl = sl.dropna()
    fit, oos = sl[sl.index <= fit_end], sl[sl.index > fit_end]
    coef = utide.solve(fit.index.tz_convert(None).to_pydatetime(), fit.values, lat=lat, method="ols",
                       conf_int="none", verbose=False, trend=False, nodal=True)
    rec = lambda idx: utide.reconstruct(idx.tz_convert(None).to_pydatetime(), coef, verbose=False).h  # noqa: E731
    pred = rec(t_pred)
    ins = skill(fit.values, rec(fit.index))
    p_oos = rec(oos.index)
    jjas = np.asarray(oos.index.month.isin([6, 7, 8, 9]))
    amp = dict(zip(coef.name, np.round(coef.A, 4)))
    lab = "out-of-sample vs Open-Meteo Marine MODEL sea level (not a tide gauge); fit never saw these hours"
    stats = {
        "fit_period": [str(fit.index[0]), str(fit.index[-1])], "n_hours": int(len(fit)),
        "n_constituents": int(len(coef.name)), "constituents": [str(c) for c in coef.name],
        "variance_explained": ins["variance_explained"], "rmse_m": ins["rmse_m"],
        "in_sample": {**ins, "label": "in-sample fit residual vs Open-Meteo Marine MODEL sea level (fit window)"},
        "out_of_sample_2024_2025": {**skill(oos.values, p_oos), "period": [str(oos.index[0]), str(oos.index[-1])],
                                    "label": lab},
        "out_of_sample_jjas_2024_2025": {**skill(oos.values[jjas], p_oos[jjas]), "label": lab + "; Jun-Sep only"},
        "mean_m": float(coef.mean),
        "amp_m": {k: float(amp[k]) for k in ["M2", "S2", "N2", "K2", "K1", "O1", "P1", "Q1"] if k in amp},
    }
    return pred, stats


def fetch_day2(year: int = 2025):
    """Day-2 forecast (value predicted 48 h before valid time) for the dashboard's causal 48 h horizon."""
    rows = []
    for s in get_sites():
        x = _series(_get(PREV2.format(lat=s.lat, lon=s.lon, y=year), RAW / f"jma2_{s.site_id}_{year}.json"),
                    "precipitation_previous_day2")
        rows.append(pd.DataFrame({"time": x.index.strftime("%Y-%m-%dT%H:%MZ"), "site_id": s.site_id,
                                  "fc2_rain_mm_h": x.values}))
        print(s.site_id, "day2 NaN", int(x.isna().sum()), "of", len(x))
    pd.concat(rows).round(3).to_csv(DATA / f"fc_day2_{year}.csv.gz", index=False, compression="gzip")


def main():
    import sys
    if "--day2-only" in sys.argv:
        fetch_day2()
        return
    RAW.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    frames, fits = [], {}
    for s in get_sites():
        rain = _series(_get(ARCHIVE.format(lat=s.lat, lon=s.lon), RAW / f"era5_{s.site_id}.json"),
                       "precipitation")
        md = _get(MARINE.format(lat=s.lat, lon=s.lon), RAW / f"marine_{s.site_id}.json")
        sl = _series(md, "sea_level_height_msl")
        fc = pd.concat([_series(_get(PREV.format(lat=s.lat, lon=s.lon, y=y), RAW / f"jma_{s.site_id}_{y}.json"),
                                "precipitation_previous_day1") for y in YEARS])
        idx = pd.DatetimeIndex([t for t in rain.index if t.month in (6, 7, 8, 9)])
        tide, st = fit_tide(sl, s.lat, idx)
        st["marine_grid_point"] = [md.get("latitude"), md.get("longitude")]
        fits[s.site_id] = st
        f = pd.DataFrame({"time": idx, "site_id": s.site_id,
                          "rain_mm_h": rain.reindex(idx).values,
                          "fc_rain_mm_h": fc.reindex(idx).values,
                          "tide_m": tide, "tide_openmeteo_m": sl.reindex(idx).values})
        frames.append(f)
        o = st["out_of_sample_2024_2025"]
        print(s.site_id, "NaN rain/fc", int(f.rain_mm_h.isna().sum()), int(f.fc_rain_mm_h.isna().sum()),
              "| fit", st["fit_period"][0][:10], st["fit_period"][1][:10], st["n_constituents"], "const",
              "| in-sample rmse %.3f ve %.4f | OOS rmse %.3f ve %.4f" % (st["rmse_m"], st["variance_explained"],
                                                                     o["rmse_m"], o["variance_explained"]))
    df = pd.concat(frames)
    df["time"] = df["time"].dt.strftime("%Y-%m-%dT%H:%MZ")
    df.round(3).to_csv(DATA / "forcing_jjas.csv.gz", index=False, compression="gzip")
    (DATA / "tide_fit.json").write_text(json.dumps(fits, indent=1))
    fetch_day2()


if __name__ == "__main__":
    main()
