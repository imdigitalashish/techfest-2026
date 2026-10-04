"""Doc-drift check: fails (exit 1) if a deliverable or results report is stale or has untraceable numbers.

Checks
1. Every deliverables/*.template.md re-renders exactly to its committed .md (numbers come from eval/results/*.json).
2. Every eval/results/<tag>.json with a v1-style report re-renders exactly to eval/results/<tag>.md.
3. The Round-1 abstract body is 600-900 words (the official suggested length), tables included.
4. Templates contain no hard-coded percentages outside placeholders, except the whitelist below
   (design constants such as the 90% target, quantile levels and the trimming fraction).

    cd perceptron-p10-trusted-text-signal && PYTHONPATH=. .venv/bin/python deliverables/check_drift.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from deliverables.render import PH, ROOT, render_text, targets  # noqa: E402

WHITELIST = {"90%", "5%", "50%", "95%", "20%", "40%", "0.5%", "1%", "100%"}  # design constants: target coverage, quantile levels, trim fraction, label-flip rates
REPORTS_V1 = ["baseline_v1", "text_minilm_v1"]


def main() -> int:
    bad = []
    for tpl, out in targets():
        t = tpl.read_text()
        if not out.exists() or render_text(t) != out.read_text():
            bad.append(f"stale render: {out.relative_to(ROOT)} (run deliverables/render.py)")
        stripped = PH.sub("", t)
        for pct in sorted(set(re.findall(r"(?<![\w.])\d+(?:\.\d+)?%", stripped)) - WHITELIST):
            bad.append(f"hard-coded number {pct!r} in {tpl.name}: use a placeholder")
        if "abstract" in out.name and out.exists():
            body = out.read_text().split("**Problem & theme.**", 1)[-1]
            words = len(re.findall(r"\S+", "\n".join(l for l in body.splitlines() if not l.startswith("|---"))))
            if not 600 <= words <= 900:
                bad.append(f"{out.name}: {words} words (allowed 600-900)")
            else:
                print(f"{out.name}: {words} words")
    for tag in REPORTS_V1:
        js, md = ROOT / "eval/results" / f"{tag}.json", ROOT / "eval/results" / f"{tag}.md"
        if not js.exists():
            continue
        before = md.read_text() if md.exists() else ""
        subprocess.run([sys.executable, str(ROOT / "eval/report.py"), tag], cwd=ROOT, check=True, capture_output=True)
        if md.read_text() != before:
            bad.append(f"stale report: eval/results/{tag}.md (re-rendered now; commit it)")
    for b in bad:
        print("DRIFT:", b)
    print("OK — no drift" if not bad else f"{len(bad)} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
