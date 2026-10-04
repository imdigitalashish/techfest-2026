"""C2 Doc-type router (rules v0): ParsedDocument -> DocType."""
from __future__ import annotations

import re


def classify(doc: dict) -> dict:
    t = " ".join(s["text"] for s in doc["sections"])[:200000].lower()
    if re.search(r"\b(what is claimed is|claims?:|\d+\.\s+an? [a-z ]+ comprising)\b", t):
        return {"type": "patent", "confidence": 0.8}
    if "abstract" in t[:3000] and re.search(r"\b(references|bibliography)\b", t):
        return {"type": "paper", "confidence": 0.7}
    if re.search(r"\b(we propose|proposed (work|research|innovation)|phase i\b|phase ii\b)", t):
        return {"type": "proposal", "confidence": 0.6}
    if re.search(r"\b(final report|progress report|technical report|executive summary)\b", t):
        return {"type": "report", "confidence": 0.6}
    return {"type": "other", "confidence": 0.3}
