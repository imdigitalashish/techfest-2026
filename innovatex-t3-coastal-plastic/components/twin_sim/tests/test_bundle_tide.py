"""Tests for the tide refit (no held-out data in the fit), the 48 h causal forecast export, the dashboard window
in bundle_part.json, and doc/result sync. Run: cd innovatex-t3-coastal-plastic/components && python -m pytest twin_sim/tests -q"""
import json
from collections import Counter

import numpy as np
import pytest

from twin_sim import report
from twin_sim import risk_forecaster as RF
from twin_sim._paths import DATA, RESULTS, C
from twin_sim.sites import SITE_IDS


def test_tide_fit_excludes_heldout_years():
    fit = json.loads((DATA / "tide_fit.json").read_text())
    for sid in SITE_IDS:
        f = fit[sid]
        assert f["fit_period"][1] < "2024-01-01"
        oos = f["out_of_sample_2024_2025"]
        assert oos["period"][0] >= "2024-01-01" and oos["n_hours"] > 10_000
        assert oos["rmse_m"] < 0.2 and oos["variance_explained"] > 0.95
        assert {"M2", "S2", "K1", "O1", "P1", "K2"} <= set(f["constituents"])


def test_48h_export_contract_and_day2_use():
    fc = RF.season_forecast(2025)
    fill = np.full(4, 0.3)
    zero = np.zeros_like(fc["_state"]["fcr"])
    f24 = RF.horizon_forecasts(fc, 30, fill, SITE_IDS, 24)
    f48 = RF.horizon_forecasts(fc, 30, fill, SITE_IDS, 48, zero)
    for f in f24 + f48:
        C.SiteForecast.model_validate(f.model_dump())
    assert {f.horizon_h for f in f48} == {48}
    for a, b in zip(f24, f48):
        assert b.drivers["rain_mm_next_48h_fc"] == pytest.approx(a.drivers["rain_mm_next_24h_fc"], abs=0.11)
        assert b.expected_arrival_kg >= a.expected_arrival_kg - 1e-6


@pytest.fixture(scope="module")
def bundle():
    p = RESULTS / "bundle_part.json"
    if not p.exists():
        pytest.skip("run python -m twin_sim.run first")
    return json.loads(p.read_text())


def test_bundle_window_contents(bundle):
    w = bundle["metrics"]["twin_sim.window"]
    ws, we = w["start_utc"].replace("Z", "+00:00"), w["end_utc"].replace("Z", "+00:00")
    in_w = lambda ts: ws[:13] <= ts[:13] <= we[:13]  # noqa: E731
    days = sorted({f["issued_at"][:10] for f in bundle["forecasts"] if f["horizon_h"] == 48})
    assert len(days) == int(w["days"]) == 7 and all(in_w(d + "T00") for d in days)
    assert Counter(f["horizon_h"] for f in bundle["forecasts"])[48] == 7 * len(SITE_IDS)
    for d in days:
        pol = {p["policy_id"] for p in bundle["plans"] if p["issued_at"][:10] == d}
        assert pol == {"P0", "P1", "P2"}
        assert all(p["issued_at"][11:16] == "00:00" for p in bundle["plans"] if p["issued_at"][:10] == d)
    for sid in SITE_IDS:
        n = sum(1 for t in bundle["telemetry"] if t["site_id"] == sid and in_w(t["t"]))
        assert n == 7 * 24
    sensed = {(t["site_id"], t["t"][:13]): t["fill"]["fill_fraction"] for t in bundle["telemetry"]}
    for f in bundle["forecasts"]:
        if f["horizon_h"] == 24 and in_w(f["issued_at"]):
            assert sensed[(f["site_id"], f["issued_at"][:13])] == pytest.approx(f["drivers"]["sensed_fill"], abs=1e-3)


def test_docs_in_sync_with_results():
    if not (RESULTS / "analysis.json").exists():
        pytest.skip("run python -m twin_sim.analysis first")
    assert report.apply(check=True) == [], "run python -m twin_sim.report"
