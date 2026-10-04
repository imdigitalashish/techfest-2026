"""P9 demo server: stdlib HTTP + the committed guard code (CPU only, offline, no model, no API).

  PYTHONPATH=perceptron-p09-agent-guardrail python perceptron-p09-agent-guardrail/demo/server.py --port 8790

GET  /                         the single-file page (static/index.html)
GET  /api/bundle               the committed bundle (demo/data/bundle.json.gz, sent gzip-encoded)
GET  /api/health               readiness, bundle hash, python
GET  /api/sweep?config=C       LIVE Tier 0 (C in none|schema|t0_v0|t0_strict|t0_balanced|t0_lenient) on the 300 real
                               calls, with the count of decisions identical to the committed result file;
                               C in cascade_aoai|cascade_fast|llm_judge_aoai|llm_judge -> REPLAYED committed rows
GET  /api/item?id=I&config=C   LIVE full check list (passes included, with evidence) for one real call
     [&variant=gt]             ... or for the closest ground-truth write of the same tool, through the same checks
All inputs are validated: malformed JSON, non-object bodies, wrong field types, unknown configs and tickets over
2,000 characters get HTTP 400 (nothing is silently truncated or run under a different config).
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
from demo.engine import CONFIGS_HIJACK, CONFIGS_ITEM, CONFIGS_LIVE, CONFIGS_REPLAYED, MAX_TICKET, engine, gt_args  # noqa: E402

T0 = float(os.environ.get("P9_T0", time.time()))
MAX_BODY = 16_000


class BadRequest(ValueError):
    pass


def field(b: dict, name: str, kind, default=None, required: bool = False, max_len: int | None = None):
    """Typed field from a JSON object body: absent -> default (or 400 if required); wrong type / too long -> 400."""
    if name not in b:
        if required:
            raise BadRequest(f"missing field {name!r}")
        return default
    v = b[name]
    if not isinstance(v, kind) or isinstance(v, bool) and kind is not bool:
        raise BadRequest(f"field {name!r} must be {getattr(kind, '__name__', kind)}")
    if max_len is not None and len(v) > max_len:
        raise BadRequest(f"field {name!r} is longer than {max_len} characters ({len(v)}); nothing was truncated or run")
    return v


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
        if n > MAX_BODY:
            raise BadRequest(f"request body over {MAX_BODY} bytes")
        try:
            b = json.loads(self.rfile.read(n) or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise BadRequest(f"malformed JSON: {e}") from None
        if not isinstance(b, dict):
            raise BadRequest("request body must be a JSON object")
        return b

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
                if c not in CONFIGS_ITEM:
                    raise BadRequest(f"config must be one of {CONFIGS_ITEM}")
                if q.get("variant") == "gt":  # the closest ground-truth write of the same tool, through the same checks
                    g = gt_args(it)
                    if g is None:
                        return self.json({"error": "no ground-truth write of this tool"}, 404)
                    return self.json({**E.checks(c, it, args=g), "args": g})
                return self.json(E.checks(c, it))
            if u.path == "/api/desk":
                return self.json(E.desk_script())
            return self.json({"error": "not found"}, 404)
        except (BadRequest, ValueError) as e:
            return self.json({"error": str(e)}, 400)
        except Exception as e:  # never kill the demo on a bad request
            traceback.print_exc()
            return self.json({"error": f"{type(e).__name__}: {e}"}, 500)

    def do_POST(self):
        u = urlparse(self.path)
        try:
            E = engine()
            b = self.body()
            if u.path == "/api/hijack":
                sc = field(b, "scenario", str, required=True)
                if sc not in E.scen:
                    raise BadRequest(f"unknown scenario {sc!r}")
                cfg = field(b, "config", str, default="t0_balanced")
                if cfg not in CONFIGS_HIJACK:
                    raise BadRequest(f"config must be one of {CONFIGS_HIJACK}")
                return self.json(E.hijack(sc, field(b, "ticket", str, required=True, max_len=MAX_TICKET), cfg))
            if u.path == "/api/desk_custom":
                args = field(b, "args", dict, required=True)
                for k in ("quantity", "limit_price"):
                    if k in args and (isinstance(args[k], bool) or not isinstance(args[k], (int, float))):
                        raise BadRequest(f"args.{k} must be a number")
                for k in ("account_id", "symbol", "side", "order_type"):
                    if k in args and not isinstance(args[k], str):
                        raise BadRequest(f"args.{k} must be a string")
                return self.json(E.desk_custom(field(b, "user_request", str, required=True, max_len=500), dict(args),
                                               field(b, "inbox", str, default="", max_len=1000)))
            return self.json({"error": "not found"}, 404)
        except (BadRequest, ValueError) as e:
            return self.json({"error": str(e)}, 400)
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
