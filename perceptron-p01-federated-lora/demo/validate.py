"""Pre-registered validation of the reduced LIVE config (proposal approved by the P1 lead, 4 Oct 2026).

Runs the live engine (the exact code path of the demo, one fresh process per run, CPU, nice 10) for seeds 0-4 x
{ghost: nobody unplugged, unplug: tablet c4 unplugged in rounds 2-6} and checks, in EVERY seed:
  P1  AnchorLoRA's manpages loss stays below the untuned model at every live evaluation (rounds 1-6), unplug run
  P2  at round 6 of the unplug run, the starter's manpages loss is above the untuned model and above AnchorLoRA's
  P3  the unplug's own effect at round 6 (unplug run - ghost run, manpages) is larger for the starter
Also: determinism (round 1 is identical, bit for bit, in the ghost and the unplug run of a seed).

  python -m demo.validate --kind unplug --seeds 0 1 2      # one batch: <= ~12 min CPU, one run at a time
  python -m demo.validate --kind ghost --seeds 3 4
  python -m demo.validate --table                          # -> demo/validation/RESULTS.md + results.json
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VAL = ROOT / "demo" / "validation"
RUNS = VAL / "runs"
SEEDS = [0, 1, 2, 3, 4]
SCRIPT = "c4:2-6"
DOM = "manpages"
CRITERIA = {
    "P1": "AnchorLoRA manpages loss < untuned at every live evaluation (rounds 1-6) of the unplug run",
    "P2": "round 6 of the unplug run: starter manpages loss > untuned AND > AnchorLoRA's",
    "P3": "unplug effect at round 6 (unplug run - ghost run, manpages) larger for the starter than for AnchorLoRA",
}


def run_path(kind: str, seed: int) -> Path:
    return RUNS / f"{kind}_s{seed}.json"


def memory_level() -> int | None:
    try:
        return int(subprocess.check_output(["sysctl", "-n", "kern.memorystatus_level"], text=True).strip())
    except Exception:
        return None


def run_batch(kind: str, seeds: list[int]) -> None:
    RUNS.mkdir(parents=True, exist_ok=True)
    py = ROOT / ".venv" / "bin" / "python"
    for seed in seeds:
        out = run_path(kind, seed)
        if out.exists():
            print(f"skip {out.name} (exists)", flush=True)
            continue
        while (lvl := memory_level()) is not None and lvl < 30:
            print(f"waiting for memory (level {lvl} < 30)", flush=True)
            time.sleep(10)
        cmd = ["nice", "-n", "10", str(py), "-m", "demo.live_engine", "--seed", str(seed), "--no-stdin",
               "--out", str(out)]
        if kind == "unplug":
            cmd += ["--unplug", SCRIPT]
            if seed == 0:  # the scripted demo scenario doubles as the RECORDED fallback run
                cmd += ["--events-out", str(ROOT / "demo" / "fallback" / "recorded_live_s0.jsonl")]
        t = time.time()
        with open(f"/tmp/p1demo_validate_{kind}_s{seed}.log", "w") as log:
            subprocess.run(cmd, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=log, check=True)
        print(f"done {out.name} in {time.time() - t:.0f}s", flush=True)


def manp(run: dict, fed: str) -> dict[int, float]:
    return {r["round"]: r["delta"][DOM] for r in run["records"] if r["fed"] == fed}


FEDS = ("fedavg_ab_homo", "anchor_full")
ROUNDS = 6
OUTAGE = {"unplug": {"c4": [2, 3, 4, 5, 6]}, "ghost": {}}  # exactly the pre-registered histories


def check_run(kind: str, seed: int) -> list[str]:
    """Why a validation run cannot be used (empty = usable): seed, 6 rounds x both strategies, the exact
    tablet-only outage (rounds 2-6) or none for a ghost, no other device unplugged, finite values."""
    path = run_path(kind, seed)
    if not path.exists():
        return [f"{path.name} missing"]
    R = json.loads(path.read_text())
    cfg, probs = R.get("config", {}), []
    if cfg.get("seed") != seed or cfg.get("rounds") != ROUNDS:
        probs.append(f"config seed/rounds {cfg.get('seed')}/{cfg.get('rounds')} != {seed}/{ROUNDS}")
    want_script = {"c4": [2, ROUNDS]} if kind == "unplug" else {}
    if cfg.get("script") != want_script:
        probs.append(f"script {cfg.get('script')} != {want_script}")
    if R.get("unplugged_rounds") != OUTAGE[kind]:
        probs.append(f"unplugged rounds {R.get('unplugged_rounds')} != {OUTAGE[kind]}")
    have = sorted((r["fed"], r["round"]) for r in R.get("records", []))
    want = sorted((f, t) for f in FEDS for t in range(1, ROUNDS + 1))
    if have != want:
        probs.append(f"records {len(have)} != the 12 (strategy, round) pairs")
    vals = list(R.get("untuned", {}).values())
    for r in R.get("records", []):
        vals += list(r["per_domain"].values()) + list(r["delta"].values())
        for dev, d in r["devices"].items():
            out = r["round"] in OUTAGE[kind].get(dev, [])
            if out != (d["state"] == "unplugged"):
                probs.append(f"{r['fed']} round {r['round']}: {dev} state {d['state']}")
    if len(R.get("untuned", {})) != 5 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in vals):
        probs.append("missing or non-finite loss values")
    return probs


def table() -> dict:
    rows, prov = [], set()
    for seed in SEEDS:
        u, g = run_path("unplug", seed), run_path("ghost", seed)
        problems = check_run("unplug", seed) + check_run("ghost", seed)
        if problems:
            rows.append({"seed": seed, "invalid": problems})
            continue
        U, G = json.loads(u.read_text()), json.loads(g.read_text())
        for R in (U, G):
            prov.add((R["provenance"]["commit"], R["provenance"]["code_sha"], R["provenance"]["dirty"]))
        au, su = manp(U, "anchor_full"), manp(U, "fedavg_ab_homo")
        ag, sg = manp(G, "anchor_full"), manp(G, "fedavg_ab_homo")
        last = max(au)
        eff_s, eff_a = su[last] - sg[last], au[last] - ag[last]
        r1u = {(r["fed"]): r["per_domain"] for r in U["records"] if r["round"] == 1}
        r1g = {(r["fed"]): r["per_domain"] for r in G["records"] if r["round"] == 1}
        rows.append({
            "seed": seed, "rounds": last,
            "anchor_manp_max": max(au.values()), "anchor_manp_r6": au[last], "starter_manp_r6": su[last],
            "effect_starter": eff_s, "effect_anchor": eff_a,
            "P1": max(au.values()) < 0, "P2": su[last] > 0 and su[last] > au[last], "P3": eff_s > eff_a,
            "deterministic_r1": r1u == r1g and U["untuned"] == G["untuned"],
            "unplugged_rounds": U["unplugged_rounds"],
            "curves": {"unplug": {"fedavg_ab_homo": su, "anchor_full": au},
                       "ghost": {"fedavg_ab_homo": sg, "anchor_full": ag}},
            "wall_s": {"unplug": U["wall_s"], "ghost": G["wall_s"]},
            "peak_rss_mb": max(U.get("peak_rss_mb", 0), G.get("peak_rss_mb", 0)),
        })
    done = [r for r in rows if "invalid" not in r]
    # a verdict exists only when every pre-registered seed has two usable runs
    verdict = {k: (all(r[k] for r in done) if len(done) == len(SEEDS) else None) for k in ("P1", "P2", "P3")}
    band = {}
    if done:
        for kind in ("unplug", "ghost"):
            for fed in ("fedavg_ab_homo", "anchor_full"):
                rounds = sorted({int(k) for r in done for k in r["curves"][kind][fed]})
                band[f"{kind}.{fed}"] = {
                    str(t): [min(r["curves"][kind][fed][t] for r in done if t in r["curves"][kind][fed]),
                             max(r["curves"][kind][fed][t] for r in done if t in r["curves"][kind][fed])]
                    for t in rounds}
    res = {"criteria": CRITERIA, "script": SCRIPT, "seeds": SEEDS, "domain": DOM, "verdict": verdict,
           "deterministic_r1_all": all(r["deterministic_r1"] for r in done) if done else None,
           "provenance": sorted([{"commit": c, "code_sha": s, "dirty": d} for c, s, d in prov],
                                key=lambda x: x["commit"]),
           "rows": rows, "band": band}
    return res


def write_table(res: dict) -> str:
    one = json.loads(run_path("unplug", 0).read_text()) if run_path("unplug", 0).exists() else {}
    live = one.get("config", {}).get("live", {})
    f = lambda v: f"{v:+.4f}"  # noqa: E731
    yn = lambda b: "PASS" if b else "FAIL"  # noqa: E731
    L = ["# Validation of the reduced LIVE config (auto-generated: `python -m demo.validate --table`)", "",
         "Pre-registered in the demo proposal (approved by the P1 lead, 4 Oct 2026, 20:11 IST); seeds 0-4, none "
         "dropped or picked. Each run is one fresh process of `demo/live_engine.py` (the demo's own code path: "
         "FlowerLoraStrategy + in-process LocalGrid, CPU, nice 10), two federations side by side with paired "
         "availability.", "",
         f"Live config: `{json.dumps(live)}`; committed config otherwise (strategies, ranks, steps, lr, seeded "
         f"dropout draws without the forced outage). Unplug script: `{SCRIPT}` (tablet removed from both grids in "
         "rounds 2-6; ghost = same seed, nobody unplugged). Values: manpages loss minus the untuned model's, on "
         "the same 8 x 64-token eval subset (nats/token); negative = better than untuned.", "",
         "Code: " + "; ".join(f"commit {p['commit']} · code_sha {p['code_sha']} · dirty {p['dirty']}"
                               for p in res["provenance"]) + ". The commit is the local commit at run time (before the "
         "rebase onto main changed its hash); code_sha (sha1 over demo/live_engine.py and components/**/*.py) identifies "
         "the code, and demo/smoke.sh checks that the current engine has the same code_sha.", "",
         "Criteria (every seed must pass):"] + [f"- **{k}** {v}" for k, v in CRITERIA.items()] + [
         "- determinism: round 1 (and the untuned eval) identical bit for bit in the ghost and unplug runs",
         "- usable runs only: each seed needs both runs with 6 rounds x both strategies, finite losses, and exactly the "
         "pre-registered history (tablet unplugged in rounds 2-6, nothing else; the ghost: nothing unplugged)", "",
         "| seed | AnchorLoRA manpages, max over r1-6 | starter manpages r6 | AnchorLoRA manpages r6 | unplug effect "
         "r6: starter / AnchorLoRA | P1 | P2 | P3 | deterministic r1 | wall s (unplug / ghost) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in res["rows"]:
        if "invalid" in r:
            L.append(f"| {r['seed']} | not usable: {'; '.join(r['invalid'])} |||||||||")
            continue
        L.append(f"| {r['seed']} | {f(r['anchor_manp_max'])} | {f(r['starter_manp_r6'])} | {f(r['anchor_manp_r6'])} | "
                 f"{f(r['effect_starter'])} / {f(r['effect_anchor'])} | {yn(r['P1'])} | {yn(r['P2'])} | "
                 f"{yn(r['P3'])} | {r['deterministic_r1']} | {r['wall_s']['unplug']:.0f} / {r['wall_s']['ghost']:.0f} |")
    v = res["verdict"]
    L += ["", "Verdict: " + ", ".join(f"{k} {'PASS' if v[k] else ('FAIL' if v[k] is False else 'incomplete')}"
                                     for k in ("P1", "P2", "P3"))
          + f"; determinism {res['deterministic_r1_all']}.", ""]
    text = "\n".join(L)
    (VAL / "RESULTS.md").write_text(text)
    (VAL / "results.json").write_text(json.dumps(res, indent=1) + "\n")
    return text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["unplug", "ghost"])
    ap.add_argument("--seeds", type=int, nargs="+", default=SEEDS)
    ap.add_argument("--table", action="store_true")
    a = ap.parse_args()
    if a.kind:
        run_batch(a.kind, a.seeds)
    if a.table:
        print(write_table(table()))
    if not a.kind and not a.table:
        ap.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
