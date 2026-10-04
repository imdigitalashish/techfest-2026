"""Semantic check (spike A, beyond quote presence): every `verified` scalar record's value must appear, as a whole
number, in its own quote (allowing x100 for % and x1000 for unit changes). Catches transcription errors where the quote
is real but the stored value is wrong. Records whose value is legitimately not in the quote must say why in `notes`
with the marker 'value-not-in-quote:'.

Run (from ev-c2-green-auto-lca/):  python3 components/ingestion/value_check.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "components" / "lca_engine"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from greenauto.db import FactorDB  # noqa: E402
import verifier  # noqa: E402


def check() -> tuple[int, list[str], list[str]]:
    db = FactorDB.load()
    n, bad, waived = 0, [], []
    for r in db.records.values():
        if r.status != "verified" or not r.is_scalar:
            continue
        n += 1
        if verifier.value_in_quote(float(r.value), r.quote):
            continue
        (waived if "value-not-in-quote:" in r.notes else bad).append(f"{r.id} value={r.value} quote={r.quote[:80]!r}")
    return n, bad, waived


if __name__ == "__main__":
    n, bad, waived = check()
    for b in bad:
        print("MISMATCH", b)
    for w in waived:
        print("waived  ", w)
    print(f"value_in_quote: {n - len(bad) - len(waived)}/{n} direct, {len(waived)} waived with reason, {len(bad)} mismatches")
    sys.exit(1 if bad else 0)
