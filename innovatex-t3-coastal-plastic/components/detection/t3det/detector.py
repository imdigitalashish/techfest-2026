"""C5 vision detector: image -> FrameDetections (contract)."""
from __future__ import annotations

import hashlib
import time
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import numpy as np

from ._contracts import Detection, FrameDetections


@lru_cache(maxsize=8)
def file_hash(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:12]


class Detector:
    def __init__(self, weights: str | Path, imgsz: int = 640, conf: float = 0.25, iou: float = 0.7,
                 device: str = "mps", model_id: str | None = None):
        from ultralytics import YOLO

        self.weights = str(weights)
        self.model = YOLO(self.weights)
        self.imgsz, self.conf, self.iou, self.device = imgsz, conf, iou, device
        self.model_id = model_id or f"{Path(self.weights).name}#sha256:{file_hash(self.weights)}"

    def detect(self, image: str | Path | np.ndarray, frame_id: str, t: datetime | None = None) -> FrameDetections:
        t0 = time.perf_counter()
        r = self.model.predict(image if not isinstance(image, Path) else str(image), imgsz=self.imgsz,
                               conf=self.conf, iou=self.iou, device=self.device, verbose=False)[0]
        latency = (time.perf_counter() - t0) * 1000
        h, w = r.orig_shape
        dets = [Detection(bbox_xyxy=tuple(round(float(v), 1) for v in b), label=r.names[int(c)], score=round(float(s), 4))
                for b, c, s in zip(r.boxes.xyxy.tolist(), r.boxes.cls.tolist(), r.boxes.conf.tolist())]
        return FrameDetections(frame_id=frame_id, t=t, image_wh=(w, h), detections=dets, model_id=self.model_id,
                               latency_ms=round(latency, 2))
