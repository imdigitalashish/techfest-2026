"""P6 demo backend: static files plus live recomputation with committed code. Optional; the page works without it.

    .venv/bin/python -m demo.server [--port 8766] [--no-warm] [--port-file PATH]

Binds 127.0.0.1 only and serves the page at once. numpy/polars/sklearn/numba are imported in a background thread
after the socket is listening; a fresh venv compiles their bytecode on first import, so the first visual never waits
for that. API (JSON, CORS-open so a file:// page can upgrade to live mode):
  GET /api/status                      readiness and the current warm-up stage
  GET /api/eval?sim=&fee=&delta=       window outcomes for naive / tuned threshold / LEV (machine decision delay 7 µs)
  GET /api/race?rt=&delta=&sim=&ids=   2×2 {your RT, machine live p50} × {naive, threshold} on the window, per-trial fates
  GET /api/timing[?remeasure=1]        compiled LEV decision step timed in-kernel on this machine
"""
from __future__ import annotations

import argparse
import asyncio
import os
import socket
import threading
import time
import traceback

from aiohttp import web

HERE = os.path.dirname(os.path.abspath(__file__))
T_START = time.time()


class Holder:
    """Owns the Live object once the heavy imports finish (background thread)."""

    def __init__(self, warm: bool) -> None:
        self.live = None
        self.stage = "importing numpy / polars / scikit-learn / numba (a fresh venv compiles bytecode on first run)"
        self.error = None
        threading.Thread(target=self._load, args=(warm,), daemon=True).start()

    def _load(self, warm: bool) -> None:
        try:
            from demo.live import Live
            live = Live()
            self.live = live
            if warm:
                live.warm()
            else:
                live.stage = "ready"
        except Exception as e:  # noqa: BLE001 — reported through /api/status; the page stays on the exported grid
            self.error = f"{type(e).__name__}: {e}"
            traceback.print_exc()

    def status(self) -> dict:
        lv = self.live
        stage = self.error or (lv.stage if lv else self.stage)
        return {"ready": bool(lv and lv.ready()), "stage": stage, "uptime_s": round(time.time() - T_START, 2),
                "load_s": round(getattr(lv, "load_s", 0.0), 2), "warm_s": round(getattr(lv, "warm_s", 0.0), 2),
                "timing": lv.timing if lv else None, "error": self.error}


def json_response(obj, status: int = 200) -> web.Response:
    return web.json_response(obj, status=status, headers={"Access-Control-Allow-Origin": "*", "Cache-Control": "no-store"})


def make_app(h: Holder) -> web.Application:
    app = web.Application()
    lock = asyncio.Lock()

    async def run(fn, *a):
        async with lock:
            return await asyncio.get_running_loop().run_in_executor(None, fn, *a)

    def need_live():
        if h.live is None:
            raise web.HTTPServiceUnavailable(text='{"error": "warming"}', content_type="application/json",
                                             headers={"Access-Control-Allow-Origin": "*"})
        return h.live

    async def status(_req):
        return json_response(h.status())

    async def evaluate(req):
        live = need_live()
        q = req.query
        try:
            sim, fee, d = q.get("sim", "frozen"), float(q.get("fee", "1")), float(q.get("delta", "1"))
            D = float(q["D"]) if "D" in q else None
            if sim not in ("frozen", "strict") or fee not in live.cands or not (0 < d <= 1000):
                raise ValueError("bad parameters")
        except (ValueError, KeyError) as e:
            return json_response({"error": str(e)}, 400)
        return json_response(await run(live.evaluate, sim, fee, d, D))

    async def race(req):
        live = need_live()
        q = req.query
        try:
            rt, d, sim = float(q.get("rt", "300")), float(q.get("delta", "1")), q.get("sim", "frozen")
            ids = [int(x) for x in q.get("ids", "").split(",") if x.strip()]
            mD = float(q["machine_D_us"]) if "machine_D_us" in q else None
            if sim not in ("frozen", "strict") or not (0 < d <= 1000) or not (0 < rt <= 60000):
                raise ValueError("bad parameters")
        except (ValueError, KeyError) as e:
            return json_response({"error": str(e)}, 400)
        return json_response(await run(live.race, rt, d, sim, ids, mD))

    async def timing(req):
        live = need_live()
        if not live.compiled:
            return json_response({"ready": False, "stage": live.stage})
        if req.query.get("remeasure") == "1":
            return json_response(await run(live.measure_timing))
        return json_response(live.timing or {"ready": False, "stage": live.stage})

    async def index(_req):
        raise web.HTTPFound("/index.html")

    app.router.add_get("/api/status", status)
    app.router.add_get("/api/eval", evaluate)
    app.router.add_get("/api/race", race)
    app.router.add_get("/api/timing", timing)
    app.router.add_get("/", index)
    app.router.add_static("/", HERE, show_index=False, follow_symlinks=False)
    return app


def free_port(start: int) -> int:
    for p in range(start, start + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8766)
    ap.add_argument("--no-warm", action="store_true", help="skip Numba compilation (sklearn path only)")
    ap.add_argument("--port-file", default="", help="write the chosen port here (used by run.sh / smoke.sh)")
    a = ap.parse_args()
    port = free_port(a.port)
    app = make_app(Holder(warm=not a.no_warm))

    async def on_startup(_app):
        if a.port_file:
            with open(a.port_file, "w") as fh:
                fh.write(str(port))
        print(f"P6 demo backend on http://127.0.0.1:{port}/ ({time.time() - T_START:.1f}s after start; live mode warms up in the background)", flush=True)

    app.on_startup.append(on_startup)
    web.run_app(app, host="127.0.0.1", port=port, print=None, access_log=None)


if __name__ == "__main__":
    main()
