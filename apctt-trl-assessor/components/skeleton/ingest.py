"""C1 Ingest & parse: raw file -> ParsedDocument (contracts.schema.json#/$defs/ParsedDocument)."""
from __future__ import annotations

import html
import re
from pathlib import Path

TAG = re.compile(r"<[^>]+>")
PARA = re.compile(r"\n\s*\n")


def _read_pages(path: Path) -> tuple[list[str], str, int | None]:
    """Return text per page (one element for non-paginated formats), parser name, page count."""
    suf = path.suffix.lower()
    if suf == ".pdf":
        from pypdf import PdfReader  # lazy: only PDFs pay the import

        reader = PdfReader(str(path))
        pages = [(p.extract_text() or "") for p in reader.pages]
        return pages, "pypdf", len(pages)
    if suf == ".docx":  # stdlib only: paragraphs from word/document.xml
        import zipfile

        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml").decode("utf-8", errors="replace")
        xml = re.sub(r"</w:p>", "\n\n", xml)
        return [html.unescape(TAG.sub("", xml))], "docx-xml", None
    raw = path.read_text(encoding="utf-8", errors="replace")
    if suf in (".html", ".htm", ".xml"):
        return [html.unescape(TAG.sub(" ", raw))], "html-strip", None
    return [raw], "plain", None


def parse(path: str | Path) -> dict:
    path = Path(path)
    try:
        pages, parser, n_pages = _read_pages(path)
    except Exception as e:  # never crash the batch on one bad file
        pages, parser, n_pages = [""], f"error:{type(e).__name__}", None
    sections = []
    for pno, text in enumerate(pages, start=1):
        for block in (b.strip() for b in PARA.split(text)):
            if not block:
                continue
            first = block.split("\n", 1)[0].strip()
            heading = first if len(first) < 80 and not first.endswith(".") and "\n" in block else ""
            sections.append({"section_id": f"s{len(sections)}", "heading": heading, "text": re.sub(r"\s+", " ", block),
                             "page": pno if n_pages else None})
    return {"doc_id": path.name, "source_path": str(path), "mime": path.suffix.lower().lstrip(".") or "txt",
            "sections": sections, "n_pages": n_pages, "n_chars": sum(len(s["text"]) for s in sections), "parser": parser}
