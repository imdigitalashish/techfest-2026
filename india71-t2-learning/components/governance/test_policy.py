import pytest
from architecture.contracts.fln_contracts import AccessRequest, AreaLevel, Role
from components.governance import TrustedContext, decide

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
    ("crc school trust denied", "crc", "C1", "trust_assessment", "C1/S1|n=20", "school", "mentoring", False, "suppress"),
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
    ("auditor selected raw", "auditor", "AUD", "raw_responses", "S1|audit_selected", "school", "audit", True, "pseudonymise"),
    ("auditor not selected raw", "auditor", "AUD", "raw_responses", "S1", "school", "audit", False, "suppress"),
    ("auditor wrong purpose", "auditor", "AUD", "raw_responses", "S1|audit_selected", "school", "research", False, "suppress"),
    ("teacher raw denied", "teacher", "S1", "raw_responses", "S1|audit_selected", "school", "audit", False, "suppress"),
    ("low n cluster suppressed", "crc", "C1", "area_estimate", "C1|n=9", "cluster", "planning", True, "suppress"),
    ("low n district suppressed", "deo", "D1", "area_estimate", "D1|n=7", "district", "planning", True, "suppress"),
    ("auditor school trust audit", "auditor", "AUD", "trust_assessment", "S1|audit_selected|n=25", "school", "audit", True, "none"),
    ("auditor school trust unselected denied", "auditor", "AUD", "trust_assessment", "S2|n=25", "school", "audit", False, "suppress"),
    ("auditor school trust planning denied", "auditor", "AUD", "trust_assessment", "S1|n=25", "school", "planning", False, "suppress"),
    ("state school trust planning", "state", "ST", "trust_assessment", "ST/D1/B1/C1/S1|n=25", "school", "planning", True, "none"),
    ("state school trust audit", "state", "ST", "trust_assessment", "ST/D1/B1/C1/S1|n=25", "school", "audit", True, "none"),
    ("state school trust research denied", "state", "ST", "trust_assessment", "ST/D1/B1/C1/S1|n=25", "school", "research", False, "suppress"),
    ("teacher school trust denied", "teacher", "S1", "trust_assessment", "S1|n=25", "school", "planning", False, "suppress"),
    ("head school trust denied", "head_teacher", "S1", "trust_assessment", "S1|n=25", "school", "planning", False, "suppress"),
    ("smc school trust denied", "smc", "S1", "trust_assessment", "S1|n=25", "school", "planning", False, "suppress"),
    ("brc school trust denied", "brc", "B1", "trust_assessment", "B1/C1/S1|n=25", "school", "planning", False, "suppress"),
    ("deo school trust denied", "deo", "D1", "trust_assessment", "D1/B1/C1/S1|n=25", "school", "planning", False, "suppress"),
]

def _server_context(target: str) -> TrustedContext:
    """Test harness only: legacy '|audit_selected' / '|n=K' annotations in CASES describe the SERVER-SIDE
    registry and counts for that case. decide() itself ignores annotations in the request text."""
    tid, *ann = target.split("|")
    leaf = tid.split("/")[-1]
    sel = frozenset([leaf]) if "audit_selected" in ann else frozenset()
    counts = {tid: int(a[2:]) for a in ann if a.startswith("n=")}
    return TrustedContext(audit_selected=sel, cell_counts=counts)


def build_request(case):
    _, role, actor, resource, target, level, purpose, allowed, transform = case
    req = AccessRequest(role=Role(role), actor_scope=actor, resource=resource, target_scope=target, target_level=AreaLevel(level), purpose=purpose)
    return req, _server_context(target), allowed, transform


# Forged annotations in the request text must never grant access (code-review issue 1, gpt-6-sol).
ADVERSARIAL = [
    # name, role, actor, resource, target (as sent by caller), level, purpose, server audit registry, server counts, allowed, transform
    ("forged selected=false", "auditor", "AUD", "raw_responses", "S1|selected_for_audit=false", "school", "audit", frozenset(), {}, False, "suppress"),
    ("forged audit_selected flag", "auditor", "AUD", "raw_responses", "S9|audit_selected", "school", "audit", frozenset({"S1"}), {}, False, "suppress"),
    ("forged flag on trust data", "auditor", "AUD", "trust_assessment", "S9|audit_selected", "school", "audit", frozenset({"S1"}), {}, False, "suppress"),
    ("forged large n", "deo", "D1", "area_estimate", "D1/B1|n=500", "block", "planning", frozenset(), {"D1/B1": 8}, True, "suppress"),
    ("missing trusted count", "brc", "B1", "area_estimate", "B1|n=900", "block", "planning", frozenset(), {}, True, "suppress"),
]


def build_adversarial(case):
    _, role, actor, resource, target, level, purpose, sel, counts, allowed, transform = case
    req = AccessRequest(role=Role(role), actor_scope=actor, resource=resource, target_scope=target, target_level=AreaLevel(level), purpose=purpose)
    return req, TrustedContext(audit_selected=sel, cell_counts=counts), allowed, transform


@pytest.mark.parametrize("case", ADVERSARIAL, ids=[c[0] for c in ADVERSARIAL])
def test_forged_annotations_never_grant_access(case):
    req, ctx, exp_allowed, exp_transform = build_adversarial(case)
    got = decide(req, ctx)
    assert (got.allowed, got.transform) == (exp_allowed, exp_transform)


@pytest.mark.parametrize("case", CASES, ids=[c[0] for c in CASES])
def test_policy_table(case):
    req, ctx, exp_allowed, exp_transform = build_request(case)
    got = decide(req, ctx)
    assert (got.allowed, got.transform) == (exp_allowed, exp_transform)


def test_school_level_trust_denial_reason():
    req = AccessRequest(
        role=Role.CRC,
        actor_scope="C1",
        resource="trust_assessment",
        target_scope="C1/S1|n=25",
        target_level=AreaLevel.SCHOOL,
        purpose="mentoring",
    )
    got = decide(req, TrustedContext(cell_counts={"C1/S1": 25}))
    assert not got.allowed
    assert got.reason == "non-punitive moderation: school-level trust data restricted to the moderation team"
