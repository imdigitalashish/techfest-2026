# Builder A FLN components

## C2 canonical
`components/canonical` converts simulator/raw rows into the shared pydantic contracts (`School`, `Student`, `Response`) and pseudonymises raw child IDs with salted SHA-256 (`ps_` + 16 hex). Inputs are UDISE-like, roster, and classroom response rows; outputs are contract models with synthetic provenance. Baseline metric is contract validation pass/fail. Run `python3 -m pytest -q components/canonical`.

## C3 competency
`components/competency` defines an illustrative ASER-style reading and numeracy ladder in `framework.json` and loads simulator item banks as contract `Item` rows/Q-matrix. Inputs are the JSON framework and item-bank DataFrames; outputs are `Competency` and `Item` models. Baseline metric is framework/Q-matrix contract validity. Run `python3 -m pytest -q components/competency`.

## C4 diagnostics
`components/diagnostics` provides a deterministic ASER paper-tool rule, Bayesian 2PL IRT posterior scoring, and a simple CAT loop selecting informative items until confidence or item limits. Inputs are child response rows plus the item bank/thresholds; outputs are `ChildDiagnosis` models and CAT item IDs. Metrics are level accuracy, macro-F1, Brier score for meeting the goal, and mean CAT items. Run `python3 -m pytest -q components/diagnostics` and `python3 components/diagnostics/evaluate.py`.

## C7 teacher view
`components/teacher_view` turns diagnoses and a local roster into a `TeacherPlan`: TaRL groups by level, illustrative activity IDs from `activities.json`, WhatsApp/SMS text, and IVR script. Inputs are diagnoses, roster, week, channel, and language; output is a contract `TeacherPlan`. Metrics are payload byte size and SMS segment bounds. Run `python3 -m pytest -q components/teacher_view`.

## C12 governance
`components/governance` implements table-driven role/scope/purpose access decisions over `AccessRequest`, including child-data restrictions, audit-only raw responses, aggregate-only roles, and suppression for aggregate cells with `n<10`. Inputs are contract access requests; outputs are `AccessDecision`. Metric is policy table pass rate. Run `python3 -m pytest -q components/governance` and `python3 components/governance/evaluate.py`.
