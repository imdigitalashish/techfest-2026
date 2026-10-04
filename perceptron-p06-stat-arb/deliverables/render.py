"""Render deliverables from templates + eval/results/headline.json.

Templates use {{key}} placeholders; every key must exist in headline.json (missing keys raise).
Usage: .venv/bin/python deliverables/render.py      (writes round1-abstract.md and architecture.md)
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [("round1-abstract.tmpl.md", "round1-abstract.md"), ("architecture.tmpl.md", "architecture.md")]
KEY = re.compile(r"\{\{(\w+)\}\}")


def headline() -> dict:
    return json.loads((ROOT / "eval" / "results" / "headline.json").read_text())


def render_one(tmpl: str, h: dict) -> str:
    def sub(m):
        k = m.group(1)
        if k not in h:
            raise KeyError(f"template key {k!r} missing from headline.json")
        return h[k]
    return KEY.sub(sub, tmpl)


def render() -> dict[str, str]:
    h = headline()
    return {out: render_one((ROOT / "deliverables" / t).read_text(), h) for t, out in PAIRS}


if __name__ == "__main__":
    for name, text in render().items():
        (ROOT / "deliverables" / name).write_text(text)
        print("rendered", name, len(text.split()), "words")
