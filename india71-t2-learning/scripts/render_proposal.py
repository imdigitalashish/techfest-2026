"""Render deliverables/round1-proposal.md to HTML (A4, Arial 11 pt, 1-inch margins) for PDF printing.

Usage: python3 scripts/render_proposal.py  -> deliverables/build/round1-proposal.html
Mermaid blocks are replaced by the pre-rendered diagram image if deliverables/build/architecture.svg exists,
otherwise by a placeholder box of the same approximate height (for page-count checks).
"""
from pathlib import Path
import re
import markdown

ROOT = Path(__file__).resolve().parents[1]
src = (ROOT / "deliverables/round1-proposal.md").read_text(encoding="utf-8")
svg = ROOT / "deliverables/build/architecture.svg"
def repl(_m):
    if svg.exists():
        return f'<img src="architecture.svg" style="width:100%;max-height:9cm">'
    return '<div style="height:7.5cm;border:1px dashed #999;text-align:center;line-height:7.5cm">[architecture diagram]</div>'
src = re.sub(r"```mermaid.*?```", repl, src, flags=re.S)
html_body = markdown.markdown(src, extensions=["tables"])
css = """
@page { size: A4; margin: 1in; }
body { font-family: Arial, Helvetica, sans-serif; font-size: 11pt; line-height: 1.25; }
h1 { font-size: 15pt; margin: 0 0 4pt; } h2 { font-size: 12.5pt; margin: 10pt 0 4pt; } h3 { font-size: 11pt; margin: 0 0 6pt; font-weight: normal; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0; } th, td { border: 1px solid #888; padding: 2pt 4pt; vertical-align: top; font-size: 11pt; }
p { margin: 4pt 0; } ol, ul { margin: 4pt 0 4pt 16pt; padding: 0; } hr { display: none; }
"""
out = ROOT / "deliverables/build"; out.mkdir(parents=True, exist_ok=True)
(out / "round1-proposal.html").write_text(f"<!doctype html><html><head><meta charset='utf-8'><style>{css}</style></head><body>{html_body}</body></html>", encoding="utf-8")
print(out / "round1-proposal.html")
