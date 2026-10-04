"""Render deliverables/presenter-card.md (itself rendered by eval/render_docs.py) to a one-page A4 PDF with headless Chrome.
Run (from innovatex-t2-aqi/): python3 deliverables/make_presenter_card.py
"""
import pathlib
import subprocess

import markdown

HERE = pathlib.Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
body = markdown.markdown((HERE / "presenter-card.md").read_text(), extensions=["tables"])
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: A4; margin: 9mm 11mm; }}
body {{ font-family: Arial, Helvetica, sans-serif; font-size: 10.4pt; line-height: 1.32; color: #111; }}
h1 {{ font-size: 14pt; margin: 0 0 4pt; color: #0f766e; }} p {{ margin: 3pt 0; }} ul {{ margin: 2pt 0 4pt 16pt; padding: 0; }}
table {{ border-collapse: collapse; width: 100%; font-size: 9.4pt; margin: 4pt 0; }}
th, td {{ border: 1px solid #bbb; padding: 2pt 4pt; text-align: left; vertical-align: top; }} th {{ background: #eef2f5; }} td:nth-child(2) {{ white-space: nowrap; }} li {{ margin: 1pt 0; }}
</style></head><body>{body}</body></html>"""
tmp = HERE / ".presenter-card.html"
tmp.write_text(html)
out = HERE / "presenter-card.pdf"
subprocess.run(["/usr/bin/nice", "-n", "10", CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={out}", tmp.as_uri()],
               check=True, capture_output=True)
tmp.unlink()
print("wrote", out)
