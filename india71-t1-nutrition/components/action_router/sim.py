from __future__ import annotations

import json
import random
import statistics
from dataclasses import dataclass

# SIMULATION — every number below is an ASSUMPTION for illustration, not an estimate of real operations.
DEFAULT_ASSUMPTIONS = {
    "n_awcs": 20,
    "awcs_per_sector": 5,
    "alerts_per_awc_per_week": 3,
    "weekly_capacity": {"aww": 4, "ls": 6, "cdpo": 10},  # tasks each individual can close per week
    "completion_probability": 0.82,  # chance an attempted task is completed that week
    "sla_days": 7,
    "review_every_days": 30,  # status quo: alerts acted on only after the monthly sector/project review
    "weeks": 12,
    "seed": 71,
}


@dataclass
class SimTask:
    created: int
    due: int
    owner: str  # individual, e.g. "aww:3", "ls:0", "cdpo:0"
    first_action: int | None = None
    done_day: int | None = None
    escalated: bool = False


def _sector(awc: int, a: dict) -> int:
    return awc // a["awcs_per_sector"]


def _monthly_status_quo(rng: random.Random, a: dict) -> dict:
    """Alerts sit on a dashboard until the next monthly review, then go to the AWW."""
    tasks: list[SimTask] = []
    for week in range(a["weeks"]):
        for awc in range(a["n_awcs"]):
            for _ in range(a["alerts_per_awc_per_week"]):
                created = week * 7 + rng.randint(0, 6)
                review = ((created // a["review_every_days"]) + 1) * a["review_every_days"]
                done = review + (0 if rng.random() < a["completion_probability"] else 7)
                tasks.append(SimTask(created, created + a["sla_days"], f"aww:{awc}", first_action=review, done_day=done,
                                     escalated=False))
    return _summarise(tasks, a)


def _weekly_ladder(rng: random.Random, a: dict) -> dict:
    """Weekly worklists with per-person capacity; overdue tasks escalate AWW → LS (sector) → CDPO."""
    tasks: list[SimTask] = []
    cap = a["weekly_capacity"]
    for week in range(a["weeks"] + 4):  # 4 drain weeks without new alerts
        today = week * 7
        if week < a["weeks"]:
            for awc in range(a["n_awcs"]):
                for _ in range(a["alerts_per_awc_per_week"]):
                    created = today - rng.randint(0, 6) if week else today
                    tasks.append(SimTask(max(created, 0), max(created, 0) + a["sla_days"], f"aww:{awc}"))
        by_owner: dict[str, list[SimTask]] = {}
        for t in tasks:
            if t.done_day is None and t.created <= today:
                by_owner.setdefault(t.owner, []).append(t)
        for owner, items in by_owner.items():
            items.sort(key=lambda t: (t.due, t.created))
            role = owner.split(":")[0]
            for t in items[: cap[role]]:
                t.first_action = today if t.first_action is None else t.first_action
                if rng.random() < a["completion_probability"]:
                    t.done_day = today
            for t in items:
                if t.done_day is None and today > t.due and role != "cdpo":
                    t.escalated = True
                    t.owner = f"ls:{_sector(int(owner.split(':')[1]), a)}" if role == "aww" else "cdpo:0"
                    t.due = today + a["sla_days"]
    return _summarise(tasks, a)


def _summarise(tasks: list[SimTask], a: dict) -> dict:
    first = [(t.first_action if t.first_action is not None else t.created + 999) - t.created for t in tasks]
    close = [(t.done_day - t.created) for t in tasks if t.done_day is not None]
    return {
        "n_tasks": len(tasks),
        "median_days_alert_to_first_action": statistics.median(first),
        "median_days_alert_to_done": statistics.median(close) if close else None,
        "pct_done_within_sla": round(100 * sum(t.done_day is not None and t.done_day - t.created <= a["sla_days"]
                                                for t in tasks) / len(tasks), 2),
        "pct_escalated": round(100 * sum(t.escalated for t in tasks) / len(tasks), 2),
        "pct_never_done": round(100 * sum(t.done_day is None for t in tasks) / len(tasks), 2),
    }


def run_simulation(**overrides) -> dict:
    a = {**DEFAULT_ASSUMPTIONS, **overrides}
    result = {
        "label": "SIMULATION — assumptions in sim.py (illustrative, not an estimate)",
        "status_quo_monthly": _monthly_status_quo(random.Random(a["seed"]), a),
        "protocol_ladder_weekly": _weekly_ladder(random.Random(a["seed"]), a),
    }
    result["metric_pct_within_sla"] = result["protocol_ladder_weekly"]["pct_done_within_sla"]
    print(json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    run_simulation()
