"""Scene alignment: COLMAP model -> gravity-aligned, floor-at-zero, metric-scaled frame (y-up).

Contract: in = COLMAP sparse model (+ optional camera_height_m from capture.json);
out = alignment.json with a 4x4 similarity T_aligned_from_colmap (row-major).
Baseline method: up = mean camera up (handheld upright capture, SOP rule) -> floor = lowest dense
height-histogram peak below the cameras, refined by SVD plane fit -> scale = camera height prior
(default 1.5 m, labelled ASSUMED) -> yaw = PCA of horizontal point spread.
"""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass

import numpy as np
import pycolmap

DEFAULT_CAMERA_HEIGHT_M = 1.5


@dataclass
class ColmapScene:
    names: list
    centers: np.ndarray
    ups: np.ndarray
    points: np.ndarray
    point_err: np.ndarray
    point_track: np.ndarray
    obs_img_idx: np.ndarray
    obs_pt_idx: np.ndarray


def _cfw(img):
    c = img.cam_from_world
    return c() if callable(c) else c


def load_colmap(path: str) -> ColmapScene:
    rec = pycolmap.Reconstruction(path)
    names, centers, ups, index = [], [], [], {}
    for iid, img in sorted(rec.images.items()):
        if hasattr(img, "has_pose") and not img.has_pose:
            continue
        T = _cfw(img)
        R = np.asarray(T.rotation.matrix())
        t = np.asarray(T.translation).reshape(3)
        index[iid] = len(names)
        names.append(img.name)
        centers.append(-R.T @ t)
        ups.append(R.T @ np.array([0.0, -1.0, 0.0]))
    pts, err, trk, oi, op = [], [], [], [], []
    for k, (_, p) in enumerate(sorted(rec.points3D.items())):
        pts.append(np.asarray(p.xyz))
        err.append(p.error)
        els = p.track.elements
        trk.append(len(els))
        for el in els:
            if el.image_id in index:
                oi.append(index[el.image_id])
                op.append(k)
    return ColmapScene(names, np.array(centers), np.array(ups), np.array(pts), np.array(err),
                       np.array(trk), np.array(oi, dtype=np.int64), np.array(op, dtype=np.int64))


def _n(v):
    return v / (np.linalg.norm(v) + 1e-12)


def _rot_a_to_b(a, b):
    a, b = _n(a), _n(b)
    v, c = np.cross(a, b), float(np.dot(a, b))
    if np.linalg.norm(v) < 1e-9:
        if c > 0:
            return np.eye(3)
        ax = _n(np.cross(a, [1, 0, 0] if abs(a[0]) < 0.9 else [0, 1, 0]))
        return 2 * np.outer(ax, ax) - np.eye(3)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx / (1.0 + c)


def estimate_alignment(sc: ColmapScene, camera_height_m: float | None = None,
                       max_err: float = 2.0, min_track: int = 3) -> dict:
    t0 = time.perf_counter()
    P = sc.points[(sc.point_err < max_err) & (sc.point_track >= min_track)]
    up0 = _n(sc.ups.mean(axis=0))
    consistency = float(np.linalg.norm(sc.ups.mean(axis=0)))
    unit = float(np.median(np.linalg.norm(P - np.median(sc.centers, axis=0), axis=1)))
    h = P @ up0
    hc_med = float(np.median(sc.centers @ up0))
    below = h < hc_med - 0.15 * unit
    hist, edges = np.histogram(h[below], bins=np.linspace(np.percentile(h, 0.5), hc_med, 120))
    mids = 0.5 * (edges[1:] + edges[:-1])
    cand = np.where(hist >= max(0.25 * hist.max(), 0.01 * below.sum()))[0]
    floor_h = float(mids[cand[0]]) if len(cand) else float(np.percentile(h, 2))
    tol = 0.03 * unit
    up = up0
    inl = np.abs(h - floor_h) < tol
    for _ in range(3):
        Q = P[inl]
        if len(Q) < 50:
            break
        c = Q.mean(axis=0)
        n = _n(np.linalg.svd(Q - c, full_matrices=False)[2][2])
        n = n if np.dot(n, up0) > 0 else -n
        if np.degrees(np.arccos(np.clip(np.dot(n, up0), -1, 1))) > 20:
            break
        up, floor_h = n, float(c @ n)
        inl = np.abs(P @ up - floor_h) < tol
    med_above = float(np.median(sc.centers @ up - floor_h))
    if camera_height_m is not None:
        H, src = float(camera_height_m), "capture.json camera_height_m"
    else:
        H, src = DEFAULT_CAMERA_HEIGHT_M, f"ASSUMED median camera height {DEFAULT_CAMERA_HEIGHT_M} m"
    s = H / med_above
    R_up = _rot_a_to_b(up, np.array([0.0, 1.0, 0.0]))
    xz = (R_up @ P.T).T[:, [0, 2]]
    xz = xz - xz.mean(axis=0)
    v0 = np.linalg.svd(xz[:: max(1, len(xz) // 20000)], full_matrices=False)[2][0]
    a = np.arctan2(v0[1], v0[0])
    R = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]]) @ R_up
    cm = np.median(sc.centers, axis=0)
    o = cm - (cm @ up - floor_h) * up
    T = np.eye(4)
    T[:3, :3] = s * R
    T[:3, 3] = -s * R @ o
    Pa, Ca = apply(T, P), apply(T, sc.centers)
    return {
        "T_aligned_from_colmap": T.tolist(), "scale": s, "scale_source": src,
        "up_colmap": up.tolist(), "up_camera_consistency": consistency,
        "up_refinement_deg": float(np.degrees(np.arccos(np.clip(np.dot(up, up0), -1, 1)))),
        "camera_height_median_m": float(np.median(Ca[:, 1])),
        "camera_height_p10_p90_m": [float(np.percentile(Ca[:, 1], 10)), float(np.percentile(Ca[:, 1], 90))],
        "floor_inlier_frac": float(np.mean(np.abs(Pa[:, 1]) < 0.03)),
        "points_below_floor_frac": float(np.mean(Pa[:, 1] < -0.05)),
        "n_points_used": int(len(P)), "n_cameras": int(len(sc.names)),
        "runtime_s": time.perf_counter() - t0,
        "frame": "y-up, floor y=0, metres (approximate if scale_source is ASSUMED)",
    }


def apply(T, X):
    T = np.asarray(T)
    return (T[:3, :3] @ np.asarray(X).T).T + T[:3, 3]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("colmap_dir")
    ap.add_argument("--out", required=True)
    ap.add_argument("--camera-height-m", type=float, default=None)
    args = ap.parse_args()
    res = estimate_alignment(load_colmap(args.colmap_dir), args.camera_height_m)
    with open(args.out, "w") as f:
        json.dump(res, f, indent=2)
    print({k: v for k, v in res.items() if k != "T_aligned_from_colmap"})
