"""Contract tests: every built component's output validates against its contract (SYNTHETIC data)."""
import numpy as np
import pandas as pd
import pytest

import contracts as C
from components.linker.link import link, pairwise_f1, person_usage
from components.simulator.sim import SimConfig, simulate
from components.targeting import engine
from components.usage_state.classify import classify


@pytest.fixture(scope="module")
def world():
    return simulate(SimConfig(n_persons=3000, n_districts=6, seed=3))


def test_simulator_account_month_contract(world):
    assert C.validate_frame(world["account_month"], C.AccountMonth, sample=1500) == 1500


def test_simulator_calibrated_inoperative_share(world):
    assert 0.15 < world["accounts"]["inoperative_true"].mean() < 0.31


def test_usage_state_contract_and_states(world):
    u = classify(world["account_month"])
    C.validate_frame(u, C.AccountUsage, sample=None)
    assert set(u["state"]) <= set(C.STATE_ORDER)
    assert len(u) == len(world["accounts"])


def test_linker_contract_and_perfect_linkage_when_all_seeded(world):
    acc = world["accounts"]
    refs = pd.DataFrame({"account_token": acc["account_token"], "bank_id": acc["bank_id"],
                         "identity_ref": "REF" + acc["person_id"].astype(str)})
    links = link(refs, b"k1")
    C.validate_frame(links, C.AccountPersonLink, sample=None)
    assert pairwise_f1(acc["person_id"], links["person_token"]) == pytest.approx(1.0)
    other = link(refs, b"k2")  # purpose-scoped keys give unlinkable tokens
    assert not set(links["person_token"]) & set(other["person_token"])
    pu = person_usage(links, classify(world["account_month"]),
                      acc[["account_token", "district_code", "gender", "age_band", "rural"]],
                      acc.loc[acc["is_dbt_account"], "account_token"])
    C.validate_frame(pu, C.PersonUsage, sample=None)
    assert len(pu) == acc["person_id"].nunique()


def test_allocation_respects_budget_and_women_floor():
    rng = np.random.default_rng(0)
    n = 2000
    U = pd.DataFrame({a: rng.normal(0.02, 0.03, n) for a in engine.ARMS})
    female = rng.random(n) < 0.4
    costs = {"none": 0, "sms_ivr": 3, "bc_visit": 100, "upi_onboard": 120, "incentive": 55}
    arms = engine.allocate(U, costs, budget=20000, female=female, min_share_women=0.6)
    spend = sum(costs[a] for a in arms)
    assert spend <= 20000 * 1.001
    treated = arms != "none"
    assert female[treated.to_numpy()].mean() >= 0.6 - 0.02
