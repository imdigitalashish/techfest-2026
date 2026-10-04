from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml

from architecture.contracts.models import Alert, Role, Task, TaskTransition

PROTOCOL_PATH = Path(__file__).with_name("protocol.yaml")


def _load_protocol() -> dict[str, Any]:
    with PROTOCOL_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


_PROTOCOL = _load_protocol()


def _kind(alert_or_task: Alert | Task) -> str:
    if isinstance(alert_or_task, Alert):
        return alert_or_task.kind.value
    return alert_or_task.alert_id.split(":", 1)[0] if ":" in alert_or_task.alert_id else alert_or_task.alert_id.rsplit("-", 1)[0]


def _owner_scope(alert: Alert, role: Role) -> str:
    if role in {Role.AWW, Role.ASHA, Role.ANM}:
        return alert.geo.awc_code
    if role == Role.LS:
        return alert.geo.sector_code
    if role in {Role.CDPO, Role.MO_PHC}:
        return alert.geo.project_code
    if role in {Role.DPO, Role.DM}:
        return alert.geo.district_code
    if role == Role.STATE:
        return alert.geo.state_code
    return "IN"


def _task_from_step(alert: Alert, step: dict[str, Any], today: date) -> Task:
    role = Role(step["owner_role"])
    return Task(
        task_id=f"{alert.alert_id}:L{step['level']}",
        alert_id=alert.alert_id,
        owner_role=role,
        owner_scope_id=_owner_scope(alert, role),
        action=step["action"],
        due_on=today + timedelta(days=int(step["due_days"])),
        status="open",
        escalation_level=int(step["level"]),
        protocol_ref=step["protocol_ref"],
        history=[
            TaskTransition(
                on=today,
                from_status="new",
                to_status="open",
                by_role=Role.SYSTEM,
                note=f"Routed by protocol step {step['level']}",
            )
        ],
    )


def route(alerts: list[Alert], today: date) -> list[Task]:
    tasks: list[Task] = []
    for alert in alerts:
        steps = _PROTOCOL["alerts"][alert.kind.value]
        tasks.append(_task_from_step(alert, steps[0], today))
    return tasks


def escalate(tasks: list[Task], today: date, alerts: dict[str, Alert] | None = None) -> list[Task]:
    """Move overdue open tasks to the next protocol step. Pass `alerts` (alert_id -> Alert) so the next owner's
    scope is derived from the alert's geography (e.g. AWC -> sector for the Lady Supervisor)."""
    out: list[Task] = []
    for task in tasks:
        if task.status != "open" or task.due_on >= today:
            out.append(task)
            continue
        alert = (alerts or {}).get(task.alert_id)
        ladder = _PROTOCOL["alerts"].get(alert.kind.value if alert else _kind(task))
        if ladder is None:
            for steps in _PROTOCOL["alerts"].values():
                if any(s["action"] == task.action and int(s["level"]) == task.escalation_level for s in steps):
                    ladder = steps
                    break
        if ladder is None:
            out.append(task)
            continue
        next_level = task.escalation_level + 1
        next_step = next((s for s in ladder if int(s["level"]) == next_level), None)
        escalated_task = task.model_copy(
            update={
                "status": "escalated",
                "history": task.history
                + [TaskTransition(on=today, from_status="open", to_status="escalated", by_role=Role.SYSTEM, note="Overdue; escalated to next protocol step.")],
            }
        )
        out.append(escalated_task)
        if next_step is not None:
            role = Role(next_step["owner_role"])
            owner_scope = _owner_scope(alert, role) if alert is not None else task.owner_scope_id
            out.append(
                Task(
                    task_id=f"{task.alert_id}:L{next_level}",
                    alert_id=task.alert_id,
                    owner_role=role,
                    owner_scope_id=owner_scope,
                    action=next_step["action"],
                    due_on=today + timedelta(days=int(next_step["due_days"])),
                    status="open",
                    escalation_level=next_level,
                    protocol_ref=next_step["protocol_ref"],
                    history=[TaskTransition(on=today, from_status="new", to_status="open", by_role=Role.SYSTEM, note=f"Escalated from {task.task_id}")],
                )
            )
    return out


def close(task: Task, outcome: str, today: date) -> Task:
    return task.model_copy(
        update={
            "status": "done",
            "history": task.history
            + [TaskTransition(on=today, from_status=task.status, to_status="done", by_role=task.owner_role, note=outcome)],
        }
    )
