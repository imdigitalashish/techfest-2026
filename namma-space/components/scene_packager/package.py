#!/usr/bin/env python3
"""Scene packager: Brush/INRIA 3DGS PLY + alignment + NavGrid -> web ScenePackage.

Writes <out>/scene.splat (antimatter15 layout, 32 B/splat: pos f32x3, scale f32x3, rgba u8x4,
quat wxyz u8x4), baked into the ALIGNED frame (y-up, floor y=0, metres), importance-pruned;
plus manifest.json (contract: ScenePackage in architecture/contracts/contracts.ts).
Usage: python components/scene_packager/package.py --ply X.ply --alignment A.json --nav N.json \
         --out .data/packages/<name> --max-splats 1000000 [--pois P.json]
"""
import argparse
import json
import os
import time

import numpy as np

SH_C0 = 0.28209479177387814


def read_ply(path):
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
    return np.memmap(path, dtype=np.dtype(props), mode="r", offset=off, shape=(n,))


def quat_from_matrix(R):
    w = np.sqrt(max(0.0, 1.0 + R[0, 0] + R[1, 1] + R[2, 2])) / 2.0
    x = np.copysign(np.sqrt(max(0.0, 1.0 + R[0, 0] - R[1, 1] - R[2, 2])) / 2.0, R[2, 1] - R[1, 2])
    y = np.copysign(np.sqrt(max(0.0, 1.0 - R[0, 0] + R[1, 1] - R[2, 2])) / 2.0, R[0, 2] - R[2, 0])
    z = np.copysign(np.sqrt(max(0.0, 1.0 - R[0, 0] - R[1, 1] + R[2, 2])) / 2.0, R[1, 0] - R[0, 1])
    q = np.array([w, x, y, z])
    return q / np.linalg.norm(q)


def quat_mul(a, b):  # a (4,), b (N,4), wxyz
    w1, x1, y1, z1 = a
    w2, x2, y2, z2 = b[:, 0], b[:, 1], b[:, 2], b[:, 3]
    return np.stack([w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2, w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                     w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2, w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2], 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ply", required=True)
    ap.add_argument("--alignment", required=True)
    ap.add_argument("--nav", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", default="scene")
    ap.add_argument("--pois", default=None)
    ap.add_argument("--max-splats", type=int, default=1_000_000)
    ap.add_argument("--min-opacity", type=float, default=0.02)
    ap.add_argument("--max-scale-m", type=float, default=1.5)
    ap.add_argument("--credits", default="")
    a = ap.parse_args()
    t0 = time.perf_counter()
    v = read_ply(a.ply)
    al = json.load(open(a.alignment))
    T = np.array(al["T_aligned_from_colmap"])
    s = float(al["scale"])
    R = T[:3, :3] / s
    pos = np.stack([v["x"], v["y"], v["z"]], 1).astype(np.float64)
    pos = (T[:3, :3] @ pos.T).T + T[:3, 3]
    logsc = np.stack([v["scale_0"], v["scale_1"], v["scale_2"]], 1).astype(np.float64)
    scale = np.exp(logsc) * s
    opa = 1.0 / (1.0 + np.exp(-np.asarray(v["opacity"], np.float64)))
    keep = (opa >= a.min_opacity) & (scale.max(1) <= a.max_scale_m) & np.isfinite(pos).all(1)
    imp = np.where(keep, opa * np.prod(scale, 1) ** (2.0 / 3.0), -1.0)  # opacity x projected area
    order = np.argsort(-imp)[: min(a.max_splats, int(keep.sum()))]
    q = np.stack([v["rot_0"], v["rot_1"], v["rot_2"], v["rot_3"]], 1).astype(np.float64)[order]
    q /= np.linalg.norm(q, axis=1, keepdims=True) + 1e-12
    q = quat_mul(quat_from_matrix(R), q)
    q /= np.linalg.norm(q, axis=1, keepdims=True)
    rgb = 0.5 + SH_C0 * np.stack([v["f_dc_0"], v["f_dc_1"], v["f_dc_2"]], 1).astype(np.float64)[order]
    rgba = np.concatenate([rgb, opa[order, None]], 1)
    rec = np.zeros(len(order), dtype=[("p", "<f4", 3), ("s", "<f4", 3), ("c", "u1", 4), ("q", "u1", 4)])
    rec["p"] = pos[order]
    rec["s"] = scale[order]
    rec["c"] = np.clip(rgba * 255.0, 0, 255).astype(np.uint8)
    rec["q"] = np.clip(q * 128.0 + 128.0, 0, 255).astype(np.uint8)
    os.makedirs(a.out, exist_ok=True)
    splat_path = os.path.join(a.out, "scene.splat")
    rec.tofile(splat_path)
    nav = json.load(open(a.nav))
    N = np.unpackbits(np.frombuffer(__import__("base64").b64decode(nav["navigable_b64"]), np.uint8))[: nav["nx"] * nav["nz"]].reshape(nav["nx"], nav["nz"]).astype(bool)
    from scipy import ndimage
    dist = ndimage.distance_transform_edt(N)
    i, k = np.unravel_index(int(np.argmax(dist)), N.shape)
    spawn = [nav["lo_xz"][0] + (i + 0.5) * nav["cell_m"], 1.6, nav["lo_xz"][1] + (k + 0.5) * nav["cell_m"]]
    rel = lambda p: os.path.relpath(p, a.out)
    manifest = {
        "schema": "namma-space/scene@1", "name": a.name,
        "splat": {"url": "scene.splat", "format": "splat", "n_splats": int(len(order)),
                  "bytes": int(os.path.getsize(splat_path)), "frame": "aligned"},
        "nav": {"url": rel(a.nav)}, "pois": {"url": rel(a.pois) if a.pois else None},
        "spawn": {"position": spawn, "yaw_deg": 0.0}, "eye_height_m": 1.6,
        "scale_source": al.get("scale_source"), "credits": [c for c in a.credits.split("|") if c],
        "packager": {"input_splats": int(len(opa)), "kept_after_filters": int(keep.sum()),
                     "min_opacity": a.min_opacity, "max_scale_m": a.max_scale_m,
                     "seconds": round(time.perf_counter() - t0, 2)},
    }
    with open(os.path.join(a.out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1)
    print(json.dumps({k: manifest[k] for k in ("splat", "spawn", "packager")}))


if __name__ == "__main__":
    main()
