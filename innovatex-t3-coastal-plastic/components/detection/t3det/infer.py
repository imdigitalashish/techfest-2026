"""C5 inference pipeline (the part the autoresearch ratchet is allowed to change).

Config keys: imgsz, conf, iou, augment (ultralytics TTA), tiles ([cols, rows] SAHI-style slicing; [1, 1] = off),
tile_overlap (fraction), tile_plus_full (also run the full frame and merge), merge_iou.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import torch
import torchvision

DEFAULT = {"imgsz": 640, "conf": 0.001, "iou": 0.7, "augment": False, "tiles": [1, 1], "tile_overlap": 0.2,
           "tile_plus_full": True, "merge_iou": 0.5, "max_det": 300}


def load_config(path: str | Path | None) -> dict:
    cfg = dict(DEFAULT)
    if path and Path(path).exists():
        cfg.update(json.loads(Path(path).read_text()))
    return cfg


def _predict(model, img: np.ndarray, cfg: dict, device: str) -> np.ndarray:
    r = model.predict(img, imgsz=cfg["imgsz"], conf=cfg["conf"], iou=cfg["iou"], augment=cfg["augment"],
                      max_det=cfg["max_det"], device=device, verbose=False)[0]
    b = r.boxes
    return np.concatenate([b.xyxy.cpu().numpy(), b.conf.cpu().numpy()[:, None]], 1) if len(b) else np.zeros((0, 5))


def predict(model, img: np.ndarray, cfg: dict, device: str | None = None) -> np.ndarray:
    """Returns N x 5 array [x1, y1, x2, y2, score] in pixels of `img` (BGR ndarray)."""
    device = device or os.environ.get("T3DET_DEVICE", "mps")
    cols, rows = cfg["tiles"]
    if cols == 1 and rows == 1:
        return _predict(model, img, cfg, device)
    h, w = img.shape[:2]
    tw, th = int(np.ceil(w / (cols - (cols - 1) * cfg["tile_overlap"]))), int(np.ceil(h / (rows - (rows - 1) * cfg["tile_overlap"])))
    out = [_predict(model, img, cfg, device)] if cfg["tile_plus_full"] else []
    for i in range(cols):
        for j in range(rows):
            x0 = 0 if cols == 1 else round(i * (w - tw) / (cols - 1))
            y0 = 0 if rows == 1 else round(j * (h - th) / (rows - 1))
            d = _predict(model, img[y0:y0 + th, x0:x0 + tw], cfg, device)
            d[:, [0, 2]] += x0
            d[:, [1, 3]] += y0
            out.append(d)
    d = np.concatenate(out, 0)
    if not len(d):
        return d
    keep = torchvision.ops.nms(torch.from_numpy(d[:, :4]).float(), torch.from_numpy(d[:, 4]).float(), cfg["merge_iou"])
    return d[keep.numpy()][: cfg["max_det"]]
