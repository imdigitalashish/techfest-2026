"""Fail if documents drift from the committed per-question results, or keep superseded design numbers.

(1) every `<!-- p2:<name>:begin/end -->` block equals what eval/render_docs.py renders now, and eval/RESULTS.md
    equals a fresh render; (2) numbers of the superseded design (2-bit layer-8 sketch, ~160 B/token, ~0.5 %) do not
    appear in current-state documents (the append-only Log in thought_node.md and ADR history are exempt).
Usage (from perceptron-p02-kv-cache/):  python3 eval/check_docs.py   (exit code 1 on drift)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_docs import DOCS, ROOT, compute, render, render_blocks, results_md  # noqa: E402

CURRENT = ["deliverables/round1-abstract.md", "deliverables/architecture.md", "deliverables/selection-memo.md",
           "thought_node.md", "research/landscape.md", "architecture/components.md", "README.md"]
STALE = ["160 B", "≈ 160", "~160", "0.5%", "0.5 %", "0.49%", "2-bit key sketch", "2-bit sketch", "2-bit index",
         "2-bit keys", "layer 8", "2-bit single-layer", "single-layer 2-bit"]


def current_part(rel: str, text: str) -> str:
    return text.split("\n## Log", 1)[0] if rel == "thought_node.md" else text


def main() -> int:
    V = compute()
    blocks = render_blocks(V)
    problems = []
    if (ROOT / "eval/RESULTS.md").read_text() != results_md(V) + "\n":
        problems.append("eval/RESULTS.md differs from a fresh render (run eval/render_docs.py)")
    for rel in DOCS[1:]:
        p = ROOT / rel
        if p.exists() and render(p.read_text(), blocks) != p.read_text():
            problems.append(f"{rel}: a marked block differs from the committed results (run eval/render_docs.py)")
    for rel in CURRENT:
        p = ROOT / rel
        if not p.exists():
            continue
        cur = current_part(rel, p.read_text())
        for s in STALE:
            if s in cur:
                problems.append(f"{rel}: superseded design number {s!r} in current-state text")
        for m in re.finditer(r"<!-- p2:([a-z0-9-]+):begin -->(.*?)<!-- p2:\1:end -->", cur, flags=re.S):
            if not m.group(2).strip():
                problems.append(f"{rel}: empty marked block {m.group(1)!r}")
    for x in problems:
        print("DRIFT:", x)
    print("check_docs:", "OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
