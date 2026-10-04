# frontline_worklist

Renders weekly frontline worklists from routed tasks.

Input: `Task` list, local beneficiary references, capacities, and week date. Output: `Worklist` records; SMS summaries contain no names and only local refs.

Metric: `evaluate_worklists()` prints `FRONTLINE_WORKLIST_METRIC {median_payload_bytes, pct_sms_le_160, n_worklists}`.

Run: `.venv/bin/python -m pytest components/frontline_worklist -q`

Assumptions: worker IDs are deterministic `role:scope_id`; English/Hindi reasons use simple action templates intended for product copy review.
