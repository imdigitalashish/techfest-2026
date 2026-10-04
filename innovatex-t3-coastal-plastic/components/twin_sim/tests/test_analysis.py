"""Tests for the fail-open fuse / re-float SENSITIVITY switches and the analysis summaries.
Run: cd innovatex-t3-coastal-plastic/components && python -m pytest twin_sim/tests -q"""
import json

import numpy as np
import pytest

from twin_sim import analysis as AN
from twin_sim import dispatch as DP
from twin_sim import interceptor as IC
from twin_sim import params as PR
from twin_sim import risk_forecaster as RF
from twin_sim import sim
from twin_sim._paths import RESULTS


@pytest.fixture(scope="module")
def season_2023():
    P = sim.param_arrays([PR.nominal()] + PR.draw(2, seed=11))
    return P, sim.physics(2023, P), RF.season_forecast(2023)


def test_default_switches_are_bit_identical(season_2023):
    P, phys, fc = season_2023
    base = sim.run_season(phys, P, DP.make_policy("P0", fc), fc, sensor_seed=5)
    same = sim.run_season(phys, dict(P, fail_open_fuse=False, refloat_mult=1.0), DP.make_policy("P0", fc), fc,
                          sensor_seed=5)
    for k in ("escaped", "ent", "over", "byp", "refl", "rel", "cleared", "end_stored"):
        assert np.array_equal(base[k], same[k]), k


@pytest.mark.parametrize("variant", ["b_fail_open_fuse", "c_fuse_refloat_x0.2"])
def test_fuse_mass_balance_and_no_release(season_2023, variant):
    P, phys, fc = season_2023
    r = sim.run_season(phys, dict(P, **AN.VARIANTS[variant]), DP.make_policy("P2", fc), fc, sensor_seed=5,
                       record=True)
    rec = r["rec"]
    assert np.allclose(rec["arrived"], rec["captured"] + rec["ent"] + rec["over"] + rec["byp"], atol=1e-6)
    assert (rec["stored"] >= -1e-9).all()
    prev = np.concatenate([np.zeros_like(rec["stored"][:1]), rec["stored"][:-1]])
    assert np.allclose(rec["stored"], prev + rec["captured"] - rec["refl"] - rec["cleared"], atol=1e-6)
    assert np.all(rec["rel"] == 0.0)
    assert np.allclose(r["load"], r["escaped"] + r["cleared"] + r["end_stored"] + r["end_pool"], atol=1e-6)


def test_release_is_part_of_refloat(season_2023):
    P, phys, fc = season_2023
    r = sim.run_season(phys, P, DP.make_policy("P0", fc), fc, sensor_seed=5)
    assert (r["rel"] <= r["refl"] + 1e-9).all() and (r["rel"] >= 0).all()


def test_paired_toy():
    p = AN.paired(np.array([1.0, 2.0, 3.0]), np.array([2.0, 2.0, 2.0]))
    assert p["draws_a_lower"] == 1 and p["n_draws"] == 3 and p["median"] == 0.0


def test_summarise_small_run():
    runs = AN.run_heldout(n_draws=2, years=[2024])
    s = AN.summarise(runs)
    assert s["checks"]["mass_balance_max_abs_err_kg"] < 1e-6 and s["checks"]["equal_crew_hours"]
    for p in ("P0", "P1", "P2"):
        R = runs[p]
        assert np.allclose((R["ent"] + R["over"] + R["byp"]) / R["escaped"], 1.0)
        assert 0.0 <= s["fwce"][p]["fwce"]["median"] <= 1.0
    assert np.all(runs["P2|b_fail_open_fuse"]["rel"] == 0.0)
    assert s["fuse_sensitivity_P2"]["a_current_release"]["escaped_rel_vs_a"]["median"] == 0.0
    assert len(s["per_draw"]["P2"]["escaped_kg"]) == 2
    assert set(s["entrainment_split"]["P2"]) == {"floor_1_minus_emax", "velocity_driven"}
    ang = s["boom_angle_sensitivity_P2"]
    assert set(ang) == set(AN.ANGLE_HARDWARE) and ang["a_current_release"]["theta90"]["escaped_rel_vs_theta90"]["median"] == 0.0
    assert not any(k.endswith("|theta90") for k in s["per_draw"])


def test_angle_switch_default_identical_and_monotone(season_2023):
    P, phys, fc = season_2023
    base = sim.run_season(phys, P, DP.make_policy("P0", fc), fc, sensor_seed=5)
    same = sim.run_season(phys, dict(P, sin_theta=1.0), DP.make_policy("P0", fc), fc, sensor_seed=5)
    assert np.array_equal(base["escaped"], same["escaped"]) and np.array_equal(base["ent"], same["ent"])
    v = np.linspace(-1.5, 1.5, 31)[:, None, None] * np.ones_like(P["e_max"])
    e90, e20 = IC.efficiency(v, P), IC.efficiency(v, dict(P, sin_theta=AN.ANGLES[20]))
    assert (e20 >= e90 - 1e-12).all() and (e20 <= P["e_max"] + 1e-12).all()


def test_entrainment_split_and_mass_balance_with_angle(season_2023):
    P, phys, fc = season_2023
    r = sim.run_season(phys, dict(P, sin_theta=AN.ANGLES[30]), DP.make_policy("P2", fc), fc, sensor_seed=5,
                       record=True)
    rec = r["rec"]
    assert np.allclose(rec["ent_floor"] + rec["ent_vel"], rec["ent"], atol=1e-9)
    assert (rec["ent_floor"] >= 0).all() and (rec["ent_vel"] >= -1e-9).all()
    assert np.allclose(rec["arrived"], rec["captured"] + rec["ent"] + rec["over"] + rec["byp"], atol=1e-6)
    assert np.allclose(r["load"], r["escaped"] + r["cleared"] + r["end_stored"] + r["end_pool"], atol=1e-6)


def test_exposure_small():
    ex = AN.exposure_nominal(years=[2024])
    for a in AN.ANGLES:
        assert 0.0 <= ex[f"theta{a}"]["share_of_hours"] <= 1.0
        assert 0.0 <= ex[f"theta{a}"]["share_of_arrived_kg"] <= 1.0
    assert ex["theta20"]["share_of_hours"] <= ex["theta90"]["share_of_hours"]
    assert len(ex["theta90"]["by_site"]) == 4


def test_analysis_json_if_present():
    p = RESULTS / "analysis.json"
    if not p.exists():
        pytest.skip("run python -m twin_sim.analysis first")
    assert p.stat().st_size < 200_000
    d = json.loads(p.read_text())
    assert d["label"] == "SIMULATED" and "twin_sim.analysis" in d["reproduce"]
    assert d["checks"]["escaped_median_matches_metrics_json"] and d["checks"]["equal_crew_hours"]
    assert d["checks"]["mass_balance_max_abs_err_kg"] < 1e-3



def test_analysis_json_angle_keys_if_regenerated():
    p = RESULTS / "analysis.json"
    if not p.exists():
        pytest.skip("run python -m twin_sim.analysis first")
    d = json.loads(p.read_text())
    new = {"entrainment_split", "boom_angle_sensitivity_P2", "exposure_P2_nominal"}
    if not new & set(d):
        pytest.skip("analysis.json predates the boom-angle keys; regenerate with python -m twin_sim.analysis")
    assert new <= set(d)
    assert set(d["boom_angle_sensitivity_P2"]) == set(AN.ANGLE_HARDWARE)
