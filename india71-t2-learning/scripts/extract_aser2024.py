#!/usr/bin/env python3
"""Extract ASER 2024 Std III reading/arithmetic tables from pdftotext output."""
from __future__ import annotations
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / ".data" / "raw" / "aser2024_report.txt"
OUT = ROOT / "data" / "public" / "aser2024_state_std3.csv"

STATE_RE = re.compile(r"^\s*([A-Za-z][A-Za-z &]+(?:Pradesh|Kashmir|Bengal|Nadu)|Andhra Pradesh|Assam|Bihar|Chhattisgarh|Gujarat|Haryana|Jharkhand|Karnataka|Kerala|Maharashtra|Meghalaya|Mizoram|Nagaland|Odisha|Punjab|Rajasthan|Sikkim|Telangana|Tripura|Uttarakhand)\s+(\d+\.\d)\s+(\d+\.\d)\s+(\d+\.\d)\s*$")
YEARS = [2018, 2022, 2024]


def clean_state(s: str) -> str:
    return " ".join(s.split())


def page_texts(text: str) -> list[str]:
    return text.split("\f")


def find_page(texts: list[str], contains: str) -> tuple[int, str]:
    for p in texts:
        if contains in p:
            m = re.search(r"Annual Status of Education Report 2024 \|\s*(\d+)|^(\d+) \| Annual Status of Education Report 2024", p, re.M)
            page_no = int(next(g for g in m.groups() if g)) if m else -1
            return page_no, p
    raise RuntimeError(f"Could not find page containing {contains!r}")


def add_all_india(rows: list[dict], pageno: int, page: str, header: str, indicator: str) -> None:
    after = page.split(header, 1)[1]
    before = after.split("Table 2:" if "Table 1:" in header else "What has", 1)[0]
    for line in before.splitlines():
        m = re.match(r"^\s*(20\d\d)\s+(\d+\.\d)\s+(\d+\.\d)\s+(\d+\.\d)", line)
        if not m:
            continue
        year = int(m.group(1))
        if year not in YEARS:
            continue
        for school_type, value in zip(["government", "private", "all"], m.groups()[1:4]):
            rows.append({
                "state": "All India",
                "school_type": school_type,
                "year": year,
                "indicator": indicator,
                "value_pct": value,
                "source_page": pageno,
            })


def add_state_table(rows: list[dict], pageno: int, page: str, marker: str, indicator: str) -> None:
    table = page.split(marker, 1)[1]
    # Retain only the state-wise table area after its State/year header.
    if "State               2018 2022 2024" in table:
        table = table.split("State               2018 2022 2024", 1)[1]
    for line in table.splitlines():
        m = STATE_RE.match(line)
        if not m:
            continue
        state = clean_state(m.group(1))
        for year, value in zip(YEARS, m.groups()[1:4]):
            rows.append({
                "state": state,
                "school_type": "government",
                "year": year,
                "indicator": indicator,
                "value_pct": value,
                "source_page": pageno,
            })


def main() -> None:
    text = RAW.read_text(encoding="utf-8", errors="replace")
    pages = page_texts(text)
    rows: list[dict] = []

    p18, page18 = find_page(pages, "Table 1: Reading level by school type: All India")
    add_all_india(rows, p18, page18, "Table 1: Reading level by school type: All India", "Std III read Std II level text")
    add_all_india(rows, p18, page18, "Table 2: Arithmetic level by school type: All India", "Std III at least subtraction")

    p52, page52 = find_page(pages, "State-wise table showing\n                                                                                                                                        % of government school\n                                                                                                                                        children in Std III who can read")
    add_state_table(rows, p52, page52, "children in Std III who can read", "Std III read Std II level text")
    p53, page53 = find_page(pages, "State-wise table showing\n                                                                                                                                            % of government school\n                                                                                                                                            children in Std III who can do at")
    add_state_table(rows, p53, page53, "children in Std III who can do at", "Std III at least subtraction")

    rows.sort(key=lambda r: (r["indicator"], r["state"] != "All India", r["state"], r["school_type"], int(r["year"])))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["state", "school_type", "year", "indicator", "value_pct", "source_page"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT} rows={len(rows)}")

if __name__ == "__main__":
    main()
