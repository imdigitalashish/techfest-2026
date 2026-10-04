from __future__ import annotations

import math
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np

sys.dont_write_bytecode = True
from marker_scale import marker_scale


class Rotation:
    def __init__(self, R):
        self._R = np.asarray(R, dtype=float)

    def matrix(self):
        return self._R


class Pose:
    def __init__(self, R, t):
        self.rotation = Rotation(R)
        self.translation = np.asarray(t, dtype=float)


class Camera:
    model = "PINHOLE"

    def __init__(self, camera_id, width, height, params):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.params = np.asarray(params, dtype=float)

    def calibration_matrix(self):
        fx, fy, cx, cy = self.params
        return np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=float)


class Image:
    has_pose = True

    def __init__(self, name, camera_id, R, t):
        self.name = name
        self.camera_id = camera_id
        self.cam_from_world = Pose(R, t)


class Rec:
    def __init__(self):
        self.cameras = {}
        self.images = {}


def _n(v):
    v = np.asarray(v, dtype=float)
    return v / np.linalg.norm(v)


def _look_at(C, target):
    up = np.array([0.0, 1.0, 0.0])
    z = _n(target - C)
    x = _n(np.cross(z, up))
    y = np.cross(z, x)
    R = np.vstack([x, y, z])
    return R, -R @ C


def _project(K, R, t, X):
    Xc = (R @ X.T).T + t
    uv = Xc[:, :2] / Xc[:, 2:3]
    return (K[:2, :2] @ uv.T).T + K[:2, 2]


def _synthetic_scene(root: Path):
    scale_units = 3.7
    side_m = 0.150
    side = side_m * scale_units
    half = side / 2
    corners = np.array([[-half, 0, -half], [half, 0, -half], [half, 0, half], [-half, 0, half]], dtype=float)
    W, H = 1000, 800
    K = np.array([[820.0, 0, W / 2], [0, 820.0, H / 2], [0, 0, 1]])
    rec = Rec()
    rec.cameras[1] = Camera(1, W, H, [820.0, 820.0, W / 2, H / 2])
    marker_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    marker = cv2.aruco.generateImageMarker(marker_dict, 0, 220, borderBits=1)
    src = np.array([[0, 0], [219, 0], [219, 219], [0, 219]], dtype=np.float32)
    rng = np.random.default_rng(3)
    target = np.array([0.0, 0.0, 0.0])
    angles = np.linspace(0.2, 2 * np.pi - 0.2, 8)
    for i, a in enumerate(angles):
        r = (1.35 + 0.12 * math.sin(i)) * scale_units
        C = np.array([r * math.cos(a), (1.15 + 0.08 * (i % 3)) * scale_units, r * math.sin(a)])
        R, t = _look_at(C, target)
        quad = _project(K, R, t, corners).astype(np.float32)
        img = np.full((H, W), 176, dtype=np.uint8)
        white = (target + 1.22 * (corners - target))
        cv2.fillConvexPoly(img, _project(K, R, t, white).astype(np.int32), 245)
        Hm = cv2.getPerspectiveTransform(src, quad)
        warped = cv2.warpPerspective(marker, Hm, (W, H), flags=cv2.INTER_LINEAR, borderValue=176)
        mask = cv2.warpPerspective(np.full_like(marker, 255), Hm, (W, H), flags=cv2.INTER_NEAREST)
        img[mask > 0] = warped[mask > 0]
        img = cv2.GaussianBlur(img, (3, 3), 0.35)
        noise = rng.normal(0, 2.0, img.shape).astype(np.int16)
        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        name = f"view_{i:02d}.png"
        assert cv2.imwrite(str(root / name), img)
        rec.images[i + 1] = Image(name, 1, R, t)
    return rec, scale_units


def test_synthetic_marker_scale():
    root = Path(__file__).resolve().parent / ".test-artifacts" / "marker-scale"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    try:
        rec, units = _synthetic_scene(root)
        res = marker_scale(rec, str(root), size_m=0.150)
        assert res["ok"], res
        assert abs(res["scale"] - 1 / units) / (1 / units) < 0.01, res
        n = np.asarray(res["normal"])
        assert math.degrees(math.acos(np.clip(float(np.dot(n, [0, 1, 0])), -1, 1))) < 2.0, res
    finally:
        shutil.rmtree(root, ignore_errors=True)
        try:
            root.parent.rmdir()
        except OSError:
            pass


def test_no_marker_negative():
    root = Path(__file__).resolve().parent / ".test-artifacts" / "no-marker"
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    try:
        cv2.imwrite(str(root / "blank.png"), np.full((400, 500), 180, dtype=np.uint8))
        rec = Rec()
        rec.cameras[1] = Camera(1, 500, 400, [500, 500, 250, 200])
        rec.images[1] = Image("blank.png", 1, np.eye(3), np.zeros(3))
        res = marker_scale(rec, str(root), size_m=0.150)
        assert not res["ok"], res
        assert "not detected" in res["reason"].lower(), res
    finally:
        shutil.rmtree(root, ignore_errors=True)
        try:
            root.parent.rmdir()
        except OSError:
            pass


if __name__ == "__main__":
    test_synthetic_marker_scale()
    test_no_marker_negative()
    print("test_marker_scale.py: all tests passed")
