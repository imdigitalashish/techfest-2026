"""Doc-drift check: numbers in deliverables must come from committed results.

Run: .venv/bin/python -m eval.check_docs        (exit 1 on drift)
1. Strict scan: every decimal number (e.g. 86.0, 0.326) in the checked documents must be rendered from a
   committed result (eval/numbers.allowed) or be a listed design constant.
2. Required claims: each named headline claim (eval/numbers.claims) listed for a document must appear in it
   verbatim, so a re-run that changes a headline number breaks the check until the document is updated.
"""
from __future__ import annotations

import pathlib
import re
import sys

from eval.numbers import allowed, claims

ROOT = pathlib.Path(__file__).resolve().parents[1]

# (path, start marker, end marker): only the slice between the markers is scanned (None = whole file)
DOCS = [
    ("deliverables/round1-abstract.md", None, None),
    ("deliverables/architecture.md", None, None),
    ("thought_node.md", "## Selection memo", "## Log"),
]
REQUIRED = {
    "deliverables/round1-abstract.md": [
        "closed5.llm41", "real.exec_fcr", "real.gpt-5.5.fcr", "real.gpt-4.1-mini.fcr",
        "real.gated.gpt-5.5.ba", "real.gpt-5.5.ba", "inv.gpt-5.5.L3", "trace.tracer_exact", "sim.ours_left", "sim.random_left",
    ],
    "thought_node.md": ["real.exec_fcr", "real.gpt-5.5.fcr"],
}
DESIGN_CONSTANTS = {"0.75", "0.5", "2.0"}  # remediation threshold, decision threshold, contract/schema versions
IGNORE = [r"(?i)gpt-[\d.]+(-mini)?", r"Opus \d+\.\d+", r"Python \d+\.\d+", r"CC BY(-NC)? \d\.\d", r"v\d+(\.\d+)+",
          r"\d+\.\d+\.\d+", r"\b20\d\d-\d\d-\d\d\b", r"\d+:\d+"]
NUM = re.compile(r"(?<![\w.])\d+\.\d+(?![\w.])")


def scan(text: str) -> list[str]:
    for pat in IGNORE:
        text = re.sub(pat, " ", text)
    return NUM.findall(text)


def main() -> int:
    ok_vals = allowed() | DESIGN_CONSTANTS
    cl = claims()
    failures = 0
    for path, start, end in DOCS:
        p = ROOT / path
        if not p.exists():
            print(f"MISSING  {path}")
            failures += 1
            continue
        text = p.read_text()
        if start:
            i = text.find(start)
            j = text.find(end, i + 1) if end else -1
            text = text[i: j if j > 0 else None] if i >= 0 else ""
        bad = sorted({n for n in scan(text) if n not in ok_vals})
        for n in bad:
            print(f"UNSOURCED {path}: {n}")
        failures += len(bad)
        for name in REQUIRED.get(path, []):
            if name not in cl:
                print(f"NO-RESULT {path}: claim {name} has no committed result")
                failures += 1
            elif cl[name] not in text:
                print(f"DRIFT     {path}: claim {name} = {cl[name]} not found")
                failures += 1
    print(f"check_docs: {'OK' if failures == 0 else 'FAIL'} ({failures} problems; {len(ok_vals)} allowed values, {len(cl)} claims)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
