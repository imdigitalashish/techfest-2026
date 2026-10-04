"""C8/C9 — Allocators. Every policy maps FleetState -> (K,) target zones (Policy protocol).

Rule-based baselines (C9):
  static    rebalance idle units toward HISTORICAL average demand shares (a fixed static policy)
  greedy    decentralised local rule: surplus idle units hop to the 4-neighbour with the largest unmet queue
  reactive  proportional rebalancing toward the last-30-step observed demand shares (strongest rule)
Look-ahead (C6 planner + C5 forecaster + C4 detector):
  mpc-ewma  MPC on a deseasonalised EWMA forecast (look-ahead, no change detection)
  mpc-cusum MPC on the change-aware forecast (CUSUM restart + slow EWMA)  <- spike
  oracle    MPC on the TRUE future rates (clairvoyant reference for regret)
"""
from __future__ import annotations

import numpy as np

from architecture.contracts.contracts import FleetState, Forecast, StepInfo
from components.coordinator.assign import flows_to_targets, transport_flows
from components.forecasting.forecasters import (ChangeAwareForecaster, EWMAForecaster,
                                                MovingAverageForecaster, OracleForecaster)
from components.detection.detectors import PoissonCusum
from components.planner.mpc import MPCPlanner, grid_edges


class _Base:
    name = "base"

    def reset(self, meta: dict) -> None:
        self.meta = meta
        self.hop = int(meta.get("hop_steps", 1))
        self.L = 3 if self.hop == 1 else max(3, self.hop)   # rules count units arriving within one lead time

    def observe(self, info: StepInfo) -> None:
        pass


class StaticPolicy(_Base):
    name = "static"

    def reset(self, meta):
        super().reset(meta)
        self.shares = meta["hist_shares"]

    def act(self, s: FleetState) -> np.ndarray:
        total = s.idle_count.sum() + s.incoming(self.L)[1:].sum()
        return flows_to_targets(transport_flows(s, total * self.shares, lookahead=self.L), s)


class ReactivePolicy(_Base):
    name = "reactive"

    def __init__(self, window: int = 30):
        self.window = window

    def reset(self, meta):
        super().reset(meta)
        Z = meta["n_zones"]
        self.ma = MovingAverageForecaster(Z, self.window, init_level=meta["init_level_raw"])
        self.t = 0

    def act(self, s: FleetState) -> np.ndarray:
        self.t = s.t
        d = self.ma.forecast(s.t, 1).mean[0] + 1e-9
        total = s.idle_count.sum() + s.incoming(self.L)[1:].sum()
        return flows_to_targets(transport_flows(s, total * d / d.sum(), lookahead=self.L), s)

    def observe(self, info):
        self.ma.observe(self.t, info.arrivals)


class GreedyPolicy(_Base):
    name = "greedy"

    def reset(self, meta):
        super().reset(meta)
        self.edges = grid_edges(meta["grid"])

    def act(self, s: FleetState) -> np.ndarray:
        Z = s.idle_count.size
        k = 1 if self.hop == 1 else self.hop
        need = s.queue_len - s.idle_count - s.incoming(k)[1:].sum(0)
        spare = np.maximum(0, s.idle_count - s.queue_len)
        flows = np.zeros((Z, Z), dtype=np.int64)
        need = need.astype(np.int64).copy()
        for i in np.flatnonzero(spare > 0):
            nb = self.edges[self.edges[:, 0] == i, 1]
            for _ in range(int(spare[i])):
                j = nb[np.argmax(need[nb])]
                if need[j] <= 0:
                    break
                flows[i, j] += 1
                need[j] -= 1
        return flows_to_targets(flows, s)


class ZeroForecaster:
    """No demand model at all: the LP sees only the current queue (ablation 'mpc-queue')."""

    def __init__(self, n_zones: int):
        self.Z = n_zones

    def observe(self, t, counts):
        pass

    def forecast(self, t, horizon):
        return Forecast(mean=np.zeros((horizon, self.Z)))


