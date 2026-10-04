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
VERSION = "v0-collapse-whitespace"


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


def quote_found(quote: str, text: str) -> bool:
    return normalize(quote) in normalize(text)
