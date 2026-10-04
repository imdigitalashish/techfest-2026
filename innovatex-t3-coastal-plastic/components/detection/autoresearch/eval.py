"""FROZEN evaluator for the C5 autoresearch ratchet. The loop never edits this file.

    python autoresearch/eval.py --weights <best.pt> --config autoresearch/config.json [--split val]
Prints ONE scalar on the last line: val mAP50 (IoU 0.5, COCO-style 101-point interpolated AP, single class).
Secondary metrics go to stderr as JSON: bootstrap SE over images, precision/recall at score>=0.25, ms/img.
The split defaults to val (model/config selection). `--split test` is for the final, once-only report.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np

COMP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(COMP))
from t3det.infer import load_config, predict  # noqa: E402
from t3det.paths import YOLO  # noqa: E402


def gt_boxes(img_path: Path, w: int, h: int) -> np.ndarray:
    lab = img_path.parent.parent / "labels" / (img_path.stem + ".txt")
    rows = [list(map(float, ln.split()))[1:] for ln in lab.read_text().splitlines() if ln.strip()]
    a = np.array(rows, dtype=float).reshape(-1, 4)
    return np.stack([(a[:, 0] - a[:, 2] / 2) * w, (a[:, 1] - a[:, 3] / 2) * h,
                     (a[:, 0] + a[:, 2] / 2) * w, (a[:, 1] + a[:, 3] / 2) * h], 1)


def iou(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    ix1, iy1 = np.maximum(a[:, None, 0], b[None, :, 0]), np.maximum(a[:, None, 1], b[None, :, 1])
    ix2, iy2 = np.minimum(a[:, None, 2], b[None, :, 2]), np.minimum(a[:, None, 3], b[None, :, 3])
    inter = np.clip(ix2 - ix1, 0, None) * np.clip(iy2 - iy1, 0, None)
    area = lambda x: (x[:, 2] - x[:, 0]) * (x[:, 3] - x[:, 1])  # noqa: E731
    return inter / (area(a)[:, None] + area(b)[None, :] - inter + 1e-9)


def match(pred: np.ndarray, gt: np.ndarray, thr: float = 0.5) -> np.ndarray:
    """Greedy by score: returns tp flags (len(pred))."""
    tp = np.zeros(len(pred), bool)
    if not len(pred) or not len(gt):
        return tp
    order = np.argsort(-pred[:, 4])
    ious = iou(pred[order, :4], gt)
    used = np.zeros(len(gt), bool)
    for k, i in enumerate(order):
        cand = np.where(~used & (ious[k] >= thr))[0]
        if len(cand):
            j = cand[np.argmax(ious[k, cand])]
            used[j] = True
            tp[i] = True
    return tp


def ap101(scores: np.ndarray, tp: np.ndarray, n_gt: int) -> float:
    if n_gt == 0 or not len(scores):
        return 0.0
    o = np.argsort(-scores, kind="stable")
    ctp = np.cumsum(tp[o])
    rec = ctp / n_gt
    prec = ctp / np.arange(1, len(o) + 1)
    prec = np.maximum.accumulate(prec[::-1])[::-1]
    return float(np.mean([prec[rec >= t].max() if (rec >= t).any() else 0.0 for t in np.linspace(0, 1, 101)]))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--weights", required=True)
    p.add_argument("--config", default=str(COMP / "autoresearch" / "config.json"))
    p.add_argument("--split", default="val", choices=["val", "test", "groningen"])
    p.add_argument("--boot", type=int, default=200)
    a = p.parse_args()
    from ultralytics import YOLO as Y

    cfg = load_config(a.config)
    model = Y(a.weights)
    paths = [Path(x) for x in (YOLO / ("groningen.txt" if a.split == "groningen" else f"{a.split}.txt")).read_text().split()]
    per_img, ts = [], []
    for i, pth in enumerate(paths):
        img = cv2.imread(str(pth))
        t0 = time.perf_counter()
        pred = predict(model, img, cfg)
        if i >= 5:
            ts.append((time.perf_counter() - t0) * 1000)
        g = gt_boxes(pth, img.shape[1], img.shape[0])
        per_img.append((pred[:, 4], match(pred, g), len(g), pred))
    cat = lambda k: np.concatenate([x[k] for x in per_img]) if per_img else np.zeros(0)  # noqa: E731
    n_gt = sum(x[2] for x in per_img)
    m = ap101(cat(0), cat(1), n_gt)
    rng = np.random.default_rng(0)
    boots = []
    for _ in range(a.boot):
        idx = rng.integers(0, len(per_img), len(per_img))
        boots.append(ap101(np.concatenate([per_img[i][0] for i in idx]), np.concatenate([per_img[i][1] for i in idx]),
                           sum(per_img[i][2] for i in idx)))
    s, tp = cat(0), cat(1)
    keep = s >= 0.25
    sec = {"split": a.split, "n_images": len(paths), "n_gt": int(n_gt), "mAP50": round(m, 4),
           "boot_se": round(float(np.std(boots)), 4), "precision@0.25": round(float(tp[keep].mean()) if keep.any() else 0, 4),
           "recall@0.25": round(float(tp[keep].sum() / max(n_gt, 1)), 4), "ms_per_img_median": round(float(np.median(ts)), 1),
           "config": cfg, "weights": a.weights}
    print(json.dumps(sec), file=sys.stderr)
    print(f"{m:.4f}")


if __name__ == "__main__":
    main()
