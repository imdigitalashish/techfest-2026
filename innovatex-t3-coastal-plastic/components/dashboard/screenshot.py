#!/usr/bin/env python3
"""Render the dashboard headless (Playwright/Chromium), fail on JS errors, save README screenshots.

Reproduce: python3 innovatex-t3-coastal-plastic/components/dashboard/screenshot.py
"""
import functools
import http.server
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent


def main() -> int:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(HERE / "site"))
    handler.log_message = lambda *a, **k: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/index.html"
    errors, out = [], {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        for name, vp, mobile in (("desktop", {"width": 1440, "height": 1000}, False), ("phone", {"width": 390, "height": 844}, True)):
            pg = b.new_page(viewport=vp, is_mobile=mobile, device_scale_factor=1)
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.on("console", lambda m: errors.append(m.text) if m.type == "error" and "tile.openstreetmap" not in m.text else None)
            pg.goto(url, wait_until="networkidle")
            pg.wait_for_selector("#verifystatus.ok, #verifystatus.bad", timeout=20000)
            out[name] = pg.inner_text("#verifystatus")
            pg.screenshot(path=str(HERE / f"screenshot-{name}.jpg"), type="jpeg", quality=60 if name == "phone" else 70, full_page=False,
                          clip=None if name == "phone" else {"x": 0, "y": 0, "width": 1440, "height": 1000})
            if name == "desktop":
                pg.click("#tamper")
                pg.wait_for_selector("#verifystatus.bad", timeout=20000)
                out["tamper"] = pg.inner_text("#verifystatus")
                pg.evaluate("document.querySelector('#records').scrollIntoView()")
                pg.screenshot(path=str(HERE / "screenshot-tamper.jpg"), type="jpeg", quality=70,
                              clip={"x": 0, "y": 0, "width": 1440, "height": 760})
            pg.close()
        b.close()
    srv.shutdown()
    for k, v in out.items():
        print(f"{k}: {v}")
    print("js_errors:", errors or "none")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
