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
    def mid_at(self, q):
        i = np.searchsorted(self.t, np.asarray(q), side="right") - 1
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
