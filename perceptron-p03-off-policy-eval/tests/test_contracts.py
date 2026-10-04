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


def test_new_knobs_leave_frozen_bank_worlds_unchanged():
    # S1 of the frozen bank v0 (eval/results/sim_bank_summary.md): V_before(old)=0.3435, V_after(old)=0.2133, V_after(new)=0.2886
    cfg = ScenarioConfig(name="S1", n_before=10_000, n_after=10_000, response_drift=-1.0, mix_shift=0.5,
                         new_policy_quality=0.7, old_policy_quality=0.3)
    t = ground_truth(World(cfg), n_mc=200_000)
    assert (round(t.v_before_old, 4), round(t.v_after_old, 4), round(t.v_after_new, 4)) == (0.3435, 0.2133, 0.2886)
    assert t.v_after_old_cf == pytest.approx(t.v_after_old)  # no feedback => same users either way


def test_shapley_identities(sim):
    from components.decomposer.decompose import shapley
    w = sim.world
    sh = shapley(sim.before, sim.after, ActionDist(probs=w.policy(sim.before.X, "new"), policy="new"),
                 ActionDist(probs=w.policy(sim.after.X, "old"), policy="old"))
    assert sh.naive == pytest.approx(sh.policy.point + sh.env)
    assert sh.interaction.point == pytest.approx(sh.effect_after.point - sh.effect_before.point)
    assert sh.policy.point == pytest.approx(0.5 * (sh.effect_after.point + sh.effect_before.point))
    t = sim.truth
    assert t.naive_expected == pytest.approx(t.shapley_policy + t.shapley_env)


def test_feedback_separates_direct_and_total_effect():
    cfg = ScenarioConfig(name="fb", feedback=1.0, response_drift=-1.0, new_policy_quality=0.7, old_policy_quality=0.3)
    t = ground_truth(World(cfg), n_mc=50_000)
    assert abs(t.feedback_population_effect) > 1e-3
    assert t.total_effect == pytest.approx(t.policy_effect_after + t.feedback_population_effect)


def test_gate_diagnostics_and_rule():
    from components.report.gate import decide, diagnostics
    rng = np.random.default_rng(0)
    w_good = rng.uniform(0.5, 1.5, 20_000)
    r = (rng.random(20_000) < 0.3).astype(float)
    d = diagnostics(w_good, r)
    assert 0.9 < d["ess_frac"] <= 1.0 and abs(d["z_mean_w"]) < 4
    rule = {"tau_ess": 0.05, "tau_r": 0.0, "tau_z": 3.0}
    assert decide(d, rule)[0]
    w_bad = np.where(rng.random(20_000) < 0.001, 900.0, 0.1)  # a few huge weights: low ESS
    ok, why = decide(diagnostics(w_bad, r), rule)
    assert not ok and any("ESS/n" in x for x in why)


def test_verdict_paths(sim):
    from components.decomposer.decompose import shapley
    from components.report.gate import diagnostics
    from components.report.verdict import verdict
    w = sim.world
    sh = shapley(sim.before, sim.after, ActionDist(probs=w.policy(sim.before.X, "new"), policy="new"),
                 ActionDist(probs=w.policy(sim.after.X, "old"), policy="old"))
    good = diagnostics(np.ones(1000), np.ones(1000))
    good["z_mean_w"] = 0.0
    rule = {"tau_ess": 0.05, "tau_r": 0.0, "tau_z": 3.0}
    v = verdict(sh, {"V(after,old)": good, "V(before,new)": good}, rule)
    assert v.decision == ("worked" if sh.policy.lo > 0 else "hurt" if sh.policy.hi < 0 else "inconclusive")
    bad = dict(good, ess_frac=0.001)
    assert verdict(sh, {"V(after,old)": bad, "V(before,new)": bad}, rule).decision == "cant_tell"
    v1 = verdict(sh, {"V(after,old)": good, "V(before,new)": bad}, rule)
    assert v1.diagnostics["decided_on"].startswith("Policy effect in the after period") and "not estimable" in v1.headline


def test_shapley_env_interval_and_gate_guards(sim):
    from components.decomposer.decompose import shapley
    from components.report.gate import decide, diagnostics
    w = sim.world
    sh = shapley(sim.before, sim.after, ActionDist(probs=w.policy(sim.before.X, "new"), policy="new"),
                 ActionDist(probs=w.policy(sim.after.X, "old"), policy="old"))
    assert sh.env_ci is not None and sh.env_ci.point == pytest.approx(sh.env)
    rule = {"tau_ess": 0.05, "tau_r": 0.0, "tau_z": 3.0}
    ok, why = decide(diagnostics(np.array([0.5, 1.5] * 50), np.zeros(100)), rule)  # review C5 counterexample
    assert not ok and "no informative rewards" in why
