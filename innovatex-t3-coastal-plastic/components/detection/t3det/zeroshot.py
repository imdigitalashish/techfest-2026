"""Zero-shot, class-agnostic C5 baseline: COCO-pretrained YOLO11n (no TUD-GV training), every detection of any COCO
class = a floating-litter candidate. Scored with the FROZEN matcher/AP of autoresearch/eval.py (imported, unchanged).

    python -m t3det.zeroshot --weights ../../.data/detection/weights/yolo11n.pt --split test
Writes results/metrics.json, results/sample_detections.json and results/samples/*.jpg.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import random
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np

from ._contracts import Detection, FrameDetections
from .detector import file_hash
from .paths import COMP, RESULTS, SEED, YOLO

_spec = importlib.util.spec_from_file_location("frozen_eval", COMP / "autoresearch" / "eval.py")
fe = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fe)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--weights", required=True)
    p.add_argument("--split", default="test")
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--n-samples", type=int, default=5)
    a = p.parse_args()
    from ultralytics import YOLO as Y

    model = Y(a.weights)
    lst = YOLO / ("groningen.txt" if a.split == "groningen" else f"{a.split}.txt")
    paths = [Path(x) for x in lst.read_text().split()]
    picks = set(random.Random(SEED).sample([str(x) for x in paths], a.n_samples)) if a.split == "test" else set()
    model_id = f"{Path(a.weights).name}#sha256:{file_hash(a.weights)} (COCO-pretrained, zero-shot, class-agnostic)"
    per_img, ts, frames = [], [], []
    for i, pth in enumerate(paths):
        img = cv2.imread(str(pth))
        t0 = time.perf_counter()
        r = model.predict(img, imgsz=a.imgsz, conf=0.001, iou=0.7, max_det=300, device="mps", verbose=False,
                          agnostic_nms=True)[0]
        dt = (time.perf_counter() - t0) * 1000
        if i >= 3:
            ts.append(dt)
        b = r.boxes
        pred = np.concatenate([b.xyxy.cpu().numpy(), b.conf.cpu().numpy()[:, None]], 1) if len(b) else np.zeros((0, 5))
        g = fe.gt_boxes(pth, img.shape[1], img.shape[0])
        per_img.append((pred, g))
        if str(pth) in picks:
            keep = pred[:, 4] >= 0.25
            dets = [Detection(bbox_xyxy=tuple(round(float(v), 1) for v in d[:4]), label="litter", score=round(float(d[4]), 4))
                    for d in pred[keep]]
            frames.append(FrameDetections(frame_id=f"tudgv-test/{pth.name}", image_wh=(img.shape[1], img.shape[0]),
                                          detections=dets, model_id=model_id, latency_ms=round(dt, 2)))
            vis = img.copy()
            for x1, y1, x2, y2 in g.astype(int):
                cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 200, 0), 2)
            for d in dets:
                x1, y1, x2, y2 = map(int, d.bbox_xyxy)
                cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(vis, f"{d.score:.2f}", (x1, max(12, y1 - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            cv2.putText(vis, "green = ground truth, red = zero-shot C5 (score>=0.25), TUD-GV test", (10, 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            (RESULTS / "samples").mkdir(parents=True, exist_ok=True)
            dst = RESULTS / "samples" / (pth.stem + ".jpg")
            small = cv2.resize(vis, (960, int(960 * img.shape[0] / img.shape[1])))
            for q in (80, 70, 60, 50, 40):
                cv2.imwrite(str(dst), small, [cv2.IMWRITE_JPEG_QUALITY, q])
                if dst.stat().st_size <= 200_000:
                    break

    def ap_at(thr: float) -> float:
        tp = np.concatenate([fe.match(pr, g, thr) for pr, g in per_img])
        sc = np.concatenate([pr[:, 4] for pr, _ in per_img])
        return fe.ap101(sc, tp, sum(len(g) for _, g in per_img))

    aps = {round(t, 2): ap_at(t) for t in np.arange(0.5, 0.951, 0.05)}
    tp50 = np.concatenate([fe.match(pr, g, 0.5) for pr, g in per_img])
    sc = np.concatenate([pr[:, 4] for pr, _ in per_img])
    n_gt = sum(len(g) for _, g in per_img)
    k = sc >= 0.25
    out = {
        "dataset": "TUD-GV floating-litter subset (Jia et al. 2024, Water Research 266:122405), doi:10.5281/zenodo.13730228, CC BY 4.0",
        "split": f"{a.split} (grouped by experiment id, seed 42; components/detection/data/splits/{a.split}.txt; held out)",
        "n_test_images": len(paths), "n_test_boxes": int(n_gt),
        "mAP50": round(aps[0.5], 4), "mAP50_95": round(float(np.mean(list(aps.values()))), 4),
        "precision": round(float(tp50[k].mean()) if k.any() else 0.0, 4),
        "recall": round(float(tp50[k].sum() / max(n_gt, 1)), 4),
        "precision_recall_at_score": 0.25,
        "per_class": {"litter": {"AP50": round(aps[0.5], 4), "AP50_95": round(float(np.mean(list(aps.values()))), 4)}},
        "latency_ms_mps": {"median": round(float(np.median(ts)), 1), "p90": round(float(np.percentile(ts, 90)), 1),
                           "n": len(ts), "batch": 1, "imgsz": a.imgsz,
                           "note": f"end-to-end predict() on a shared, thrashing Apple M5 (load avg {os.getloadavg()[0]:.0f}"
                                   " on 10 cores, swap full): an upper bound, not the model's real speed"},
        "model_id": model_id,
        "baseline_kind": "ZERO-SHOT (no training on TUD-GV): COCO-pretrained YOLO11n, class-agnostic NMS, every COCO "
                         "class counted as a litter candidate. The trained YOLO11n baseline was blocked by machine "
                         "thrash (README A1); its command is in README.",
        "metric_impl": "frozen matcher of autoresearch/eval.py: greedy IoU match, COCO-style 101-point AP; mAP50_95 = "
                       "mean AP over IoU 0.50:0.05:0.95; precision/recall at score >= 0.25",
        "reproduce": "cd innovatex-t3-coastal-plastic && bash components/detection/data/fetch_data.sh && cd components/detection && "
                     "python3.11 -m t3det.prepare && curl -sSL -o ../../.data/detection/weights/yolo11n.pt "
                     "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt && python3.11 -m t3det.zeroshot "
                     f"--weights ../../.data/detection/weights/yolo11n.pt --split {a.split}",
        "evaluated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "machine": f"{platform.machine()} macOS {platform.mac_ver()[0]} (Apple M5, MPS)",
        "ap_by_iou": {str(t): round(v, 4) for t, v in aps.items()},
    }
    name = "metrics.json" if a.split == "test" else f"metrics_{a.split}.json"
    (RESULTS / name).write_text(json.dumps(out, indent=1) + "\n")
    if frames:
        (RESULTS / "sample_detections.json").write_text(json.dumps([json.loads(f.model_dump_json()) for f in frames], indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("n_test_images", "mAP50", "mAP50_95", "precision", "recall")}), out["latency_ms_mps"]["median"])


if __name__ == "__main__":
    main()
