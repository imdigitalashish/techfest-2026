"""Sequential, memory-guarded run queue for the shared M5 (Supervisor rules, 4 Oct 11:10 IST).

- One training run at a time, under `nice -n 10`.
- Pause the run (SIGSTOP) when `kern.memorystatus_level` < 25 %; resume (SIGCONT) above 30 %.
  A run only starts when the level is above 30 %.
- Work list: eval/queue.txt, one run per line: `<tag> <scenario> <strategy> <seed> [--flag value ...]`
  (# comments allowed; extra flags are passed to eval.run_matrix, e.g. `--alpha 64`).
  The runner re-reads the file before every run, so lines can be added or reordered while it works;
  runs already present in eval/results/<tag>_<scenario>.jsonl are skipped (idempotent, safe to restart).

Usage:  nice -n 10 python -m eval.queue_runner            # runs until the queue is empty, then exits
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "eval" / "queue.txt"
RES = ROOT / "eval" / "results"
LOG = RES / "logs" / "queue.log"
LOW, HIGH = 25, 30
CHILD: subprocess.Popen | None = None


def log(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(line + "\n")


def mem_level() -> int:
    try:
        return int(subprocess.check_output(["sysctl", "-n", "kern.memorystatus_level"], text=True).strip())
    except Exception:
        return 100


def done(tag: str, scenario: str, strategy: str, seed: int, rounds: int = 12) -> bool:
    f = RES / f"{tag}_{scenario}.jsonl"
    if not f.exists():
        return False
    for line in f.read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            if r["strategy"] == strategy and r["seed"] == seed and r["rounds"] == rounds:
                return True
    return False


def next_run(failed: dict) -> tuple | None:
    for raw in QUEUE.read_text().splitlines():
        parts = raw.split("#")[0].split()
        if len(parts) < 4:
            continue
        spec = (parts[0], parts[1], parts[2], int(parts[3]), tuple(parts[4:]))
        if failed.get(spec, 0) >= 2 or done(*spec[:4]):
            continue
        return spec
    return None


def run(spec: tuple) -> int:
    global CHILD
    while mem_level() <= HIGH:
        log(f"memory level {mem_level()}% ≤ {HIGH}%: waiting to start {spec}")
        time.sleep(30)
    tag, scenario, strategy, seed, extra = spec
    cmd = ["nice", "-n", "10", sys.executable, "-m", "eval.run_matrix", "--tag", tag, "--scenario", scenario,
           "--strategies", strategy, "--seeds", str(seed), "--skip-existing", *extra]
    t0 = time.time()
    out_path = RES / "logs" / f"run_{tag}_{scenario}_{strategy}_s{seed}.out"
    log(f"START {spec}")
    with out_path.open("w") as out:
        CHILD = subprocess.Popen(cmd, cwd=ROOT, stdout=out, stderr=subprocess.STDOUT)
        paused = False
        while CHILD.poll() is None:
            lvl = mem_level()
            if not paused and lvl < LOW:
                os.kill(CHILD.pid, signal.SIGSTOP)
                paused = True
                log(f"PAUSE pid {CHILD.pid}: memory level {lvl}% < {LOW}%")
            elif paused and lvl > HIGH:
                os.kill(CHILD.pid, signal.SIGCONT)
                paused = False
                log(f"RESUME pid {CHILD.pid}: memory level {lvl}% > {HIGH}%")
            time.sleep(10)
    for line in out_path.read_text(errors="ignore").splitlines():
        if line.startswith(("DONE", "Traceback")) or "Error" in line:
            log("   " + line)
    log(f"END {spec} rc={CHILD.returncode} wall={time.time() - t0:.0f}s")
    return CHILD.returncode


def _terminate(signum, frame) -> None:  # noqa: ARG001
    if CHILD and CHILD.poll() is None:
        os.kill(CHILD.pid, signal.SIGCONT)
        CHILD.terminate()
        log(f"stopped child {CHILD.pid} on signal {signum}")
    sys.exit(1)


def main() -> None:
    signal.signal(signal.SIGTERM, _terminate)
    signal.signal(signal.SIGINT, _terminate)
    failed: dict = {}
    log(f"queue runner up (pid {os.getpid()}), memory level {mem_level()}%")
    while True:
        spec = next_run(failed)
        if spec is None:
            log("queue empty: exiting")
            return
        if run(spec) != 0:
            failed[spec] = failed.get(spec, 0) + 1
            log(f"FAILED {spec} ({failed[spec]}x)")


if __name__ == "__main__":
    main()
