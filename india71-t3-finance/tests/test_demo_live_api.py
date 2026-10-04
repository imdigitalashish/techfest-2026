"""Tests for demo/live_api.py: every attack outcome comes from the committed C5 and C11 code."""
import math

import pytest

from demo import live_api as L

TABLES = {t: [{"unit": f"D{i}", "numerator": 40 + i, "denominator": 100 + 3 * i} for i in range(1, 6)] for t in L.DP_TABLES}


@pytest.fixture()
def sess(tmp_path):
    return L.Session(b"test-key", str(tmp_path / "ledger.json"), TABLES, seed=7)


def test_scripted_attacks_end_to_end(sess):
    steps = {s["step"]: s["result"] for s in L.run_script(sess)}
    rule = {k.split(":")[1]: (v["decision"]["allow"], v["decision"]["rule_ids"][0])
            for k, v in steps.items() if k.startswith("c5:") and k != "c5:log"}
    assert rule == {"bc_other_bank": (False, "D5"), "bc_own_bank": (True, "A2"), "bc_as_bank": (False, "D8"),
                    "bc_aadhaar": (False, "D2"), "slbc_bc_scores": (False, "D6"), "dfs_person_list": (False, "D4"),
                    "researcher_district": (True, "A4")}
    assert set(steps["c5:bc_own_bank"]["decision"]["obligations"]["masked_fields"]) >= {"balance", "aadhaar_number"}
    assert steps["c5:researcher_district"]["decision"]["obligations"]["dp_epsilon"] == L.TOTAL_EPS
    for kind in ("delete", "flip", "forge"):
        assert steps[f"tamper:{kind}"]["verify"]["valid"] is False
    ks = steps["tamper:keyed_suffix"]["verify"]
    assert ks["valid"] and ks["unanchored"] == 1 and not ks["full_integrity"]
    log = steps["c5:log"]
    assert len(log["entries"]) == len(L.C5_SCRIPT) and log["verify"]["full_integrity"]  # real log untouched
    assert steps["c11:release:district_usage"]["ok"] and steps["c11:release:district_usage"]["spent"] == L.TABLE_EPS
    assert steps["c11:race"]["winners"] == 1 and steps["c11:race"]["spent"] == L.TOTAL_EPS
    assert steps["c11:release:district_usage_60plus"]["error"] == "PermissionError"
    assert steps["c11:charge:refund"]["error"] == "ValueError" and steps["c11:charge:nan"]["error"] == "ValueError"
    assert steps["c11:restart"]["reloaded"]["spent"] == L.TOTAL_EPS and not steps["c11:restart"]["charge_after_restart"]["ok"]
    assert steps["c11:reopen"]["error"] == "ValueError"


def test_contract_refuses_malformed_request(sess):
    r = sess.c5_request({"requester_role": "superuser", "requester_id": "x", "purpose": "p", "data_elements": [],
                         "granularity": "person", "legal_basis": "b"})
    assert r["ok"] is False and r["error"] == "contract"
    assert sess.c5_log()["entries"] == []


def test_unregistered_requester_is_denied_and_logged(sess):
    r = sess.c5_request({"requester_role": "bc", "requester_id": "bc-unknown", "purpose": "outreach",
                         "data_elements": ["target_list"], "granularity": "person", "legal_basis": "bank_bc_agreement",
                         "own_customers_only": True, "subject_bank_id": "PSB_A"})
    assert r["decision"]["rule_ids"] == ["D8"] and r["entry"]["seq"] == 0


def test_averaging_baseline_recovers_cell_without_a_budget_but_not_with_one():
    b = L.averaging_baseline(23, L.TABLE_EPS, 200, seed=11)
    assert b["allowed_with_ledger"] == int(L.TOTAL_EPS / L.TABLE_EPS)
    assert abs(b["estimate_without"] - 23) < 1.5
    assert math.isfinite(b["estimate_with_ledger"])
