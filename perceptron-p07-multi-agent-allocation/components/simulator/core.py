"""C1 — Dispatch simulator core (fast numpy) + the per-step semantics every policy is judged on.

Step t:  1) policy moves IDLE agents (travel = Manhattan hops, 1 step per hop; MOVING until arrival)
         2) requests of step t join their zone's FIFO queue
         3) IDLE agents in a zone serve its oldest waiting requests (same-zone matching; shared rule
            for every policy, so only the allocation decision differs); a served agent is BUSY for
            max(1, hops(origin, dest)) steps and becomes IDLE at the destination
         4) requests that have waited `patience` steps abandon (lost)
         5) clocks advance; agents whose eta reaches 0 become IDLE
Requests in a zone are always a contiguous FIFO range (service and abandonment both take the oldest),
so the queue is two pointers into a pre-sampled per-zone request array — exact and O(1) per event.
"""
from __future__ import annotations

import numpy as np

from architecture.contracts.contracts import BUSY, IDLE, MOVING, DemandTrace, FleetState, StepInfo
from components.scenarios.scenarios import manhattan


class DispatchCore:
    def __init__(self, trace: DemandTrace, n_agents: int = 40, patience: int = 10,
                 move_cost: float = 0.05, lost_penalty: float = 0.0, init_seed: int = 0,
                 init_shares: np.ndarray | None = None, move_steps_per_hop: int = 1):
        self.trace = trace
        self.T, self.Z = trace.counts.shape
        self.G = int(round(np.sqrt(self.Z)))
        assert self.G * self.G == self.Z, "zones must form a square grid"
        self.K, self.P = int(n_agents), int(patience)
        self.move_cost, self.lost_penalty = float(move_cost), float(lost_penalty)
        self.travel = manhattan(self.G)
        self.hop_steps = int(move_steps_per_hop)       # reallocation lead time L per hop (cold-start analogue)
        self.move_time = self.travel * self.hop_steps   # empty repositioning only; service trips stay max(1, hops)
        self.trip = np.maximum(1, self.travel)
        # per-zone request arrays in arrival order
        self.times_z, self.dest_z = [], []
        T = self.T
        for z in range(self.Z):
            c = trace.counts[:, z]
            starts = trace.offsets[:, z]
            idx = np.repeat(starts - np.concatenate([[0], np.cumsum(c)[:-1]]), c) + np.arange(int(c.sum()))
            self.times_z.append(np.repeat(np.arange(T), c).astype(np.int64))
            self.dest_z.append(trace.req_dest[idx].astype(np.int64))
        shares = init_shares if init_shares is not None else trace.rates[0] / trace.rates[0].sum()
        rng = np.random.default_rng(np.random.SeedSequence([init_seed, 11]))
        self._init_zone = rng.choice(self.Z, size=self.K, p=shares / shares.sum()).astype(np.int64)
        self.reset()

    # ------------------------------------------------------------------ API
    def reset(self) -> FleetState:
        self.t = 0
        self.zone = self._init_zone.copy()
        self.status = np.full(self.K, IDLE, dtype=np.int64)
        self.eta = np.zeros(self.K, dtype=np.int64)
        self.head = np.zeros(self.Z, dtype=np.int64)
        self.tail = np.zeros(self.Z, dtype=np.int64)
        return self.state()

    @property
    def done(self) -> bool:
        return self.t >= self.T

    def state(self) -> FleetState:
        idle = self.status == IDLE
        last = self.trace.counts[self.t - 1] if self.t > 0 else np.zeros(self.Z, dtype=np.int32)
        return FleetState(t=self.t, agent_zone=self.zone.copy(), agent_status=self.status.copy(),
                          agent_eta=self.eta.copy(),
                          idle_count=np.bincount(self.zone[idle], minlength=self.Z),
                          queue_len=self.tail - self.head, last_arrivals=last.astype(np.int64),
                          travel_time=self.move_time, od_prob=self.trace.od_prob, patience=self.P)

    def step(self, targets: np.ndarray) -> StepInfo:
        t, Z = self.t, self.Z
        assert t < self.T, "episode finished"
        targets = np.asarray(targets, dtype=np.int64)
        # 1) moves
        idle = self.status == IDLE
        mv = idle & (targets != self.zone) & (targets >= 0) & (targets < Z)
        empty = 0
        if mv.any():
            d = self.travel[self.zone[mv], targets[mv]]
            empty = int(d.sum())
            self.eta[mv] = self.move_time[self.zone[mv], targets[mv]]
            self.zone[mv] = targets[mv]
            self.status[mv] = MOVING
        # 2) arrivals
        arr = self.trace.counts[t].astype(np.int64)
        self.tail += arr
        # 3) same-zone FIFO matching
        served = np.zeros(Z, dtype=np.int64)
        wait_hist = np.zeros(self.P, dtype=np.int64)
        idle_idx = np.flatnonzero(self.status == IDLE)
        if idle_idx.size:
            zs = self.zone[idle_idx]
            order = np.argsort(zs, kind="stable")
            idle_sorted, zs_sorted = idle_idx[order], zs[order]
            starts = np.searchsorted(zs_sorted, np.arange(Z), side="left")
            ends = np.searchsorted(zs_sorted, np.arange(Z), side="right")
            n = np.minimum(ends - starts, self.tail - self.head)
            for z in np.flatnonzero(n > 0):
                k, h = int(n[z]), int(self.head[z])
                ag = idle_sorted[starts[z]:starts[z] + k]
                dests = self.dest_z[z][h:h + k]
                wait_hist += np.bincount(t - self.times_z[z][h:h + k], minlength=self.P)[: self.P]
                self.zone[ag] = dests
                self.status[ag] = BUSY
                self.eta[ag] = self.trip[z, dests]
                self.head[z] += k
                served[z] = k
        # 4) abandonment: arrival time <= t - P + 1 has waited P steps
        lost = np.zeros(Z, dtype=np.int64)
        cutoff = t - self.P + 1
        if cutoff >= 0:
            for z in np.flatnonzero(self.tail > self.head):
                nh = int(np.searchsorted(self.times_z[z], cutoff, side="right"))
                if nh > self.head[z]:
                    lost[z] = nh - self.head[z]
                    self.head[z] = nh
        # 5) advance clocks
        busy = self.status != IDLE
        self.eta[busy] -= 1
        fin = busy & (self.eta <= 0)
        self.status[fin] = IDLE
        self.eta[fin] = 0
        self.t += 1
        reward = float(served.sum() - self.lost_penalty * lost.sum() - self.move_cost * empty)
        return StepInfo(arrivals=arr, served=served, lost=lost, wait_hist=wait_hist,
                        empty_moves=empty, reward=reward)
