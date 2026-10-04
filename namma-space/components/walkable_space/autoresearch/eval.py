#!/usr/bin/env python3
"""FROZEN evaluator for the walkable-space ratchet. The loop must never edit this file.

Prints one scalar `score J = recall_nav - path_collision_rate` (higher is better) + secondaries.
  recall_nav           share of held-out camera floor positions inside the navigable map
                       (the photographer physically stood there, so it must be walkable)
  path_collision_rate  share of held-out start->goal paths passing < 0.15 m from the dense proxy
                       (3DGS splats: opacity > 0.1, max scale < 0.2 m, body band 0.15-1.7 m, >= 3 per 5 cm cell)
Anti-gaming: agent_radius / agent_height / step_height / cell are forced here; success must stay 1.0
(else J = -1); proxy sanity reported as `proxy_hits_at_heldout_cams` (should stay ~0).
Splits: A = every 8th image (offset 0), B = every 8th image offset 4 (confirmation split).
Usage: python eval.py --params params.json --split A
"""
import argparse
import json
import os
import sys
import time

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))  # namma-space/
sys.path.insert(0, os.path.join(ROOT, "components"))
from path_planner.planner import GridPlanner, densify  # noqa: E402
from walkable_space.walkable import build_grid  # noqa: E402

FORCED = dict(cell=0.05, agent_radius=0.25, agent_height=1.70, step_height=0.15)
R_COLLIDE, N_PAIRS, OPA_MIN = 0.15, 40, 0.1
CACHE = os.path.join(ROOT, ".cache", "walkable_eval_drjohnson.npz")
COLMAP = os.path.join(ROOT, ".data/deepblending/drjohnson/sparse/0")
PLY = os.path.join(ROOT, ".data/runs/drjohnson_brush/drjohnson_15000.ply")
ALIGN = os.path.join(ROOT, ".data/packages/drjohnson/alignment.json")


def build_cache():
    from scene_alignment.align import apply, load_colmap
    sys.path.insert(0, os.path.join(ROOT, "eval"))
    from run_nav_e2e import read_ply
    sc = load_colmap(COLMAP)
    al = json.load(open(ALIGN))
    T, s = np.array(al["T_aligned_from_colmap"]), al["scale"]
    P, C = apply(T, sc.points), apply(T, sc.centers)
    _, v = read_ply(PLY, ["x", "y", "z", "opacity", "scale_0", "scale_1", "scale_2"])
    X = apply(T, np.stack([v["x"], v["y"], v["z"]], 1))
    opa = 1 / (1 + np.exp(-v["opacity"]))
    smax = np.exp(np.max(np.stack([v["scale_0"], v["scale_1"], v["scale_2"]], 1), 1)) * s
    dense = X[(opa > OPA_MIN) & (smax < 0.2) & (X[:, 1] > 0.15) & (X[:, 1] < 1.7)]
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    np.savez_compressed(CACHE, P=P, C=C, obs_img=sc.obs_img_idx, obs_pt=sc.obs_pt_idx, dense=dense.astype(np.float32))


def run(params, split):
    if not os.path.exists(CACHE):
        build_cache()
    d = np.load(CACHE)
    P, C, oi, op, dense = d["P"], d["C"], d["obs_img"], d["obs_pt"], d["dense"]
    off = {"A": 0, "B": 4}[split]
    test = (np.arange(len(C)) % 8) == off
    train = ~test
    m = train[oi]
    oc, opp = oi[m], op[m]
    keep = np.bincount(opp, minlength=len(P)) >= 2
    remap = -np.ones(len(P), np.int64)
    remap[keep] = np.arange(keep.sum())
    mm = keep[opp]
    p = dict(params)
    p.update(FORCED)
    use_c, use_t = p.pop("use_carving", True), p.pop("use_trajectory", True)
    t0 = time.perf_counter()
    g = build_grid(P[keep], C[train], C[oc[mm]] if use_c else None, remap[opp[mm]] if use_c else None,
                   use_carving=use_c, use_trajectory=use_t, params=p)
    build_s = time.perf_counter() - t0
    lo, cell, nx, nz = g["lo"], g["cell"], g["nx"], g["nz"]
    ij = np.floor((dense[:, [0, 2]] - lo) / cell).astype(int)
    ok = (ij[:, 0] >= 0) & (ij[:, 0] < nx) & (ij[:, 1] >= 0) & (ij[:, 1] < nz)
    D = np.zeros((nx, nz), np.int32)
    np.add.at(D, (ij[ok, 0], ij[ok, 1]), 1)
    ddist = ndimage.distance_transform_edt(~(D >= 3)) * cell
    clip = lambda a: (np.clip(a[:, 0], 0, nx - 1), np.clip(a[:, 1], 0, nz - 1))
    tij = clip(np.floor((C[test][:, [0, 2]] - lo) / cell).astype(int))
    recall = float(g["navigable"][tij].mean())
    proxy_hits = float((ddist[tij] < R_COLLIDE).mean())
    te = np.where(test)[0]
    allp = [(a, b) for i, a in enumerate(te) for b in te[i + 1:]]
    pairs = [allp[i] for i in np.random.default_rng(0).choice(len(allp), size=min(N_PAIRS, len(allp)), replace=False)]
    pl = GridPlanner(g["navigable"], g["clearance"], lo, cell)
    n_ok, n_coll, ratios = 0, 0, []
    for a, b in pairs:
        r = pl.plan(C[a][[0, 2]], C[b][[0, 2]])
        if not r["ok"]:
            continue
        sa, sb = C[a][[0, 2]], C[b][[0, 2]]
        if max(np.linalg.norm(r["xz"][0] - sa), np.linalg.norm(r["xz"][-1] - sb)) > 1.0:
            continue
        n_ok += 1
        pts = np.floor((densify(r["xz"]) - lo) / cell).astype(int)
        n_coll += bool((ddist[clip(pts)] < R_COLLIDE).any())
        ratios.append(r["length_m"] / max(np.linalg.norm(sb - sa), 1e-6))
    success = n_ok / len(pairs)
    coll = n_coll / max(n_ok, 1)
    J = recall - coll if success == 1.0 else -1.0
    return {"J": J, "recall_nav": recall, "path_collision_rate": coll, "success": success,
            "length_ratio_median": float(np.median(ratios)) if ratios else None,
            "proxy_hits_at_heldout_cams": proxy_hits, "area_navigable_m2": float(g["navigable"].sum() * cell * cell),
            "build_s": build_s, "split": split, "n_test": int(test.sum()), "pairs": len(pairs)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--params", default=os.path.join(HERE, "params.json"))
    ap.add_argument("--split", default="A", choices=["A", "B"])
    a = ap.parse_args()
    res = run(json.load(open(a.params)), a.split)
    print(f"score {res['J']:.4f}")
    print(json.dumps(res))
