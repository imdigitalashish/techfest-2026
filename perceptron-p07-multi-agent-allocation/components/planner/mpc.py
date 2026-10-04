"""C6 — Look-ahead planner: rolling-horizon MPC as a linear program on a time-expanded zone graph.

Variables for tau = 0..H-1 (block per tau): x[tau, e] idle units hopping along grid edge e (1 step,
4-neighbourhood; longer trips = successive hops, re-planned every step); y[tau, i] units staying idle;
s[tau, i] units serving requests in zone i (they reappear at destination j after trip[i, j] steps
with probability od[i, j] — a fluid approximation); b[tau, i] backlog carried to tau+1.
  conservation (=):  y + sum_out x + s - y[tau-1] - sum_in x[tau-1] - sum_k od[k,i] s[tau-trip[k,i], k]
                     = supply[tau, i]   (idle now at tau=0; known units freeing up at tau>=1)
  demand (<=):       s + b - b[tau-1] <= D_hat[tau, i] (+ current queue at tau=0)
  objective (min):   sum_tau gamma^tau ( -s + c_wait*b + c_move*x )
Only x[0] is executed (receding horizon). Structure matrices are built once; per call only the
right-hand sides change. Solver: HiGHS via scipy.optimize.linprog. Dual prices of the tau=0
conservation rows (value of one more idle unit in zone i) are returned for price-based coordination.
"""
from __future__ import annotations

import time

import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog

from architecture.contracts.contracts import Plan
from components.scenarios.scenarios import manhattan


def grid_edges(grid: int) -> np.ndarray:
    E = []
    for i in range(grid * grid):
        r, c = divmod(i, grid)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < grid and 0 <= cc < grid:
                E.append((i, rr * grid + cc))
    return np.array(E, dtype=np.int64)


class MPCPlanner:
    def __init__(self, grid: int, od_prob: np.ndarray, horizon: int = 6, c_move: float = 0.05,
                 c_wait: float = 0.02, gamma: float = 0.97):
        self.G, self.Z, self.H = grid, grid * grid, int(horizon)
        self.edges = grid_edges(grid)
        self.E = len(self.edges)
        self.trip = np.maximum(1, manhattan(grid))
        self.od = od_prob
        Z, E, H = self.Z, self.E, self.H
        self.B = E + 3 * Z
        n = H * self.B
        X = lambda t, e: t * self.B + e
        Y = lambda t, i: t * self.B + E + i
        S = lambda t, i: t * self.B + E + Z + i
        Bk = lambda t, i: t * self.B + E + 2 * Z + i
        r, c, v = [], [], []
        for t in range(H):
            for i in range(Z):
                row = t * Z + i
                r += [row, row]; c += [Y(t, i), S(t, i)]; v += [1.0, 1.0]
                if t > 0:
                    r.append(row); c.append(Y(t - 1, i)); v.append(-1.0)
            for e, (i, j) in enumerate(self.edges):
                r.append(t * Z + i); c.append(X(t, e)); v.append(1.0)
                if t + 1 < H:
                    r.append((t + 1) * Z + j); c.append(X(t, e)); v.append(-1.0)
            for k in range(Z):
                for i in range(Z):
                    ta = t + self.trip[k, i]
                    if ta < H and od_prob[k, i] > 0:
                        r.append(ta * Z + i); c.append(S(t, k)); v.append(-float(od_prob[k, i]))
        self.A_eq = sp.csr_matrix((v, (r, c)), shape=(H * Z, n))
        r, c, v = [], [], []
        for t in range(H):
            for i in range(Z):
                row = t * Z + i
                r += [row, row]; c += [S(t, i), Bk(t, i)]; v += [1.0, 1.0]
                if t > 0:
                    r.append(row); c.append(Bk(t - 1, i)); v.append(-1.0)
        self.A_ub = sp.csr_matrix((v, (r, c)), shape=(H * Z, n))
        cost = np.zeros(n)
        for t in range(H):
            g = gamma ** t
            cost[t * self.B: t * self.B + E] = g * c_move
            cost[t * self.B + E + Z: t * self.B + E + 2 * Z] = -g
            cost[t * self.B + E + 2 * Z: t * self.B + E + 3 * Z] = g * c_wait
        self.cost = cost

    def solve(self, idle: np.ndarray, incoming: np.ndarray, queue: np.ndarray, demand: np.ndarray) -> Plan:
        """idle (Z,), incoming (H, Z) units freeing up at tau (row 0 ignored), queue (Z,), demand (H, Z)."""
        t0 = time.perf_counter()
        H, Z = self.H, self.Z
        b_eq = incoming[:H].astype(float).copy()
        b_eq[0] = idle
        b_ub = np.maximum(demand[:H], 0.0).astype(float).copy()
        b_ub[0] += queue
        res = linprog(self.cost, A_ub=self.A_ub, b_ub=b_ub.ravel(), A_eq=self.A_eq, b_eq=b_eq.ravel(),
                      bounds=(0, None), method="highs-ipm")
        flows = np.zeros((Z, Z), dtype=np.int64)
        if res.status != 0:
            return Plan(flows=flows, objective=float("nan"), solve_ms=1e3 * (time.perf_counter() - t0),
                        status="infeasible")
        x0 = res.x[: self.E]
        for i in range(Z):
            out = np.flatnonzero(self.edges[:, 0] == i)
            f = x0[out]
            tot = min(int(round(f.sum())), int(idle[i]))
            if tot <= 0:
                continue
            base = np.floor(f).astype(np.int64)
            rem = tot - base.sum()
            if rem > 0:
                base[np.argsort(-(f - base))[:rem]] += 1
            elif rem < 0:
                base = np.floor(f * tot / max(f.sum(), 1e-9)).astype(np.int64)
            flows[i, self.edges[out, 1]] = base
        duals = -np.asarray(res.eqlin.marginals[:Z]) if res.eqlin is not None else None
        return Plan(flows=flows, objective=-float(res.fun), solve_ms=1e3 * (time.perf_counter() - t0),
                    status="ok", zone_value=duals)
