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
MEMO_TEMPLATE = ROOT / "deliverables" / "selection-memo.tmpl.md"
NODE = ROOT / "thought_node.md"


def render(template: Path = TEMPLATE) -> str:
    disp = json.loads((ROOT / "eval" / "results" / "headline.json").read_text())["display"]
    text = template.read_text()
    missing = sorted(set(re.findall(r"\{\{(\w+)\}\}", text)) - set(disp))
    if missing:
        raise KeyError(f"placeholders without values: {missing}")
    return re.sub(r"\{\{(\w+)\}\}", lambda m: disp[m.group(1)], text)


def render_memo_into_node() -> str:
    """Replace the thought node's '## Selection memo' section with the rendered memo template."""
    node = NODE.read_text()
    a = node.index("## Selection memo")
    b = node.index("\n## ", a + 5)
    memo = render(MEMO_TEMPLATE).rstrip("\n") + "\n"
    return node[:a] + memo + node[b:]


def memo_ready() -> bool:
    disp = json.loads((ROOT / "eval" / "results" / "headline.json").read_text())["display"]
    return MEMO_TEMPLATE.exists() and set(re.findall(r"\{\{(\w+)\}\}", MEMO_TEMPLATE.read_text())) <= set(disp)


if __name__ == "__main__":
    OUT.write_text(render())
    if memo_ready():
        NODE.write_text(render_memo_into_node())
        print("rendered the selection memo into thought_node.md")
    else:
        print("selection memo not rendered: review scores not recorded yet (reviews/scores.json)")
    body = OUT.read_text().split("**Problem & theme.**", 1)[-1]
    print(f"wrote {OUT.relative_to(ROOT)}; words in body (alphanumeric tokens): {sum(1 for w in body.split() if re.search(r'[A-Za-z0-9]', w))}")
