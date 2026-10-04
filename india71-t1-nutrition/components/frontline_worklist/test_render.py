from __future__ import annotations

from datetime import date

from architecture.contracts.models import Role, Task
from components.frontline_worklist.render import build_worklists, evaluate_worklists, payload_bytes, to_sms


def task(task_id: str, due: date, level: int = 0, role: Role = Role.AWW, scope: str = "AWC1") -> Task:
    return Task(
        task_id=task_id,
        alert_id=task_id.split(":")[0],
        owner_role=role,
        owner_scope_id=scope,
        action="home_visit_and_referral" if role == Role.AWW else "medical_appraisal",
        due_on=due,
        status="open",
        escalation_level=level,
        protocol_ref="ref (VERIFY)",
        history=[],
    )


def test_build_worklists_sorts_and_caps():
    tasks = [
        task("a1:L0", date(2026, 1, 10), 0),
        task("a2:L1", date(2026, 1, 9), 1),
        task("a3:L0", date(2026, 1, 8), 0),
    ]
    worklists = build_worklists(tasks, {"a1": "B1", "a2": "B2", "a3": "B3"}, {"aww:AWC1": 2}, date(2026, 1, 5))
    assert len(worklists) == 1
    assert worklists[0].capacity == 2
    assert [i.child_local_ref for i in worklists[0].items] == ["B2", "B3"]
    assert worklists[0].items[0].priority == 3


def test_sms_has_no_names_and_fits_160_chars():
    wl = build_worklists([task("a1:L0", date(2026, 1, 10))], {"a1": "BEN-001"}, {"default": 5}, date(2026, 1, 5))[0]
    messages = to_sms(wl)
    assert messages == ["Poshan Setu: BEN-001 P2 home visit and referral due 2026-01-10"]
    assert all(len(m) <= 160 for m in messages)
    assert "name" not in messages[0].lower()


def test_payload_metric():
    wls = build_worklists(
        [task("a1:L0", date(2026, 1, 10)), task("a2:L0", date(2026, 1, 11), role=Role.MO_PHC, scope="P1")],
        {"a1": "B1", "a2": "B2"},
        {"default": 5},
        date(2026, 1, 5),
    )
    assert all(payload_bytes(w) > 0 for w in wls)
    metric = evaluate_worklists(wls)
    assert metric["pct_sms_le_160"] == 100.0
    assert metric["n_worklists"] == 2
