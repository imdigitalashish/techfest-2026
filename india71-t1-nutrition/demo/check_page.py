"""Headless load of the offline demo page (optional step of demo/smoke.sh). Needs Python Playwright + Chromium.

Loads every screen from file:// (no server), asserts key on-screen values, no page errors and no non-file requests,
and that the first screen is ready well under the 60-second bar. Run: python3 demo/check_page.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = (Path(__file__).resolve().parent / "index.html").as_uri()
EXPECT = [
    ("india", ["all 36 States and UTs", "19.3%", "5.46%", "REAL DATA"]),
    ("districts&state=MH&district=Nandurbar&cohort=nandurbar", ["In Nandurbar, 30.7%", "13.5%", "45.8%", "706 of 707 districts"]),
    ("find&cov=0.35&noise=0", ["0.51", "0.94", "0.97", "simulation assumption", "SYNTHETIC"]),
    ("find&cov=0&noise=0.4", ["true by definition", "0.89", "0.70"]),
    ("child&cohort=nandurbar", ["SIMULATED children · REAL district rates", "correctly", "wasting begins"]),
    ("week&cohort=nandurbar&K=5&reveal=1", ["Who gets them?", "Listed and then wasted", "0.429"]),
    ("sms&cohort=amravati", ["no names", "overflow", "ASHA"]),
    ("break&cohort=nandurbar&req=cdpo_discipline&tamper=truncate", ["DENIED", "deny-employment-action", "broken at entry", "chain verifies"]),
    ("break&cohort=nandurbar&tamper=resealall", ["chain verifies", "broken at entry"]),
]


def main() -> int:
    errors: list[str] = []
    foreign: list[str] = []
    failures = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("request", lambda r: foreign.append(r.url) if not r.url.startswith(("file:", "data:", "about:")) else None)
        t0 = time.perf_counter()
        page.goto(f"{URL}#india")
        page.wait_for_selector("html[data-ready='1']", timeout=60000)
        first = time.perf_counter() - t0
        ok = first < 60
        failures += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} first visual ready in {first:.2f} s (bar: 60 s)")
        for fragment, needles in EXPECT:
            page.goto("about:blank")
            page.goto(f"{URL}#{fragment}")
            page.wait_for_selector("html[data-ready='1']")
            text = page.inner_text("main")
            missing = [n for n in needles if n not in text]
            failures += bool(missing)
            print(f"  {'ok  ' if not missing else 'FAIL'} #{fragment.split('&')[0]:<9} {', '.join(needles) if not missing else 'missing: ' + ', '.join(missing)}")
        page.goto("about:blank")
        page.goto(f"{URL}#find&cov=0&noise=0.4")
        page.wait_for_selector("html[data-ready='1']")
        vals = [float(v) for v in page.locator("#s-find .bar .val").all_inner_texts()]
        ok = len(vals) == 3 and vals[2] > vals[0] and vals[2] > vals[1]
        failures += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} no shared IDs, +40% typos: Bloom-filter F1 {vals[2] if vals else '?'} beats shared-ID {vals[0] if vals else '?'} and pooled names {vals[1] if vals else '?'}")
        browser.close()
    if errors:
        failures += 1
        print("  FAIL page errors:", *errors, sep="\n    ")
    if foreign:
        failures += 1
        print("  FAIL non-file requests:", *foreign, sep="\n    ")
    if not errors and not foreign:
        print("  ok   no page errors; no network requests (file:// only)")
    print("check_page:", f"{failures} FAILED" if failures else "all checks pass")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
