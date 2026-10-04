"""Train a YOLO floating-litter detector on the TUD-GV grouped split (val = model selection only).

    python -m t3det.train --model yolo11n.pt --imgsz 640 --epochs 50 --time 0.85 --name baseline_yolo11n_640
Extra ultralytics hyper-parameters: --hyp mosaic=1.0 copy_paste=0.3 hsv_v=0.5 ...
Weights and logs go to .data/detection/runs/<name>/ (gitignored). The test split is never touched here.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .paths import DATA, RUNS, SEED, YOLO

WEIGHTS = DATA / "weights"


def _val(v: str):
    for cast in (int, float):
        try:
            return cast(v)
        except ValueError:
            pass
    return {"true": True, "false": False}.get(v.lower(), v)


def train(model: str, imgsz: int, epochs: int, name: str, time_h: float | None = None, batch: int = 8,
          workers: int = 2, hyp: dict | None = None, data: Path = YOLO / "tudgv.yaml") -> Path:
    from ultralytics import YOLO as Y

    from . import mps_patch

    mps_patch.apply()
    import torch

    torch.set_num_threads(4)  # shared 10-core machine; the CPU-side label assigner needs only a few
    src = WEIGHTS / model if (WEIGHTS / model).exists() else model
    m = Y(str(src))
    args = dict(data=str(data), imgsz=imgsz, epochs=epochs, batch=batch, workers=workers, device="mps",
                seed=SEED, deterministic=True, project=str(RUNS), name=name, exist_ok=True, plots=False,
                cache=False, patience=100, verbose=False)
    if time_h:
        args["time"] = time_h
    args.update(hyp or {})
    t0 = time.time()
    m.train(**args)
    run = RUNS / name
    (run / "train_meta.json").write_text(json.dumps(
        {"model": model, "args": {k: str(v) for k, v in args.items()}, "wall_s": round(time.time() - t0, 1)}, indent=1))
    return run / "weights" / "best.pt"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="yolo11n.pt")
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--time", type=float, default=None, help="wall-clock cap in hours (ultralytics `time`)")
    p.add_argument("--batch", type=int, default=8)
    p.add_argument("--name", required=True)
    p.add_argument("--hyp", nargs="*", default=[])
    a = p.parse_args()
    hyp = {k: _val(v) for k, v in (h.split("=", 1) for h in a.hyp)}
    print(train(a.model, a.imgsz, a.epochs, a.name, a.time, a.batch, hyp=hyp))


if __name__ == "__main__":
    main()
