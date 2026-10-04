"""LIVE engine of the P1 demo: two federations side by side on ONE shared SmolLM2-135M, CPU only.

The starter (`fedavg_ab_homo`) and AnchorLoRA (`anchor_full`) each run through the Flower Message API of
components/flower_adapter (FlowerLoraStrategy -> Message -> ClientApp -> reply) on an in-process LocalGrid,
driven round by round. Unplugging a device removes its node from BOTH grids from the next round on
(LocalGrid.kill_node; an in-process node removal, not an OS-process kill), so both federations always see the
same availability (full-system comparison under paired availability).

Everything is the committed configuration (strategies, ranks 16/8/4/2/4, local steps 16/8/4/2/4, lr 1e-3, LoRA
r_max 16 on q/v, seeded dropout draws) except the reduced LIVE config below, and the forced tablet outage of the
committed scenario, which is removed: the judge supplies the outage. Events go to stdout as JSON lines; commands
come from stdin as JSON lines ({"cmd": "unplug"|"replug", "device": "c4"}, {"cmd": "pause"|"resume"|"stop"}).

  python -m demo.live_engine --seed 0                                    # driven by demo/server.py
  python -m demo.live_engine --seed 0 --unplug c4:2-6 --no-stdin --out run.json   # scripted (demo/validate.py)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import queue
import resource
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STRATS = ("fedavg_ab_homo", "anchor_full")
LIVE = {"batch_size": 1, "seq_len": 64, "eval_blocks_per_domain": 8, "eval_stride": 6, "rounds": 6,
        "lr": 1e-3, "threads": 4, "eval_every": 1}
MEM_START, MEM_PAUSE, MEM_RESUME = 30, 25, 30
MEMORY_MAX_AGE = 4  # anchor_full's memory_max_age (asserted after loading)


def memory_level() -> int | None:
    """macOS kern.memorystatus_level; None where unavailable (the guard is then off)."""
    try:
        out = subprocess.check_output(["sysctl", "-n", "kern.memorystatus_level"], text=True,
                                      stderr=subprocess.DEVNULL)
        return int(out.strip())
    except Exception:
        return None


def live_schedule(rounds: int, seed: int, forced: dict | None = None) -> dict:
    """allowed_steps[(t, cid)] from exactly the RNG draws of availability_schedule(..., "dropout").

    Only the forced outage is a parameter (default: none). With forced={"c4": range(4, 9)} this equals the
    committed schedule (checked by demo/smoke_checks.py).
    """
    import numpy as np

    from components.device_simulator import DEFAULT_PROFILES

    forced = forced or {}
    rng = np.random.default_rng(10_000 + seed)
    sched = {}
    for t in range(rounds):
        for p in DEFAULT_PROFILES:
            u_off, u_cut, u_frac = rng.random(3)
            if t in forced.get(p.client_id, ()) or u_off < p.p_offline:
                sched[(t, p.client_id)] = 0
            elif u_cut < p.p_cutoff:
                sched[(t, p.client_id)] = max(1, int(p.local_steps * (0.25 + 0.5 * u_frac)))
            else:
                sched[(t, p.client_id)] = p.local_steps
    return sched


def provenance() -> dict:
    """git commit + sha1 over the engine and every components/*.py file (what actually ran)."""
    h = hashlib.sha1()
    files = [ROOT / "demo" / "live_engine.py"] + sorted(
        p for p in (ROOT / "components").rglob("*.py") if "__pycache__" not in p.parts)
    for p in files:
        h.update(str(p.relative_to(ROOT)).encode())
        h.update(p.read_bytes())

    def git(*args: str) -> str | None:
        try:
            return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return None

    status = git("status", "--porcelain", "--", "components", "demo/live_engine.py")
    return {"commit": git("rev-parse", "--short", "HEAD") or "unknown", "code_sha": h.hexdigest()[:12],
            "dirty": None if status is None else bool(status)}


def _clean(x):
    """JSON-safe copy: NaN/inf -> None (browsers reject NaN in JSON)."""
    if isinstance(x, float):
        return x if math.isfinite(x) else None
    if isinstance(x, dict):
        return {str(k): _clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_clean(v) for v in x]
    return x


def _rss_mb() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r / 1e6 if sys.platform == "darwin" else r / 1e3  # bytes on macOS, KiB on Linux


class Engine:
    def __init__(self, seed: int = 0, rounds: int = LIVE["rounds"], threads: int = LIVE["threads"],
                 emit=None, script: dict | None = None) -> None:
        self.seed, self.rounds, self.threads = seed, rounds, threads
        self.sink = emit or (lambda ev: None)
        self.script = script or {}  # {cid: (first_round, last_round)}, 1-based, inclusive
        self.lock = threading.RLock()
        self.pending: dict[str, bool] = {}  # cid -> unplug (True) / replug (False), applied at the next round
        self.unplugged: set[str] = set()
        self.unplug_rounds: dict[str, list[int]] = {}
        self.paused = False
        self.stopped = False
        self.t = 0  # round in progress (1-based); 0 before round 1
        self.records: list[dict] = []
        self.t0 = time.time()

    # ---- events and commands -------------------------------------------------------------------
    def emit(self, ev: str, **kw) -> None:
        with self.lock:
            kw = {"ev": ev, "t_wall": round(time.time() - self.t0, 3), **kw}
            self.sink(_clean(kw))

    def command(self, c: dict) -> None:
        """Thread-safe; unplug/replug take effect at the next round boundary in BOTH federations."""
        with self.lock:
            kind = c.get("cmd")
            if kind in ("unplug", "replug"):
                dev = c.get("device")
                if dev not in {f"c{i}" for i in range(5)}:
                    self.emit("error", message=f"unknown device {dev!r}")
                    return
                self.pending[dev] = kind == "unplug"
                self.emit("cmd_ack", cmd=kind, device=dev, effective_round=self.t + 1)
            elif kind == "pause":
                self.paused = True
                self.emit("paused", after_round=self.t)
            elif kind == "resume":
                self.paused = False
                self.emit("resumed", round=self.t)
            elif kind == "stop":
                self.stopped = True
                self.paused = False
                self.emit("stopping", round=self.t)
            else:
                self.emit("error", message=f"unknown command {c!r}")

    def guard(self, where: str, start: bool = False) -> None:
        """Memory guard: start only at level >= 30; pause while < 25, resume at >= 30."""
        lvl = memory_level()
        if lvl is None or lvl >= (MEM_START if start else MEM_PAUSE):
            return
        self.emit("memory", paused=True, level=lvl, where=where)
        while lvl is not None and lvl < MEM_RESUME and not self.stopped:
            time.sleep(2)
            lvl = memory_level()
        self.emit("memory", paused=False, level=lvl, where=where)

    # ---- setup ---------------------------------------------------------------------------------
    def load(self) -> None:
        import torch

        torch.set_num_threads(self.threads)
        import components.local_trainer.trainer as trainer

        trainer.pick_device = lambda: torch.device("cpu")  # CPU only (demo rule); components/ untouched
        from flwr.app import ConfigRecord, Context, RecordDict

        from components.device_simulator import DEFAULT_PROFILES
        from components.flower_adapter import FlowerLoraStrategy, LocalGrid, make_client_app
        from components.orchestrator.simulate import ExperimentConfig, load_world

        self.ConfigRecord = ConfigRecord
        t = time.time()
        lm, data = load_world(ExperimentConfig())
        L = LIVE
        # first seq_len tokens of every committed block; every eval_stride-th held-out block
        self.data = {d: (tr[:, : L["seq_len"]].contiguous(),
                         ev[:: L["eval_stride"]][: L["eval_blocks_per_domain"], : L["seq_len"]].contiguous())
                     for d, (tr, ev) in data.items()}
        self.lm = lm
        self.devices = [{"id": p.client_id, "cls": p.device_class, "domain": p.domain, "rank": p.rank,
                         "steps": p.local_steps, "n": p.n_train_blocks} for p in DEFAULT_PROFILES]
        self.node_by_cid = {p.client_id: i + 1 for i, p in enumerate(DEFAULT_PROFILES)}
        self.sched = live_schedule(self.rounds, self.seed)
        self.feds = {}
        for name in STRATS:
            cfg = ExperimentConfig(strategy=name, scenario="dropout", seed=self.seed, rounds=self.rounds,
                                   batch_size=L["batch_size"], lr=L["lr"], eval_every=L["eval_every"])
            strat = FlowerLoraStrategy(cfg, lm, self.data, log=lambda m: print(m, file=sys.stderr, flush=True))
            strat.sched = dict(self.sched)  # same draws, no forced outage
            strat.bind_nodes(self.node_by_cid)
            app = make_client_app(lm, strat.client_blocks)
            apps = {node: self._wrap(app, name, cid) for cid, node in self.node_by_cid.items()}
            ctxs = {node: Context(run_id=1, node_id=node, node_config={"client_id": cid, "partition-id": cid},
                                  state=RecordDict(), run_config={}) for cid, node in self.node_by_cid.items()}
            self.feds[name] = {"strategy": strat, "grid": LocalGrid(apps, ctxs), "arrays": strat.initial_arrays()}
        assert self.feds["anchor_full"]["strategy"].inner.memory_max_age == MEMORY_MAX_AGE
        self.load_s = time.time() - t

    def _wrap(self, app, fed: str, cid: str):
        def call(msg, ctx):
            self.guard("train")
            c = msg.content["config"]
            self.emit("device_start", fed=fed, round=self.t, device=cid, steps=int(c["allowed_steps"]),
                      planned=int(c["planned_steps"]), rank=int(c["rank"]))
            reply = app(msg, ctx)
            m = reply.content["meta"]
            self.emit("device_done", fed=fed, round=self.t, device=cid, steps_done=int(m["steps_done"]),
                      planned=int(m["planned_steps"]), status=str(m["status"]), train_loss=float(m["train_loss"]),
                      wall_s=round(float(m["wall_s"]), 3))
            return reply

        return call

    # ---- rounds --------------------------------------------------------------------------------
    def _record(self, name: str, r: int, unpl: list[str], train_s: float, eval_s: float) -> dict:
        s = self.feds[name]["strategy"]
        entry = s.rounds_log[-1]
        agg = entry["aggregation"]
        ev = entry["eval"]["per_domain_loss"]
        devices = {}
        for u in entry["updates"]:
            cid = u["client_id"]
            if cid in unpl:
                state = "unplugged"
            elif u["status"] in ("ok", "partial"):
                state = "fresh"
            elif u["status"] == "late_discarded":
                state = "discarded"
            else:
                state = "offline"
            devices[cid] = {"state": state, "steps": [u["steps_done"], u["planned_steps"]],
                            "scheduled_steps": self.sched[(r - 1, cid)]}
        if name == "anchor_full":  # server memory (MIFA-style): reused for <= 4 rounds, then expired
            g = s.g
            for cid, d in devices.items():
                if d["state"] == "fresh":
                    continue
                if cid in g["mem_round"]:
                    d["memory_age"] = (r - 1) - g["mem_round"][cid]
                    d["memory"] = "reused" if cid in agg["used_memory_for"] else "expired"
                else:
                    d["memory"] = "none"
        delta = {d: ev[d] - self.base[d] for d in ev}
        return {"fed": name, "round": r, "per_domain": ev, "delta": delta,
                "macro_delta": sum(delta.values()) / len(delta), "devices": devices,
                "fresh": len(agg["reporters"]), "reporters": agg["reporters"], "memory": agg["used_memory_for"],
                "weights": agg["weights"], "norm_share": agg["norm_share"], "update_norm": agg["update_norm"],
                "train_s": round(train_s, 2), "eval_s": round(eval_s, 2)}

    def run(self) -> dict:
        prov = provenance()
        self.emit("hello", seed=self.seed, rounds=self.rounds, live=LIVE, strategies=list(STRATS),
                  script={k: list(v) for k, v in self.script.items()}, provenance=prov)
        self.guard("start", start=True)
        if self.stopped:
            self.emit("done", completed_rounds=0, wall_s=round(time.time() - self.t0, 1), peak_rss_mb=round(_rss_mb()))
            return {"config": {"seed": self.seed}, "records": [], "completed_rounds": 0}
        self.emit("loading")
        self.load()
        self.emit("loaded", load_s=round(self.load_s, 2), devices=self.devices, memory_level=memory_level(),
                  schedule={f"r{t + 1}": {c: self.sched[(t, c)] for c in self.node_by_cid} for t in range(self.rounds)})
        base = {}
        for name in STRATS:  # both federations start from B = 0, i.e. exactly the untuned model
            self.guard("eval")
            self.feds[name]["strategy"].evaluate_global(0)
            base[name] = self.feds[name]["strategy"].evals[-1]["per_domain_loss"]
        self.base = base["anchor_full"]
        identical = base["anchor_full"] == base["fedavg_ab_homo"]
        self.emit("untuned", per_domain=self.base, identical_start=identical,
                  eval_tokens_per_domain=LIVE["eval_blocks_per_domain"] * LIVE["seq_len"])
        for r in range(1, self.rounds + 1):
            for cid, (a, b) in self.script.items():
                if r == a:
                    self.command({"cmd": "unplug", "device": cid})
                if r == b + 1:
                    self.command({"cmd": "replug", "device": cid})
            while self.paused and not self.stopped:
                time.sleep(0.2)
            if self.stopped:
                break
            with self.lock:
                for dev, out in self.pending.items():
                    (self.unplugged.add if out else self.unplugged.discard)(dev)
                self.pending.clear()
                self.t = r
                unpl = sorted(self.unplugged)
            for name in STRATS:
                grid = self.feds[name]["grid"]
                for cid, node in self.node_by_cid.items():
                    if cid in unpl:
                        grid.kill_node(node)
                    else:
                        grid.killed.discard(node)  # plugged back in: the node rejoins the grid
            for cid in unpl:
                self.unplug_rounds.setdefault(cid, []).append(r)
            tr0 = time.time()
            self.emit("round_start", round=r, unplugged=unpl,
                      scheduled={c: self.sched[(r - 1, c)] for c in self.node_by_cid})
            for name in STRATS:
                fed = self.feds[name]
                s = fed["strategy"]
                t1 = time.time()
                msgs = s.configure_train(r, fed["arrays"], self.ConfigRecord(), fed["grid"])
                replies = fed["grid"].send_and_receive(msgs)
                fed["arrays"], _ = s.aggregate_train(r, replies)
                t2 = time.time()
                self.guard("eval")
                s.evaluate_global(r)
                rec = self._record(name, r, unpl, t2 - t1, time.time() - t2)
                self.records.append(rec)
                self.emit("round", **rec)
            self.emit("round_end", round=r, wall_s=round(time.time() - tr0, 2), memory_level=memory_level(),
                      rss_mb=round(_rss_mb()))
        result = {"config": {"seed": self.seed, "rounds": self.rounds, "live": LIVE, "strategies": list(STRATS),
                             "script": {k: list(v) for k, v in self.script.items()},
                             "forced_outage": "none (the judge or the script supplies the outage)"},
                  "provenance": prov, "untuned": self.base, "identical_start": identical,
                  "load_s": round(self.load_s, 2), "unplugged_rounds": self.unplug_rounds,
                  "completed_rounds": len({rec["round"] for rec in self.records}),
                  "records": self.records, "wall_s": round(time.time() - self.t0, 1), "peak_rss_mb": round(_rss_mb())}
        self.emit("done", completed_rounds=result["completed_rounds"], wall_s=result["wall_s"],
                  peak_rss_mb=result["peak_rss_mb"])
        return result


def parse_script(items: list[str]) -> dict:
    out = {}
    for it in items:
        dev, rng = it.split(":")
        a, b = (int(x) for x in rng.split("-"))
        out[dev] = (a, b)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--rounds", type=int, default=LIVE["rounds"])
    ap.add_argument("--threads", type=int, default=LIVE["threads"])
    ap.add_argument("--unplug", action="append", default=[], help="scripted unplug DEVICE:FIRST-LAST (1-based)")
    ap.add_argument("--out", help="write the run (config, provenance, per-round records) as JSON")
    ap.add_argument("--events-out", help="also write every event as a JSON line (recorded fallback)")
    ap.add_argument("--no-stdin", action="store_true", help="do not read commands from stdin")
    args = ap.parse_args()

    ev_file = open(args.events_out, "w") if args.events_out else None

    def sink(ev: dict) -> None:
        line = json.dumps(ev, allow_nan=False)
        print(line, flush=True)
        if ev_file:
            ev_file.write(line + "\n")
            ev_file.flush()

    eng = Engine(seed=args.seed, rounds=args.rounds, threads=args.threads, emit=sink,
                 script=parse_script(args.unplug))
    if not args.no_stdin:
        def reader() -> None:
            for line in sys.stdin:
                if line.strip():
                    try:
                        eng.command(json.loads(line))
                    except Exception as e:  # noqa: BLE001
                        eng.emit("error", message=f"bad command: {e}")
            eng.command({"cmd": "stop"})  # parent went away

        threading.Thread(target=reader, daemon=True).start()
    try:
        result = eng.run()
    except Exception as e:  # noqa: BLE001
        eng.emit("error", message=f"{type(e).__name__}: {e}", trace=traceback.format_exc()[-2000:])
        sys.exit(1)
    if args.out:
        Path(args.out).write_text(json.dumps(_clean(result), indent=1, allow_nan=False) + "\n")
    if ev_file:
        ev_file.close()


if __name__ == "__main__":
    main()
