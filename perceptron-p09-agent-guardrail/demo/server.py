"""P9 demo server: stdlib HTTP + the committed guard code (CPU only, offline, no model, no API).

  PYTHONPATH=perceptron-p09-agent-guardrail python perceptron-p09-agent-guardrail/demo/server.py --port 8790

GET  /                         the single-file page (static/index.html)
GET  /api/bundle               the committed bundle (demo/data/bundle.json.gz, sent gzip-encoded)
GET  /api/health               readiness, bundle hash, python
GET  /api/sweep?config=C       LIVE Tier 0 (C in none|schema|t0_v0|t0_strict|t0_balanced|t0_lenient) on the 300 real
                               calls, with the count of decisions identical to the committed result file;
                               C in cascade_aoai|cascade_fast|llm_judge_aoai|llm_judge -> REPLAYED committed rows
GET  /api/item?id=I&config=C   LIVE full check list (passes included, with evidence) for one real call
POST /api/hijack               {scenario, ticket, config} -> SCRIPTED agent + LIVE retail guard (ticket = untrusted)
GET  /api/desk                 LIVE run of eval/demo_mvp.py (SYNTHETIC desk), parsed into cards
POST /api/desk_custom          {user_request, args, inbox} -> LIVE desk guard on a free-form call
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DEMO = Path(__file__).resolve().parent
sys.path.insert(0, str(DEMO.parent))
from demo.engine import CONFIGS_LIVE, CONFIGS_REPLAYED, engine  # noqa: E402

T0 = float(os.environ.get("P9_T0", time.time()))


class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *a):  # quiet
        pass

    def send(self, code: int, body: bytes, ctype: str, extra: dict | None = None) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def json(self, obj, code: int = 200) -> None:
        self.send(code, json.dumps(obj).encode(), "application/json")

    def body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            E = engine()
            if u.path in ("/", "/index.html"):
                return self.send(200, (DEMO / "static" / "index.html").read_bytes(), "text/html; charset=utf-8")
            if u.path.startswith("/static/") and ".." not in u.path:
                f = DEMO / u.path.lstrip("/")
                if f.is_file():
                    ctype = {".html": "text/html; charset=utf-8", ".png": "image/png", ".js": "text/javascript", ".css": "text/css"}.get(f.suffix, "application/octet-stream")
                    return self.send(200, f.read_bytes(), ctype)
            if u.path.startswith("/fallback/") and ".." not in u.path:
                f = DEMO / u.path.lstrip("/")
                if f.is_file():
                    return self.send(200, f.read_bytes(), "image/png" if f.suffix == ".png" else "text/plain; charset=utf-8")
            if u.path == "/api/bundle":
                return self.send(200, E.bundle_gz, "application/json", {"Content-Encoding": "gzip"})
            if u.path == "/api/health":
                return self.json({"ready": True, "bundle_sha256_12": E.bundle_sha, "python": sys.version.split()[0],
                                  "uptime_s": round(time.time() - T0, 1), "items": len(E.items)})
            if u.path == "/api/sweep":
                c = q.get("config", "t0_balanced")
                if c in CONFIGS_LIVE:
                    return self.json(E.sweep(c))
                if c in CONFIGS_REPLAYED:
                    return self.json(E.replayed(c))
                return self.json({"error": f"unknown config {c}"}, 400)
            if u.path == "/api/item":
                it = E.by_id.get(q.get("id", ""))
                if it is None:
                    return self.json({"error": "unknown item"}, 404)
                c = q.get("config", "t0_strict")
                c = c if c.startswith("t0_") else "t0_balanced"
                return self.json(E.checks(c, it))
            if u.path == "/api/desk":
                return self.json(E.desk_script())
            return self.json({"error": "not found"}, 404)
        except Exception as e:  # never kill the demo on a bad request
            traceback.print_exc()
            return self.json({"error": f"{type(e).__name__}: {e}"}, 500)

    def do_POST(self):
        u = urlparse(self.path)
        try:
            E = engine()
            b = self.body()
            if u.path == "/api/hijack":
                if b.get("scenario") not in E.scen:
                    return self.json({"error": "unknown scenario"}, 400)
                return self.json(E.hijack(b["scenario"], str(b.get("ticket", ""))[:2000], b.get("config", "t0_balanced")))
            if u.path == "/api/desk_custom":
                return self.json(E.desk_custom(str(b.get("user_request", ""))[:500], dict(b.get("args") or {}), str(b.get("inbox", ""))[:1000]))
            return self.json({"error": "not found"}, 404)
        except Exception as e:
            traceback.print_exc()
            return self.json({"error": f"{type(e).__name__}: {e}"}, 500)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8790)
    a = ap.parse_args()
    t = time.time()
    E = engine()
    s = E.sweep("t0_strict")  # warm-up + self-check before serving
    print(f"[demo] bundle {E.bundle_sha} loaded; live t0_strict == committed on {s['matches_committed']}/{s['n']} calls "
          f"({time.time() - t:.1f} s)", flush=True)
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), H)
    print(f"[demo] serving http://127.0.0.1:{a.port}/", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
