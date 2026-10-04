"""Write results/sample_detections.json (list of FrameDetections) + <=5 annotated test images (<=200 KB each).

    python -m t3det.samples --weights <best.pt> --n 5
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import cv2

from .detector import Detector
from .paths import RESULTS, SEED, YOLO


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--weights", required=True)
    p.add_argument("--n", type=int, default=5)
    p.add_argument("--conf", type=float, default=0.25)
    a = p.parse_args()
    test = (YOLO / "test.txt").read_text().split()
    picks = random.Random(SEED).sample(test, a.n)
    det = Detector(a.weights, conf=a.conf)
    out_dir = RESULTS / "samples"
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.jpg"):
        old.unlink()
    frames = []
    for pth in picks:
        fd = det.detect(Path(pth), frame_id=f"tudgv-test/{Path(pth).name}")
        frames.append(json.loads(fd.model_dump_json()))
        img = cv2.imread(pth)
        h, w = img.shape[:2]
        lab = Path(pth).parent.parent / "labels" / (Path(pth).stem + ".txt")
        for ln in lab.read_text().splitlines():  # ground truth in green
            if ln.strip():
                _, cx, cy, bw, bh = map(float, ln.split())
                cv2.rectangle(img, (int((cx - bw / 2) * w), int((cy - bh / 2) * h)),
                              (int((cx + bw / 2) * w), int((cy + bh / 2) * h)), (0, 200, 0), 2)
        for d in fd.detections:  # predictions in red with score
            x1, y1, x2, y2 = map(int, d.bbox_xyxy)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(img, f"{d.score:.2f}", (x1, max(12, y1 - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        cv2.putText(img, "green = ground truth, red = C5 prediction (TUD-GV test split)", (10, 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        dst = out_dir / (Path(pth).stem + ".jpg")
        small = cv2.resize(img, (960, int(960 * h / w)))
        for q in (80, 70, 60, 50, 40):
            cv2.imwrite(str(dst), small, [cv2.IMWRITE_JPEG_QUALITY, q])
            if dst.stat().st_size <= 200_000:
                break
    (RESULTS / "sample_detections.json").write_text(json.dumps(frames, indent=1) + "\n")
    print(f"{len(frames)} frames, {sum(len(f['detections']) for f in frames)} detections -> {RESULTS}")


if __name__ == "__main__":
    main()
