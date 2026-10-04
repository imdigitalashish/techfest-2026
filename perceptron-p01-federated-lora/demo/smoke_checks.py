"""Headless smoke test of the P1 demo: no browser, no GPU. Exit 0 = every check passed.

  python3 demo/smoke_checks.py --replay-only    # stdlib only: page data vs committed sources, headline numbers,
                                                #   validation runs + verdict, fallback files, server, stage flow
                                                #   (protocol double), page selftest in headless Chrome (WARN if none)
  .venv/bin/python demo/smoke_checks.py         # + live path: schedule equivalence; through the server, the real
                                                #   engine holds after round 1, takes the tablet unplug, resumes,
                                                #   and stops on request (rounds 1-2 equal the committed seed-0 runs);
                                                #   Flower path == the in-process harness for round 1
demo/smoke.sh wraps this under nice -n 10.
"""
from __future__ import annotations

import argparse
import html
import itertools
import json
import math
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from demo import export_replay  # noqa: E402  (stdlib only)
from demo import validate  # noqa: E402  (stdlib only)

FAILS: list[str] = []
MINUS = "\u2212"


def check(cond: bool, msg: str) -> None:
    print(("  ok   " if cond else "  FAIL ") + msg, flush=True)
    if not cond:
        FAILS.append(msg)


def fmt(v: float, nd: int = 3, signed: bool = True) -> str:
    """Python twin of fmt() in demo/web/app.js (how the page prints a number)."""
    s = f"{abs(v):.{nd}f}"
    if float(s) == 0:
        return s
    return (MINUS if v < 0 else "+" if signed else "") + s


def load_page_data() -> dict:
    text = (ROOT / "demo" / "web" / "data.js").read_text()
    assert text.startswith("window.P1 = ") and text.rstrip().endswith(";")
    return json.loads(text[len("window.P1 = "):].rstrip().rstrip(";"))


