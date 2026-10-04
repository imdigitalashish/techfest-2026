# policy_gate

Purpose-bound access control as policy-as-code.

Input: `AccessRequest` plus context (`subject_geo`, `has_open_task`, `escalated`, `approval_id`). Output: `AccessDecision`.

Metric: `evaluate_suite()` in `test_policy_gate.py` prints `POLICY_GATE_METRIC {pass_rate, false_allows, n_cases}`.

Run: `.venv/bin/python -m pytest components/policy_gate -q`

Assumptions: scope containment is evaluated against `context["subject_geo"]`. Legal citations (policy v0.2.0) are verified against primary texts: see `research/sources/V1-dpdp-verified.md` and `research/sources/V3-lead-verified-nfsa-abdm-cmam.md`. Purpose `employment_action` is always denied (ADR 002).
