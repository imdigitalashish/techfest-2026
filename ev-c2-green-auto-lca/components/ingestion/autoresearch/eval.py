"""FROZEN evaluator for the quote verifier (spike A, C3). The loop never edits this file.

Gold positives: every `verified` record in data/factors/*.yaml whose source has a local PDF copy.
Negatives: the same quotes with one digit changed (each digit d -> (d+1) % 10 at the first digit position, and
separately at the last digit position) — a verifier that accepts these would let wrong numbers through.
Scalar: found_rate on positives, reported as 0 if false_accept_rate > 0 (fail-closed requirement).

Run (from ev-c2-green-auto-lca/): python3 components/ingestion/autoresearch/eval.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "components" / "ingestion"))
import verifier  # noqa: E402


def perturb(q: str, which: str) -> str | None:
    digits = [m.start() for m in re.finditer(r"\d", q)]
    if not digits:
        return None
    i = digits[0] if which == "first" else digits[-1]
    return q[:i] + str((int(q[i]) + 1) % 10) + q[i + 1:]


def main() -> None:
    sources = {s["id"]: s for f in (ROOT / "data/sources").glob("*.yaml") for s in yaml.safe_load(f.read_text())}
    gold = []
    for f in sorted((ROOT / "data/factors").glob("*.yaml")):
        for r in yaml.safe_load(f.read_text()):
            src = sources.get(r["source_id"], {})
            lc = src.get("local_copy", "")
            if r["status"] == "verified" and lc.endswith(".pdf") and (ROOT / lc).exists():
                gold.append((r["id"], r["quote"], lc))
    found, fa, neg = 0, 0, 0
    misses = []
    for rid, q, lc in gold:
        text = verifier.load_text(lc)
        if verifier.quote_found(q, text):
            found += 1
        else:
            misses.append(rid)
        for which in ("first", "last"):
            pq = perturb(q, which)
            if pq and pq != q:
                neg += 1
                fa += int(verifier.quote_found(pq, text))
    found_rate = found / len(gold) if gold else 0.0
    false_accept = fa / neg if neg else 0.0
    scalar = found_rate if fa == 0 else 0.0
    print(json.dumps({"scalar": round(scalar, 4), "found_rate": round(found_rate, 4), "n_positive": len(gold),
                      "false_accept_rate": round(false_accept, 4), "n_negative": neg,
                      "verifier_version": verifier.VERSION, "misses": misses}))


if __name__ == "__main__":
    main()
