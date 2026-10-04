"""Fetch arXiv records (title, authors, dates, journal ref, abstract) via the official arXiv API.

Writes full records to a Markdown evidence file and prints one compact line per record,
so research claims can be traced to the exact abstract that was read.

Usage:
  python arxiv_fetch.py --out ../sources/arxiv_classics.md --titles titles.txt
  python arxiv_fetch.py --out ../sources/arxiv_newest.md --query 'abs:"off-policy evaluation"' --max 80 --since 2025-01-01
"""
from __future__ import annotations

import argparse
import datetime as dt
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

API = "http://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}


def query(search: str, max_results: int, sort_by_date: bool) -> list[dict]:
    params = {"search_query": search, "start": 0, "max_results": max_results}
    if sort_by_date:
        params.update(sortBy="submittedDate", sortOrder="descending")
    url = f"{API}?{urllib.parse.urlencode(params)}"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                root = ET.fromstring(r.read())
            break
        except Exception as e:  # network is flaky tonight: retry with backoff
            if attempt == 3:
                print(f"ERROR {search}: {e}")
                return []
            time.sleep(5 * (attempt + 1))
    out = []
    for e in root.findall("a:entry", NS):
        rid = e.findtext("a:id", default="", namespaces=NS).rsplit("/abs/", 1)[-1]
        out.append(
            {
                "id": rid,
                "title": " ".join(e.findtext("a:title", default="", namespaces=NS).split()),
                "authors": [a.findtext("a:name", namespaces=NS) for a in e.findall("a:author", NS)],
                "published": e.findtext("a:published", default="", namespaces=NS)[:10],
                "updated": e.findtext("a:updated", default="", namespaces=NS)[:10],
                "journal_ref": e.findtext("x:journal_ref", default="", namespaces=NS),
                "comment": " ".join((e.findtext("x:comment", default="", namespaces=NS) or "").split()),
                "abstract": " ".join(e.findtext("a:summary", default="", namespaces=NS).split()),
            }
        )
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--titles", help="file with one exact title per line (searched as ti:\"...\")")
    p.add_argument("--query", action="append", default=[])
    p.add_argument("--max", type=int, default=3)
    p.add_argument("--since", default="")
    args = p.parse_args()

    searches = []
    if args.titles:
        for line in open(args.titles):
            t = line.strip()
            if t:
                stop = {"and", "for", "the", "via", "with", "under", "from", "into", "towards", "not", "or"}
                words = " AND ".join(
                    f"ti:{w}" for w in t.replace(":", " ").replace("-", " ").split() if len(w) > 2 and w.lower() not in stop
                )
                searches.append((t, words, 3, False))
    for q in args.query:
        searches.append((q, q, args.max, True))

    accessed = dt.date.today().isoformat()
    with open(args.out, "a") as f:
        for label, s, n, by_date in searches:
            recs = query(s, n, by_date)
            time.sleep(3)
            f.write(f"\n## Query: {label}\n\n")
            if not recs:
                f.write("_No results._\n")
                print(f"[none] {label[:70]}")
            for r in recs:
                if args.since and r["published"] < args.since:
                    continue
                au = ", ".join(r["authors"][:6]) + (" et al." if len(r["authors"]) > 6 else "")
                f.write(
                    f"### arXiv:{r['id']} — {r['title']}\n"
                    f"- Authors: {au}\n- Published: {r['published']} (updated {r['updated']})\n"
                    f"- Journal ref: {r['journal_ref'] or '—'} · Comment: {r['comment'] or '—'}\n"
                    f"- URL: https://arxiv.org/abs/{r['id']} (accessed {accessed} via arXiv API)\n"
                    f"- Abstract: {r['abstract']}\n\n"
                )
                print(f"{r['id']} | {r['published']} | {r['title'][:85]} | {', '.join(a.split()[-1] for a in r['authors'][:3])} | {(r['journal_ref'] or r['comment'])[:50]}")


if __name__ == "__main__":
    main()
