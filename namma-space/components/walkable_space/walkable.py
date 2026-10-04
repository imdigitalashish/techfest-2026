"""Walkable space (spike A): aligned sparse geometry + capture evidence -> 2D navigation grid.

Contract: in = aligned points (N,3), camera centres (trajectory), optional observation rays
(camera centre -> observed point); out = NavGrid (navigable mask, obstacle mask, clearance in m).
Evidence fused:
  * obstacles  : points in the body band [step_height, agent_height] (>= min_occ_points per voxel)
  * carving    : rays camera->point mark voxels as observed-free; a voxel stays an obstacle only if
                 free_samples <= carve_beta * point_count (removes floaters)
  * floor      : points within floor_tol of y=0, plus low-band carved voxels
  * trajectory : where the capturer walked is walkable (SOP rule "walk the real routes")
Navigable = walkable eroded by agent_radius, restricted to the component that holds the trajectory.
"""
from __future__ import annotations

import base64
import time

import numpy as np
from scipy import ndimage

DEFAULTS = dict(cell=0.05, voxel=0.10, agent_radius=0.25, agent_height=1.70, step_height=0.15,
                floor_tol=0.08, floor_dilate_m=0.30, min_occ_points=2, carve_beta=4.0,
                traj_radius=0.35, close_m=0.20)


def _disk(r_cells):
    r = int(max(1, round(r_cells)))
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def build_grid(points, traj, rays_from=None, rays_to=None, use_carving=True, use_trajectory=True,
               params=None):
    p = dict(DEFAULTS)
    p.update(params or {})
    t0 = time.perf_counter()
    P, C = np.asarray(points, float), np.asarray(traj, float)
    lo = np.minimum(np.percentile(P[:, [0, 2]], 1, axis=0), C[:, [0, 2]].min(0)) - 1.0
    hi = np.maximum(np.percentile(P[:, [0, 2]], 99, axis=0), C[:, [0, 2]].max(0)) + 1.0
    cell, vox = p["cell"], p["voxel"]
    nx, nz = (int(v) for v in np.ceil((hi - lo) / cell))
    ratio = int(round(vox / cell))
    vnx, vnz = -(-nx // ratio), -(-nz // ratio)
    ny = int(np.ceil((p["agent_height"] - p["step_height"]) / vox))
    size = vnx * ny * vnz

    def vflat(X):
        i = np.floor((X[:, 0] - lo[0]) / vox).astype(np.int64)
        k = np.floor((X[:, 2] - lo[1]) / vox).astype(np.int64)
        j = np.floor((X[:, 1] - p["step_height"]) / vox).astype(np.int64)
        ok = (i >= 0) & (i < vnx) & (k >= 0) & (k < vnz) & (j >= 0) & (j < ny)
        return (i[ok] * ny + j[ok]) * vnz + k[ok]

    occ = np.bincount(vflat(P), minlength=size).astype(np.float32).reshape(vnx, ny, vnz)
    free = np.zeros(size, np.float32)
    n_samples = 0
    if use_carving and rays_from is not None and len(rays_from):
        A = np.asarray(rays_from, float)
        D = P[np.asarray(rays_to)] - A
        L = np.linalg.norm(D, axis=1)
        step = vox * 0.5
        for s in range(0, len(A), 20000):
            a, d, l = A[s:s + 20000], D[s:s + 20000], L[s:s + 20000]
            n = np.maximum(((l - 2 * vox) / step).astype(np.int64), 0)
            tot = int(n.sum())
            if tot == 0:
                continue
            r = np.repeat(np.arange(len(a)), n)
            t = (np.arange(tot) - np.repeat(np.cumsum(n) - n, n)) * step
            free += np.bincount(vflat(a[r] + d[r] * (t / l[r])[:, None]), minlength=size)
            n_samples += tot
    free = free.reshape(vnx, ny, vnz)
    obst = occ >= p["min_occ_points"]
    if use_carving:
        obst &= free <= p["carve_beta"] * occ
    up2 = lambda m: np.kron(m, np.ones((ratio, ratio), bool))[:nx, :nz]
    O = up2(obst.any(axis=1))
    fl = P[np.abs(P[:, 1]) < p["floor_tol"]]
    ij = np.floor((fl[:, [0, 2]] - lo) / cell).astype(int)
    ok = (ij[:, 0] >= 0) & (ij[:, 0] < nx) & (ij[:, 1] >= 0) & (ij[:, 1] < nz)
    F = np.zeros((nx, nz), bool)
    F[ij[ok, 0], ij[ok, 1]] = True
    F = ndimage.binary_dilation(F, _disk(p["floor_dilate_m"] / cell))
    if use_carving:
        F |= up2(free[:, 0, :] > 0)
    cij = np.floor((C[:, [0, 2]] - lo) / cell).astype(int)
    cij[:, 0] = np.clip(cij[:, 0], 0, nx - 1)
    cij[:, 1] = np.clip(cij[:, 1], 0, nz - 1)
    T = np.zeros((nx, nz), bool)
    T[cij[:, 0], cij[:, 1]] = True
    T = ndimage.binary_dilation(T, _disk(p["traj_radius"] / cell))
    W = ndimage.binary_closing(F | T if use_trajectory else F, _disk(p["close_m"] / cell)) & ~O
    if use_trajectory:
        W |= T
    clearance = ndimage.distance_transform_edt(W) * cell
    N = clearance >= p["agent_radius"]
    lab, nlab = ndimage.label(N, structure=np.ones((3, 3)))
    if nlab > 1:
        cnt = np.bincount(lab[cij[:, 0], cij[:, 1]], minlength=nlab + 1)
        cnt[0] = 0
        if cnt.max() == 0:
            cnt = np.bincount(lab.ravel())
            cnt[0] = 0
        N = lab == int(np.argmax(cnt))
    return dict(lo=lo, cell=cell, nx=nx, nz=nz, obstacle=O, floor=F, trajectory=T, walkable=W,
                navigable=N, clearance=clearance, params=p, n_ray_samples=n_samples,
                runtime_s=time.perf_counter() - t0)


def to_json(g):
    pack = lambda m: base64.b64encode(np.packbits(m.astype(np.uint8).ravel())).decode()
    return {"frame": "aligned, y-up, metres; cell (i,k) centre = (lo_x+(i+0.5)*cell, lo_z+(k+0.5)*cell)",
            "lo_xz": [float(g["lo"][0]), float(g["lo"][1])], "cell_m": g["cell"], "nx": g["nx"],
            "nz": g["nz"], "layout": "row-major (i,k), np.packbits big-endian",
            "navigable_b64": pack(g["navigable"]), "obstacle_b64": pack(g["obstacle"]),
            "params": g["params"]}
