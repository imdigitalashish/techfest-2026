"""SYNTHETIC flux sequence for C6: real litter crops (TUD-GV test split) drifting across a real water
background (a TUD-GV test frame with its litter inpainted), with exact ground-truth line crossings.

    python -m t3det.synth --out .data/detection/synth/seq01 --frames 300 --items 24 --seed 7
Writes frames/*.jpg + gt.json {fps, line, crossings, items:[{id, t_enter, ...}]}. Items come only from
the held-out test split, so the detector has never seen them. Labelled SYNTHETIC everywhere.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import cv2
import numpy as np

from .paths import DATA, YOLO


def _boxes(label: Path, w: int, h: int) -> list[tuple[int, int, int, int]]:
    out = []
    for line in label.read_text().split("\n"):
        if line.strip():
            _, cx, cy, bw, bh = map(float, line.split())
            out.append((int((cx - bw / 2) * w), int((cy - bh / 2) * h), int((cx + bw / 2) * w), int((cy + bh / 2) * h)))
    return out


def clean_background(img_path: Path) -> np.ndarray:
    img = cv2.imread(str(img_path))
    h, w = img.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    for x1, y1, x2, y2 in _boxes(img_path.parent.parent / "labels" / (img_path.stem + ".txt"), w, h):
        pad = 6
        mask[max(0, y1 - pad):y2 + pad, max(0, x1 - pad):x2 + pad] = 255
    return cv2.inpaint(img, mask, 7, cv2.INPAINT_TELEA)


def crops(test_paths: list[Path], n: int, rng: random.Random) -> list[np.ndarray]:
    pool = []
    for p in test_paths:
        img = cv2.imread(str(p))
        h, w = img.shape[:2]
        for x1, y1, x2, y2 in _boxes(p.parent.parent / "labels" / (p.stem + ".txt"), w, h):
            if (x2 - x1) >= 12 and (y2 - y1) >= 12:
                pool.append((p, (x1, y1, x2, y2)))
    pick = rng.sample(pool, n)
    out = []
    for p, (x1, y1, x2, y2) in pick:
        img = cv2.imread(str(p))
        out.append(img[y1:y2, x1:x2].copy())
    return out


def paste(frame: np.ndarray, crop: np.ndarray, cx: float, cy: float) -> None:
    h, w = crop.shape[:2]
    x1, y1 = int(round(cx - w / 2)), int(round(cy - h / 2))
    fx1, fy1, fx2, fy2 = max(0, x1), max(0, y1), min(frame.shape[1], x1 + w), min(frame.shape[0], y1 + h)
    if fx2 <= fx1 or fy2 <= fy1:
        return
    c = crop[fy1 - y1:fy2 - y1, fx1 - x1:fx2 - x1].astype(np.float32)
    # soft elliptical alpha so the paste has no hard rectangle edge
    yy, xx = np.mgrid[0:h, 0:w]
    a = np.clip(1.6 - np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2), 0, 1)
    a = a[fy1 - y1:fy2 - y1, fx1 - x1:fx2 - x1, None]
    roi = frame[fy1:fy2, fx1:fx2].astype(np.float32)
    frame[fy1:fy2, fx1:fx2] = (a * c + (1 - a) * roi).astype(np.uint8)


def generate(out: Path, frames: int, items: int, seed: int, fps: float = 5.0,
             speed: tuple[float, float] = (4, 9)) -> dict:
    rng = random.Random(seed)
    test = [Path(p) for p in (YOLO / "test.txt").read_text().split()]
    bg = clean_background(rng.choice(test))
    h, w = bg.shape[:2]
    line_x = w / 2
    objs = []
    for i, crop in enumerate(crops(test, items, rng)):
        v = rng.uniform(*speed)  # px/frame (flow left -> right)
        # enter early enough to reach the counting line before the clip ends
        t0 = rng.randint(0, max(1, frames - int((line_x + crop.shape[1] + 20) / v) - 1))
        objs.append({"id": i, "crop": crop, "t0": t0, "x0": -crop.shape[1], "y": rng.uniform(0.1 * h, 0.9 * h),
                     "vx": v, "vy": rng.uniform(-0.6, 0.6), "phase": rng.uniform(0, 6.28)})
    (out / "frames").mkdir(parents=True, exist_ok=True)
    crossings = []
    for f in range(frames):
        frame = bg.copy()
        # mild global illumination flicker + sensor noise
        frame = np.clip(frame.astype(np.int16) + int(6 * np.sin(f / 9)) + np.random.default_rng(seed * 1000 + f)
                        .integers(-4, 5, frame.shape, dtype=np.int16), 0, 255).astype(np.uint8)
        for o in objs:
            if f < o["t0"]:
                continue
            k = f - o["t0"]
            x = o["x0"] + o["vx"] * k
            y = o["y"] + o["vy"] * k + 3 * np.sin(o["phase"] + k / 6)
            xp = o["x0"] + o["vx"] * (k - 1)
            if k >= 1 and xp < line_x <= x and o["id"] not in {c["id"] for c in crossings}:
                crossings.append({"id": o["id"], "frame": f})
            if -o["crop"].shape[1] <= x <= w + o["crop"].shape[1]:
                paste(frame, o["crop"], x, y)
        cv2.imwrite(str(out / "frames" / f"{f:05d}.jpg"), frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
    gt = {"label": "SYNTHETIC", "seed": seed, "fps": fps, "frames": frames, "image_wh": [w, h], "speed_px_per_frame": list(speed),
          "line": [[line_x, 0], [line_x, h]], "direction": "left_to_right", "n_items": items,
          "gt_crossings": len(crossings), "crossings": crossings,
          "items": [{"id": o["id"], "t0": o["t0"], "vx": round(o["vx"], 2), "crop_wh": list(o["crop"].shape[1::-1])}
                    for o in objs]}
    (out / "gt.json").write_text(json.dumps(gt, indent=1))
    return gt


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DATA / "synth" / "seq01"))
    p.add_argument("--frames", type=int, default=300)
    p.add_argument("--items", type=int, default=24)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--speed", type=float, nargs=2, default=[4, 9], help="px/frame range")
    a = p.parse_args()
    gt = generate(Path(a.out), a.frames, a.items, a.seed, speed=tuple(a.speed))
    print(f"SYNTHETIC sequence: {gt['frames']} frames, {gt['n_items']} items, {gt['gt_crossings']} GT crossings -> {a.out}")


if __name__ == "__main__":
    main()
