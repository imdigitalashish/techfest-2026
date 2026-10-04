"""Print {"training": {...}} for metrics.json: device, epochs completed, epoch time, total wall-clock, guard events.

    python -m t3det.train_summary <run>/weights/best.pt [<guard run.json>]
Sources: ultralytics results.csv (per-epoch rows, cumulative `time` column), train_meta.json, the guard's run.json.
"""
from __future__ import annotations

import csv
import json
import statistics
import sys
from pathlib import Path


def summary(weights: str, run_json: str | None) -> dict:
    run = Path(weights).parents[1]
    rows = list(csv.DictReader((run / "results.csv").open())) if (run / "results.csv").exists() else []
    rows = [{k.strip(): v.strip() for k, v in r.items()} for r in rows]
    meta = json.loads((run / "train_meta.json").read_text()) if (run / "train_meta.json").exists() else {}
    guard = json.loads(Path(run_json).read_text()) if run_json and Path(run_json).exists() else {}
    t = [float(r["time"]) for r in rows if r.get("time")]
    ep = [b - a for a, b in zip([0.0] + t[:-1], t)] if t else []
    val = [(int(float(r["epoch"])), float(r.get("metrics/mAP50(B)", "nan")), float(r.get("metrics/mAP50-95(B)", "nan")))
           for r in rows]
    best = max(val, key=lambda v: v[2]) if val else None
    out = {
        "device": guard.get("device") or meta.get("device"),
        "imgsz": guard.get("imgsz"),
        "epochs_completed": len(rows),
        "epoch_time_s": {"median": round(statistics.median(ep), 1), "mean": round(statistics.mean(ep), 1),
                         "first": round(ep[0], 1), "last": round(ep[-1], 1)} if ep else None,
        "train_loop_s": round(t[-1], 1) if t else None,
        "total_wall_clock_s": guard.get("wall_clock_s", meta.get("wall_s")),
        "total_wall_clock_note": "trainer process start to exit: dataset cache build + training + ultralytics' final "
                                 "val of best.pt; includes any guard pauses",
        "paused_s_approx": guard.get("paused_s_approx"), "hard_capped": guard.get("hard_capped"),
        "start_ist": guard.get("start_ist"), "end_ist": guard.get("end_ist"), "exit_code": guard.get("exit_code"),
        "val_from_training_log": {"last_epoch": {"epoch": val[-1][0], "mAP50": val[-1][1], "mAP50_95": val[-1][2]},
                                  "max_mAP50_95_epoch": {"epoch": best[0], "mAP50": best[1], "mAP50_95": best[2]}}
        if val else None,
        "recipe": "yolo11n.pt (COCO-pretrained, ultralytics assets v8.3.0) fine-tuned on the TUD-GV grouped train split "
                  "(969 images). ultralytics 8.4.12 defaults (SGD/AdamW auto, mosaic 1.0 with close_mosaic 10, warmup "
                  "3 epochs, hsv/flip augmentations) except: batch 8, workers 2, cache=disk, seed 42 deterministic, "
                  "wall-clock budget `time` (ultralytics re-plans epochs and the LR schedule to fit). best.pt = best "
                  "val fitness. MPS runs use the CPU label-assigner patch (README A3); NMS time limit lifted.",
        "command": guard.get("command") or " ".join(meta.get("argv", [])),
    }
    return {"training": out}


if __name__ == "__main__":
    print(json.dumps(summary(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)))
