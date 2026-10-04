"""Check that every precise number quoted in the docs appears in a committed results file.

    cd perceptron-p04-lob-regimes && python eval/check_numbers.py

A "precise number" is any decimal with >= 3 decimals (log-loss, AUC, deltas, CI bounds) or any
decimal followed by "bps". Each must occur, after normalising the minus sign, in eval/results/*.md,
or equal (to its printed precision) a value in eval/results/*.json. The script exits non-zero and
lists every unmatched number; the doc is then fixed, not the check.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ["deliverables/round1-abstract.md", "deliverables/architecture.md", "deliverables/qa-prep.md",
        "architecture/adr/001-spike.md",
        "research/landscape.md", "thought_node.md"]
CONSTANTS = {"0.6931": "ln 2"}
NUM = re.compile(r"(?<![\w.])[+\-−]?\d+\.\d{3,}(?![\d])|(?<![\w.])[+\-−]?\d+\.\d{1,3}(?=\s?bps)")


def norm(x: str) -> str:
    return x.replace("−", "-").lstrip("+")


def json_values(obj, out: set) -> None:
    if isinstance(obj, dict):
        for v in obj.values():
            json_values(v, out)
    elif isinstance(obj, list):
        for v in obj:
            json_values(v, out)
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        for nd in (1, 2, 3, 4):
            out.add(f"{obj:.{nd}f}")


def main() -> int:
    pool_md: set[str] = set()
    pool_json: set[str] = set()
    for p in (ROOT / "eval" / "results").glob("*.md"):
        pool_md.update(norm(m.group(0)) for m in re.finditer(r"[+\-−]?\d+\.\d+", p.read_text()))
    for p in (ROOT / "eval" / "results").glob("*.json"):
        json_values(json.loads(p.read_text()), pool_json)
    pool_md |= {x.lstrip("-") for x in pool_md}
    pool_json |= {x.lstrip("-") for x in pool_json}
    allow = set()
    allow_path = ROOT / "eval" / "check_numbers_allow.tsv"
    if allow_path.exists():
        for row in allow_path.read_text().splitlines()[1:]:
            if row.strip():
                doc_, num_, _reason = row.split("\t")
                allow.add((doc_, num_))
    bad = []
    n = 0
    for doc in DOCS:
        path = ROOT / doc
        if not path.exists():
            continue
        text = path.read_text()
        if doc == "thought_node.md":  # only the current-state sections, not the historical log
            text = text.split("## Log")[0]
        for ln_no, line in enumerate(text.splitlines(), 1):
            for m in NUM.finditer(line):
                n += 1
                v = norm(m.group(0))
                if re.fullmatch(r"\d{4}\.\d{4,5}", v) or v in CONSTANTS or (doc, m.group(0)) in allow:
                    continue  # arXiv IDs, math constants, numbers quoted from external sources
                if v in pool_md or v in pool_json or v.lstrip("-") in pool_md or v.lstrip("-") in pool_json:
                    continue
                bad.append(f"{doc}:{ln_no}: {m.group(0)}  …{line.strip()[:90]}")
    print(f"checked {n} quoted numbers in {len(DOCS)} docs against eval/results/*")
    for b in bad:
        print("UNMATCHED", b)
    print("OK" if not bad else f"{len(bad)} unmatched")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
