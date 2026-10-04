"""Build a TRL-labelled text dataset from fetched TechPort records.

Reads .data/techport/raw/*.json.gz (see fetch_techport.py) and writes
.data/techport/techport_trl.jsonl with one row per project that has text and a TRL label.
Text = title + description + benefits (HTML stripped). Metadata is kept for analysis only;
models must use text only (the hidden set is raw documents without TechPort metadata).

Usage: python data/techport/build_dataset.py
"""
from __future__ import annotations

import collections
import glob
import gzip
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / ".data" / "techport"
TAG = re.compile(r"<[^>]+>")
WS = re.compile(r"\s+")


def clean(s: str | None) -> str:
    if not s:
        return ""
    return WS.sub(" ", html.unescape(TAG.sub(" ", s))).strip()


def trl(v) -> int | None:
    try:
        v = int(v)
    except (TypeError, ValueError):
        return None
    return v if 1 <= v <= 9 else None


def main() -> None:
    rows, n_raw = [], 0
    for fp in sorted(glob.glob(str(ROOT / "raw" / "*.json.gz"))):
        n_raw += 1
        with gzip.open(fp, "rt", encoding="utf-8") as f:
            p = json.load(f).get("project", {})
        title, desc, ben = clean(p.get("title")), clean(p.get("description")), clean(p.get("benefits"))
        row = {
            "id": p.get("projectId"),
            "title": title,
            "description": desc,
            "benefits": ben,
            "text": " \n".join(x for x in (title, desc, ben) if x),
            "trl_begin": trl(p.get("trlBegin")),
            "trl_current": trl(p.get("trlCurrent")),
            "trl_end": trl(p.get("trlEnd")),
            "status": p.get("status"),
            "program": (p.get("program") or {}).get("acronym") or (p.get("program") or {}).get("title"),
            "start_year": p.get("startYear"),
            "end_year": p.get("endYear"),
            "primary_tx": (p.get("primaryTx") or {}).get("code"),
        }
        if len(desc) >= 200 and any(row[k] for k in ("trl_begin", "trl_current", "trl_end")):
            rows.append(row)
    out = ROOT / "techport_trl.jsonl"
    with out.open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"raw records: {n_raw}; usable (desc>=200 chars and >=1 TRL label): {len(rows)} -> {out}")
    for k in ("trl_begin", "trl_current", "trl_end"):
        c = collections.Counter(r[k] for r in rows if r[k])
        print(k, "n=%d" % sum(c.values()), dict(sorted(c.items())))
    print("status", collections.Counter(r["status"] for r in rows).most_common(5))


if __name__ == "__main__":
    main()
