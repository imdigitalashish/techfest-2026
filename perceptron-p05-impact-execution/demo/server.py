"""Ghost Market demo server: serves demo/ and runs fresh synced twin pairs on demand (the live lane).

  .venv/bin/python demo/server.py [--port 8650]
GET /api/status          -> {"live": bool, "reason": str, "mem": int|null, "paused": bool}
GET /api/run?seed=&qty=  -> ghost + TWAP + impact-aware (IA_sched_only) worlds, synced, via demo/p5demo.py
One run at a time, at nice >= 10. A run starts only when kern.memorystatus_level >= 30 and stops early below 25;
either way the reply is {"paused": true} and the page shows "live paused (memory guard)".
Binds 127.0.0.1 only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
import traceback
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

DEMO = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DEMO)
ABIDES = os.path.join(ROOT, ".cache", "abides-jpmc-public")
STATE = {"app": "p5-ghost-market", "live": False, "reason": "warming up the simulator"}
RUN_LOCK = threading.Lock()
D = None
TWAP = {"kind": "TWAP", "label": "TWAP"}


class Paused(Exception):
    pass


def mem_level():
    import subprocess
    try:
        return int(subprocess.run(["sysctl", "-n", "kern.memorystatus_level"], capture_output=True, text=True,
                                  timeout=5).stdout.strip())
    except Exception:
        return None


def warm():
    global D
    if not os.path.isdir(ABIDES):
        STATE.update(live=False, reason="live lane off: ABIDES not fetched (run scripts/fetch_abides.sh); replays work")
        return
    try:
        sys.path.insert(0, DEMO)
        import p5demo
        D = p5demo
        STATE.update(live=True, reason="ready")
    except Exception as e:  # missing numpy/pandas etc.
        STATE.update(live=False, reason=f"live lane off: {type(e).__name__}: {e}")


def live_run(seed: int, qty: int) -> dict:
    lv = mem_level()
    if lv is not None and lv < 30:
        raise Paused(lv)
    t0 = time.time()
    g = D.run_arm(seed, None, 0, "per_wakeup")
    import numpy as np
    arrival = float(g["res"].mid_at(np.array([D.START]))[0])
    base = int(round(arrival))
    worlds = {"ghost": D.world_view(g, base)}
    for name, spec in (("twap", TWAP), ("ia", D.ia_spec())):
        lv = mem_level()
        if lv is not None and lv < 25:
            raise Paused(lv)
        tr = D.run_arm(seed, spec, qty, "per_wakeup")
        st = D.pair_stats(g, tr)
        stats = {k: st[k] for k in ("t1", "is_bps", "drift_bps", "own_bps", "instant_bps", "filled", "n_fills",
                                    "ident", "ident_ok", "top1_exact", "hold", "arrival")}
        worlds[name] = dict(D.world_view(tr, base), fills=D.fills_view(st["fills"]), stats=stats,
                            gap2=D.half_cents(st["path"][::5]))
        del tr
    return dict(seed=seed, qty=qty, base=base, arrival=arrival, ladder_dt=D.LADDER_DT, worlds=worlds,
                label="1 new seed (live, synced)", wall_s=time.time() - t0)


def _clean(o):
    if isinstance(o, float) and o != o:
        return None
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_clean(v) for v in o]
    return o


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=DEMO, **k)

    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _json(self, code, obj):
        body = json.dumps(_clean(obj), separators=(",", ":"), allow_nan=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api/status":
            lv = mem_level()
            return self._json(200, dict(STATE, mem=lv, paused=bool(lv is not None and lv < 30)))
        if u.path == "/api/run":
            if not STATE["live"]:
                return self._json(503, {"error": STATE["reason"]})
            q = parse_qs(u.query)
            try:
                seed = int(q.get("seed", ["2026"])[0])
                qty = int(q.get("qty", ["4000"])[0])
                assert 0 <= seed < 2 ** 31 and 1000 <= qty <= 16000 and qty % 1000 == 0
            except Exception:
                return self._json(400, {"error": "seed must be 0..2^31-1 and qty one of 1,000..16,000 (step 1,000)"})
            if not RUN_LOCK.acquire(blocking=False):
                return self._json(409, {"busy": True})
            try:
                return self._json(200, live_run(seed, qty))
            except Paused as p:
                return self._json(200, {"paused": True, "reason": "live paused (memory guard)", "mem": p.args[0]})
            except Exception as e:
                traceback.print_exc()
                return self._json(500, {"error": f"{type(e).__name__}: {e}"})
            finally:
                RUN_LOCK.release()
        return super().do_GET()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8650)
    a = ap.parse_args()
    try:
        cur = os.nice(0)
        if cur < 10:
            os.nice(10 - cur)
    except OSError:
        pass
    srv = None
    for port in range(a.port, a.port + 20):
        try:
            srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    if srv is None:
        sys.exit("no free port")
    threading.Thread(target=warm, daemon=True).start()
    print(f"SERVING http://127.0.0.1:{srv.server_address[1]}/", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
