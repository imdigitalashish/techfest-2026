from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import cv2
import numpy as np
import pycolmap


def _cfw(img):
    c = img.cam_from_world
    return c() if callable(c) else c


def _has_pose(img) -> bool:
    h = getattr(img, "has_pose", True)
    return bool(h() if callable(h) else h)


def _rotmat(T) -> np.ndarray:
    r = getattr(T, "rotation", None)
    r = r() if callable(r) else r
    if r is None:
        return np.asarray(T[:3, :3], dtype=float)
    m = getattr(r, "matrix", None)
    return np.asarray(m() if callable(m) else m, dtype=float)


def _trans(T) -> np.ndarray:
    tr = getattr(T, "translation", None)
    if tr is None:
        tr = np.asarray(T)[:3, 3]
    return np.asarray(tr, dtype=float).reshape(3)


def _camera_center(img) -> np.ndarray:
    T = _cfw(img)
    R, t = _rotmat(T), _trans(T)
    return -R.T @ t


def detect_marker(image_paths: list[str], marker_id=0, dictionary=cv2.aruco.DICT_4X4_50) -> dict:
    aruco_dict = cv2.aruco.getPredefinedDictionary(dictionary) if isinstance(dictionary, int) else dictionary
    params = cv2.aruco.DetectorParameters()
    params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    detector = cv2.aruco.ArucoDetector(aruco_dict, params)
    out = {}
    for p in image_paths:
        img = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        scale = 1.0
        h, w = img.shape[:2]
        mx = max(h, w)
        work = img
        if mx > 2000:
            scale = 2000.0 / mx
            work = cv2.resize(img, (int(round(w * scale)), int(round(h * scale))), interpolation=cv2.INTER_AREA)
        corners, ids, _ = detector.detectMarkers(work)
        if ids is None:
            continue
        ids = ids.reshape(-1)
        hits = np.where(ids == marker_id)[0]
        if len(hits) == 0:
            continue
        pts = np.asarray(corners[int(hits[0])], dtype=np.float32).reshape(4, 2)
        if scale != 1.0:
            pts = pts / scale
        out[Path(p).name] = pts.astype(float)
    return out


def _camera_dict(rec):
    cams = getattr(rec, "cameras")
    return cams() if callable(cams) else cams


def _image_dict(rec):
    imgs = getattr(rec, "images")
    return imgs() if callable(imgs) else imgs


def _cam_model(camera):
    model = getattr(camera, "model", getattr(camera, "model_name", ""))
    name = getattr(model, "name", None)
    return str(name if name is not None else model).split(".")[-1].upper()


def _cam_params(camera):
    return np.asarray(getattr(camera, "params", []), dtype=float).reshape(-1)


def _K_dist(camera):
    if hasattr(camera, "calibration_matrix"):
        try:
            K = np.asarray(camera.calibration_matrix(), dtype=float)
        except Exception:
            K = None
    else:
        K = None
    m, p = _cam_model(camera), _cam_params(camera)
    dist = np.zeros(5, dtype=float)
    if m in {"SIMPLE_PINHOLE", "SIMPLE_RADIAL", "RADIAL"} and len(p) >= 3:
        K = np.array([[p[0], 0, p[1]], [0, p[0], p[2]], [0, 0, 1]], dtype=float)
        if m == "SIMPLE_RADIAL" and len(p) >= 4:
            dist[0] = p[3]
        elif m == "RADIAL" and len(p) >= 5:
            dist[:2] = p[3:5]
    elif m == "PINHOLE" and len(p) >= 4:
        K = np.array([[p[0], 0, p[2]], [0, p[1], p[3]], [0, 0, 1]], dtype=float)
    elif m == "OPENCV" and len(p) >= 8:
        K = np.array([[p[0], 0, p[2]], [0, p[1], p[3]], [0, 0, 1]], dtype=float)
        dist[:4] = p[4:8]
    if K is None:
        raise ValueError(f"Unsupported camera model/params: {m}")
    return K, dist


