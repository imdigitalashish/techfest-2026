"""C10 Report: one primary decision target (review A3, re-score): the after-period policy contrast on observed traffic.

- The primary decision (worked / hurt / inconclusive) is taken ONLY on the after-period contrast D1, and ONLY if the
  overlap gate passes on the after-period logs behind its off-policy cell V(after, old). Otherwise: "cant_tell".
- The Shapley attribution (and the before-period contrast it needs) is reported as SECONDARY information when its own
  cell V(before, new) also passes the gate. It never replaces the primary decision.
- A sensitivity curve is attached only if it was computed for the same after-period contrast (Hajek-MSM).
"""
from __future__ import annotations

from architecture.contracts.contracts import SensitivityCurve, ShapleyDecomposition, Verdict
from components.report.gate import decide

AFTER, BEFORE = "V(after,old)", "V(before,new)"


def _f(x: float, scale: float, unit: str) -> str:
    return f"{x * scale:+.2f}{unit}"


def verdict(sh: ShapleyDecomposition, gate_diags: dict[str, dict], rule: dict, scale: float = 100.0,
            unit: str = " points", sensitivity: SensitivityCurve | None = None) -> Verdict:
    why = {c: decide(d, rule)[1] for c, d in gate_diags.items()}
    ok = {c: not r for c, r in why.items()}
    fmt = lambda iv: f"{_f(iv.point, scale, unit)} [{_f(iv.lo, scale, unit)}, {_f(iv.hi, scale, unit)}]"
    head = f"Dashboard moved {_f(sh.naive, scale, unit)}. "
    if not ok.get(AFTER, False):
        head += f"Primary (after-period contrast): can't tell from these logs ({AFTER}: {', '.join(why.get(AFTER, ['not gated']))})."
        if ok.get(BEFORE, False):
            head += f" Secondary, not a decision: before-period contrast {fmt(sh.effect_before)}."
        return Verdict(decision="cant_tell", headline=head, shapley=sh, diagnostics={"gate": gate_diags, "rule": rule})
    d1 = sh.effect_after
    decision = "worked" if d1.lo > 0 else "hurt" if d1.hi < 0 else "inconclusive"
    head += f"Primary (after-period contrast): {fmt(d1)}."
    if ok.get(BEFORE, False):
        head += f" Secondary: Shapley policy {fmt(sh.policy)}, environment {_f(sh.env, scale, unit)}, interaction {fmt(sh.interaction)}."
    else:
        head += " Secondary Shapley attribution not estimable (" + ", ".join(why.get(BEFORE, ["not gated"])) + ")."
    if sensitivity is not None and sensitivity.gamma_star is not None:
        head += f" After-period Hajek-MSM: the interval first includes zero at tested Γ = {sensitivity.gamma_star:g}."
    return Verdict(decision=decision, headline=head, shapley=sh, sensitivity=sensitivity,
                   diagnostics={"gate": gate_diags, "rule": rule, "decided_on": "after-period contrast"})
