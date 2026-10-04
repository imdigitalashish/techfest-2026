"""P7 demo engine: a thin wrapper over the COMMITTED simulator, policies and planner (nothing is re-implemented).

LiveRun   two allocators on ONE shared DemandTrace (common random numbers), plus shocks injected by the judge.
BatchRun  a whole committed episode (shock day, long week, NYC July 3-4) recomputed live, then compared with the
          committed row in eval/results/*/episodes.csv (parity).

Shock injection adds requests only at steps >= the current step. Every zone's request prefix (the part the FIFO
pointers head/tail already cover) is therefore unchanged. Each core's per-zone arrays are rebuilt from the new
trace by the committed DispatchCore constructor, and its unit state, head and tail are kept.
"""
from __future__ import annotations

import csv
import json
import threading
import time
from dataclasses import replace
from pathlib import Path

import numpy as np

from architecture.contracts.contracts import DemandTrace
from components.forecasting.forecasters import OracleForecaster
from components.policies.policies import make_policy
from components.scenarios.scenarios import SCENARIOS, build_trace
from components.simulator.core import DispatchCore
from eval.harness import NYC, WIN, episode_meta

P7 = Path(__file__).resolve().parents[1]
DEMO = Path(__file__).resolve().parent
DATA = DEMO / "data"
RESULTS = P7 / "eval" / "results"
NYC_EXPORT = DATA / "nyc_jul03-04_r200.npz"
SHOCK = SCENARIOS["shock"]   # committed shock shape: shock_size^2 block, +shock_extra x zone-mean rate, shock_duration steps
DEMO_SEED = 7000             # demo seeds 7000+ appear in no committed result or registration
N_AGENTS = 40
CELLS_L, CELLS_P = (1, 2, 4, 8), (3, 10)   # the committed (L, P) grid (eval/results/phase-v2)
RULES = ("greedy", "reactive", "static")
BRAINS = ("mpc-ewma", "mpc-queue", "mpc-ewma@trust=0.5", "oracle")


def best_rules() -> dict[tuple[int, int], str]:
    """Best rule per (L, P) cell, as chosen by the committed phase-v2 analysis (by mean; exploratory)."""
    with open(RESULTS / "phase-v2" / "phase_summary.csv") as f:
        return {(int(r["L"]), int(r["P"])): r["best_rule"] for r in csv.DictReader(f)}


def committed_row(run: str, policy: str, seed: int, scenario: str | None = None) -> dict | None:
    with open(RESULTS / run / "episodes.csv") as f:
        for r in csv.DictReader(f):
            if r["policy"] == policy and int(r["seed"]) == seed and (scenario is None or r["scenario"] == scenario):
                return r
    return None


# ---------------------------------------------------------------- trace surgery (shock injection)
def inject_shock(trace: DemandTrace, t0: int, zones: list[int], extra: float, duration: int,
                 rng: np.random.Generator) -> DemandTrace:
    """New trace = old trace + Poisson(extra) requests per step in `zones` for steps t0 .. t0+duration-1.
    Destinations follow the trace's static OD map, sampled the way build_trace samples them."""
    T, Z = trace.counts.shape
    t1 = min(T, t0 + duration)
    rates = trace.rates.copy()
    rates[t0:t1, zones] += extra
    add = np.zeros_like(trace.counts)
    if t1 > t0:
        add[t0:t1, zones] = rng.poisson(extra, size=(t1 - t0, len(zones)))
    counts = (trace.counts + add).astype(np.int32)
    cell_old = np.repeat(np.arange(T * Z), trace.counts.reshape(-1))
    cell_add = np.repeat(np.arange(T * Z), add.reshape(-1))
    origin = cell_add % Z
    cdf = np.cumsum(trace.od_prob, axis=1)
    cdf[:, -1] = 1.0
    u = rng.random(cell_add.size)
    dest_add = np.empty(cell_add.size, dtype=np.int16)
    for z in np.unique(origin):
        m = origin == z
        dest_add[m] = np.searchsorted(cdf[z], u[m], side="right")
    # within one (step, zone) cell the existing requests keep their order and the injected ones follow
    order = np.lexsort((np.r_[np.zeros(cell_old.size), np.ones(cell_add.size)], np.r_[cell_old, cell_add]))
    req_dest = np.r_[trace.req_dest, dest_add][order].astype(np.int16)
    flat = counts.reshape(-1)
    offsets = (np.cumsum(flat, dtype=np.int64) - flat).reshape(T, Z)
    return DemandTrace(rates=rates, counts=counts, req_dest=req_dest, offsets=offsets, od_prob=trace.od_prob,
                       change_points=list(trace.change_points), name=trace.name)


