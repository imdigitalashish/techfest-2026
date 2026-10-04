"""Tests for the ablation policies (P1m, P2_notide, P2_nofc) and the analysis keys they feed.
Run: cd innovatex-t3-coastal-plastic/components && python -m pytest twin_sim/tests -q"""
import json

import numpy as np
import pytest

from twin_sim import analysis as AN
from twin_sim import dispatch as DP
from twin_sim import params as PR
from twin_sim import risk_forecaster as RF
from twin_sim import sim
from twin_sim._paths import RESULTS


@pytest.fixture(scope="module")
def fc23():
    return RF.season_forecast(2023)


def _ctx(fc, fill):
    return DP.DayCtx(day=10, t0=240, fill_obs=np.array([fill]), fc=fc, S=4)


def test_p1m_ranks_by_mass_not_fraction(fc23):
    # nominal capacities: mithi 9000 kg, trombay 1800 kg -> 0.8 of mithi outweighs 0.9 of trombay
    ctx = _ctx(fc23, [0.8, 0.2, 0.2, 0.9])
    assert sorted(s for s, _, _ in DP.p1(ctx)[0]) == [0, 3]
    m = DP.p1m(ctx)[0]
    assert [s for s, _, _ in m] == [0, 0]                       # 7200 kg - 3200 kg per crew still > 1620 kg
    assert all(start == DP.FIXED_START_UTC and h == DP.SHIFT_H for _, start, h in m)


def test_access_tide_shape(fc23):
    a = fc23["access_tide"]
    assert a.shape == fc23["access"].shape and (a >= 0).all() and (a <= 1).all()


def test_notide_fixed_start_and_nofc_ignores_forecast(fc23):
    ctx = _ctx(fc23, [0.3, 0.5, 0.2, 0.6])
    assert all(st == DP.FIXED_START_UTC for _, st, _ in DP.make_policy("P2_notide", fc23)(ctx)[0])
    base = DP.make_policy("P2_nofc", fc23)(ctx)[0]
    fake = dict(fc23, arr24=fc23["arr24"] * 50 + 1e4, p_bypass=np.ones_like(fc23["p_bypass"]),
                access=np.zeros_like(fc23["access"]))
    assert DP.make_policy("P2_nofc", fake)(ctx)[0] == base


def test_ablation_policies_equal_crew_hours(fc23):
    P = sim.param_arrays(PR.draw(2, seed=3))
    phys = sim.physics(2023, P)
    h = [sim.run_season(phys, P, DP.make_policy(n, fc23), fc23, sensor_seed=2)["crew_h"]
         for n in ("P0", "P1m", "P2_notide", "P2_nofc")]
    assert all(np.allclose(h[0], x) for x in h[1:])


def test_ablation_keys_small_run():
    s = AN.summarise(AN.run_heldout(n_draws=2, years=[2024]))
    ab = s["ablations"]["paired_escaped_rel_diff"]
    assert {"P2_vs_P1m", "P2_vs_P2_notide", "P2_vs_P2_nofc", "P1m_vs_P1"} <= set(ab)
    mb = s["mass_boundary"]["P2"]
    assert {"unique_input_kg", "cleared_kg", "stored_at_season_end_kg", "escaped_kg"} <= set(mb)
    assert s["checks"]["mass_balance_max_abs_err_kg"] < 1e-6 and s["checks"]["equal_crew_hours"]


def test_analysis_json_ablation_keys_if_regenerated():
    p = RESULTS / "analysis.json"
    if not p.exists():
        pytest.skip("run python -m twin_sim.analysis first")
    d = json.loads(p.read_text())
    if "ablations" not in d:
        pytest.skip("analysis.json predates the ablation keys; regenerate with python -m twin_sim.analysis")
    assert d["label"] == "SIMULATED" and p.stat().st_size < 200_000
    assert {"ablations", "mass_boundary"} <= set(d)
