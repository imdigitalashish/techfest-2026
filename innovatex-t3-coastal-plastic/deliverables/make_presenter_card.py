"""Render deliverables/presenter-card.md (itself rendered from src/) to a one-page A4 PDF with headless Chrome.

Run: python3 innovatex-t3-coastal-plastic/deliverables/make_presenter_card.py
"""
import pathlib
import re
import subprocess

import markdown

HERE = pathlib.Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
src = re.sub(r"^<!--.*?-->\n", "", (HERE / "presenter-card.md").read_text(), flags=re.S)
body = markdown.markdown(src, extensions=["tables"])
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: A4; margin: 8mm 10mm; }}
body {{ font-family: Arial, Helvetica, sans-serif; font-size: 10pt; line-height: 1.28; color: #111; }}
h1 {{ font-size: 13.5pt; margin: 0 0 4pt; }} p {{ margin: 3pt 0; }} ul {{ margin: 2pt 0 4pt 15pt; padding: 0; }}
li {{ margin: 1pt 0; }}
table {{ border-collapse: collapse; width: 100%; font-size: 9pt; margin: 3pt 0; }}
th, td {{ border: 1px solid #bbb; padding: 2pt 4pt; text-align: left; }} th {{ background: #eef2f5; }}
</style></head><body>{body}</body></html>"""
tmp = HERE / ".presenter-card.html"
tmp.write_text(html)
out = HERE / "presenter-card.pdf"
subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={out}", tmp.as_uri()],
               check=True, capture_output=True)
tmp.unlink()
print("wrote", out)
