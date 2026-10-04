#!/usr/bin/env python3
"""Fetch arXiv abstract pages and record verified metadata (title, date, comments, abstract head).

Usage: python scripts/verify_arxiv.py research/sources/arxiv_ids.txt research/sources/arxiv_verified.tsv
Every row in the output was read from arxiv.org at the access time recorded in the row.
"""
from __future__ import annotations

import concurrent.futures as cf
import html
import re
import subprocess
import sys
import time
from pathlib import Path


def fetch(aid: str) -> dict:
    url = f"https://arxiv.org/abs/{aid}"
    try:
        page = subprocess.run(["curl", "-sL", "--max-time", "240", url], capture_output=True, text=True,
                              timeout=260).stdout
    except Exception as e:  # noqa: BLE001
        return {"id": aid, "status": f"error:{type(e).__name__}"}

    def meta(name: str) -> str:
        m = re.search(rf'<meta (?:name|property)="{name}" content="([^"]*)"', page)
        return html.unescape(m.group(1)).strip() if m else ""

    com = re.search(r'<td class="tablecell comments mathjax">(.*?)</td>', page, re.S)
    jref = re.search(r'<td class="tablecell jref">(.*?)</td>', page, re.S)
    authors = re.findall(r'<meta name="citation_author" content="([^"]*)"', page)
    return {
        "id": aid, "status": "ok" if meta("citation_title") else "no-title",
        "title": meta("citation_title"), "date": meta("citation_date"),
        "first_author": html.unescape(authors[0]) if authors else "",
        "comments": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(com.group(1)))).strip() if com else "",
        "jref": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(jref.group(1)))).strip() if jref else "",
        "abstract": meta("og:description")[:600],
        "accessed": time.strftime("%Y-%m-%d %H:%M %Z"),
    }


def main() -> None:
    ids = [l.split("#")[0].strip() for l in Path(sys.argv[1]).read_text().splitlines()]
    ids = [i for i in ids if i]
    out = Path(sys.argv[2])
    cols = ["id", "status", "title", "first_author", "date", "comments", "jref", "accessed", "abstract"]
    with cf.ThreadPoolExecutor(max_workers=16) as ex:
        rows = list(ex.map(fetch, ids))
    with out.open("w") as f:
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(str(r.get(c, "")).replace("\t", " ").replace("\n", " ") for c in cols) + "\n")
    print(f"{sum(r['status'] == 'ok' for r in rows)}/{len(rows)} ok → {out}")


if __name__ == "__main__":
    main()
