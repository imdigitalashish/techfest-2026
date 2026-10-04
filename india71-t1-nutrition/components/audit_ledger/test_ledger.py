from __future__ import annotations

import json
import random

from components.audit_ledger.ledger import Ledger


def _filled(n=1000) -> Ledger:
    ledger = Ledger()
    for i in range(n):
        ledger.append("actor", "read", f"child:{i}", decision_ref=f"d:{i}")
    return ledger


def test_append_1000_and_verify_round_trip():
    ledger = _filled()
    ok, first_bad = ledger.verify()
    assert ok and first_bad is None
    clone = Ledger.from_jsonl(ledger.to_jsonl())
    assert clone.verify() == (True, None)


def _mutate(ledger: Ledger, rng: random.Random) -> Ledger:
    clone = Ledger.from_jsonl(ledger.to_jsonl())
    kind = rng.choice(["change", "delete", "reorder"])
    if kind == "change":
        idx = rng.randrange(len(clone.entries))
        clone.entries[idx] = clone.entries[idx].model_copy(update={"object_ref": clone.entries[idx].object_ref + ":tampered"})
    elif kind == "delete":
        del clone.entries[rng.randrange(len(clone.entries))]
    else:
        idx = rng.randrange(len(clone.entries) - 1)
        clone.entries[idx], clone.entries[idx + 1] = clone.entries[idx + 1], clone.entries[idx]
    return clone


def test_mutations_detected():
    ledger = _filled()
    assert not _mutate(ledger, random.Random(1)).verify()[0]
    deleted = Ledger.from_jsonl(ledger.to_jsonl())
    del deleted.entries[10]
    assert deleted.verify()[0] is False
    reordered = Ledger.from_jsonl(ledger.to_jsonl())
    reordered.entries[20], reordered.entries[21] = reordered.entries[21], reordered.entries[20]
    assert reordered.verify()[0] is False


def evaluate_suite() -> dict:
    base = _filled()
    rng = random.Random(71)
    detected = 0
    for _ in range(100):
        detected += not _mutate(base, rng).verify()[0]
    result = {"tamper_detection_rate": detected / 100, "n_mutations": 100}
    print("AUDIT_LEDGER_METRIC " + json.dumps(result, sort_keys=True))
    return result


def test_metric():
    assert evaluate_suite()["tamper_detection_rate"] == 1.0
