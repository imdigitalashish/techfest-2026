"""C10 Report: turn a 2x2 Shapley decomposition + overlap-gate diagnostics into a decision a manager can act on.

Order of checks: (1) the gate on the logs behind each off-policy cell; any failure -> "cant_tell";
(2) the 95% interval of the Shapley policy term: excludes 0 -> "worked" / "hurt", else "inconclusive".
"""
from __future__ import annotations

from architecture.contracts.contracts import SensitivityCurve, ShapleyDecomposition, Verdict
from components.report.gate import decide


def _pp(x: float, scale: float, unit: str) -> str:
    return f"{x * scale:+.2f}{unit}"


def verdict(sh: ShapleyDecomposition, gate_diags: dict[str, dict], rule: dict, scale: float = 100.0,
            unit: str = " points", sensitivity: SensitivityCurve | None = None) -> Verdict:
    reasons = {cell: decide(d, rule)[1] for cell, d in gate_diags.items()}
    failed = {c: r for c, r in reasons.items() if r}
    base = (f"Dashboard moved {_pp(sh.naive, scale, unit)}: policy {_pp(sh.policy.point, scale, unit)} "
            f"[{_pp(sh.policy.lo, scale, unit)}, {_pp(sh.policy.hi, scale, unit)}], environment {_pp(sh.env, scale, unit)}, "
            f"interaction {_pp(sh.interaction.point, scale, unit)}.")
    if failed:
        why = "; ".join(f"{c}: {', '.join(r)}" for c, r in failed.items())
        return Verdict(decision="cant_tell", headline=f"Can't tell from these logs ({why}).", shapley=sh,
                       sensitivity=sensitivity, diagnostics={"gate": gate_diags, "rule": rule})
    if sh.policy.lo > 0:
        decision = "worked"
    elif sh.policy.hi < 0:
        decision = "hurt"
    else:
        decision = "inconclusive"
    if sensitivity is not None and sensitivity.gamma_star is not None and decision != "inconclusive":
        base += f" Overturned by hidden confounding at Γ = {sensitivity.gamma_star:g}."
    return Verdict(decision=decision, headline=base, shapley=sh, sensitivity=sensitivity,
                   diagnostics={"gate": gate_diags, "rule": rule})
