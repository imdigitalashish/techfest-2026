from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from architecture.contracts.models import AuditEntry

ZERO_HASH = "0" * 64


def _canonical_payload(entry: AuditEntry, prev_hash: str | None = None) -> str:
    data = entry.model_dump(mode="json")
    data["prev_hash"] = entry.prev_hash if prev_hash is None else prev_hash
    data.pop("hash", None)
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def _hash_entry(entry: AuditEntry, prev_hash: str | None = None) -> str:
    payload = _canonical_payload(entry, prev_hash=prev_hash)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class Ledger:
    def __init__(self, entries: Iterable[AuditEntry] | None = None):
        self.entries = list(entries or [])

    def append(self, actor_id: str, action: str, object_ref: str, decision_ref: str | None = None) -> AuditEntry:
        prev_hash = self.entries[-1].hash if self.entries else ZERO_HASH
        entry = AuditEntry(
            seq=len(self.entries),
            ts=datetime.now(timezone.utc),
            actor_id=actor_id,
            action=action,
            object_ref=object_ref,
            decision_ref=decision_ref,
            prev_hash=prev_hash,
            hash=ZERO_HASH,
        )
        entry = entry.model_copy(update={"hash": _hash_entry(entry)})
        self.entries.append(entry)
        return entry

    def verify(self) -> tuple[bool, int | None]:
        expected_prev = ZERO_HASH
        for index, entry in enumerate(self.entries):
            if entry.seq != index or entry.prev_hash != expected_prev:
                return False, index
            expected_hash = _hash_entry(entry)
            if entry.hash != expected_hash:
                return False, index
            expected_prev = entry.hash
        return True, None

    def to_jsonl(self, path: str | Path | None = None) -> str:
        text = "\n".join(e.model_dump_json() for e in self.entries)
        if path is not None:
            Path(path).write_text(text + ("\n" if text else ""), encoding="utf-8")
        return text

    @classmethod
    def from_jsonl(cls, source: str | Path) -> "Ledger":
        if isinstance(source, Path) or (isinstance(source, str) and Path(source).exists() and "\n" not in source):
            text = Path(source).read_text(encoding="utf-8")
        else:
            text = str(source)
        entries = [AuditEntry.model_validate_json(line) for line in text.splitlines() if line.strip()]
        return cls(entries)
