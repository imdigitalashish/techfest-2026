#!/usr/bin/env python3
"""End-to-end navigation-geometry eval on Deep Blending *drjohnson* (public multi-room house).

COLMAP model -> scene_alignment -> walkable_space (4 evidence variants) -> path_planner, scored
against a dense proxy obstacle map built from the trained 3DGS splats (opacity > OPA_MIN, max scale
< 0.2 m, body band 0.15-1.7 m). The dense proxy is NOT ground truth; it is an independent,
denser geometry estimate from the same photos. Brush stores opacity as logits; on drjohnson the
p99 activated opacity is ~0.42, so OPA_MIN = 0.1 (0.5 kept only 0.16% of splats).
Held-out split: every 8th camera (same convention as the splat eval split).
Reproduce:  cd namma-space && .venv/bin/python eval/run_nav_e2e.py
"""
import json
import os
import platform
import sys
import time

import numpy as np
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "components"))
from path_planner.planner import GridPlanner, densify  # noqa: E402
from scene_alignment.align import apply, estimate_alignment, load_colmap  # noqa: E402
from walkable_space.walkable import build_grid, to_json  # noqa: E402

COLMAP = os.path.join(ROOT, ".data/deepblending/drjohnson/sparse/0")
PLY = os.path.join(ROOT, ".data/runs/drjohnson_brush/drjohnson_15000.ply")
OUT = os.path.join(ROOT, "eval/results")
PKG = os.path.join(ROOT, ".data/packages/drjohnson")
R_COLLIDE = 0.15
OPA_MIN = 0.1
N_PAIRS = 40


def read_ply(path, fields):
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
    return n, {k: np.asarray(arr[k], dtype=np.float32) for k in fields}


def evaluate(g, C, test, dense_xyz, pairs):
    lo, cell, nx, nz = g["lo"], g["cell"], g["nx"], g["nz"]
    ij = np.floor((dense_xyz[:, [0, 2]] - lo) / cell).astype(int)
    ok = (ij[:, 0] >= 0) & (ij[:, 0] < nx) & (ij[:, 1] >= 0) & (ij[:, 1] < nz)
    D = np.zeros((nx, nz), np.int32)
    np.add.at(D, (ij[ok, 0], ij[ok, 1]), 1)
    ddist = ndimage.distance_transform_edt(~(D >= 3)) * cell
    N, W = g["navigable"], g["walkable"]
    tij = np.floor((C[test][:, [0, 2]] - lo) / cell).astype(int)
    tij[:, 0] = np.clip(tij[:, 0], 0, nx - 1)
    tij[:, 1] = np.clip(tij[:, 1], 0, nz - 1)
    pl = GridPlanner(N, g["clearance"], lo, cell)
    rows = []
    for a, b in pairs:
        sa, sb = C[a][[0, 2]], C[b][[0, 2]]
        r = pl.plan(sa, sb)
        if not r["ok"]:
            rows.append({"ok": False, "ms": r["ms"]})
            continue
        pts = densify(r["xz"])
        pij = np.floor((pts - lo) / cell).astype(int)
        dd = ddist[np.clip(pij[:, 0], 0, nx - 1), np.clip(pij[:, 1], 0, nz - 1)]
        rows.append({"ok": True, "ms": r["ms"], "len": r["length_m"],
                     "straight": float(np.linalg.norm(sb - sa)),
                     "snap": float(max(np.linalg.norm(r["xz"][0] - sa), np.linalg.norm(r["xz"][-1] - sb))),
                     "coll": bool((dd < R_COLLIDE).any()), "coll_frac": float((dd < R_COLLIDE).mean())})
    good = [x for x in rows if x["ok"] and x["snap"] <= 1.0]
    ms = np.array([x["ms"] for x in rows])
    return {
        "area_walkable_m2": float(W.sum() * cell * cell), "area_navigable_m2": float(N.sum() * cell * cell),
        "heldout_recall_walkable": float(W[tij[:, 0], tij[:, 1]].mean()),
        "heldout_recall_navigable": float(N[tij[:, 0], tij[:, 1]].mean()),
        "navigable_cells_within_15cm_of_dense_obstacle": float((ddist[N] < R_COLLIDE).mean()) if N.any() else None,
        "pairs": len(pairs), "success_rate": len(good) / len(pairs),
        "path_collision_rate": (sum(x["coll"] for x in good) / len(good)) if good else None,
        "path_samples_in_collision": float(np.mean([x["coll_frac"] for x in good])) if good else None,
        "length_ratio_median": float(np.median([x["len"] / max(x["straight"], 1e-6) for x in good])) if good else None,
        "plan_ms_median": float(np.median(ms)), "plan_ms_p95": float(np.percentile(ms, 95)),
        "grid_build_s": g["runtime_s"], "ray_samples": g["n_ray_samples"], "grid_cells": [g["nx"], g["nz"]],
    }


