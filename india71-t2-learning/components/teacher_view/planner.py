from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Iterable, Mapping

from architecture.contracts.fln_contracts import ChildDiagnosis, Subject, TeacherPlan, TeachingGroup

ACT_PATH = Path(__file__).with_name("activities.json")


def _segments(text: str) -> int:
    limit = 70 if any(ord(c) > 127 for c in text) else 160
    return (len(text) + limit - 1) // limit


def make_plan(diagnoses: Iterable[ChildDiagnosis], roster: Mapping[str, str], week_of: date, channel: str = "whatsapp", language: str = "en") -> TeacherPlan:
    diagnoses = list(diagnoses)
    if not diagnoses:
        raise ValueError("diagnoses required")
    subject = diagnoses[0].subject
    udise = diagnoses[0].udise_code
    activities = json.loads(ACT_PATH.read_text())[subject.value]
    buckets: dict[int, list[str]] = defaultdict(list)
    for d in diagnoses:
        buckets[int(d.level)].append(roster.get(d.student, d.student[-4:]))
    # Merge tiny groups into adjacent level to keep instructions usable.
    for lvl in list(sorted(buckets)):
        if 0 < len(buckets[lvl]) < 3 and len(buckets) > 1:
            target = lvl - 1 if lvl > 0 else 1
            buckets[target].extend(buckets.pop(lvl))
    groups = []
    for lvl in sorted(buckets):
        acts = [a["id"] for a in activities[str(lvl)][:2]]
        groups.append(TeachingGroup(label=f"Level {lvl}", level=lvl, student_refs=sorted(buckets[lvl]), activity_ids=acts))
    lines = []
    if language == "hi":
        lines.append(f"सप्ताह {week_of}: कक्षा 3 {('भाषा' if subject == Subject.LANGUAGE else 'गणित')} TaRL समूह")
        for g in groups:
            names = ",".join(g.student_refs[:12])
            lines.append(f"स्तर {g.level}: {names}. गतिविधि: {'/'.join(g.activity_ids)}")
    else:
        lines.append(f"Week {week_of}: Grade 3 {subject.value} TaRL groups")
        for g in groups:
            names = ",".join(g.student_refs[:12])
            lines.append(f"Level {g.level}: {names}. Do: {'/'.join(g.activity_ids)}")
    text = "\n".join(lines)
    if channel == "sms" and _segments(text) > 3:
        lines = lines[:1] + [f"L{g.level}:{len(g.student_refs)} kids {('/'.join(g.activity_ids))[:18]}" for g in groups]
        text = "\n".join(lines)
        if _segments(text) > 3:
            text = text[:207]
    return TeacherPlan(udise_code=udise, grade=3, subject=subject, week_of=week_of, groups=groups,
                       message_text=text, channel=channel, language=language, payload_bytes=len(text.encode("utf-8")))


def sms_segments(plan: TeacherPlan) -> int:
    return _segments(plan.message_text)


def render_ivr_script(plan: TeacherPlan) -> str:
    lines = [f"Namaste. Grade {plan.grade} {plan.subject.value} plan for week {plan.week_of}."]
    for i, g in enumerate(plan.groups, start=1):
        lines.append(f"Press {i} for {g.label}: {len(g.student_refs)} children. Activity {' and '.join(g.activity_ids)}.")
    lines.append("Repeat daily and reassess on Friday.")
    return " ".join(lines)
