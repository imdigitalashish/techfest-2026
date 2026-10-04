"""Fail if documents drift from the committed run (eval/results/latest.json).

Checks: (1) every marked block equals what eval/render_docs.py would render now; (2) superseded headline numbers from
earlier runs do not appear in current-state documents (the append-only Log in thought_node.md is exempt).
Usage (from ev-c2-green-auto-lca/):  python3 eval/check_docs.py   (exit code 1 on drift)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_docs import DOCS, ROOT, render  # noqa: E402

# Headlines of superseded runs (CO2-only grid, E0 petrol central, before maintenance and source-ambiguity ranges).
STALE = ["36.9 %", "36.9%", "29.2–43.8", "29.2-43.8", "14.0 %", "55.2 %", "62.95", "39.71", "48.5 % vs", "57.6–69.0"]


def current_part(rel: str, text: str) -> str:
    return text.split("\n## Log", 1)[0] if rel == "thought_node.md" else text


def main() -> int:
    d = json.loads((ROOT / "eval/results/latest.json").read_text())
    problems = []
    for rel in DOCS:
        p = ROOT / rel
        if not p.exists():
            continue
        t = p.read_text()
        if render(t, d) != t:
            problems.append(f"{rel}: marked block differs from the current run (run eval/render_docs.py)")
        cur = current_part(rel, t)
        for s in STALE:
            if s in cur:
                problems.append(f"{rel}: stale number {s!r} in current-state text")
    # key numbers must also appear in the methodology prose (not only in rendered blocks)
    from render_docs import key_numbers
    meth = (ROOT / "deliverables/round1-methodology.md").read_text().split("<!-- results-table:begin -->")[0]
    prose = meth.split("<!-- headline:end -->")[-1]
    for k in ("2w_central", "car_central"):
        if key_numbers(d)[k] not in prose:
            problems.append(f"methodology prose lacks the current {k} number {key_numbers(d)[k]!r}")
    for rel in DOCS:
        p = ROOT / rel
        if p.exists():
            for m in re.finditer(r"<!-- ([a-z-]+):begin -->(.*?)<!-- \1:end -->", p.read_text(), flags=re.S):
                if not m.group(2).strip():
                    problems.append(f"{rel}: marked block '{m.group(1)}' is empty")
    meth_text = (ROOT / "deliverables/round1-methodology.md").read_text()
    if meth_text.count("<!-- results-table:begin -->") != 1:
        problems.append("methodology must contain exactly one results-table block")
    else:
        blk = meth_text.split("<!-- results-table:begin -->")[1].split("<!-- results-table:end -->")[0]
        if blk.count("\n|") < 8:
            problems.append("methodology results table has fewer rows than expected")
    for x in problems:
        print("DRIFT", x)
    print("docs OK" if not problems else f"{len(problems)} drift problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
