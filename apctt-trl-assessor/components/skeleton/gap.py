"""C6 Rubric engine & gap analysis v0 — faithful by construction.

Criterion of level L is judged from the model's own threshold P(TRL >= L) (= p_gt[L-2]) together with the
achieved evidence for that level: met if P >= 0.5, not_met if P < 0.5 and no achieved evidence, unknown when
the model and the evidence disagree. The gap list is the next level's criterion plus the rubric's action text.
"""
from __future__ import annotations

from .evidence import load_rubric


def analyse(decision: dict, dist: dict, evidence: list[dict], rubric: dict | None = None) -> dict:
    r = rubric or load_rubric()
    by_signal: dict[str, list[str]] = {}
    for e in evidence:
        if e["polarity"] == "achieved":
            by_signal.setdefault(e["signal"], []).append(e["evidence_id"])
    criteria = []
    for lv in r["levels"]:
        L = lv["level"]
        p_ge = 1.0 if L == 1 else dist["p_gt"][L - 2]
        ev = by_signal.get(lv["signal"], [])
        if p_ge >= 0.5 and (ev or L <= decision["trl"]):
            status = "met"
        elif p_ge < 0.5 and not ev:
            status = "not_met"
        else:
            status = "unknown"
        criteria.append({"criterion_id": lv["criterion_id"], "level": L, "text": lv["text"], "status": status,
                         "evidence_ids": ev[:10]})
    nxt = decision["trl"] + 1 if decision["trl"] < 9 else None
    missing = [{"criterion_id": lv["criterion_id"], "text": lv["text"], "suggested_actions": list(lv["actions"])}
               for lv in r["levels"] if nxt is not None and lv["level"] == nxt]
    n_planned = sum(e["polarity"] == "planned" for e in evidence)
    return {"criteria": criteria, "next_level": nxt, "missing_for_next_level": missing,
            "notes": f"rubric={r['rubric_id']}; P(TRL>=L) from model thresholds; {len(evidence)} evidence items "
                     f"({n_planned} planned, not counted as achieved)."}