# ---------------------------------------------------------------- one allocator on the shared trace
class Panel:
    def __init__(self, name: str, trace: DemandTrace, meta: dict, seed: int, L: int, P: int):
        self.name = name
        self.core = DispatchCore(trace, n_agents=N_AGENTS, patience=P, init_seed=seed,
                                 init_shares=meta["hist_shares"], move_steps_per_hop=L)
        self.pol = make_policy(name)
        self.pol.reset(meta if name.startswith("oracle") else dict(meta, rates=None))   # as eval/harness.py
        self.plan = None
        planner = getattr(self.pol, "planner", None)
        if planner is not None:   # keep the plan the policy just executed (dual prices, solve time); no re-solve
            solve = planner.solve

            def capture(*a, **k):
                self.plan = solve(*a, **k)
                return self.plan
            planner.solve = capture
        T = trace.horizon
        self.served, self.lost, self.arr, self.empty = (np.zeros(T, np.int64) for _ in range(4))

    def step(self):
        st = self.core.state()
        info = self.core.step(self.pol.act(st))
        self.pol.observe(info)
        t = st.t
        self.served[t], self.lost[t], self.arr[t] = info.served.sum(), info.lost.sum(), info.arrivals.sum()
        self.empty[t] = info.empty_moves
        return info

    def retarget(self, trace: DemandTrace) -> None:
        c = self.core
        tmp = DispatchCore(trace, n_agents=c.K, patience=c.P, move_steps_per_hop=c.hop_steps)
        for z in range(c.Z):   # FIFO pointers only cover requests that arrived before the injection step
            n = int(c.tail[z])
            if not (np.array_equal(tmp.times_z[z][:n], c.times_z[z][:n])
                    and np.array_equal(tmp.dest_z[z][:n], c.dest_z[z][:n])):
                raise RuntimeError("shock injection would rewrite the past")
        c.trace, c.times_z, c.dest_z = trace, tmp.times_z, tmp.dest_z
        fc = getattr(self.pol, "fc", None)
        if isinstance(fc, OracleForecaster):
            fc.rates = trace.rates   # the true-rate planner sees the shock from its onset, never before

    def units(self) -> dict:
        c = self.core
        return dict(zone=c.zone.tolist(), status=c.status.tolist(), eta=c.eta.tolist(), q=(c.tail - c.head).tolist())

    def frame(self, info) -> dict:
        f = self.units()
        f.update(srv=info.served.tolist(), lost=info.lost.tolist(), empty=int(info.empty_moves))
        if self.plan is not None:
            zv = self.plan.zone_value
            f["price"] = None if zv is None else [round(float(x), 3) for x in zv]
            f["ms"] = round(float(self.plan.solve_ms), 3)
        return f

    def totals(self, t: int) -> dict:
        S, A = int(self.served[:t].sum()), int(self.arr[:t].sum())
        return dict(served=S, lost=int(self.lost[:t].sum()), arrivals=A, served_frac=S / max(1, A),
                    empty_per_srv=int(self.empty[:t].sum()) / max(1, S))


