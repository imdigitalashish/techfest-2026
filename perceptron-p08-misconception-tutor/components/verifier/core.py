"""Verifier: independent SymPy check of the answer key + targeting/discrimination checks."""
from __future__ import annotations

import re

import sympy

from architecture.contracts import Item, PredictedAnswer, VerificationReport
from components.bugs.school_math import decode, to_sympy

_SAFE = re.compile(r"^[0-9\s+\-*/(),Ratinol]*$")  # digits, operators, brackets and the word Rational only


class SympyVerifier:
    def verify(self, item: Item, predicted: list[PredictedAnswer]) -> VerificationReport:
        issues: list[str] = []
        toks = None
        try:
            toks = decode(item.params["tokens"]) if item.params.get("tokens") else None
        except Exception as exc:  # malformed encoding
            issues.append(f"bad tokens: {exc}")
        if toks is None:
            issues.append("no machine-readable expression")
        well_formed = bool(item.stem.strip()) and toks is not None
        key_ok, method = False, "none"
        if toks is not None:
            expr = to_sympy(toks)
            if not _SAFE.match(expr):
                issues.append("unsafe expression string")
            else:
                try:
                    val = sympy.sympify(expr, rational=True)
                    key_ok = bool(sympy.Rational(item.answer_key) == val)
                    method = "sympy"
                    if not key_ok:
                        issues.append(f"key mismatch: sympy={val} key={item.answer_key}")
                except (sympy.SympifyError, TypeError, ValueError, ZeroDivisionError) as exc:
                    issues.append(f"sympy failed: {exc}")
        if item.options:
            vals = [o.value for o in item.options]
            if len(set(vals)) != len(vals):
                issues.append("duplicate option values")
                well_formed = False
            keys = [o for o in item.options if o.is_key]
            if len(keys) != 1 or keys[0].value != item.answer_key:
                issues.append("options must contain exactly one key equal to answer_key")
                well_formed = False
        pv = {p.misconception_id: p.value for p in predicted}
        tgt = item.target_misconception_id
        target_val = pv.get(tgt) if tgt else None
        target_fires = tgt is None or (target_val is not None and target_val != item.answer_key)
        if tgt and not target_fires:
            issues.append("target misconception does not change the answer on this item")
        firing = [v for v in pv.values() if v is not None]
        discriminative = bool(firing) and len(set(firing)) == len(firing) and item.answer_key not in firing
        n_sep = 0
        if tgt and target_fires:
            n_sep = sum(1 for m, v in pv.items() if m != tgt and v is not None and v != target_val and firing.count(v) == 1)
        return VerificationReport(
            item_id=item.item_id, well_formed=well_formed, key_verified=key_ok, key_method=method,
            target_fires=target_fires, discriminative=discriminative, n_competitors_separated=n_sep, issues=issues,
        )
