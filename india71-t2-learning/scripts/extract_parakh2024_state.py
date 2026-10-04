#!/usr/bin/env python3
"""Extract Grade 3 state averages from PARAKH Rashtriya Sarvekshan 2024 reports."""
from __future__ import annotations

import csv
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".data" / "parakh2024_state"
OUT = ROOT / "data" / "public" / "parakh2024_grade3_state.csv"
BASE_URL = "https://parakh.ncert.gov.in/sites/default/files/2025-07"
REFERER = "https://parakh.ncert.gov.in/prs"
NATIONAL_REPORT = "https://parakh.ncert.gov.in/sites/default/files/2025-07/REPORT_India_IND.pdf"

STATE_REPORTS = [
    ("Jammu and Kashmir", "Jammu & Kashmir", "001"),
    ("Himachal Pradesh", "Himachal Pradesh", "002"),
    ("Punjab", "Punjab", "003"),
    ("Chandigarh", "Chandigarh", "004"),
    ("Uttarakhand", "Uttarakhand", "005"),
    ("Haryana", "Haryana", "006"),
    ("NCT of Delhi", "NCT of Delhi", "007"),
    ("Rajasthan", "Rajasthan", "008"),
    ("Uttar Pradesh", "Uttar Pradesh", "009"),
    ("Bihar", "Bihar", "010"),
    ("Sikkim", "Sikkim", "011"),
    ("Arunachal Pradesh", "Arunachal Pradesh", "012"),
    ("Nagaland", "Nagaland", "013"),
    ("Manipur", "Manipur", "014"),
    ("Mizoram", "Mizoram", "015"),
    ("Tripura", "Tripura", "016"),
    ("Meghalaya", "Meghalaya", "017"),
    ("Assam", "Assam", "018"),
    ("West Bengal", "West Bengal", "019"),
    ("Jharkhand", "Jharkhand", "020"),
    ("Odisha", "Odisha", "021"),
    ("Chhattisgarh", "Chhattisgarh", "022"),
    ("Madhya Pradesh", "Madhya Pradesh", "023"),
    ("Gujarat", "Gujarat", "024"),
    ("Maharashtra", "Maharashtra", "027"),
    ("Andhra Pradesh", "Andhra Pradesh", "028"),
    ("Karnataka", "Karnataka", "029"),
    ("Goa", "Goa", "030"),
    ("Lakshadweep", "Lakshadweep", "031"),
    ("Kerala", "Kerala", "032"),
    ("Tamil Nadu", "Tamil Nadu", "033"),
    ("Puducherry", "Puducherry", "034"),
    ("Andaman and Nicobar Islands", "Andaman & Nicobar Islands", "035"),
    ("Telangana", "Telangana", "036"),
    ("Ladakh", "Ladakh", "037"),
]


def report_url(url_name: str, code: str) -> str:
    filename = f"REPORT_{urllib.parse.quote(url_name)}_IND{code}.pdf"
    return f"{BASE_URL}/{filename}"


def download(url: str, dest: Path) -> None:
    if dest.exists() and dest.stat().st_size > 10_000:
        return
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0", "Referer": REFERER},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        dest.write_bytes(response.read())


def pdf_text(pdf: Path) -> str:
    return subprocess.check_output(
        ["pdftotext", "-layout", str(pdf), "-"],
        text=True,
        stderr=subprocess.DEVNULL,
    )


def grade3_comparison_page(text: str, state: str) -> tuple[int, str]:
    for page_no, page in enumerate(text.split("\f"), start=1):
        if (
            "GRADE 3" in page
            and "Comparison of State Average with National Average Across Subjects" in page
            and "Language" in page
            and "Mathematics" in page
        ):
            return page_no, page
    raise RuntimeError(f"Grade 3 comparison page not found for {state}")


def extract_values(page: str, state: str) -> tuple[int, int]:
    section = page.split("Comparison of State Average with National Average Across Subjects", 1)[1]
    section = section.split("In both Language", 1)[0]
    nums = [int(x) for x in re.findall(r"(\d+)%", section)]
    if len(nums) < 4:
        raise RuntimeError(f"Expected at least four percentages on Grade 3 comparison page for {state}: {nums}")
    language_state, language_national, math_state, math_national = nums[:4]
    if (language_national, math_national) != (64, 60):
        raise RuntimeError(
            f"Unexpected national values on {state} page: "
            f"Language={language_national}, Mathematics={math_national}"
        )
    return language_state, math_state


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    download(NATIONAL_REPORT, CACHE / "REPORT_India_IND.pdf")

    rows: list[dict[str, str | int]] = []
    samples: list[str] = []
    failures: list[str] = []
    for state, url_name, code in STATE_REPORTS:
        url = report_url(url_name, code)
        pdf = CACHE / f"REPORT_{state.replace(' ', '_').replace('/', '_')}_IND{code}.pdf"
        try:
            download(url, pdf)
            text = pdf_text(pdf)
            page_no, page = grade3_comparison_page(text, state)
            language, mathematics = extract_values(page, state)
        except (urllib.error.URLError, subprocess.CalledProcessError, RuntimeError) as exc:
            failures.append(f"{state}: {exc}")
            continue
        for subject, value in [("Language", language), ("Mathematics", mathematics)]:
            rows.append(
                {
                    "state": state,
                    "subject": subject,
                    "value_pct": value,
                    "source_url": url,
                    "source_page": page_no,
                }
            )
        if len(samples) < 5:
            samples.append(f"{state} p.{page_no}: Language={language} Mathematics={mathematics}")

    rows.sort(key=lambda r: (str(r["state"]), str(r["subject"])))
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["state", "subject", "value_pct", "source_url", "source_page"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {OUT} rows={len(rows)} states={len({r['state'] for r in rows})}")
    print("verified samples: " + "; ".join(samples))
    if failures:
        print("skipped: " + "; ".join(failures), file=sys.stderr)


if __name__ == "__main__":
    main()