# ---------------------------------------------------------------- live city: the judge's shocks
class LiveRun:
    def __init__(self, L: int = 1, P: int = 10, rule: str = "auto", brain: str = "mpc-ewma", drift: bool = False,
                 seed: int = DEMO_SEED, start: int = 240, horizon: int = 1440):
        if L not in CELLS_L or P not in CELLS_P:
            raise ValueError("L and P must be a committed grid cell")
        if rule == "auto":
            rule = "reactive" if drift else best_rules()[(L, P)]   # drift: the pre-registered shock+drift reference
        if rule not in RULES or brain not in BRAINS:
            raise ValueError("unknown rule or brain")
        self.L, self.P, self.rule, self.brain, self.drift, self.seed = L, P, rule, brain, bool(drift), int(seed)
        self.cfg = replace(SCENARIOS["drift" if drift else "stationary"], horizon=horizon)
        self.trace = build_trace(self.cfg, self.seed)
        meta = episode_meta(self.cfg, self.trace)
        meta.update(hop_steps=L, patience=P)
        self.panels = [Panel(rule, self.trace, meta, self.seed, L, P), Panel(brain, self.trace, meta, self.seed, L, P)]
        self.shocks: list[dict] = []
        self.lock = threading.Lock()
        self.t = 0
        for _ in range(start):   # warm up to the start clock (04:00 by default) without frames
            self._step()

    @property
    def done(self) -> bool:
        return self.t >= self.trace.horizon

    def _step(self):
        infos = [p.step() for p in self.panels]
        if not np.array_equal(infos[0].arrivals, infos[1].arrivals):
            raise RuntimeError("common random numbers violated")
        self.t += 1
        return infos

    def snapshot(self) -> dict:
        return dict(t=self.t, panels=[p.units() for p in self.panels])

    def advance(self, n: int) -> list[dict]:
        frames = []
        with self.lock:
            for _ in range(max(0, int(n))):
                if self.done:
                    break
                t = self.t
                infos = self._step()
                frames.append(dict(t=t, arr=infos[0].arrivals.tolist(),
                                   panels=[p.frame(i) for p, i in zip(self.panels, infos)]))
        return frames

    def shock(self, zone: int, size: float = 1.0) -> dict:
        with self.lock:
            G, s = self.cfg.grid, SHOCK.shock_size
            r, c = divmod(int(zone), G)
            r0, c0 = min(max(r, 0), G - s), min(max(c, 0), G - s)
            zones = [(r0 + i) * G + (c0 + j) for i in range(s) for j in range(s)]
            extra = float(size) * SHOCK.shock_extra * self.cfg.total_rate / (G * G)
            t0 = self.t
            rng = np.random.default_rng([self.seed, 99, t0, zones[0], len(self.shocks)])
            new = inject_shock(self.trace, t0, zones, extra, SHOCK.shock_duration, rng)
            for p in self.panels:
                p.retarget(new)
            self.trace = new
            sh = dict(t0=t0, zones=zones, size=float(size), extra_per_zone=extra,
                      end=min(self.trace.horizon, t0 + SHOCK.shock_duration), window=WIN)
            self.shocks.append(sh)
            return sh

    def stats(self) -> dict:
        t = self.t
        out = dict(t=t, done=self.done, panels=[p.totals(t) for p in self.panels], shocks=[])
        for sh in self.shocks:
            a, b = sh["t0"], min(t, sh["t0"] + WIN)
            out["shocks"].append(dict(sh, lost=[int(p.lost[a:b].sum()) for p in self.panels],
                                      arrivals=int(self.panels[0].arr[a:b].sum()), steps=b - a,
                                      complete=t >= sh["t0"] + WIN))
        if self.shocks:
            a = self.shocks[0]["t0"]
            out["lost_since_first_shock"] = [int(p.lost[a:t].sum()) for p in self.panels]
        return out

    def describe(self) -> dict:
        return dict(L=self.L, P=self.P, rule=self.rule, brain=self.brain, drift=self.drift, seed=self.seed,
                    horizon=self.trace.horizon, grid=self.cfg.grid, n_agents=N_AGENTS, scenario=self.cfg.name,
                    shock=dict(size=SHOCK.shock_size, extra=SHOCK.shock_extra, duration=SHOCK.shock_duration, window=WIN))


