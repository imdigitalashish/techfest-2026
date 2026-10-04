"""P1 demo server (Python stdlib only, so the committed-results page works before any venv or model exists).

  python3 demo/server.py [--port 8765] [--no-browser]

Serves demo/web/ and, only when the project venv and the cached SmolLM2-135M are present, runs the LIVE engine
(`nice -n 10 .venv/bin/python -m demo.live_engine`) as one child process (one model copy), relaying its JSON-line
events to the page over Server-Sent Events and the judge's clicks back to it on stdin. The engine itself pauses
while kern.memorystatus_level < 25 and resumes at >= 30 (and starts only at >= 30); the page shows that pause.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "demo" / "web"
LIVE_DIR = ROOT / "demo" / ".live"  # session recordings + engine log (gitignored)
VENV_PY = ROOT / ".venv" / "bin" / "python"
MODEL = "HuggingFaceTB/SmolLM2-135M"
TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
         ".css": "text/css; charset=utf-8", ".json": "application/json", ".svg": "image/svg+xml",
         ".png": "image/png", ".jsonl": "application/x-ndjson"}


def memory_level() -> int | None:
    try:
        return int(subprocess.check_output(["sysctl", "-n", "kern.memorystatus_level"], text=True,
                                           stderr=subprocess.DEVNULL).strip())
    except Exception:
        return None


def hub_dir() -> Path:
    if os.environ.get("HF_HUB_CACHE"):
        return Path(os.environ["HF_HUB_CACHE"])
    if os.environ.get("HF_HOME"):
        return Path(os.environ["HF_HOME"]) / "hub"
    return Path.home() / ".cache" / "huggingface" / "hub"


def live_check() -> tuple[bool, list[str]]:
    why = []
    if not VENV_PY.exists():
        why.append("no project venv (.venv): run demo/fetch.sh")
    snaps = hub_dir() / f"models--{MODEL.replace('/', '--')}" / "snapshots"
    if not any(snaps.glob("*/config.json")) or not any(snaps.glob("*/*.safetensors")):
        why.append(f"{MODEL} not in the local Hugging Face cache: run demo/fetch.sh")
    if not (ROOT / "eval" / "data" / "blocks_smollm2-135m_T128_N2400_E48.npz").exists():
        why.append("committed token blocks missing (eval/data/*.npz)")
    return not why, why


class Live:
    """One engine process at a time; every event is kept for late subscribers and written to a recording."""

    def __init__(self) -> None:
        self.lock = threading.Condition()
        self.proc: subprocess.Popen | None = None
        self.events: list[dict] = []
        self.run_id = 0
        self.seed = None
        self.state = "idle"
        self.rec = None

    def start(self, seed: int) -> tuple[int, dict]:
        ok, why = live_check()
        if not ok:
            return 409, {"error": "live unavailable", "why": why}
        with self.lock:
            if self.proc and self.proc.poll() is None:
                return 409, {"error": "a live run is already in progress"}
            LIVE_DIR.mkdir(exist_ok=True)
            stamp = time.strftime("%Y%m%d-%H%M%S")
            self.rec = open(LIVE_DIR / f"session-{stamp}-s{seed}.jsonl", "w")
            log = open(LIVE_DIR / "engine.log", "a")
            cmd = ["nice", "-n", "10", str(VENV_PY), "-m", "demo.live_engine", "--seed", str(seed)]
            self.proc = subprocess.Popen(cmd, cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log,
                                         text=True, bufsize=1)
            self.run_id += 1
            self.seed = seed
            self.events = [{"ev": "server_start", "run_id": self.run_id, "seed": seed, "pid": self.proc.pid,
                            "cmd": " ".join(cmd[:3] + [".venv/bin/python"] + cmd[4:])}]
            self.state = "running"
            self.lock.notify_all()
            threading.Thread(target=self._pump, args=(self.proc, self.run_id), daemon=True).start()
        return 200, {"ok": True, "run_id": self.run_id, "pid": self.proc.pid}

    def _pump(self, proc: subprocess.Popen, run_id: int) -> None:
        for line in proc.stdout:  # type: ignore[union-attr]
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            self._add(ev, run_id)
        rc = proc.wait()
        self._add({"ev": "engine_exit", "code": rc}, run_id)
        with self.lock:
            if run_id == self.run_id:
                self.state = "finished" if rc == 0 else "failed"
                if self.rec:
                    self.rec.close()
                    self.rec = None

    def _add(self, ev: dict, run_id: int) -> None:
        with self.lock:
            if run_id != self.run_id:
                return
            self.events.append(ev)
            if self.rec:
                self.rec.write(json.dumps(ev) + "\n")
                self.rec.flush()
            self.lock.notify_all()

    def command(self, cmd: dict) -> tuple[int, dict]:
        with self.lock:
            if not self.proc or self.proc.poll() is not None:
                return 409, {"error": "no live run in progress"}
            try:
                self.proc.stdin.write(json.dumps(cmd) + "\n")  # type: ignore[union-attr]
                self.proc.stdin.flush()  # type: ignore[union-attr]
            except (BrokenPipeError, OSError) as e:
                return 409, {"error": str(e)}
        return 200, {"ok": True}

    def stop(self) -> tuple[int, dict]:
        with self.lock:
            p = self.proc
        if not p or p.poll() is not None:
            return 200, {"ok": True, "note": "nothing running"}
        p.terminate()
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
        return 200, {"ok": True}

    def status(self) -> dict:
        ok, why = live_check()
        with self.lock:
            return {"live_available": ok, "why": why, "state": self.state, "run_id": self.run_id, "seed": self.seed,
                    "pid": self.proc.pid if self.proc else None, "n_events": len(self.events),
                    "memory_level": memory_level(), "time": time.strftime("%H:%M:%S")}


LIVE = Live()


class Handler(BaseHTTPRequestHandler):
    server_version = "p1demo/1"

    def log_message(self, fmt, *args) -> None:  # quiet
        pass

    def _json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return {}

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?")[0]
        if path == "/api/status":
            return self._json(200, LIVE.status())
        if path == "/api/events":
            return self._sse()
        if path in ("/", ""):
            path = "/index.html"
        f = (WEB / path.lstrip("/")).resolve()
        if WEB.resolve() not in f.parents or not f.is_file():
            self.send_error(404)
            return
        body = f.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", TYPES.get(f.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?")[0]
        body = self._body()
        if path == "/api/start":
            try:
                seed = int(body.get("seed", 0))
            except (TypeError, ValueError):
                seed = 0
            return self._json(*LIVE.start(max(0, min(4, seed))))
        if path == "/api/cmd":
            cmd = {k: body[k] for k in ("cmd", "device") if k in body}
            if cmd.get("cmd") not in ("unplug", "replug", "pause", "resume", "stop"):
                return self._json(400, {"error": "unknown command"})
            return self._json(*LIVE.command(cmd))
        if path == "/api/stop":
            return self._json(*LIVE.stop())
        self.send_error(404)

    def _sse(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        run, i = None, 0
        try:
            while True:
                with LIVE.lock:
                    if run != LIVE.run_id:
                        run, i = LIVE.run_id, 0
                    batch = LIVE.events[i:]
                    i += len(batch)
                    if not batch:
                        LIVE.lock.wait(timeout=15)
                if batch:
                    payload = "".join(f"data: {json.dumps(dict(ev, run_id=run))}\n\n" for ev in batch)
                    self.wfile.write(payload.encode())
                else:
                    self.wfile.write(b": keep-alive\n\n")
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            return


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()
    srv = None
    for port in range(a.port, a.port + 20):
        try:
            srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    if srv is None:
        sys.exit(f"no free port in {a.port}-{a.port + 19}")
    srv.daemon_threads = True
    url = f"http://127.0.0.1:{srv.server_address[1]}/"
    ok, why = live_check()
    print(f"P1 demo at {url}  (committed results ready; live panel: {'enabled' if ok else 'disabled - ' + '; '.join(why)})",
          flush=True)
    if not a.no_browser:
        threading.Timer(0.3, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        LIVE.stop()


if __name__ == "__main__":
    main()
