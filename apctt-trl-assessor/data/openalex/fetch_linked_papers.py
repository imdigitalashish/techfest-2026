"""Fetch title + abstract (OpenAlex, public API, no key) for papers DOI-linked from TechPort projects.

For every fetched TechPort record with a TRL, library items of type Link whose URL contains doi.org/10.* are
resolved via https://api.openalex.org/works/doi:<doi>. Output: .data/openalex/linked_papers.jsonl with
{project_id, doi, title, abstract, publication_year, type}. Resumable; ~4 polite workers.
Usage: python data/openalex/fetch_linked_papers.py
"""
from __future__ import annotations

import glob
import gzip
import json
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / ".data"
OUT = ROOT / "openalex" / "linked_papers.jsonl"
UA = "techfest-2026-apctt-research/0.1 (mailto:imdigitalashish@users.noreply.github.com)"


def links():
    pairs = set()
    for fp in glob.glob(str(ROOT / "techport" / "raw" / "*.json.gz")):
        p = json.load(gzip.open(fp, "rt")).get("project", {})
        if not (p.get("trlCurrent") or p.get("trlBegin") or p.get("trlEnd")):
            continue
        for li in p.get("libraryItems") or []:
            m = re.search(r"doi\.org/(10\.[^\s?#]+)", li.get("url") or "")
            if li.get("libraryItemType") == "Link" and m:
                pairs.add((p["projectId"], urllib.parse.unquote(m.group(1)).rstrip("/.").lower()))
    return sorted(pairs)


def abstract(inv):
    if not inv:
        return ""
    pos = sorted((i, w) for w, idx in inv.items() for i in idx)
    return " ".join(w for _, w in pos)


def fetch(pair):
    pid, doi = pair
    url = "https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="/:")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
                w = json.loads(r.read())
            return {"project_id": pid, "doi": doi, "title": w.get("title") or "", "abstract": abstract(w.get("abstract_inverted_index")),
                    "publication_year": w.get("publication_year"), "type": w.get("type")}
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {"project_id": pid, "doi": doi, "error": 404}
        except Exception:
            pass
        time.sleep(2 * (attempt + 1))
    return {"project_id": pid, "doi": doi, "error": "failed"}


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    done = {(r["project_id"], r["doi"]) for r in map(json.loads, OUT.open())} if OUT.exists() else set()
    todo = [p for p in links() if p not in done]
    print(f"{len(done)} done, {len(todo)} to fetch", flush=True)
    with ThreadPoolExecutor(4) as ex, OUT.open("a") as f:
        for r in ex.map(fetch, todo):
            f.write(json.dumps(r) + "\n"); f.flush()
    rows = list(map(json.loads, OUT.open()))
    ok = [r for r in rows if r.get("abstract")]
    print(f"{len(rows)} records; {len(ok)} with abstracts; {len({r['project_id'] for r in ok})} projects")


if __name__ == "__main__":
    main()
