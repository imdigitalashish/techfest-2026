"""Doc-drift and claim-provenance check. Exit code 1 on any problem.

1. Every <!--n:KEY-->…<!--/n--> marker equals what eval/render_docs.py renders from eval/results/latest.json.
2. Every <!--v:ROW-->…<!--/v--> marker cites an existing row of research/fact-check.md, and each number inside the
   marker appears in THAT row (claim-level binding, not a file-wide substring match).
3. Superseded numbers (STALE) do not appear in current-state text (the append-only Log of thought_node.md is exempt).
4. In the Round-1 deliverables, every significant number (>= 4 digits, a decimal, or a percentage) outside markers is
   flagged — headings included (only a leading section number is skipped). Explicit scoped exceptions: lines marked
   UNVERIFIED, years/ISO dates, thresholds/targets (after ≥ ≤ < > ~), software/licence versions, code spans, interval levels.
Usage (from ev-c1-infra-map-india/): python3 eval/check_docs.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_docs import DOCS, MARK, ROOT, render  # noqa: E402

VMARK = re.compile(r"<!--v:([A-Za-z0-9]+)-->(.*?)<!--/v-->", re.S)
STALE = ["8.15%", "2,385", "0.901 → Chapman 0.697", "~20× low", "3,848 stations", "+3,621", "7,776", "80,833", "3,336 sites",
         "pre-registered pass rule", "Nagpur (most underserved)", "29% more accurate"]
ROUND1 = ["deliverables/round1-methodology.md", "deliverables/round1-roadmap.md"]
NUM = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{2,3})+(?:\.\d+)?|\d+\.\d+|\d{4,}|\d+(?:\.\d+)?\s?%)(?![\w])")
IGNORE = re.compile(r"^(19|20)\d{2}$|^\d{4}-\d{2}")  # years / ISO dates
SKIP_BEFORE = re.compile(r"(≥|≤|<|>|~|§|target|Python|ODbL|CC BY|BY-SA|CDLA-P-|Permissive-|Apache-|maplibre-gl@|within|places|\d-|v)\s*$")


def current_part(rel: str, text: str) -> str:
    return text.split("\n## Log", 1)[0] if rel == "thought_node.md" else text


def fact_rows(text: str) -> dict[str, str]:
    rows = {}
    for line in text.splitlines():
        m = re.match(r"^\|\s*([A-Za-z]?\d+)\s*\|(.*)$", line)
        if m:
            rows[m.group(1)] = m.group(2)
    return rows


def flagged_numbers(line: str) -> list[str]:
    s = MARK.sub(" ", line)
    s = VMARK.sub(" ", s)
    s = re.sub(r"`[^`]*`", " ", s)
    s = re.sub(r"https?://\S+", " ", s)
    s = re.sub(r"\b(?:PIB|PRID|No\.|IS|Clause|clause)\s*[\d/.()a-z-]+", " ", s)
    s = re.sub(r"^\s*#+\s*[A-Z]?\d+(?:\.\d+)*\.?\s", " ", s)  # leading section number of a heading
    out = []
    for m in NUM.finditer(s):
        tok = m.group(1).strip()
        before, after = s[max(0, m.start() - 12):m.start()], s[m.end():m.end() + 14]
        if IGNORE.match(tok) or SKIP_BEFORE.search(before) or re.match(r"\s*(CI|confidence|predictive|interval|range)", after):
            continue
        out.append(tok)
    return out


def main() -> int:
    latest = json.loads((ROOT / "eval/results/latest.json").read_text())
    rows = fact_rows((ROOT / "research/fact-check.md").read_text())
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
        for m in VMARK.finditer(t):
            rid, txt = m.group(1), m.group(2)
            if rid not in rows:
                problems.append(f"{rel}: v-marker cites unknown fact-check row {rid!r}")
                continue
            for tok in [x.group(1).strip() for x in NUM.finditer(txt)] or []:
                if tok not in rows[rid] and tok.replace(" ", "") not in rows[rid]:
                    problems.append(f"{rel}: {tok!r} is not in fact-check row {rid}")
        cur = current_part(rel, t)
        for s in STALE:
            if s in cur:
                problems.append(f"{rel}: superseded text {s!r} in current-state text")
    for rel in ROUND1:
        for i, line in enumerate((ROOT / rel).read_text().splitlines(), 1):
            if "UNVERIFIED" in line or line.lstrip().startswith("|---"):
                continue
            for tok in flagged_numbers(line):
                problems.append(f"{rel}:{i}: number {tok!r} is neither rendered from a run nor bound to a fact-check row")
    print("\n".join(problems) if problems else f"check_docs: OK ({len(DOCS)} documents, {len(latest)} rendered keys, {len(rows)} fact rows)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
