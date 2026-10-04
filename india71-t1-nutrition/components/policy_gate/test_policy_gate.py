from __future__ import annotations

import json
from datetime import datetime, timezone

from architecture.contracts.models import AccessRequest, DataCategory, GeoUnit, Purpose, Role, ScopeLevel
from components.policy_gate.gate import decide

GEO = GeoUnit(state_code="S1", district_code="D1", project_code="P1", sector_code="SEC1", awc_code="AWC1", village_code="V1")


def req(role: Role, scope_level: ScopeLevel, scope_id: str, purpose: Purpose, category: DataCategory, **kw) -> AccessRequest:
    return AccessRequest(
        request_id=kw.pop("request_id", f"r-{role.value}-{purpose.value}-{category.value}"),
        actor_id="actor-1",
        actor_role=role,
        actor_scope_level=scope_level,
        actor_scope_id=scope_id,
        purpose=purpose,
        data_category=category,
        subject_child_key=kw.pop("subject_child_key", "child-1"),
        subject_scope_id=kw.pop("subject_scope_id", None),
        consent_artefact_id=kw.pop("consent_artefact_id", None),
        requested_at=datetime.now(timezone.utc),
    )


CASES = [
    ("aww own awc service", req(Role.AWW, ScopeLevel.AWC, "AWC1", Purpose.SERVICE_DELIVERY, DataCategory.IDENTIFIED_CHILD), {"subject_geo": GEO}, "allow"),
    ("asha task care", req(Role.ASHA, ScopeLevel.AWC, "AWC1", Purpose.CARE_COORDINATION, DataCategory.IDENTIFIED_CHILD), {"subject_geo": GEO, "has_open_task": True}, "allow"),
    ("anm task care", req(Role.ANM, ScopeLevel.AWC, "AWC1", Purpose.CARE_COORDINATION, DataCategory.IDENTIFIED_CHILD), {"subject_geo": GEO, "has_open_task": True}, "allow"),
    ("mo task care", req(Role.MO_PHC, ScopeLevel.PROJECT, "P1", Purpose.CARE_COORDINATION, DataCategory.IDENTIFIED_CHILD), {"subject_geo": GEO, "has_open_task": True}, "allow"),
    ("health open referral", req(Role.MO_PHC, ScopeLevel.PROJECT, "P1", Purpose.CARE_COORDINATION, DataCategory.HEALTH_RECORD), {"subject_geo": GEO, "has_open_task": True}, "allow"),
    ("health consent", req(Role.AWW, ScopeLevel.AWC, "AWC1", Purpose.SERVICE_DELIVERY, DataCategory.HEALTH_RECORD, consent_artefact_id="consent-1"), {"subject_geo": GEO}, "allow"),
    ("ls pseudo", req(Role.LS, ScopeLevel.SECTOR, "SEC1", Purpose.SUPERVISION, DataCategory.PSEUDONYMOUS_CHILD), {"subject_geo": GEO}, "allow_transformed"),
    ("ls risk", req(Role.LS, ScopeLevel.SECTOR, "SEC1", Purpose.SUPERVISION, DataCategory.RISK_SCORE), {"subject_geo": GEO}, "allow_transformed"),
    ("ls escalated identified", req(Role.LS, ScopeLevel.SECTOR, "SEC1", Purpose.SUPERVISION, DataCategory.IDENTIFIED_CHILD), {"subject_geo": GEO, "escalated": True}, "allow"),
    ("cdpo aggregate", req(Role.CDPO, ScopeLevel.PROJECT, "P1", Purpose.PROGRAMME_MONITORING, DataCategory.AGGREGATE), {"subject_geo": GEO}, "allow_transformed"),
    ("cdpo escalated identified", req(Role.CDPO, ScopeLevel.PROJECT, "P1", Purpose.CARE_COORDINATION, DataCategory.IDENTIFIED_CHILD), {"subject_geo": GEO, "escalated": True}, "allow"),
    ("dpo aggregate", req(Role.DPO, ScopeLevel.DISTRICT, "D1", Purpose.PROGRAMME_MONITORING, DataCategory.AGGREGATE), {"subject_geo": GEO}, "allow_transformed"),
    ("dm aggregate", req(Role.DM, ScopeLevel.DISTRICT, "D1", Purpose.PROGRAMME_MONITORING, DataCategory.AGGREGATE), {"subject_geo": GEO}, "allow_transformed"),
    ("state aggregate", req(Role.STATE, ScopeLevel.STATE, "S1", Purpose.PROGRAMME_MONITORING, DataCategory.AGGREGATE), {"subject_geo": GEO}, "allow_transformed"),
    ("public dp aggregate", req(Role.PUBLIC, ScopeLevel.NATIONAL, "IN", Purpose.PUBLIC_REPORTING, DataCategory.AGGREGATE), {"subject_geo": GEO}, "allow_transformed"),
    ("research approved", req(Role.RESEARCHER, ScopeLevel.NATIONAL, "IN", Purpose.RESEARCH, DataCategory.PSEUDONYMOUS_CHILD), {"subject_geo": GEO, "approval_id": "irb-1"}, "allow_transformed"),
    ("model training pseudo", req(Role.SYSTEM, ScopeLevel.NATIONAL, "IN", Purpose.MODEL_TRAINING, DataCategory.RISK_SCORE), {"subject_geo": GEO}, "allow_transformed"),
    ("deny aww other awc", req(Role.AWW, ScopeLevel.AWC, "AWC2", Purpose.SERVICE_DELIVERY, DataCategory.IDENTIFIED_CHILD), {"subject_geo": GEO}, "deny"),
    ("deny asha no task", req(Role.ASHA, ScopeLevel.AWC, "AWC1", Purpose.CARE_COORDINATION, DataCategory.IDENTIFIED_CHILD), {"subject_geo": GEO}, "deny"),
    ("deny anm no task", req(Role.ANM, ScopeLevel.AWC, "AWC1", Purpose.CARE_COORDINATION, DataCategory.IDENTIFIED_CHILD), {"subject_geo": GEO}, "deny"),
    ("deny researcher identified", req(Role.RESEARCHER, ScopeLevel.NATIONAL, "IN", Purpose.RESEARCH, DataCategory.IDENTIFIED_CHILD), {"subject_geo": GEO, "approval_id": "irb-1"}, "deny"),
    ("deny public pseudonymous", req(Role.PUBLIC, ScopeLevel.NATIONAL, "IN", Purpose.PUBLIC_REPORTING, DataCategory.PSEUDONYMOUS_CHILD), {"subject_geo": GEO}, "deny"),
    ("deny other purpose", req(Role.AWW, ScopeLevel.AWC, "AWC1", Purpose.OTHER, DataCategory.IDENTIFIED_CHILD), {"subject_geo": GEO}, "deny"),
    ("deny dpo identified no escalation", req(Role.DPO, ScopeLevel.DISTRICT, "D1", Purpose.PROGRAMME_MONITORING, DataCategory.IDENTIFIED_CHILD), {"subject_geo": GEO}, "deny"),
    ("deny health no consent", req(Role.AWW, ScopeLevel.AWC, "AWC1", Purpose.SERVICE_DELIVERY, DataCategory.HEALTH_RECORD), {"subject_geo": GEO}, "deny"),
    ("deny mo no task", req(Role.MO_PHC, ScopeLevel.PROJECT, "P1", Purpose.CARE_COORDINATION, DataCategory.IDENTIFIED_CHILD), {"subject_geo": GEO}, "deny"),
    ("deny researcher no approval", req(Role.RESEARCHER, ScopeLevel.NATIONAL, "IN", Purpose.RESEARCH, DataCategory.PSEUDONYMOUS_CHILD), {"subject_geo": GEO}, "deny"),
    ("deny model identified", req(Role.SYSTEM, ScopeLevel.NATIONAL, "IN", Purpose.MODEL_TRAINING, DataCategory.IDENTIFIED_CHILD), {"subject_geo": GEO}, "deny"),
    ("deny ls wrong sector", req(Role.LS, ScopeLevel.SECTOR, "SEC2", Purpose.SUPERVISION, DataCategory.PSEUDONYMOUS_CHILD), {"subject_geo": GEO}, "deny"),
]


