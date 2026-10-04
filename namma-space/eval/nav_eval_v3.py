#!/usr/bin/env python3
"""Path-safety evaluation v3 — fixes from the gpt-6-astra review (2026-10-04).

Reference ("instrument"), frozen and independent of the candidate:
  dense proxy = 3DGS splats (opacity > 0.1, max scale < 0.2 m, 0.15-1.70 m band) -> fixed 5 cm grid with
  its own bounds; obstacle cell = >= 3 splats; EDT = distance to the nearest obstacle cell. NOT ground truth
  (same photos as the candidate); a real-geometry scene is scheduled for confirmation.
Endpoints: each held-out camera's floor projection is moved to the nearest reference cell with clearance
  >= r (searched within 0.5 m); cameras without one are dropped (reported).
Pairs: ALL pairs of valid held-out endpoints that the reference itself connects (Dijkstra on the reference
  free space with clearance >= r).
Per pair, the candidate (NavGrid from buffered training frames + A*) either REFUSES (no path, or snap
  > 0.25 m) or returns a route; the full polyline (endpoint -> snapped start -> path -> snapped goal ->
  endpoint) is sampled every 2.5 cm and COLLIDES if any sample is out of the reference bounds or has
  clearance < r + cell·√2/2 (conservative: certifies distance ≥ r to every obstacle-cell centre; diagonal moves may not cut corners, matching the candidate A*).
Score: CFC@r = share of pairs with a non-colliding route (refusal and collision both fail). Reported with
  Wilson 95% intervals, refusal and collision rates, stretch vs the reference geodesic, and paired sign
  tests between variants on identical pairs.
"""
import json
import math
import os
import sys

import numpy as np
from scipy import ndimage, sparse
from scipy.sparse import csgraph

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "components"))
sys.path.insert(0, os.path.join(ROOT, "eval"))
from nav_eval_v2 import prepare  # noqa: E402  (same data loading; v2 scoring is superseded)
from path_planner.planner import GridPlanner, densify  # noqa: E402
from walkable_space.walkable import build_grid  # noqa: E402

REF_CELL, REF_MIN_SPLATS, MAX_EXTENT_M = 0.05, 3, 150.0


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 4), round(c + h, 4)]


def sign_test(wins, losses):
    n = wins + losses
    if n == 0:
        return 1.0
    k = min(wins, losses)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def reference(d, radius):
    X, C = d["dense"], d["C"]
    lo = np.minimum(X[:, [0, 2]].min(0), C[:, [0, 2]].min(0)) - 1.0
    hi = np.maximum(X[:, [0, 2]].max(0), C[:, [0, 2]].max(0)) + 1.0
    if ((hi - lo) > MAX_EXTENT_M).any():  # outlier splats/cameras: robust bounds, refuse if still implausible
        lo = np.minimum(np.percentile(X[:, [0, 2]], 1, 0), np.percentile(C[:, [0, 2]], 2, 0)) - 1.0
        hi = np.maximum(np.percentile(X[:, [0, 2]], 99, 0), np.percentile(C[:, [0, 2]], 98, 0)) + 1.0
        if ((hi - lo) > MAX_EXTENT_M).any():
            raise ValueError(f"implausible reference extent {np.round(hi - lo, 1)} m; check posing/alignment")
        X = X[np.all((X[:, [0, 2]] >= lo) & (X[:, [0, 2]] < hi), axis=1)]
    nx, nz = (int(v) for v in np.ceil((hi - lo) / REF_CELL))
    ij = np.floor((X[:, [0, 2]] - lo) / REF_CELL).astype(int)
    occ = np.zeros((nx, nz), np.int32)
    np.add.at(occ, (ij[:, 0], ij[:, 1]), 1)
    edt = ndimage.distance_transform_edt(~(occ >= REF_MIN_SPLATS)) * REF_CELL
    margin = REF_CELL * math.sqrt(2) / 2  # a sample anywhere in a cell is within this of the cell centre
    free = edt >= radius + margin
    idx = -np.ones((nx, nz), np.int64)
    idx[free] = np.arange(free.sum())
    rows, cols, w = [], [], []
    for di, dk, wt in ((1, 0, 1.0), (0, 1, 1.0), (1, 1, math.sqrt(2)), (1, -1, math.sqrt(2))):
        k0, k1 = (0, nz - dk) if dk >= 0 else (-dk, nz)
        src = (slice(0, nx - di), slice(k0, k1))
        dst = (slice(di, nx), slice(k0 + dk, k1 + dk))
        m = free[src] & free[dst]
        if di and dk:  # no diagonal corner-cutting (same rule as the candidate A*)
            m &= free[(slice(di, nx), slice(k0, k1))] & free[(slice(0, nx - di), slice(k0 + dk, k1 + dk))]
        rows.append(idx[src][m]); cols.append(idx[dst][m]); w.append(np.full(int(m.sum()), wt * REF_CELL))
    G = sparse.coo_matrix((np.concatenate(w), (np.concatenate(rows), np.concatenate(cols))),
                          shape=(free.sum(), free.sum())).tocsr()
    return {"lo": lo, "nx": nx, "nz": nz, "edt": edt, "free": free, "idx": idx, "G": G, "radius": radius,
            "margin": margin}


