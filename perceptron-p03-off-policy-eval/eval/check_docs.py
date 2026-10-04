"""Doc-drift check: every number quoted in the deliverables must trace to committed results.

1. Re-renders deliverables/round1-abstract.md from its template + eval/results/headline.json and fails if the
   committed file differs (someone edited a number by hand, or results changed without re-rendering).
2. Scans the checked documents for numeric tokens. Each must equal a value rendered from headline.json, or appear in
   deliverables/static_numbers.tsv (number, source). Anything else is reported as untraced and fails the check.
Run: cd perceptron-p03-off-policy-eval && .venv/bin/python eval/check_docs.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "deliverables"))
from render import render  # noqa: E402

NUM = re.compile(r"(?<![\w./])[−+-]?\d[\d,]*(?:\.\d+)?(?:/\d+)?%?")
CHECKED = [ROOT / "deliverables" / "round1-abstract.md"]


def memo_section() -> str:
    s = (ROOT / "thought_node.md").read_text()
    a = s.index("## Selection memo")
    b = s.index("\n## ", a + 5)
    return s[a:b]


def norm(tok: str) -> str:
    return tok.replace("−", "-").replace(",", "").lstrip("+")


def main() -> int:
    ok = True
    rendered = render()
    committed = (ROOT / "deliverables" / "round1-abstract.md").read_text()
    if rendered != committed:
        print("DRIFT: deliverables/round1-abstract.md differs from a fresh render (run deliverables/render.py)")
        ok = False
    values = {norm(v) for v in json.loads((ROOT / "eval" / "results" / "headline.json").read_text())["display"].values()}
    static = {}
    for line in (ROOT / "deliverables" / "static_numbers.tsv").read_text().splitlines()[1:]:
        if line.strip():
            n, src = line.split("\t", 1)
            static[norm(n)] = src
    texts = [(p.name, p.read_text()) for p in CHECKED] + [("thought_node.md#Selection memo", memo_section())]
    for name, text in texts:
        untraced = []
        for tok in NUM.findall(text):
            t = norm(tok)
            if t in values or t in static or t.rstrip("%") in static:
                continue
            untraced.append(tok)
        print(f"{name}: {len(NUM.findall(text))} numeric tokens, {len(untraced)} untraced{': ' + ', '.join(sorted(set(untraced))) if untraced else ''}")
        ok &= not untraced
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
