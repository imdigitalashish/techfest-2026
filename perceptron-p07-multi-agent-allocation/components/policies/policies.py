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

from architecture.contracts.contracts import FleetState, StepInfo
from components.coordinator.assign import flows_to_targets, transport_flows
from components.forecasting.forecasters import (ChangeAwareForecaster, EWMAForecaster,
                                                MovingAverageForecaster, OracleForecaster)
from components.planner.mpc import MPCPlanner, grid_edges


class _Base:
    name = "base"

    def reset(self, meta: dict) -> None:
        self.meta = meta

    def observe(self, info: StepInfo) -> None:
        pass


class StaticPolicy(_Base):
    name = "static"

    def reset(self, meta):
        super().reset(meta)
        self.shares = meta["hist_shares"]

    def act(self, s: FleetState) -> np.ndarray:
        total = s.idle_count.sum() + s.incoming(3)[1:].sum()
        return flows_to_targets(transport_flows(s, total * self.shares), s)


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
        total = s.idle_count.sum() + s.incoming(3)[1:].sum()
        return flows_to_targets(transport_flows(s, total * d / d.sum()), s)

    def observe(self, info):
        self.ma.observe(self.t, info.arrivals)


class GreedyPolicy(_Base):
    name = "greedy"

    def reset(self, meta):
        super().reset(meta)
        self.edges = grid_edges(meta["grid"])

    def act(self, s: FleetState) -> np.ndarray:
        Z = s.idle_count.size
        need = s.queue_len - s.idle_count - s.incoming(1)[1]
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


class MPCPolicy(_Base):
    def __init__(self, kind: str = "cusum", horizon: int = 6, c_move: float = 0.05, c_wait: float = 0.02,
                 gamma: float = 0.97, alpha: float | None = None, delta: float = 1.0, h: float = 8.0):
        self.kind, self.H = kind, horizon
        self.kw = dict(c_move=c_move, c_wait=c_wait, gamma=gamma)
        self.alpha, self.delta, self.h = alpha, delta, h
        self.name = {"ewma": "mpc-ewma", "cusum": "mpc-cusum", "cusum1": "mpc-cusum-v1", "oracle": "oracle"}[kind]

    def reset(self, meta):
        super().reset(meta)
        self.planner = MPCPlanner(meta["grid"], meta["od_prob"], horizon=self.H, **self.kw)
        prof, lvl = meta["profile"], meta["init_level"]
        if self.kind == "ewma":
            self.fc = EWMAForecaster(prof, lvl, alpha=self.alpha or 0.05)
        elif self.kind == "cusum1":  # ratchet v1 (autoresearch/candidate.py), promoted for end-to-end checks
            from components.forecasting.autoresearch.candidate import RestartMeanForecaster
            self.fc = RestartMeanForecaster(prof, lvl, alpha=self.alpha or 0.01, delta=self.delta, h=self.h)
        elif self.kind == "cusum":
            self.fc = ChangeAwareForecaster(prof, lvl, alpha=self.alpha or 0.01, delta=self.delta, h=self.h)
        else:
            self.fc = OracleForecaster(meta["rates"])
        self.t, self.solve_ms = 0, []

    def act(self, s: FleetState) -> np.ndarray:
        self.t = s.t
        fc = self.fc.forecast(s.t, self.H)
        plan = self.planner.solve(s.idle_count, s.incoming(self.H)[: self.H], s.queue_len, fc.mean)
        self.solve_ms.append(plan.solve_ms)
        return flows_to_targets(plan.flows, s)

    def observe(self, info):
        self.fc.observe(self.t, info.arrivals)


def make_policy(name: str, **kw):
    return {"static": StaticPolicy, "greedy": GreedyPolicy, "reactive": ReactivePolicy,
            "mpc-ewma": lambda **k: MPCPolicy("ewma", **k), "mpc-cusum": lambda **k: MPCPolicy("cusum", **k),
            "mpc-cusum-v1": lambda **k: MPCPolicy("cusum1", **k),
            "oracle": lambda **k: MPCPolicy("oracle", **k)}[name](**kw)
