"""Capture the demo's fallback screenshots and an animated GIF of the linkage knobs, headless and offline.

Needs Playwright for Python with Chromium, plus Pillow (demo/requirements-demo.txt):
    python3 -m pip install -r demo/requirements-demo.txt && python3 -m playwright install chromium
Run from india71-t1-nutrition/:  python3 demo/capture_fallback.py
Writes demo/fallback/NN-*.png and demo/fallback/find-every-child.gif. Fails on any page error or any non-file:// request.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

DEMO = Path(__file__).resolve().parent
URL = (DEMO / "index.html").as_uri()
OUT = DEMO / "fallback"
SHOTS = [
    ("01-india-surveyed", "india"),
    ("02-india-reported", "india&tileMode=pt"),
    ("03-districts-nandurbar", "districts&state=MH&district=Nandurbar&cohort=nandurbar"),
    ("04-find-as-simulated", "find&cov=0.35&noise=0&cohort=nandurbar"),
    ("05-find-no-ids-40pct-typos", "find&cov=0&noise=0.4&cohort=nandurbar"),
    ("06-one-child-nandurbar", "child&cohort=nandurbar"),
    ("07-this-week-revealed", "week&cohort=nandurbar&K=5&reveal=1"),
    ("08-worker-sms", "sms&cohort=nandurbar"),
    ("09-break-it-discipline-truncate", "break&cohort=nandurbar&req=cdpo_discipline&tamper=truncate"),
    ("10-break-it-reseal-all", "break&cohort=nandurbar&req=fake_consent&tamper=resealall"),
    ("11-districts-amravati-melghat", "districts&state=MH&district=Amravati&cohort=amravati"),
    ("12-one-child-amravati", "child&cohort=amravati"),
]
GIF_SEQUENCE = [(1.0, 0), (0.75, 0), (0.5, 0), (0.35, 0), (0.2, 0), (0.1, 0), (0.0, 0), (0.0, 0.1), (0.0, 0.2), (0.0, 0.3), (0.0, 0.4)]


def main() -> int:
    OUT.mkdir(exist_ok=True)
    errors: list[str] = []
    foreign: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("request", lambda r: foreign.append(r.url) if not r.url.startswith(("file:", "data:", "about:")) else None)

        def load(fragment: str) -> None:
            page.goto("about:blank")
            page.goto(f"{URL}#{fragment}")
            page.wait_for_selector("html[data-ready='1']", timeout=15000)
            page.wait_for_timeout(450)

        for name, fragment in SHOTS:
            load(fragment)
            page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
            print("wrote", f"demo/fallback/{name}.png")

        frames = []
        for cov, noise in GIF_SEQUENCE:
            load(f"find&cov={cov:g}&noise={noise:g}&cohort=nandurbar")
            img = Image.open(io.BytesIO(page.locator("#s-find .g-link > .panel").first.screenshot())).convert("RGB")
            img = img.resize((760, round(img.height * 760 / img.width)), Image.LANCZOS)
            frames.append(img.quantize(colors=96, method=Image.Quantize.MEDIANCUT))
        durations = [900] * (len(frames) - 1) + [2600]
        frames[0].save(OUT / "find-every-child.gif", save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
        print("wrote demo/fallback/find-every-child.gif")
        browser.close()
    if errors:
        print("PAGE ERRORS:", *errors, sep="\n  ")
    if foreign:
        print("NON-FILE REQUESTS:", *foreign, sep="\n  ")
    return 1 if errors or foreign else 0


if __name__ == "__main__":
    sys.exit(main())
