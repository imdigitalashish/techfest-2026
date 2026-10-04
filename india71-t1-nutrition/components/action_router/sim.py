from __future__ import annotations

import json
import random
import statistics
from dataclasses import dataclass
from datetime import date, timedelta

DEFAULT_ASSUMPTIONS = {
    "n_awcs": 20,
    "alerts_per_awc_per_week": 3,
    "role_weekly_capacity": {"aww": 20, "ls": 35, "mo_phc": 25, "cdpo": 25, "dpo": 40, "asha": 20},
    "completion_probability": 0.82,
    "weeks": 12,
    "seed": 71,
}


@dataclass
class SimTask:
    created: int
    due: int
    owner: str
    first_action: int | None = None
    done: bool = False
    escalated: bool = False


def _monthly_status_quo(rng: random.Random, assumptions: dict) -> dict:
    tasks: list[SimTask] = []
    for week in range(assumptions["weeks"]):
        for _ in range(assumptions["n_awcs"] * assumptions["alerts_per_awc_per_week"]):
            created = week * 7
            review_day = ((created // 30) + 1) * 30
            done = rng.random() < assumptions["completion_probability"]
            tasks.append(SimTask(created=created, due=created + 7, owner="meeting", first_action=review_day, done=done, escalated=review_day > created + 7))
    return _summarise(tasks)


def _weekly_ladder(rng: random.Random, assumptions: dict) -> dict:
    tasks: list[SimTask] = []
    capacity = assumptions["role_weekly_capacity"]
    for week in range(assumptions["weeks"]):
        backlog = [t for t in tasks if not t.done]
        by_owner: dict[str, list[SimTask]] = {}
        for t in backlog:
            by_owner.setdefault(t.owner, []).append(t)
        for owner, owner_tasks in by_owner.items():
            owner_tasks.sort(key=lambda t: (t.due, t.created))
            for t in owner_tasks[: capacity.get(owner, 10)]:
                if t.first_action is None:
                    t.first_action = week * 7
                t.done = rng.random() < assumptions["completion_probability"]
                if not t.done and week * 7 > t.due:
                    t.escalated = True
                    t.owner = "ls" if t.owner == "aww" else "cdpo"
        for _ in range(assumptions["n_awcs"] * assumptions["alerts_per_awc_per_week"]):
            created = week * 7
            tasks.append(SimTask(created=created, due=created + 7, owner="aww"))
    return _summarise(tasks)


def _summarise(tasks: list[SimTask]) -> dict:
    first_days = [(t.first_action if t.first_action is not None else t.created + 999) - t.created for t in tasks]
    within = [t.done and (t.first_action or 10**9) <= t.due for t in tasks]
    open_by_worker: dict[str, int] = {}
    for t in tasks:
        if not t.done:
            open_by_worker[t.owner] = open_by_worker.get(t.owner, 0) + 1
    return {
        "median_days_alert_to_first_action": statistics.median(first_days),
        "pct_done_within_sla": round(100 * sum(within) / len(tasks), 2),
        "pct_escalated": round(100 * sum(t.escalated for t in tasks) / len(tasks), 2),
        "max_open_tasks_per_worker": max(open_by_worker.values() or [0]),
    }


def run_simulation(**overrides) -> dict:
    assumptions = {**DEFAULT_ASSUMPTIONS, **overrides}
    rng_a = random.Random(assumptions["seed"])
    rng_b = random.Random(assumptions["seed"])
    result = {
        "label": "SIMULATION — assumptions in sim.py",
        "status_quo_monthly": _monthly_status_quo(rng_a, assumptions),
        "protocol_ladder_weekly": _weekly_ladder(rng_b, assumptions),
        "metric_pct_within_sla": None,
    }
    result["metric_pct_within_sla"] = result["protocol_ladder_weekly"]["pct_done_within_sla"]
    print(json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    run_simulation()
