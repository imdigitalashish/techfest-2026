"""Ratchet driver: evaluate candidate C5 inference configs with the FROZEN eval.py and keep/revert.

    python autoresearch/ratchet.py --weights <best.pt> --candidates autoresearch/candidates.json
Each candidate = {"hypothesis": str, "patch": {config keys}}. The incumbent config lives in autoresearch/config.json.
Appends one row per run to autoresearch/results.tsv: timestamp, commit, hypothesis, metric, delta, kept, notes.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CFG = HERE / "config.json"
TSV = HERE / "results.tsv"
HEADER = "timestamp\tcommit\thypothesis\tmetric\tdelta\tkept\tnotes\n"


def run_eval(weights: str, cfg: dict, split: str = "val") -> tuple[float, dict]:
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(cfg, f)
    r = subprocess.run([sys.executable, str(HERE / "eval.py"), "--weights", weights, "--config", f.name, "--split", split],
                       capture_output=True, text=True, cwd=HERE.parent)
    if r.returncode:
        raise RuntimeError(r.stderr[-2000:])
    sec = json.loads([ln for ln in r.stderr.splitlines() if ln.startswith("{")][-1])
    return float(r.stdout.strip().splitlines()[-1]), sec


def log(hyp: str, metric: float, delta: float | str, kept: str, notes: str) -> None:
    if not TSV.exists():
        TSV.write_text(HEADER)
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=HERE).stdout.strip()
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with TSV.open("a") as f:
        f.write(f"{ts}\t{sha}\t{hyp}\t{metric:.4f}\t{delta if isinstance(delta, str) else f'{delta:+.4f}'}\t{kept}\t{notes}\n")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--weights", required=True)
    p.add_argument("--candidates", required=True)
    p.add_argument("--floor", type=float, default=0.01)
    a = p.parse_args()
    inc = json.loads(CFG.read_text())
    base, sec = run_eval(a.weights, inc)
    log("incumbent (re-measured)", base, "n/a", "baseline", f"boot_se={sec['boot_se']} ms/img={sec['ms_per_img_median']} cfg={json.dumps(inc)}")
    print(f"incumbent {base:.4f}", flush=True)
    for c in json.loads(Path(a.candidates).read_text()):
        cand = {**inc, **c["patch"]}
        try:
            m, s = run_eval(a.weights, cand)
        except RuntimeError as e:
            log(c["hypothesis"], 0.0, "n/a", "error", str(e).splitlines()[-1][:200])
            continue
        d = m - base
        keep = d > max(a.floor, s["boot_se"])
        log(c["hypothesis"], m, d, "yes" if keep else "no",
            f"boot_se={s['boot_se']} P@.25={s['precision@0.25']} R@.25={s['recall@0.25']} ms/img={s['ms_per_img_median']} "
            f"patch={json.dumps(c['patch'])}")
        print(f"{c['hypothesis']}: {m:.4f} ({d:+.4f}) {'KEEP' if keep else 'revert'}", flush=True)
        if keep:
            inc, base = cand, m
            CFG.write_text(json.dumps(inc, indent=1) + "\n")


if __name__ == "__main__":
    main()
