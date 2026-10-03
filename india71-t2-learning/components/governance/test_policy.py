import pytest
from architecture.contracts.fln_contracts import AccessRequest, AreaLevel, Role
from components.governance import decide

CASES = [
    ("teacher own child", "teacher", "S1", "child_diagnosis", "S1", "school", "remediation", True, "pseudonymise"),
    ("teacher other child", "teacher", "S1", "child_diagnosis", "S2", "school", "remediation", False, "suppress"),
    ("head own plan", "head_teacher", "S1", "teacher_plan", "S1", "school", "remediation", True, "none"),
    ("head other plan", "head_teacher", "S1", "teacher_plan", "S2", "school", "remediation", False, "suppress"),
    ("teacher own agg", "teacher", "S1", "area_estimate", "S1|n=30", "school", "planning", True, "aggregate"),
    ("teacher low n agg", "teacher", "S1", "area_estimate", "S1|n=8", "school", "planning", True, "suppress"),
    ("smc own", "smc", "S1", "area_estimate", "S1|n=40", "school", "planning", True, "aggregate"),
    ("smc other", "smc", "S1", "area_estimate", "S2|n=40", "school", "planning", False, "suppress"),
    ("crc cluster", "crc", "C1", "area_estimate", "C1|n=200", "cluster", "mentoring", True, "aggregate"),
    ("crc school in cluster", "crc", "C1", "trust_assessment", "C1/S1|n=20", "school", "mentoring", True, "aggregate"),
    ("crc other cluster", "crc", "C1", "area_estimate", "C2|n=200", "cluster", "mentoring", False, "suppress"),
    ("brc block", "brc", "B1", "area_estimate", "B1|n=900", "block", "planning", True, "aggregate"),
    ("brc cluster", "brc", "B1", "area_estimate", "B1/C1|n=90", "cluster", "planning", True, "aggregate"),
    ("brc outside", "brc", "B1", "area_estimate", "B2/C1|n=90", "cluster", "planning", False, "suppress"),
    ("deo district", "deo", "D1", "area_estimate", "D1|n=9000", "district", "planning", True, "aggregate"),
    ("deo block", "deo", "D1", "trust_assessment", "D1/B1|n=300", "block", "planning", True, "aggregate"),
    ("deo outside", "deo", "D1", "area_estimate", "D2|n=9000", "district", "planning", False, "suppress"),
    ("state state", "state", "ST", "area_estimate", "ST|n=100000", "state", "planning", True, "aggregate"),
    ("state district", "state", "ST", "area_estimate", "ST/D1|n=9000", "district", "planning", True, "aggregate"),
    ("state outside", "state", "ST", "area_estimate", "XX/D1|n=9000", "district", "planning", False, "suppress"),
    ("auditor selected raw", "auditor", "AUD", "raw_responses", "S1|audit_selected", "school", "audit", True, "none"),
    ("auditor not selected raw", "auditor", "AUD", "raw_responses", "S1", "school", "audit", False, "suppress"),
    ("auditor wrong purpose", "auditor", "AUD", "raw_responses", "S1|audit_selected", "school", "research", False, "suppress"),
    ("teacher raw denied", "teacher", "S1", "raw_responses", "S1|audit_selected", "school", "audit", False, "suppress"),
    ("low n cluster suppressed", "crc", "C1", "area_estimate", "C1|n=9", "cluster", "planning", True, "suppress"),
    ("low n district suppressed", "deo", "D1", "area_estimate", "D1|n=7", "district", "planning", True, "suppress"),
]

def build_request(case):
    _, role, actor, resource, target, level, purpose, allowed, transform = case
    return AccessRequest(role=Role(role), actor_scope=actor, resource=resource, target_scope=target, target_level=AreaLevel(level), purpose=purpose), allowed, transform

@pytest.mark.parametrize("case", CASES, ids=[c[0] for c in CASES])
def test_policy_table(case):
    req, exp_allowed, exp_transform = build_request(case)
    got = decide(req)
    assert (got.allowed, got.transform) == (exp_allowed, exp_transform)
