"""Browser regression for the P6 demo page: headless Chrome driven over the DevTools protocol (aiohttp websocket; no new
dependencies). Used by demo/smoke.py. Skipped, and reported as skipped, when no Chrome/Chromium binary is found
(set CHROME=/path/to/chrome to choose one).

Covers the stage-safety and state findings of reviews/2026-10-04-demo-gpt-6-astra.md:
  D02  sweeping to δ = 20 ms and pressing Start races at the named setup (frozen · 1 bp · 1 ms);
  D01  five trials with ~300 ms presses finish within the presenter deadline; every trial is logged;
  D04  after the backend dies, the page notices without interaction and, before anything is touched, no label (the
       finished race included) still claims live computation; after a δ change the race is rescored offline;
  D10  the offline race summary names the committed p50 as the ratio's base.
"""
from __future__ import annotations

import asyncio
import glob
import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import time

import aiohttp
from urllib.parse import quote
from yarl import URL


def find_chrome() -> tuple[str | None, bool]:
    """(binary, is_headless_shell)."""
    home = os.path.expanduser("~")
    cands = [os.environ.get("CHROME", ""),
             "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             "/Applications/Chromium.app/Contents/MacOS/Chromium",
             shutil.which("google-chrome") or "", shutil.which("google-chrome-stable") or "",
             shutil.which("chromium") or "", shutil.which("chromium-browser") or ""]
    for c in cands:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c, False
    shells = sorted(glob.glob(f"{home}/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-*/chrome-headless-shell")
                    + glob.glob(f"{home}/.cache/ms-playwright/chromium_headless_shell-*/chrome-*/chrome-headless-shell"))
    return (shells[-1], True) if shells else (None, False)