# ---------------------------------------------------------------------------------------------------------
def replay_checks() -> None:
    print("[page data]")
    built = export_replay.build()
    on_disk = (ROOT / "demo" / "web" / "data.js").read_text()
    check(built == on_disk, "demo/web/data.js is exactly what demo/export_replay.py builds from the committed sources")
    P = load_page_data()
    res = ROOT / "eval" / "results"
    canon = json.loads((res / "v2_canonical.json").read_text())
    dcanon = json.loads((res / "v2_dropout_canonical.json").read_text())
    check(P["canonical"] == canon, "embedded canonical dict == eval/results/v2_canonical.json")
    check(P["dropout_canonical"] == dcanon, "embedded dropout dict == eval/results/v2_dropout_canonical.json")
    check(P["untuned"] == json.loads((res / "base_per_domain_smollm2-135m.json").read_text()),
          "embedded untuned losses == base_per_domain_smollm2-135m.json")

    print("[headline numbers as the page prints them]")
    C = {**canon, **dcanon}
    expect = {  # numbers quoted in the lead's brief / deliverables, as the page formats them
        ("dropout.spike_vs_fedavg_ab_homo.macro_mean", 3): f"{MINUS}0.081",
        ("dropout.spike_vs_fedavg_ab_homo.macro_lo", 3): f"{MINUS}0.093",
        ("dropout.spike_vs_fedavg_ab_homo.macro_hi", 3): f"{MINUS}0.070",
        ("dropout.spike_vs_ffa_lora.macro_mean", 3): f"{MINUS}0.050",
        ("dropout.spike_vs_ffa_lora.macro_lo", 3): f"{MINUS}0.053",
        ("dropout.spike_vs_ffa_lora.macro_hi", 3): f"{MINUS}0.046",
        ("dropout.spike_vs_flexlora.macro_mean", 3): f"{MINUS}0.083",
        ("dropout.spike_vs_flexlora.macro_lo", 3): f"{MINUS}0.091",
        ("dropout.spike_vs_flexlora.macro_hi", 3): f"{MINUS}0.074",
        ("dropout.fedavg_ab_homo.c0_norm_mean", 2): "0.88",
        ("dropout.anchor_full.c0_norm_mean", 2): "0.22",  # as deliverables/round1-abstract.md renders it (.2f)
        ("dropout.fedavg_ab_homo.outage_peak_rise_mean", 3): "+0.277",
        ("dropout.ffa_lora.outage_peak_rise_mean", 3): "+0.076",
        ("dropout.flexlora.outage_peak_rise_mean", 3): "+0.233",
        ("dropout.anchor_full.outage_peak_rise_mean", 3): f"{MINUS}0.020",
        ("dropout.spike_vs_fedavg_ab_homo.micro_mean", 3): "+0.116",
        ("dropout.spike_vs_fedavg_ab_homo.worst_mean", 3): "+0.057",
    }
    for (k, nd), want in expect.items():
        signed = not k.endswith("c0_norm_mean")
        got = fmt(C[k], nd, signed)
        check(got == want, f"{k} prints as {got} (expected {want})")
    check(C["dropout.anchor_full.domains_ci_pos_bonf"] == 5, "AnchorLoRA: 5 of 5 domains above untuned (Bonferroni)")
    for s in ("fedavg_ab_homo", "ffa_lora", "flexlora"):
        worse = [d for d in export_replay.DOMAINS if C[f"dropout.{s}.{d}.gain_hi_bonf"] < 0]
        check(C[f"dropout.{s}.domains_ci_pos_bonf"] == 1 and len(worse) == 4 and "wiki" not in worse,
              f"{s}: only wiki above untuned, the other 4 below (Bonferroni)")
    check(C["dropout.anchor_full.outage_peak_rise_max"] < 0,
          "AnchorLoRA's tablet domain below untuned at every evaluated round in every seed (peak max < 0)")

    print("[every committed key the page reads exists]")
    js = (ROOT / "demo" / "web" / "app.js").read_text()
    subst = {"${s}": export_replay.STRATS, "${d}": export_replay.DOMAINS, "${d.id}": [d[0] for d in export_replay.DEVICES],
             "${k}": ["spike_vs_fedavg_ab_homo", "spike_vs_ffa_lora", "spike_vs_flexlora"]}
    templates = set(re.findall(r"[`'](?:dropout|base)\.[A-Za-z0-9_.${}]+[`']", js))
    missing, n = [], 0
    for t in templates:
        t = t[1:-1]
        if "<" in t:
            continue
        holes = [hk for hk in subst if hk in t]
        for combo in itertools.product(*(subst[hk] for hk in holes)):
            key = t
            for hk, v in zip(holes, combo):
                key = key.replace(hk, v)
            n += 1
            if key not in C:
                missing.append(key)
    check(not missing and n > 100, f"{n} key expansions from {len(templates)} templates in app.js all present" +
          (f"; missing {missing[:3]}" if missing else ""))

    print("[replay series vs committed summaries]")
    rep = P["replay"]["runs"]
    for s in export_replay.STRATS:
        per_seed = []
        for seed in rep[s].values():
            nz = [r["norm_share_c0"] for r in seed["rounds"] if r["norm_share_c0"] is not None]
            per_seed.append(sum(nz) / len(nz))
        check(abs(sum(per_seed) / len(per_seed) - C[f"dropout.{s}.c0_norm_mean"]) < 1e-5,
              f"{s}: per-round workstation norm share averages to c0_norm_mean")
        peaks = [max(r["eval"]["manpages"] for r in seed["rounds"] if r["eval"]) - P["untuned"]["manpages"]
                 for seed in rep[s].values()]
        check(abs(sum(peaks) / len(peaks) - C[f"dropout.{s}.outage_peak_rise_mean"]) < 1e-5,
              f"{s}: replayed man-page curve peaks average to outage_peak_rise_mean")
    prof = (ROOT / "components" / "device_simulator" / "profiles.py").read_text()
    found = re.findall(r'client_id="(c\d)", device_class="([^"]+)", domain="([^"]+)", n_train_blocks=(\d+),\s*'
                       r'rank=(\d+), local_steps=(\d+)', prof)
    check([(a, b, c, int(d), int(e), int(f)) for a, b, c, d, e, f in found] == export_replay.DEVICES,
          "device list on the page mirrors components/device_simulator/profiles.py")

    print("[validation artifacts]")
    res_file = ROOT / "demo" / "validation" / "results.json"
    check(res_file.exists(), "demo/validation/results.json exists")
    if res_file.exists():
        committed = json.loads(res_file.read_text())
        fresh = json.loads(json.dumps(validate.table()))  # same JSON round trip as results.json
        check(fresh["verdict"] == committed["verdict"] and fresh["rows"] == committed["rows"],
              "validation table recomputed from demo/validation/runs equals results.json")
        for kind in ("unplug", "ghost"):
            for seed in validate.SEEDS:
                probs = validate.check_run(kind, seed)
                check(not probs, f"validation run {kind}_s{seed}: seed, 6 rounds x both strategies, exact outage "
                                 f"({validate.OUTAGE[kind] or 'none'}), finite" + (f" -- {probs}" if probs else ""))
        check(sorted(committed["verdict"]) == ["P1", "P2", "P3"] and all(v is True for v in committed["verdict"].values()),
              f"pre-registered criteria all True (not just present): {committed['verdict']}")
        check(sorted(r["seed"] for r in committed["rows"]) == validate.SEEDS and all("invalid" not in r for r in committed["rows"]),
              "verdict covers seeds 0-4, every one usable")
        check(committed["deterministic_r1_all"] is True, "round 1 identical in ghost and unplug runs (every seed)")
        from demo.live_engine import provenance  # stdlib at import time (torch loads lazily)

        now = provenance()["code_sha"]
        validated = sorted({p["code_sha"] for p in committed["provenance"]})
        check(validated == [now], f"live engine + components code_sha {now} == the validated code_sha {validated}")
    rec = P.get("recorded")
    check(rec is not None, "RECORDED run present (demo/fallback/recorded_live_s0.jsonl)")
    if rec:
        rounds = [e for e in rec["events"] if e["ev"] == "round"]
        u0 = json.loads(validate.run_path("unplug", 0).read_text())
        same = all(any(r["fed"] == e["fed"] and r["round"] == e["round"] and r["per_domain"] == e["per_domain"]
                       for r in u0["records"]) for e in rounds)
        check(len(rounds) == 12 and same, "RECORDED events are the validation unplug run of seed 0 (12 round events, same values)")
    fb = ROOT / "demo" / "fallback"
    need = ["frame1_committed_gains.png", "frame2_committed_outage.png"] + [f"frame3_recorded_live_r{t}.png" for t in range(1, 7)]
    pngs_ok = all((fb / n).is_file() and (fb / n).read_bytes()[:8] == b"\x89PNG\r\n\x1a\n" for n in need)
    gif = fb / "recorded_live.gif"
    gif_ok = gif.is_file() and gif.read_bytes()[:6] in (b"GIF89a", b"GIF87a") and gif.stat().st_size > 10_000
    check(pngs_ok and gif_ok, f"fallback: {len(need)} PNG frames + recorded_live.gif exist and are valid images")