def endpoints(ref, C, cams, search=0.5):
    out = {}
    fi, fk = np.nonzero(ref["free"])
    centres = ref["lo"] + (np.stack([fi, fk], 1) + 0.5) * REF_CELL
    for c in cams:
        dd = np.linalg.norm(centres - C[c][[0, 2]], axis=1)
        j = int(np.argmin(dd))
        if dd[j] <= search:
            out[int(c)] = (centres[j], int(ref["idx"][fi[j], fk[j]]))
    return out


def evaluate_one(d, ref, offset=0, buffer=2, holdout_every=8, use_carving=True, use_trajectory=True,
                 params=None, max_snap_m=0.25):
    P, C, oi, op, rank = d["P"], d["C"], d["obs_img"], d["obs_pt"], d["rank"]
    test = rank % holdout_every == offset
    near = np.zeros(len(C), bool)
    for t in rank[test]:
        near[(rank >= t - buffer) & (rank <= t + buffer)] = True
    train = ~near
    m = train[oi]
    oc, opp = oi[m], op[m]
    keep = np.bincount(opp, minlength=len(P)) >= 2
    remap = -np.ones(len(P), np.int64)
    remap[keep] = np.arange(keep.sum())
    mm = keep[opp]
    g = build_grid(P[keep], C[train], C[oc[mm]] if use_carving else None, remap[opp[mm]] if use_carving else None,
                   use_carving=use_carving, use_trajectory=use_trajectory, params=params)
    ep = endpoints(ref, C, np.where(test)[0])
    cams = sorted(ep)
    dist = csgraph.dijkstra(ref["G"], directed=False, indices=[ep[c][1] for c in cams])
    pl = GridPlanner(g["navigable"], g["clearance"], g["lo"], g["cell"])
    r_need = ref["radius"] + ref["margin"]
    outcomes, stretches = {}, []
    for i, a in enumerate(cams):
        for b in cams[i + 1:]:
            geo = dist[i, ep[b][1]]
            if not np.isfinite(geo) or geo <= 0:
                continue
            ea, eb = ep[a][0], ep[b][0]
            r = pl.plan(ea, eb)
            if not r["ok"] or max(np.linalg.norm(r["xz"][0] - ea), np.linalg.norm(r["xz"][-1] - eb)) > max_snap_m:
                outcomes[f"{a}-{b}"] = "refuse"
                continue
            poly = densify(np.vstack([ea, r["xz"], eb]), step=0.025)
            ij = np.floor((poly - ref["lo"]) / REF_CELL).astype(int)
            inb = (ij[:, 0] >= 0) & (ij[:, 0] < ref["nx"]) & (ij[:, 1] >= 0) & (ij[:, 1] < ref["nz"])
            collide = (not inb.all()) or bool((ref["edt"][ij[:, 0], ij[:, 1]] < r_need).any())
            outcomes[f"{a}-{b}"] = "collide" if collide else "ok"
            if not collide:
                stretches.append(float(np.linalg.norm(np.diff(poly, axis=0), axis=1).sum() / geo))
    n = len(outcomes)
    k_ok = sum(v == "ok" for v in outcomes.values())
    k_ref = sum(v == "refuse" for v in outcomes.values())
    k_col = n - k_ok - k_ref
    return {"n_heldout": int(test.sum()), "n_endpoints": len(cams), "n_pairs": n,
            "CFC": k_ok / n if n else None, "CFC_wilson95": wilson(k_ok, n),
            "CFC_camera_bootstrap95": camera_bootstrap(outcomes) if n else None,
            "refusal_rate": k_ref / n if n else None, "collision_rate": k_col / n if n else None,
            "stretch_median": float(np.median(stretches)) if stretches else None,
            "stretch_p90": float(np.percentile(stretches, 90)) if stretches else None,
            "area_navigable_m2": float(g["navigable"].sum() * g["cell"] ** 2), "outcomes": outcomes}


