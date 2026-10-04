# policy_gate

Purpose-bound access control as policy-as-code.

Input: `AccessRequest` plus context (`subject_geo`, `has_open_task`, `escalated`, `approval_id`). Output: `AccessDecision`.

Metric: `evaluate_suite()` in `test_policy_gate.py` prints `POLICY_GATE_METRIC {pass_rate, false_allows, n_cases}`.

Run: `.venv/bin/python -m pytest components/policy_gate -q`

Assumptions: scope containment is evaluated against `context["subject_geo"]`. Legal citations are working placeholders and each is marked `(VERIFY)` for primary-text verification.
