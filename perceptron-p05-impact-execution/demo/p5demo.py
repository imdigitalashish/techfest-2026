"""Shared demo helpers: run one ABIDES twin arm through the committed P5 code and extract what the page shows.

Everything numeric goes through committed functions: sim_env.world.run_world (the world and its RNG coupling),
sim_env.twins.make_factory, execution_agent.policies.make_policy, and the tca metrics. The only addition is
`top5_pre_trade_identity`, which extends tca.pre_window_exact from the top of book to the five levels logged here.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time

import numpy as np

DEMO = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DEMO)
for _c in ("sim_env", "execution_agent", "tca", "impact_model"):
    _p = os.path.join(ROOT, "components", _c)
    if _p not in sys.path:
        sys.path.insert(0, _p)
if os.path.join(ROOT, "eval") not in sys.path:
    sys.path.insert(0, os.path.join(ROOT, "eval"))

import sim_env  # noqa: E402,F401  (ABIDES path setup)
from sim_env import world as W  # noqa: E402
from sim_env.twins import make_factory  # noqa: E402
from sim_env.world import TICKER, ns_at, run_world  # noqa: E402
from execution_agent.policies import TwapPolicy, make_policy  # noqa: E402
from tca import decompose_is, impact_path, implementation_shortfall, pre_window_exact  # noqa: E402
from run_experiment import CFG  # noqa: E402

DEPTH = 5
SIDE = CFG["side"]
START, END = ns_at(CFG["start"]), ns_at(CFG["end"])
OPEN = ns_at("09:30:00")
DT_S = (END - START) / 1e9 / CFG["n_slots"]
GRID = START + np.arange(0, 1801, dtype=np.int64) * 1_000_000_000   # run_experiment's impact grid
MID_GRID = OPEN + np.arange(0, 2101, dtype=np.int64) * 1_000_000_000  # 09:30:00 .. 10:05:00, 1 s
LADDER_DT = 2
LADDER_GRID = MID_GRID[::LADDER_DT]
POLICY_FILE = os.path.join(ROOT, "eval", "policies", "e8_ablation.json")  # E8/E10 arms; IA_sched_only == E6's


def ia_spec():
    import json
    return next(s for s in json.load(open(POLICY_FILE)) if s["label"] == "IA_sched_only")


class _Capture:
    """Stands in for abides_core.abides inside sim_env.world and keeps the last end_state (book log)."""

    def __init__(self, real):
        self.real, self.last = real, None

    def run(self, *a, **k):
        self.last = self.real.run(*a, **k)
        return self.last

    def __getattr__(self, name):
        return getattr(self.real, name)


if not isinstance(W.abides, _Capture):
    W.abides = _Capture(W.abides)
_CAP = W.abides
_WORK = tempfile.mkdtemp(prefix="p5demo_")   # ABIDES writes ./log/<run>; keep that out of the repo


def mem_level():
    try:
        return int(subprocess.run(["sysctl", "-n", "kern.memorystatus_level"], capture_output=True,
                                  text=True, timeout=5).stdout.strip())
    except Exception:
        return None


def _ladder(book_log2):
    n = len(book_log2)
    t = np.fromiter((d["QuoteTime"] for d in book_log2), dtype=np.int64, count=n)
    L = np.zeros((n, 4, DEPTH), dtype=np.int64)   # bid px, bid qty, ask px, ask qty (0 = empty level)
    for i, d in enumerate(book_log2):
        b, a = d["bids"], d["asks"]
        if len(b):
            b = np.asarray(b)[:DEPTH]
            L[i, 0, :len(b)], L[i, 1, :len(b)] = b[:, 0], b[:, 1]
        if len(a):
            a = np.asarray(a)[:DEPTH]
            L[i, 2, :len(a)], L[i, 3, :len(a)] = a[:, 0], a[:, 1]
    return t, L


def run_arm(seed: int, spec, qty: int, rng_sync: str) -> dict:
    """One world: spec=None is the null twin (an ExecutionAgent with quantity 0, as in twins.run_null)."""
    pol = TwapPolicy() if spec is None else make_policy(spec, CFG["n_slots"], DT_S)
    fac = make_factory(pol, SIDE, qty if spec is not None else 0, CFG["start"], CFG["end"], CFG["n_slots"])
    cwd, t0 = os.getcwd(), time.time()
    os.chdir(_WORK)
    try:
        res = run_world(seed, fac, end_time=CFG["end_time"], book_log_depth=DEPTH, rng_sync=rng_sync)
        es, _CAP.last = _CAP.last, None
        tb, L = _ladder(es["agents"][0].order_books[TICKER].book_log2)
        del es
    finally:
        os.chdir(cwd)
        shutil.rmtree(os.path.join(_WORK, "log"), ignore_errors=True)
    return dict(res=res, tb=tb, L=L, wall=time.time() - t0)


def top5_pre_trade_identity(a: dict, b: dict, start_ns: int = START):
    """Event-level identity of every logged top-5 book state before start_ns: (identical events, total events)."""
    ma, mb = a["tb"] < start_ns, b["tb"] < start_ns
    na, nb = int(ma.sum()), int(mb.sum())
    n = min(na, nb)
    same = (a["tb"][:n] == b["tb"][:n]) & (a["L"][:n] == b["L"][:n]).all(axis=(1, 2))
    return int(same.sum()), max(na, nb)


def pair_stats(null: dict, tr: dict) -> dict:
    """Twin-gap path and cost terms for one treatment arm against its null twin (all via committed tca code)."""
    rec = tr["res"].agent_record
    arrival = float(null["res"].mid_at(np.array([START]))[0])
    path = impact_path(tr["res"], null["res"], GRID, SIDE)
    is_ = implementation_shortfall(rec["fills"], arrival, SIDE)
    dec = decompose_is(rec["fills"], [d[0] for d in rec["decisions"]], arrival, SIDE, tr["res"], null["res"])
    k, n = top5_pre_trade_identity(tr, null)
    hn, ht = null["res"].holdings_by_type, tr["res"].holdings_by_type
    hold = {k_: int(ht.get(k_, 0) - hn.get(k_, 0)) for k_ in sorted(set(hn) | set(ht)) if k_ != "ExecutionAgent"}
    return dict(path=path, arrival=arrival, t1=float(path[1200]), is_bps=float(is_["is_bps"]),
                drift_bps=dec["drift_bps"], own_bps=dec["own_impact_bps"], instant_bps=dec["instant_bps"],
                filled=int(rec["filled"]), n_fills=len(rec["fills"]), fills=rec["fills"],
                ident=[k, n], ident_ok=bool(k == n and n > 0),
                top1_exact=bool(pre_window_exact(tr["res"], null["res"], START)), hold=hold)


def half_cents(x: np.ndarray) -> list:
    """Mids and gaps are multiples of 0.5 cent: store 2x as exact ints (None for an empty book side)."""
    return [None if not np.isfinite(v) else int(round(2 * v)) for v in np.asarray(x, float)]


def world_view(w: dict, base: int) -> dict:
    """Mid path (1 s) and top-5 ladder (2 s) from 09:30 to 10:05; ladder prices relative to `base` cents."""
    mid = w["res"].mid_at(MID_GRID)
    idx = np.searchsorted(w["tb"], LADDER_GRID, side="right") - 1
    L = w["L"][np.clip(idx, 0, None)].copy()
    L[idx < 0] = 0
    px = L[:, [0, 2], :]
    L[:, [0, 2], :] = np.where(px > 0, px - base, -99999)
    return dict(mid2=half_cents(mid), lad=L.reshape(len(L), -1).tolist())


def fills_view(fills) -> list:
    return [[round((t - OPEN) / 1e9, 3), int(p), int(q)] for t, p, q in fills]
