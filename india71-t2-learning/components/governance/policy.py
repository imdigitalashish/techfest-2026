from __future__ import annotations

import re
from architecture.contracts.fln_contracts import AccessDecision, AccessRequest, AreaLevel, Role


def _in_scope(actor: str, target: str) -> bool:
    target = target.split("|", 1)[0]
    return target == actor or target.startswith(actor + "/") or target.startswith(actor + ":")


def _n(target: str) -> int | None:
    m = re.search(r"(?:^|[|;])n=(\d+)(?:$|[|;])", target)
    return int(m.group(1)) if m else None


def _audit_selected(target: str) -> bool:
    return "audit_selected" in target or "selected_for_audit" in target


def decide(req: AccessRequest) -> AccessDecision:
    n = _n(req.target_scope)
    if req.target_level != AreaLevel.SCHOOL and n is not None and n < 10:
        return AccessDecision(allowed=True, transform="suppress", reason="aggregate cell has fewer than 10 children")
    if req.resource == "raw_responses":
        ok = req.role == Role.AUDITOR and req.purpose == "audit" and _audit_selected(req.target_scope)
        return AccessDecision(allowed=ok, transform="none" if ok else "suppress", reason="auditor raw response access requires audit-selected school")
    if req.resource in ("child_diagnosis", "teacher_plan"):
        if req.role in (Role.TEACHER, Role.HEAD_TEACHER) and req.target_level == AreaLevel.SCHOOL and _in_scope(req.actor_scope, req.target_scope):
            return AccessDecision(allowed=True, transform="pseudonymise" if req.resource == "child_diagnosis" else "none", reason="school staff may use own-school child-level remediation data")
        return AccessDecision(allowed=False, transform="suppress", reason="child-level data limited to own school teachers/head teachers")
    if req.resource == "trust_assessment" and req.target_level == AreaLevel.SCHOOL:
        if req.role == Role.AUDITOR and req.purpose == "audit":
            return AccessDecision(allowed=True, transform="none", reason="school-level trust data available to moderation auditors")
        if req.role == Role.STATE and req.purpose in ("audit", "planning") and _in_scope(req.actor_scope, req.target_scope):
            return AccessDecision(allowed=True, transform="none", reason="school-level trust data available to the state moderation team")
        return AccessDecision(
            allowed=False,
            transform="suppress",
            reason="non-punitive moderation: school-level trust data restricted to the moderation team",
        )
    # Aggregate resources.
    if n is not None and n < 10:
        return AccessDecision(allowed=True, transform="suppress", reason="aggregate cell has fewer than 10 children")
    if req.role == Role.SMC:
        ok = req.target_level == AreaLevel.SCHOOL and _in_scope(req.actor_scope, req.target_scope)
        return AccessDecision(allowed=ok, transform="aggregate" if ok else "suppress", reason="SMC sees only own school aggregate")
    if req.role == Role.CRC:
        ok = req.target_level in (AreaLevel.SCHOOL, AreaLevel.CLUSTER) and _in_scope(req.actor_scope, req.target_scope)
        return AccessDecision(allowed=ok, transform="aggregate" if ok else "suppress", reason="CRC sees own cluster aggregates")
    if req.role == Role.BRC:
        ok = req.target_level in (AreaLevel.SCHOOL, AreaLevel.CLUSTER, AreaLevel.BLOCK) and _in_scope(req.actor_scope, req.target_scope)
        return AccessDecision(allowed=ok, transform="aggregate" if ok else "suppress", reason="BRC sees own block aggregates")
    if req.role == Role.DEO:
        ok = req.target_level in (AreaLevel.SCHOOL, AreaLevel.CLUSTER, AreaLevel.BLOCK, AreaLevel.DISTRICT) and _in_scope(req.actor_scope, req.target_scope)
        return AccessDecision(allowed=ok, transform="aggregate" if ok else "suppress", reason="DEO sees own district aggregates")
    if req.role == Role.STATE:
        ok = req.target_level in (AreaLevel.SCHOOL, AreaLevel.CLUSTER, AreaLevel.BLOCK, AreaLevel.DISTRICT, AreaLevel.STATE) and _in_scope(req.actor_scope, req.target_scope)
        return AccessDecision(allowed=ok, transform="aggregate" if ok else "suppress", reason="state sees scoped aggregates")
    if req.role in (Role.TEACHER, Role.HEAD_TEACHER):
        ok = req.target_level == AreaLevel.SCHOOL and _in_scope(req.actor_scope, req.target_scope)
        return AccessDecision(allowed=ok, transform="aggregate" if ok else "suppress", reason="school staff aggregate access scoped to own school")
    return AccessDecision(allowed=False, transform="suppress", reason="no matching policy grant")
