"""C1 data fetch: real hourly rain (ERA5 via Open-Meteo archive), archived real NWP rain forecasts
(JMA GSM via Open-Meteo Previous Runs API, issued >= 1 day ahead) and tide (Open-Meteo Marine
sea_level_height_msl, harmonically fitted with UTide and predicted for 2019-2025).

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
ARCHIVE = ("https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
           "&start_date=2019-06-01&end_date=2025-09-30&hourly=precipitation&models=era5&timezone=UTC")
MARINE = ("https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}"
          "&hourly=sea_level_height_msl&start_date=2022-01-01&end_date=2025-09-30&timezone=UTC")
PREV = ("https://previous-runs-api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        "&hourly=precipitation_previous_day1&models=jma_gsm&start_date={y}-06-01&end_date={y}-09-30"
        "&timezone=UTC")


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


def fit_tide(sl: pd.Series, lat: float, t_pred: pd.DatetimeIndex):
    import utide
    sl = sl.dropna()
    tt = (sl.index.tz_convert(None)).to_pydatetime()
    coef = utide.solve(tt, sl.values, lat=lat, method="ols", conf_int="none", verbose=False,
                       trend=False, nodal=True)
    pred = utide.reconstruct(t_pred.tz_convert(None).to_pydatetime(), coef, verbose=False).h
    fitted = utide.reconstruct(tt, coef, verbose=False).h
    resid = sl.values - fitted
    amp = dict(zip(coef.name, np.round(coef.A, 4)))
    stats = {
        "fit_period": [str(sl.index[0]), str(sl.index[-1])], "n_hours": int(len(sl)),
        "variance_explained": float(1 - resid.var() / sl.values.var()),
        "rmse_m": float(np.sqrt(np.mean(resid ** 2))), "mean_m": float(coef.mean),
        "amp_m": {k: float(amp[k]) for k in ["M2", "S2", "N2", "K2", "K1", "O1", "P1", "Q1"] if k in amp},
    }
    return pred, stats


def main():
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
        print(s.site_id, "rain NaN", int(f.rain_mm_h.isna().sum()), "fc NaN", int(f.fc_rain_mm_h.isna().sum()),
              "tide var expl %.3f rmse %.3f" % (st["variance_explained"], st["rmse_m"]))
    df = pd.concat(frames)
    df["time"] = df["time"].dt.strftime("%Y-%m-%dT%H:%MZ")
    df.round(3).to_csv(DATA / "forcing_jjas.csv.gz", index=False, compression="gzip")
    (DATA / "tide_fit.json").write_text(json.dumps(fits, indent=1))


if __name__ == "__main__":
    main()
