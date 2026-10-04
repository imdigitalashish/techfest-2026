"""Evaluate trained C5 weights: held-out test ONCE (+ val and the Groningen cross-site split) and latency.

    T3DET_DEVICE=mps python -m t3det.evaluate --weights <best.pt> --imgsz 640 --also val groningen --out results/metrics.json
Splits: val | test (TUD-GV grouped split) | groningen (different canal + camera). ultralytics val(): COCO-style
101-point AP, conf 0.001, NMS IoU 0.7; P and R are ultralytics' values at its max-F1 confidence.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .detector import model_id_for
from .paths import COMP, YOLO

DEVICE = os.environ.get("T3DET_DEVICE", "mps")
IST = timezone(timedelta(hours=5, minutes=30))


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=COMP, text=True).strip()
    except Exception:
        return "unknown"


def box_metrics(weights: str, split: str, imgsz: int = 640, batch: int = 16) -> dict:
    from ultralytics import YOLO as Y

    from . import mps_patch

    mps_patch.apply_all()  # lifts the NMS wall-clock limit that would blank images on a loaded machine
    data = YOLO / ("groningen.yaml" if split == "groningen" else "tudgv.yaml")
    r = Y(weights).val(data=str(data), split="test" if split == "groningen" else split, imgsz=imgsz, batch=batch,
                       device=DEVICE, conf=0.001, iou=0.7, plots=False, verbose=False, workers=2)
    names = r.names
    per_class = {names[int(c)]: {"AP50": round(float(r.box.ap50[i]), 4), "AP50_95": round(float(r.box.ap[i]), 4)}
                 for i, c in enumerate(r.box.ap_class_index)}
    lst = YOLO / ("groningen.txt" if split == "groningen" else f"{split}.txt")
    return {"split": split, "n_images": len(lst.read_text().split()), "mAP50": round(float(r.box.map50), 4),
            "mAP50_95": round(float(r.box.map), 4), "precision": round(float(r.box.mp), 4),
            "recall": round(float(r.box.mr), 4), "per_class": per_class,
            "ultralytics_speed_ms": {k: round(v, 2) for k, v in r.speed.items()}}


def latency(weights: str, imgsz: int = 640, n: int = 50, warmup: int = 10) -> dict:
    """End-to-end predict() wall-clock per image (decode + preprocess + inference + NMS), batch 1."""
    from ultralytics import YOLO as Y

    paths = (YOLO / "test.txt").read_text().split()[: n + warmup]
    m = Y(weights)
    ts = []
    for i, p in enumerate(paths):
        t0 = time.perf_counter()
        m.predict(p, imgsz=imgsz, device=DEVICE, conf=0.25, verbose=False)
        if i >= warmup:
            ts.append((time.perf_counter() - t0) * 1000)
    return {"median": round(statistics.median(ts), 2), "p90": round(sorted(ts)[int(0.9 * len(ts))], 2), "n": len(ts),
            "batch": 1, "imgsz": imgsz, "device": DEVICE,
            "note": f"shared Apple M5 (1-min load avg {os.getloadavg()[0]:.0f} on 10 cores, process niced +10, another "
                    "app using the GPU); includes JPEG decode of a 1280x720 image: an upper bound"
                    + ("" if DEVICE == "mps" else "; measured on CPU, key name kept for the schema")}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--weights", required=True)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--also", nargs="*", default=["val", "groningen"], help="extra splits reported alongside test")
    p.add_argument("--model-id", default=None)
    p.add_argument("--out", default=str(COMP / "results" / "metrics.json"))
    p.add_argument("--reproduce", default="")
    p.add_argument("--extra", default="{}", help="JSON merged into the output (e.g. training details)")
    a = p.parse_args()
    test = box_metrics(a.weights, "test", a.imgsz)
    out = {
        "dataset": "TUD-GV floating-litter subset (Jia et al. 2024, Water Research 266:122405), "
                   "doi:10.5281/zenodo.13730228, CC BY 4.0",
        "split": "test (grouped by experiment id, seed 42; components/detection/data/splits/test.txt; held out: "
                 "evaluated once, never used for training or selection)",
        "n_test_images": test["n_images"],
        "mAP50": test["mAP50"], "mAP50_95": test["mAP50_95"], "precision": test["precision"], "recall": test["recall"],
        "per_class": test["per_class"],
        "latency_ms_mps": latency(a.weights, a.imgsz),
        "model_id": a.model_id or model_id_for(a.weights),
        "device": DEVICE,
        "reproduce": a.reproduce,
        "evaluated_at": datetime.now(IST).isoformat(timespec="seconds"),
        "code_commit": _git_sha(),
        "machine": f"{platform.machine()} macOS {platform.mac_ver()[0]} (Apple M5, 24 GB, shared)",
        "eval_settings": {"imgsz": a.imgsz, "conf": 0.001, "iou_nms": 0.7, "nms_time_limit": "lifted (see mps_patch.py)",
                          "ap": "ultralytics COCO-style 101-point; P/R at ultralytics' max-F1 confidence"},
        "ultralytics_speed_ms": test["ultralytics_speed_ms"],
        "other_splits": {s: box_metrics(a.weights, s, a.imgsz) for s in a.also},
    }
    out.update(json.loads(a.extra))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("mAP50", "mAP50_95", "precision", "recall")}),
          {s: v["mAP50"] for s, v in out["other_splits"].items()}, out["latency_ms_mps"]["median"])


if __name__ == "__main__":
    main()
