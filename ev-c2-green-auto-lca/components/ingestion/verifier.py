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
VERSION = "v5-fragments-in-order-number-boundaries"


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


def _find(frag: str, t: str, pos: int) -> int:
    """Find frag in t from pos, but a fragment that starts/ends with a digit may not continue a larger number
    (e.g. '0.675' must not match inside '10.675' or '0.6751')."""
    pre = r"(?<![\d.,])" if frag[:1].isdigit() else ""
    post = r"(?![\d]|[.,]\d)" if frag[-1:].isdigit() else ""
    m = re.compile(pre + re.escape(frag) + post).search(t, pos)
    return m.start() if m else -1


def quote_found(quote: str, text: str) -> bool:
    """Every ' ... '-separated fragment must appear verbatim (whitespace-collapsed), in order, and numbers at fragment
    edges may not be part of larger numbers. No fuzzy fallback (v3's table window accepted perturbed numbers).
    NOTE: this is an evidence-PRESENCE check; value_in_quote() checks the record's value against its own quote."""
    t = normalize(text)
    pos = 0
    for frag in (normalize(f) for f in re.split(r"\s*(?:\.\.\.|…)\s*", quote)):
        if not frag:
            continue
        i = _find(frag, t, pos)
        if i < 0:
            return False
        pos = i + len(frag)
    return True


def _variants(v: float) -> set[str]:
    out = set()
    for x in (v, v * 100, v * 1000, v / 1000):
        for d in range(0, 5):
            r = round(x, d)
            if abs(r - x) > 1e-9 * max(1.0, abs(x)):
                continue
            txt = f"{r:.{d}f}"
            out |= {txt, f"{r:,.{d}f}", f"{r:,.{d}f}".replace(",", " ")}
            if "." in txt:
                out.add(txt.rstrip("0").rstrip("."))
    return {o for o in out if o not in ("0", "")}


def value_in_quote(value: float, quote: str) -> bool:
    """True if the record's value (or the same number scaled by 100/1000 for %/unit changes) appears as a whole
    number in its quote. A semantic check that the quote is evidence for THIS value."""
    q = normalize(quote)
    return any(_find(c, q, 0) >= 0 for c in _variants(float(value)))
