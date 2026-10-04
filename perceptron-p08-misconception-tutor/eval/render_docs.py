"""Render deliverables from templates: every {{claim.name}} is replaced by the value from eval/numbers.claims().

Run: .venv/bin/python -m eval.render_docs   (fails if a placeholder has no committed result)
Templates: deliverables/templates/*.md  ->  deliverables/*.md
"""
from __future__ import annotations

import pathlib
import re
import sys

from eval.numbers import claims

ROOT = pathlib.Path(__file__).resolve().parents[1]
TPL = ROOT / "deliverables" / "templates"
PH = re.compile(r"\{\{([A-Za-z0-9_.\-]+)\}\}")


def render(text: str, cl: dict) -> tuple[str, list[str]]:
    missing = []

    def sub(m):
        k = m.group(1)
        if k not in cl:
            missing.append(k)
            return m.group(0)
        return cl[k]

    return PH.sub(sub, text), missing


def main() -> int:
    cl = claims()
    bad = 0
    for t in sorted(TPL.glob("*.md")):
        out, missing = render(t.read_text(), cl)
        for k in missing:
            print(f"MISSING claim {k} in {t.name}")
        bad += len(missing)
        (ROOT / "deliverables" / t.name).write_text(
            f"<!-- GENERATED from deliverables/templates/{t.name} by `python -m eval.render_docs`; edit the template, not this file. -->\n" + out)
        print(f"rendered deliverables/{t.name}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
