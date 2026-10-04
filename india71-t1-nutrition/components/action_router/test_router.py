from __future__ import annotations

from datetime import date, timedelta

from architecture.contracts.models import Alert, AlertKind, GeoUnit, Role
from components.action_router.router import close, escalate, route
from components.action_router.sim import run_simulation

GEO = GeoUnit(state_code="S1", district_code="D1", project_code="P1", sector_code="SEC1", awc_code="AWC1", village_code="V1")


def alert(kind: AlertKind, alert_id: str = "a1") -> Alert:
    return Alert(alert_id=alert_id, child_key="child-1", geo=GEO, kind=kind, severity=4, created_on=date(2026, 1, 1), evidence=["e"], recommended_action="act", synthetic=True)


def test_route_sam_first_step():
    tasks = route([alert(AlertKind.SAM)], date(2026, 1, 1))
    assert len(tasks) == 1
    task = tasks[0]
    assert task.owner_role == Role.AWW
    assert task.owner_scope_id == "AWC1"
    assert task.action == "home_visit_and_referral"
    assert task.due_on == date(2026, 1, 3)
    assert task.escalation_level == 0


def test_route_data_recheck_unit_level():
    a = alert(AlertKind.DATA_RECHECK, "dr1").model_copy(update={"child_key": None})
    task = route([a], date(2026, 1, 1))[0]
    assert task.owner_role == Role.LS
    assert task.action == "remeasure_random_sample_10_children"
    assert task.due_on == date(2026, 1, 15)


def test_escalate_overdue_task_creates_next_step():
    task = route([alert(AlertKind.SAM)], date(2026, 1, 1))[0]
    out = escalate([task], date(2026, 1, 4))
    assert [t.status for t in out] == ["escalated", "open"]
    assert out[1].owner_role == Role.MO_PHC
    assert out[1].escalation_level == 1
    assert out[1].action == "medical_appraisal"
    assert out[0].history[-1].to_status == "escalated"


def test_escalate_not_due_and_close():
    task = route([alert(AlertKind.MAM)], date(2026, 1, 1))[0]
    assert escalate([task], task.due_on) == [task]
    done = close(task, "completed home visit", date(2026, 1, 2))
    assert done.status == "done"
    assert done.history[-1].note == "completed home visit"
    assert escalate([done], date(2026, 2, 1)) == [done]


def test_simulation_metric():
    result = run_simulation(n_awcs=3, alerts_per_awc_per_week=1, weeks=4)
    assert result["label"] == "SIMULATION — assumptions in sim.py"
    assert result["protocol_ladder_weekly"]["pct_done_within_sla"] >= result["status_quo_monthly"]["pct_done_within_sla"]
    assert result["metric_pct_within_sla"] == result["protocol_ladder_weekly"]["pct_done_within_sla"]
