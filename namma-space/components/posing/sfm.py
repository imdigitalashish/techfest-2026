#!/usr/bin/env python3
"""Posing (component 3): keyframes -> COLMAP model (pycolmap 4.2, CPU), undistorted for 3DGS training.

Output (<out>/):
  database.db, sparse_raw/ (all models), model/ (largest model, distorted)
  colmap/images + colmap/sparse/0   (undistorted PINHOLE; read by Brush and the rest of the pipeline)
  posing.json  (contract PosedFrames + timings)
Mapper: "global" (pycolmap.global_mapping, the GLOMAP-style global SfM) with fallback to "incremental"
when the global model registers < 80% of the frames.
"""
import argparse
import json
import os
import shutil
import time

import pycolmap


def _largest(maps):
    return max(maps.values(), key=lambda r: r.num_reg_images()) if maps else None


def _better(a, a_sanity, b, b_sanity):
    """Is model a preferable to model b? A non-degenerate model wins; then more registered images."""
    if a is None:
        return False
    if b is None:
        return True
    a_deg, b_deg = (a_sanity or {}).get("degenerate", True), (b_sanity or {}).get("degenerate", True)
    if a_deg != b_deg:
        return not a_deg
    return a.num_reg_images() > b.num_reg_images()


def pose_sanity(rec):
    """Reference-free degeneracy check. Registration rate and reprojection error do NOT catch collapsed or
    scattered global solutions (seen on drjohnson with sequential matching: 99.6% registered, 0.66 px, yet ATE 34%
    of the scene). Flags many far cameras or a strongly bimodal camera spread."""
    import numpy as np
    C = []
    for img in rec.images.values():
        T = img.cam_from_world() if callable(img.cam_from_world) else img.cam_from_world
        R = np.asarray(T.rotation.matrix())
        C.append(-R.T @ np.asarray(T.translation).reshape(3))
    C = np.array(C)
    d = np.linalg.norm(C - np.median(C, axis=0), axis=1)
    p50, p75 = (float(x) for x in np.percentile(d, [50, 75]))
    out_frac = float(np.mean(d > 3 * max(p75, 1e-9)))
    spread = p75 / max(p50, 1e-9)
    return {"outlier_cam_frac": round(out_frac, 4), "spread_ratio_p75_p50": round(spread, 3),
            "degenerate": bool(out_frac > 0.05 or spread > 3.5)}


def _mean_reproj(rec):
    try:
        return float(rec.compute_mean_reprojection_error())
    except Exception:  # noqa: BLE001
        errs = [p.error for p in rec.points3D.values()]
        return float(sum(errs) / max(len(errs), 1))


def run_sfm(frames_dir, out, mapper="global", matcher="auto", camera_model="SIMPLE_RADIAL",
            max_image_size=1600, seq_overlap=20, ordered=True):
    os.makedirs(out, exist_ok=True)
    t = {}
    db = os.path.join(out, "database.db")
    if os.path.exists(db):
        os.remove(db)
    n = len([f for f in os.listdir(frames_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))])
    t0 = time.perf_counter()
    ro = pycolmap.ImageReaderOptions()
    ro.camera_model = camera_model
    eo = pycolmap.FeatureExtractionOptions()
    eo.max_image_size = max_image_size
    eo.num_threads = -1
    pycolmap.extract_features(db, frames_dir, camera_mode=pycolmap.CameraMode.SINGLE, reader_options=ro,
                              extraction_options=eo, device=pycolmap.Device.cpu)
    t["extract_s"] = time.perf_counter() - t0
    t0 = time.perf_counter()
    # unordered photo sets need all pairs (sequential matching gave a degenerate model on drjohnson); video is ordered
    use_exh = matcher == "exhaustive" or (matcher == "auto" and (n <= 150 or (not ordered and n <= 600)))
    if use_exh:
        pycolmap.match_exhaustive(db, device=pycolmap.Device.cpu)
    else:
        po = pycolmap.SequentialPairingOptions()
        po.overlap = seq_overlap
        po.quadratic_overlap = True
        pycolmap.match_sequential(db, pairing_options=po, device=pycolmap.Device.cpu)
    t["match_s"] = time.perf_counter() - t0
    raw = os.path.join(out, "sparse_raw")
    shutil.rmtree(raw, ignore_errors=True)
    os.makedirs(raw)
    used, rec = mapper, None
    t0 = time.perf_counter()
    if mapper == "global":
        try:
            rec = _largest(pycolmap.global_mapping(db, frames_dir, raw))
        except Exception as e:  # noqa: BLE001
            print("global mapping failed:", e)
    sanity = pose_sanity(rec) if rec is not None and rec.num_reg_images() >= 3 else None
    if rec is None or rec.num_reg_images() < 0.8 * n or (sanity and sanity["degenerate"]):
        g, g_sanity = rec, sanity
        rec = _largest(pycolmap.incremental_mapping(db, frames_dir, raw))
        used = "incremental"
        sanity = pose_sanity(rec) if rec is not None and rec.num_reg_images() >= 3 else None
        if _better(g, g_sanity, rec, sanity):
            rec, used, sanity = g, "global", g_sanity
    t["map_s"] = time.perf_counter() - t0
    if rec is None:
        raise RuntimeError("SfM failed: no model")
    model = os.path.join(out, "model")
    shutil.rmtree(model, ignore_errors=True)
    os.makedirs(model)
    rec.write(model)
    t0 = time.perf_counter()
    und = os.path.join(out, "colmap")
    shutil.rmtree(und, ignore_errors=True)
    pycolmap.undistort_images(und, model, frames_dir)
    sp = os.path.join(und, "sparse")
    os.makedirs(os.path.join(sp, "0"), exist_ok=True)
    for f in os.listdir(sp):
        if f.endswith((".bin", ".txt")):
            shutil.move(os.path.join(sp, f), os.path.join(sp, "0", f))
    for extra in ("stereo", "run-colmap-geometric.sh", "run-colmap-photometric.sh"):
        p = os.path.join(und, extra)
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif os.path.exists(p):
            os.remove(p)
    t["undistort_s"] = time.perf_counter() - t0
    res = {"colmap_dir": os.path.join(und, "sparse", "0"), "image_dir": os.path.join(und, "images"),
           "n_frames": n, "n_registered": int(rec.num_reg_images()),
           "registration_rate": rec.num_reg_images() / max(n, 1), "n_points3D": int(rec.num_points3D()),
           "mean_reprojection_error_px": _mean_reproj(rec), "mapper": used,
           "matcher": "exhaustive" if use_exh else f"sequential(overlap={seq_overlap},quadratic)", "ordered_input": ordered,
           "pose_sanity": sanity,
           "camera_model": camera_model, "timings_s": {k: round(v, 2) for k, v in t.items()},
           "seconds": round(sum(t.values()), 2), "pycolmap": pycolmap.__version__}
    with open(os.path.join(out, "posing.json"), "w") as f:
        json.dump(res, f, indent=1)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("frames_dir")
    ap.add_argument("out")
    ap.add_argument("--mapper", default="global", choices=["global", "incremental"])
    ap.add_argument("--matcher", default="auto", choices=["auto", "sequential", "exhaustive"])
    ap.add_argument("--unordered", action="store_true", help="photo collection (not video): prefer exhaustive matching")
    a = ap.parse_args()
    print(json.dumps(run_sfm(a.frames_dir, a.out, a.mapper, a.matcher, ordered=not a.unordered)))