# ---------------------------------------------------------------- whole committed episodes, recomputed live
def load_nyc(path: Path = NYC_EXPORT) -> tuple[DemandTrace, dict, dict]:
    """The committed export of build_nyc_trace(July 3-4, train July 1-2, seed=200); see demo/export_nyc.py."""
    z = np.load(path, allow_pickle=False)
    counts = z["counts"].astype(np.int32)
    T, Z = counts.shape
    flat = counts.reshape(-1)
    offsets = (np.cumsum(flat, dtype=np.int64) - flat).reshape(T, Z)
    trace = DemandTrace(rates=np.zeros((T, Z)), counts=counts, req_dest=z["req_dest"].astype(np.int16),
                        offsets=offsets, od_prob=z["od_prob"], change_points=[], name="nyc-jul03-04")
    meta = dict(grid=5, n_zones=Z, od_prob=z["od_prob"], profile=z["profile"], hist_shares=z["hist_shares"],
                init_level=z["init_level"], init_level_raw=z["init_level_raw"], rates=None)
    info = json.loads(str(z["info"]))
    return trace, meta, info


class BatchRun:
    """kind: 'shock-day' (mvp-v2 row), 'week' (long-week-v2 row) or 'nyc' (nyc-v2 row); L=1, P=10 as committed."""
    SPEC = {"shock-day": ("mvp-v2", "shock", ("greedy", "reactive", "mpc-ewma")),
            "week": ("long-week-v2", "long-week", ("greedy", "reactive", "mpc-ewma")),
            "nyc": ("nyc-v2", "nyc-jul03-04", ("static", "greedy", "reactive", "mpc-ewma"))}

    def __init__(self, kind: str, seed: int = 200, show: tuple[str, ...] | None = None):
        self.kind, self.seed = kind, int(seed)
        self.run_dir, self.scenario, self.policies = self.SPEC[kind]
        self.info: dict = {}
        if kind == "nyc":
            trace, meta, self.info = load_nyc()
            if self.info["seed"] != self.seed:
                raise ValueError("only the exported replicate is available offline")
            self.event = NYC[self.scenario][2]
            self.day = 1440
        else:
            cfg = SCENARIOS[self.scenario]
            if kind == "shock-day":
                cfg = replace(cfg, horizon=1440)
            trace = build_trace(cfg, self.seed)
            meta = episode_meta(cfg, trace)
            self.event, self.day = None, cfg.day
        meta.update(hop_steps=1, patience=10)
        self.trace = trace
        self.T = trace.horizon
        self.panels = [Panel(p, trace, meta, self.seed, 1, 10) for p in self.policies]
        self.show = [self.policies.index(p) for p in (show or self.policies)]
        self.frames: list[dict] = []
        self.t, self.done, self.error, self.summary = 0, False, None, None
        self.lock = threading.Lock()
        self.wall = 0.0

    def keep(self, t: int) -> bool:
        if self.event is not None and self.event[0] - 90 <= t < self.event[1] + 30:
            return True   # NYC: every minute around the July 4 night window
        return t % 10 == 9 or t == self.T - 1

    def run(self) -> None:
        try:
            t0 = time.perf_counter()
            cum = np.zeros((len(self.panels), 3), np.int64)
            while self.t < self.T:
                for p in self.panels:
                    p.step()
                t = self.t
                self.t += 1
                cum += [[p.served[t], p.lost[t], p.arr[t]] for p in self.panels]
                if self.keep(t):
                    fr = dict(t=t, cum=cum.tolist(),
                              panels=[dict(zone=self.panels[i].core.zone.tolist(),
                                           status=self.panels[i].core.status.tolist(),
                                           q=(self.panels[i].core.tail - self.panels[i].core.head).tolist())
                                      for i in self.show])
                    with self.lock:
                        self.frames.append(fr)
            self.wall = time.perf_counter() - t0
            self.summary = self.finish()
        except Exception as e:  # surfaced to the UI and to the smoke test
            self.error = repr(e)
        self.done = True

    def start(self) -> "BatchRun":
        threading.Thread(target=self.run, daemon=True).start()
        return self

    def metrics(self, p: Panel) -> dict:
        """The per-episode metrics of eval/harness.py run_episode: served_frac, shock_lost, daily_served, event_lost."""
        S, A = int(p.served.sum()), int(p.arr.sum())
        m = dict(served_frac=S / max(1, A), lost=int(p.lost.sum()), arrivals=A)
        on = [c for c in self.trace.change_points if c.kind == "shock_on"]
        if on:
            m["shock_lost"] = float(np.mean([int(p.lost[c.t:c.t + WIN].sum()) for c in on]))
        if self.event is not None:
            a, b = self.event
            m["event_lost"] = int(p.lost[a:b].sum())
            m["event_served"] = float(p.served[a:b].sum() / max(1, p.arr[a:b].sum()))
        D = self.day
        if self.T // D >= 2:
            m["daily_served"] = [round(float(p.served[d * D:(d + 1) * D].sum() / max(1, p.arr[d * D:(d + 1) * D].sum())), 5)
                                 for d in range(self.T // D)]
        return m

    def finish(self) -> dict:
        out = dict(kind=self.kind, seed=self.seed, policies=list(self.policies), wall_s=round(self.wall, 2),
                   metrics={}, parity={}, row=f"eval/results/{self.run_dir}/episodes.csv")
        for p in self.panels:
            m = self.metrics(p)
            out["metrics"][p.name] = m
            row = committed_row(self.run_dir, p.name, self.seed, self.scenario)
            if row is None:
                out["parity"][p.name] = None
                continue
            chk = {"served_frac": abs(float(row["served_frac"]) - m["served_frac"]) <= 1e-12}
            if "shock_lost" in m and row.get("shock_lost"):
                chk["shock_lost"] = float(row["shock_lost"]) == m["shock_lost"]
            if "event_lost" in m and row.get("event_lost"):
                chk["event_lost"] = int(float(row["event_lost"])) == m["event_lost"]
            if "daily_served" in m and row.get("daily_served"):
                chk["daily_served"] = json.loads(row["daily_served"]) == m["daily_served"]
            out["parity"][p.name] = dict(checks=chk, committed_served_frac=float(row["served_frac"]))
        checked = [v for v in out["parity"].values() if v]
        out["parity_all"] = bool(checked) and all(all(v["checks"].values()) for v in checked)
        return out

    def static(self) -> dict:
        return dict(kind=self.kind, seed=self.seed, T=self.T, info=self.info, event=self.event,
                    policies=list(self.policies), show=[self.policies[i] for i in self.show])

    def poll(self, k: int, limit: int = 400) -> dict:
        with self.lock:
            fr = self.frames[k:k + limit]
            n = len(self.frames)
        return dict(self.static(), t=self.t, frames=fr, next=k + len(fr), available=n,
                    done=self.done and k + len(fr) >= n, error=self.error, summary=self.summary if self.done else None)


def batch_worker(kind: str, seed: int, show: tuple, q) -> None:
    """Child-process entry point (demo/server.py): recompute one episode and stream its frames back, so the
    live city in the server process never waits for the interpreter lock."""
    import os
    try:
        os.nice(10)
    except OSError:
        pass
    try:
        r = BatchRun(kind, seed, show=show)
    except Exception as e:
        q.put(("done", None, repr(e), 0.0))
        return
    q.put(("static", r.static()))
    th = threading.Thread(target=r.run, daemon=True)
    th.start()
    sent = 0
    while th.is_alive() or sent < len(r.frames):
        th.join(timeout=0.25)
        with r.lock:
            new = r.frames[sent:]
        if new:
            q.put(("frames", new, r.t))
            sent += len(new)
    q.put(("done", r.summary, r.error, r.wall))
