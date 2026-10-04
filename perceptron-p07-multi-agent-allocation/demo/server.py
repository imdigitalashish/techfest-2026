"""P7 demo server (Python stdlib only): serves demo/index.html and a small JSON API over demo/engine.py.

    .venv/bin/python -m demo.server [--port 8707] [--no-open] [--t0 EPOCH_SECONDS]

Binds 127.0.0.1 only and needs no network at run time.
  POST /api/live/new    {scenario, L, P, rule, brain, drift, seed, role} -> a new city. synthetic: armed inside the
                        onset window of its committed reference (config.reference). nyc: role 'reference' (unperturbed,
                        fast-forwarding to 21:15 on 4 July in the background) or 'interactive' (taken from a pool that
                        is pre-warmed to 21:15 in the background, so the judge's turn starts at once)
  POST /api/live/warm   {sid, from, frames}               -> fast-forward time-lapse frames; snapshot when done
  POST /api/live/step   {sid, n}                          -> next n simulated minutes (frames)
  POST /api/live/shock  {sid, zone, size}                 -> unannounced shock from the current minute; 400 if the
                        run has ended (no zero-length surges) or it is the unperturbed NYC reference run
  POST /api/run         {kind: week|nyc|shock-day, seed}  -> recompute a committed episode in the background
  GET  /api/run/<rid>?from=k                              -> frames so far, summary and parity when done
  GET  /api/health ;  POST /api/first_visual (time-to-first-visual report)
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import platform
import queue
import secrets
import socket
import sys
import threading
import time
import webbrowser
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.metadata import version
from urllib.parse import parse_qs, urlparse

from demo.engine import BRAINS, DEMO, DEMO_SEED, RULES, LiveRun, batch_worker, best_rules

TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".json": "application/json",
         ".png": "image/png", ".gif": "image/gif", ".mp4": "video/mp4", ".md": "text/plain; charset=utf-8"}
LIVE: OrderedDict[str, LiveRun] = OrderedDict()
RUNS: dict[str, "RemoteRun"] = {}
LOCK = threading.Lock()
STATE = dict(t0=None, started=time.time(), first_visual_s=None)
SHOW = {"week": ("greedy", "reactive", "mpc-ewma"), "nyc": ("reactive", "mpc-ewma"), "shock-day": ("greedy", "mpc-ewma")}
POOL: dict = dict(run=None, filling=False)   # one interactive NYC session, pre-warmed to 21:15 in the background
POOL_LOCK = threading.Lock()
BUSY: dict = dict(step=0.0, warms=0)   # when a session last stepped; warm-ups someone is waiting for


def pool_polite() -> float:
    """The background warm-up yields while a session plays or another warm-up runs; otherwise it runs at full speed."""
    return 0.002 if BUSY["warms"] > 0 or time.time() - BUSY["step"] < 1.0 else 0.0


def busy_warm(run: LiveRun, **kw) -> LiveRun:
    with POOL_LOCK:
        BUSY["warms"] += 1
    try:
        return run.warm(**kw)
    finally:
        with POOL_LOCK:
            BUSY["warms"] -= 1


def pool_fill(polite=pool_polite) -> None:
    """Pre-warm one interactive NYC session in the background, so the judge's turn starts at once without stalling
    the session that is playing."""
    with POOL_LOCK:
        if POOL["run"] is not None or POOL["filling"]:
            return
        POOL["filling"] = True
    try:
        run = LiveRun(scenario="nyc", role="interactive")
        with POOL_LOCK:
            POOL["run"] = run
    finally:
        with POOL_LOCK:
            POOL["filling"] = False
    run.warm(polite=polite)


def pool_take() -> LiveRun:
    with POOL_LOCK:
        run, POOL["run"] = POOL["run"], None
    if run is None:   # nothing pre-warmed: warm at full speed, someone is waiting
        run = LiveRun(scenario="nyc", role="interactive")
        threading.Thread(target=busy_warm, args=(run,), daemon=True).start()
    else:
        run.polite = 0.0   # if still warming, finish at full speed

    def refill() -> None:   # after this run is ready, so the two warm-ups do not compete
        while not run.warmed:
            time.sleep(0.25)
        time.sleep(3.0)
        pool_fill()
    threading.Thread(target=refill, daemon=True).start()
    return run


def health() -> dict:
    try:
        hv = version("highspy")
    except Exception:
        hv = None
    return dict(ok=True, python=platform.python_version(), highspy=hv, uptime_s=round(time.time() - STATE["started"], 1),
                first_visual_s=STATE["first_visual_s"], live_sessions=len(LIVE), demo_seed=DEMO_SEED,
                best_rules={f"{k[0]},{k[1]}": v for k, v in best_rules().items()}, rules=RULES, brains=BRAINS)


def register(run: LiveRun) -> str:
    sid = secrets.token_hex(6)
    with LOCK:
        LIVE[sid] = run
        while len(LIVE) > 6:
            LIVE.popitem(last=False)
    return sid


def live_new(b: dict) -> dict:
    scenario = str(b.get("scenario", "synthetic"))
    if scenario == "nyc":
        role = str(b.get("role", "reference"))
        if role == "interactive":
            run = pool_take()
        elif role == "reference":   # fast-forward to 21:15 on 4 July in the background; the page plays the time-lapse
            run = LiveRun(scenario="nyc", role="reference")
            snap = run.snapshot()   # 3 July 00:00, before the warm-up thread starts
            threading.Thread(target=lambda: (busy_warm(run, every=10), pool_fill()), daemon=True).start()
            return dict(sid=register(run), config=run.describe(), snapshot=snap, warming=True)
        else:
            raise ValueError("unknown role")
        return dict(sid=register(run), config=run.describe(), warming=True)
    run = LiveRun(L=int(b.get("L", 1)), P=int(b.get("P", 10)), rule=str(b.get("rule", "auto")),
                  brain=str(b.get("brain", "mpc-ewma")), drift=bool(b.get("drift", False)),
                  seed=int(b.get("seed", DEMO_SEED)), scenario="synthetic")
    busy_warm(run)
    return dict(sid=register(run), config=run.describe(), snapshot=run.snapshot(), stats=run.stats(), warming=False)


def live_warm(b: dict) -> dict:
    run, k = live_get(b), int(b.get("from", 0))
    want = bool(b.get("frames", True))   # False: no time-lapse (the interactive run opens armed at its start)
    fr = run.warm_frames[k:k + 300] if want else []
    out = dict(frames=fr, next=k + len(fr), t=run.t, target=run.start, error=run.error,
               done=run.warmed and (not want or k + len(fr) >= len(run.warm_frames)))
    if out["done"]:
        out.update(snapshot=run.snapshot(), stats=run.stats())
    return out


class SessionGone(Exception):
    """The page holds a session id this server does not know (expired, or the server restarted)."""


def live_get(b: dict) -> LiveRun:
    run = LIVE.get(str(b.get("sid")))
    if run is None:
        raise SessionGone("this session has expired (the server may have restarted)")
    return run


class RemoteRun:
    """A demo.engine.BatchRun computed in a niced child process; same poll() interface."""

    def __init__(self, kind: str, seed: int, show: tuple):
        self.kind, self.seed = kind, seed
        self.frames: list = []
        self.meta: dict = dict(kind=kind, seed=seed, T=None, info={}, event=None, policies=[], show=list(show))
        self.t, self.done, self.error, self.summary, self.wall = 0, False, None, None, 0.0
        self.lock = threading.Lock()
        ctx = mp.get_context("spawn")
        self.q = ctx.Queue()
        self.proc = ctx.Process(target=batch_worker, args=(kind, seed, tuple(show), self.q), daemon=True)
        self.proc.start()

    def wait(self) -> "RemoteRun":
        while True:
            try:
                msg = self.q.get(timeout=1.0)
            except queue.Empty:
                if not self.proc.is_alive():
                    self.error, self.done = f"worker process exited (code {self.proc.exitcode})", True
                    return self
                continue
            if msg[0] == "static":
                self.meta = msg[1]
            elif msg[0] == "frames":
                with self.lock:
                    self.frames.extend(msg[1])
                    self.t = msg[2]
            else:
                self.summary, self.error, self.wall = msg[1], msg[2], msg[3]
                self.done = True
                self.proc.join(timeout=5)
                return self

    def poll(self, k: int, limit: int = 400) -> dict:
        with self.lock:
            fr = self.frames[k:k + limit]
            n = len(self.frames)
        return dict(self.meta, t=self.t, frames=fr, next=k + len(fr), available=n,
                    done=self.done and k + len(fr) >= n, error=self.error, summary=self.summary if self.done else None)


def report(r: RemoteRun) -> None:
    s = r.summary
    if r.error or s is None:
        print(f"[P7 demo] {r.kind} recompute FAILED: {r.error}", flush=True)
        return
    ok = sum(bool(v) and all(v["checks"].values()) for v in s["parity"].values())
    print(f"[P7 demo] {r.kind} (seed {r.seed}) recomputed in {s['wall_s']} s; parity with {s['row']}: "
          f"{'OK' if s['parity_all'] else 'MISMATCH'} ({ok}/{len(s['parity'])} allocators)", flush=True)


def run_start(b: dict, wait: bool = False) -> dict:
    kind, seed = str(b.get("kind")), int(b.get("seed", 200))
    if kind not in SHOW:
        raise ValueError("unknown run kind")
    rid = f"{kind}-{seed}"
    with LOCK:
        r = RUNS.get(rid)
        fresh = r is None or bool(r.error)
        if fresh:
            r = RUNS[rid] = RemoteRun(kind, seed, SHOW[kind])
    if fresh:
        if wait:
            report(r.wait())
        else:
            threading.Thread(target=lambda: report(r.wait()), daemon=True).start()
    return dict(rid=rid)


def prewarm() -> None:
    """Recompute the week in the background so that tab plays at once (July 4th runs as live sessions)."""
    time.sleep(1.5)
    for kind in ("week",):
        try:
            run_start(dict(kind=kind, seed=200), wait=True)
        except Exception as e:  # the tab retries on demand
            print(f"[P7 demo] prewarm {kind} failed: {e!r}", flush=True)


class Handler(BaseHTTPRequestHandler):
    server_version = "P7Demo/1.0"

    def log_message(self, fmt, *args):  # keep the terminal readable during a demo
        pass

    def _send(self, body: bytes, ctype: str, code: int = 200) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code: int = 200) -> None:
        self._send(json.dumps(obj, separators=(",", ":")).encode(), "application/json", code)

    def do_GET(self):
        u = urlparse(self.path)
        try:
            if u.path in ("/", "/index.html"):
                return self._send((DEMO / "index.html").read_bytes(), TYPES[".html"])
            if u.path == "/api/health":
                return self._json(health())
            if u.path.startswith("/api/run/"):
                r = RUNS.get(u.path.rsplit("/", 1)[-1])
                if r is None:
                    return self._json(dict(error="unknown run"), 404)
                k = int(parse_qs(u.query).get("from", ["0"])[0])
                return self._json(r.poll(k))
            p = (DEMO / u.path.lstrip("/")).resolve()
            if (DEMO / "data") in p.parents or (DEMO / "fallback") in p.parents:
                if p.is_file() and p.suffix in TYPES:
                    return self._send(p.read_bytes(), TYPES[p.suffix])
            return self._json(dict(error="not found"), 404)
        except Exception as e:
            return self._json(dict(error=repr(e)), 500)

    def do_POST(self):
        u = urlparse(self.path)
        try:
            n = int(self.headers.get("Content-Length") or 0)
            b = json.loads(self.rfile.read(n) or b"{}") if n else {}
            if u.path == "/api/live/new":
                return self._json(live_new(b))
            if u.path == "/api/live/warm":
                return self._json(live_warm(b))
            if u.path == "/api/live/step":
                BUSY["step"] = time.time()
                run = live_get(b)
                frames = run.advance(min(256, int(b.get("n", 1))))
                return self._json(dict(frames=frames, stats=run.stats()))
            if u.path == "/api/live/shock":
                run = live_get(b)
                sh = run.shock(int(b["zone"]), float(b.get("size", 1.0)))
                return self._json(dict(shock=sh, stats=run.stats()))
            if u.path == "/api/run":
                return self._json(run_start(b))
            if u.path == "/api/first_visual":
                if STATE["first_visual_s"] is None:
                    ref = STATE["t0"] or STATE["started"]
                    STATE["first_visual_s"] = round(time.time() - ref, 2)
                    since = "run.sh started" if STATE["t0"] else "the server started"
                    print(f"[P7 demo] first visual {STATE['first_visual_s']:.1f} s after {since}", flush=True)
                return self._json(dict(first_visual_s=STATE["first_visual_s"]))
            return self._json(dict(error="not found"), 404)
        except SessionGone as e:
            return self._json(dict(error=str(e), code="session_gone"), 410)
        except (KeyError, ValueError) as e:
            return self._json(dict(error=str(e).strip("'")), 400)
        except Exception as e:
            return self._json(dict(error=repr(e)), 500)


def bind(port: int) -> ThreadingHTTPServer:
    tries = [port] if port == 0 else list(range(port, port + 20))
    for p in tries:
        try:
            srv = ThreadingHTTPServer(("127.0.0.1", p), Handler)
            srv.daemon_threads = True
            return srv
        except OSError:
            continue
    raise SystemExit(f"no free port in {tries[0]}..{tries[-1]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8707)
    ap.add_argument("--no-open", action="store_true")
    ap.add_argument("--no-prewarm", action="store_true", help="recompute the week only when its tab asks")
    ap.add_argument("--t0", type=float, default=None, help="epoch seconds when run.sh started (time-to-first-visual)")
    a = ap.parse_args()
    STATE["t0"] = a.t0
    srv = bind(a.port)
    url = f"http://127.0.0.1:{srv.server_address[1]}/"
    ready = time.time() - (a.t0 or STATE["started"])
    print(f"[P7 demo] serving {url}  ({ready:.1f} s after start; offline; Ctrl-C to stop)", flush=True)
    if not a.no_open:
        threading.Timer(0.2, webbrowser.open, (url,)).start()
    threading.Thread(target=pool_fill, daemon=True).start()   # the judge's July 4th turn, ready before it is needed
    if not a.no_prewarm:
        threading.Thread(target=prewarm, daemon=True).start()
    try:
        srv.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print("\n[P7 demo] stopped")
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
