"""Tests for the demo's PROTOTYPE components: C7 fraud & safety gate and C8 last-mile orchestrator."""
import datetime as dt
import json
import pathlib

import contracts as C
from components.fraud_gate import gate
from components.outreach import orchestrate
from components.policy_engine.engine import PolicyEngine

TODAY = dt.date(2026, 10, 5)
ROOT = pathlib.Path(__file__).resolve().parents[1]


def _row(tok, **kw):
    base = {"account_token": tok, "arm": "bc_visit", "in_holdout": False, "usage_state": "basic",
            "regulatory_inoperative": False, "kyc_due": False, "on_suspect_list": False}
    return {**base, **kw}


def test_c7_rules_first_match_and_contract():
    rows = [_row("A1", arm="none"), _row("A2", in_holdout=True, on_suspect_list=True), _row("A3", on_suspect_list=True,
            usage_state="no_use_24m"), _row("A4", usage_state="no_use_24m"), _row("A5", regulatory_inoperative=True),
            _row("A6", kyc_due=True), _row("A7")]
    got = [(d["decision"], d["rule"]) for d in gate.decide(rows, TODAY)]
    assert got == [("allow", "N0"), ("allow", "N0"), ("hold", "H1"), ("verify", "V1"), ("verify", "V1"),
                   ("verify", "V2"), ("allow", "A1")]
    for d in gate.decide(rows, TODAY):
        C.SafetyDecision.model_validate(gate.contract_view(d))


def test_c7_hold_is_time_bounded_and_appealable():
    d = gate.decide_one(_row("H", on_suspect_list=True), TODAY)
    assert d["resolve_by"] == (TODAY + dt.timedelta(days=gate.SERVICE_DAYS)).isoformat()
    assert d["appeal"] and d["risk_score"] == 1.0


def _allow_all(bc):
    return {"allow": True, "rule_ids": ["A2"], "obligations": {"masked_fields": ["balance", "aadhaar_number"]}}


def test_c8_tasks_contract_holds_kyc_steps_and_masks():
    rows = [dict(_row("V", usage_state="no_use_24m"), bc_id="BC1", reason_codes="R1;G1", balance=12.5, aadhaar_number="x"),
            dict(_row("H", on_suspect_list=True), bc_id="BC1"),
            dict(_row("U", arm="upi_onboard"), bc_id="BC1"),
            dict(_row("S", arm="sms_ivr", usage_state="no_use_24m"), bc_id="BC1")]
    out = orchestrate.build_tasks(rows, gate.decide(rows, TODAY), TODAY, authorize=_allow_all)
    assert [t["account_token"] for t in out["tasks"]] == ["V", "U", "S"]
    assert [h["account_token"] for h in out["held"]] == ["H"]
    for t in out["tasks"]:
        C.ChannelTask.model_validate(t)
    card = {c["account_token"]: c for c in out["cards"]}
    assert orchestrate.KYC_BC in card["V"]["steps"] and orchestrate.KYC_REMOTE in card["S"]["steps"]
    assert card["U"]["channel"] == "bc_assisted_upi123pay" and card["S"]["assigned_bc_id"] is None
    assert "balance" not in card["V"]["visible_fields"] and "aadhaar_number" not in card["V"]["visible_fields"]
    assert card["V"]["masked"] == ["balance", "aadhaar_number"]


def test_c8_bc_daily_cap_rolls_over():
    rows = [dict(_row(f"A{i}"), bc_id="BC9") for i in range(orchestrate.CAP_PER_BC_DAY + 1)]
    out = orchestrate.build_tasks(rows, gate.decide(rows, TODAY), TODAY, authorize=_allow_all)
    due = [t["due_date"] for t in out["tasks"]]
    assert due[:-1] == [TODAY.isoformat()] * orchestrate.CAP_PER_BC_DAY
    assert due[-1] == (TODAY + dt.timedelta(days=1)).isoformat()


def test_c8_needs_c5_allow_from_the_real_policy_engine():
    spec = json.loads((ROOT / "components" / "policy_engine" / "scenarios.json").read_text())
    eng = PolicyEngine(b"test-key", spec["registry"])

    def authorize_for(bank):
        def f(bc):
            return eng.request({"request_id": f"bc-list-{bc}", "requester_role": "bc", "requester_id": "bc-1",
                                "purpose": "outreach", "data_elements": ["target_list"], "granularity": "person",
                                "legal_basis": "bank_bc_agreement", "own_customers_only": True, "subject_bank_id": bank})
        return f

    rows = [dict(_row("V", usage_state="no_use_24m"), bc_id="BC1", balance=1.0)]
    ok = orchestrate.build_tasks(rows, gate.decide(rows, TODAY), TODAY, authorize=authorize_for("PSB_A"))
    assert ok["access"]["BC1"]["rule_ids"] == ["A2"] and len(ok["tasks"]) == 1
    assert "balance" in ok["cards"][0]["masked"] and "balance" not in ok["cards"][0]["visible_fields"]
    other = orchestrate.build_tasks(rows, gate.decide(rows, TODAY), TODAY, authorize=authorize_for("PVT_E"))
    assert other["access"]["BC1"]["rule_ids"] == ["D5"] and other["tasks"] == [] and other["denied_bcs"] == ["BC1"]
    assert len(eng.log.entries) == 2  # both decisions were logged