def _cam_from_img(camera, pts_px: np.ndarray) -> np.ndarray:
    pts_px = np.asarray(pts_px, dtype=float).reshape(-1, 2)
    fn = getattr(camera, "cam_from_img", None)
    if callable(fn):
        try:
            arr = np.asarray(fn(pts_px), dtype=float).reshape(-1, 2)
            if len(arr) == len(pts_px):
                return arr
        except Exception:
            try:
                return np.vstack([np.asarray(fn(p), dtype=float).reshape(2) for p in pts_px])
            except Exception:
                pass
    K, dist = _K_dist(camera)
    return cv2.undistortPoints(pts_px.reshape(-1, 1, 2), K, dist).reshape(-1, 2)


def _img_from_cam(camera, xy: np.ndarray) -> np.ndarray:
    xy = np.asarray(xy, dtype=float).reshape(-1, 2)
    fn = getattr(camera, "img_from_cam", None)
    if callable(fn):
        try:
            arr = np.asarray(fn(xy), dtype=float).reshape(-1, 2)
            if len(arr) == len(xy):
                return arr
        except Exception:
            try:
                return np.vstack([np.asarray(fn(p), dtype=float).reshape(2) for p in xy])
            except Exception:
                pass
    K, dist = _K_dist(camera)
    obj = np.c_[xy, np.ones(len(xy))].astype(float)
    pts, _ = cv2.projectPoints(obj, np.zeros(3), np.zeros(3), K, dist)
    return pts.reshape(-1, 2)


def _linear_triangulate(obs):
    A = []
    for R, t, xy, *_ in obs:
        P = np.c_[R, t.reshape(3, 1)]
        x, y = xy
        A.extend([x * P[2] - P[0], y * P[2] - P[1]])
    _, _, vt = np.linalg.svd(np.asarray(A), full_matrices=False)
    Xh = vt[-1]
    return Xh[:3] / Xh[3]


def _reproj_errors(X, obs):
    errs = []
    for R, t, _xy, camera, px in obs:
        Xc = R @ X + t
        if Xc[2] <= 1e-9:
            errs.append(float("inf"))
            continue
        pr = _img_from_cam(camera, (Xc[:2] / Xc[2]).reshape(1, 2))[0]
        errs.append(float(np.linalg.norm(pr - px)))
    return np.asarray(errs)


def _refine_point(X, obs):
    try:
        from scipy.optimize import least_squares
    except Exception:
        return X

    def residual(v):
        res = []
        for R, t, _xy, camera, px in obs:
            Xc = R @ v + t
            if Xc[2] <= 1e-9:
                res.extend([1e3, 1e3])
            else:
                res.extend((_img_from_cam(camera, (Xc[:2] / Xc[2]).reshape(1, 2))[0] - px).tolist())
        return np.asarray(res)

    return least_squares(residual, X, loss="soft_l1", f_scale=2.0, max_nfev=50).x


