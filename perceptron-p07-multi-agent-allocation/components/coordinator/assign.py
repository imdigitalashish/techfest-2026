"""C7 — Coordinator: zone-level flows -> per-agent move orders, and the transport rebalancer used
by rule-based allocators.

Units in the same zone are interchangeable in this simulator, so flows_to_targets picks the lowest-index
idle units (deterministic). With heterogeneous units (battery, capacity) this is where a Hungarian /
auction assignment would go — see architecture/components.md (C7).
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment

from architecture.contracts.contracts import IDLE, FleetState


def flows_to_targets(flows: np.ndarray, state: FleetState) -> np.ndarray:
    targets = state.agent_zone.copy()
    idle = np.flatnonzero(state.agent_status == IDLE)
    if idle.size == 0 or flows.sum() == 0:
        return targets
    zs = state.agent_zone[idle]
    for i in np.flatnonzero(flows.sum(1) > 0):
        units = idle[zs == i]
        dests = np.repeat(np.arange(flows.shape[1]), flows[i])
        m = min(units.size, dests.size)
        targets[units[:m]] = dests[:m]
    return targets


def transport_flows(state: FleetState, desired: np.ndarray, lookahead: int = 3) -> np.ndarray:
    """Move surplus idle units to deficit zones (min total travel) so that supply available within
    `lookahead` steps matches `desired` (float, per zone). Returns integer (Z, Z) flows."""
    Z = desired.size
    idle = state.idle_count
    soon = state.incoming(lookahead)[1:].sum(0)
    supply = idle + soon
    surplus = np.minimum(idle, np.floor(np.maximum(0.0, supply - desired))).astype(np.int64)
    deficit = np.floor(np.maximum(0.0, desired - supply) + 0.5).astype(np.int64)
    flows = np.zeros((Z, Z), dtype=np.int64)
    if surplus.sum() == 0 or deficit.sum() == 0:
        return flows
    rows = np.repeat(np.arange(Z), surplus)
    cols = np.repeat(np.arange(Z), deficit)
    r, c = linear_sum_assignment(state.travel_time[np.ix_(rows, cols)])
    np.add.at(flows, (rows[r], cols[c]), 1)
    np.fill_diagonal(flows, 0)
    return flows
