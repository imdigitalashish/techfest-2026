"""Render run-derived numbers into documents from eval/results/latest.json, so documents cannot drift from the run.

Inline marker (invisible in rendered Markdown):  <!--n:KEY-->current text<!--/n-->
Usage (from ev-c1-infra-map-india/): python3 eval/render_docs.py      # rewrites markers in place
Then python3 eval/check_docs.py verifies nothing drifted and no unverified number remains.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ["deliverables/round1-methodology.md", "deliverables/round1-roadmap.md", "research/landscape.md",
        "architecture/adr/001-spike.md", "architecture/components.md", "thought_node.md"]
MARK = re.compile(r"<!--n:([A-Za-z0-9_]+)-->(.*?)<!--/n-->", re.S)


def render(text: str, latest: dict) -> str:
    def sub(m):
        k = m.group(1)
        if k not in latest:
            raise KeyError(f"unknown number key {k!r}")
        return f"<!--n:{k}-->{latest[k]['text']}<!--/n-->"
    return MARK.sub(sub, text)


def main():
    latest = json.loads((ROOT / "eval/results/latest.json").read_text())
    for rel in DOCS:
        p = ROOT / rel
        if p.exists():
            t = p.read_text(); r = render(t, latest)
            if r != t:
                p.write_text(r); print(f"rendered {rel}")


if __name__ == "__main__":
    main()
