"""Doc-drift and claim-provenance check for the Round-1 deliverables. Exit code 1 on any problem.

1. Drift: every rendered deliverable equals what eval/render_docs.py renders now from deliverables/src/ + committed results.
2. Binding: in every {{v:ID|text}} placeholder, row ID exists in research/fact-check.md and each number in `text` appears in
   that row (claim-level binding, not a file-wide match).
3. Unmarked numbers: in the templates, every significant number (≥ 4 digits, a decimal, or a percentage) outside
   placeholders is flagged. Scoped exceptions: lines containing UNVERIFIED, years / ISO dates / year ranges, clock times,
   thresholds after ≥ ≤ < > ~, version strings (v2.1), units glued to a model/part name (ESP32-S3, SX1262, IN865).
4. Stale: superseded numbers (STALE) must not appear in current-state text (rendered deliverables, the current part of
   thought_node.md, landscape, components).
Usage (from innovatex-t2-aqi/): python3 eval/check_docs.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_docs import OUT, PH, ROOT, SRC, TEMPLATES, render_all  # noqa: E402

STALE = ["36.2 µg", "77.0 →", "77.0 µg", "33.8 ± 2.6", "97.8 ± 15.6", "58.0 ± 16.0", "−65 %", "-65%", "−42 %", "-42%", "65 %",
         "tamper-proof", "can't be edited", "so clean sites can keep working", "close to its data limit", "24.1 µg/m³ (r 0.90"]
CURRENT = ["research/landscape.md", "architecture/components.md"]
NUM = re.compile(r"(?<![\w.\-/])(\d{1,3}(?:,\d{2,3})+(?:\.\d+)?|\d+\.\d+|\d{4,}|\d+(?:\.\d+)?\s?%)(?![\w])")
SKIP_BEFORE = re.compile(r"(≥|≤|<|>|~|±|v|×|§|Table|Figure|below|above|under|over|ESP|SX|IN|SHT|PMS|SDS|SPS|SEN|A|F|B|C|S)\s*$")


def numbers(text: str) -> list[str]:
    return [m.group(1) for m in NUM.finditer(text)]


def norm(s: str) -> str:
    return s.replace("\u2009", " ").replace("–", "-").replace("−", "-").replace(" %", "%").replace(",", "")


def fact_rows() -> dict[str, str]:
    rows = {}
    for line in (ROOT / "research" / "fact-check.md").read_text().splitlines():
        m = re.match(r"^\|\s*(F\d+)\s*\|(.*)$", line)
        if m:
            rows[m.group(1)] = norm(m.group(2))
    return rows


def main() -> int:
    problems: list[str] = []
    rendered = render_all()
    for name, text in rendered.items():
        disk = (OUT / name).read_text() if (OUT / name).exists() else ""
        if disk != text:
            problems.append(f"DRIFT {name}: rendered file differs from template + results (run eval/render_docs.py)")
    rows = fact_rows()
    for name in TEMPLATES:
        p = SRC / name
        if not p.exists():
            continue
        src = p.read_text()
        for m in PH.finditer(src):
            if m.group(1) != "v":
                continue
            fid, text = m.group(2).strip(), m.group(3) or ""
            if fid not in rows:
                problems.append(f"BIND {name}: unknown fact row {fid}")
                continue
            for n in numbers(text) + re.findall(r"\d+", text):
                if norm(n) not in rows[fid]:
                    problems.append(f"BIND {name}: '{n}' in {{{{v:{fid}|{text}}}}} not found in fact row {fid}")
        for i, line in enumerate(src.splitlines(), 1):
            if "UNVERIFIED" in line:
                continue
            bare = PH.sub(" ", line)
            bare = re.sub(r"`[^`]*`", " ", bare)
            bare = re.sub(r"!\[[^\]]*\]", " ", bare)  # Marp image directives (bg right:40%)
            bare = re.sub(r"\(https?://[^)]*\)|https?://\S+", " ", bare)
            for m in NUM.finditer(bare):
                tok = m.group(1)
                before = bare[: m.start()]
                if re.fullmatch(r"(19|20)\d{2}", tok) or re.search(r"\d{4}-$", before) or SKIP_BEFORE.search(before):
                    continue
                problems.append(f"UNMARKED {name}:{i}: '{tok}' — bind it ({{{{n:…}}}} / {{{{v:F…|…}}}}) or rephrase")
    targets = {f"deliverables/{n}": t for n, t in rendered.items()}
    tn = (ROOT / "thought_node.md").read_text().split("\n## Log", 1)[0]
    targets["thought_node.md (current part)"] = tn
    for rel in CURRENT:
        targets[rel] = (ROOT / rel).read_text()
    for rel, text in targets.items():
        text = "\n".join(ln for ln in text.splitlines() if "Never say" not in ln)  # explicit do-not-say lists are allowed
        for s in STALE:
            if s in text:
                problems.append(f"STALE {rel}: contains superseded '{s}'")
    memo = tn.split("## Selection memo", 1)[-1].split("\n## ", 1)[0]
    k = __import__("render_docs").keys()
    for key in ["at_pair", "at_ring", "at_selfcal", "at_gain_selfcal_vs_refcal_pct", "bom_kit", "pw_load", "pw_margin", "calm_lt10_winter_pct"]:
        if k[key] not in memo:
            problems.append(f"MEMO thought_node.md Selection memo: run number {key} = {k[key]} not found (memo out of date?)")
    for p in problems:
        print(p)
    print(f"check_docs: {len(problems)} problem(s) in {len(rendered)} rendered docs, {len(rows)} fact rows")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