# ---------------------------------------------------------------------------------------------------------
def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def http(url: str, data: dict | None = None) -> tuple[int, bytes]:
    req = urllib.request.Request(url, data=None if data is None else json.dumps(data).encode(),
                                 headers={"Content-Type": "application/json"}, method="GET" if data is None else "POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def server_checks() -> None:
    print("[server, system python3, stdlib only]")
    port = free_port()
    py = "/usr/bin/env"
    proc = subprocess.Popen([py, "python3", str(ROOT / "demo" / "server.py"), "--port", str(port), "--no-browser"],
                            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        line = proc.stdout.readline()  # type: ignore[union-attr]
        m = re.search(r"http://127\.0\.0\.1:(\d+)/", line)
        check(m is not None, f"server started: {line.strip()[:90]}")
        if m is None:
            return
        base = f"http://127.0.0.1:{m.group(1)}"
        t0 = time.time()
        code, body = http(base + "/")
        check(code == 200 and b"AnchorLoRA" in body, f"GET / -> {code} in {time.time() - t0:.2f}s")
        for path in ("/app.js", "/style.css", "/data.js"):
            code, body = http(base + path)
            check(code == 200 and len(body) > 1000, f"GET {path} -> {code} ({len(body) // 1024} KB)")
        code, body = http(base + "/api/status")
        st = json.loads(body)
        check(code == 200 and "live_available" in st, f"GET /api/status -> live_available={st.get('live_available')}")
        code, _ = http(base + "/api/cmd", {"cmd": "unplug", "device": "c4"})
        check(code == 409, f"POST /api/cmd with no live run -> {code} (refused)")
        code, _ = http(base + "/../demo/server.py")
        check(code == 404, "path traversal refused")
    finally:
        proc.terminate()
        proc.wait(timeout=5)


def start_server(env: dict | None = None) -> tuple[subprocess.Popen, str | None]:
    proc = subprocess.Popen(["/usr/bin/env", "python3", str(ROOT / "demo" / "server.py"), "--port", str(free_port()),
                             "--no-browser"], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                            env={**os.environ, **(env or {})})
    m = re.search(r"http://127\.0\.0\.1:(\d+)/", proc.stdout.readline())  # type: ignore[union-attr]
    return proc, (f"http://127.0.0.1:{m.group(1)}" if m else None)


def status(base: str) -> dict:
    return json.loads(http(base + "/api/status")[1])


def wait_until(pred, timeout: float, step: float = 0.1):
    t = time.time()
    while time.time() - t < timeout:
        v = pred()
        if v:
            return v
        time.sleep(step)
    return None


def recording(since: float) -> Path | None:
    files = [f for f in (ROOT / "demo" / ".live").glob("session-*.jsonl") if f.stat().st_mtime >= since - 1]
    return max(files, key=lambda f: f.stat().st_mtime) if files else None


def events(path: Path | None) -> list[dict]:
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()] if path and path.exists() else []


def stage_flow_checks() -> None:
    print("[stage flow through the server, with the engine's protocol double (demo/fake_engine.py, no model)]")
    proc, base = start_server({"P1_DEMO_TEST_ENGINE": str(ROOT / "demo" / "fake_engine.py")})
    try:
        check(base is not None, "server started with the protocol double")
        if base is None:
            return
        t0 = time.time()
        code, _ = http(base + "/api/start", {"seed": 0})
        check(code == 200, f"POST /api/start -> {code}")
        code, body = http(base + "/api/cmd", {"cmd": "unplug", "device": "c4"})
        check(code == 409 and b"round 1" in body, f"plug change before round 1 refused -> {code} {body[:60]!r}")
        held = wait_until(lambda: status(base).get("holding"), 15)
        evs = events(recording(t0))
        kinds = [e["ev"] for e in evs]
        hold = next((e for e in evs if e["ev"] == "stage_hold"), None)
        check(bool(held) and hold is not None and hold["after_round"] == 1 and hold["staged"] is True
              and not any(e["ev"] == "round_start" and e["round"] == 2 for e in evs),
              "engine holds after round 1 (stage_hold after_round=1, staged) before any round 2")
        code, _ = http(base + "/api/cmd", {"cmd": "unplug", "device": "c4"})
        check(code == 200, f"tablet plug pulled at the hold -> {code}")
        code, _ = http(base + "/api/cmd", {"cmd": "resume"})
        check(code == 200, f"resume -> {code}")
        wait_until(lambda: status(base).get("round") == 3, 15, 0.02)
        code, body = http(base + "/api/cmd", {"cmd": "unplug", "device": "c1"})
        check(code == 409 and b"no later round" in body, f"plug change in the final round refused -> {code} {body[:60]!r}")
        fin = wait_until(lambda: (lambda s: s if not s["running"] else None)(status(base)), 15)
        check(bool(fin) and fin["state"] == "finished", f"run finished -> state {fin and fin['state']}")
        evs = events(recording(t0))
        ack = next((e for e in evs if e["ev"] == "cmd_ack" and e["device"] == "c4"), {})
        r2 = next((e for e in evs if e["ev"] == "round_start" and e["round"] == 2), {})
        check(ack.get("effective_round") == 2 and r2.get("unplugged") == ["c4"], "unplug acknowledged for round 2 and applied in round 2")
        mem = [e for e in evs if e["ev"] == "memory" and e.get("paused")]
        start = next((e for e in mem if e.get("where") == "start"), {})
        train = next((e for e in mem if e.get("where") == "train"), {})
        check(start.get("reason") == "waiting_to_start" and start.get("requires") == 30
              and train.get("reason") == "paused_training" and train.get("resumes_at") == 30 and train.get("pause_below") == 25,
              "memory events carry their reason and threshold (start: requires 30; training: below 25, resumes at 30)")
        t1 = time.time()
        http(base + "/api/start", {"seed": 0})
        wait_until(lambda: status(base).get("holding"), 15)
        code, body = http(base + "/api/stop", {})
        st = status(base)
        check(code == 200 and json.loads(body).get("stopped") is True and not st["running"] and st["state"] == "stopped",
              f"stop is awaited: /api/stop -> {code}, then status running={st['running']} state={st['state']}")
        ex = wait_until(lambda: next((e for e in events(recording(t1)) if e["ev"] == "engine_exit"), None), 5)
        check(bool(ex) and ex.get("stopped") is True, "engine_exit recorded as stopped")
    finally:
        proc.terminate()
        proc.wait(timeout=5)


def find_chrome() -> str | None:
    cands = [os.environ.get("P1_DEMO_CHROME"), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             "/Applications/Chromium.app/Contents/MacOS/Chromium",
             "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
             shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("chromium-browser")]
    return next((c for c in cands if c and Path(c).exists()), None)


def ui_checks() -> None:
    print("[page in headless Chrome at 1440x900: ?selftest=1 drives all 4 tabs and the stage flow from committed fixtures]")
    chrome = find_chrome()
    if not chrome:
        print("  WARN no Chrome/Chromium/Edge found: headless UI check skipped (not a failure)")
        return
    url = (ROOT / "demo" / "web" / "index.html").as_uri() + "?selftest=1"
    buf: list[str] = []
    with tempfile.TemporaryDirectory() as prof:
        cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1440,900",
               f"--user-data-dir={prof}", "--use-mock-keychain", "--no-first-run", "--no-default-browser-check",
               "--disable-extensions", "--disable-background-networking", "--disable-component-update", "--disable-sync",
               "--virtual-time-budget=20000", "--dump-dom", url]
        t0 = time.time()
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, start_new_session=True)

        def reader() -> None:
            for line in p.stdout:  # type: ignore[union-attr]
                buf.append(line)
                if "</html>" in line:
                    return

        th = threading.Thread(target=reader, daemon=True)
        th.start()
        th.join(timeout=60)
        try:
            os.killpg(p.pid, signal.SIGKILL)  # headless Chrome may linger after --dump-dom; its own process group
        except ProcessLookupError:
            pass
        p.wait(timeout=10)
    m = re.search(r'<pre id="selftest"[^>]*>(.*?)</pre>', "".join(buf), re.S)
    check(m is not None, f"selftest result found in the dumped DOM ({time.time() - t0:.1f}s, file:// page, no network)")
    if not m:
        return
    r = json.loads(html.unescape(m.group(1)))
    for c in r["checks"]:
        check(c["ok"], f"page: {c['name']}" + (f" -- {c['detail']}" if not c["ok"] and c.get("detail") else ""))


