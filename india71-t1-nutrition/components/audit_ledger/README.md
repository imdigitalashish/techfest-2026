# audit_ledger

Tamper-evident append-only audit log.

Input: actor/action/object/decision references. Output: `AuditEntry` with a SHA-256 hash chained to the previous entry (`0` × 64 genesis hash).

Metric: tests run 100 random mutations and print `AUDIT_LEDGER_METRIC {tamper_detection_rate, n_mutations}`.

Run: `.venv/bin/python -m pytest components/audit_ledger -q`

Assumptions: canonical JSON is Pydantic JSON-mode fields without the `hash` field, sorted by key.
