"""Render deliverables/round1-proposal.md to HTML for A4 PDF printing (Arial >= 11 pt, 1-inch margins).

Usage (from india71-t3-finance/): .venv/bin/python deliverables/render_html.py
Then print .cache/proposal.html to PDF with a Chromium browser (A4, margins 1 in, background graphics on),
e.g. via Playwright page.pdf(format="A4", margin=1in). Mermaid diagrams render in the browser.
The leading "Draft status" blockquote is dropped from the rendered copy.
"""
import pathlib
import re

import markdown

ROOT = pathlib.Path(__file__).resolve().parents[1]
src = (ROOT / "deliverables" / "round1-proposal.md").read_text()
src = re.sub(r"^> Draft status:.*?(?:\n(?!>).*?)?\n\n", "", src, count=1, flags=re.M | re.S)
blocks = []


def stash(m):
    blocks.append(m.group(1))
    return f"\n\nMERMAIDBLOCK{len(blocks) - 1}\n\n"


src = re.sub(r"```mermaid\n(.*?)```", stash, src, flags=re.S)
body = markdown.markdown(src, extensions=["tables", "fenced_code"])
for i, b in enumerate(blocks):
    body = body.replace(f"<p>MERMAIDBLOCK{i}</p>", f'<pre class="mermaid">{b}</pre>')
html = f"""<!doctype html><html><head><meta charset="utf-8"><title>India71_100 proposal</title>
<style>
@page {{ size: A4; margin: 1in; }}
html, body {{ font-family: Arial, Helvetica, sans-serif; font-size: 11pt; line-height: 1.25; color: #000; }}
h1 {{ font-size: 14pt; margin: 0 0 4pt; }} h2 {{ font-size: 12pt; margin: 9pt 0 3pt; }}
p, li {{ margin: 0 0 4pt; }} ul, ol {{ margin: 0 0 4pt 16pt; padding: 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 3pt 0 5pt; font-size: 11pt; }}
th, td {{ border: 0.5pt solid #777; padding: 1.5pt 3pt; vertical-align: top; text-align: left; }}
th {{ background: #eee; }} code {{ font-family: Arial, sans-serif; }}
pre.mermaid {{ text-align: center; margin: 4pt 0; }} pre.mermaid svg {{ max-width: 100%; }}
</style>
<script type="module">
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
mermaid.initialize({{ startOnLoad: false, theme: "neutral", flowchart: {{ useMaxWidth: true }}, themeVariables: {{ fontFamily: "Arial", fontSize: "16px" }} }});
await mermaid.run({{ querySelector: ".mermaid" }});
document.body.setAttribute("data-rendered", "1");
</script></head><body>{body}</body></html>"""
out = ROOT / ".cache" / "proposal.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html)
print(out)
