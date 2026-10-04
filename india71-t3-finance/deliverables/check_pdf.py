"""Check the Round-1 PDF against the brief: <= 6 A4 pages, Arial only, every glyph >= 11 pt, fonts embedded, 1-inch margins.

Usage (from india71-t3-finance/): .venv/bin/python deliverables/check_pdf.py "deliverables/India71_100_[TeamID].pdf"
Needs poppler's `pdffonts` on PATH. Exit code 1 on any failure.
"""
import subprocess
import sys

import pdfplumber

path = sys.argv[1]
fails = []
with pdfplumber.open(path) as pdf:
    n = len(pdf.pages)
    w, h = pdf.pages[0].width, pdf.pages[0].height
    sizes, fonts, x0, x1, top, bottom = set(), set(), 1e9, 0, 1e9, 0
    for p in pdf.pages:
        for c in p.chars:
            if not c["text"].strip():
                continue
            sizes.add(round(c["size"], 1))
            fonts.add(c["fontname"].split("+")[-1])
            x0, x1, top, bottom = min(x0, c["x0"]), max(x1, c["x1"]), min(top, c["top"]), max(bottom, c["bottom"])
if n > 6:
    fails.append(f"{n} pages > 6")
if abs(w - 595) > 2 or abs(h - 842) > 2:
    fails.append(f"page size {w:.0f}x{h:.0f} is not A4")
if min(sizes) < 11:
    fails.append(f"glyphs below 11 pt: {sorted(s for s in sizes if s < 11)}")
non_arial = sorted(f for f in fonts if not f.startswith("Arial"))
if non_arial:
    fails.append(f"non-Arial fonts used: {non_arial}")
if min(x0, top) < 71.5 or w - x1 < 71.5 or h - bottom < 71.5:
    fails.append(f"text outside 1-inch margins: x0={x0:.0f} x1={x1:.0f} top={top:.0f} bottom={bottom:.0f}")
pf = subprocess.run(["pdffonts", path], capture_output=True, text=True).stdout.splitlines()[2:]
not_emb = [l.split()[0] for l in pf if l.split()[-5] != "yes"]
if not_emb:
    fails.append(f"fonts not embedded: {not_emb}")
print(f"{path}: {n} pages, sizes {sorted(sizes)}, fonts {sorted(fonts)}, embedded {len(pf) - len(not_emb)}/{len(pf)}, "
      f"text box x {x0:.0f}-{x1:.0f} y {top:.0f}-{bottom:.0f}")
print("PASS" if not fails else "FAIL: " + "; ".join(fails))
sys.exit(1 if fails else 0)