def triangulate_marker(rec: pycolmap.Reconstruction, detections: dict, image_dir: str) -> dict:
    del image_dir
    cams = _camera_dict(rec)
    views = []
    for _, img in sorted(_image_dict(rec).items()):
        if not _has_pose(img):
            continue
        name = getattr(img, "name", "")
        det = detections.get(name)
        if det is None:
            det = detections.get(Path(name).name)
        if det is None:
            continue
        cam_id = getattr(img, "camera_id")
        camera = cams[cam_id] if isinstance(cams, dict) else cams[cam_id]
        T = _cfw(img)
        R, t = _rotmat(T), _trans(T)
        norm = _cam_from_img(camera, np.asarray(det, dtype=float))
        views.append((img, camera, R, t, np.asarray(det, dtype=float), norm))
    if len(views) < 2:
        raise ValueError(f"Need at least 2 marker views to triangulate, got {len(views)}")

    corners = []
    all_errs = []
    for ci in range(4):
        obs = [(R, t, norm[ci], cam, px[ci]) for _img, cam, R, t, px, norm in views]
        X = _linear_triangulate(obs)
        err = _reproj_errors(X, obs)
        inl = err < 2.0
        if inl.sum() >= 2 and inl.sum() < len(obs):
            obs = [o for o, ok in zip(obs, inl) if ok]
            X = _linear_triangulate(obs)
        X = _refine_point(X, obs)
        err = _reproj_errors(X, obs)
        corners.append(X)
        all_errs.extend(err[np.isfinite(err)].tolist())
    C = np.asarray(corners)
    edges = np.array([np.linalg.norm(C[(i + 1) % 4] - C[i]) for i in range(4)])
    diags = np.array([np.linalg.norm(C[2] - C[0]), np.linalg.norm(C[3] - C[1])])
    centre = C.mean(axis=0)
    _, _, vt = np.linalg.svd(C - centre, full_matrices=False)
    normal = vt[-1]
    cam_mean = np.mean([_camera_center(v[0]) for v in views], axis=0)
    if np.dot(normal, cam_mean - centre) < 0:
        normal = -normal
    normal = normal / (np.linalg.norm(normal) + 1e-12)
    return {
        "corners_world": C,
        "side_model": float(edges.mean()),
        "side_std": float(edges.std()),
        "diagonal_check": float(abs(diags[0] - diags[1]) / (diags.mean() + 1e-12)),
        "plane_normal": normal,
        "centre": centre,
        "n_views": int(len(views)),
        "reproj_px": float(np.mean(all_errs)) if all_errs else float("inf"),
    }


def _image_paths(image_dir: str) -> list[str]:
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
    return [str(p) for p in sorted(Path(image_dir).iterdir()) if p.suffix.lower() in exts]


def marker_scale(colmap_sparse_dir, image_dir: str, marker_id=0, dictionary=cv2.aruco.DICT_4X4_50, size_m=0.150) -> dict:
    rec = pycolmap.Reconstruction(colmap_sparse_dir) if isinstance(colmap_sparse_dir, (str, Path)) else colmap_sparse_dir
    detections = detect_marker(_image_paths(image_dir), marker_id=marker_id, dictionary=dictionary)
    if not detections:
        return {"scale": None, "side_model": None, "n_views": 0, "reproj_px": None, "edge_cv": None,
                "normal": None, "centre": None, "ok": False, "reason": "marker not detected in any image"}
    try:
        tri = triangulate_marker(rec, detections, image_dir)
    except Exception as e:
        return {"scale": None, "side_model": None, "n_views": len(detections), "reproj_px": None, "edge_cv": None,
                "normal": None, "centre": None, "ok": False, "reason": str(e)}
    side = tri["side_model"]
    edge_cv = tri["side_std"] / (side + 1e-12)
    reasons = []
    if tri["n_views"] < 3:
        reasons.append("fewer than 3 registered marker views")
    if edge_cv > 0.05:
        reasons.append("edge coefficient of variation > 5%")
    if tri["reproj_px"] > 3.0:
        reasons.append("mean reprojection error > 3 px")
    return {
        "scale": float(size_m / side),
        "side_model": float(side),
        "n_views": tri["n_views"],
        "reproj_px": tri["reproj_px"],
        "edge_cv": float(edge_cv),
        "normal": tri["plane_normal"].astype(float).tolist(),
        "centre": tri["centre"].astype(float).tolist(),
        "ok": not reasons,
        "reason": "ok" if not reasons else "; ".join(reasons),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("colmap_sparse_dir")
    ap.add_argument("image_dir")
    ap.add_argument("--size-m", type=float, default=0.150)
    ap.add_argument("--out", default="marker.json")
    args = ap.parse_args()
    res = marker_scale(args.colmap_sparse_dir, args.image_dir, size_m=args.size_m)
    with open(args.out, "w") as f:
        json.dump(res, f, indent=2)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
