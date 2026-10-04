"""Build the Round-1 proposal HTML for PDF printing (A4, 1-inch margins, Arial >= 11 pt).

Usage:
  .venv/bin/python deliverables/build_pdf.py            # writes .cache/proposal_print.html
Then print to PDF with Chromium (we use Playwright's page.pdf, format A4, 1in margins,
printBackground) into deliverables/India71_100_[TeamID].pdf, and check pages with:
  .venv/bin/python deliverables/build_pdf.py --check "deliverables/India71_100_[TeamID].pdf"
Mermaid blocks are rendered client-side by mermaid.js (CDN) with fontSize 15px (~11.3 pt).
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "deliverables" / "round1-proposal.md"
OUT = ROOT / ".cache" / "proposal_print.html"

CSS = """
@page { size: A4; margin: 1in; }
html, body { font-family: Arial, Helvetica, sans-serif; font-size: 11pt; line-height: 1.22; color: #000; }
h1 { font-size: 14pt; margin: 0 0 3pt; }
h2 { font-size: 12pt; margin: 7pt 0 2pt; }
p, li { margin: 1.5pt 0; }
ul, ol { margin: 1pt 0 1pt 14pt; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 3pt 0; font-size: 11pt; }
th, td { border: 0.6pt solid #777; padding: 1.5pt 3pt; vertical-align: top; }
th { background: #eee; }
hr { border: 0; border-top: 0.6pt solid #999; margin: 4pt 0; }
pre.mermaid { margin: 2pt 0; text-align: center; }
pre.mermaid svg { max-width: 100%; height: auto; }
code { font-family: Arial, Helvetica, sans-serif; }
"""

MERMAID_JS = """
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>
  mermaid.initialize({ startOnLoad: false, theme: 'neutral',
    themeVariables: { fontFamily: 'Arial, Helvetica, sans-serif', fontSize: '15px' },
    flowchart: { htmlLabels: true, nodeSpacing: 16, rankSpacing: 24, padding: 6, useMaxWidth: true, wrappingWidth: 260 } });
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
    md = SRC.read_text()
    blocks: list[str] = []

    def stash(m: re.Match) -> str:
        blocks.append(m.group(1))
        return f"\n\nMERMAIDBLOCK{len(blocks) - 1}\n\n"

    md = re.sub(r"```mermaid\n(.*?)```", stash, md, flags=re.S)
    body = markdown.markdown(md, extensions=["tables"])
    for i, b in enumerate(blocks):
        body = body.replace(f"<p>MERMAIDBLOCK{i}</p>", f'<pre class="mermaid">{html.escape(b)}</pre>')
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style>{MERMAID_JS}</head>"
                   f"<body>{body}</body></html>")
    return OUT


def check(pdf: str) -> None:
    from pypdf import PdfReader

    r = PdfReader(pdf)
    box = r.pages[0].mediabox
    print(f"pages={len(r.pages)} size_pt={float(box.width):.0f}x{float(box.height):.0f} (A4 = 595x842)")
    fonts = set()
    for p in r.pages:
        res = p.get("/Resources") or {}
        for f in (res.get("/Font") or {}).values():
            fonts.add(str(f.get_object().get("/BaseFont")))
    print("fonts:", sorted(fonts))


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--check":
        check(sys.argv[2])
    else:
        print(build())
