"""Render deliverables from templates: {{key}} placeholders are filled from eval/results/headline.json (display values).

Reproduce: cd perceptron-p03-off-policy-eval && .venv/bin/python eval/build_headline.py && .venv/bin/python deliverables/render.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "deliverables" / "round1-abstract.tmpl.md"
OUT = ROOT / "deliverables" / "round1-abstract.md"


def render() -> str:
    disp = json.loads((ROOT / "eval" / "results" / "headline.json").read_text())["display"]
    text = TEMPLATE.read_text()
    missing = sorted(set(re.findall(r"\{\{(\w+)\}\}", text)) - set(disp))
    if missing:
        raise KeyError(f"placeholders without values: {missing}")
    return re.sub(r"\{\{(\w+)\}\}", lambda m: disp[m.group(1)], text)


if __name__ == "__main__":
    OUT.write_text(render())
    body = OUT.read_text().split("**Problem & theme.**", 1)[-1]
    print(f"wrote {OUT.relative_to(ROOT)}; words in body (alphanumeric tokens): {sum(1 for w in body.split() if re.search(r'[A-Za-z0-9]', w))}")