class MPCPolicy(_Base):
    def __init__(self, kind: str = "cusum", horizon: int | None = None, c_move: float = 0.05, c_wait: float = 0.02,
                 gamma: float = 0.97, alpha: float | None = None, delta: float = 1.0, h: float = 8.0,
                 myopic: bool = False, backend: str = "auto", abandon_aware: bool = True, trust: float = 1.0):
        self.kind, self.H, self.myopic = kind, horizon, myopic
        self.trust = float(trust)   # scales the demand forecast fed to the LP: 0 = queue-only, 1 = certainty equivalence
        self.kw = dict(c_move=c_move, c_wait=c_wait, gamma=gamma, backend=backend)
        self.alpha, self.delta, self.h, self.abandon_aware = alpha, delta, h, abandon_aware
        self.name = {"ewma": "mpc-ewma", "cusum": "mpc-cusum", "cusum1": "mpc-cusum-v1", "oracle": "oracle",
                     "queue": "mpc-queue"}[kind] if not myopic else "mpc-myopic"

    def reset(self, meta):
        super().reset(meta)
        if self.myopic:  # same LP, shortest horizon in which a move can pay off (one step after arrival)
            self.Hrun = self.hop + 1
        else:
            self.Hrun = self.H or (6 if self.hop == 1 else self.hop + 6)   # look-ahead must exceed the lead time
        P = meta.get("patience") if self.abandon_aware else None
        self.planner = MPCPlanner(meta["grid"], meta["od_prob"], horizon=self.Hrun, hop_steps=self.hop, patience=P,
                                  **self.kw)
        prof, lvl = meta["profile"], meta["init_level"]
        if self.kind == "ewma":
            self.fc = EWMAForecaster(prof, lvl, alpha=self.alpha or 0.05)
        elif self.kind == "cusum1":  # ratchet v1 (autoresearch/candidate.py), promoted for end-to-end checks
            from components.forecasting.autoresearch.candidate import RestartMeanForecaster
            self.fc = RestartMeanForecaster(prof, lvl, alpha=self.alpha or 0.01, delta=self.delta, h=self.h)
        elif self.kind == "cusum":
            self.fc = ChangeAwareForecaster(prof, lvl, alpha=self.alpha or 0.01, delta=self.delta, h=self.h)
        elif self.kind == "queue":
            self.fc = ZeroForecaster(meta["n_zones"])
        else:
            self.fc = OracleForecaster(meta["rates"])
        self.t, self.solve_ms = 0, []

    def act(self, s: FleetState) -> np.ndarray:
        self.t = s.t
        fc = self.fc.forecast(s.t, self.Hrun)
        plan = self.planner.solve(s.idle_count, s.incoming(self.Hrun)[: self.Hrun], s.queue_len, self.trust * fc.mean)
        self.solve_ms.append(plan.solve_ms)
        return flows_to_targets(plan.flows, s)

    def observe(self, info):
        self.fc.observe(self.t, info.arrivals)


class GatedTrustMPC(MPCPolicy):
    """Spike A'' (decision-aware, regime-gated forecast trust). EWMA forecast; a per-zone Poisson CUSUM is used ONLY
    to gate trust: zones with an alarm (self or grid neighbour) in the last `window` steps plan on tau_shock x forecast,
    all other zones on tau_quiet x forecast. Parameters are tuned on tuning seeds only (eval/preregistration.md, Add. B)."""

    def __init__(self, tau_shock: float = 0.25, tau_quiet: float = 0.75, window: float = 60, scope: float = 0, **kw):
        super().__init__("ewma", **kw)
        self.tau_shock, self.tau_quiet, self.window = float(tau_shock), float(tau_quiet), int(window)
        self.city = float(scope) >= 0.5   # scope=1: city-wide regime (any recent alarm lowers trust everywhere)
        self.name = "mpc-gated"

    def reset(self, meta):
        super().reset(meta)
        Z, G = meta["n_zones"], meta["grid"]
        self.det = PoissonCusum(Z, delta=self.delta, h=self.h)
        self.last_alarm = np.full(Z, -10**9)
        E = grid_edges(G)
        self.adj = np.eye(Z, dtype=bool)
        self.adj[E[:, 0], E[:, 1]] = True

    def act(self, s: FleetState) -> np.ndarray:
        self.t = s.t
        recent = (s.t - self.last_alarm) <= self.window
        if self.city:
            gate = np.full(recent.shape, bool(recent.any()))
        else:
            gate = self.adj[recent].any(0) if recent.any() else recent
        trust = np.where(gate, self.tau_shock, self.tau_quiet)
        fc = self.fc.forecast(s.t, self.Hrun)
        plan = self.planner.solve(s.idle_count, s.incoming(self.Hrun)[: self.Hrun], s.queue_len, fc.mean * trust[None, :])
        self.solve_ms.append(plan.solve_ms)
        return flows_to_targets(plan.flows, s)

    def observe(self, info):
        f = float(self.fc.f(self.t))
        out, _ = self.det.update(self.t, info.arrivals, self.fc.level * f, f)
        self.last_alarm[out.alarm] = self.t
        self.fc.observe(self.t, info.arrivals)


