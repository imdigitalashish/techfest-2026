"""Executable checks for C5 recharge-verifier abstention and verdicts (final-deck review D5, C2).

Run: innovatex-t1-groundwater/.venv/bin/python -m pytest -q innovatex-t1-groundwater/components/recharge_verifier/test_verifier.py
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import verifier  # noqa: E402

REG = {"structure_id": "TEST", "pit_area_m2": 2.25, "catchment_m2": 250.0, "runoff_coeff": 0.75,
       "overflow_stage_m": 1.5, "k_as_built_per_h": 0.4}
IDX = pd.date_range("2025-07-01 00:00", periods=12 * 60, freq="1min")


def _stage(rise_at_min: int = 120, peak: float = 0.5, k: float = 0.4) -> pd.Series:
    """30-min linear rise to `peak`, then exponential recession with constant k (1/h)."""
    h = np.zeros(len(IDX))
    for i in range(len(IDX)):
        if rise_at_min <= i < rise_at_min + 30:
            h[i] = peak * (i - rise_at_min + 1) / 30
        elif i >= rise_at_min + 30:
            h[i] = peak * np.exp(-k * (i - rise_at_min - 30) / 60.0)
    return pd.Series(h, index=IDX)


def _rain(mm_total: float = 10.0, start: int = 115, minutes: int = 30) -> pd.Series:
    r = np.zeros(len(IDX))
    r[start:start + minutes] = mm_total / minutes
    return pd.Series(r, index=IDX)


def _main_event(events: list[dict]) -> dict:
    real = [e for e in events if e["verdict"] != "no_inflow"]
    assert real, f"no event detected: {events}"
    return max(real, key=lambda e: e["max_rise_m"])


def test_rain_explains_rise_is_not_implausible():
    e = _main_event(verifier.verify(_stage(), _rain(), REG))
    assert e["verdict"] in {"verified", "clogged"}
    assert e["detail"] is None


def test_observed_zero_rain_is_implausible():
    e = _main_event(verifier.verify(_stage(), pd.Series(0.0, index=IDX), REG))
    assert e["verdict"] == "implausible"


def test_absent_rain_series_defers():
    e = _main_event(verifier.verify(_stage(), pd.Series(dtype=float), REG))
    assert e["verdict"] == "deferred"
    assert e["detail"] == "insufficient rain data"


def test_all_nan_rain_defers():
    e = _main_event(verifier.verify(_stage(), pd.Series(np.nan, index=IDX), REG))
    assert e["verdict"] == "deferred"


def test_partial_rain_outage_defers():
    r = _rain()
    r.iloc[60:300] = np.nan          # gauge outage covering the storm
    e = _main_event(verifier.verify(_stage(), r, REG))
    assert e["verdict"] == "deferred"


def test_stage_gap_defers():
    s = _stage()
    s = s.drop(s.index[160:260])     # 100-min hole in the stage record during the recession
    e = _main_event(verifier.verify(s, _rain(), REG))
    assert e["verdict"] == "deferred"
    assert e["detail"] == "stage gap > 60 min"


def test_small_bucket_is_below_event_threshold():
    """20 L into a 2.25 m2 pit = 8.9 mm rise < H_ON (2 cm): not an event at all (disclosed limitation)."""
    s = pd.Series(0.0, index=IDX)
    s.iloc[300:] = 0.020 / 2.25
    events = verifier.verify(s, pd.Series(0.0, index=IDX), REG)
    assert [e for e in events if e["verdict"] != "no_inflow"] == []
