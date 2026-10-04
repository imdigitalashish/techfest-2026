# action_router

Turns alerts into accountable tasks and escalates overdue work along a protocol ladder.

Input: list of `Alert` and a date. Output: list of `Task`; `close()` appends a `TaskTransition`.

Metric: `components/action_router/sim.py` prints one-line JSON labelled `SIMULATION — assumptions in sim.py`; the isolated metric is `metric_pct_within_sla`.

Run: `.venv/bin/python -m pytest components/action_router -q` or `.venv/bin/python -m components.action_router.sim`.

Assumptions: timelines are working assumptions pending verification against national CMAM protocol 2023 and are marked `(VERIFY)` in `protocol.yaml`.
