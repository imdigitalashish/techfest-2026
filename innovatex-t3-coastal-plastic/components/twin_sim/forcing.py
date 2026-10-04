"""C1 forcing: load the processed real-data forcing (see fetch_forcing.py) and emit ForcingSeries."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from ._paths import DATA, C
from .sites import SITE_IDS

RAIN_SRC = ("https://archive-api.open-meteo.com/v1/archive?...&hourly=precipitation&models=era5 "
            "(ERA5 reanalysis, Copernicus/ECMWF via Open-Meteo)")
TIDE_SRC = ("https://marine-api.open-meteo.com/v1/marine?...&hourly=sea_level_height_msl (2022-2025) "
            "-> UTide harmonic fit (data/tide_fit.json) -> prediction")
FC_SRC = ("https://previous-runs-api.open-meteo.com/v1/forecast?...&hourly=precipitation_previous_day1"
          "&models=jma_gsm (archived JMA GSM run issued one day earlier)")
ACCESSED = datetime(2026, 10, 4, tzinfo=timezone.utc)


@dataclass
class Season:
    year: int
    t: pd.DatetimeIndex          # hourly UTC, Jun 1 00:00 .. Sep 30 23:00
    rain: np.ndarray             # (T, S) mm/h  observed (reanalysis)
    fc_rain: np.ndarray          # (T, S) mm/h  forecast issued >= 1 day earlier
    tide: np.ndarray             # (T, S) m MSL harmonic prediction
    site_ids: list


_CACHE: dict = {}


def load_table() -> pd.DataFrame:
    if "df" not in _CACHE:
        df = pd.read_csv(DATA / "forcing_jjas.csv.gz")
        df["time"] = pd.to_datetime(df["time"], utc=True)
        _CACHE["df"] = df
    return _CACHE["df"]


def season(year: int) -> Season:
    key = ("season", year)
    if key in _CACHE:
        return _CACHE[key]
    df = load_table()
    d = df[df.time.dt.year == year]
    piv = {c: d.pivot(index="time", columns="site_id", values=c)[SITE_IDS] for c in
           ("rain_mm_h", "fc_rain_mm_h", "tide_m")}
    t = piv["rain_mm_h"].index
    rain = piv["rain_mm_h"].fillna(0.0).to_numpy()
    fc = piv["fc_rain_mm_h"]
    # forecast gaps (if any) are filled with 0 = "no forecast rain"; counted in data/README
    s = Season(year, t, rain, fc.fillna(0.0).to_numpy(), piv["tide_m"].interpolate().to_numpy(), list(SITE_IDS))
    _CACHE[key] = s
    return s


def forcing_series(year: int, site_idx: int) -> "C.ForcingSeries":
    s = season(year)
    return C.ForcingSeries(
        site_id=s.site_ids[site_idx], t=list(s.t.to_pydatetime()),
        rain_mm_h=np.round(s.rain[:, site_idx], 2).tolist(), tide_m=np.round(s.tide[:, site_idx], 3).tolist(),
        tide_datum="MSL",
        rain_provenance=C.Provenance(kind="reanalysis", source=RAIN_SRC, retrieved_at=ACCESSED),
        tide_provenance=C.Provenance(kind="harmonic_prediction", source=TIDE_SRC, retrieved_at=ACCESSED,
                                     notes="constituents fitted to Open-Meteo Marine model sea level (not a tide gauge)"))
