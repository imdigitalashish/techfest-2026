"""P8 demo server: serves demo/web and a small JSON API for the live engine (Python stdlib http.server).

    .venv/bin/python -m demo.server [--port 8808] [--no-browser] [--local-text]

- Binds to 127.0.0.1 only. Never calls an LLM or any other network service.
- The REAL and CASCADE tabs replay demo/web/data.js (derived outcomes only); the LIVE tab calls /api/*.
- --local-text (INTERNAL VERIFICATION ONLY, off by default): reads Eedi item text from the local, gitignored
  .data/ copy at runtime and serves it to this machine's browser. It is never written to disk. Do not use it in
  front of judges, in recordings or in screenshots (Kaggle Eedi rules §7.B; CC BY-NC 4.0).
"""
from __future__ import annotations

import argparse
import json
import socket
import sys
import threading
import time
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "demo" / "web"
DATA = ROOT / ".data"
STATIC = {"/": ("index.html", "text/html; charset=utf-8"), "/index.html": ("index.html", "text/html; charset=utf-8"),
          "/data.js": ("data.js", "text/javascript; charset=utf-8")}
FAVICON = (b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><rect width="16" height="16" rx="3" fill="#16233f"/>'
           b'<path d="M4 8.5l2.5 2.5L12 5" stroke="#fff" stroke-width="2" fill="none"/></svg>')
MAX_BODY = 16_384


class State:
    mode = "no-text"
    real = None  # live.RealText when --local-text
    real_ids: list[str] = []
    real_codes: dict[str, str] = {}
    engine_calls = 0
    started = time.time()


def _tokens(body: dict):
    from demo import live

    return live.tokens_from(expr=body.get("expr"), tokens=body.get("tokens"))


def api(method: str, path: str, body: dict) -> tuple[int, dict]:
    from demo import live

    if method == "GET" and path == "/api/health":
        return 200, {"ok": True, "mode": State.mode, "local_text_available": (DATA / "eedi2024").exists(),
                     "llm_calls": 0, "engine_calls": State.engine_calls, "presets": live.PRESETS,
                     "rules": live.rule_info(), "uptime_s": round(time.time() - State.started, 1)}
    if method == "POST" and path == "/api/question":
        return 200, live.new_question(int(body.get("k", 0)))
    if method == "POST" and path == "/api/parse":
        toks = _tokens(body)
        return 200, dict(live.question(toks), rules=live.rule_table(toks))
    if method == "POST" and path == "/api/certify":
        State.engine_calls += 1
        return 200, live.certify(_tokens(body), str(body.get("answer", "")))
    if method == "POST" and path == "/api/rerun":
        n = int(body.get("n", 1000))
        State.engine_calls += n
        return 200, live.rerun(_tokens(body), str(body.get("answer", "")), n)
    if method == "POST" and path == "/api/predict":
        State.engine_calls += 1
        return 200, live.predict(_tokens(body), str(body.get("answer", "")))
    if method == "POST" and path == "/api/reveal":
        State.engine_calls += 1
        return 200, live.reveal(str(body.get("token", "")), str(body.get("answer", "")))
    if method == "POST" and path == "/api/slipstorm":
        out = live.slip_storm()
        State.engine_calls += out["slips"]
        return 200, out
    if path.startswith("/api/real"):
        if State.real is None:
            return 403, {"ok": False, "mode": State.mode,
                         "error": "Item text is not available in this mode (Kaggle Eedi rules \u00a77.B). "
                                  "Local text is for internal verification only: demo/run.sh --local-text."}
        if method == "POST" and path == "/api/real/rerun":
            out = State.real.rerun_all(int(body.get("n", 2)))
            codes = out.pop("codes")
            out["matches_export"] = sum(1 for i, c in codes.items() if State.real_codes.get(i) == c)
            return 200, out
        if method == "GET" and path.startswith("/api/real/"):
            iid = path.rsplit("/", 1)[-1]
            if iid not in State.real_codes:
                return 404, {"ok": False, "error": "not a benchmark item"}
            out = State.real.item(iid)
            out["export_engine"] = State.real_codes[iid]
            return 200, out
    return 404, {"ok": False, "error": f"no route {method} {path}"}