class Page:
    def __init__(self, ws):
        self.ws, self.n = ws, 0

    async def send(self, method: str, params: dict | None = None) -> dict:
        self.n += 1
        mid = self.n
        await self.ws.send_str(json.dumps({"id": mid, "method": method, "params": params or {}}))
        while True:
            msg = json.loads((await self.ws.receive()).data)
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg["result"]

    async def ev(self, expr: str):
        r = await self.send("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
        if "exceptionDetails" in r:
            raise RuntimeError(f"JS error in {expr[:80]}: {r['exceptionDetails'].get('text')} {r['exceptionDetails'].get('exception', {}).get('description', '')[:200]}")
        return r["result"].get("value")

    async def wait(self, expr: str, timeout: float, poll: float = 0.03):
        t0 = time.time()
        while time.time() - t0 < timeout:
            v = await self.ev(expr)
            if v:
                return v
            await asyncio.sleep(poll)
        raise TimeoutError(f"timed out after {timeout:.0f} s waiting for: {expr[:120]}")


LABELS_JS = """({mode: document.getElementById('mode').textContent, ok: document.getElementById('liveok').textContent,
    scope: document.getElementById('scope').textContent, rule: document.getElementById('raceRule').textContent,
    status: document.getElementById('raceStatus').textContent, setup: document.getElementById('raceSetup').textContent,
    two: document.getElementById('two').textContent, trials: document.getElementById('trials').textContent,
    summary: document.getElementById('raceSummary').textContent, big: document.getElementById('bigcmp').textContent,
    cards: [...document.querySelectorAll('.card')].map(c => c.textContent).join(' ')})"""
LIVE_CLAIM = re.compile(r"\bLIVE\b|measured live|recomputed live|live p50|\bLive:|\blive ·|\(live\)|median, exact|exact RT")


def live_claims(labels: dict) -> list[str]:
    """Labels that still claim live computation, as 'label: matched text'."""
    return [f"{k}: {m.group(0)!r}" for k, v in labels.items() for m in [LIVE_CLAIM.search(v)] if m]


SET_DELTA = "(d => { const s = document.getElementById('delta'); s.value = P6_DATA.meta.deltas_ms.indexOf(d); s.dispatchEvent(new Event('input')); })"
PRESS = "document.dispatchEvent(new KeyboardEvent('keydown', {code: 'Space', key: ' ', bubbles: true}))"


async def scenario(cdp_port: int, url: str, kill_backend, ok) -> None:
    async with aiohttp.ClientSession() as http:
        async with http.put(URL(f"http://127.0.0.1:{cdp_port}/json/new?{quote(url, safe='')}", encoded=True)) as r:
            target = await r.json(content_type=None)
        async with http.ws_connect(target["webSocketDebuggerUrl"], max_msg_size=0) as ws:
            pg = Page(ws)
            await pg.send("Runtime.enable")
            await pg.send("Emulation.setDeviceMetricsOverride", {"width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False})
            await pg.wait("window.P6_STATE && P6_STATE.conn === 'live' && !!P6_STATE.liveRes", 60)
            labels = await pg.ev("({mode: document.getElementById('mode').textContent, ok: document.getElementById('liveok').textContent})")
            ok("browser: page reaches LIVE and labels it", "LIVE" in labels["mode"] and "recomputed live" in labels["ok"], labels["mode"])

            # D02: the scripted sweep ends at 20 ms; Start must race at the named setup
            await pg.ev(f"{SET_DELTA}(20)")
            await pg.ev("document.querySelector('#steps button[data-step=\"2\"]').click()")
            t0 = time.time()
            await pg.ev("document.getElementById('raceBtn').click()")
            st = await pg.ev("({sim: P6_STATE.sim, fee: P6_STATE.fee, d: P6_DATA.meta.deltas_ms[P6_STATE.di], speed: P6_STATE.speed, setup: document.getElementById('raceSetup').textContent})")
            ok("browser: Start applies the named race setup (frozen · 1 bp · 1 ms · 1×) after a sweep to 20 ms",
               (st["sim"], st["fee"], st["d"], st["speed"]) == ("frozen", 1, 1, 1) and "Racing at the race setup" in st["setup"], str({k: st[k] for k in ("sim", "fee", "d", "speed")}))

            # D01: five automated presses ~300 ms after each flash; one deliberate false start first
            await pg.wait("P6_STATE.race.state === 'wait'", 10)
            await asyncio.sleep(0.2)
            await pg.ev(PRESS)
            for _ in range(5):
                await pg.wait("P6_STATE.race.state === 'flash'", 15, poll=0.005)
                await asyncio.sleep(0.3)
                await pg.ev(PRESS)
                await pg.wait("P6_STATE.race.state !== 'flash'", 5)
            await pg.wait("P6_STATE.race.result && !P6_STATE.race.running", 30)
            wall = time.time() - t0
            r = await pg.ev("""(() => { const R = P6_STATE.race, g = P6_DATA.grid_window['frozen|f1|d1|D7'].tot;
                return {wallS: R.wallS, deadline: 45, log: R.log.map(x => x.kind), n: R.trials.length, src: R.result.src, sim: R.result.sim, d: R.result.d,
                        machThr: R.result.mach.thr.usd, gridThr: g.thr.usd, rows: document.querySelectorAll('#trials tbody tr').length}; })()""")
            ok("browser: a 5-trial race (plus a false start) finishes within the 45 s presenter deadline",
               r["n"] == 5 and r["wallS"] <= r["deadline"] and wall <= r["deadline"] + 5, f"{r['wallS']:.1f} s in-page, {wall:.1f} s wall; log {r['log']}")
            ok("browser: every trial and the false start are listed", r["rows"] == 6 and r["log"].count("false") == 1, f"{r['rows']} table rows")
            ok("browser: race scored live at the race setup; machine selector = exported grid",
               r["src"] == "live" and r["sim"] == "frozen" and r["d"] == 1 and abs(r["machThr"] - r["gridThr"]) < 1e-6, f"machine threshold {r['machThr']:+.2f} USD")

            # sanity: before the kill, the race panel does carry live labels (so the checks below can fail)
            before = await pg.ev(LABELS_JS)
            ok("browser: before the loss the race panel is labelled live (precondition)",
               bool(live_claims({k: before[k] for k in ("status", "two", "summary")})), before["status"])

            # D04: kill the backend and touch NOTHING: the heartbeat must notice, and every label, the finished race
            # included, must stop claiming live computation without any interaction
            t1 = time.time()
            kill_backend()
            await pg.wait("P6_STATE.conn === 'lost'", 15)
            ok("browser: backend loss detected without interaction", True, f"{time.time() - t1:.1f} s after the kill")
            await pg.wait("P6_STATE.race.result && P6_STATE.race.result.src === 'grid'", 5)
            lab = await pg.ev(LABELS_JS)
            stale = live_claims(lab)
            ok("browser: untouched after the loss, no label (race panel included) claims live computation",
               "OFFLINE" in lab["mode"] and "lost" in lab["mode"] and "exported grid" in lab["ok"] and "backend lost" in lab["scope"]
               and "scored after the backend was lost" in lab["status"] and "Offline:" in lab["summary"] and "exported grid" in lab["big"]
               and "compute allowance" in lab["two"] and not stale,
               f"race status '{lab['status']}'" + (f"; stale: {stale}" if stale else ""))
            ok("browser: offline race ratio is against the committed p50, outcomes at the 7 µs allowance (D10)",
               "committed decision-step p50" in lab["summary"] and "7 µs allowance" in lab["summary"], "")

            # then change δ offline: the same reaction times are rescored on the grid and the labels stay offline
            await pg.ev(f"{SET_DELTA}(5)")
            await pg.wait("P6_STATE.race.result && P6_STATE.race.result.src === 'grid' && P6_STATE.race.result.d === 5", 10)
            lab2 = await pg.ev(LABELS_JS)
            stale2 = live_claims(lab2)
            ok("browser: after changing δ offline, the race is rescored at 5 ms and labels stay offline",
               "δ = 5 ms" in lab2["summary"] and "OFFLINE" in lab2["mode"] and not stale2, "; ".join(stale2))
            errs = await pg.ev("window.__p6errors ? window.__p6errors.length : 0")
            ok("browser: no uncaught page errors", errs == 0, f"{errs} error(s)")


def run(page_url: str, kill_backend, ok) -> bool:
    chrome, shell = find_chrome()
    if not chrome:
        print("SKIP  browser regression: no Chrome/Chromium binary found (set CHROME=/path/to/chrome)", flush=True)
        return False
    udd = tempfile.mkdtemp(prefix="p6chrome-")
    args = [chrome, "--remote-debugging-port=0", f"--user-data-dir={udd}", "--no-first-run", "--no-default-browser-check", "--disable-gpu",
            "--disable-extensions", "--disable-background-timer-throttling", "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows", "--window-size=1440,900", "about:blank"]
    if not shell:
        args.insert(1, "--headless=new")
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        pf, t0 = os.path.join(udd, "DevToolsActivePort"), time.time()
        while not (os.path.exists(pf) and open(pf).read().strip()):
            if time.time() - t0 > 30 or proc.poll() is not None:
                ok("browser: headless Chrome started", False, chrome)
                return True
            time.sleep(0.1)
        port = int(open(pf).read().split()[0])
        try:
            asyncio.run(scenario(port, page_url, kill_backend, ok))
        except Exception as e:  # noqa: BLE001 — a failed wait or JS error is a failed regression, not a crash
            ok("browser: regression scenario completed", False, f"{type(e).__name__}: {e}")
        return True
    finally:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
            proc.wait(timeout=10)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            pass
        shutil.rmtree(udd, ignore_errors=True)
