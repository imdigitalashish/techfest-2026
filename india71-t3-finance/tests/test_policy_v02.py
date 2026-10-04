"""C6 v0.2 policies respect the budget, the women's floor and the who-only arm restriction."""
import numpy as np
import pandas as pd

from components.targeting import policy_v02 as pv

COSTS = {"none": 0, "sms_ivr": 3, "bc_visit": 100, "upi_onboard": 120, "incentive": 55}
ATE = {"sms_ivr": (0.01, 0.01), "bc_visit": (0.05, 0.02), "upi_onboard": (0.015, 0.02), "incentive": (0.012, 0.02)}


def _spend(arms):
    return sum(COSTS[a] for a in arms)


def test_rule_policy_budget_and_arms():
    arms = pv.rule_policy(1000, ATE, COSTS, 10_000, np.random.default_rng(0))
    assert _spend(arms) <= 10_000
    assert set(arms) == {"sms_ivr", "bc_visit"}  # stage 1 = best effect per rupee; upgrade = best extra effect per extra rupee


def test_two_stage_who_only_uses_rule_arm_and_floor():
    rng = np.random.default_rng(1)
    U = pd.DataFrame({a: rng.normal(m, 0.03, 1000) for a, (m, _) in ATE.items()})
    female = rng.random(1000) < 0.4
    arms = pv.two_stage(U, ATE, COSTS, 10_000, female, 0.55, arm_choice="rule")
    assert _spend(arms) <= 10_000 * 1.001
    up = arms != "sms_ivr"
    assert set(arms[up]) <= {"bc_visit"}
    assert female[up].mean() >= 0.55 - 0.02
