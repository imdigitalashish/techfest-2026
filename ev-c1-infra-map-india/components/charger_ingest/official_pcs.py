"""Extract state-wise official public-charging-station (PCS) counts from two PIB releases (cached HTML).

Sources (opened 2026-10-04):
  PIB 2118894, 04 Apr 2025 — BEE data, PCS installed as on 01 Apr 2025, tier-1/2/3 split (total 26,367).
  PIB 2151390, 01 Aug 2025 — MoP inputs, 29,277 PCS installed across the country, state-wise.
Usage: python components/charger_ingest/official_pcs.py  (needs .cache/sources/*.html from .cache/fetch_sources.py)
"""
import html as H, os, re
import pandas as pd
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = {"pib2118894": (".cache/sources/196a5e80cd92.html", "https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2118894", "2025-04-01"),
       "pib2151390": (".cache/sources/fdd0f25dfec5.html", "https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2151390", "2025-08-01")}
def rows(path):
    h = open(os.path.join(ROOT, path), errors="ignore").read()
    for tr in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", h):
        cells = [re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", c))).strip() for c in re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", tr)]
        yield [c for c in cells]
def num(s):
    s = s.replace(",", "").strip()
    return int(s) if s.isdigit() else (0 if s in ("-", "") else None)
out = []
for key, (path, url, ason) in SRC.items():
    for c in rows(path):
        if len(c) >= 3 and c[0].strip().isdigit() and re.search(r"[A-Za-z]", c[1]) and not re.search(r"\d", c[1]):
            vals = [num(x) for x in c[2:]]
            if any(v is None for v in vals): continue
            rec = {"source": key, "as_on": ason, "state": c[1], "pcs_total": vals[-1], "url": url}
            if len(vals) == 4: rec.update(tier1=vals[0], tier2=vals[1], tier3=vals[2])
            out.append(rec)
df = pd.DataFrame(out).drop_duplicates(["source", "state"])
p = os.path.join(os.path.dirname(__file__), "data", "official_pcs_statewise.csv")
df.to_csv(p, index=False)
print(df.groupby("source").pcs_total.agg(["count", "sum"]).to_string())
