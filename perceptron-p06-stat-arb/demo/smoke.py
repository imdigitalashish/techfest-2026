"""Headless smoke test for the P6 demo (PLAYBOOK §11). Exit code 0 = every assertion passed.

    demo/smoke.sh            (or: .venv/bin/python -m demo.smoke, from perceptron-p06-stat-arb/)

1. Static: the page references only local files; asset integrity (md5 vs provenance); size budget; counts.
2. Committed numbers: at δ = 1/5/20 ms the exported day-scope grid, summed over the 6 registered cells, equals the
   committed 2026-10-01 totals (V0: falsification_walkforward_12d_prereg.json; V1: sensitivity_amendment1.json).
3. Backend: start demo/server.py and check:
   - time to first page and to Numba-ready are each ≤ 60 s;
   - live recompute equals the exported grid at sample configs;
   - compiled LEV equals sklearn;
   - the race endpoint at a grid reaction time equals the grid;
   - the flattened models equal lev_*.npz.
4. Browser (demo/browser_check.py, headless Chrome; skipped if none is installed): race setup, race length within the
   presenter deadline, and honest labels after the backend is killed.
5. Copy guard: wording withdrawn after the demo review must not come back; the talk track stays ≤ 350 spoken words.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import pickle
import re
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # perceptron-p06-stat-arb/
DEMO = os.path.join(ROOT, "demo")
A = os.path.join(DEMO, "assets")
RESULTS: list[tuple[str, bool, str]] = []


def ok(name: str, cond: bool, detail: str = "") -> bool:
    RESULTS.append((name, bool(cond), detail))
    print(f"{'PASS' if cond else 'FAIL'}  {name}  {detail}", flush=True)
    return bool(cond)


def md5(path: str) -> str:
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def load_data() -> dict:
    raw = open(os.path.join(A, "data.js")).read().strip()
    return json.loads(raw[len("window.P6_DATA="):-1])


def pyg_key(sim: str, fee: float, d: float, D_us: float) -> str:
    return f"{sim}|f{fee:g}|d{d:g}|D{D_us:g}"


def static_checks(P: dict) -> None:
    urls = []
    for f in ("index.html", "app.js", "style.css"):
        urls += [(f, u) for u in re.findall(r"https?://[^\s\"'`)<>]+", open(os.path.join(DEMO, f)).read())]
    bad = [u for u in urls if not u[1].startswith("http://127.0.0.1")]
    ok("page references only local files (no CDN, no remote URLs)", not bad, str(bad[:3]) if bad else f"{len(urls)} URL(s), all 127.0.0.1")
    html = open(os.path.join(DEMO, "index.html")).read()
    srcs = re.findall(r'(?:src|href)="([^"]+)"', html)
    missing = [s for s in srcs if not s.startswith("data:") and not os.path.exists(os.path.join(DEMO, s))]
    ok("every src/href in index.html exists locally", not missing, str(srcs))
    prov = json.load(open(os.path.join(A, "provenance.json")))
    bad_md5 = [f for f, v in prov["outputs"].items() if md5(os.path.join(A, f)) != v["md5"]]
    ok("assets match provenance md5", not bad_md5, f"{len(prov['outputs'])} files; built at {prov['built_at_ist']}")
    blob = lambda f: subprocess.run(["git", "hash-object", f], cwd=ROOT, capture_output=True, text=True).stdout.strip()  # noqa: E731
    stale = [f for f, h in prov.get("source_blobs", {}).items() if blob(f) != h]
    ok("assets were built by the current code (git blob of builder + components)", bool(prov.get("source_blobs")) and not stale,
       f"{len(prov.get('source_blobs', {}))} source files" + (f"; changed since build: {stale}" if stale else ""))
    total = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(DEMO) for f in fs if "__pycache__" not in dp)
    big = [f for dp, _, fs in os.walk(DEMO) for f in fs if os.path.getsize(os.path.join(dp, f)) > 20e6]
    ok("demo/ size ≤ 10.5 MB and no file > 20 MB", total <= 10.5e6 and not big, f"{total / 1e6:.2f} MB")
    banned = {"bounded to": "D06", "floors": "D07", "latency floor": "D07", "(India) →": "D07", "12-month": "D05", "measured now": "D04",
              "trades nothing": "D09", "LIVE (warming)": "D04"}
    hits = [f"{w!r} in {f} ({banned[w]})" for f in ("app.js", "index.html", "SCRIPT.md", "fallback/README.md")
            for w in banned if os.path.exists(os.path.join(DEMO, f)) and w in open(os.path.join(DEMO, f)).read()]
    ok("copy guard: wording withdrawn after the demo review is absent", not hits, "; ".join(hits) if hits else f"{len(banned)} phrases")
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in open(os.path.join(DEMO, "SCRIPT.md")).read().splitlines()
            if re.match(r"^\| \d:\d\d", l)]
    spoken = sum(len(c[2].split()) for c in rows if c[2] != "—")
    ok("talk track fits 3:00: spoken words ≤ 350 and the last row ends at 3:00 (D11)",
       bool(rows) and spoken <= 350 and rows[-1][0].endswith("3:00"), f"{spoken} spoken words in {len(rows)} timed rows (≈ {spoken / 3:.0f} s at 180 wpm)")
    m = P["meta"]
    ok("episode count matches meta and provenance", len(P["episodes"]["t_us"]) == m["window_episodes"] == prov["window"]["episodes"],
       f"{m['window_episodes']} episodes in the window")
    ok("candidate counts match meta", all(len(P["cands"][f]["opp_id"]) == m["window_candidates"][f] for f in P["cands"]), str(m["window_candidates"]))
    ok("build reproduction checks all passed", all(c["ok"] is not False for c in P["checks"]) and sum(c["ok"] is True for c in P["checks"]) >= 10,
       f"{sum(c['ok'] is True for c in P['checks'])}/{len(P['checks'])} passed")


def committed_checks(P: dict) -> None:
    m = P["meta"]
    wf = json.load(open(os.path.join(ROOT, "eval/results/falsification_walkforward_12d_prereg.json")))
    sens = json.load(open(os.path.join(ROOT, "eval/results/sensitivity_amendment1.json")))
    day = m["test_day"]
    v0 = next(r for r in wf["table"] if r["test"] == day)
    v1 = {p: sens["per_day_raw"]["V1_strict"][day][p]["total"] for p in ("naive", "threshold_pair", "lev")}
    for sim, ref in (("frozen", {"naive": v0["naive"], "thr": v0["threshold_pair"], "lev": v0["lev"]}),
                     ("strict", {"naive": v1["naive"], "thr": v1["threshold_pair"], "lev": v1["lev"]})):
        mine = {p: sum(P["grid_day"][pyg_key(sim, f, d, m["machine_D_us"])][p]["usd"] for f in m["fees"] for d in m["reg_deltas_ms"]) for p in ref}
        good = all(abs(mine[p] - ref[p]) <= 1e-6 * max(1.0, abs(ref[p])) for p in ref)
        ok(f"day grid at δ=1/5/20 == committed {day} totals ({'V0 walk-forward' if sim == 'frozen' else 'V1 strict'})", good,
           " ".join(f"{p} {mine[p]:+,.2f}/{ref[p]:+,.2f}" for p in ref))


def get(port: int, path: str, timeout: float = 30.0):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=timeout) as r:
        body = r.read()
        return r.status, (json.loads(body) if path.startswith("/api/") else body.decode())


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def backend_checks(P: dict) -> None:
    m = P["meta"]
    port = free_port()
    pf = tempfile.NamedTemporaryFile(delete=False).name
    t0 = time.time()
    proc = subprocess.Popen([sys.executable, "-m", "demo.server", "--port", str(port), "--port-file", pf], cwd=ROOT,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True)
    try:
        t_page = t_ready = None
        while time.time() - t0 < 90:
            if proc.poll() is not None:
                break
            try:
                port = int(open(pf).read().strip() or port)
                if t_page is None:
                    st, html = get(port, "/index.html", 5)
                    if st == 200 and "assets/data.js" in html:
                        t_page = time.time() - t0
                s = get(port, "/api/status", 5)[1]
                if s["ready"]:
                    t_ready = time.time() - t0
                    break
            except (OSError, ValueError):
                pass
            time.sleep(0.25)
        ok("backend serves the page ≤ 60 s after start", t_page is not None and t_page <= 60, f"{t_page:.1f} s" if t_page else "never")
        ok("backend live (Numba compiled + timed) ≤ 60 s after start", t_ready is not None and t_ready <= 60, f"{t_ready:.1f} s" if t_ready else "never")
        if t_ready is None:
            print(proc.stdout.read() if proc.poll() is not None else "", flush=True)
            return
        configs = [("frozen", 1.0, 1.0), ("frozen", 1.0, 5.0), ("frozen", 1.0, 20.0), ("frozen", 2.0, 5.0), ("frozen", 1.0, 0.01),
                   ("frozen", 1.0, 100.0), ("strict", 1.0, 1.0), ("strict", 1.0, 20.0), ("strict", 2.0, 1.0), ("strict", 1.0, 0.1)]
        worst_tot, worst_pnl, oc_mis, lev_err, engines = 0.0, 0.0, 0, 0.0, set()
        for sim, fee, d in configs:
            r = get(port, f"/api/eval?sim={sim}&fee={fee:g}&delta={d:g}")[1]
            g = P["grid_window"][pyg_key(sim, fee, d, m["machine_D_us"])]
            for p in ("naive", "thr", "lev"):
                worst_tot = max(worst_tot, abs(r["tot"][p]["usd"] - g["tot"][p]["usd"]))
                oc_mis += int(r["tot"][p]["n"] != g["tot"][p]["n"])
            for i, c in enumerate(g["oc"]):
                oc_mis += int((-1 if c == "-" else int(c)) != r["oc"][i])
                worst_pnl = max(worst_pnl, abs(g["pnl_c"][i] / 100 - r["pnl"][i]))
            lev_err = max(lev_err, r["lev_max_abs_err_vs_sklearn_bps"])
            engines.add(r["lev_engine"].split(" ")[0])
        ok("live recompute == exported grid (10 configs: totals, counts, per-opportunity outcomes)", worst_tot < 1e-6 and oc_mis == 0 and worst_pnl <= 0.0051,
           f"max |Δtotal| {worst_tot:.1e} USD, outcome mismatches {oc_mis}, max |Δpnl| {worst_pnl:.4f} (exported in cents)")
        ok("compiled LEV (Numba) == sklearn on the window's opportunities", engines == {"numba"} and lev_err < 1e-9, f"engine {engines}, max |Δ| {lev_err:.1e} bps")
        tm = get(port, "/api/timing")[1]
        ok("live decision timing measured, exact vs sklearn", tm.get("ready") and tm["exact_max_abs_err_bps"] < 1e-9 and tm["p50_us"] > 0,
           f"p50 {tm['p50_us']:.2f} µs, p99 {tm['p99_us']:.2f} µs over {tm['n_calls']:,} calls")
        ids = P["cands"]["1"]["opp_id"][:3]
        r = get(port, f"/api/race?rt=300&delta=1&sim=frozen&ids={','.join(map(str, ids))}&machine_D_us={m['machine_D_us']:g}")[1]
        gy, gm = P["grid_window"][pyg_key("frozen", 1.0, 1.0, 300000.0)], P["grid_window"][pyg_key("frozen", 1.0, 1.0, m["machine_D_us"])]
        good = all(abs(r[w][p]["usd"] - g["tot"][p]["usd"]) < 1e-6 and r[w][p]["n"] == g["tot"][p]["n"]
                   for w, g in (("you", gy), ("machine", gm)) for p in ("naive", "thr"))
        ok("race at RT 300 ms, δ 1 ms == exported grid (you and machine rows)", good,
           f"you naive {r['you']['naive']['usd']:+.2f} thr {r['you']['thr']['usd']:+.2f} · machine naive {r['machine']['naive']['usd']:+.2f} thr {r['machine']['thr']['usd']:+.2f}")
        if os.environ.get("P6_SMOKE_NO_BROWSER") != "1":
            from demo import browser_check
            browser_check.run(f"http://127.0.0.1:{port}/#stage-1", lambda: os.killpg(proc.pid, signal.SIGTERM), ok)
    finally:
        if proc.poll() is None:            # the browser regression may already have killed it (macOS: EPERM on a dead group)
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                pass
        proc.wait(timeout=10)
        os.unlink(pf)


def model_checks() -> None:
    from components.decision.compiled import flatten
    for sim in ("frozen", "strict"):
        with gzip.open(os.path.join(A, f"lev_{sim}.pkl.gz"), "rb") as fh:
            model = pickle.load(fh)
        a, z = flatten(model), np.load(os.path.join(A, f"lev_{sim}.npz"))
        same = all(np.array_equal(np.asarray(a[k]), z[k], equal_nan=np.asarray(a[k]).dtype.kind == "f") for k in z.files)
        ok(f"LEV ({sim}) pickle flattens to the committed lev_{sim}.npz", same, f"{a['n_trees']} trees / {a['n_nodes']:,} nodes")


def main() -> int:
    t0 = time.time()
    os.chdir(ROOT)
    sys.path.insert(0, ROOT)
    P = load_data()
    static_checks(P)
    committed_checks(P)
    model_checks()
    backend_checks(P)
    n_fail = sum(not r[1] for r in RESULTS)
    print(f"\nsmoke: {len(RESULTS) - n_fail}/{len(RESULTS)} passed in {time.time() - t0:.1f} s", flush=True)
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