def test_policy_cases():
    for name, access_req, context, expected in CASES:
        assert decide(access_req, context).decision == expected, name


def test_transforms_and_first_match():
    public = decide(req(Role.PUBLIC, ScopeLevel.NATIONAL, "IN", Purpose.PUBLIC_REPORTING, DataCategory.AGGREGATE), {"subject_geo": GEO})
    assert public.transform == "dp_noise"
    district = decide(req(Role.DPO, ScopeLevel.DISTRICT, "D1", Purpose.PROGRAMME_MONITORING, DataCategory.AGGREGATE), {"subject_geo": GEO})
    assert district.transform == "suppress_small_cells"
    other = decide(req(Role.PUBLIC, ScopeLevel.NATIONAL, "IN", Purpose.OTHER, DataCategory.AGGREGATE), {"subject_geo": GEO})
    assert other.rule_id == "deny-other-purpose"


def evaluate_suite() -> dict:
    false_allows = 0
    passed = 0
    for _, access_req, context, expected in CASES:
        decision = decide(access_req, context).decision
        passed += decision == expected
        false_allows += expected == "deny" and decision != "deny"
    result = {"pass_rate": round(passed / len(CASES), 4), "false_allows": false_allows, "n_cases": len(CASES)}
    print("POLICY_GATE_METRIC " + json.dumps(result, sort_keys=True))
    return result


def test_evaluate_suite_metric():
    metric = evaluate_suite()
    assert metric["pass_rate"] == 1.0
    assert metric["false_allows"] == 0
