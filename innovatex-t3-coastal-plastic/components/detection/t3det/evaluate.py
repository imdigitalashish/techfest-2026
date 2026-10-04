"""Evaluate C5 weights on a split and measure MPS latency.

    python -m t3det.evaluate --weights <best.pt> --split test --out results/metrics.json
Splits: val | test (TUD-GV grouped split) | groningen (cross-site, different canal + camera).
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from .detector import file_hash
from .paths import COMP, YOLO


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=COMP, text=True).strip()
    except Exception:
        return "unknown"


def box_metrics(weights: str, split: str, imgsz: int = 640, batch: int = 16) -> dict:
    from ultralytics import YOLO as Y

    data = YOLO / ("groningen.yaml" if split == "groningen" else "tudgv.yaml")
    m = Y(weights)
    r = m.val(data=str(data), split="test" if split == "groningen" else split, imgsz=imgsz, batch=batch,
              device="mps", conf=0.001, iou=0.7, plots=False, verbose=False, workers=2)
    names = r.names
    per_class = {names[int(c)]: {"AP50": round(float(r.box.ap50[i]), 4), "AP50_95": round(float(r.box.ap[i]), 4)}
                 for i, c in enumerate(r.box.ap_class_index)}
    lst = YOLO / ("groningen.txt" if split == "groningen" else f"{split}.txt")
    n_img = len(lst.read_text().split())
    return {"split": split, "n_images": n_img, "mAP50": round(float(r.box.map50), 4),
            "mAP50_95": round(float(r.box.map), 4), "precision": round(float(r.box.mp), 4),
            "recall": round(float(r.box.mr), 4), "per_class": per_class,
            "ultralytics_speed_ms": {k: round(v, 2) for k, v in r.speed.items()}}


def latency_mps(weights: str, split: str = "test", imgsz: int = 640, n: int = 50, warmup: int = 10) -> dict:
    """End-to-end predict() wall-clock per image (decode + preprocess + inference + NMS), batch 1, MPS."""
    from ultralytics import YOLO as Y

    paths = (YOLO / f"{split}.txt").read_text().split()[: n + warmup]
    m = Y(weights)
    ts = []
    for i, p in enumerate(paths):
        t0 = time.perf_counter()
        m.predict(p, imgsz=imgsz, device="mps", conf=0.25, verbose=False)
        if i >= warmup:
            ts.append((time.perf_counter() - t0) * 1000)
    return {"median": round(statistics.median(ts), 2), "p90": round(sorted(ts)[int(0.9 * len(ts))], 2),
            "n": len(ts), "batch": 1, "imgsz": imgsz,
            "note": f"shared Apple M5 (load avg {os.getloadavg()[0]:.0f} on 10 cores during timing); "
                    "includes JPEG decode of <=1280 px image"}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--weights", required=True)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--split", default="test")
    p.add_argument("--also", nargs="*", default=["val", "groningen"], help="extra splits reported alongside")
    p.add_argument("--model-id", default=None)
    p.add_argument("--out", default=str(COMP / "results" / "metrics.json"))
    p.add_argument("--reproduce", default="")
    p.add_argument("--extra", default="{}", help="JSON merged into the output (e.g. training details)")
    a = p.parse_args()
    main_m = box_metrics(a.weights, a.split, a.imgsz)
    out = {
        "dataset": "TUD-GV floating-litter subset (Jia et al. 2024, Water Research 266:122405), "
                   "doi:10.5281/zenodo.13730228, CC BY 4.0",
        "split": f"{a.split} (grouped by experiment id, seed 42; lists in components/detection/data/splits/)",
        "n_test_images": main_m["n_images"],
        "mAP50": main_m["mAP50"], "mAP50_95": main_m["mAP50_95"],
        "precision": main_m["precision"], "recall": main_m["recall"], "per_class": main_m["per_class"],
        "latency_ms_mps": latency_mps(a.weights, "test", a.imgsz),
        "model_id": a.model_id or f"{Path(a.weights).name}#sha256:{file_hash(a.weights)}",
        "reproduce": a.reproduce,
        "evaluated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "code_commit": _git_sha(),
        "machine": f"{platform.machine()} macOS {platform.mac_ver()[0]} (Apple M5, MPS)",
        "eval_settings": {"imgsz": a.imgsz, "conf": 0.001, "iou_nms": 0.7, "ap": "ultralytics COCO-style 101-pt"},
        "ultralytics_speed_ms": main_m["ultralytics_speed_ms"],
        "other_splits": {s: box_metrics(a.weights, s, a.imgsz) for s in a.also},
    }
    out.update(json.loads(a.extra))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("mAP50", "mAP50_95", "precision", "recall")}),
          {s: v["mAP50"] for s, v in out["other_splits"].items()}, out["latency_ms_mps"]["median"])


if __name__ == "__main__":
    main()
