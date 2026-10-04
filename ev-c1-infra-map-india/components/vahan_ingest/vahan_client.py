"""Plain-HTTP client for the public VAHAN 4 dashboard (no browser needed).

The dashboard at https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml
is a JSF/PrimeFaces page. Each dropdown fires a partial-AJAX "change" event that
updates dependent widgets; the Refresh button (j_idt65) re-renders the pivot table
and the "EXCEL file" link (groupingTable:xls) exports the full table as .xlsx.
We replay exactly those requests. Widget ids were read from the live page on
2026-10-04; if the site is redeployed they may change -> `Vahan.selftest()` fails loudly.
"""
from __future__ import annotations

import io
import re
import time
from dataclasses import dataclass

import pandas as pd
import requests

BASE = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/128 Safari/537.36 (research; EV Infra Map India)"}
AJAX_HDR = {"Faces-Request": "partial/ajax", "X-Requested-With": "XMLHttpRequest"}
REFRESH_RENDER = "VhCatg norms fuel VhClass combTablePnl groupingTable msg vhCatgPnl"

# VAHAN fuel labels that denote plug-in electric drivetrains.
BEV_FUELS = ["ELECTRIC(BOV)", "PURE EV"]
PHEV_FUELS = ["PLUG-IN HYBRID EV"]


@dataclass
class Option:
    value: str
    label: str


def _options(html_text: str, select_id: str) -> list[Option]:
    m = re.search(rf'<select[^>]*id="{select_id}_input"[^>]*>(.*?)</select>', html_text, re.S)
    if not m:
        return []
    return [Option(v, re.sub(r"\s+", " ", l).replace("&amp;", "&").strip())
            for v, l in re.findall(r'<option value="([^"]*)"[^>]*>([^<]*)</option>', m.group(1))]


class Vahan:
    def __init__(self, delay_s: float = 0.4, timeout: int = 120):
        self.delay_s, self.timeout = delay_s, timeout
        self.s = requests.Session()
        self.s.headers.update(UA)
        r = self._req("get", BASE)
        self.page = r.text
        self.vs = re.search(r'name="javax.faces.ViewState"[^>]*value="([^"]+)"', r.text).group(1)
        self.form = {"masterLayout_formlogin": "masterLayout_formlogin", "j_idt26_input": "A",
                     "j_idt34_input": "-1", "selectedRto_input": "-1",
                     "yaxisVar_input": "State", "xaxisVar_input": "Fuel",
                     "selectedYearType_input": "C", "selectedYear_input": "A"}
        self.states = [o for o in _options(self.page, "j_idt34") if o.value != "-1"]

    def _req(self, method: str, url: str, **kw) -> requests.Response:
        for attempt in range(5):
            try:
                time.sleep(self.delay_s)
                r = self.s.request(method, url, timeout=self.timeout, **kw)
                r.raise_for_status()
                return r
            except requests.RequestException:
                if attempt == 4:
                    raise
                time.sleep(3 * (attempt + 1))
        raise RuntimeError("unreachable")

    def _ajax(self, source: str, render: str, event: str | None = None) -> str:
        d = dict(self.form)
        d.update({"javax.faces.partial.ajax": "true", "javax.faces.source": source,
                  "javax.faces.partial.execute": source if event else "@all",
                  "javax.faces.partial.render": render, "javax.faces.ViewState": self.vs})
        if event:
            d["javax.faces.behavior.event"] = event
            d["javax.faces.partial.event"] = event
        else:
            d[source] = source
        t = self._req("post", BASE, data=d, headers=AJAX_HDR).text
        m = re.search(r'<update id="[^"]*javax.faces.ViewState[^"]*"><!\[CDATA\[([^\]]+)\]\]>', t)
        if m:
            self.vs = m.group(1)
        return t

    def _set(self, field: str, value: str, source: str, render: str) -> str:
        self.form[field] = value
        return self._ajax(source, render, event="change")

    def set_state(self, code: str) -> list[Option]:
        t = self._set("j_idt34_input", code, "j_idt34", "selectedRto yaxisVar")
        self.form["selectedRto_input"] = "-1"
        return [o for o in _options(t, "selectedRto") if o.value != "-1"]

    def set_rto(self, code: str) -> None:
        self._set("selectedRto_input", code, "selectedRto", "yaxisVar")

    def query(self, y: str, x: str, year: str, year_type: str = "C") -> pd.DataFrame:
        """Return the pivot table (rows = y categories, columns = x categories) for the current state/RTO."""
        self._set("yaxisVar_input", y, "yaxisVar", "xaxisVar")
        self._set("xaxisVar_input", x, "xaxisVar", "multipleYear")
        self._set("selectedYearType_input", year_type, "selectedYearType", "selectedYear")
        self._set("selectedYear_input", year, "selectedYear", "selectedYear")
        self._ajax("j_idt65", REFRESH_RENDER)
        d = dict(self.form)
        d.update({"groupingTable:xls": "groupingTable:xls", "javax.faces.ViewState": self.vs})
        r = self._req("post", BASE, data=d)
        if "spreadsheetml" not in r.headers.get("Content-Type", ""):
            raise RuntimeError(f"export failed: {r.headers.get('Content-Type')}")
        return parse_export(r.content)


def parse_export(xlsx: bytes) -> pd.DataFrame:
    """Parse a VAHAN 'reportTable.xlsx' export into a wide frame: [row_label, <x cols>..., TOTAL]."""
    raw = pd.read_excel(io.BytesIO(xlsx), header=None, dtype=str)
    hdr_i = next(i for i in range(len(raw)) if str(raw.iat[i, 0]).strip() == "S No")
    title = str(raw.iat[0, 0]).strip()
    labels = [str(v).strip() for v in raw.iloc[hdr_i + 1].tolist()]
    cols = []
    for j in range(raw.shape[1]):
        top = str(raw.iat[hdr_i, j]).strip()
        if j == 0:
            cols.append("s_no")
        elif j == 1:
            cols.append("row_label")
        elif top.upper() == "TOTAL":
            cols.append("TOTAL")
        else:
            cols.append(labels[j] if labels[j] not in ("nan", "") else top)
    body = raw.iloc[hdr_i + 2:].copy()
    body.columns = cols
    body = body[body["s_no"].astype(str).str.strip().str.match(r"^\d+$")]
    for c in cols[2:]:
        body[c] = pd.to_numeric(body[c].astype(str).str.replace(",", "").str.strip(), errors="coerce").fillna(0).astype("int64")
    body = body.drop(columns=["s_no"]).reset_index(drop=True)
    body.attrs["title"] = title
    return body
