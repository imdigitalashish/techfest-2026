"""C5 Consent, Purpose & Policy Engine — deny by default; deciding and logging are one fail-closed operation.

PolicyEngine.request(AccessRequest) -> AccessDecision (contracts.py) decides AND appends a keyed, hash-chained audit
entry; if the append fails, the decision is a denial. Rules are data (DENY_RULES, RULES), each citing the verified
source it rests on (research/landscape.md [P*]). The legal mapping is the project's reading, pending legal review.

Limits (stated, not hidden): role and customer scope are taken from the request — in production they must come from
authenticated bank/BC identity; checkpoints must be published outside the operator's control (e.g. to RBI/SLBC or a
transparency log) — this skeleton only returns them; entries after the latest checkpoint are reported as unanchored.
"""
from __future__ import annotations

import hashlib
import hmac
import json

GRAN_ORDER = ["account", "person", "bc_area", "branch", "block", "district", "state", "national"]  # fine -> coarse
PERSON_LEVEL_DATA = {"account_ledger", "kyc_status", "account_usage_state", "person_usage_state", "target_list"}
AGGREGATE_DATA = {"aggregate_usage_rates", "gender_gap", "effect_estimates", "implementer_scores"}
STAT_PURPOSES = {"accountability_statistics", "research"}
FORUM_ROLES = {"dfs", "rbi", "slbc", "ldm", "state_govt", "researcher", "public", "npci", "dbt_mission"}

DENY_RULES = [
    ("D0", lambda r: not str(r.get("legal_basis", "")).strip(), "No legal basis stated"),
    ("D1", lambda r: "biometrics" in r["data_elements"], "Core biometric information may never be shared (Aadhaar Act s.29(1)) [P15]"),
    ("D2", lambda r: "aadhaar_number" in r["data_elements"], "Aadhaar numbers stay in the Aadhaar Data Vault; systems use reference keys (UIDAI Circular 14/2025) [P16]"),
    ("D3", lambda r: r["purpose"] in STAT_PURPOSES and (set(r["data_elements"]) & PERSON_LEVEL_DATA or r["granularity"] in ("account", "person")),
     "Statistical/research processing may not use person-level data for person-specific decisions (DPDP s.17(2)(b); Rules r.16) [P13, P23]"),
    ("D4", lambda r: r["requester_role"] not in ("bank", "bc") and (set(r["data_elements"]) & PERSON_LEVEL_DATA or r["granularity"] in ("account", "person")),
     "Person- and account-level data never leave the account-holding bank and its BC (governance matrix)"),
    ("D5", lambda r: r["requester_role"] in ("bank", "bc") and not r["own_customers_only"],
     "A bank or BC may process data only of the bank's own customers, at any granularity"),
    ("D6", lambda r: r["requester_role"] in FORUM_ROLES and r["granularity"] == "bc_area",
     "No individual BC / BC Sakhi performance tables are released to forums or the public (no worker scores)"),
]

# Allow rules: (id, roles, purposes, data elements, finest granularity, accepted legal-basis codes, obligations, basis text)
RULES = [
    ("A1", {"bank"}, {"targeting", "outreach", "fraud_prevention"}, PERSON_LEVEL_DATA, "account",
     {"rbi_inoperative_review", "customer_consent"}, {"retention_days": 90, "masked_fields": ["aadhaar_number"]},
     "Banks must review accounts without customer-induced transactions and contact or trace holders (RBI/2023-24/105) [P8]"),
    ("A2", {"bc"}, {"outreach"}, {"target_list"}, "person",
     {"bank_bc_agreement"}, {"retention_days": 30, "masked_fields": ["balance", "aadhaar_number", "transaction_history"]},
     "BC acts for the account-holding bank (BC-facilitated re-KYC: RBI/2025-26/51, /52) [P24, P25]; task list with reason codes only"),
    ("A3", {"dfs", "rbi", "slbc", "ldm", "state_govt"}, {"accountability_statistics"}, AGGREGATE_DATA, "branch",
     {"dpdp_s17_2_b_statistics"}, {"dp_epsilon": 1.0, "min_cell_size": 20, "retention_days": 365},
     "Aggregate statistics under DPDP s.17(2)(b) and Rules r.16 Second Schedule standards [P13, P23]; differential privacy (C11)"),
    ("A4", {"researcher"}, {"research"}, AGGREGATE_DATA, "district",
     {"dpdp_s17_2_b_statistics"}, {"dp_epsilon": 1.0, "min_cell_size": 20, "retention_days": 365},
     "Research on aggregates under DPDP s.17(2)(b) and Rules r.16 [P13, P23]"),
    ("A5", {"public"}, {"accountability_statistics"}, AGGREGATE_DATA, "state",
     {"dpdp_s17_2_b_statistics"}, {"dp_epsilon": 1.0, "min_cell_size": 20},
     "Public state-level usage page (governance matrix)"),
]


