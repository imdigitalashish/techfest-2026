"""Regenerate the fallback deck (demo/fallback/*.png) from the live page, in talk-track order.

    cd perceptron-p04-lob-regimes && python demo/capture_fallback.py      # needs the replay/splice cache (run.sh)

Serves demo/ on a free local port, drives headless Chromium (Python Playwright) through the SCRIPT.md story and
saves one PNG per step. Prices appear only as 10-minute candles and alarms only as 10-minute counts.
"""
from __future__ import annotations

import socket
import subprocess
import sys
import time
from pathlib import Path

DEMO = Path(__file__).resolve().parent
OUT = DEMO / "fallback"

# (file, day, dial stop, element to capture, extra action)
DECK = [
    ("01_scoreboard.png", None, "naive_3", "#scoreboard", None),
    ("02_stage_2026-08-01_alpha_1e-3.png", "2026-08-01", "naive_3", "#stage", None),
    ("03_stage_2026-08-01_alpha_1e-30_HERO.png", "2026-08-01", "naive_30", "#stage", None),
    ("04_stage_2026-08-01_calibrated_q0.999.png", "2026-08-01", "cal_0.999", "#stage", None),
    ("05_stage_2026-08-01_off.png", "2026-08-01", "off", "#stage", None),
    ("06_fees_vip9_100ms.png", None, "naive_3", "#exec", "fees"),
    ("07_splice_calm_to_volatile_12h_SEMI-SYNTHETIC.png", None, "naive_3", "#splice", None),
    ("A1_stage_2026-10-01_lower_median_alpha_1e-30.png", "2026-10-01", "naive_30", "#stage", None),
    ("A2_stage_2026-03-01_most_volatile_alpha_1e-30.png", "2026-03-01", "naive_30", "#stage", None),
    ("A3_stage_2024-05-01_fomc_dev_illustrative.png", "2024-05-01", "naive_3", "#stage", None),
    ("A4_details_dial_sweep_and_why.png", "2026-08-01", "naive_30", "#details", "details"),
]


def main() -> int:
    from playwright.sync_api import sync_playwright
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1", "--directory", str(DEMO)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(0.8)
        OUT.mkdir(exist_ok=True)
        for old in OUT.glob("*.png"):
            old.unlink()
        with sync_playwright() as pw:
            br = pw.chromium.launch()
            p = br.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
            p.goto(f"http://127.0.0.1:{port}/index.html")
            p.wait_for_selector("body[data-ready='1']")
            p.wait_for_function("() => document.querySelector('#splice').dataset.shown", timeout=30000)
            for name, day, stop, sel, extra in DECK:
                if day:
                    p.evaluate("d => selectDay(d)", day)
                    p.wait_for_function("d => document.querySelector('#rp-totals').dataset.payloadDay === d", arg=day, timeout=30000)
                p.evaluate("id => setStop(id)", stop)
                if extra == "fees":
                    p.locator("#k-tier button", has_text="VIP 9").click()
                    p.locator("#k-delay button", has_text="100 ms").click()
                    p.locator("#k-pol button", has_text="Regime gate").click()
                if extra == "details":
                    p.evaluate("() => { document.querySelector('#details').open = true; }")
                    p.wait_for_timeout(300)
                    p.evaluate("() => { drawReplay(); drawDial(); }")
                p.wait_for_timeout(400)
                p.locator(sel).screenshot(path=str(OUT / name))
                print("wrote", name)
                if extra == "details":
                    p.evaluate("() => { document.querySelector('#details').open = false; }")
            br.close()
    finally:
        srv.terminate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
