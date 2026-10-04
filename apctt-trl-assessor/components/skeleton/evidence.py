"""C3 Evidence extractor (rubric-lexicon v0): ParsedDocument + rubric -> EvidenceItem[].

Cue phrases come only from the rubric file (EU Annex G + NASA wording); nothing is keyed to documents.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

RUBRIC = Path(__file__).resolve().parents[2] / "architecture" / "contracts" / "rubric_eu_nasa_v0.json"
SENT = re.compile(r"[^.!?]+(?:[.!?]+|$)")


@lru_cache(maxsize=4)
def load_rubric(path: str = str(RUBRIC)) -> dict:
    r = json.loads(Path(path).read_text())
    for lv in r["levels"]:
        lv["_re"] = re.compile("|".join(f"(?:{c})" for c in lv["cues"]), re.I)
    r["_planned"] = re.compile("|".join(r["polarity"]["planned"]), re.I)
    r["_negated"] = re.compile("|".join(r["polarity"]["negated"]), re.I)
    r["_scale"] = [(k, re.compile(v, re.I)) for k, v in (("subsystem", r["scale"]["subsystem"]),
                                                          ("system", r["scale"]["system"]),
                                                          ("component", r["scale"]["component"]))]
    return r


def extract(doc: dict, rubric: dict | None = None, max_items: int = 60) -> list[dict]:
    r = rubric or load_rubric()
    items: list[dict] = []
    for sec in doc["sections"]:
        text = sec["text"]
        for m in SENT.finditer(text):
            sent = m.group(0)
            for lv in r["levels"]:
                if not lv["_re"].search(sent):
                    continue
                polarity = "negated" if r["_negated"].search(sent) else ("planned" if r["_planned"].search(sent) else "achieved")
                scale = next((k for k, rx in r["_scale"] if rx.search(sent)), "unknown")
                start = m.start() + (len(sent) - len(sent.lstrip()))
                items.append({"evidence_id": f"e{len(items)}", "section_id": sec["section_id"],
                              "char_start": start, "char_end": m.end(), "quote": sent.strip()[:1000],
                              "signal": lv["signal"], "environment": lv["environment"], "scale": scale,
                              "polarity": polarity, "confidence": 0.5})
                if len(items) >= max_items:
                    return items
    return items


def level_of(signal: str, rubric: dict | None = None) -> int:
    r = rubric or load_rubric()
    return next(lv["level"] for lv in r["levels"] if lv["signal"] == signal)