class Handler(BaseHTTPRequestHandler):
    server_version = "P8Demo/1"

    def log_message(self, fmt, *args):  # quiet; errors still reach stderr through send_error paths
        pass

    def _send(self, code: int, payload: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(payload)

    def _json(self, code: int, obj: dict) -> None:
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _route(self, method: str) -> None:
        path = self.path.split("?", 1)[0]
        if method == "GET" and path == "/favicon.ico":
            self._send(200, FAVICON, "image/svg+xml")
            return
        if method == "GET" and path in STATIC:
            name, ctype = STATIC[path]
            f = WEB / name
            if not f.exists():
                self._send(404, f"missing demo/web/{name}".encode(), "text/plain; charset=utf-8")
                return
            self._send(200, f.read_bytes(), ctype)
            return
        if not path.startswith("/api/"):
            self._send(404, b"not found", "text/plain; charset=utf-8")
            return
        body: dict = {}
        if method == "POST":
            n = int(self.headers.get("Content-Length") or 0)
            if n > MAX_BODY:
                self._json(413, {"ok": False, "error": "request too large"})
                return
            try:
                body = json.loads(self.rfile.read(n) or b"{}")
            except ValueError:
                self._json(400, {"ok": False, "error": "invalid JSON"})
                return
        try:
            code, out = api(method, path, body)
        except (ValueError, SyntaxError, KeyError, ZeroDivisionError) as exc:
            code, out = 400, {"ok": False, "error": str(exc) or type(exc).__name__}
        except Exception as exc:  # keep the demo up; report the error to the page
            code, out = 500, {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        self._json(code, out)

    def do_GET(self):  # noqa: N802
        self._route("GET")

    def do_POST(self):  # noqa: N802
        self._route("POST")


def free_port(start: int) -> int:
    for port in range(start, start + 30):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"no free port in {start}-{start + 29}")


def load_data() -> dict:
    txt = (WEB / "data.js").read_text(encoding="utf-8")
    prefix = "window.P8 = "
    assert txt.startswith(prefix), "demo/web/data.js is malformed: re-run python -m demo.export"
    return json.loads(txt[len(prefix):].rstrip().rstrip(";"))


def setup(local_text: bool) -> None:
    data = load_data()
    State.real_ids = [r["id"] for r in data["real"]["items"]]
    State.real_codes = {r["id"]: r["eng"] for r in data["real"]["items"]}
    if local_text:
        if not (DATA / "eedi2024" / "queries_w_rels.parquet").exists():
            raise SystemExit("--local-text needs the local Eedi copy: run `demo/run.sh --fetch` (or "
                             "`.venv/bin/python -m eval.data.fetch`) first.")
        from demo import live

        State.real = live.RealText(DATA, State.real_ids)
        State.mode = "local-text"
    from demo import live

    threading.Thread(target=live.warm, name="warm", daemon=True).start()  # first live timings are representative


def make_server(port: int, local_text: bool = False) -> ThreadingHTTPServer:
    setup(local_text)
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    srv.daemon_threads = True
    return srv


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8808)
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--local-text", action="store_true",
                    help="INTERNAL VERIFICATION ONLY: show Eedi item text from the local .data/ copy")
    a = ap.parse_args(argv)
    port = free_port(a.port)
    srv = make_server(port, a.local_text)
    url = f"http://127.0.0.1:{port}/"
    print(f"P8 demo on {url}  mode={State.mode}  (Ctrl-C to stop; no LLM is ever called)", flush=True)
    if State.mode == "local-text":
        print("LOCAL TEXT is ON: internal verification only. Do not present, record or screenshot.", flush=True)
    if not a.no_browser:
        threading.Timer(0.3, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()


if __name__ == "__main__":
    main(sys.argv[1:])
