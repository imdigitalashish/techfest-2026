from __future__ import annotations

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
    subject_id = _scope_id_for(req.actor_scope_level, geo, req.subject_scope_id)
    if relation in {"contains", "same"}:
        return subject_id is not None and req.actor_scope_id == subject_id
    return False


def _requires_match(rule: dict[str, Any], req: AccessRequest, context: dict[str, Any]) -> bool:
    requirements = rule.get("requires", {}) or {}
    for key, expected in requirements.items():
        if key == "consent_artefact_id":
            actual = req.consent_artefact_id
        else:
            actual = context.get(key)
        if expected == "present" and not actual:
            return False
        if expected == "missing" and actual:
            return False
        if isinstance(expected, bool) and bool(actual) is not expected:
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


def decide(req: AccessRequest, context: dict[str, Any]) -> AccessDecision:
    """Return the first matching policy decision, defaulting to deny."""
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
