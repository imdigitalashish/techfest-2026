# Trust/audit autoresearch spike

Goal: improve the audit-calibrated measurement engine for synthetic FLN district data without peeking at hidden truth outside the evaluator.

Frozen metric: `block_mae_pp_at_10pct_budget` from `python3 components/trust_audit/autoresearch/eval.py` (lower is better).

Constraints:
- Only edit `components/trust_audit/*.py`, excluding `evaluate.py` and tests.
- Keep a change only if the metric improves beyond noise on seeds `1..5` and does not worsen held-out seeds `101..105`.
- Preserve contract validation for `TrustAssessment` outputs.
- Do not use hidden truth in risk scoring, audit selection, or adjustment except via the simulated `retest` function.

Idea backlog:
- Better forensic risk features: impossible transitions, class-size heaping, subject disagreement, item-level residuals.
- Model-assisted estimators (GREG/MRP) combining audit retests with UDISE+ covariates.
- Optimal inclusion probabilities under fixed audit budgets.
- Two-phase sampling: first schools, then children per school based on risk and enrolment.
- Child-level vs school-level retest allocation trade-offs.
