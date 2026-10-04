#!/usr/bin/env python3
"""Path-safety evaluation v2 (fixes from the independent review of ADR 001, 2026-10-04).

Changes vs v1 (eval/run_nav_e2e.py):
  * buffered hold-out: every 8th frame (by capture order) is held out, and frames within +-`buffer` of a
    held-out frame are removed from the map-building set, so the trajectory prior cannot "see" the
    held-out positions through their immediate neighbours (leakage fix);
  * a route counts only if both snap distances (true start/goal -> nearest navigable cell) are <= 0.25 m,
    and collisions are checked on the full polyline INCLUDING the connectors from the true endpoints;
  * clearance is checked at the agent radius (0.25 m) as well as 0.15 m; the first/last 0.30 m of each
    route are excluded (the camera's floor projection can sit next to furniture);
  * one continuous primary score, CFC@0.25 = share of held-out pairs with a valid, collision-free route
    (no -1 cliff; refusing a route costs exactly as much as a colliding one);
  * reports the proxy noise floor (held-out camera positions within 0.15 m of a proxy obstacle).
The dense proxy is NOT ground truth: 3DGS splats from the same photos (opacity > 0.1, max scale < 0.2 m,
0.15-1.70 m band, >= 3 splats per 5 cm cell).
"""
import json
import os
import sys

import numpy as np
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "components"))
from path_planner.planner import GridPlanner, densify  # noqa: E402
from scene_alignment.align import apply, load_colmap  # noqa: E402
from walkable_space.walkable import build_grid  # noqa: E402


def read_ply_fields(path, fields):
    types = {"float": "<f4", "float32": "<f4", "double": "<f8", "uchar": "u1", "uint8": "u1", "int": "<i4"}
    with open(path, "rb") as f:
        hdr = []
        while True:
            line = f.readline().decode("ascii", "ignore").strip()
            hdr.append(line)
            if line == "end_header":
                break
        off = f.tell()
    n, props, inv = 0, [], False
    for line in hdr:
        t = line.split()
        if t[:2] == ["element", "vertex"]:
            n, inv = int(t[2]), True
        elif t and t[0] == "element":
            inv = False
        elif t and t[0] == "property" and inv:
            props.append((t[2], types[t[1]]))
    arr = np.memmap(path, dtype=np.dtype(props), mode="r", offset=off, shape=(n,))
    return {k: np.asarray(arr[k], dtype=np.float32) for k in fields}


def prepare(colmap_dir, alignment, ply_path, opa_min=0.1, smax_m=0.2, band=(0.15, 1.70)):
    sc = load_colmap(colmap_dir)
    al = json.load(open(alignment)) if isinstance(alignment, str) else alignment
    T, s = np.array(al["T_aligned_from_colmap"]), float(al["scale"])
    v = read_ply_fields(ply_path, ["x", "y", "z", "opacity", "scale_0", "scale_1", "scale_2"])
    X = apply(T, np.stack([v["x"], v["y"], v["z"]], 1))
    opa = 1 / (1 + np.exp(-v["opacity"]))
    smax = np.exp(np.max(np.stack([v["scale_0"], v["scale_1"], v["scale_2"]], 1), 1)) * s
    dense = X[(opa > opa_min) & (smax < smax_m) & (X[:, 1] > band[0]) & (X[:, 1] < band[1])]
    order = np.argsort(np.array(sc.names))
    rank = np.empty_like(order)
    rank[order] = np.arange(len(order))
    return {"P": apply(T, sc.points), "C": apply(T, sc.centers), "obs_img": sc.obs_img_idx, "obs_pt": sc.obs_pt_idx,
            "rank": rank, "dense": dense.astype(np.float32), "names": sc.names}


