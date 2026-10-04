"""Doc-drift and unverified-number check. Exit code 1 on any problem.

1. Every <!--n:KEY-->…<!--/n--> marker equals what eval/render_docs.py renders from eval/results/latest.json.
2. Superseded numbers (STALE) do not appear in current-state text (the append-only Log of thought_node.md is exempt).
3. In the Round-1 deliverables, every significant number (≥ 4 digits, a decimal, or a percentage) is either inside a
   marker, present verbatim in research/fact-check.md (lead-verified external sources), or on a line marked UNVERIFIED.
   Dates, years and identifiers are ignored.
Usage (from ev-c1-infra-map-india/): python3 eval/check_docs.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_docs import DOCS, MARK, ROOT, render  # noqa: E402

STALE = ["8.15%", "2,385", "0.901 → Chapman 0.697", "~20× low", "3,848 stations", "+3,621", "7,776"]
ROUND1 = ["deliverables/round1-methodology.md", "deliverables/round1-roadmap.md"]
NUM = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{2,3})+(?:\.\d+)?|\d+\.\d+|\d{4,}|\d+(?:\.\d+)?\s?%)(?![\w])")
IGNORE = re.compile(r"^(19|20)\d{2}$|^\d{4}-\d{2}")  # years / ISO dates


def current_part(rel: str, text: str) -> str:
    return text.split("\n## Log", 1)[0] if rel == "thought_node.md" else text


def main() -> int:
    latest = json.loads((ROOT / "eval/results/latest.json").read_text())
    verified = (ROOT / "research/fact-check.md").read_text()
    problems = []
    for rel in DOCS:
        p = ROOT / rel
        if not p.exists():
            continue
        t = p.read_text()
        try:
            if render(t, latest) != t:
                problems.append(f"{rel}: a number marker differs from the current run (run eval/render_docs.py)")
        except KeyError as e:
            problems.append(f"{rel}: {e}")
        cur = current_part(rel, t)
        for s in STALE:
            if s in cur:
                problems.append(f"{rel}: superseded number {s!r} in current-state text")
    for rel in ROUND1:
        for i, line in enumerate((ROOT / rel).read_text().splitlines(), 1):
            if "UNVERIFIED" in line or line.lstrip().startswith(("|---", "#")):
                continue
            stripped = MARK.sub(" ", line)
            stripped = re.sub(r"https?://\S+", " ", stripped)
            stripped = re.sub(r"\b(?:PIB|PRID|No\.|IS|Clause|clause)\s*[\d/.-]+", " ", stripped)
            for m in NUM.finditer(stripped):
                tok = m.group(1).strip()
                before = stripped[max(0, m.start() - 12):m.start()]
                if IGNORE.match(tok) or re.search(r"(≥|≤|<|>|~|target|Python|ODbL|CC BY|BY-SA|CDLA-P-|Apache-|maplibre-gl@|v)\s*$", before):
                    continue  # years/dates, targets and thresholds, software/licence versions
                if tok in verified or tok.replace(" ", "") in verified:
                    continue
                problems.append(f"{rel}:{i}: number {tok!r} is neither rendered from a run nor in research/fact-check.md")
    print("\n".join(problems) if problems else f"check_docs: OK ({len(DOCS)} documents, {len(latest)} rendered keys)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