def _finer(g: str, limit: str) -> bool:
    return GRAN_ORDER.index(g) < GRAN_ORDER.index(limit)


def _deny(req: dict, rid: str, why: str) -> dict:
    return {"request_id": req["request_id"], "allow": False, "obligations": {"masked_fields": []}, "rule_ids": [rid], "reason": why}


def _decide(req: dict) -> dict:
    for rid, test, why in DENY_RULES:
        if test(req):
            return _deny(req, rid, why)
    for rid, roles, purposes, data, finest, bases, obligations, text in RULES:
        if (req["requester_role"] in roles and req["purpose"] in purposes and set(req["data_elements"]) <= data
                and not _finer(req["granularity"], finest)):
            if req["legal_basis"] not in bases:
                return _deny(req, "D7", f"Legal basis '{req['legal_basis']}' does not match rule {rid} (accepted: {sorted(bases)})")
            return {"request_id": req["request_id"], "allow": True, "obligations": {"masked_fields": [], **obligations},
                    "rule_ids": [rid], "reason": text}
    return _deny(req, "DEFAULT_DENY", "No rule allows this role, purpose, data and granularity")


class AuditLog:
    """Append-only log; entry_hash = HMAC(key, prev_hash|seq|request_id|decision|payload_sha256)."""

    GENESIS = "0" * 64

    def __init__(self, key: bytes):
        self.key = key
        self.entries: list[dict] = []

    @staticmethod
    def _h(key: bytes, prev: str, seq: int, rid: str, decision: bool, payload: str) -> str:
        return hmac.new(key, f"{prev}|{seq}|{rid}|{int(decision)}|{payload}".encode(), hashlib.sha256).hexdigest()

    def append(self, req: dict, dec: dict) -> dict:
        prev = self.entries[-1]["entry_hash"] if self.entries else self.GENESIS
        payload = hashlib.sha256(json.dumps({"req": req, "dec": dec}, sort_keys=True).encode()).hexdigest()
        seq = len(self.entries)
        e = {"seq": seq, "request_id": req["request_id"], "decision": dec["allow"], "payload_sha256": payload,
             "prev_hash": prev, "entry_hash": self._h(self.key, prev, seq, req["request_id"], dec["allow"], payload)}
        self.entries.append(e)
        return e

    def checkpoint(self) -> dict:
        """Chain head to be published outside the operator's control; anchors every entry up to `length`."""
        return {"length": len(self.entries), "head": self.entries[-1]["entry_hash"] if self.entries else self.GENESIS}

    @classmethod
    def verify(cls, entries: list[dict], key: bytes, checkpoint: dict | None = None) -> dict:
        """{'valid': chain intact and keyed; 'anchored': entries covered by the checkpoint; 'unanchored': entries after
        it; 'full_integrity': valid with every entry anchored}."""
        prev, ok = cls.GENESIS, True
        for i, e in enumerate(entries):
            if e["seq"] != i or e["prev_hash"] != prev or \
                    e["entry_hash"] != cls._h(key, prev, e["seq"], e["request_id"], e["decision"], e["payload_sha256"]):
                ok = False
                break
            prev = e["entry_hash"]
        anchored = 0
        if checkpoint is not None:
            n = checkpoint["length"]
            if len(entries) < n or (n and entries[n - 1]["entry_hash"] != checkpoint["head"]):
                ok = False
            anchored = min(n, len(entries))
        return {"valid": ok, "anchored": anchored, "unanchored": len(entries) - anchored,
                "full_integrity": ok and checkpoint is not None and anchored == len(entries)}


class PolicyEngine:
    def __init__(self, key: bytes):
        self.log = AuditLog(key)

    def request(self, req: dict) -> dict:
        dec = _decide(req)
        try:
            self.log.append(req, dec)
        except Exception:  # fail closed: an unlogged decision is a denial
            return _deny(req, "AUDIT_FAIL", "Audit append failed")
        return dec
