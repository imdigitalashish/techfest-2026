"""Purpose-bound, role-scoped access decisions (C12).

Fail-closed: anything that grants access must come from a TRUSTED, server-side context, never from the
request text. `target_scope` is only an identifier path (e.g. "ST/D1/B1/C1/S1"); any annotations a caller
appends after "|" (such as "audit_selected" or "n=30") are ignored. The audit-selection registry and the
children-per-cell counts are supplied by the server in `TrustedContext`; an aggregate with no trusted count
is suppressed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from architecture.contracts.fln_contracts import AccessDecision, AccessRequest, AreaLevel, Role


@dataclass(frozen=True)
class TrustedContext:
    audit_selected: frozenset = frozenset()          # school ids selected for this round's independent re-test (server registry)
    cell_counts: Mapping[str, int] = field(default_factory=dict)  # children per target id, computed server-side


def _target_id(target: str) -> str:
    return target.split("|", 1)[0]


def _leaf(target: str) -> str:
    return _target_id(target).split("/")[-1]


def _in_scope(actor: str, target: str) -> bool:
    target = _target_id(target)
    return target == actor or target.startswith(actor + "/") or target.startswith(actor + ":")


def decide(req: AccessRequest, ctx: TrustedContext | None = None) -> AccessDecision:
    ctx = ctx or TrustedContext()
    tid = _target_id(req.target_scope)
    n = ctx.cell_counts.get(tid)
    if req.target_level != AreaLevel.SCHOOL and n is not None and n < 10:
        return AccessDecision(allowed=True, transform="suppress", reason="aggregate cell has fewer than 10 children")
    if req.resource == "raw_responses":
        ok = req.role == Role.AUDITOR and req.purpose == "audit" and _leaf(req.target_scope) in ctx.audit_selected
        return AccessDecision(allowed=ok, transform="pseudonymise" if ok else "suppress", reason="auditor raw response access requires a school in the server-side audit registry")
    if req.resource in ("child_diagnosis", "teacher_plan"):
        if req.role in (Role.TEACHER, Role.HEAD_TEACHER) and req.target_level == AreaLevel.SCHOOL and _in_scope(req.actor_scope, req.target_scope):
            return AccessDecision(allowed=True, transform="pseudonymise" if req.resource == "child_diagnosis" else "none", reason="school staff may use own-school child-level remediation data")
        return AccessDecision(allowed=False, transform="suppress", reason="child-level data limited to own school teachers/head teachers")
    if req.resource == "trust_assessment" and req.target_level == AreaLevel.SCHOOL:
        if req.role == Role.AUDITOR and req.purpose == "audit" and _leaf(req.target_scope) in ctx.audit_selected:
            return AccessDecision(allowed=True, transform="none", reason="school-level moderation data available to auditors for audit-selected schools")
        if req.role == Role.STATE and req.purpose in ("audit", "planning") and _in_scope(req.actor_scope, req.target_scope):
            return AccessDecision(allowed=True, transform="none", reason="school-level trust data available to the state moderation team")
        return AccessDecision(
            allowed=False,
            transform="suppress",
            reason="non-punitive moderation: school-level trust data restricted to the moderation team",
        )
    # Aggregate resources: fail closed without a trusted count.
    if n is None or n < 10:
        return AccessDecision(allowed=True, transform="suppress", reason="aggregate cell has fewer than 10 children or no trusted count")
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
