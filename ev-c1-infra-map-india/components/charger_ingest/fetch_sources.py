"""Fetch cited source pages into .cache/sources/<sha1[:12]>.html (used by official_pcs.py).
Usage (from ev-c1-infra-map-india/): python3 components/charger_ingest/fetch_sources.py components/charger_ingest/source_urls.txt
"""
import concurrent.futures as cf, hashlib, os, re, sys, requests, html as H
urls=[u.strip() for u in open(sys.argv[1]) if u.strip()]
def get(u):
    os.makedirs('.cache/sources', exist_ok=True); f='.cache/sources/'+hashlib.sha1(u.encode()).hexdigest()[:12]+'.html'
    try:
        r=requests.get(u,timeout=25,headers={"User-Agent":"Mozilla/5.0 (Macintosh) Chrome/128"},allow_redirects=True)
        open(f,'w').write(r.text)
        m=re.search(r'<title[^>]*>(.*?)</title>',r.text,re.S|re.I)
        t=H.unescape(re.sub(r'\s+',' ',m.group(1)).strip()[:80]) if m else '-'
        return f"{r.status_code} {len(r.text):>7} | {t} | {u} | {f}"
    except Exception as e:
        return f"ERR {type(e).__name__} | {u}"
with cf.ThreadPoolExecutor(10) as ex:
    for line in ex.map(get,urls): print(line)
