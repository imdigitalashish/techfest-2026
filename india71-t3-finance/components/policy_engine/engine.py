"""C5 Consent, Purpose & Policy Engine — deny by default; every decision is written to a hash-chained audit log.

decide(AccessRequest) -> AccessDecision (contracts.py). Rules are data (RULES / DENY_RULES below); each cites the
verified source it rests on (research/landscape.md [P*]). The legal mapping is the project's reading, pending legal
review; the engine makes that reading explicit, testable and auditable.
"""
from __future__ import annotations

import hashlib
import json

GRAN_ORDER = ["account", "person", "bc_area", "branch", "block", "district", "state", "national"]  # fine -> coarse
PERSON_LEVEL_DATA = {"account_ledger", "kyc_status", "account_usage_state", "person_usage_state", "target_list"}
AGGREGATE_DATA = {"aggregate_usage_rates", "gender_gap", "effect_estimates", "implementer_scores"}
STAT_PURPOSES = {"accountability_statistics", "research"}

# Explicit denials, checked first (they override any allow rule).
DENY_RULES = [
    ("D1", lambda r: "biometrics" in r["data_elements"], "Core biometric information may never be shared (Aadhaar Act s.29(1)) [P15]"),
    ("D2", lambda r: "aadhaar_number" in r["data_elements"], "Aadhaar numbers stay in the Aadhaar Data Vault; systems use reference keys (UIDAI Circular 14/2025) [P16]"),
    ("D3", lambda r: r["purpose"] in STAT_PURPOSES and (set(r["data_elements"]) & PERSON_LEVEL_DATA or r["granularity"] in ("account", "person")),
     "Statistical/research processing may not use person-level data for person-specific decisions (DPDP s.17(2)(b); Rules r.16) [P13, P23]"),
    ("D4", lambda r: r["requester_role"] not in ("bank", "bc") and (set(r["data_elements"]) & PERSON_LEVEL_DATA or r["granularity"] in ("account", "person")),
     "Person- and account-level data never leave the account-holding bank and its BC (governance matrix)"),
    ("D5", lambda r: r["requester_role"] in ("bank", "bc") and r["granularity"] in ("account", "person") and not r["own_customers_only"],
     "A bank or BC may see person-level data only for the bank's own customers"),
]

# Allow rules: (id, roles, purposes, data elements allowed, finest granularity allowed, obligations, basis)
RULES = [
    ("A1", {"bank"}, {"targeting", "outreach", "fraud_prevention"}, PERSON_LEVEL_DATA, "account",
     {"retention_days": 90, "masked_fields": ["aadhaar_number"]},
     "Banks must review accounts without customer-induced transactions and contact or trace holders (RBI/2023-24/105) [P8]; own customers only"),
    ("A2", {"bc"}, {"outreach"}, {"target_list"}, "person",
     {"retention_days": 30, "masked_fields": ["balance", "aadhaar_number", "transaction_history"]},
     "BC acts for the account-holding bank; task list with reason codes only (least privilege)"),
    ("A3", {"dfs", "rbi", "slbc", "ldm", "state_govt"}, {"accountability_statistics"}, AGGREGATE_DATA, "bc_area",
     {"dp_epsilon": 1.0, "min_cell_size": 20, "retention_days": 365},
     "Aggregate statistics under DPDP s.17(2)(b) and Rules r.16 Second Schedule standards [P13, P23]; differential privacy (C11)"),
    ("A4", {"researcher"}, {"research"}, AGGREGATE_DATA, "district",
     {"dp_epsilon": 1.0, "min_cell_size": 20, "retention_days": 365},
     "Research on aggregates under DPDP s.17(2)(b) and Rules r.16 [P13, P23]"),
    ("A5", {"public"}, {"accountability_statistics"}, AGGREGATE_DATA, "state",
     {"dp_epsilon": 1.0, "min_cell_size": 20},
     "Public state-level usage page (governance matrix)"),
]


def _finer(g: str, limit: str) -> bool:
    return GRAN_ORDER.index(g) < GRAN_ORDER.index(limit)


def decide(req: dict) -> dict:
    """req: AccessRequest fields as a dict. Returns AccessDecision fields as a dict."""
    for rid, test, why in DENY_RULES:
        if test(req):
            return {"request_id": req["request_id"], "allow": False, "obligations": {"masked_fields": []}, "rule_ids": [rid], "reason": why}
    for rid, roles, purposes, data, finest, obligations, basis in RULES:
        if (req["requester_role"] in roles and req["purpose"] in purposes and set(req["data_elements"]) <= data
                and not _finer(req["granularity"], finest)):
            ob = {"masked_fields": [], **obligations}
            return {"request_id": req["request_id"], "allow": True, "obligations": ob, "rule_ids": [rid], "reason": basis}
    return {"request_id": req["request_id"], "allow": False, "obligations": {"masked_fields": []}, "rule_ids": ["DEFAULT_DENY"],
            "reason": "No rule allows this role, purpose, data and granularity"}


class AuditLog:
    """Append-only, hash-chained log: entry_hash = sha256(prev_hash || seq || request_id || decision || payload_sha256)."""

    GENESIS = "0" * 64

    def __init__(self):
        self.entries: list[dict] = []

    @staticmethod
    def _h(prev: str, seq: int, rid: str, decision: bool, payload: str) -> str:
        return hashlib.sha256(f"{prev}|{seq}|{rid}|{int(decision)}|{payload}".encode()).hexdigest()

    def append(self, req: dict, dec: dict) -> dict:
        prev = self.entries[-1]["entry_hash"] if self.entries else self.GENESIS
        payload = hashlib.sha256(json.dumps({"req": req, "dec": dec}, sort_keys=True).encode()).hexdigest()
        seq = len(self.entries)
        e = {"seq": seq, "request_id": req["request_id"], "decision": dec["allow"], "payload_sha256": payload,
             "prev_hash": prev, "entry_hash": self._h(prev, seq, req["request_id"], dec["allow"], payload)}
        self.entries.append(e)
        return e

    def checkpoint(self) -> dict:
        """Head of the chain, to be published outside the operator's control (e.g. to RBI/SLBC or a transparency
        log). Without it a hash chain cannot detect deletion of its newest entries (tail truncation)."""
        return {"length": len(self.entries), "head": self.entries[-1]["entry_hash"] if self.entries else self.GENESIS}

    @classmethod
    def verify(cls, entries: list[dict], checkpoint: dict | None = None) -> bool:
        if checkpoint is not None:
            if len(entries) < checkpoint["length"]:
                return False
            if checkpoint["length"] and entries[checkpoint["length"] - 1]["entry_hash"] != checkpoint["head"]:
                return False
        prev = cls.GENESIS
        for i, e in enumerate(entries):
            if e["seq"] != i or e["prev_hash"] != prev:
                return False
            if e["entry_hash"] != cls._h(prev, e["seq"], e["request_id"], e["decision"], e["payload_sha256"]):
                return False
            prev = e["entry_hash"]
        return True