# ---------------------------------------------------------------------------------------------------------
def wait_memory(limit_s: int = 90) -> bool:
    t = time.time()
    while True:
        try:
            lvl = int(subprocess.check_output(["sysctl", "-n", "kern.memorystatus_level"], text=True).strip())
        except Exception:
            return True
        if lvl >= 30:
            return True
        if time.time() - t > limit_s:
            return False
        print(f"  (memory level {lvl} < 30: waiting)", flush=True)
        time.sleep(5)


def live_checks() -> None:
    print("[live path: schedule]")
    from components.device_simulator import DEFAULT_PROFILES, availability_schedule
    from demo.live_engine import live_schedule

    check(all(live_schedule(12, s, {"c4": range(4, 9)}) == availability_schedule(DEFAULT_PROFILES, 12, s, "dropout")
              for s in range(5)), "live schedule == committed availability_schedule when given the forced outage")
    if not wait_memory():
        check(False, "memory level stayed < 30: live checks not run (guard)")
        return
    print("[live path through the server: real engine, hold after round 1, tablet unplugged, resume, awaited stop]")
    proc, base = start_server()
    by: dict = {}
    try:
        check(base is not None and status(base).get("live_available") is True, "server up, live engine available")
        if base is None:
            return
        t0 = time.time()
        code, _ = http(base + "/api/start", {"seed": 0})
        check(code == 200, f"POST /api/start -> {code}")
        code, body = http(base + "/api/cmd", {"cmd": "unplug", "device": "c4"})
        check(code == 409 and b"round 1" in body, f"plug change before round 1 refused -> {code}")
        held = wait_until(lambda: status(base).get("holding"), 240, 0.5)
        evs = events(recording(t0))
        check(bool(held) and any(e["ev"] == "stage_hold" and e["after_round"] == 1 for e in evs)
              and not any(e["ev"] == "round_start" and e["round"] == 2 for e in evs),
              f"engine holds after round 1 ({time.time() - t0:.0f}s after start)")
        c1, _ = http(base + "/api/cmd", {"cmd": "unplug", "device": "c4"})
        c2, _ = http(base + "/api/cmd", {"cmd": "resume"})
        check(c1 == 200 and c2 == 200, f"tablet plug pulled at the hold, resumed -> {c1}, {c2}")
        done2 = wait_until(lambda: (lambda ev: ev if sum(e["ev"] == "round" and e["round"] == 2 for e in ev) == 2 else None)(
            events(recording(t0))), 240, 0.5)
        code, body = http(base + "/api/stop", {})
        st = status(base)
        check(bool(done2) and code == 200 and not st["running"] and st["state"] == "stopped",
              f"round 2 done, then stop awaited -> {code}, running={st['running']}, state={st['state']} ({time.time() - t0:.0f}s)")
        pid = next((e.get("pid") for e in events(recording(t0)) if e["ev"] == "server_start"), None)
        gone = True
        try:
            os.kill(pid, 0)
            gone = False
        except (ProcessLookupError, TypeError):
            pass
        check(gone, f"engine process {pid} is gone after the stop")
        evs = events(recording(t0))
    finally:
        proc.terminate()
        proc.wait(timeout=5)
    ack = next((e for e in evs if e["ev"] == "cmd_ack" and e.get("device") == "c4"), {})
    check(ack.get("effective_round") == 2, "unplug acknowledged for round 2 (the validated scenario)")
    untuned = next((e for e in evs if e["ev"] == "untuned"), {})
    by = {(e["fed"], e["round"]): e for e in evs if e["ev"] == "round"}
    vals = [v for rec in by.values() for v in rec["per_domain"].values()] + list(untuned.get("per_domain", {}).values())
    check(len(by) == 4 and len(vals) == 25 and all(math.isfinite(v) for v in vals), f"{len(vals)} live losses, all finite")
    check(untuned.get("identical_start") is True, "both federations start from the identical untuned model")
    if len(by) < 4:
        return
    a2 = by[("anchor_full", 2)]["devices"]["c4"]
    s2 = by[("fedavg_ab_homo", 2)]["devices"]["c4"]
    check(s2["state"] == "unplugged" and a2["state"] == "unplugged" and a2.get("memory") == "reused" and a2.get("memory_age") == 1,
          "round 2: tablet unplugged in both grids; AnchorLoRA reuses its last update (age 1/4)")
    u0 = json.loads(validate.run_path("unplug", 0).read_text())
    g0 = json.loads(validate.run_path("ghost", 0).read_text())
    ref_u = {(r["fed"], r["round"]): r["per_domain"] for r in u0["records"]}
    ref_g = {(r["fed"], r["round"]): r["per_domain"] for r in g0["records"]}
    dg = max(abs(by[(f, 1)]["per_domain"][d] - ref_g[(f, 1)][d]) for f in ("fedavg_ab_homo", "anchor_full") for d in ref_g[(f, 1)])
    du = max(abs(by[(f, r)]["per_domain"][d] - ref_u[(f, r)][d]) for f in ("fedavg_ab_homo", "anchor_full") for r in (1, 2)
             for d in ref_u[(f, r)])
    check(dg <= 1e-6, f"round 1 == committed ghost_s0 (max |diff| {dg:.1e})")
    check(du <= 1e-6, f"rounds 1-2 == committed unplug_s0 (same unplug; max |diff| {du:.1e})")

    print("[live path: Flower adapter == in-process harness (components.orchestrator.run_experiment), round 1]")
    import torch

    torch.set_num_threads(4)
    import components.local_trainer.trainer as trainer

    trainer.pick_device = lambda: torch.device("cpu")
    from components.orchestrator.simulate import ExperimentConfig, load_world, run_experiment
    from demo.live_engine import LIVE

    lm, data = load_world(ExperimentConfig())
    live_data = {d: (tr[:, : LIVE["seq_len"]].contiguous(),
                     ev[:: LIVE["eval_stride"]][: LIVE["eval_blocks_per_domain"], : LIVE["seq_len"]].contiguous())
                 for d, (tr, ev) in data.items()}
    worst = 0.0
    for f in ("fedavg_ab_homo", "anchor_full"):
        cfg = ExperimentConfig(strategy=f, scenario="dropout", seed=0, rounds=1, batch_size=LIVE["batch_size"],
                               lr=LIVE["lr"], eval_every=1)
        _, log = run_experiment(cfg, lm, live_data, log=lambda m: None)
        ip = log[0]["eval"]["per_domain_loss"]
        worst = max(worst, max(abs(ip[d] - by[(f, 1)]["per_domain"][d]) for d in ip))
    check(worst <= 1e-6, f"round-1 losses: Flower path vs in-process harness, max |diff| {worst:.1e}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--replay-only", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    replay_checks()
    server_checks()
    stage_flow_checks()
    ui_checks()
    if not a.replay_only:
        live_checks()
    print(f"\nsmoke: {'PASS' if not FAILS else 'FAIL'} ({len(FAILS)} failed) in {time.time() - t0:.0f}s"
          + ("" if not a.replay_only else " [replay only: live path NOT checked]"))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
