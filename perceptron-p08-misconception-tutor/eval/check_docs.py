"""Doc-drift check: numbers in deliverables must come from committed results (hardened after the 4 Oct review).

Run: .venv/bin/python -m eval.check_docs            (exit 1 on any problem)
     .venv/bin/python -m eval.check_docs --selftest (proves the check catches a falsified number)
1. Committed inputs: eval/results/ must have no uncommitted changes, so documents reflect committed results.
2. Fresh render: every rendered artefact (deliverables/*.md and the thought-node selection memo) must equal a
   fresh render of its template, so a hand edit or a stale number fails, even if the wrong number exists elsewhere.
3. Placeholders: every {{claim}} in a template must resolve to a committed result.
4. Strict scan: every decimal number in a rendered artefact must be one of the rendered claim values or a listed
   design constant (not merely any number found somewhere in the results).
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

from eval import render_docs
from eval.numbers import claims

ROOT = pathlib.Path(__file__).resolve().parents[1]
DESIGN_CONSTANTS = {"0.75", "0.5", "2.0"}  # remediation threshold, decision threshold, schema versions
IGNORE = [r"(?i)gpt-[\d.]+(-mini)?", r"Opus \d+\.\d+", r"Python \d+\.\d+", r"CC BY(-NC)? \d\.\d", r"v\d+(\.\d+)+",
          r"\d+\.\d+\.\d+", r"\b20\d\d-\d\d-\d\d\b", r"\d+:\d+"]
NUM = re.compile(r"(?<![\w.])\d+\.\d+(?![\w.])")


def scan(text: str) -> list[str]:
    for pat in IGNORE:
        text = re.sub(pat, " ", text)
    return NUM.findall(text)


def check(cl: dict, files: dict[pathlib.Path, str] | None = None) -> list[str]:
    problems = []
    out, missing = render_docs.outputs(cl)
    problems += [f"NO-RESULT placeholder {k}" for k in missing]
    ok_vals = DESIGN_CONSTANTS | {n for v in cl.values() for n in NUM.findall(v.replace("$", " "))}
    for path, expected in out.items():
        rel = path.relative_to(ROOT)
        actual = (files or {}).get(path, path.read_text() if path.exists() else None)
        if actual != expected:
            problems.append(f"STALE {rel}: differs from a fresh render of its template")
        region = expected
        if path.name == "thought_node.md":
            i, j = expected.find(render_docs.MEMO_START), expected.find(render_docs.MEMO_END)
            region = expected[i:j]
        problems += [f"UNSOURCED {rel}: {n}" for n in sorted(set(scan(region))) if n not in ok_vals]
    return problems


def committed_inputs() -> list[str]:
    r = subprocess.run(["git", "status", "--porcelain", "--", "eval/results"], cwd=ROOT, capture_output=True, text=True)
    return [f"UNCOMMITTED {line.strip()}" for line in r.stdout.splitlines() if line.strip()]


def selftest() -> int:
    cl = claims()
    out, _ = render_docs.outputs(cl)
    abstract = ROOT / "deliverables" / "round1-abstract.md"
    target = cl["diag.gpt-5.5.cost1000_cascade"]
    falsified = out[abstract].replace(target, cl["diag.gpt-5.5.cost1000_llm"], 1)  # the reviewer's "$7.32 -> $7.32" edit
    caught = any("STALE" in p for p in check(cl, {abstract: falsified}))
    print(f"selftest: falsified '{target}' -> '{cl['diag.gpt-5.5.cost1000_llm']}' in the abstract: {'CAUGHT' if caught else 'MISSED'}")
    return 0 if caught else 1


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if "--selftest" in args:
        return selftest()
    cl = claims()
    problems = committed_inputs() + check(cl)
    for p in problems:
        print(p)
    print(f"check_docs: {'OK' if not problems else 'FAIL'} ({len(problems)} problems; {len(cl)} claims)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
