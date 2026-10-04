"""Doc-drift and claim-provenance check for the Round-1 deliverables. Exit code 1 on any problem.

1. Drift: every rendered deliverable equals what eval/render_docs.py renders now from deliverables/src/ + committed results.
2. Results: every {{r:alias}} resolves (eval/doc_numbers.py).
3. Binding: every {{f:ID|text}} names a row in research/fact-check.md, and every number in `text` appears in that row.
4. Markers: rendered deliverables contain no ⟨FILL⟩ / [V] / TODO markers (team fields use ‹…› placeholders instead).
5. Stale: superseded numbers or banned phrases must not appear in rendered deliverables (except on lines that say
   "Don't say") or in the current part of thought_node.md.
6. Unmarked numbers: in templates, significant numbers (≥4 digits, a decimal, a comma group or a percentage) outside
   placeholders are flagged. Scoped exceptions: URLs; years, ISO dates, year ranges and clock/slide times; lines marked
   UNVERIFIED or ASSUMPTION; Marp image directives; the phrase "90% interval"; self-cited table rows (a row that carries its own URL and a 2026-10-0x access date).
Usage: python3 innovatex-t3-coastal-plastic/eval/check_docs.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from doc_numbers import ALIASES, COMPUTED, value  # noqa: E402
from render_docs import OUT, PH, ROOT, TEMPLATES, render_all  # noqa: E402

STALE = ["2.2%", "2.2 %", "13.5%", "29 of 40", "29/40", "⟨FILL", "**[V", "[V]", "tamper-proof", "blockchain",
         "cannot flood", "can't flood"]
NUM = re.compile(r"(?<![\w.\-/₹])(\d{1,3}(?:,\d{2,3})+(?:\.\d+)?|\d+\.\d+|\d{4,}|\d+(?:\.\d+)?\s?%)(?![\w])")
EXEMPT_LINE = re.compile(r"UNVERIFIED|ASSUMPTION")
SELF_CITED = re.compile(r"https?://\S+.*2026-10-0\d|2026-10-0\d.*https?://")
YEARLIKE = re.compile(r"^(19|20)\d\d$")
URL = re.compile(r"https?://\S+")
IMG = re.compile(r"!\[[^\]]*\]")  # Marp image directives such as ![bg right:46% fit]
INTERVAL_DEF = re.compile(r"\b90\s?% interval")
VERSIONS = re.compile(r"\bCC BY(?:-[A-Z]+)*\s\d+(?:\.\d+)+|\b[Vv]ersion\s\d+(?:\.\d+)+")  # licence/version strings
TIMES = re.compile(r"\b\d{1,2}:\d{2}(?:[–-]\d{1,2}:\d{2})?\b|\b\d{4}-\d{2}-\d{2}\b|\b(?:19|20)\d\d[–-](?:19|20)?\d\d\b")


def norm(s: str) -> str:
    return (s.replace("\u2009", " ").replace("\u202f", " ").replace("–", "-").replace("−", "-")
            .replace(" %", "%").replace(",", ""))


def nums(text: str) -> list[str]:
    return [m.group(1) for m in NUM.finditer(text)]


def fact_rows() -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in (ROOT / "research" / "fact-check.md").read_text().splitlines():
        m = re.match(r"^\|\s*([FD]\d+)\s*\|(.*)$", line)
        if m:
            rows[m.group(1)] = m.group(2)
    return rows


def main() -> int:
    problems: list[str] = []
    rendered = render_all()  # raises on an unknown alias (check 2)

    for path, text in rendered.items():  # 1. drift
        if not path.exists():
            problems.append(f"drift: {path.relative_to(ROOT)} missing; run eval/render_docs.py")
        elif path.read_text() != text:
            problems.append(f"drift: {path.relative_to(ROOT)} differs from its template + committed results; re-render")

    rows = fact_rows()
    for src in TEMPLATES:  # 3. binding, 6. unmarked numbers
        tpl = src.read_text()
        for m in PH.finditer(tpl):
            kind, key, txt = m.group(1), m.group(2).strip(), m.group(3) or ""
            if kind == "r" and key not in ALIASES and key not in COMPUTED:
                problems.append(f"{src.name}: unknown result alias {key}")
            if kind == "f":
                if key not in rows:
                    problems.append(f"{src.name}: unknown fact id {key}")
                    continue
                row = norm(rows[key])
                for n in nums(txt):
                    if norm(n) not in row:
                        problems.append(f"{src.name}: {key} text cites {n!r}, not found in its fact-check row")
        for i, line in enumerate(tpl.splitlines(), 1):
            if EXEMPT_LINE.search(line) or SELF_CITED.search(line):
                continue
            bare = PH.sub(" ", line)
            bare = URL.sub(" ", bare)
            bare = IMG.sub(" ", bare)
            bare = INTERVAL_DEF.sub(" ", bare)
            bare = VERSIONS.sub(" ", bare)
            bare = TIMES.sub(" ", bare)
            for n in nums(bare):
                if YEARLIKE.match(n.replace(",", "")):
                    continue
                problems.append(f"{src.name}:{i}: unmarked number {n!r} (bind it with {{{{f:..}}}} or {{{{r:..}}}})")

    current = [p for p in rendered]  # 4. markers + 5. stale
    tn = (ROOT / "thought_node.md").read_text()
    tn_current = tn.split("## Log", 1)[0]
    for path in current:
        text = path.read_text() if path.exists() else ""
        for line in text.splitlines():
            if re.search(r"don'?t say|DON'T SAY", line, re.I):
                continue  # a line that tells the presenter what NOT to say may quote the banned phrase
            for s in STALE:
                if s in line:
                    problems.append(f"stale/marker {s!r} in {path.relative_to(ROOT)}: {line[:60]!r}")
    for s in STALE[:4]:
        if s in tn_current:
            problems.append(f"stale {s!r} in the current part of thought_node.md")

    for p in problems:
        print("FAIL", p)
    print(f"check_docs: {len(problems)} problem(s) across {len(TEMPLATES)} template(s), {len(rows)} fact rows, "
          f"{len(ALIASES)} result aliases")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
