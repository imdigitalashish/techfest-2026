"""Quote verifier — the fail-closed gate of spike A (C3 ingestion): a candidate or verified record is accepted only
if its verbatim quote is found in the text of its source document.

This file is the ONLY file the autoresearch loop edits (see autoresearch/program.md); eval.py is frozen.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
CACHE = PROJECT / ".cache" / "doctext"
VERSION = "v3-fragments+3-line-table-window"


def load_text(local_copy: str) -> str:
    """Plain text of a local PDF (pdftotext -layout), cached under .cache/doctext/."""
    src = PROJECT / local_copy
    CACHE.mkdir(parents=True, exist_ok=True)
    out = CACHE / (src.name + ".txt")
    if not out.exists():
        subprocess.run(["pdftotext", "-layout", str(src), str(out)], check=True, capture_output=True)
    return out.read_text(errors="ignore")


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


TABLE_LINES = 3         # a table cell's header/label/value may sit on up to 3 consecutive layout lines
TABLE_MAX_TOKENS = 12   # the fallback is only allowed for short, cell-like quotes


def _tokens(s: str) -> list[str]:
    return normalize(s).split(" ")


def table_window_found(frag: str, raw_text: str) -> bool:
    """Fallback for table cells laid out on different lines: every token of a short numeric fragment occurs as a
    whole token within TABLE_LINES consecutive lines of the layout text; numbers must match exactly."""
    toks = _tokens(frag)
    if not toks or len(toks) > TABLE_MAX_TOKENS or not any(re.search(r"\d", x) for x in toks):
        return False
    lines = [ln.split() for ln in raw_text.splitlines() if ln.strip()]
    for i in range(len(lines)):
        window = set(x for ln in lines[i:i + TABLE_LINES] for x in ln)
        if all(x in window for x in toks):
            return True
    return False


def quote_found(quote: str, text: str) -> bool:
    """Every ' ... '-separated fragment must appear verbatim (whitespace-collapsed), in order; a short numeric
    fragment that fails verbatim may pass the bounded table-window check instead."""
    t = normalize(text)
    pos = 0
    for frag in (normalize(f) for f in re.split(r"\s*(?:\.\.\.|…)\s*", quote)):
        if not frag:
            continue
        i = t.find(frag, pos)
        if i < 0:
            if table_window_found(frag, text):
                continue
            return False
        pos = i + len(frag)
    return True
