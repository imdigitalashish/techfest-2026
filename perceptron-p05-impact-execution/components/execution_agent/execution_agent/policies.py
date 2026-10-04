"""Execution policies: pure functions of a DecisionContext -> child orders.

They don't import ABIDES, so they can be unit-tested and reused in other simulators.
Prices are integer cents; quantities are shares; the side is "SELL" or "BUY".
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np


@dataclass
class ChildOrder:
    kind: str                    # "MKT" | "LMT"
    qty: int
    price: Optional[int] = None  # required for LMT


@dataclass
class DecisionContext:
    t_ns: int
    slot: int
    n_slots: int
    slot_times_ns: Sequence[int]
    quantity: int
    filled: int
    side: str
    bids: List[Tuple[int, int]]          # [(price, qty)] best first
    asks: List[Tuple[int, int]]
    fills: List[Tuple[int, int, int]]    # [(t_ns, price, qty)]

    @property
    def remaining(self) -> int:
        return self.quantity - self.filled

    @property
    def is_final(self) -> bool:
        return self.slot >= self.n_slots - 1

    def opposite_book(self) -> List[Tuple[int, int]]:
        return self.bids if self.side == "SELL" else self.asks


class Policy:
    name = "base"

    def target_cum(self, ctx: DecisionContext) -> float:
        raise NotImplementedError

    def decide(self, ctx: DecisionContext) -> List[ChildOrder]:
        if ctx.remaining <= 0:
            return []
        if ctx.is_final:
            return [ChildOrder("MKT", ctx.remaining)]
        child = int(round(self.target_cum(ctx))) - ctx.filled
        child = max(0, min(child, ctx.remaining))
        return [ChildOrder("MKT", child)] if child > 0 else []


class TwapPolicy(Policy):
    """Equal slices per decision slot, executed with market orders (the textbook baseline)."""
    name = "TWAP"

    def target_cum(self, ctx):
        return ctx.quantity * (ctx.slot + 1) / ctx.n_slots


class VwapPolicy(Policy):
    """Slices follow a historical volume curve estimated on TRAINING seeds only."""
    name = "VWAP"

    def __init__(self, cum_profile: Sequence[float]):
        self.cum_profile = np.asarray(cum_profile, dtype=float)

    def target_cum(self, ctx):
        return ctx.quantity * float(self.cum_profile[min(ctx.slot, len(self.cum_profile) - 1)])


class ProbePolicy(Policy):
    """Random-size slices (system identification of our impact kernel; calibration only)."""
    name = "PROBE"

    def __init__(self, seed: int):
        self.rs = np.random.RandomState(seed)

    def decide(self, ctx):
        if ctx.remaining <= 0:
            return []
        if ctx.is_final:
            return [ChildOrder("MKT", ctx.remaining)]
        base = ctx.quantity / ctx.n_slots
        child = int(min(ctx.remaining, round(base * self.rs.uniform(0.0, 2.0))))
        return [ChildOrder("MKT", child)] if child > 0 else []


def propagator_qp_schedule(n: int, dt_s: float, inst_cost: float, g_tr: float, tau_s: float) -> np.ndarray:
    """Optimal slice fractions under a transient-impact (propagator) model.

    Expected cost of slices x (shares, sum Q) = sum_j x_j^2 * inst_cost
        + sum_{i<j} x_j x_i g_tr exp(-(t_j - t_i)/tau)    (discrete propagator cost)
    The permanent part adds a constant (sum x fixed), so it doesn't change the optimum.
    Minimise x^T A x subject to 1^T x = 1 and x >= 0 (active-set clipping).
    """
    t = np.arange(n) * dt_s
    lag = np.abs(t[:, None] - t[None, :])
    A = 0.5 * g_tr * np.exp(-lag / max(tau_s, 1e-9))
    np.fill_diagonal(A, inst_cost + 0.5 * g_tr)
    active = np.ones(n, dtype=bool)
    x = np.zeros(n)
    for _ in range(n):
        Ai = A[np.ix_(active, active)]
        w = np.linalg.solve(Ai, np.ones(active.sum()))
        xa = w / w.sum()
        if (xa >= 0).all():
            x[:] = 0
            x[active] = xa
            return x
        idx = np.where(active)[0]
        active[idx[xa < 0]] = False
    return np.full(n, 1.0 / n)


class ImpactAwarePolicy(Policy):
    """Impact-aware agent (IA).

    1. Schedule: propagator-QP optimal slices from our calibrated impact kernel
       (instantaneous cost + exponentially decaying transient impact).
    2. Feedback: estimates its own outstanding transient impact
       I_hat(t) = sum_i q_i g_tr exp(-(t - t_i)/tau) and slows down while the book
       is still displaced by its own earlier trades, catching up when it has recovered.
    3. Tactic: marketable limit order that takes at most `max_levels` price levels
       of the opposite book; the unfilled rest posts at that price until the next slot.
    The final slot sweeps the remainder with a market order (forced completion).

    ref_mode: "post_trade" (legacy, used in E3-E6) compares the pre-trade own impact with the
    *post*-trade steady state, so at average-rate trading excess = exp(-dt/tau) - 1 (about -0.39 at
    dt = 30 s, tau = 60 s): the rule acts as a ~1.2x speed-up, not a brake (code review 4 Oct: eval/results/code-review-2026-10-04.md).
    "pre_trade" compares like with like (steady-state excess = 0).
    """
    name = "IA"

    def __init__(self, n_slots: int, dt_s: float, inst_cost: float, g_tr: float, tau_s: float,
                 beta: float = 0.5, max_levels: int = 1, use_qp: bool = True, use_feedback: bool = True,
                 use_limit: bool = True, catchup_tol: float = 0.15, ref_mode: str = "post_trade"):
        assert ref_mode in ("post_trade", "pre_trade")
        self.ref_mode = ref_mode
        self.p = dict(inst_cost=inst_cost, g_tr=g_tr, tau_s=tau_s, beta=beta, max_levels=max_levels,
                      use_qp=use_qp, use_feedback=use_feedback, use_limit=use_limit, catchup_tol=catchup_tol)
        w = propagator_qp_schedule(n_slots, dt_s, inst_cost, g_tr, tau_s) if use_qp else np.full(n_slots, 1.0 / n_slots)
        self.cum = np.cumsum(w)
        self.g_tr, self.tau_s = g_tr, tau_s
        self.beta, self.max_levels = beta, max_levels
        self.use_feedback, self.use_limit, self.catchup_tol = use_feedback, use_limit, catchup_tol

    def own_impact(self, ctx) -> float:
        return sum(q * self.g_tr * np.exp(-(ctx.t_ns - t) / 1e9 / self.tau_s) for t, _, q in ctx.fills)

    def decide(self, ctx):
        if ctx.remaining <= 0:
            return []
        if ctx.is_final:
            return [ChildOrder("MKT", ctx.remaining)]
        target = ctx.quantity * self.cum[ctx.slot]
        base = max(0.0, target - ctx.filled)
        if self.use_feedback and ctx.slot > 0:
            # Reference: steady-state own impact when trading at the average rate.
            rate = ctx.quantity / ctx.n_slots
            dt = (ctx.slot_times_ns[1] - ctx.slot_times_ns[0]) / 1e9
            decay = np.exp(-dt / self.tau_s)
            ref = rate * self.g_tr / max(1e-9, 1 - decay)
            if self.ref_mode == "pre_trade":
                ref *= decay
            excess = (self.own_impact(ctx) - ref) / max(ref, 1e-9)
            behind = (target - ctx.filled) / ctx.quantity
            mult = 1.0 - self.beta * float(np.clip(excess, -1.0, 1.0))
            if behind > self.catchup_tol:
                mult = max(mult, 1.0)
            base *= mult
        child = int(round(min(base, ctx.remaining)))
        if child <= 0:
            return []
        if not self.use_limit:
            return [ChildOrder("MKT", child)]
        book = ctx.opposite_book()
        if not book:
            return []
        limit_px = int(book[: self.max_levels][-1][0])
        return [ChildOrder("LMT", child, limit_px)]


def make_policy(spec: Dict, n_slots: int, dt_s: float) -> Policy:
    kind = spec["kind"]
    if kind == "TWAP":
        return TwapPolicy()
    if kind == "VWAP":
        return VwapPolicy(spec["cum_profile"])
    if kind == "PROBE":
        return ProbePolicy(spec.get("probe_seed", 0))
    if kind == "IA":
        kw = {k: v for k, v in spec.items() if k not in ("kind", "label")}
        return ImpactAwarePolicy(n_slots=n_slots, dt_s=dt_s, **kw)
    raise ValueError(kind)
