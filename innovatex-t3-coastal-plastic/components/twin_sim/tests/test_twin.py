"""Contract tests + mass-balance tests for twin_sim.
Run: cd innovatex-t3-coastal-plastic/components && python -m pytest twin_sim/tests -q"""
import json

import numpy as np
import pytest

from twin_sim import dispatch as DP
from twin_sim import forcing as FO
from twin_sim import interceptor as IC
from twin_sim import params as PR
from twin_sim import risk_forecaster as RF
from twin_sim import sim
from twin_sim._paths import RESULTS, C
from twin_sim.sites import get_sites


@pytest.fixture(scope="module")
def nominal_run():
    draws = [PR.nominal()] + PR.draw(3, seed=7)
    P = sim.param_arrays(draws)
    phys = sim.physics(2023, P)
    fc = RF.season_forecast(2023)
    r = sim.run_season(phys, P, DP.make_policy("P2", fc), fc, sensor_seed=1, record=True)
    return P, phys, fc, r


def test_sites_contract():
    sites = get_sites()
    assert 3 <= len(sites) <= 5
    for s in sites:
        C.Site.model_validate(s.model_dump())
        assert s.provenance["lat"].kind == "observed"


def test_forcing_contract_and_real_signal():
    f = FO.forcing_series(2025, 0)
    C.ForcingSeries.model_validate(f.model_dump())
    assert len(f.t) == 122 * 24
    tide = np.array(f.tide_m)
    assert tide.max() - tide.min() > 3.0          # spring range of several metres
    assert f.tide_provenance.kind == "harmonic_prediction" and f.rain_provenance.kind == "reanalysis"


def test_mass_balance_hourly(nominal_run):
    P, phys, fc, r = nominal_run
    rec = r["rec"]
    lhs = rec["arrived"]
    rhs = rec["captured"] + rec["ent"] + rec["over"] + rec["byp"]
    assert np.allclose(lhs, rhs, atol=1e-6)
    assert (rec["stored"] >= -1e-9).all()
    assert (rec["stored"] <= P["capacity_kg"] + 1e-6).all()
    prev = np.concatenate([np.zeros_like(rec["stored"][:1]), rec["stored"][:-1]])
    assert np.allclose(rec["stored"], prev + rec["captured"] - rec["refl"] - rec["cleared"], atol=1e-6)
    for k in ("captured", "ent", "over", "byp", "refl", "cleared"):
        assert (rec[k] >= -1e-9).all(), k


def test_mass_balance_season(nominal_run):
    P, phys, fc, r = nominal_run
    fresh = phys["fresh"].sum(axis=0)
    rhs = r["escaped"] + r["cleared"] + r["end_stored"] + r["end_pool"]
    assert np.allclose(fresh, rhs, rtol=1e-9, atol=1e-6)


def test_interceptor_contract(nominal_run):
    P, phys, fc, r = nominal_run
    rec = r["rec"]
    s = IC.interceptor_series("mithi_mahim", list(phys["t"].to_pydatetime()),
                              {k: rec[k][:, 0, 0] for k in rec}, float(P["capacity_kg"][0, 0]), "test")
    C.InterceptorSeries.model_validate(s.model_dump())


def test_equal_crew_hours():
    fc = RF.season_forecast(2021)
    P = sim.param_arrays(PR.draw(2, seed=3))
    phys = sim.physics(2021, P)
    hours = [sim.run_season(phys, P, DP.make_policy(p, fc), fc, sensor_seed=2)["crew_h"] for p in ("P0", "P1", "P2")]
    assert np.allclose(hours[0], hours[1]) and np.allclose(hours[0], hours[2])
    assert hours[0][0] == DP.N_CREWS * DP.SHIFT_H * 122


def test_forecast_and_plan_contracts(nominal_run):
    P, phys, fc, r = nominal_run
    sids = [s.site_id for s in get_sites()]
    f = r["rec"]["fill_obs"][24 * 10, 0]
    for sf in RF.site_forecasts(fc, 10, f, sids):
        C.SiteForecast.model_validate(sf.model_dump())
    plan = DP.dispatch_plan("P2", 10, r["plans"][10][0], fc, sids, f)
    C.DispatchPlan.model_validate(plan.model_dump())
    assert len(plan.assignments) == DP.N_CREWS


def test_bundle_part_if_present():
    p = RESULTS / "bundle_part.json"
    if not p.exists():
        pytest.skip("run python -m twin_sim.run first")
    assert p.stat().st_size <= 5_000_000
    b = C.DashboardBundle.model_validate(json.loads(p.read_text()))
    assert b.telemetry and all(t.simulated for t in b.telemetry)
    assert {s.site_id for s in b.sites} == {f.site_id for f in b.forcing}
