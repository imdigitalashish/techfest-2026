# action_router

Turns alerts into accountable tasks and escalates overdue work along a protocol ladder.

Input: list of `Alert` and a date. Output: list of `Task`; `close()` appends a `TaskTransition`.

Metric: `components/action_router/sim.py` prints one-line JSON labelled `SIMULATION — assumptions in sim.py`; the isolated metric is `metric_pct_within_sla`.

Run: `.venv/bin/python -m pytest components/action_router -q` or `.venv/bin/python -m components.action_router.sim`.

Assumptions: `protocol.yaml` v0.2.0: official steps cite the CMAM Protocol 2023 (MWCD + MoHFW) page numbers, verified in `research/sources/V3-lead-verified-nfsa-abdm-cmam.md`; rules marked `DESIGN` are Poshan Setu operating choices, not official norms. The ops simulation (`sim.py`) uses illustrative assumptions.
