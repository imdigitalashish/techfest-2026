"""Fact-check helper: fetch a URL (cached in .cache/sources/), print short snippets around regex matches.
Usage (from ev-c1-infra-map-india/): python3 research/tools/verify.py URL REGEX [REGEX...]
Prints: HTTP status, page title, and up to 3 snippets (±160 chars) per regex. PDFs are converted with pdftotext if present.
"""
import hashlib, html as H, os, re, subprocess, sys
import requests
url, pats = sys.argv[1], sys.argv[2:]
os.makedirs(".cache/sources", exist_ok=True)
f = ".cache/sources/" + hashlib.sha1(url.encode()).hexdigest()[:12]
try:
    r = requests.get(url, timeout=40, headers={"User-Agent": "Mozilla/5.0 (Macintosh) Chrome/128 Safari/537.36"}, allow_redirects=True)
    status, ctype, body = r.status_code, r.headers.get("Content-Type", ""), r.content
except Exception as e:
    print("ERR", type(e).__name__, url); sys.exit(0)
if "pdf" in ctype or body[:4] == b"%PDF":
    open(f + ".pdf", "wb").write(body)
    try:
        text = subprocess.run(["pdftotext", "-layout", f + ".pdf", "-"], capture_output=True, text=True, timeout=120).stdout
    except FileNotFoundError:
        import io
        from pypdf import PdfReader
        text = "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(body)).pages)
    title = "(pdf)"
else:
    h = body.decode("utf-8", "ignore"); open(f + ".html", "w").write(h)
    m = re.search(r"<title[^>]*>(.*?)</title>", h, re.S | re.I); title = H.unescape(re.sub(r"\s+", " ", m.group(1)).strip())[:100] if m else "-"
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h); text = H.unescape(re.sub(r"<[^>]+>", " ", h))
text = re.sub(r"\s+", " ", text)
print(f"{status} | {title} | {len(text)} chars | {url}")
for p in pats:
    hits = [m for m in re.finditer(p, text, re.I)][:3]
    print(f"  /{p}/ -> {len(list(re.finditer(p, text, re.I)))} hits")
    for m in hits:
        print("    …" + text[max(0, m.start() - 160):m.end() + 160].strip() + "…")
