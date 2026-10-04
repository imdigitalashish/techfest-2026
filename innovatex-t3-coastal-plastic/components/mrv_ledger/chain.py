"""Hash-chained evidence records (C11): append, verify, anchor, Ed25519 signatures.

entry.hash = sha256(canonical_json({"seq", "record", "reconciliation", "prev_hash"})) and
entry.prev_hash = previous entry's hash (GENESIS_HASH for seq 0). Any edit, deletion, insertion or
reordering breaks a recomputed hash or a link. Truncating the tail or rewriting the whole chain is
only detectable against an external anchor (a published head hash + length), so `verify` takes one.
Hashing makes records tamper-evident; it does not make what was recorded true.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Iterable, Optional

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from ._contracts import ClearanceRecord, LedgerEntry, Reconciliation
from .canonical import GENESIS_HASH, canonical_json, sha256_hex


def entry_hash(seq: int, record: ClearanceRecord, reconciliation: Reconciliation, prev_hash: str) -> str:
    body = {
        "seq": seq,
        "record": record.model_dump(mode="json"),
        "reconciliation": reconciliation.model_dump(mode="json"),
        "prev_hash": prev_hash,
    }
    return sha256_hex(canonical_json(body))


def append(entries: list[LedgerEntry], record: ClearanceRecord, reconciliation: Reconciliation) -> LedgerEntry:
    seq = len(entries)
    prev = entries[-1].hash if entries else GENESIS_HASH
    e = LedgerEntry(seq=seq, record=record, reconciliation=reconciliation, prev_hash=prev,
                    hash=entry_hash(seq, record, reconciliation, prev))
    entries.append(e)
    return e


def anchor(entries: list[LedgerEntry]) -> dict:
    """What gets published outside the ledger (e.g. committed to git, posted on the ward portal)."""
    return {"length": len(entries), "head_hash": entries[-1].hash if entries else GENESIS_HASH}


@dataclass
class VerifyResult:
    ok: bool
    checked: int
    problems: list[str] = field(default_factory=list)

    @property
    def first_bad(self) -> Optional[int]:
        for p in self.problems:
            if p.startswith("seq "):
                return int(p.split()[1].rstrip(":"))
        return None


def verify(entries: Iterable[LedgerEntry], expected_anchor: Optional[dict] = None) -> VerifyResult:
    entries = list(entries)
    problems: list[str] = []
    prev = GENESIS_HASH
    for i, e in enumerate(entries):
        if e.seq != i:
            problems.append(f"seq {i}: position holds seq={e.seq} (deleted, inserted or reordered)")
        if e.prev_hash != prev:
            problems.append(f"seq {i}: prev_hash does not link to the previous entry")
        if entry_hash(e.seq, e.record, e.reconciliation, e.prev_hash) != e.hash:
            problems.append(f"seq {i}: content does not match its hash (edited)")
        prev = e.hash
    if expected_anchor is not None:
        got = anchor(entries)
        if got["length"] != expected_anchor["length"]:
            problems.append(f"anchor: length {got['length']} != published {expected_anchor['length']}")
        if got["head_hash"] != expected_anchor["head_hash"]:
            problems.append("anchor: head hash differs from the published head (truncated or rewritten)")
    return VerifyResult(ok=not problems, checked=len(entries), problems=problems)


# ------------------------------------------------------------------ signatures ----
def demo_key(signer_id: str) -> Ed25519PrivateKey:
    """DEMO ONLY: deterministic key from a public seed. A deployment keeps keys in the device's secure element."""
    return Ed25519PrivateKey.from_private_bytes(hashlib.sha256(f"t3-demo-key:{signer_id}".encode()).digest())


def public_hex(key: Ed25519PrivateKey) -> str:
    return key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()


def sign_entry(entry: LedgerEntry, signer_id: str, key: Ed25519PrivateKey) -> dict:
    """Signature over the entry hash (UTF-8 hex). The hash commits to the record and the whole prefix."""
    return {"seq": entry.seq, "hash": entry.hash, "signer_id": signer_id, "public_key_hex": public_hex(key),
            "signature_hex": key.sign(entry.hash.encode()).hex()}


def verify_signatures(entries: list[LedgerEntry], signatures: list[dict], trusted_keys: dict[str, str],
                      delegations: Optional[dict[str, list[str]]] = None) -> VerifyResult:
    """trusted_keys: signer_id -> public key hex, distributed out of band (key registry).
    delegations: crew_id -> signer_ids allowed to sign that crew's records (e.g. a supervisor's device when the
    crew device fails); distributed with the key registry. Without an entry, only the record's own crew may sign.
    A signature counts only if its signer is the record's crew (or a delegate) and it covers this entry's hash."""
    delegations = delegations or {}
    problems: list[str] = []
    by_seq = {s["seq"]: s for s in signatures}
    for e in entries:
        s = by_seq.get(e.seq)
        if s is None:
            problems.append(f"seq {e.seq}: unsigned")
            continue
        pub = trusted_keys.get(s["signer_id"])
        if pub is None or pub != s["public_key_hex"]:
            problems.append(f"seq {e.seq}: signer {s['signer_id']} not in the key registry")
            continue
        crew = e.record.crew_id
        if s["signer_id"] != crew and s["signer_id"] not in delegations.get(crew, []):
            problems.append(f"seq {e.seq}: signer {s['signer_id']} is not crew {crew} and holds no delegation")
            continue
        if s.get("hash") != e.hash:
            problems.append(f"seq {e.seq}: signature is for a different hash")
            continue
        try:
            Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub)).verify(bytes.fromhex(s["signature_hex"]), e.hash.encode())
        except (InvalidSignature, ValueError):
            problems.append(f"seq {e.seq}: bad signature")
    return VerifyResult(ok=not problems, checked=len(entries), problems=problems)