def evaluate(d, params=None, holdout_every=8, offset=0, buffer=2, n_pairs=40, seed=0, radii=(0.15, 0.25),
             max_snap_m=0.25, end_exclude_m=0.30, use_carving=True, use_trajectory=True):
    P, C, oi, op, rank, dense = d["P"], d["C"], d["obs_img"], d["obs_pt"], d["rank"], d["dense"]
    n = len(C)
    test = rank % holdout_every == offset
    near = np.zeros(n, bool)
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
    lo, cell, nx, nz = g["lo"], g["cell"], g["nx"], g["nz"]
    ij = np.floor((dense[:, [0, 2]] - lo) / cell).astype(int)
    ok = (ij[:, 0] >= 0) & (ij[:, 0] < nx) & (ij[:, 1] >= 0) & (ij[:, 1] < nz)
    D = np.zeros((nx, nz), np.int32)
    np.add.at(D, (ij[ok, 0], ij[ok, 1]), 1)
    ddist = ndimage.distance_transform_edt(~(D >= 3)) * cell
    clip = lambda a: (np.clip(a[:, 0], 0, nx - 1), np.clip(a[:, 1], 0, nz - 1))
    te = np.where(test)[0]
    tij = clip(np.floor((C[te][:, [0, 2]] - lo) / cell).astype(int))
    allp = [(a, b) for i, a in enumerate(te) for b in te[i + 1:]]
    pairs = [allp[i] for i in np.random.default_rng(seed).choice(len(allp), size=min(n_pairs, len(allp)), replace=False)]
    pl = GridPlanner(g["navigable"], g["clearance"], lo, cell)
    rows = []
    for a, b in pairs:
        sa, sb = C[a][[0, 2]], C[b][[0, 2]]
        r = pl.plan(sa, sb)
        if not r["ok"]:
            rows.append({"valid": False, "why": "no_path"})
            continue
        snap = max(np.linalg.norm(r["xz"][0] - sa), np.linalg.norm(r["xz"][-1] - sb))
        if snap > max_snap_m:
            rows.append({"valid": False, "why": "snap", "snap_m": float(snap)})
            continue
        poly = densify(np.vstack([sa, r["xz"], sb]), step=0.025)
        sarc = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(poly, axis=0), axis=1))])
        inner = (sarc >= end_exclude_m) & (sarc <= sarc[-1] - end_exclude_m)
        dmin = float(ddist[clip(np.floor((poly[inner] - lo) / cell).astype(int))].min()) if inner.any() else 9.9
        rows.append({"valid": True, "dmin": dmin, "len": float(sarc[-1]), "straight": float(np.linalg.norm(sb - sa)),
                     "ms": r["ms"]})
    valid = [x for x in rows if x["valid"]]
    out = {"n_heldout": int(test.sum()), "n_map_frames": int(train.sum()), "buffer": buffer, "pairs": len(pairs),
           "success": len(valid) / len(pairs),
           "recall_buffered": float(g["navigable"][tij].mean()),
           "proxy_noise_floor_015": float((ddist[tij] < 0.15).mean()),
           "length_ratio_median": float(np.median([x["len"] / max(x["straight"], 1e-6) for x in valid])) if valid else None,
           "plan_ms_median": float(np.median([x["ms"] for x in valid])) if valid else None,
           "area_navigable_m2": float(g["navigable"].sum() * cell * cell),
           "fail_reasons": {k: sum(1 for x in rows if not x["valid"] and x["why"] == k) for k in ("no_path", "snap")}}
    for rr in radii:
        out[f"CFC@{rr:.2f}"] = sum(1 for x in valid if x["dmin"] >= rr) / len(pairs)
    out["score"] = out["CFC@0.25"] if "CFC@0.25" in out else out[f"CFC@{radii[-1]:.2f}"]
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--colmap", default=os.path.join(ROOT, ".data/deepblending/drjohnson/sparse/0"))
    ap.add_argument("--alignment", default=os.path.join(ROOT, ".data/packages/drjohnson/alignment.json"))
    ap.add_argument("--ply", default=os.path.join(ROOT, ".data/runs/drjohnson_brush/drjohnson_15000.ply"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    d = prepare(a.colmap, a.alignment, a.ply)
    res = {}
    for name, (uc, ut) in {"points_only": (False, False), "points+carving": (True, False),
                           "points+trajectory": (False, True), "full": (True, True)}.items():
        res[name] = {"A": evaluate(d, use_carving=uc, use_trajectory=ut, offset=0),
                     "B": evaluate(d, use_carving=uc, use_trajectory=ut, offset=4)}
        print(name, json.dumps({s: {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res[name][s].items()
                                    if k in ("score", "CFC@0.15", "success", "recall_buffered", "proxy_noise_floor_015")}
                                for s in "AB"}))
    if a.out:
        json.dump({"protocol": "nav_eval_v2 (see docstring)", "dense_proxy_splats": int(len(d["dense"])),
                   "variants": res, "reproduce": "cd namma-space && .venv/bin/python eval/nav_eval_v2.py --out eval/results/drjohnson_nav_v2.json"},
                  open(a.out, "w"), indent=1)
