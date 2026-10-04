#!/usr/bin/env python3
"""POI placement from frames (component 8, baseline "manual tagging from evidence frames").

For each spec item {label, kind, aliases, image, u, v} (u, v = pixel fractions 0..1 in that image), cast a
ray from the posed camera through the pixel into the reconstructed sparse points (aligned frame), take a
robust near-surface depth (20th percentile of points within 2 deg of the ray), and snap an approach point
onto the navigable grid. Writes POI[] (architecture/contracts/contracts.ts) to <work>/package/pois.json.
Also used later for voice tags (timestamp -> frame -> centre pixel) and door-sign OCR boxes.
Usage: python poi_from_frames.py --work .data/work/<name> --spec pois_spec.json
"""
import argparse
import base64
import json
import os
import sys

import numpy as np
import pycolmap

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "components"))
from scene_alignment.align import apply  # noqa: E402


def load(work):
    rec = pycolmap.Reconstruction(os.path.join(work, "sfm", "colmap", "sparse", "0"))
    al = json.load(open(os.path.join(work, "alignment.json")))
    T = np.array(al["T_aligned_from_colmap"])
    src = {f.get("source", f["name"]): f["name"] for f in json.load(open(os.path.join(work, "frames.json")))["frames"]}
    nav = json.load(open(os.path.join(work, "package", "nav.json")))
    N = np.unpackbits(np.frombuffer(base64.b64decode(nav["navigable_b64"]), np.uint8))[: nav["nx"] * nav["nz"]]
    N = N.reshape(nav["nx"], nav["nz"]).astype(bool)
    P = apply(T, np.array([p.xyz for p in rec.points3D.values()]))
    return rec, T, src, nav, N, P


def place(rec, T, P, img_name, u, v, cone_deg=2.0):
    img = next(i for i in rec.images.values() if i.name == img_name)
    cam = rec.cameras[img.camera_id]
    cfw = img.cam_from_world() if callable(img.cam_from_world) else img.cam_from_world
    R = np.asarray(cfw.rotation.matrix())
    t = np.asarray(cfw.translation).reshape(3)
    fx, fy, cx, cy = cam.params[:4] if len(cam.params) >= 4 else (cam.params[0], cam.params[0], cam.params[1], cam.params[2])
    d_cam = np.array([(u * cam.width - cx) / fx, (v * cam.height - cy) / fy, 1.0])
    c_w, d_w = -R.T @ t, R.T @ d_cam
    s = np.linalg.norm(T[:3, 0])
    c_a, d_a = apply(T, c_w[None])[0], (T[:3, :3] @ d_w) / s
    d_a /= np.linalg.norm(d_a)
    rel = P - c_a
    depth = rel @ d_a
    ang = np.degrees(np.arccos(np.clip(depth / (np.linalg.norm(rel, axis=1) + 1e-9), -1, 1)))
    sel = (ang < cone_deg) & (depth > 0.3)
    if sel.sum() < 3:
        return None, c_a
    z = float(np.percentile(depth[sel], 20))
    return c_a + z * d_a, c_a


def snap(nav, N, xz):
    from scipy import ndimage
    idx = ndimage.distance_transform_edt(~N, return_distances=False, return_indices=True)
    lo, cell = np.array(nav["lo_xz"]), nav["cell_m"]
    i, k = np.clip(np.floor((np.asarray(xz) - lo) / cell).astype(int), 0, [nav["nx"] - 1, nav["nz"] - 1])
    a, b = idx[0][i, k], idx[1][i, k]
    return [float(lo[0] + (a + 0.5) * cell), float(lo[1] + (b + 0.5) * cell)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--spec", required=True)
    a = ap.parse_args()
    rec, T, src, nav, N, P = load(a.work)
    pois, report = [], []
    for k, s in enumerate(json.load(open(a.spec))):
        name = src.get(s["image"], s["image"])
        pos, cam = place(rec, T, P, name, s.get("u", 0.5), s.get("v", 0.5))
        if pos is None:
            report.append({"label": s["label"], "ok": False, "reason": "no points along ray"})
            continue
        pos[1] = float(np.clip(pos[1], 0.3, 2.2))
        appr = snap(nav, N, pos[[0, 2]])
        pois.append({"id": f"poi-{k:02d}", "label": s["label"], "aliases": s.get("aliases", []), "kind": s.get("kind", "item"),
                     "position": [float(x) for x in pos], "approach_xz": appr, "source": "manual", "confidence": 1.0,
                     "evidence": [{"frame": s["image"], "pixel_frac": [s.get("u", 0.5), s.get("v", 0.5)]}]})
        report.append({"label": s["label"], "ok": True, "pos": [round(float(x), 2) for x in pos],
                       "dist_cam_m": round(float(np.linalg.norm(pos - cam)), 2),
                       "approach_offset_m": round(float(np.linalg.norm(np.array(appr) - pos[[0, 2]])), 2)})
    json.dump(pois, open(os.path.join(a.work, "package", "pois.json"), "w"), indent=1)
    print(json.dumps(report))


if __name__ == "__main__":
    main()
