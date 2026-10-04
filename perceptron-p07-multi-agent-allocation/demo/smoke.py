"""Headless smoke test of the P7 demo: no browser needed. Run via demo/smoke.sh (from a fresh clone too).

Checks: committed exports present and current (evidence.js, recorded_live.js); the page needs no network; no label
outside the LIVE word list says "live" (so the recorded fallback never claims to be live); the review's wording is
in place; the server boots; the July 4th reference run fast-forwards, refuses surges, reproduces the committed
served fractions and window losses of replicate 200; the judge's turn opens armed at 21:15, takes a surge, reports
its real duration (cut at midnight) and refuses a surge after the end; the synthetic stress test opens armed at
05:00 as in phase-v2, the planner loses fewer than the rule on a fixed seed and surge, off-reference surges are
flagged, bad and after-end surges are refused; the background recomputes match the committed metrics; the fallback
screenshots are 1280x720 and the media fit the size budget. Exit code 1 if any check fails.
--quick skips the week recompute and the recording check (the slowest checks).
"""
from __future__ import annotations

import json
import re
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.request

from demo.engine import DEMO, NYC_START, P7, BatchRun, committed_row

OUT: list[tuple[str, bool, str]] = []
NYC_WIN = (1440 + 21 * 60 + 30, 1440 + 23 * 60 + 30)
NYC_END = 2880
PARITY = "matches the committed served-fraction and loss metrics"
REQUIRED = {   # review 2026-10-04 (gpt-6-astra), items 1-10: wording that must be on the page
    "index.html": ["Your turn: restart at 21:15", "not a new test seed or a calibrated prediction", "OFF-REFERENCE",
                   "The interventions and simulations were computed live; the reference distributions and confidence "
                   "intervals are committed results.", "raw TLC cell pickups, before thinning",
                   "fleet-wide losses, 21:30–23:30", "Illustrative, retrospectively chosen window: not a causal estimate",
                   "up to 6 h; this replay ends at midnight", PARITY, "daily fractions match at committed precision",
                   "LIVE COMPUTATION STOPPED.", "Retry", "Open recorded fallback"],
    "SCRIPT.md": ["Your turn: restart at 21:15", "not a new test seed or a calibrated prediction", "OFF-REFERENCE",
                  "The interventions and simulations were computed live; the reference distributions and confidence "
                  "intervals are committed results.", "4 seeds", PARITY],
    "README.md": [PARITY, "daily fractions match at committed precision"],
}
BANNED = ["seed #21", "bit-identical", "Your surge is seed"]


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


def refused(base: str, path: str, body: dict) -> tuple[int, str]:
    """POST that should be refused: (HTTP status, error message)."""
    try:
        code, r = http(base, path, body)
        return code, json.dumps(r)[:120]
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read()).get("error", "")
        except ValueError:
            return e.code, ""


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


def nyc_session(base: str, role: str) -> tuple[str, dict]:
    _, r = http(base, "/api/live/new", dict(scenario="nyc", role=role))
    sid, k, n_tl, t0, lapse = r["sid"], 0, 0, time.time(), role == "reference"
    while True:
        _, w = http(base, "/api/live/warm", {"sid": sid, "from": k, "frames": lapse})
        k, n_tl = w["next"], n_tl + len(w["frames"])
        if w.get("error") or w["done"] or time.time() - t0 > 300:
            break
        time.sleep(0.2)
    w.update(timelapse_frames=n_tl, warm_s=round(time.time() - t0, 1), first=r)
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


def live_words(text: str) -> list[str]:
    """Code lines that would show the word 'live' to a viewer, outside the LIVE word list (PROV-WORDS:LIVE),
    the API paths and the mode identifier LIVE. Comments are ignored."""
    bad = []
    for line in text.splitlines():
        if "PROV-WORDS:LIVE" in line:
            continue
        s = re.sub(r"(^|\s)//.*$", "", line)
        s = re.sub(r"/\*.*?\*/|<!--.*?-->", "", s).replace("/api/live/", "")
        s = re.sub(r"'LIVE'|\.LIVE\b|\bLIVE\s*:", "", s)
        if re.search(r"\blive\b", s, re.I):
            bad.append(line.strip()[:90])
    return bad