class UncertaintyTrustMPC(MPCPolicy):
    """Detector-free comparator for Addendum B1(c). Per-zone forecast trust from residual uncertainty:
    trust_z = m_z^2 / (m_z^2 + kappa * v_z), clipped to [floor, 1], where m_z is the deseasonalised EWMA level and
    v_z an EWMA (rate beta) of squared deseasonalised one-step residuals (initialised at the Poisson value v = m).
    For Poisson noise v ~ m, so trust ~ m / (m + kappa): small fractional forecasts in quiet zones are shrunk most,
    and residual blow-ups (shocks) lower trust where they happen."""

    def __init__(self, kappa: float = 0.5, beta: float = 0.05, floor: float = 0.0, **kw):
        super().__init__("ewma", **kw)
        self.kappa, self.beta, self.floor = float(kappa), float(beta), float(floor)
        self.name = "mpc-unctrust"

    def reset(self, meta):
        super().reset(meta)
        self.v = np.maximum(np.asarray(self.fc.level, dtype=float), 1e-6).copy()
        self.last_trust = None

    def act(self, s: FleetState) -> np.ndarray:
        self.t = s.t
        m = np.maximum(self.fc.level, 1e-9)
        trust = np.clip(m ** 2 / (m ** 2 + self.kappa * self.v), self.floor, 1.0)
        self.last_trust = trust
        fc = self.fc.forecast(s.t, self.Hrun)
        plan = self.planner.solve(s.idle_count, s.incoming(self.Hrun)[: self.Hrun], s.queue_len, fc.mean * trust[None, :])
        self.solve_ms.append(plan.solve_ms)
        return flows_to_targets(plan.flows, s)

    def observe(self, info):
        f = float(self.fc.f(self.t))
        r = info.arrivals / f - self.fc.level
        self.v += self.beta * (r ** 2 - self.v)
        self.fc.observe(self.t, info.arrivals)


def make_policy(name: str, **kw):
    """'base@k=v,k2=v2' builds a variant of a base policy (e.g. 'mpc-ewma@c_move=0.5'); its name keeps the suffix."""
    if "@" in name:
        base, spec = name.split("@", 1)
        for item in spec.split(","):
            k, v = item.split("=")
            x = float(v)
            kw[k] = int(x) if x.is_integer() and k in ("horizon",) else x
        pol = make_policy(base, **kw)
        pol.name = name
        return pol
    return {"static": StaticPolicy, "greedy": GreedyPolicy, "reactive": ReactivePolicy,
            "mpc-myopic": lambda **k: MPCPolicy("ewma", myopic=True, **k),
            "mpc-gated": lambda **k: GatedTrustMPC(**k),
            "mpc-unctrust": lambda **k: UncertaintyTrustMPC(**k),
            "mpc-queue": lambda **k: MPCPolicy("queue", **k),
            "mpc-ewma": lambda **k: MPCPolicy("ewma", **k), "mpc-cusum": lambda **k: MPCPolicy("cusum", **k),
            "mpc-cusum-v1": lambda **k: MPCPolicy("cusum1", **k),
            "oracle": lambda **k: MPCPolicy("oracle", **k)}[name](**kw)
