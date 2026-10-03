"""Typed contracts between P7 components — the single source of truth.

Shapes: Z = number of zones, K = number of agents (resource units), H = look-ahead horizon (steps),
T = episode length (steps). All arrays are numpy. Every component imports its types from here;
changing this file is a lead decision (record it in thought_node.md and bump CONTRACT_VERSION).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

import numpy as np

CONTRACT_VERSION = "1.0.0"

IDLE, MOVING, BUSY = 0, 1, 2  # agent status codes


# ---------------------------------------------------------------- C2 Scenario -> C1 Simulator
@dataclass(frozen=True)
class ChangePoint:
    """Ground-truth label of a demand change (used only by evaluators, never by policies)."""
    t: int
    kind: str  # "shock_on" | "shock_off" | "drift_start" | "drift_end" | "spike_on" | "spike_off"
    zones: tuple[int, ...]
    magnitude: float


@dataclass
class DemandTrace:
    """A fully pre-sampled request stream (common random numbers across policies).

    rates[t, z]   true Poisson intensity (expected requests per step) — hidden from policies
    counts[t, z]  realised arrivals per step and zone
    req_dest      destination zone of every request, flattened in (t, z) order; request k of
                  (t, z) is at offsets[t, z] + k
    """
    rates: np.ndarray            # (T, Z) float64
    counts: np.ndarray           # (T, Z) int32
    req_dest: np.ndarray         # (N,) int16
    offsets: np.ndarray          # (T, Z) int64
    od_prob: np.ndarray          # (Z, Z) float64, P(dest | origin) — static map knowledge
    change_points: list[ChangePoint] = field(default_factory=list)
    name: str = ""

    @property
    def horizon(self) -> int:
        return int(self.rates.shape[0])

    @property
    def n_zones(self) -> int:
        return int(self.rates.shape[1])


# ---------------------------------------------------------------- C1 Simulator -> policies
@dataclass
class FleetState:
    """What every policy observes at the start of step t (fully observable fleet, hidden rates)."""
    t: int
    agent_zone: np.ndarray       # (K,) int — current zone, or target zone if MOVING/BUSY
    agent_status: np.ndarray     # (K,) int — IDLE / MOVING / BUSY
    agent_eta: np.ndarray        # (K,) int — steps until IDLE at agent_zone (0 if IDLE)
    idle_count: np.ndarray       # (Z,) int — idle agents per zone
    queue_len: np.ndarray        # (Z,) int — waiting (unserved, not yet abandoned) requests
    last_arrivals: np.ndarray    # (Z,) int — requests that arrived in step t-1 (observed demand)
    travel_time: np.ndarray      # (Z, Z) int — steps to move between zones (0 on diagonal)
    od_prob: np.ndarray          # (Z, Z) float — P(dest | origin), static map knowledge
    patience: int                # steps a request waits before abandoning

    def incoming(self, horizon: int) -> np.ndarray:
        """(horizon+1, Z) agents becoming IDLE at the start of step t+k (k>=1) per zone."""
        Z = self.idle_count.shape[0]
        inc = np.zeros((horizon + 1, Z), dtype=np.int64)
        busy = self.agent_status != IDLE
        eta = self.agent_eta[busy]
        zone = self.agent_zone[busy]
        ok = eta <= horizon
        np.add.at(inc, (eta[ok], zone[ok]), 1)
        return inc


@dataclass
class StepInfo:
    """Per-step outcome reported by the simulator."""
    arrivals: np.ndarray         # (Z,) int
    served: np.ndarray           # (Z,) int
    lost: np.ndarray             # (Z,) int — abandoned this step
    wait_hist: np.ndarray        # (patience,) int — histogram of waits of requests served this step
    empty_moves: int             # zone-hops started this step by agents moving without a request
    reward: float                # team reward = served - lost_penalty*lost - move_cost*empty_moves


# ---------------------------------------------------------------- C4 Detector / C5 Forecaster
@dataclass
class DetectorOutput:
    alarm: np.ndarray            # (Z,) bool — change declared at this step
    stat: np.ndarray             # (Z,) float — detector statistic (CUSUM value / changepoint prob)
    change_start: np.ndarray     # (Z,) int — estimated change onset (absolute step), -1 if none


@dataclass
class Forecast:
    """Look-ahead demand belief for steps t .. t+H-1."""
    mean: np.ndarray             # (H, Z) float — expected arrivals per step
    upper: np.ndarray | None = None  # (H, Z) float — calibrated upper quantile (optional)
    quantile: float | None = None    # level of `upper`


@runtime_checkable
class DemandForecaster(Protocol):
    def observe(self, t: int, counts: np.ndarray) -> None: ...
    def forecast(self, t: int, horizon: int) -> Forecast: ...


# ---------------------------------------------------------------- C6 Planner -> C7 Coordinator
@dataclass
class Plan:
    flows: np.ndarray            # (Z, Z) int — idle agents to send i -> j now (diag = 0)
    objective: float             # planner objective value (expected served - move cost)
    solve_ms: float              # wall-clock solve time
    status: str = "ok"           # "ok" | "fallback" | "infeasible"
    zone_value: np.ndarray | None = None  # (Z,) dual prices of idle capacity (optional)


@runtime_checkable
class Policy(Protocol):
    """A complete allocator (baseline, look-ahead stack, oracle or RL). Maps state -> joint action."""
    name: str

    def reset(self, trace_meta: dict) -> None: ...

    def act(self, state: FleetState) -> np.ndarray:
        """Return (K,) int target zone per agent; only IDLE agents move (target != zone)."""
        ...

    def observe(self, info: StepInfo) -> None: ...
