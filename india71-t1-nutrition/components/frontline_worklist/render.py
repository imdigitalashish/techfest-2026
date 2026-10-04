from __future__ import annotations

import json
import statistics
from datetime import date
from typing import Any

from architecture.contracts.models import Role, Task, Worklist, WorklistItem

_REASON_TEMPLATES = {
    "home_visit_and_referral": ("SAM alert: home visit and referral due", "SAM चेतावनी: घर भेंट और रेफरल करें"),
    "medical_appraisal": ("Medical appraisal due after referral", "रेफरल के बाद चिकित्सीय जांच बाकी"),
    "counselling_and_supplementary_nutrition": ("MAM alert: counselling and nutrition support", "MAM चेतावनी: परामर्श और पोषण सहायता"),
    "remeasure_in_14_days": ("Follow-up measurement due", "फॉलो-अप माप बाकी"),
    "home_visit_and_counselling": ("Growth risk: home visit and counselling", "वृद्धि जोखिम: घर भेंट और परामर्श"),
    "joint_visit_if_illness_flagged": ("Joint visit if illness is flagged", "बीमारी संकेत पर संयुक्त भेंट करें"),
    "monthly_remeasure": ("Monthly growth re-measurement due", "मासिक वृद्धि पुनर्माप बाकी"),
    "remeasure_random_sample_10_children": ("Data recheck: re-measure sample of 10", "डेटा जांच: 10 बच्चों का पुनर्माप"),
    "equipment_check": ("Equipment check for data-quality alert", "डेटा गुणवत्ता हेतु उपकरण जांच"),
    "joint_health_follow_up": ("Health signal follow-up", "स्वास्थ्य संकेत फॉलो-अप"),
}


def _capacity(capacity_by_worker: dict[Any, int], role: Role, scope_id: str) -> int:
    candidates = [(role.value, scope_id), f"{role.value}:{scope_id}", scope_id, role.value, "default"]
    for key in candidates:
        if key in capacity_by_worker:
            return int(capacity_by_worker[key])
    return 10


def _priority(task: Task) -> int:
    return max(1, min(4, 2 + task.escalation_level))


def _reason(action: str) -> tuple[str, str]:
    return _REASON_TEMPLATES.get(action, (f"Action due: {action.replace('_', ' ')}", f"कार्य बाकी: {action.replace('_', ' ')}"))


def build_worklists(tasks: list[Task], child_local_refs: dict[str, str], capacity_by_worker: dict, week_of: date) -> list[Worklist]:
    grouped: dict[tuple[Role, str], list[Task]] = {}
    for task in tasks:
        if task.status == "open":
            grouped.setdefault((task.owner_role, task.owner_scope_id), []).append(task)
    worklists: list[Worklist] = []
    for (role, scope_id), group in sorted(grouped.items(), key=lambda x: (x[0][0].value, x[0][1])):
        cap = _capacity(capacity_by_worker, role, scope_id)
        group.sort(key=lambda t: (-_priority(t), t.due_on, t.task_id))
        items = []
        for task in group[:cap]:
            child_ref = child_local_refs.get(task.task_id) or child_local_refs.get(task.alert_id) or "UNIT"
            en, hi = _reason(task.action)
            items.append(
                WorklistItem(
                    child_local_ref=child_ref,
                    task_id=task.task_id,
                    action=task.action,
                    due_on=task.due_on,
                    priority=_priority(task),
                    reason_en=en,
                    reason_hi=hi,
                )
            )
        worklists.append(
            Worklist(worker_role=role, worker_id=f"{role.value}:{scope_id}", scope_id=scope_id, week_of=week_of, capacity=cap, items=items, synthetic=True)
        )
    return worklists


def to_sms(worklist: Worklist) -> list[str]:
    messages: list[str] = []
    for item in worklist.items:
        action = item.action.replace("_", " ")[:48]
        msg = f"Poshan Setu: {item.child_local_ref} P{item.priority} {action} due {item.due_on.isoformat()}"
        if len(msg) > 160:
            msg = msg[:157] + "..."
        messages.append(msg)
    return messages


def payload_bytes(worklist: Worklist) -> int:
    payload = worklist.model_dump(mode="json", exclude_none=True)
    return len(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def evaluate_worklists(worklists: list[Worklist]) -> dict:
    sizes = [payload_bytes(w) for w in worklists]
    sms = [m for w in worklists for m in to_sms(w)]
    result = {
        "median_payload_bytes": statistics.median(sizes) if sizes else 0,
        "pct_sms_le_160": round(100 * sum(len(m) <= 160 for m in sms) / len(sms), 2) if sms else 100.0,
        "n_worklists": len(worklists),
    }
    print("FRONTLINE_WORKLIST_METRIC " + json.dumps(result, sort_keys=True))
    return result
