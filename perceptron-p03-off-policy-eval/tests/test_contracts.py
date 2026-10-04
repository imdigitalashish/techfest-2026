"""Contract tests: every component's I/O contract and the identities the system relies on.
Run: cd perceptron-p03-off-policy-eval && .venv/bin/python -m pytest -q tests
"""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from architecture.contracts.contracts import ActionDist, BanditLog, ScenarioConfig  # noqa: E402
from components.decomposer.decompose import decompose  # noqa: E402
from components.estimators.ope import crossfit_q, delta_vs_onpolicy, estimate  # noqa: E402
from components.intervals.ci import bootstrap, wald  # noqa: E402
from components.sensitivity.msm import delta_curve, hajek_bounds  # noqa: E402
from components.simulator.sim import World, ground_truth, simulate  # noqa: E402

CFG = ScenarioConfig(name="t", n_before=4000, n_after=4000, response_drift=-0.5, mix_shift=0.5,
                     new_policy_quality=0.7, old_policy_quality=0.3)


@pytest.fixture(scope="module")
def sim():
    return simulate(CFG, ground_truth(World(CFG), n_mc=50_000))


def test_banditlog_rejects_bad_action():
    with pytest.raises(Exception):
        BanditLog(X=np.zeros((3, 2)), A=np.array([0, 1, 5]), R=np.zeros(3), period=np.zeros(3, int), n_actions=3)


def test_actiondist_rows_sum_to_one():
    with pytest.raises(Exception):
        ActionDist(probs=np.full((2, 3), 0.5), policy="bad")


def test_truth_identities(sim):
    t = sim.truth
    assert t.naive_expected == pytest.approx(t.policy_effect_after + t.env_change)
    assert t.env_change == pytest.approx(t.mix_shift + t.response_drift)


def test_ipw_of_logging_policy_is_onpolicy_mean(sim):
    log = sim.after
    pi_logged = ActionDist(probs=sim.world.policy(log.X, "new"), policy="new")
    v = estimate("IPW", log, pi_logged)
    assert v.value == pytest.approx(log.R.mean(), rel=1e-9)


def test_dr_recovers_policy_effect(sim):
    pi_old = ActionDist(probs=sim.world.policy(sim.after.X, "old"), policy="old")
    d = delta_vs_onpolicy("DR", sim.after, pi_old, crossfit_q(sim.after))
    se = d.influence.std(ddof=1) / np.sqrt(len(d.influence))
    assert abs(d.delta - sim.truth.policy_effect_after) < 4 * se


def test_decomposition_identity(sim):
    w = sim.world
    dec = decompose(sim.before, sim.after, ActionDist(probs=w.policy(sim.after.X, "old"), policy="old"),
                    ActionDist(probs=w.policy(sim.before.X, "old"), policy="old"))
    assert dec.naive == pytest.approx(dec.policy_effect.point + dec.env_change)
    assert dec.env_change == pytest.approx(dec.mix_shift + dec.response_drift)


def test_msm_gamma1_is_hajek_and_widens(sim):
    log = sim.after
    c = sim.world.policy(log.X, "old")[np.arange(len(log.A)), log.A]
    w = c / log.pscore
    hajek = (w * log.R).sum() / w.sum()
    lo1, hi1 = hajek_bounds(c, log.pscore, log.R, 1.0)
    assert lo1 == pytest.approx(hajek) and hi1 == pytest.approx(hajek)
    lo2, hi2 = hajek_bounds(c, log.pscore, log.R, 2.0)
    assert lo2 < lo1 and hi2 > hi1
    curve = delta_curve(c, log.pscore, log.R, [1.0, 2.0, 4.0], B=20)
    assert all(l <= h for l, h in zip(curve.lo, curve.hi))
    assert curve.hi[2] - curve.lo[2] >= curve.hi[0] - curve.lo[0]


def test_intervals_contain_point():
    phi = np.random.default_rng(0).normal(1.0, 1.0, 500)
    for ci in (wald(phi), bootstrap(phi, B=200)):
        assert ci.lo <= ci.point <= ci.hi
