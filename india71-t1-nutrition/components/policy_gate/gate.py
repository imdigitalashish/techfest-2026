from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml

from architecture.contracts.models import AccessDecision, AccessRequest, GeoUnit, ScopeLevel

POLICY_PATH = Path(__file__).with_name("policy.yaml")


def _load_policy() -> dict[str, Any]:
    with POLICY_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


_POLICY = _load_policy()
POLICY_VERSION = str(_POLICY.get("version", "0.1.0"))


def _value(value: Any) -> str:
    return getattr(value, "value", str(value))


def _geo(context: dict[str, Any]) -> GeoUnit | None:
    raw = context.get("subject_geo") or context.get("geo")
    if raw is None:
        return None
    if isinstance(raw, GeoUnit):
        return raw
    return GeoUnit.model_validate(raw)


# Actor role and scope must come from the authenticated session (IdP), not the request body; the gate
# additionally refuses role/scope-level combinations that cannot exist (e.g. an AWW with national scope).
ALLOWED_SCOPE_LEVELS = {
    "aww": {"awc"}, "asha": {"awc", "village"}, "anm": {"awc", "village", "sector"}, "ls": {"sector"},
    "cdpo": {"project"}, "mo_phc": {"project"}, "dpo": {"district"}, "dm": {"district"}, "state": {"state"},
    "public": {"national"}, "researcher": {"national", "state", "district"},
    "system": {"awc", "village", "sector", "project", "district", "state", "national"},
}
CHILD_LEVEL = {"identified_child", "pseudonymous_child", "risk_score", "health_record"}


def _valid_grant(registry_key: str, grant_id: str | None, req: AccessRequest, context: dict[str, Any]) -> bool:
    """A consent artefact / research approval counts only if a trusted registry vouches for it:
    same child (if child-specific), purpose covered, and not expired."""
    if not grant_id:
        return False
    registry = context.get(registry_key)
    if not isinstance(registry, dict) or grant_id not in registry:
        return False
    g = registry[grant_id]
    if g.get("child_key") not in (None, req.subject_child_key):
        return False
    if _value(req.purpose) not in set(g.get("purposes", [])):
        return False
    valid_until = g.get("valid_until")
    return isinstance(valid_until, date) and req.requested_at.date() <= valid_until


def _scope_id_for(level: ScopeLevel, geo: GeoUnit | None, subject_scope_id: str | None) -> str | None:
    if geo is None:
        return subject_scope_id
    return {
        ScopeLevel.AWC: geo.awc_code,
        ScopeLevel.VILLAGE: geo.village_code,
        ScopeLevel.SECTOR: geo.sector_code,
        ScopeLevel.PROJECT: geo.project_code,
        ScopeLevel.DISTRICT: geo.district_code,
        ScopeLevel.STATE: geo.state_code,
        ScopeLevel.NATIONAL: "IN",
    }[level]


def _scope_matches(req: AccessRequest, relation: str, context: dict[str, Any]) -> bool:
    if relation == "any":
        return True
    geo = _geo(context)
    if geo is None and _value(req.data_category) in CHILD_LEVEL:
        return False  # fail closed: child-level data needs trusted subject geography, never a request-supplied scope
    subject_id = _scope_id_for(req.actor_scope_level, geo, req.subject_scope_id)
    if relation in {"contains", "same"}:
        return subject_id is not None and req.actor_scope_id == subject_id
    return False


def _requires_match(rule: dict[str, Any], req: AccessRequest, context: dict[str, Any]) -> bool:
    requirements = rule.get("requires", {}) or {}
    for key, expected in requirements.items():
        if key == "consent_artefact_id":
            actual = _valid_grant("consent_registry", req.consent_artefact_id, req, context)
        elif key == "approval_id":
            actual = _valid_grant("approval_registry", context.get("approval_id"), req, context)
        else:
            actual = context.get(key)
        if expected == "present" and not actual:
            return False
        if expected == "missing" and actual:
            return False
        if isinstance(expected, bool) and actual is not expected:  # strict: the string "false" is not False/True
            return False
        if expected not in {"present", "missing", True, False} and actual != expected:
            return False
    return True


def _matches(rule: dict[str, Any], req: AccessRequest, context: dict[str, Any]) -> bool:
    return (
        _value(req.actor_role) in rule["roles"]
        and _value(req.purpose) in rule["purposes"]
        and _value(req.data_category) in rule["data_categories"]
        and _scope_matches(req, rule.get("scope", "contains"), context)
        and _requires_match(rule, req, context)
    )


def _decision(req: AccessRequest, rule: dict[str, Any]) -> AccessDecision:
    return AccessDecision(
        request_id=req.request_id,
        decision=rule["decision"],
        transform=rule.get("transform", "none"),
        legal_basis=rule.get("legal_basis"),
        rule_id=rule["id"],
        reason=rule.get("rationale", ""),
        policy_version=POLICY_VERSION,
    )


def _deny(req: AccessRequest, rule_id: str, reason: str) -> AccessDecision:
    return AccessDecision(request_id=req.request_id, decision="deny", transform="none", legal_basis=None,
                          rule_id=rule_id, reason=reason, policy_version=POLICY_VERSION)


def decide(req: AccessRequest, context: dict[str, Any]) -> AccessDecision:
    """Return the first matching policy decision, defaulting to deny."""
    if _value(req.actor_scope_level) not in ALLOWED_SCOPE_LEVELS.get(_value(req.actor_role), set()):
        return _deny(req, "deny-scope-level-mismatch", "Actor scope level is not valid for this role.")
    for rule in _POLICY["rules"]:
        if _matches(rule, req, context):
            return _decision(req, rule)
    default = _POLICY["default"]
    return AccessDecision(
        request_id=req.request_id,
        decision=default["decision"],
        transform=default.get("transform", "none"),
        legal_basis=default.get("legal_basis"),
        rule_id="default-deny",
        reason=default.get("rationale", "Default deny."),
        policy_version=POLICY_VERSION,
    )
