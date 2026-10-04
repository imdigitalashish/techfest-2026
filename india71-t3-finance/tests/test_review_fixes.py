"""Regression tests for the 4 Oct cross-model code-review fixes (reviews/2026-10-04-code-gpt-6-sol.md)."""
import math

import numpy as np
import pandas as pd
import pytest

from components.dp_publisher.dp import Ledger, release_rates
from components.scorecard.scorecard import incremental
from components.targeting import policy_v03 as pv

COSTS = {"none": 0, "sms_ivr": 3, "bc_visit": 100, "upi_onboard": 120, "incentive": 55}
ATE = {"sms_ivr": (0.01, 0.01), "bc_visit": (0.05, 0.01), "upi_onboard": (0.015, 0.01), "incentive": (0.012, 0.01)}


def _plans(n=2000, budget=10 * 2000, floor=0.55, seed=0):
    rng = np.random.default_rng(seed)
    female = rng.random(n) < 0.5
    U = pd.DataFrame({a: rng.normal(m, 0.03, n) for a, (m, _) in ATE.items()})
    rp = pv.rule_plan(n, ATE, COSTS, budget, female, floor, np.random.default_rng(1))
    return rp, pv.challenger_plan(rp, U, female, floor), female


def test_issue1_challenger_differs_from_rule_only_in_upgrades():
    rp, ch, _ = _plans()
    s1, up = rp["info"]["stage1"], rp["info"]["upgrade"]
    r = rp["arms"]
    assert ((r != "none") == (ch != "none")).all()            # identical stage-1 recipients and holdout
    assert (r == up).sum() == (ch == up).sum() > 0             # same upgrade arm and count
    assert set(ch[ch != "none"]) <= {s1, up}


def test_issue1_no_upgrades_means_identical_plans():
    ate = dict(ATE, sms_ivr=(-0.05, 0.01))                     # cheapest arm shown harmful -> costly stage 1, no upgrades
    rng = np.random.default_rng(2)
    female = rng.random(500) < 0.5
    rp = pv.rule_plan(500, ate, COSTS, 5000, female, 0.5, np.random.default_rng(3))
    U = pd.DataFrame({a: rng.normal(0, 0.03, 500) for a in ATE})
    assert rp["info"]["k2"] == 0 and (pv.challenger_plan(rp, U, female, 0.5) == rp["arms"]).all()


def test_issue3_floor_on_all_deployable_plans_and_tiny_case():
    rp, ch, female = _plans(floor=0.6)
    assert pv.floor_ok(rp["arms"], female, 0.6, ~rp["holdout"]) and pv.floor_ok(ch, female, 0.6, ~rp["holdout"])
    female2 = np.array([True, False])
    picked = pv.stratified_pick(np.array([0, 1]), 1, female2, 0.5, rng=np.random.default_rng(0))
    assert female2[picked].sum() == 1                           # reviewer's 2-person, 1-contact case


def test_issue5_holdout_gets_no_outreach():
    rp, ch, _ = _plans()
    assert rp["holdout"].sum() > 0 and (rp["arms"][rp["holdout"]] == "none").all() and (ch[rp["holdout"]] == "none").all()


def test_issue2_dp_noise_is_secret_and_ledger_validates(tmp_path):
    cnt = pd.DataFrame({"numerator": [27], "denominator": [100]})
    a = release_rates(cnt, 1.0, Ledger(10), "t")
    b = release_rates(cnt, 1.0, Ledger(10), "t")
    replay = release_rates(cnt, 1.0, Ledger(10), "t", seed=0)
    assert not (a.equals(b) and a.equals(replay))              # fresh secret noise per release
    for bad in (float("nan"), float("inf"), -1.0, 0.0):
        with pytest.raises(ValueError):
            Ledger(1.0).charge(bad, "t")
    p = str(tmp_path / "ledger.json")
    Ledger(1.0, p).charge(0.6, "unit")
    with pytest.raises(PermissionError):                       # budget persists across restarts and composes
        Ledger(1.0, p).charge(0.6, "district")


def test_issue13_small_units_are_flagged_not_nan():
    df = pd.DataFrame({"unit_id": [1] * 50 + [2] * 5, "holdout": [False] * 40 + [True] * 10 + [False] * 5,
                       "meaningful": np.r_[np.ones(25), np.zeros(25), np.ones(5)]})
    inc = incremental(df, min_n=10)
    assert inc.loc[2, "status"] == "insufficient_data" and math.isnan(inc.loc[2, "incremental"])
    assert inc.loc[1, "status"] == "ok"


def test_reissue19_two_ledger_clients_cannot_double_spend(tmp_path):
    p = str(tmp_path / "shared.json")
    a, b = Ledger(1.0, p), Ledger(1.0, p)          # both created before either charges
    a.charge(0.7, "unit")
    with pytest.raises(PermissionError):
        b.charge(0.7, "district")


def test_reissue3_strict_floor_has_no_tolerance_and_holdout_rounding_is_safe():
    female = np.array([True] * 5 + [False] * 4)
    arms = np.array(["sms_ivr"] * 3 + ["none"] * 2 + ["sms_ivr"] * 4, dtype=object)  # 3 of 7 treated are women
    assert not pv.floor_ok(arms, female, 5 / 9)    # needs ceil(5/9*7) = 4 women; one short must fail
    rp = pv.rule_plan(9, ATE, COSTS, 1000, female, 5 / 9, np.random.default_rng(0))
    assert pv.floor_ok(rp["arms"], female, 5 / 9, ~rp["holdout"])   # women rounded down in the holdout
    assert female[~rp["holdout"]].mean() >= 5 / 9
