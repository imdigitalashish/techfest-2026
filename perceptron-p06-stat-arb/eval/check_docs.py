"""Doc-drift check: every number quoted in the deliverables must trace to committed results.

0. Rebuilds eval/results/headline.json from the committed result files (eval/headline.py) and fails if it differs.
1. Re-renders deliverables/round1-abstract.md and architecture.md from their templates + eval/results/headline.json
   and fails if a committed file differs (a number edited by hand, or results changed without re-rendering).
2. Scans the abstract, the architecture page and the selection memo for numeric tokens. Each must equal a value
   rendered from headline.json or appear in deliverables/static_numbers.tsv (token, source); otherwise it is
   reported as untraced and the check fails.
3. The abstract body (from "Problem and theme" on) must be 600–900 words (the brief's suggested length).
Run (from perceptron-p06-stat-arb/): .venv/bin/python eval/check_docs.py
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "deliverables"))
sys.path.insert(0, str(ROOT))
from render import headline, render  # noqa: E402

from eval.headline import build as build_headline  # noqa: E402

NUM = re.compile(r"(?<![\w./])[−+-]?\$?\d[\d,]*(?:\.\d+)?%?")
DATES = re.compile(r"\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}(?::\d{2})?)?|\b\d{1,2}:\d{2}(?::\d{2})?\b|\b[0-9a-f]{7,40}\b")
WORDS = re.compile(r"[A-Za-z0-9$+\-−–.,%/≥≤()'’µ]+")


def norm(tok: str) -> str:
    return tok.replace("−", "-").replace(",", "").replace("$", "").lstrip("+").rstrip("%").rstrip(".")


def tokens(text: str) -> list[str]:
    text = DATES.sub(" ", text)
    text = re.sub(r"`[^`]*`", " ", text)          # code/paths/commands are not claims
    text = re.sub(r"\]\([^)]*\)", "]", text)        # link targets
    return [norm(t) for t in NUM.findall(text)]


def memo_section() -> str:
    s = (ROOT / "thought_node.md").read_text()
    a = s.index("## Selection memo")
    b = s.index("\n## ", a + 5)
    return s[a:b]


def main() -> int:
    ok = True
    fresh = build_headline()
    if fresh != headline():
        ok = False
        diff = sorted(k for k in set(fresh) | set(headline()) if fresh.get(k) != headline().get(k))
        print(f"STALE: eval/results/headline.json differs from a fresh build from the result files: {diff}")
    rendered = render()
    for name, text in rendered.items():
        cur = (ROOT / "deliverables" / name).read_text()
        if cur != text:
            ok = False
            print(f"DRIFT: deliverables/{name} differs from its rendered template (run deliverables/render.py)")
    allowed = set()
    for v in headline().values():
        allowed.update(tokens(str(v)))
    static = {}
    with open(ROOT / "deliverables" / "static_numbers.tsv") as f:
        for row in csv.reader(f, delimiter="\t"):
            if row and not row[0].startswith("#"):
                static[norm(row[0])] = row[1] if len(row) > 1 else ""
    allowed.update(static)
    docs = {"deliverables/round1-abstract.md": (ROOT / "deliverables" / "round1-abstract.md").read_text(),
            "deliverables/architecture.md": (ROOT / "deliverables" / "architecture.md").read_text(),
            "thought_node.md#selection-memo": memo_section()}
    for name, text in docs.items():
        bad = sorted({t for t in tokens(text) if t not in allowed})
        if bad:
            ok = False
            print(f"UNTRACED in {name}: {', '.join(bad)}")
    body = docs["deliverables/round1-abstract.md"].split("**Problem and theme.**", 1)[-1]
    n = len(WORDS.findall(body))
    if not 600 <= n <= 900:
        ok = False
    print(f"abstract body words: {n} (600–900)")
    print("check_docs:", "OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
