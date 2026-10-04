"""C6 Rubric engine & gap analysis v0.1 — evidence-led, model-consistent reporting.

Status per rubric criterion comes from the document's evidence only:
  supported      achieved evidence for that level's signal, no negation
  contradicted   negated evidence present (with or without achieved evidence — conservative)
  not_evidenced  nothing in this document (NOT a claim that the technology lacks the capability)
The model's P(TRL >= level) is reported next to each criterion (`model_p_ge`) but never marks a criterion
supported. On abstention every criterion is not_evidenced and no progression advice is given.
The evidence does not (yet) feed the TRL model, so this is NOT a faithfulness claim about the predictor.
"""
from __future__ import annotations

from .evidence import load_rubric


def analyse(decision: dict, dist: dict, evidence: list[dict], rubric: dict | None = None) -> dict:
    r = rubric or load_rubric()
    ach: dict[str, list[str]] = {}
    neg: dict[str, list[str]] = {}
    for e in evidence:
        if e["polarity"] == "achieved":
            ach.setdefault(e["signal"], []).append(e["evidence_id"])
        elif e["polarity"] == "negated":
            neg.setdefault(e["signal"], []).append(e["evidence_id"])
    criteria = []
    for lv in r["levels"]:
        L, sig = lv["level"], lv["signal"]
        a, n = ach.get(sig, []), neg.get(sig, [])
        if decision["abstain"] or not (a or n):
            status, ids = "not_evidenced", []
        elif n:
            status, ids = "contradicted", n + a
        else:
            status, ids = "supported", a
        p_ge = 1.0 if L == 1 else float(dist["p_gt"][L - 2])
        criteria.append({"criterion_id": lv["criterion_id"], "level": L, "text": lv["text"], "status": status,
                         "evidence_ids": ids[:10], "model_p_ge": round(min(max(p_ge, 0.0), 1.0), 4)})
    nxt = None if (decision["abstain"] or decision["trl"] >= 9) else decision["trl"] + 1
    missing = [{"criterion_id": c["criterion_id"], "text": c["text"],
                "suggested_actions": list(next(lv for lv in r["levels"] if lv["level"] == nxt)["actions_to_reach"])}
               for c in criteria if nxt is not None and c["level"] == nxt and c["status"] != "supported"]
    n_planned = sum(e["polarity"] == "planned" for e in evidence)
    note = ("abstained: input too short or unreadable; no progression advice. " if decision["abstain"] else "")
    return {"criteria": criteria, "next_level": nxt, "missing_for_next_level": missing,
            "notes": note + f"rubric={r['rubric_id']}; status is evidence-led (not_evidenced = absent from this "
                            f"document); model_p_ge = model P(TRL>=level); {len(evidence)} evidence items, "
                            f"{n_planned} planned (never counted as achieved)."}
