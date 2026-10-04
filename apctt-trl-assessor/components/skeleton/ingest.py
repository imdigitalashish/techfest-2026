"""C1 Ingest & parse: raw file -> ParsedDocument (contracts.schema.json#/$defs/ParsedDocument)."""
from __future__ import annotations

import html
import re
from pathlib import Path

TAG = re.compile(r"<[^>]+>")
PARA = re.compile(r"\n\s*\n")


def _read_text(path: Path) -> tuple[str, str, int | None]:
    suf = path.suffix.lower()
    if suf == ".pdf":
        from pypdf import PdfReader  # lazy: only PDFs pay the import

        reader = PdfReader(str(path))
        pages = [(p.extract_text() or "") for p in reader.pages]
        return "\n\n".join(pages), "pypdf", len(pages)
    raw = path.read_text(encoding="utf-8", errors="replace")
    if suf in (".html", ".htm", ".xml"):
        return html.unescape(TAG.sub(" ", raw)), "html-strip", None
    return raw, "plain", None


def parse(path: str | Path) -> dict:
    path = Path(path)
    try:
        text, parser, n_pages = _read_text(path)
    except Exception as e:  # never crash the batch on one bad file
        text, parser, n_pages = "", f"error:{type(e).__name__}", None
    sections = []
    for i, block in enumerate(b.strip() for b in PARA.split(text)):
        if not block:
            continue
        first = block.split("\n", 1)[0].strip()
        heading = first if len(first) < 80 and not first.endswith(".") and "\n" in block else ""
        sections.append({"section_id": f"s{i}", "heading": heading, "text": re.sub(r"\s+", " ", block), "page": None})
    return {"doc_id": path.stem, "source_path": str(path), "mime": path.suffix.lower().lstrip(".") or "txt",
            "sections": sections, "n_pages": n_pages, "n_chars": sum(len(s["text"]) for s in sections), "parser": parser}