def save_png(g, C, train, test, paths, path):
    from PIL import Image, ImageDraw
    img = np.full((g["nz"], g["nx"], 3), 110, np.uint8)
    img[g["walkable"].T] = (225, 225, 225)
    img[g["navigable"].T] = (190, 235, 190)
    img[g["obstacle"].T] = (25, 25, 25)
    im = Image.fromarray(img).resize((g["nx"] * 2, g["nz"] * 2), Image.NEAREST)
    dr = ImageDraw.Draw(im)
    px = lambda xz: tuple(((np.asarray(xz) - g["lo"]) / g["cell"] * 2).tolist())
    for xz in paths:
        dr.line([px(p) for p in xz], fill=(255, 120, 0), width=3)
    for c, col in ((C[train], (40, 90, 220)), (C[test], (220, 30, 30))):
        for p in c[:, [0, 2]]:
            x, y = px(p)
            dr.ellipse([x - 3, y - 3, x + 3, y + 3], fill=col)
    im.save(path)


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PKG, exist_ok=True)
    t0 = time.perf_counter()
    sc = load_colmap(COLMAP)
    t_load = time.perf_counter() - t0
    al = estimate_alignment(sc)
    T, s = np.array(al["T_aligned_from_colmap"]), al["scale"]
    P, C = apply(T, sc.points), apply(T, sc.centers)
    test = np.arange(len(C)) % 8 == 0
    train = ~test
    m = train[sc.obs_img_idx]
    oc, op = sc.obs_img_idx[m], sc.obs_pt_idx[m]
    keep = np.bincount(op, minlength=len(P)) >= 2
    remap = -np.ones(len(P), np.int64)
    remap[keep] = np.arange(keep.sum())
    mm = keep[op]
    rays_from, rays_to, Pk = C[oc[mm]], remap[op[mm]], P[keep]
    t1 = time.perf_counter()
    n_splats, v = read_ply(PLY, ["x", "y", "z", "opacity", "scale_0", "scale_1", "scale_2"])
    X = apply(T, np.stack([v["x"], v["y"], v["z"]], 1))
    opa = 1 / (1 + np.exp(-v["opacity"]))
    smax = np.exp(np.max(np.stack([v["scale_0"], v["scale_1"], v["scale_2"]], 1), 1)) * s
    dense = X[(opa > OPA_MIN) & (smax < 0.2) & (X[:, 1] > 0.15) & (X[:, 1] < 1.7)]
    t_ply = time.perf_counter() - t1
    te = np.where(test)[0]
    allp = [(a, b) for i, a in enumerate(te) for b in te[i + 1:]]
    rng = np.random.default_rng(0)
    pairs = [allp[i] for i in rng.choice(len(allp), size=min(N_PAIRS, len(allp)), replace=False)]
    variants = {"points_only": (False, False), "points+carving": (True, False),
                "points+trajectory": (False, True), "full(carving+trajectory)": (True, True)}
    res = {}
    for name, (uc, ut) in variants.items():
        g = build_grid(Pk, C[train], rays_from if uc else None, rays_to if uc else None,
                       use_carving=uc, use_trajectory=ut)
        res[name] = evaluate(g, C, test, dense, pairs)
        print(name, json.dumps({k: (round(x, 3) if isinstance(x, float) else x) for k, x in res[name].items()}))
    pl = GridPlanner(g["navigable"], g["clearance"], g["lo"], g["cell"])
    demo = [pl.plan(C[a][[0, 2]], C[b][[0, 2]]) for a, b in pairs[:6]]
    save_png(g, C, train, test, [d["xz"] for d in demo if d["ok"]], os.path.join(OUT, "drjohnson_floorplan.png"))
    with open(os.path.join(PKG, "nav.json"), "w") as f:
        json.dump(to_json(g), f)
    with open(os.path.join(PKG, "alignment.json"), "w") as f:
        json.dump(al, f, indent=1)
    import pycolmap
    import scipy
    out = {"dataset": "Deep Blending drjohnson via HF nvs-bench/deepblending (COLMAP poses shipped)",
           "machine": f"{platform.machine()} {platform.mac_ver()[0]} (shared Apple M5, 24 GB)",
           "versions": {"python": platform.python_version(), "numpy": np.__version__,
                        "scipy": scipy.__version__, "pycolmap": pycolmap.__version__},
           "n_images": len(C), "n_train": int(train.sum()), "n_test": int(test.sum()),
           "n_points3D": int(len(P)), "n_points_used": int(len(Pk)), "n_rays": int(len(rays_to)),
           "n_splats": int(n_splats), "n_dense_proxy_splats": int(len(dense)),
           "timings_s": {"colmap_load": t_load, "alignment": al["runtime_s"], "ply_read": t_ply},
           "alignment": {k: x for k, x in al.items() if k != "T_aligned_from_colmap"},
           "collision_radius_m": R_COLLIDE, "variants": res,
           "reproduce": "cd namma-space && .venv/bin/python eval/run_nav_e2e.py"}
    with open(os.path.join(OUT, "drjohnson_nav.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("ALIGN", json.dumps(out["alignment"]))
    print("META", json.dumps({k: out[k] for k in ("n_images", "n_points3D", "n_points_used", "n_rays", "n_splats",
                                                  "n_dense_proxy_splats", "timings_s")}))


if __name__ == "__main__":
    main()
