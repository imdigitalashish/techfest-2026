"""Build the Round-1 proposal PDF (A4, 1-inch margins, Arial >= 11 pt, fonts embedded).

Usage (from india71-t2-learning/):
  python3 deliverables/build_pdf.py            # writes .cache/proposal_print.html (vector mermaid via mermaid.js)
  -> print to PDF with Chromium/Playwright: page.pdf(format='A4', margin 1in, printBackground) into
     "deliverables/India71_100_[TeamID].pdf"
  python3 deliverables/build_pdf.py --check    # pages, page size, fonts (embedded?), smallest glyph size
"""
from __future__ import annotations

import html
import re
import subprocess
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "deliverables" / "round1-proposal.md"
OUT = ROOT / ".cache" / "proposal_print.html"
PDF = ROOT / "deliverables" / "India71_100_[TeamID].pdf"

CSS = """
@page { size: A4; margin: 1in; }
html, body { font-family: Arial, Helvetica, sans-serif; font-size: 11pt; line-height: 1.2; color: #000; overflow-wrap: anywhere; }
li, td, th, p { overflow-wrap: anywhere; }
h1 { font-size: 14pt; margin: 0 0 2pt; } h2 { font-size: 12pt; margin: 6pt 0 2pt; } h3 { font-size: 11.5pt; margin: 0 0 3pt; font-weight: normal; }
p, li { margin: 1.5pt 0; } ul, ol { margin: 1pt 0 1pt 14pt; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 3pt 0; font-size: 11pt; }
th, td { border: 0.6pt solid #777; padding: 1.2pt 3pt; vertical-align: top; } th { background: #eee; }
hr { border: 0; border-top: 0.6pt solid #999; margin: 3pt 0; }
pre.mermaid { margin: 2pt 0; text-align: center; font-family: Arial, Helvetica, sans-serif; }
pre.mermaid svg { height: auto; }
code, pre, kbd, samp { font-family: Arial, Helvetica, sans-serif; font-size: 11pt; }
a { color: #000; text-decoration: none; word-break: break-all; }
em, i { font-style: normal; }
"""

MERMAID_JS = """
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>
  mermaid.initialize({ startOnLoad: false, theme: 'neutral',
    themeVariables: { fontFamily: 'Arial, Helvetica, sans-serif', fontSize: '15px' },
    flowchart: { htmlLabels: true, nodeSpacing: 14, rankSpacing: 20, padding: 5, useMaxWidth: false, wrappingWidth: 240 } });
  window.addEventListener('load', async () => {
    const pres = document.querySelectorAll('pre.mermaid');
    for (let i = 0; i < pres.length; i++) {
      const { svg } = await mermaid.render('mmd' + i, pres[i].textContent);
      pres[i].innerHTML = svg;
    }
    window.__ready = true;
  });
</script>
"""


def build() -> Path:
    md = SRC.read_text(encoding="utf-8")
    blocks: list[str] = []

    def stash(m: re.Match) -> str:
        blocks.append(m.group(1))
        return f"\n\nMERMAIDBLOCK{len(blocks) - 1}\n\n"

    md = re.sub(r"```mermaid\n(.*?)```", stash, md, flags=re.S)
    body = markdown.markdown(md, extensions=["tables"])
    for i, b in enumerate(blocks):
        body = body.replace(f"<p>MERMAIDBLOCK{i}</p>", f'<pre class="mermaid">{html.escape(b)}</pre>')
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style>{MERMAID_JS}</head><body>{body}</body></html>", encoding="utf-8")
    return OUT


def check(pdf: Path = PDF) -> int:
    import pdfplumber
    from pypdf import PdfReader

    r = PdfReader(str(pdf)); box = r.pages[0].mediabox
    print(f"pages={len(r.pages)} size_pt={float(box.width):.0f}x{float(box.height):.0f} (A4 = 595x842)")
    out = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True).stdout.splitlines()[2:]
    fonts = [(l.split()[0], l.split()[-5] if len(l.split()) > 5 else "?") for l in out if l.strip()]
    print("fonts (name, embedded):", fonts)
    sizes = []
    with pdfplumber.open(str(pdf)) as p:
        for page in p.pages:
            sizes += [round(c["size"], 2) for c in page.chars if c["text"].strip()]
    small = sorted(set(s for s in sizes if s < 10.95))
    print(f"glyphs={len(sizes)} min_size_pt={min(sizes):.2f} sizes_below_11pt={small[:10]}")
    non_arial = [f for f, _ in fonts if "Arial" not in f]
    ok = len(r.pages) <= 6 and not non_arial and all(e == "yes" for _, e in fonts) and not small
    print("CHECK", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        sys.exit(check(Path(sys.argv[2]) if len(sys.argv) > 2 else PDF))
    print(build())
