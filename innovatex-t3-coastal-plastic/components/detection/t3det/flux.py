"""C6 flux counter: ByteTrack tracks (ultralytics) + line crossing -> FluxEstimate (contract).

Each track id is counted at most once, when its box centre changes side of the counting line in the
configured direction. Items are converted to mass with a MassModel whose provenance is explicit.
"""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Iterable

import numpy as np

from ._contracts import FluxEstimate, Provenance


@dataclass
class CountingLine:
    p1: tuple[float, float]
    p2: tuple[float, float]

    def side(self, x: float, y: float) -> int:
        (x1, y1), (x2, y2) = self.p1, self.p2
        v = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)
        return 0 if v == 0 else (1 if v > 0 else -1)


@dataclass
class LineCrossingCounter:
    line: CountingLine
    direction: int = 0  # 0 = either way; +1 / -1 = only crossings from side -d to side +d
    last_side: dict[int, int] = field(default_factory=dict)
    counted: set[int] = field(default_factory=set)
    by_label: Counter = field(default_factory=Counter)

    def update(self, track_id: int, cx: float, cy: float, label: str = "litter") -> bool:
        s = self.line.side(cx, cy)
        prev = self.last_side.get(track_id)
        if s != 0:
            self.last_side[track_id] = s
        if prev is None or s == 0 or s == prev or track_id in self.counted:
            return False
        if self.direction and s != self.direction:
            return False
        self.counted.add(track_id)
        self.by_label[label] += 1
        return True

    @property
    def count(self) -> int:
        return len(self.counted)


@dataclass
class MassModel:
    """Per-item mass distribution (lognormal fitted to a mean and a 90% interval of the mean item mass)."""
    mean_g: float
    ci90_g: tuple[float, float]
    kind: str  # Provenance kind of the conversion factor: "observed" (cited) or "assumption"
    source: str

    def kg(self, n: int) -> tuple[float, tuple[float, float]]:
        lo, hi = self.ci90_g
        return n * self.mean_g / 1000, (n * lo / 1000, n * hi / 1000)


class FluxCounter:
    def __init__(self, weights: str, line: CountingLine, site_id: str, mass: MassModel, imgsz: int = 640,
                 conf: float = 0.1, tracker: str = "bytetrack.yaml", direction: int = 0, device: str = "mps"):
        from ultralytics import YOLO

        self.model = YOLO(weights)
        self.weights, self.line, self.site_id, self.mass = weights, line, site_id, mass
        self.imgsz, self.conf, self.tracker, self.direction, self.device = imgsz, conf, tracker, direction, device

    def run(self, frames: Iterable[np.ndarray], t_start: datetime, fps: float, provenance: Provenance,
            on_frame=None) -> FluxEstimate:
        counter = LineCrossingCounter(self.line, self.direction)
        n_frames = 0
        for i, frame in enumerate(frames):
            r = self.model.track(frame, persist=i > 0, tracker=self.tracker, conf=self.conf, imgsz=self.imgsz,
                                 device=self.device, verbose=False)[0]
            n_frames += 1
            if r.boxes.id is not None:
                for (x1, y1, x2, y2), tid, c in zip(r.boxes.xyxy.tolist(), r.boxes.id.int().tolist(),
                                                    r.boxes.cls.int().tolist()):
                    counter.update(tid, (x1 + x2) / 2, (y1 + y2) / 2, r.names[c])
            if on_frame:
                on_frame(i, r, counter)
        minutes = n_frames / fps / 60
        est, ci = self.mass.kg(counter.count)
        return FluxEstimate(
            site_id=self.site_id, t_start=t_start, t_end=t_start + timedelta(seconds=n_frames / fps),
            items_crossed=counter.count, items_per_min=round(counter.count / minutes, 3) if minutes else 0.0,
            by_label=dict(counter.by_label), est_kg=round(est, 4), est_kg_ci90=(round(ci[0], 4), round(ci[1], 4)),
            method=(f"YOLO detector + ByteTrack (ultralytics, conf>={self.conf}) + line-crossing count, one count per "
                    f"track id; mass = items x mean item mass ({self.mass.mean_g} g, {self.mass.kind}: {self.mass.source})"),
            provenance=provenance)


def lognormal_ci90(mean: float, cv: float) -> tuple[float, float]:
    """90% interval of a lognormal with given mean and coefficient of variation (helper for assumptions)."""
    s2 = math.log(1 + cv * cv)
    mu = math.log(mean) - s2 / 2
    s = math.sqrt(s2)
    return math.exp(mu - 1.645 * s), math.exp(mu + 1.645 * s)
