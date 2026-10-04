"""C10 Report: turn a 2x2 Shapley decomposition + overlap-gate diagnostics into a decision a manager can act on.

Each off-policy cell is gated on the logs it is estimated from:
  "V(after,old)"  (after-period logs)  -> needed for effect_after  (environment-first ordering)
  "V(before,new)" (before-period logs) -> needed for effect_before (policy-first ordering)
Both pass -> decide on the Shapley policy term (and report the interaction). Only one passes -> decide on that
ordering's effect and say the interaction is not estimable. Neither -> "cant_tell".
Decision: the term's 95% interval excludes 0 -> "worked" / "hurt"; otherwise "inconclusive".
"""
from __future__ import annotations

from architecture.contracts.contracts import Interval, SensitivityCurve, ShapleyDecomposition, Verdict
from components.report.gate import decide

AFTER, BEFORE = "V(after,old)", "V(before,new)"


def _f(x: float, scale: float, unit: str) -> str:
    return f"{x * scale:+.2f}{unit}"


def _decide(iv: Interval) -> str:
    return "worked" if iv.lo > 0 else "hurt" if iv.hi < 0 else "inconclusive"


def verdict(sh: ShapleyDecomposition, gate_diags: dict[str, dict], rule: dict, scale: float = 100.0,
            unit: str = " points", sensitivity: SensitivityCurve | None = None) -> Verdict:
    why = {c: decide(d, rule)[1] for c, d in gate_diags.items()}
    ok = {c: not r for c, r in why.items()}
    after_ok, before_ok = ok.get(AFTER, False), ok.get(BEFORE, False)
    fmt = lambda iv: f"{_f(iv.point, scale, unit)} [{_f(iv.lo, scale, unit)}, {_f(iv.hi, scale, unit)}]"
    head = f"Dashboard moved {_f(sh.naive, scale, unit)}. "
    if after_ok and before_ok:
        term, label = sh.policy, "Policy (Shapley)"
        head += (f"{label} {fmt(term)}; environment {_f(sh.env, scale, unit)}; "
                 f"interaction {fmt(sh.interaction)}.")
    elif after_ok or before_ok:
        term = sh.effect_after if after_ok else sh.effect_before
        label = "Policy effect in the after period" if after_ok else "Policy effect in the before period"
        failed = BEFORE if after_ok else AFTER
        head += f"{label} {fmt(term)}; interaction not estimable ({failed}: {', '.join(why[failed])})."
    else:
        reasons = "; ".join(f"{c}: {', '.join(r)}" for c, r in why.items() if r)
        return Verdict(decision="cant_tell", headline=head + f"Can't tell from these logs ({reasons}).", shapley=sh,
                       sensitivity=sensitivity, diagnostics={"gate": gate_diags, "rule": rule})
    decision = _decide(term)
    if sensitivity is not None and sensitivity.gamma_star is not None and decision != "inconclusive":
        head += f" Hidden confounding of Γ = {sensitivity.gamma_star:g} would overturn it."
    return Verdict(decision=decision, headline=head, shapley=sh, sensitivity=sensitivity,
                   diagnostics={"gate": gate_diags, "rule": rule, "decided_on": label})
