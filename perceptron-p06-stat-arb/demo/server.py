"""P6 demo backend: static files plus live recomputation with committed code. Optional; the page works without it.

    .venv/bin/python -m demo.server [--port 8766] [--no-warm]

Binds 127.0.0.1 only. API (JSON, CORS-open so a file:// page can upgrade to live mode):
  GET /api/status                      readiness; Numba compiles in a background thread after start-up
  GET /api/eval?sim=&fee=&delta=       window outcomes for naive / tuned threshold / LEV (machine decision delay 7 µs)
  GET /api/race?rt=&delta=&sim=&ids=   2×2 {your RT, machine live p50} × {naive, threshold} on the window, per-trial fates
  GET /api/timing[?remeasure=1]        compiled LEV decision step timed in-kernel on this machine
"""
from __future__ import annotations

import argparse
import asyncio
import socket
import threading
import time

from aiohttp import web

from demo.live import HERE, Live

T_START = time.time()


def json_response(obj, status: int = 200) -> web.Response:
    return web.json_response(obj, status=status, headers={"Access-Control-Allow-Origin": "*", "Cache-Control": "no-store"})


def make_app(live: Live) -> web.Application:
    app = web.Application()
    lock = asyncio.Lock()

    async def run(fn, *a):
        async with lock:
            return await asyncio.get_running_loop().run_in_executor(None, fn, *a)

    async def status(_req):
        return json_response({"ready": live.ready(), "stage": live.stage, "uptime_s": round(time.time() - T_START, 2),
                              "load_s": round(live.load_s, 2), "warm_s": round(getattr(live, "warm_s", 0.0), 2), "timing": live.timing})

    async def evaluate(req):
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
    live = Live()
    if not a.no_warm:
        threading.Thread(target=live.warm, daemon=True).start()
    port = free_port(a.port)
    if a.port_file:
        with open(a.port_file, "w") as fh:
            fh.write(str(port))
    print(f"P6 demo backend on http://127.0.0.1:{port}/ (assets loaded in {live.load_s:.1f}s; Numba warming in background)", flush=True)
    web.run_app(make_app(live), host="127.0.0.1", port=port, print=None, access_log=None)


if __name__ == "__main__":
    main()
