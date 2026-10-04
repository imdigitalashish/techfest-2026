"""C6 flux counter: ByteTrack tracks (ultralytics) + line crossing -> FluxEstimate (contract).

Each track id is counted at most once, when its box centre changes side of the counting line in the
configured direction. Items are converted to mass with a MassModel whose provenance is explicit.
"""
from __future__ import annotations

import math
import os
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

    def direction_for_flow(self, flow: tuple[float, float]) -> int:
        """Counter direction (+1/-1) for items moving along `flow`: the side of the line they cross INTO."""
        mx, my = (self.p1[0] + self.p2[0]) / 2, (self.p1[1] + self.p2[1]) / 2
        s = self.side(mx + flow[0], my + flow[1])
        if s == 0:
            raise ValueError(f"flow {flow} is parallel to the counting line")
        return s


# Flow direction names used by the SYNTHETIC ground truth (image coordinates: x right, y down).
FLOW_VECTORS = {"left_to_right": (1.0, 0.0), "right_to_left": (-1.0, 0.0),
                "top_to_bottom": (0.0, 1.0), "bottom_to_top": (0.0, -1.0)}


@dataclass
class LineCrossingCounter:
    line: CountingLine
    direction: int = 0  # 0 = either way (diagnostic only); +1 / -1 = only crossings INTO side +1 / -1
    last_side: dict[int, int] = field(default_factory=dict)
    counted: set[int] = field(default_factory=set)
    by_label: Counter = field(default_factory=Counter)
    events: list[dict] = field(default_factory=list)

    def update(self, track_id: int, cx: float, cy: float, label: str = "litter", t: float | None = None) -> bool:
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
        self.events.append({"track_id": track_id, "t": t, "x": round(cx, 1), "y": round(cy, 1), "label": label})
        return True

    @property
    def count(self) -> int:
        return len(self.counted)


@dataclass
class MassModel:
    """Items -> kg. Per-item mass mean/sd from a cited survey; 90% CI of a sum of n independent items (CLT)."""
    mean_g: float
    sd_g: float
    kind: str  # provenance of the factor for OUR site: "assumption" when transferred from another river
    source: str

    def kg(self, n: int) -> tuple[float, tuple[float, float]]:
        half = 1.645 * self.sd_g * math.sqrt(n)
        return n * self.mean_g / 1000, (max(0.0, n * self.mean_g - half) / 1000, (n * self.mean_g + half) / 1000)


# van Emmerik et al. (2019) Sci. Rep., "Seasonality of riverine macroplastic transport" (Saigon River),
# https://pmc.ncbi.nlm.nih.gov/articles/PMC6753078/ (opened 2026-10-04): "each visually counted particle equals on
# average 1.9 x 10^-2 kg (sigma = 3.7 x 10^-2 kg) sampled plastic in the upper 0.5 m"; net-sampled items average
# 1.0 x 10^-2 kg/item (sigma 3.3 x 10^-2, N = 3057). Transfer from Saigon to Mumbai nullahs is an ASSUMPTION.
SAIGON_VISUAL_COUNT = MassModel(
    mean_g=19.0, sd_g=37.0, kind="assumption",
    source="van Emmerik et al. 2019 Sci Rep (Saigon), PMC6753078: 1.9e-2 kg per visually counted item, sd 3.7e-2; "
           "transfer to Mumbai assumed")


class FluxCounter:
    def __init__(self, weights: str, line: CountingLine, site_id: str, mass: MassModel, imgsz: int = 640,
                 conf: float = 0.1, tracker: str = "bytetrack.yaml", direction: int = 0, device: str | None = None):
        from ultralytics import YOLO

        self.model = YOLO(weights)
        self.weights, self.line, self.site_id, self.mass = weights, line, site_id, mass
        self.imgsz, self.conf, self.tracker, self.direction = imgsz, conf, tracker, direction
        self.device = device or os.environ.get("T3DET_DEVICE", "mps")

    def run(self, frames: Iterable[np.ndarray], t_start: datetime, fps: float, provenance: Provenance,
            on_frame=None) -> FluxEstimate:
        counter = LineCrossingCounter(self.line, self.direction)
        self.last_counter = counter
        # ultralytics binds `persist` once, at the first track() call (register_tracker); persist=False there re-creates
        # ByteTrack on EVERY later call, so IDs restart each frame. Always persist; reset explicitly per clip instead.
        for trk in getattr(getattr(self.model, "predictor", None), "trackers", None) or []:
            trk.reset()
        n_frames = 0
        for i, frame in enumerate(frames):
            r = self.model.track(frame, persist=True, tracker=self.tracker, conf=self.conf, imgsz=self.imgsz,
                                 device=self.device, verbose=False)[0]
            n_frames += 1
            if r.boxes.id is not None:
                for (x1, y1, x2, y2), tid, c in zip(r.boxes.xyxy.tolist(), r.boxes.id.int().tolist(),
                                                    r.boxes.cls.int().tolist()):
                    counter.update(tid, (x1 + x2) / 2, (y1 + y2) / 2, r.names[c], t=i)
            if on_frame:
                on_frame(i, r, counter)
        minutes = n_frames / fps / 60
        est, ci = self.mass.kg(counter.count)
        return FluxEstimate(
            site_id=self.site_id, t_start=t_start, t_end=t_start + timedelta(seconds=n_frames / fps),
            items_crossed=counter.count, items_per_min=round(counter.count / minutes, 3) if minutes else 0.0,
            by_label=dict(counter.by_label), est_kg=round(est, 4), est_kg_ci90=(round(ci[0], 4), round(ci[1], 4)),
            method=(f"YOLO detector + ByteTrack (ultralytics, persistent across frames, conf>={self.conf}) + "
                    f"line-crossing count, one count per track id, direction "
                    f"{'either (diagnostic)' if not self.direction else f'into side {self.direction:+d} only'}; mass = items x {self.mass.mean_g} g/item (sd {self.mass.sd_g} g; {self.mass.kind}: "
                    f"{self.mass.source}); CI90 = n*mean +/- 1.645*sd*sqrt(n)"),
            provenance=provenance)


def count_error_pct(predicted: int, truth: int) -> float:
    return 100.0 * abs(predicted - truth) / max(truth, 1)
