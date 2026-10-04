"""Render deliverables from templates: every {{claim.name}} is replaced by the value from eval/numbers.claims().

Run: .venv/bin/python -m eval.render_docs          (writes; fails if a placeholder has no committed result)
     .venv/bin/python -m eval.render_docs --check  (writes nothing; exit 1 if any rendered output differs from disk)
Templates: deliverables/templates/*.md -> deliverables/*.md. The selection memo is also rendered into
thought_node.md between the MEMO_START / MEMO_END markers, so hand edits to it are detected.
"""
from __future__ import annotations

import pathlib
import re
import sys

from eval.numbers import claims

ROOT = pathlib.Path(__file__).resolve().parents[1]
TPL = ROOT / "deliverables" / "templates"
PH = re.compile(r"\{\{([A-Za-z0-9_.\-]+)\}\}")
MEMO_START = "<!-- MEMO_START: rendered from deliverables/templates/selection-memo.md by `python -m eval.render_docs` -->"
MEMO_END = "<!-- MEMO_END -->"


def render(text: str, cl: dict) -> tuple[str, list[str]]:
    missing = []

    def sub(m):
        k = m.group(1)
        if k not in cl:
            missing.append(k)
            return m.group(0)
        return cl[k]

    return PH.sub(sub, text), missing


def outputs(cl: dict | None = None) -> tuple[dict[pathlib.Path, str], list[str]]:
    """Return {path: full expected file content} for every rendered artefact, plus missing placeholders."""
    cl = cl or claims()
    out, missing = {}, []
    memo = None
    for t in sorted(TPL.glob("*.md")):
        body, miss = render(t.read_text(), cl)
        missing += [f"{t.name}:{k}" for k in miss]
        out[ROOT / "deliverables" / t.name] = (
            f"<!-- GENERATED from deliverables/templates/{t.name} by `python -m eval.render_docs`; edit the template, not this file. -->\n" + body)
        if t.name == "selection-memo.md":
            memo = body
    tn = ROOT / "thought_node.md"
    if memo is not None and tn.exists():
        s = tn.read_text()
        i, j = s.find(MEMO_START), s.find(MEMO_END)
        if i >= 0 and j > i:
            out[tn] = s[: i + len(MEMO_START)] + "\n" + memo.rstrip("\n") + "\n" + s[j:]
    return out, missing


def main(argv=None) -> int:
    check = "--check" in (argv if argv is not None else sys.argv[1:])
    out, missing = outputs()
    for k in missing:
        print(f"MISSING claim {k}")
    stale = 0
    for path, text in out.items():
        rel = path.relative_to(ROOT)
        if check:
            if not path.exists() or path.read_text() != text:
                print(f"STALE     {rel} differs from a fresh render (edited by hand, or results changed)")
                stale += 1
        else:
            path.write_text(text)
            print(f"rendered {rel}")
    return 1 if (missing or stale) else 0


if __name__ == "__main__":
    sys.exit(main())
