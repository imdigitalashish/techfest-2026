"""Contract tests for the P7 walking skeleton. Run: .venv/bin/python -m pytest -q tests"""
from dataclasses import replace

import numpy as np
from pettingzoo.test import parallel_api_test

from architecture.contracts.contracts import IDLE, Forecast
from components.forecasting.forecasters import ChangeAwareForecaster, EWMAForecaster
from components.planner.mpc import MPCPlanner
from components.policies.policies import make_policy
from components.scenarios.scenarios import SCENARIOS, build_trace, diurnal_profile, historical_shares, od_matrix
from components.simulator.core import DispatchCore
from components.simulator.pz_env import DispatchParallelEnv

CFG = replace(SCENARIOS["shock+drift+spikes"], horizon=300, shock_window=(0.3, 0.4), shock_duration=60)


def _meta(trace):
    shares = historical_shares(CFG, n_days=1)
    return dict(grid=CFG.grid, n_zones=CFG.grid ** 2, od_prob=trace.od_prob, profile=diurnal_profile(CFG, n_days=1),
                hist_shares=shares, init_level=shares * CFG.total_rate, init_level_raw=shares * CFG.total_rate,
                rates=trace.rates)


def test_trace_is_deterministic_and_labelled():
    a, b = build_trace(CFG, 3), build_trace(CFG, 3)
    assert np.array_equal(a.counts, b.counts) and np.array_equal(a.req_dest, b.req_dest)
    assert a.counts.sum() == a.req_dest.size
    kinds = {c.kind for c in a.change_points}
    assert {"shock_on", "shock_off", "drift_start", "spike_on"} <= kinds


def test_pettingzoo_parallel_api():
    env = DispatchParallelEnv(CFG, n_agents=12, horizon=60)
    parallel_api_test(env, num_cycles=50)


def test_units_conserved_and_requests_accounted():
    tr = build_trace(CFG, 1)
    core = DispatchCore(tr, n_agents=20, patience=5, init_seed=1)
    pol = make_policy("reactive"); pol.reset(_meta(tr))
    served = lost = 0
    while not core.done:
        st = core.state()
        assert st.agent_zone.size == 20 and st.idle_count.sum() == (st.agent_status == IDLE).sum()
        info = core.step(pol.act(st)); pol.observe(info)
        served += info.served.sum(); lost += info.lost.sum()
        assert info.wait_hist.sum() == info.served.sum()
    waiting = int((core.tail - core.head).sum())
    assert served + lost + waiting == tr.counts.sum()


def test_wrapper_matches_core():
    env = DispatchParallelEnv(CFG, n_agents=10, horizon=80)
    env.reset(seed=4)
    tr = build_trace(replace(CFG, horizon=80), 4)
    core = DispatchCore(tr, n_agents=10, patience=10, init_seed=4)
    rng = np.random.default_rng(0)
    for _ in range(79):
        a = rng.integers(0, 25, size=10)
        _, rew, *_ = env.step({f"unit_{i}": int(a[i]) for i in range(10)})
        info = core.step(a)
        assert np.isclose(sum(rew.values()), info.reward)
    assert np.array_equal(env.core.zone, core.zone)


def test_planner_flows_feasible():
    p = MPCPlanner(5, od_matrix(CFG), horizon=6)
    rng = np.random.default_rng(0)
    idle = rng.integers(0, 4, 25)
    plan = p.solve(idle, rng.integers(0, 2, (6, 25)), rng.integers(0, 3, 25), rng.random((6, 25)))
    assert plan.status == "ok" and plan.flows.shape == (25, 25)
    assert (plan.flows >= 0).all() and (plan.flows.sum(1) <= idle).all() and np.trace(plan.flows) == 0


def test_forecasters_follow_contract():
    prof = np.ones(1440); lvl = np.full(25, 0.4)
    for fc in (EWMAForecaster(prof, lvl), ChangeAwareForecaster(prof, lvl)):
        for t in range(30):
            fc.observe(t, np.full(25, 2))
        out = fc.forecast(30, 6)
        assert isinstance(out, Forecast) and out.mean.shape == (6, 25) and (out.mean >= 0).all()
    assert ChangeAwareForecaster(prof, lvl).det.Z == 25


def test_planner_backends_agree():
    od = od_matrix(CFG)
    a, b = MPCPlanner(5, od, horizon=8, hop_steps=2, backend="highspy"), MPCPlanner(5, od, horizon=8, hop_steps=2, backend="scipy")
    rng = np.random.default_rng(1)
    for _ in range(10):
        args = (rng.integers(0, 4, 25), rng.integers(0, 2, (8, 25)), rng.integers(0, 4, 25), rng.random((8, 25)))
        pa, pb = a.solve(*args), b.solve(*args)
        assert pa.status == pb.status == "ok" and abs(pa.objective - pb.objective) < 1e-6
