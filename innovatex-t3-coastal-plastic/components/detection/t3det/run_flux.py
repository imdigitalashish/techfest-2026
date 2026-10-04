"""Run C6 on the SYNTHETIC sequence and score the count against ground truth.

    python -m t3det.run_flux --weights <best.pt> --seq .data/detection/synth/seq01
Writes results/flux_synthetic.json: {label: SYNTHETIC, gt_crossings, items_crossed, count_error_pct, flux_estimate}.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import cv2

from ._contracts import Provenance
from .flux import SAIGON_VISUAL_COUNT, CountingLine, FluxCounter, count_error_pct
from .paths import DATA, RESULTS


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--weights", required=True)
    p.add_argument("--seq", default=str(DATA / "synth" / "seq01"))
    p.add_argument("--conf", type=float, default=0.1)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--out", default=str(RESULTS / "flux_synthetic.json"))
    a = p.parse_args()
    import torch

    torch.set_num_threads(4)
    seq = Path(a.seq)
    gt = json.loads((seq / "gt.json").read_text())
    (x1, y1), (x2, y2) = gt["line"]
    line = CountingLine((x1, y1), (x2, y2))  # direction=0: count a track once, whichever way it crosses
    fc = FluxCounter(a.weights, line, site_id="SYNTHETIC-seq01", mass=SAIGON_VISUAL_COUNT, imgsz=a.imgsz,
                     conf=a.conf, direction=0)
    frames = (cv2.imread(str(f)) for f in sorted((seq / "frames").glob("*.jpg")))
    t0 = datetime(2026, 10, 4, 0, 0, tzinfo=timezone.utc)
    prov = Provenance(kind="synthetic", source=f"component:detection/t3det.synth seed={gt['seed']}",
                      retrieved_at=datetime.now(timezone.utc),
                      notes="SYNTHETIC: real TUD-GV test-split litter crops pasted on an inpainted TUD-GV water frame; "
                            "mass factor is an ASSUMPTION transferred from the Saigon River (van Emmerik et al. 2019)")
    est = fc.run(frames, t0, fps=gt["fps"], provenance=prov)
    out = {"label": "SYNTHETIC", "sequence": str(seq.name), "frames": gt["frames"], "fps": gt["fps"],
           "gt_crossings": gt["gt_crossings"], "items_crossed": est.items_crossed,
           "count_error_pct": round(count_error_pct(est.items_crossed, gt["gt_crossings"]), 2),
           "detector_weights": Path(a.weights).name, "tracker": "bytetrack.yaml (ultralytics defaults)",
           "conf": a.conf, "imgsz": a.imgsz,
           "reproduce": f"python -m t3det.synth --out {a.seq} --frames {gt['frames']} --items {gt['n_items']} "
                        f"--seed {gt['seed']} && python -m t3det.run_flux --weights <best.pt> --seq {a.seq}",
           "flux_estimate": json.loads(est.model_dump_json())}
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("gt_crossings", "items_crossed", "count_error_pct")}))


if __name__ == "__main__":
    main()
