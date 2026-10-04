from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable, Mapping

from architecture.contracts.fln_contracts import ChildDiagnosis, Subject, TeacherPlan, TeachingGroup

ACT_PATH = Path(__file__).with_name("activities.json")
ROLL_DISPLAY_CAP = 12
WHATSAPP_BYTE_CAP = 1024


def _segments(text: str) -> int:
    limit = 70 if any(ord(c) > 127 for c in text) else 160
    return (len(text) + limit - 1) // limit


def _roll_key(ref: str) -> tuple[int, str]:
    nums = re.findall(r"\d+", ref)
    return (int(nums[-1]) if nums else 10**9, ref)


def _roll_label(ref: str, language: str) -> str:
    nums = re.findall(r"\d+", ref)
    if nums:
        return f"रोल {int(nums[-1])}" if language == "hi" else f"Roll {int(nums[-1])}"
    return ref


def _format_rolls(refs: list[str], language: str, cap: int = ROLL_DISPLAY_CAP) -> str:
    ordered = sorted(refs, key=_roll_key)
    shown = [_roll_label(r, language) for r in ordered[:cap]]
    sep = ", "
    if len(ordered) > cap:
        more = len(ordered) - cap
        suffix = f" … (+{more} और)" if language == "hi" else f" … (+{more} more)"
        return sep.join(shown) + suffix
    return sep.join(shown)


def _activity_text(activity_ids: list[str], activities: dict, level: int, language: str) -> str:
    by_id = {a["id"]: a for a in activities[str(level)]}
    key = "name_hi" if language == "hi" else "name_en"
    return "; ".join(f"{by_id[a].get(key, by_id[a].get('name_en', a))} [{a}]" for a in activity_ids)


def _first_activity_name(activity_ids: list[str], activities: dict, level: int, language: str) -> str:
    if not activity_ids:
        return ""
    a = {x["id"]: x for x in activities[str(level)]}[activity_ids[0]]
    return a.get("name_hi" if language == "hi" else "name_en", a.get("name_en", activity_ids[0]))


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
    for lvl in list(sorted(buckets)):
        if 0 < len(buckets[lvl]) < 3 and len(buckets) > 1:
            target = lvl - 1 if lvl > 0 else 1
            buckets[target].extend(buckets.pop(lvl))
    groups = []
    for lvl in sorted(buckets):
        acts = [a["id"] for a in activities[str(lvl)][:2]]
        groups.append(TeachingGroup(label=f"Level {lvl}", level=lvl, student_refs=sorted(buckets[lvl], key=_roll_key), activity_ids=acts))

    if channel == "sms":
        if language == "hi":
            lines = [f"सप्ताह {week_of}: कक्षा 3 {('भाषा' if subject == Subject.LANGUAGE else 'गणित')} समूह"]
            lines += [f"स्तर {g.level}: {len(g.student_refs)} बच्चे; {_first_activity_name(g.activity_ids, activities, g.level, language)}" for g in groups]
        else:
            lines = [f"Week {week_of}: G3 {subject.value} groups"]
            lines += [f"L{g.level}: {len(g.student_refs)} kids; {_first_activity_name(g.activity_ids, activities, g.level, language)}" for g in groups]
        text = "\n".join(lines)
        while _segments(text) > 3 and len(lines) > 1:
            lines[-1] = lines[-1].split(";")[0]
            text = "\n".join(lines)
    else:
        if language == "hi":
            lines = [f"सप्ताह {week_of}: कक्षा 3 {('भाषा' if subject == Subject.LANGUAGE else 'गणित')} TaRL समूह"]
            for g in groups:
                lines.append(f"स्तर {g.level} ({len(g.student_refs)}): {_format_rolls(g.student_refs, language)}. गतिविधि: {_activity_text(g.activity_ids, activities, g.level, language)}")
        else:
            lines = [f"Week {week_of}: Grade 3 {subject.value} TaRL groups"]
            for g in groups:
                lines.append(f"Level {g.level} ({len(g.student_refs)}): {_format_rolls(g.student_refs, language)}. Activity: {_activity_text(g.activity_ids, activities, g.level, language)}")
        text = "\n".join(lines)
        if channel == "whatsapp" and len(text.encode("utf-8")) > WHATSAPP_BYTE_CAP:
            compact = [lines[0]]
            lab = "स्तर" if language == "hi" else "Level"
            compact += [f"{lab} {g.level} ({len(g.student_refs)}): {_format_rolls(g.student_refs, language, cap=6)}; {_first_activity_name(g.activity_ids, activities, g.level, language)}" for g in groups]
            text = "\n".join(compact)
    if channel == "whatsapp" and len(text.encode("utf-8")) > WHATSAPP_BYTE_CAP:
        raise ValueError("WhatsApp teacher plan exceeds 1 KB")
    if channel == "sms" and _segments(text) > 3:
        raise ValueError("SMS teacher plan exceeds 3 segments")
    return TeacherPlan(udise_code=udise, grade=3, subject=subject, week_of=week_of, groups=groups,
                       message_text=text, channel=channel, language=language, payload_bytes=len(text.encode("utf-8")))


def sms_segments(plan: TeacherPlan) -> int:
    return _segments(plan.message_text)


def render_ivr_script(plan: TeacherPlan) -> str:
    recheck = plan.week_of + timedelta(days=28)
    acts = json.loads(ACT_PATH.read_text())[plan.subject.value]
    lines = [f"Namaste. Grade {plan.grade} {plan.subject.value} plan for week {plan.week_of}."]
    for i, g in enumerate(plan.groups, start=1):
        lines.append(f"Press {i} for {g.label}: {len(g.student_refs)} children. Activity: {_first_activity_name(g.activity_ids, acts, g.level, 'en')}.")
    lines.append(f"Repeat daily. Recheck children on {recheck}.")
    return " ".join(lines)
