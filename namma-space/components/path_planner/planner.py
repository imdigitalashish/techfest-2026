"""Path planner: NavGrid + start/goal (aligned metres) -> collision-free polyline on the floor.

Baseline: 8-connected A* (no corner cutting) with a clearance penalty (prefers corridor centres),
then greedy line-of-sight string pulling on the navigable (already radius-eroded) mask.
Optimal on the grid for its cost; all error comes from the map (walkable_space), not the search.
"""
from __future__ import annotations

import heapq
import math
import time

import numpy as np
from scipy import ndimage

_SQ2 = math.sqrt(2.0)
_NB = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
       (-1, -1, _SQ2), (-1, 1, _SQ2), (1, -1, _SQ2), (1, 1, _SQ2)]


class GridPlanner:
    def __init__(self, navigable, clearance, lo, cell, w_clear=2.0, c_pref=0.6):
        self.N = np.asarray(navigable, bool)
        self.lo, self.cell = np.asarray(lo, float), float(cell)
        self.nx, self.nz = self.N.shape
        self.pen = 1.0 + w_clear * np.clip((c_pref - clearance) / c_pref, 0.0, 1.0)
        self.near = ndimage.distance_transform_edt(~self.N, return_distances=False, return_indices=True)

    def to_ij(self, xz):
        ij = np.floor((np.asarray(xz, float) - self.lo) / self.cell).astype(int)
        return int(np.clip(ij[0], 0, self.nx - 1)), int(np.clip(ij[1], 0, self.nz - 1))

    def to_xz(self, ij):
        return self.lo + (np.asarray(ij, float) + 0.5) * self.cell

    def snap(self, ij):
        return int(self.near[0][ij]), int(self.near[1][ij])

    def astar(self, s, g):
        N, pen, nx, nz = self.N, self.pen, self.nx, self.nz
        gi, gk = g
        best, came, closed = {s: 0.0}, {}, set()
        pq = [(math.hypot(s[0] - gi, s[1] - gk), 0.0, s)]
        while pq:
            _, d, u = heapq.heappop(pq)
            if u in closed:
                continue
            if u == g:
                break
            closed.add(u)
            i, k = u
            for di, dk, w in _NB:
                a, b = i + di, k + dk
                if a < 0 or b < 0 or a >= nx or b >= nz or not N[a, b]:
                    continue
                if di and dk and not (N[a, k] and N[i, b]):
                    continue
                nd = d + w * 0.5 * (pen[i, k] + pen[a, b])
                if nd < best.get((a, b), 1e18):
                    best[(a, b)] = nd
                    came[(a, b)] = u
                    heapq.heappush(pq, (nd + math.hypot(a - gi, b - gk), nd, (a, b)))
        if g != s and g not in came:
            return None
        path = [g]
        while path[-1] != s:
            path.append(came[path[-1]])
        return path[::-1]

    def los(self, a, b, eps=0.05):
        # Conservative supercover in cell units: vertices are cell centres (i+0.5); a continuous point u
        # lies in cell floor(u). Checking floor(u±eps) on both axes guards boundary/corner grazing.
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) * 10) + 2
        t = np.linspace(0.0, 1.0, n)
        ui = a[0] + 0.5 + t * (b[0] - a[0])
        uk = a[1] + 0.5 + t * (b[1] - a[1])
        for di in (-eps, eps):
            for dk in (-eps, eps):
                ii = np.clip(np.floor(ui + di).astype(int), 0, self.nx - 1)
                kk = np.clip(np.floor(uk + dk).astype(int), 0, self.nz - 1)
                if not self.N[ii, kk].all():
                    return False
        return True

    def smooth(self, path):
        if len(path) < 3:
            return list(path)
        out, anchor = [path[0]], 0
        for j in range(2, len(path)):
            if not self.los(path[anchor], path[j]):
                anchor = j - 1
                out.append(path[anchor])
        out.append(path[-1])
        return out

    def plan(self, start_xz, goal_xz):
        t0 = time.perf_counter()
        if not self.N.any():
            return {"ok": False, "ms": (time.perf_counter() - t0) * 1e3, "why": "empty navigable grid"}
        s, g = self.snap(self.to_ij(start_xz)), self.snap(self.to_ij(goal_xz))
        raw = self.astar(s, g)
        if raw is None:
            return {"ok": False, "ms": (time.perf_counter() - t0) * 1e3}
        xz = self.to_xz(np.array(self.smooth(raw)))
        length = float(np.linalg.norm(np.diff(xz, axis=0), axis=1).sum()) if len(xz) > 1 else 0.0
        return {"ok": True, "ms": (time.perf_counter() - t0) * 1e3, "xz": xz, "length_m": length,
                "raw_cells": len(raw)}


def densify(xz, step=0.05):
    out = [xz[0]]
    for a, b in zip(xz[:-1], xz[1:]):
        n = max(1, int(np.ceil(np.linalg.norm(b - a) / step)))
        out.extend(a + (b - a) * (t / n) for t in range(1, n + 1))
    return np.array(out)


if __name__ == "__main__":
    # contract test: a wall with a single doorway; the path must use the doorway and never touch the wall
    nx = nz = 60
    walk = np.ones((nx, nz), bool)
    walk[30, :] = False
    walk[30, 45:50] = True
    clear = ndimage.distance_transform_edt(walk) * 0.1
    nav = clear >= 0.15
    pl = GridPlanner(nav, clear, (0.0, 0.0), 0.1)
    r = pl.plan((1.0, 1.0), (5.5, 1.0))
    assert r["ok"], r
    pts = densify(r["xz"])
    ij = np.floor(pts / 0.1).astype(int)
    assert nav[ij[:, 0], ij[:, 1]].all(), "path leaves navigable space"
    assert any(abs(p[0] - 3.05) < 0.1 and 4.5 <= p[1] <= 5.0 for p in pts), "path must cross the doorway"
    assert r["length_m"] >= 4.5, r["length_m"]
    print("planner contract test OK", round(r["length_m"], 2), "m", round(r["ms"], 1), "ms")
