"""C7 Assemble & validate: build the internal Assessment and validate it against our own contracts.

The stdlib validator below covers ONLY the keywords our internal contracts use and raises on any other keyword
(fail-closed), so it can never silently pass an unfamiliar schema. The official output (10 Oct) needs an explicit
adapter Assessment -> official record and a standards-complete validator (or the organisers' checker); the internal
dry run is not evidence of official compliance.
"""
from __future__ import annotations

import json
from pathlib import Path

from .paths import resource

CONTRACTS = resource("contracts.schema.json", "architecture/contracts/contracts.schema.json")
_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}
SUPPORTED = {"$ref", "$schema", "$id", "$defs", "title", "description", "type", "enum", "required", "properties",
             "additionalProperties", "items", "minItems", "maxItems", "minimum", "maximum", "maxLength"}


def load_schema(path: Path = CONTRACTS) -> dict:
    return json.loads(Path(path).read_text())


def validate(inst, schema: dict, root: dict, path: str = "$") -> list[str]:
    """Minimal JSON Schema subset: $ref, type, enum, required, properties, additionalProperties(bool|schema),
    items, minItems, maxItems, minimum, maximum, maxLength."""
    unknown = set(schema) - SUPPORTED
    if unknown:
        raise NotImplementedError(f"internal validator does not implement {sorted(unknown)}; use a full JSON Schema validator")
    if "$ref" in schema:
        node = root
        for part in schema["$ref"].lstrip("#/").split("/"):
            node = node[part]
        return validate(inst, node, root, path)
    errs: list[str] = []
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        ok = False
        for t in types:
            if t == "integer":
                ok |= isinstance(inst, int) and not isinstance(inst, bool)
            elif t == "number":
                ok |= isinstance(inst, (int, float)) and not isinstance(inst, bool)
            else:
                ok |= isinstance(inst, _TYPES[t])
        if not ok:
            return [f"{path}: expected {types}, got {type(inst).__name__}"]
    if "enum" in schema and inst not in schema["enum"]:
        errs.append(f"{path}: {inst!r} not in {schema['enum']}")
    if isinstance(inst, (int, float)) and not isinstance(inst, bool):
        if "minimum" in schema and inst < schema["minimum"]:
            errs.append(f"{path}: {inst} < {schema['minimum']}")
        if "maximum" in schema and inst > schema["maximum"]:
            errs.append(f"{path}: {inst} > {schema['maximum']}")
    if isinstance(inst, str) and "maxLength" in schema and len(inst) > schema["maxLength"]:
        errs.append(f"{path}: longer than {schema['maxLength']}")
    if isinstance(inst, dict):
        for k in schema.get("required", []):
            if k not in inst:
                errs.append(f"{path}: missing {k}")
        props = schema.get("properties", {})
        for k, v in inst.items():
            if k in props:
                errs += validate(v, props[k], root, f"{path}.{k}")
            elif schema.get("additionalProperties") is False:
                errs.append(f"{path}: unexpected {k}")
            elif isinstance(schema.get("additionalProperties"), dict):
                errs += validate(v, schema["additionalProperties"], root, f"{path}.{k}")
    if isinstance(inst, list):
        if "minItems" in schema and len(inst) < schema["minItems"]:
            errs.append(f"{path}: fewer than {schema['minItems']} items")
        if "maxItems" in schema and len(inst) > schema["maxItems"]:
            errs.append(f"{path}: more than {schema['maxItems']} items")
        if "items" in schema:
            for i, v in enumerate(inst):
                errs += validate(v, schema["items"], root, f"{path}[{i}]")
    return errs


def assemble(doc, doc_type, decision, dist, evidence, gap, runtime_ms, versions, error=None) -> dict:
    return {"doc_id": doc["doc_id"], "doc_type": doc_type, "decision": decision, "distribution": dist,
            "evidence": evidence, "gap_analysis": gap, "runtime_ms": float(runtime_ms), "versions": versions,
            "error": error}


def check_assessment(a: dict, schema: dict | None = None) -> list[str]:
    s = schema or load_schema()
    return validate(a, {"$ref": "#/$defs/Assessment"}, s)
