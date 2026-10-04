"""Contract and TCA unit tests (no simulator needed). Run: .venv/bin/python -m pytest -q tests"""
import os, sys
import numpy as np
import pytest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ("architecture/contracts", "components/tca", "components/execution_agent", "components/impact_model"):
    sys.path.insert(0, os.path.join(ROOT, p))
import contracts as C  # noqa: E402
from tca.metrics import decompose_is, implementation_shortfall  # noqa: E402
from execution_agent.policies import DecisionContext, ImpactAwarePolicy, TwapPolicy, propagator_qp_schedule  # noqa: E402


class _W:  # minimal WorldResult stand-in: piecewise-constant mid
    def __init__(self, t, mid):
        self.t, self.m = np.asarray(t), np.asarray(mid, float)
    def mid_at(self, q, strictly_before=False):
        i = np.searchsorted(self.t, np.asarray(q), side="left" if strictly_before else "right") - 1
        return self.m[np.clip(i, 0, len(self.m) - 1)]


def test_contract_validation():
    with pytest.raises(Exception):
        C.ChildOrder(kind="LMT", qty=10)
    with pytest.raises(Exception):
        C.VolumeProfile(cum_fraction=[0.5, 0.4, 1.0])
    C.TwinSpec(world=C.WorldSpec(seed=1), parent=C.ParentOrder(side="SELL", quantity=4000),
               policy=C.PolicySpec(kind="TWAP", label="TWAP"))


def test_is_decomposition_identity():
    rs = np.random.RandomState(0)
    t = np.arange(0, 100)
    twin = _W(t, 100000 + rs.randn(100).cumsum())
    treat = _W(t, twin.m - np.linspace(0, 8, 100))
    dts = [5, 25, 55, 85]
    fills = [(d + 1, int(treat.mid_at([d])[0] - 1), 100) for d in dts]
    arr = 100000.0
    isd = implementation_shortfall(fills, arr, "SELL")
    dec = decompose_is(fills, dts, arr, "SELL", treat, twin)
    assert abs(isd["is_bps"] - (dec["drift_bps"] + dec["own_impact_bps"] + dec["instant_bps"])) < 1e-9
    assert dec["own_impact_bps"] > 0


def test_twap_completes_and_qp_sums_to_one():
    pol = TwapPolicy()
    filled, n = 0, 40
    for k in range(n):
        ctx = DecisionContext(0, k, n, list(range(n)), 4000, filled, "SELL", [(100, 100)], [(101, 100)], [])
        filled += sum(o.qty for o in pol.decide(ctx))
    assert filled == 4000
    w = propagator_qp_schedule(40, 30.0, 0.005, 0.0059, 60.0)
    assert abs(w.sum() - 1) < 1e-9 and (w >= 0).all()
    assert w[0] > w[20] and w[-1] > w[20]  # U-shape under transient impact


def test_ia_limit_never_beyond_max_levels():
    pol = ImpactAwarePolicy(40, 30.0, 0.005, 0.0059, 60.0, max_levels=1)
    ctx = DecisionContext(0, 3, 40, [i * 30_000_000_000 for i in range(40)], 4000, 300, "SELL",
                          [(99990, 50), (99980, 500)], [(100000, 80)], [])
    orders = pol.decide(ctx)
    assert all(o.kind == "LMT" and o.price == 99990 for o in orders)


def _excess_at_steady_state(ref_mode):
    dt_ns = 30_000_000_000
    n = 40
    pol = ImpactAwarePolicy(n, 30.0, 0.005, 0.0059, 60.0, ref_mode=ref_mode)
    rate = 4000 / n
    k = 30
    fills = [(i * dt_ns, 99990, int(rate)) for i in range(k)]
    ctx = DecisionContext(k * dt_ns, k, n, [i * dt_ns for i in range(n)], 4000, int(rate) * k, "SELL",
                          [(99990, 100)], [(100000, 100)], fills)
    decay = np.exp(-30.0 / 60.0)
    ref = rate * 0.0059 / (1 - decay) * (decay if ref_mode == "pre_trade" else 1.0)
    return (pol.own_impact(ctx) - ref) / ref


def test_feedback_reference_modes():
    assert abs(_excess_at_steady_state("pre_trade")) < 0.01
    assert abs(_excess_at_steady_state("post_trade") - (np.exp(-0.5) - 1)) < 0.01  # documented legacy bias


def test_fill_time_split_sums_to_instant():
    from tca.metrics import decompose_fill_time
    rs = np.random.RandomState(1)
    t = np.arange(0, 200)
    twin = _W(t, 100000 + rs.randn(200).cumsum())
    treat = _W(t, twin.m - np.linspace(0, 6, 200))
    dts = [10, 60, 110, 160]
    fills = [(d + 7, int(treat.mid_at([d + 3])[0] - 1), 50) for d in dts] + [(d + 1, int(treat.mid_at([d])[0]) - 2, 25) for d in dts]
    arr = 100000.0
    dec = decompose_is(fills, dts, arr, "SELL", treat, twin)
    ft = decompose_fill_time(fills, dts, arr, "SELL", treat)
    assert abs(dec["instant_bps"] - (ft["delay_bps"] + ft["at_fill_bps"])) < 1e-9


def test_docs_have_no_drift():
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(ROOT, "eval", "check_docs.py")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-2000:]