def compare(o1, o2):
    keys = sorted(set(o1) & set(o2))
    w = sum(o1[k] == "ok" and o2[k] != "ok" for k in keys)
    l = sum(o1[k] != "ok" and o2[k] == "ok" for k in keys)
    return {"pairs": len(keys), "wins": w, "losses": l, "sign_test_p": round(sign_test(w, l), 4)}


def camera_bootstrap(outcomes, n_boot=2000, seed=0):
    """95% CI for CFC that respects shared-endpoint dependence: resample endpoint CAMERAS with replacement and
    weight each pair (a, b) by count(a) * count(b). Pair-level Wilson intervals are too narrow (gpt-6-sol review)."""
    pairs = [tuple(int(x) for x in k.split("-")) + (v == "ok",) for k, v in outcomes.items()]
    cams = sorted({c for a, b, _ in pairs for c in (a, b)})
    pos = {c: i for i, c in enumerate(cams)}
    A = np.array([pos[a] for a, _, _ in pairs])
    B = np.array([pos[b] for _, b, _ in pairs])
    ok = np.array([o for _, _, o in pairs], float)
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n_boot):
        cnt = np.bincount(rng.integers(0, len(cams), len(cams)), minlength=len(cams)).astype(float)
        w = cnt[A] * cnt[B]
        if w.sum() > 0:
            vals.append(float((w * ok).sum() / w.sum()))
    return [round(float(np.percentile(vals, 2.5)), 4), round(float(np.percentile(vals, 97.5)), 4)]


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--colmap", default=os.path.join(ROOT, ".data/deepblending/drjohnson/sparse/0"))
    ap.add_argument("--alignment", default=os.path.join(ROOT, ".data/packages/drjohnson/alignment.json"))
    ap.add_argument("--ply", default=os.path.join(ROOT, ".data/runs/drjohnson_brush/drjohnson_15000.ply"))
    ap.add_argument("--radius", type=float, default=0.25)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    d = prepare(a.colmap, a.alignment, a.ply)
    ref = reference(d, a.radius)
    variants = {"points_only": (False, False), "points+carving": (True, False),
                "points+trajectory": (False, True), "full": (True, True)}
    res = {}
    for name, (uc, ut) in variants.items():
        res[name] = {s: evaluate_one(d, ref, offset=o, use_carving=uc, use_trajectory=ut) for s, o in (("A", 0), ("B", 4))}
        print(name, json.dumps({s: {k: v for k, v in res[name][s].items() if k in ("n_pairs", "CFC", "CFC_wilson95",
                                                                                   "refusal_rate", "collision_rate", "stretch_median")}
                                for s in "AB"}), flush=True)
    paired = {f"{v}_vs_points_only_{s}": compare(res[v][s]["outcomes"], res["points_only"][s]["outcomes"])
              for v in variants if v != "points_only" for s in "AB"}
    print("paired", json.dumps(paired))
    if a.out:
        json.dump({"protocol": "nav_eval_v3 (see docstring)", "radius_m": a.radius, "reference_cells": [ref["nx"], ref["nz"]],
                   "reference_free_cells": int(ref["free"].sum()), "dense_proxy_splats": int(len(d["dense"])),
                   "variants": res, "paired_vs_points_only": paired,
                   "reproduce": "cd namma-space && .venv/bin/python eval/nav_eval_v3.py --out eval/results/drjohnson_nav_v3.json"},
                  open(a.out, "w"), indent=1)
