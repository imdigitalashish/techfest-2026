"""Tiny stdlib HTTP backend for the P10 'Break the band' demo. Serves static/index.html and JSON endpoints.

    PYTHONPATH=<project> python demo/server.py [--port 8710] [--host 127.0.0.1]

All numbers come from engine.py (committed code paths) or the committed result JSONs; posts typed in the page are
scored by scorer_worker.py (a separate process).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DEMO = Path(__file__).resolve().parent
sys.path.insert(0, str(DEMO))
T0 = float(os.environ.get("P10_T0", time.time()))


class Scorer:
    """Owns the scorer_worker.py child; warms up in the background so the page is usable before it is ready."""

    def __init__(self):
        self.status = {"ready": False, "scorer": None, "label": "warming up…", "error": None}
        self._lock = threading.Lock()
        self._id = 0
        env = {**os.environ, "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1", "P10_DEVICE": "cpu",
               "PYTHONPATH": os.pathsep.join([str(DEMO.parent), os.environ.get("PYTHONPATH", "")])}
        self.proc = subprocess.Popen([sys.executable, str(DEMO / "scorer_worker.py")], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, env=env, bufsize=1)
        threading.Thread(target=self._wait_ready, daemon=True).start()

    def _wait_ready(self):
        line = self.proc.stdout.readline()
        try:
            self.status = json.loads(line)
        except Exception:  # noqa: BLE001
            self.status = {"ready": False, "scorer": None, "label": "scorer failed to start", "error": line[:300]}
        print(f"[demo] scorer: {self.status.get('label')} (load {self.status.get('load_s')} s)"
              + (f" — {self.status['error']}" if self.status.get("error") else ""), flush=True)

    def score(self, texts: list[str]) -> dict:
        if not self.status.get("ready"):
            raise RuntimeError("scorer is still warming up")
        with self._lock:
            self._id += 1
            self.proc.stdin.write(json.dumps({"id": self._id, "texts": texts}) + "\n")
            self.proc.stdin.flush()
            out = json.loads(self.proc.stdout.readline())
        if "error" in out:
            raise RuntimeError(out["error"])
        return {**out, "label": self.status["label"]}


SCORER: Scorer | None = None
ENGINE = None
ENGINE_LOCK = threading.Lock()
META = None


def _posts(body) -> tuple[list[float], list[float]]:
    s, w = [], []
    for p in body.get("posts", []):
        c = int(p.get("copies", 1))
        if c < 0 or c > 50:
            raise ValueError("copies must be in 0..50")
        sent, tr = float(p["sentiment"]), float(p["trust"])
        if not (-1 <= sent <= 1 and 0 <= tr <= 1):
            raise ValueError("sentiment must be in [-1, 1] and trust in [0, 1]")
        s += [sent] * c
        w += [tr] * c
    return s, w


def _k(body) -> int:
    k = int(body.get("k", 3))
    if not 0 <= k <= 10:
        raise ValueError("k must be in 0..10")
    return k


def _row(body) -> int:
    if "row" in body:
        r = int(body["row"])
        if not 0 <= r < len(ENGINE.test):
            raise ValueError("row out of range")
        return r
    return ENGINE.row_of(body["ticker"], body["date"])


def handle(path: str, q: dict, body: dict):
    e = ENGINE
    if path == "/api/health":
        return {"engine_ready": e is not None, "scorer": SCORER.status if SCORER else None,
                "uptime_s": round(time.time() - T0, 2)}
    if e is None:
        raise RuntimeError("engine is still loading")
    if path == "/api/meta":
        return META
    if path == "/api/random":
        seed = int(q["seed"][0]) if "seed" in q else None
        return e.day(e.random_row(seed))
    if path == "/api/day":
        return e.day(_row(body))
    if path == "/api/trust":
        return {"trust": e.trust(float(body.get("followers", 0)), float(body.get("age_days", 1)),
                                 bool(body.get("verified", False)), int(body.get("n_cashtags", 1)))}
    if path == "/api/score":
        if SCORER is None:
            raise RuntimeError("scorer is still warming up")
        texts = [str(t)[:500] for t in body.get("texts", [])][:20]
        return SCORER.score(texts)
    with ENGINE_LOCK:
        if path == "/api/attack":
            s, w = _posts(body)
            return e.attack(_row(body), s, w, _k(body))
        if path == "/api/flips":
            return e.flips(_row(body), _k(body))
        if path == "/api/redteam":
            n = min(int(body.get("n", 2000)), 5000)
            return e.redteam(_row(body), _k(body), n, int(body.get("seed", 0)))
        if path == "/api/population":
            s, w = _posts(body)
            return e.population(s, w, _k(body))
    raise KeyError(path)


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, payload, ctype="application/json"):
        data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _dispatch(self, body):
        u = urlparse(self.path)
        if u.path in ("/", "/index.html"):
            return self._send(200, (DEMO / "static/index.html").read_bytes(), "text/html; charset=utf-8")
        if not u.path.startswith("/api/"):
            return self._send(404, {"error": "not found"})
        try:
            self._send(200, handle(u.path, parse_qs(u.query), body))
        except KeyError as ex:
            self._send(404, {"error": f"unknown: {ex}"})
        except (ValueError, TypeError) as ex:
            self._send(400, {"error": str(ex)})
        except RuntimeError as ex:
            self._send(503, {"error": str(ex)})

    def do_GET(self):
        self._dispatch({})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0) or 0)
        if n > 100_000:
            return self._send(413, {"error": "body too large"})
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"error": "bad json"})
        self._dispatch(body if isinstance(body, dict) else {})


def main():
    global SCORER, ENGINE, META
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=int(os.environ.get("P10_PORT", 8710)))
    ap.add_argument("--host", default="127.0.0.1")
    a = ap.parse_args()
    srv = ThreadingHTTPServer((a.host, a.port), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    from engine import Engine
    ENGINE = Engine()
    META = ENGINE.meta()
    SCORER = Scorer()  # started after the engine so the first visual is not slowed by the torch warm-up
    print(f"[demo] engine ready in {time.time() - T0:.1f} s (live ACI {META['aci_clean_live']['coverage']:.4%}, "
          f"committed {META['committed']['aci_cov']:.4%})", flush=True)
    print(f"[demo] READY http://{a.host}:{a.port}/", flush=True)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        if SCORER:
            SCORER.proc.terminate()
        srv.shutdown()


if __name__ == "__main__":
    main()
