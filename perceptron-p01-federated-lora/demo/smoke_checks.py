"""Headless smoke test of the P1 demo: no browser, no GPU. Exit 0 = every check passed.

  python3 demo/smoke_checks.py --replay-only    # stdlib only: page data vs committed sources, headline numbers, server
  .venv/bin/python demo/smoke_checks.py         # + live path: schedule equivalence, a 2-round live run through the
                                                #   Flower path (finite, equal to the committed ghost/validation run),
                                                #   and Flower path == the in-process harness for round 1
demo/smoke.sh wraps this under nice -n 10.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import socket
import subprocess
import sys
import tempfile
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
        check(all(v is not None for v in committed["verdict"].values()), f"validation complete: {committed['verdict']}")
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
    print("[live path: 2 rounds through the Flower adapter, CPU, tablet unplugged in round 2]")
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "run.json"
        t0 = time.time()
        r = subprocess.run([sys.executable, "-m", "demo.live_engine", "--seed", "0", "--rounds", "2", "--unplug", "c4:2-2",
                            "--no-stdin", "--out", str(out)], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           text=True, timeout=170)
        check(r.returncode == 0 and out.exists(), f"engine exit {r.returncode} in {time.time() - t0:.0f}s")
        if not out.exists():
            return
        events = [json.loads(x) for x in r.stdout.splitlines() if x.strip()]
        check(all(isinstance(e, dict) and "ev" in e for e in events), f"{len(events)} stdout lines, all JSON events")
        run = json.loads(out.read_text())
    vals = [v for rec in run["records"] for v in rec["per_domain"].values()] + list(run["untuned"].values())
    check(len(run["records"]) == 4 and all(math.isfinite(v) for v in vals), f"{len(vals)} live losses, all finite")
    check(run["identical_start"] is True, "both federations start from the identical untuned model")
    by = {(r["fed"], r["round"]): r for r in run["records"]}
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
    if not a.replay_only:
        live_checks()
    print(f"\nsmoke: {'PASS' if not FAILS else 'FAIL'} ({len(FAILS)} failed) in {time.time() - t0:.0f}s"
          + ("" if not a.replay_only else " [replay only: live path NOT checked]"))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