def png_size(path) -> tuple[int, int]:
    with open(path, "rb") as f:
        head = f.read(24)
    return struct.unpack(">II", head[16:24]) if head[:8] == b"\x89PNG\r\n\x1a\n" else (0, 0)


def main() -> None:
    quick = "--quick" in sys.argv
    t_start = time.time()
    rec = None if quick else subprocess.Popen(["nice", "-n", "10", sys.executable, "-m", "demo.record", "--check"], cwd=P7,
                                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    # ---- committed files and exports
    for f in ("index.html", "run.sh", "smoke.sh", "SCRIPT.md", "README.md", "data/evidence.js", "data/nyc_jul03-04_r200.npz",
              "data/recorded_live.js"):
        check(f"present: demo/{f}", (DEMO / f).exists())
    r = subprocess.run([sys.executable, "-m", "demo.export_evidence", "--check"], cwd=P7, capture_output=True, text=True)
    check("evidence current: evidence.js equals the committed result files", r.returncode == 0, r.stdout.strip() or r.stderr.strip()[-200:])
    # ---- offline: the page references nothing outside demo/
    for f in [DEMO / "index.html", *sorted((DEMO / "data").glob("*.js"))]:
        urls = sorted(set(re.findall(r"https?://[^\s\"'<>)]+", f.read_text())))
        check(f"no http(s) URL in {f.relative_to(P7)}", not urls, ", ".join(urls[:3]))
    html = (DEMO / "index.html").read_text()
    srcs = re.findall(r"""<(?:script|link|img|iframe)[^>]+(?:src|href)=["']([^"']+)""", html)
    check("page loads only local files", all(s.startswith("data/") or s.startswith("data:") for s in srcs), ", ".join(srcs))
    # ---- provenance: one MODE value drives every label; recorded mode never says live
    rec_line = [ln for ln in html.splitlines() if "PROV-WORDS:RECORDED" in ln]
    live_line = [ln for ln in html.splitlines() if "PROV-WORDS:LIVE" in ln]
    bad = live_words(html)
    check("provenance: 'live' appears only in the LIVE word list (index.html)", len(live_line) == 1 and not bad, "; ".join(bad[:3]))
    check("recorded mode has no 'live' label (RECORDED word list, recorded_live.js)",
          len(rec_line) == 1 and not re.search(r"\blive\b", rec_line[0], re.I)
          and not re.search(r"\blive\b", (DEMO / "data/recorded_live.js").read_text(), re.I))
    # ---- the review's wording
    miss = [f"{f}: {w[:40]}" for f, ws in REQUIRED.items() for w in ws if w not in (DEMO / f).read_text()]
    check("review wording present (handover, intervention vs reference, closing line, anomaly, parity scope)", not miss, "; ".join(miss[:3]))
    found = [f"{p.name}: {b}" for p in [DEMO / "index.html", DEMO / "SCRIPT.md", DEMO / "README.md"] for b in BANNED
             if b in p.read_text()]
    check("retired wording absent ('seed #21', 'bit-identical')", not found, "; ".join(found))
    # ---- the observed-surge box sits on the top committed July 4 surge (research note; find_surges when data exist)
    note = (P7 / "research/components/real-trace-replay.md").read_text()
    m = re.search(r"\|\s*1\s*\|\s*(\d+)\s*\|\s*(2025-07-04 \d\d:\d\d–\d\d:\d\d)\s*\|", note)
    ev = json.loads((DEMO / "data/evidence.js").read_text().split("=", 1)[1].rstrip().rstrip(";"))["claims"]["nyc_surge"]
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
    # ---- server
    proc = subprocess.Popen([sys.executable, "-m", "demo.server", "--port", "0", "--no-open"], cwd=P7,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
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

        # ---- July 4th: the unperturbed reference run, as the page opens it (armed; the judge presses play)
        sid, w = nyc_session(base, "reference")
        check("July 4th reference: first picture at once, then fast-forward to 21:15 on 4 July",
              w["first"].get("snapshot", {}).get("t") == 0 and w["done"] and not w.get("error") and w["snapshot"]["t"] == NYC_START,
              f"{w['timelapse_frames']} time-lapse frames in {w['warm_s']} s")
        code, msg = refused(base, "/api/live/shock", dict(sid=sid, zone=7, size=1))
        check("July 4th reference: refuses a surge (it stays unperturbed)", code == 400, f"HTTP {code}: {msg}")
        frames, stats = step_until(base, sid, NYC_END, NYC_START)
        check("July 4th reference: frames sane (2 fleets x 40 units, 25 cells)", frames and sane(frames), f"{len(frames)} frames")
        check("July 4th reference: every request served, lost or waiting", conserved(stats, frames[-1]))
        win = [sum(sum(f["panels"][i]["lost"]) for f in frames if NYC_WIN[0] <= f["t"] < NYC_WIN[1]) for i in (0, 1)]
        rows = [committed_row("nyc-v2", p, 200) for p in ("reactive", "mpc-ewma")]
        com = [int(float(row["event_lost"])) for row in rows]
        frac = [p["served"] / p["arrivals"] for p in stats["panels"]]
        same = all(abs(f - float(row["served_frac"])) <= 1e-12 for f, row in zip(frac, rows))
        check(f"July 4th reference {PARITY} (eval/results/nyc-v2/episodes.csv, replicate 200)",
              win == com and same and stats["done"], f"window lost {win} vs {com}; served {[round(f, 6) for f in frac]}")

        # ---- July 4th: the judge's turn (a separate interactive run from the pre-warmed pool)
        sid2, w2 = nyc_session(base, "interactive")
        check("July 4th 'Your turn': opens armed at 21:15 (no time-lapse)",
              w2["done"] and not w2.get("error") and w2["snapshot"]["t"] == NYC_START and w2["timelapse_frames"] == 0,
              f"ready in {w2['warm_s']} s")
        frames, _ = step_until(base, sid2, NYC_START + 5, NYC_START)
        _, sh = http(base, "/api/live/shock", dict(sid=sid2, zone=7, size=1))
        s = sh["shock"]
        check("July 4th 'Your turn': surge returns its real start, end and duration (cut at midnight)",
              s["t0"] == NYC_START + 5 and s["end"] == NYC_END and s["minutes"] == NYC_END - s["t0"] and s["full_minutes"] == 360
              and s["truncated"] and s["ref"]["status"] == "none", f"cells {s['zones']}, {s['minutes']} of {s['full_minutes']} min")
        frames, stats = step_until(base, sid2, NYC_START + 65, NYC_START + 5)
        check("July 4th 'Your turn': the surge is simulated", stats["shocks"] and stats["shocks"][0]["steps"] == 60 and sane(frames),
              f"lost in its first hour (reactive, planner) = {stats['shocks'][0]['lost']}")
        step_until(base, sid2, NYC_END, NYC_START + 65)
        code, msg = refused(base, "/api/live/shock", dict(sid=sid2, zone=7, size=1))
        check("July 4th 'Your turn': a surge after the end is refused", code == 400 and "ended" in msg, f"HTTP {code}: {msg}")

        # ---- stress test (synthetic): fixed seed and surge, armed at 05:00 as in phase-v2
        _, r = http(base, "/api/live/new", dict(scenario="synthetic", L=1, P=10, seed=7000))
        sid3, cfg = r["sid"], r["config"]
        ref = cfg.get("reference") or {}
        check("stress test: opens armed at 05:00, 12-h run, phase-v2 reference (onsets 04:12-06:36)",
              r["snapshot"]["t"] == 300 and cfg["horizon"] == 720 and ref.get("run") == "phase-v2" and ref.get("onset") == [252, 396],
              f"t {r['snapshot']['t']}, horizon {cfg['horizon']}, reference {ref.get('run')} {ref.get('onset')}")
        _, sh = http(base, "/api/live/shock", dict(sid=sid3, zone=12, size=1))
        frames, stats = step_until(base, sid3, 300 + 120, 300)
        lost = stats["shocks"][0]["lost"]
        check("stress test: frames sane, same requests in both cities (CRN asserted server-side)", sane(frames))
        check("stress test: every request served, lost or waiting", conserved(stats, frames[-1]))
        check("stress test: planner loses fewer than the rule (seed 7000, L=1, P=10, x1 surge on zone 12 at 05:00)",
              stats["shocks"][0]["complete"] and lost[1] < lost[0], f"120-min window lost (reactive, planner) = {lost}")
        check("stress test: that surge is IN-REFERENCE, 6 h, not truncated",
              sh["shock"]["ref"]["status"] == "in" and sh["shock"]["minutes"] == 360 and not sh["shock"]["truncated"])
        _, sh2 = http(base, "/api/live/shock", dict(sid=sid3, zone=0, size=1))
        _, st = http(base, "/api/live/step", dict(sid=sid3, n=0))
        flags = [x["ref"] for x in st["stats"]["shocks"]]
        check("stress test: a second surge while the first is still on is flagged OFF-REFERENCE (the first keeps its window)",
              [f["status"] for f in flags] == ["in", "off"] and "overlaps" in " ".join(flags[1]["reasons"]))
        code, msg = refused(base, "/api/live/shock", dict(sid=sid3, zone=0, size=3))
        check("stress test: a surge size outside x0.5/x1/x2 is refused", code == 400, f"HTTP {code}: {msg}")
        _, r = http(base, "/api/live/new", dict(scenario="synthetic", L=1, P=10, seed=7001))
        sid4 = r["sid"]
        step_until(base, sid4, 400, 300)
        _, sh = http(base, "/api/live/shock", dict(sid=sid4, zone=12, size=2))
        why = " ".join(sh["shock"]["ref"]["reasons"])
        check("stress test: onset outside the reference window and size x2 are flagged OFF-REFERENCE",
              sh["shock"]["ref"]["status"] == "off" and "onset 06:40" in why and "size" in why, why)
        step_until(base, sid4, 401, 400)
        http(base, "/api/live/shock", dict(sid=sid4, zone=0, size=1))
        _, st = http(base, "/api/live/step", dict(sid=sid4, n=0))
        check("stress test: a later surge inside a surge's 120-min window flags that surge as overlapping",
              "overlaps" in " ".join(st["stats"]["shocks"][0]["ref"]["reasons"]))
        step_until(base, sid4, 720, 401)
        code, msg = refused(base, "/api/live/shock", dict(sid=sid4, zone=12, size=1))
        check("stress test: a surge after the end of the run is refused (no zero-length surges)", code == 400 and "ended" in msg,
              f"HTTP {code}: {msg}")

        # ---- background recomputes vs committed rows
        s = poll_run(base, "nyc", 300)
        check(f"NYC recompute {PARITY} (eval/results/nyc-v2/episodes.csv, replicate 200, 4 allocators)",
              s and s.get("parity_all"), "" if not s else s.get("error") or f"{s['wall_s']} s")
        if not quick:
            s = poll_run(base, "week", 900)
            check(f"week recompute {PARITY}; daily fractions at committed precision (long-week-v2, seed 200)",
                  s and s.get("parity_all"), "" if not s else s.get("error") or f"{s['wall_s']} s")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
    b = BatchRun("shock-day")
    b.run()
    check(f"shock-day recompute {PARITY} (eval/results/mvp-v2/episodes.csv, seed 200)", b.summary and b.summary["parity_all"])
    # ---- fallback media
    fb = [p for p in (DEMO / "fallback").glob("*") if p.is_file()]
    pngs = [p for p in fb if p.suffix == ".png"]
    total = sum(p.stat().st_size for p in fb)
    check("fallback/ has screenshots and a video", pngs and any(p.suffix in (".mp4", ".gif") for p in fb), f"{len(fb)} files")
    wrong = [f"{p.name} {png_size(p)}" for p in pngs if png_size(p) != (1280, 720)]
    check("fallback screenshots are 1280x720", pngs and not wrong, "; ".join(wrong[:3]))
    check("fallback/ total < 15 MB, every file < 10 MB", total < 15e6 and all(p.stat().st_size < 10e6 for p in fb), f"{total / 1e6:.1f} MB")
    if rec:
        out = rec.communicate()[0].strip()
        check("recorded_live.js reproduces from committed code (demo/record.py --check)", rec.returncode == 0, out[-200:])
    bad = [n for n, ok, _ in OUT if not ok]
    print(f"\n{len(OUT) - len(bad)}/{len(OUT)} checks passed in {time.time() - t_start:.0f} s" + (f"; FAILED: {bad}" if bad else ""))
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
