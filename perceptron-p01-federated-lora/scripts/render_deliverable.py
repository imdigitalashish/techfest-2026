#!/usr/bin/env python3
"""Render a deliverable template, filling {{key|format}} from committed results.

Usage: python scripts/render_deliverable.py deliverables/round1-abstract.template.md deliverables/round1-abstract.md --tag v2

`key` is a key of eval/results/<tag>_canonical.json or <tag>_dropout_canonical.json (or const.*).
`format` is a Python format spec, optionally prefixed by `abs` (absolute value) and/or `pct` (× 100),
e.g. {{dropout.anchor_full.macro_mean|.3f}}, {{dropout.spike_vs_fedavg_ab_homo.macro_lo|+.3f}},
{{dropout.fedavg_ab_homo.agg_err_mean|pct.0f}}. Expressions min(...)/max(...) over several keys are allowed:
{{max(clean.fedavg_ab_het.agg_err_mean,dropout.fedavg_ab_het.agg_err_mean)|pct.0f}}.
Missing keys are a hard error, so a deliverable can never ship a number that is not in the results.
Afterwards the body word count is printed (text between '### Problem' and the first '---' line).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_numbers import load  # noqa: E402

PAT = re.compile(r"\{\{\s*([^|}]+?)\s*(?:\|\s*([^}]+?))?\s*\}\}")


def value(expr: str, canon: dict) -> float:
    m = re.fullmatch(r"(min|max)\((.+)\)", expr)
    if m:
        vals = [canon[k.strip()] for k in m.group(2).split(",")]
        return min(vals) if m.group(1) == "min" else max(vals)
    return canon[expr]


def render(text: str, canon: dict) -> str:
    def sub(m: re.Match) -> str:
        expr, fmt = m.group(1), (m.group(2) or "")
        v = value(expr, canon)
        if fmt.startswith("abs"):
            v, fmt = abs(v), fmt[3:]
        if fmt.startswith("pct"):
            v, fmt = 100 * v, fmt[3:]
        return format(v, fmt)

    return PAT.sub(sub, text)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("template")
    ap.add_argument("out")
    ap.add_argument("--tag", default="v2")
    args = ap.parse_args()
    canon = load(args.tag)
    try:
        out = render(Path(args.template).read_text(), canon)
    except KeyError as e:
        sys.exit(f"missing result key: {e}")
    Path(args.out).write_text(out)
    body = out.split("### Problem", 1)[-1].split("\n---\n")[0]
    print(f"rendered {args.out}: body words = {len(('### Problem' + body).split())}")


if __name__ == "__main__":
    main()
