"""Canonical JSON + SHA-256, byte-identical to the browser verifier (dashboard/site/ledger_verify.js).

Canonical form (RFC 8785 / JCS subset): object keys sorted by UTF-16 code units, no whitespace,
strings as JSON.stringify writes them, numbers as ECMAScript Number::toString writes them.
Python's repr() already yields the shortest round-trip digits; only the layout differs from JS,
so `_num` re-lays those digits out with the ECMAScript rules.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any

GENESIS_HASH = "0" * 64


def _num(x: float | int) -> str:
    if isinstance(x, bool):
        raise TypeError("bool is not a number")
    if isinstance(x, int):
        if abs(x) > 2**53:
            raise ValueError("integer outside the IEEE-754 exact range")
        return str(x)
    if not math.isfinite(x):
        raise ValueError("NaN/Infinity are not valid canonical JSON")
    if x == 0:
        return "0"
    if x.is_integer() and abs(x) < 2**53:
        return str(int(x))
    mant, _, exp_s = repr(abs(x)).partition("e")
    ip, _, fp = mant.partition(".")
    digits = (ip + fp).lstrip("0")
    s = digits.rstrip("0")
    k = len(s)
    n = k + (int(exp_s) if exp_s else 0) - len(fp) + (len(digits) - k)
    if k <= n <= 21:
        out = s + "0" * (n - k)
    elif 0 < n <= 21:
        out = s[:n] + "." + s[n:]
    elif -6 < n <= 0:
        out = "0." + "0" * (-n) + s
    else:
        e = n - 1
        out = (s if k == 1 else s[0] + "." + s[1:]) + "e" + ("+" if e >= 0 else "-") + str(abs(e))
    return ("-" if x < 0 else "") + out


def canonical_json(obj: Any) -> str:
    if obj is None:
        return "null"
    if obj is True:
        return "true"
    if obj is False:
        return "false"
    if isinstance(obj, (int, float)):
        return _num(obj)
    if isinstance(obj, str):
        return json.dumps(obj, ensure_ascii=False)
    if isinstance(obj, (list, tuple)):
        return "[" + ",".join(canonical_json(v) for v in obj) + "]"
    if isinstance(obj, dict):
        keys = sorted(obj, key=lambda k: k.encode("utf-16-be"))
        return "{" + ",".join(json.dumps(k, ensure_ascii=False) + ":" + canonical_json(obj[k]) for k in keys) + "}"
    raise TypeError(f"not JSON-serialisable: {type(obj).__name__}")


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
