"""Headless smoke test of the P7 demo: no browser needed. Run via demo/smoke.sh (from a fresh clone too).

Checks: committed exports present and current; the page needs no network; the server boots; the July 4th tab
(live NYC session) fast-forwards, steps, reproduces the committed window losses for replicate 200 and accepts a
click-surge; the synthetic stress test returns sane frames and the planner loses fewer requests than the rule on a
fixed seed and surge; the background recomputes match the committed rows; the fallback media fit the size budget.
Exit code 1 if any check fails.  --quick skips the week recompute (the slowest check).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from demo.engine import DEMO, NYC_START, P7, BatchRun, committed_row

OUT: list[tuple[str, bool, str]] = []
NYC_WIN = (1440 + 21 * 60 + 30, 1440 + 23 * 60 + 30)


def check(name: str, ok, detail: str = "") -> bool:
    OUT.append((name, bool(ok), detail))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""), flush=True)
    return bool(ok)


def http(base: str, path: str, body: dict | None = None, timeout: float = 120):
    req = urllib.request.Request(base + path, data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"}, method="GET" if body is None else "POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        return r.status, (json.loads(raw) if r.headers.get("Content-Type", "").startswith("application/json") else raw.decode())


def sane(frames: list[dict]) -> bool:
    return all(len(f["arr"]) == 25 and len(f["panels"]) == 2 and all(len(p["zone"]) == 40 and len(p["q"]) == 25 for p in f["panels"])
               for f in frames)


def conserved(stats: dict, last: dict) -> bool:
    """Every request so far is served, lost or still waiting, in each panel."""
    return all(p["served"] + p["lost"] + sum(q["q"]) == p["arrivals"] for p, q in zip(stats["panels"], last["panels"]))


def step_until(base: str, sid: str, t_end: int, t_now: int) -> tuple[list, dict]:
    frames, stats = [], None
    while t_now < t_end:
        _, r = http(base, "/api/live/step", dict(sid=sid, n=min(64, t_end - t_now)))
        frames += r["frames"]
        stats = r["stats"]
        t_now = stats["t"]
        if stats["done"]:
            break
    return frames, stats


def nyc_session(base: str) -> tuple[str, dict]:
    _, r = http(base, "/api/live/new", dict(scenario="nyc"))
    sid, k, n_tl, t0 = r["sid"], 0, 0, time.time()
    while True:
        _, w = http(base, "/api/live/warm", dict(sid=sid, **{"from": k}))
        k, n_tl = w["next"], n_tl + len(w["frames"])
        if w.get("error") or w["done"] or time.time() - t0 > 300:
            break
        time.sleep(0.3)
    w["timelapse_frames"], w["warm_s"] = n_tl, round(time.time() - t0, 1)
    return sid, w


def poll_run(base: str, kind: str, timeout: float) -> dict | None:
    http(base, "/api/run", dict(kind=kind, seed=200))
    t0 = time.time()
    while time.time() - t0 < timeout:
        _, r = http(base, f"/api/run/{kind}-200?from=1000000")
        if r.get("error"):
            return dict(error=r["error"])
        if r.get("summary"):
            return r["summary"]
        time.sleep(1.0)
    return None


def main() -> None:
    quick = "--quick" in sys.argv
    t_start = time.time()
    # ---- committed files and exports
    for f in ("index.html", "run.sh", "smoke.sh", "SCRIPT.md", "README.md", "data/evidence.js", "data/nyc_jul03-04_r200.npz",
              "data/recorded_live.js"):
        check(f"present: demo/{f}", (DEMO / f).exists())
    for mod, what in (("demo.export_evidence", "evidence.js equals the committed result files"),
                      ("demo.record", "recorded_live.js reproduces from committed code")):
        r = subprocess.run([sys.executable, "-m", mod, "--check"], cwd=P7, capture_output=True, text=True)
        check(what, r.returncode == 0, r.stdout.strip() or r.stderr.strip()[-200:])
    # ---- offline: the page references nothing outside demo/
    for f in [DEMO / "index.html", *sorted((DEMO / "data").glob("*.js"))]:
        urls = sorted(set(re.findall(r"https?://[^\s\"'<>)]+", f.read_text())))
        check(f"no http(s) URL in {f.relative_to(P7)}", not urls, ", ".join(urls[:3]))
    # ---- the observed-surge box sits on the top committed July 4 surge (research note; find_surges when data exist)
    note = (P7 / "research/components/real-trace-replay.md").read_text()
    m = re.search(r"\|\s*1\s*\|\s*(\d+)\s*\|\s*(2025-07-04 \d\d:\d\d–\d\d:\d\d)\s*\|", note)
    ev = json.loads((DEMO / "data/evidence.js").read_text().split("=", 1)[1].rstrip().rstrip(";"))["claims"]["nyc_surge"]
    html = (DEMO / "index.html").read_text()
    check("observed-surge box = top committed July 4 surge (research/components/real-trace-replay.md rank 1)",
          m and ev["cell"] == m.group(1) == "3" and ev["window"] == m.group(2) and "EV.claims.nyc_surge.cell" in html
          and "EV.claims.nyc_surge.window" in html, f"cell {ev['cell']}, {ev['window']}, ratio {ev['ratio']}")
    try:
        from components.scenarios.nyc_tlc import PARQUET, find_surges
        if PARQUET.exists():
            top = find_surges("2025-07-04", train_days=["2025-07-01", "2025-07-02"])[0]
            check("find_surges (raw TLC data) agrees: top surge cell 3", top["cell"] == 3, f"{top}")
        else:
            print("SKIP  find_surges cross-check (no .data/nyc_tlc; the committed research note is the source)")
    except ImportError as e:
        print(f"SKIP  find_surges cross-check ({e})")
    srcs = re.findall(r"""<(?:script|link|img|iframe)[^>]+(?:src|href)=["']([^"']+)""", (DEMO / "index.html").read_text())
    check("page loads only local files", all(s.startswith("data/") or s.startswith("data:") for s in srcs), ", ".join(srcs))
    # ---- server
    proc = subprocess.Popen([sys.executable, "-m", "demo.server", "--port", "0", "--no-open"], cwd=P7,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    base = None
    t0 = time.time()
    try:
        line = proc.stdout.readline()
        m = re.search(r"serving (http://127\.0\.0\.1:\d+)/", line)
        base = m.group(1) if m else None
        check("server boots (127.0.0.1 only)", base, f"{time.time() - t0:.1f} s; {line.strip()}")
        if not base:
            return
        code, page = http(base, "/")
        check("GET / serves the page", code == 200 and "<canvas" in page and "July 4th (real trips)" in page)
        _, h = http(base, "/api/health")
        check("GET /api/health", h.get("ok"), f"python {h.get('python')}, highspy {h.get('highspy')}")

        # ---- July 4th tab: live NYC session, as the page opens it
        sid, w = nyc_session(base)
        check("July 4th: fast-forward to 21:15 on 4 July (computed live)", w["done"] and not w.get("error") and w["snapshot"]["t"] == NYC_START,
              f"{w['timelapse_frames']} time-lapse frames in {w['warm_s']} s")
        frames, stats = step_until(base, sid, 2880, NYC_START)
        check("July 4th: live frames sane (2 fleets x 40 units, 25 cells)", frames and sane(frames), f"{len(frames)} frames")
        check("July 4th: every request served, lost or waiting", conserved(stats, frames[-1]))
        win = [sum(sum(f["panels"][i]["lost"]) for f in frames if NYC_WIN[0] <= f["t"] < NYC_WIN[1]) for i in (0, 1)]
        com = [int(float(committed_row("nyc-v2", p, 200)["event_lost"])) for p in ("reactive", "mpc-ewma")]
        check("July 4th: live window losses = committed row for replicate 200 (reactive, planner)", win == com, f"live {win}, committed {com}")
        sid2, w2 = nyc_session(base)
        frames, _ = step_until(base, sid2, NYC_START + 5, NYC_START)
        _, sh = http(base, "/api/live/shock", dict(sid=sid2, zone=7, size=1))
        frames, stats = step_until(base, sid2, NYC_START + 65, NYC_START + 5)
        ok = sh["shock"]["t0"] == NYC_START + 5 and stats["shocks"] and stats["shocks"][0]["steps"] == 60 and sane(frames)
        check("July 4th: a click-surge on real demand is accepted and simulated", ok,
              f"cells {sh['shock']['zones']}, lost in its first hour (reactive, planner) = {stats['shocks'][0]['lost']}")

        # ---- stress test (synthetic): fixed seed and surge
        _, r = http(base, "/api/live/new", dict(scenario="synthetic", L=1, P=10, seed=7000))
        sid3, t = r["sid"], r["snapshot"]["t"]
        frames, stats = step_until(base, sid3, 300, t)
        _, sh = http(base, "/api/live/shock", dict(sid=sid3, zone=12, size=1))
        frames2, stats = step_until(base, sid3, 300 + 120, 300)
        lost = stats["shocks"][0]["lost"]
        check("stress test: frames sane, same requests in both cities (CRN asserted server-side)", sane(frames + frames2))
        check("stress test: every request served, lost or waiting", conserved(stats, frames2[-1]))
        check("stress test: planner loses fewer than the rule (seed 7000, L=1, P=10, x1 surge on zone 12 at 05:00)",
              stats["shocks"][0]["complete"] and lost[1] < lost[0], f"120-min window lost (reactive, planner) = {lost}")

        # ---- background recomputes vs committed rows
        s = poll_run(base, "nyc", 300)
        check("NYC recompute bit-identical to eval/results/nyc-v2/episodes.csv (replicate 200, 4 allocators)",
              s and s.get("parity_all"), "" if not s else s.get("error") or f"{s['wall_s']} s")
        if not quick:
            s = poll_run(base, "week", 900)
            check("week recompute bit-identical to eval/results/long-week-v2/episodes.csv (seed 200, 3 allocators)",
                  s and s.get("parity_all"), "" if not s else s.get("error") or f"{s['wall_s']} s")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
    b = BatchRun("shock-day")
    b.run()
    check("shock-day recompute bit-identical to eval/results/mvp-v2/episodes.csv (seed 200)", b.summary and b.summary["parity_all"])
    # ---- fallback media
    fb = [p for p in (DEMO / "fallback").glob("*") if p.is_file()]
    total = sum(p.stat().st_size for p in fb)
    check("fallback/ has screenshots and a video", any(p.suffix == ".png" for p in fb) and any(p.suffix in (".mp4", ".gif") for p in fb),
          f"{len(fb)} files")
    check("fallback/ total < 15 MB, every file < 10 MB", total < 15e6 and all(p.stat().st_size < 10e6 for p in fb), f"{total / 1e6:.1f} MB")
    bad = [n for n, ok, _ in OUT if not ok]
    print(f"\n{len(OUT) - len(bad)}/{len(OUT)} checks passed in {time.time() - t_start:.0f} s" + (f"; FAILED: {bad}" if bad else ""))
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
