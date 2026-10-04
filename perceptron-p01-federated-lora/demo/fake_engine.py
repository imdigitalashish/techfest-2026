"""Protocol double of demo/live_engine.py, used only by demo/smoke_checks.py (never by the demo itself).

No model and no torch: it speaks the engine's JSON-line events and stdin commands with instant rounds, so the
server's stage flow (hold after round 1, plug gating, memory-reason annotation, awaited stop) is testable in
seconds. Like the real engine, it applies plug changes and honours a pause at the top of the next round.
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import time

ROUNDS = 3
STATE = {"paused": False, "stopped": False, "t": 0, "pending": {}, "out": set()}
LOCK = threading.Lock()


def emit(ev: str, **kw) -> None:
    print(json.dumps({"ev": ev, **kw}), flush=True)


def reader() -> None:
    for line in sys.stdin:
        try:
            c = json.loads(line)
        except ValueError:
            continue
        with LOCK:
            kind = c.get("cmd")
            if kind in ("unplug", "replug"):
                STATE["pending"][c["device"]] = kind == "unplug"
                emit("cmd_ack", cmd=kind, device=c["device"], effective_round=STATE["t"] + 1)
            elif kind == "pause":
                STATE["paused"] = True
                emit("paused", after_round=STATE["t"])
            elif kind == "resume":
                STATE["paused"] = False
                emit("resumed", round=STATE["t"])
            elif kind == "stop":
                STATE["stopped"] = True
    with LOCK:
        STATE["stopped"] = True


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    seed = ap.parse_args().seed
    threading.Thread(target=reader, daemon=True).start()
    emit("hello", seed=seed, rounds=ROUNDS, provenance={"commit": "test", "code_sha": "protocol-double", "dirty": None})
    emit("memory", paused=True, level=29, where="start")
    time.sleep(0.6)
    emit("memory", paused=False, level=31, where="start")
    emit("loading")
    emit("loaded", load_s=0.0)
    emit("untuned", per_domain={"manpages": 4.0}, identical_start=True)
    r = 0
    for r in range(1, ROUNDS + 1):
        while True:
            with LOCK:
                paused, stopped = STATE["paused"], STATE["stopped"]
            if stopped or not paused:
                break
            time.sleep(0.05)
        if stopped:
            break
        with LOCK:
            for dev, out in STATE["pending"].items():
                (STATE["out"].add if out else STATE["out"].discard)(dev)
            STATE["pending"].clear()
            STATE["t"] = r
            unplugged = sorted(STATE["out"])
        emit("round_start", round=r, unplugged=unplugged, scheduled={})
        time.sleep(0.4 if r < ROUNDS else 1.5)  # the final round is long enough to try a (refused) plug change
        if r == 2:
            emit("memory", paused=True, level=24, where="train")
            time.sleep(0.1)
            emit("memory", paused=False, level=30, where="train")
        emit("round_end", round=r, wall_s=0.4)
    emit("done", completed_rounds=r)


if __name__ == "__main__":
    main()
