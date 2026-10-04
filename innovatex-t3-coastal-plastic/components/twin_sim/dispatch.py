"""C10 dispatch policies at EQUAL crew-hours (n_crews x shift_h every day, one site per crew-shift).

P0 fixed schedule (status quo, area-weighted rotation, fixed 08:30-16:30 IST shift)
P1 fill-threshold: crews to the two fullest booms by SIMULATED fill sensor, fixed shift
P2 forecast- and tide-aware: kg-at-risk from sensed fill + day-ahead forecast arrivals, weighted by
   forecast bypass/overflow risk; shift start chosen inside daylight to maximise predicted access
   (low water, slack/ebb current) from the harmonic tide. Knobs: p2_knobs.json (autoresearch ratchet)."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

import numpy as np

from . import risk_forecaster as RF
from ._paths import C

N_CREWS, SHIFT_H = 2, 8
FIXED_START_UTC = 3                         # 08:30 IST
DAYLIGHT_STARTS_UTC = [1, 2, 3, 4, 5]       # 06:30 .. 10:30 IST starts; shifts end by 18:30 IST
P0_CYCLE = [2, 1, 2, 3, 2, 1, 0]            # crew-2 weekly rotation (crew-1 always at site 0 = Mithi)
KNOBS_PATH = Path(__file__).with_name("p2_knobs.json")


@dataclass
class DayCtx:
    day: int
    t0: int
    fill_obs: np.ndarray    # (D, S) SIMULATED sensed fill fraction at 00 UTC
    fc: dict
    S: int


def crew_matrix(assign: list, D: int, S: int) -> np.ndarray:
    W = np.zeros((D, S, 24))
    for di, crews in enumerate(assign):
        hours = 0
        for s, start, h in crews:
            assert 0 <= start and start + h <= 24
            W[di, s, start:start + h] += 1
            hours += h
        assert hours == N_CREWS * SHIFT_H, "equal crew-hours violated"
    return W


def p0(ctx: DayCtx):
    a = [(0, FIXED_START_UTC, SHIFT_H), (P0_CYCLE[ctx.day % 7], FIXED_START_UTC, SHIFT_H)]
    return [a] * ctx.fill_obs.shape[0]


def p1(ctx: DayCtx):
    out = []
    for f in ctx.fill_obs:
        top = np.argsort(-f, kind="stable")[:N_CREWS]
        out.append([(int(s), FIXED_START_UTC, SHIFT_H) for s in top])
    return out


def load_knobs() -> dict:
    return json.loads(KNOBS_PATH.read_text())


def p2_factory(fc: dict, knobs: dict | None = None):
    k = dict(load_knobs(), **(knobs or {}))
    starts = list(k["starts_utc"])
    rate, cap = fc["clear_rate"], fc["capacity_kg"]

    def p2(ctx: DayCtx):
        d = ctx.day
        acc = fc["access"][d]                                   # (24, S) predicted access
        win = np.array([acc[h:h + SHIFT_H].sum(0) for h in starts])
        if k["tide_aware"]:
            bi = win.argmax(0)
            best_start = np.array(starts)[bi]
            acc_sum = win.max(0)
        else:
            best_start = np.full(ctx.S, FIXED_START_UTC)
            acc_sum = acc[FIXED_START_UTC:FIXED_START_UTC + SHIFT_H].sum(0)
        clear_cap = rate * acc_sum
        out = []
        for f in ctx.fill_obs:
            p_over, _ = RF.p_overflow(fc, d, f)
            risk = (k["w_stock"] + k["w_bypass"] * fc["p_bypass"][d] + k["w_over"] * p_over
                    + k["loss_weight"] * (1.0 - fc["e_cap"][d]))
            arr = fc["arr24"][d] if k["arr_horizon"] == 24 else fc["arr48"][d]
            remaining = f * cap + k["w_arrival"] * fc["e_cap"][d] * arr
            crews = []
            for _ in range(N_CREWS):
                val = np.minimum(remaining, clear_cap) * risk
                s = int(np.argmax(val))
                crews.append((s, int(best_start[s]), SHIFT_H))
                remaining[s] = max(remaining[s] - clear_cap[s], 0.0)
            out.append(crews)
        return out
    return p2


def make_policy(name: str, fc: dict, knobs: dict | None = None):
    return {"P0": lambda f: p0, "P1": lambda f: p1, "P2": lambda f: p2_factory(f, knobs)}[name](fc)


def dispatch_plan(policy_id: str, day: int, crews: list, fc: dict, site_ids: list, fill_obs) -> "C.DispatchPlan":
    t0 = fc["t"][day * 24].to_pydatetime()
    asg = []
    for c, (s, start, h) in enumerate(crews):
        acc = fc["access"][day][start:start + h, s].sum()
        exp = min(float(fill_obs[s] * fc["capacity_kg"][s]), fc["clear_rate"] * float(acc))
        asg.append(C.Assignment(crew_id=f"crew-{c + 1}", site_id=site_ids[s], start=t0 + timedelta(hours=start),
                                end=t0 + timedelta(hours=start + h), expected_cleared_kg=round(max(exp, 0.0), 1),
                                reason=f"{policy_id}: sensed fill {fill_obs[s]:.2f}, predicted access {acc:.1f}/{h} h"))
    return C.DispatchPlan(plan_id=f"{policy_id}-{t0:%Y-%m-%d}", issued_at=t0, policy_id=policy_id, assignments=asg,
                          objective={"crew_hours": float(N_CREWS * SHIFT_H)})
