"""C6 evaluation on SYNTHETIC clips with exact ground-truth crossings (review fix 2026-10-04, finding #3).

    T3DET_DEVICE=cpu nice -n 10 python3.11 -m t3det.run_flux --weights <best.pt> --legacy-diagnostic
    T3DET_DEVICE=cpu nice -n 10 python3.11 -m t3det.run_flux --weights <yolo11n.pt> --sequences seq02 \
        --detector-kind "ZERO-SHOT COCO-pretrained YOLO11n" --out results/flux_synthetic_zeroshot.json

- Direction: the counter's direction is derived from the ground truth (gt.json `flow_vector`), so prediction and
  truth count the same crossings. Counting both directions is replayed on the SAME tracks as a labelled diagnostic.
- Matching: predicted crossings are matched one-to-one to GT crossings (Hungarian assignment). A pair is admissible
  when |dt| <= TOL_S seconds and |dy| <= max(16 px, half the item's height) at the counting line. Reported as matched /
  false (duplicate: an admissible GT crossing exists but is taken; spurious: none nearby) / missed.
- Signed count error = 100 * (predicted - truth) / truth, pooled over the suite; 95% interval = percentile bootstrap
  over sequences (2,000 resamples, seed 0).
Sequences are regenerated deterministically (t3det.synth) when missing or outdated.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

import cv2
import numpy as np

from . import synth
from ._contracts import Provenance
from .detector import model_id_for
from .flux import FLOW_VECTORS, SAIGON_VISUAL_COUNT, CountingLine, FluxCounter, LineCrossingCounter, count_error_pct
from .paths import DATA, RESULTS

SUITE = {
    "seq01": {"frames": 300, "items": 24, "seed": 7, "speed": [4, 9]},
    "seq02": {"frames": 120, "items": 12, "seed": 11, "speed": [6, 12]},
    **{f"seq{s}": {"frames": 200, "items": 12, "seed": s, "speed": [5, 12]} for s in range(21, 29)},
}
REFERENCE = "seq02"  # the clip published before the fix: top-level fields + FluxEstimate
TOL_S = 1.0
SENSITIVITY_S = (0.4, 1.0, 2.0)
Y_GATE_MIN_PX = 16.0
IST = timezone(timedelta(hours=5, minutes=30))


def counter_direction(gt: dict) -> int:
    """Direction sign for LineCrossingCounter that counts exactly the ground truth's crossings."""
    line = CountingLine(tuple(gt["line"][0]), tuple(gt["line"][1]))
    flow = tuple(gt.get("flow_vector") or FLOW_VECTORS[gt["direction"]])
    return line.direction_for_flow(flow)


def ensure_sequence(name: str, spec: dict) -> dict:
    d = DATA / "synth" / name
    if (d / "gt.json").exists():
        gt = json.loads((d / "gt.json").read_text())
        if (gt.get("seed") == spec["seed"] and gt.get("frames") == spec["frames"] and gt.get("n_items") == spec["items"]
                and list(gt.get("speed_px_per_frame", [])) == list(spec["speed"]) and gt.get("flow_vector")
                and all("y" in c for c in gt["crossings"])):
            return gt
    shutil.rmtree(d, ignore_errors=True)
    return synth.generate(d, spec["frames"], spec["items"], spec["seed"], speed=tuple(spec["speed"]))


def match(pred: list[dict], gt: list[dict], tol_frames: float) -> dict:
    """One-to-one matching of predicted crossings {t, y} to GT crossings {frame, y, h}."""
    from scipy.optimize import linear_sum_assignment

    P, G = len(pred), len(gt)
    adm = np.zeros((P, G), bool)
    cost = np.full((P, G), 1e6)
    for i, p in enumerate(pred):
        for j, g in enumerate(gt):
            gate = max(Y_GATE_MIN_PX, 0.5 * g["h"])
            dt, dy = abs(p["t"] - g["frame"]), abs(p["y"] - g["y"])
            if dt <= tol_frames and dy <= gate:
                adm[i, j] = True
                cost[i, j] = dt / max(tol_frames, 1e-9) + dy / gate
    pairs = []
    if P and G:
        r, c = linear_sum_assignment(cost)
        pairs = [(int(i), int(j)) for i, j in zip(r, c) if adm[i, j]]
    mp, mg = {i for i, _ in pairs}, {j for _, j in pairs}
    false = [i for i in range(P) if i not in mp]
    dup = [i for i in false if adm[i].any()]
    return {"matched": len(pairs), "false": len(false), "false_duplicate": len(dup),
            "false_spurious": len(false) - len(dup), "missed": G - len(pairs),
            "pairs": pairs, "dup_idx": dup, "missed_idx": [j for j in range(G) if j not in mg],
            "nearest_gt": {i: int(np.argmin(np.where(adm[i], cost[i], np.inf))) for i in dup}}


def _frames(name: str):
    return (cv2.imread(str(f)) for f in sorted((DATA / "synth" / name / "frames").glob("*.jpg")))


def evaluate_sequence(weights: str, name: str, gt: dict, imgsz: int, conf: float, device: str) -> tuple[dict, dict]:
    line = CountingLine(tuple(gt["line"][0]), tuple(gt["line"][1]))
    sign = counter_direction(gt)
    fc = FluxCounter(weights, line, site_id=f"SYNTHETIC-{name}", mass=SAIGON_VISUAL_COUNT, imgsz=imgsz, conf=conf,
                     direction=sign, device=device)
    tracks: list[tuple] = []

    def on_frame(i, r, _counter):
        if r.boxes.id is not None:
            for (x1, y1, x2, y2), tid, c in zip(r.boxes.xyxy.tolist(), r.boxes.id.int().tolist(),
                                                r.boxes.cls.int().tolist()):
                tracks.append((i, tid, (x1 + x2) / 2, (y1 + y2) / 2, r.names[c]))

    prov = Provenance(kind="synthetic", source=f"component:detection/t3det.synth seed={gt['seed']}",
                      retrieved_at=datetime.now(timezone.utc),
                      notes="SYNTHETIC: real TUD-GV test-split litter crops pasted on an inpainted TUD-GV water frame; "
                            "mass factor is an ASSUMPTION transferred from the Saigon River (van Emmerik et al. 2019)")
    est = fc.run(_frames(name), datetime(2026, 10, 4, tzinfo=timezone.utc), fps=gt["fps"], provenance=prov,
                 on_frame=on_frame)
    events = fc.last_counter.events
    replay = {}
    for key, d in (("matched_direction", sign), ("both_directions", 0)):
        c = LineCrossingCounter(line, d)
        for i, tid, cx, cy, lab in tracks:
            c.update(tid, cx, cy, lab, t=i)
        replay[key] = c
    assert replay["matched_direction"].count == est.items_crossed, "replay must reproduce the in-run count"
    tol = TOL_S * gt["fps"]
    m = match(events, gt["crossings"], tol)
    mb = match(replay["both_directions"].events, gt["crossings"], tol)
    items = {it["id"]: it for it in gt["items"]}
    multi = sum(1 for i in m["dup_idx"]
                if items[gt["crossings"][m["nearest_gt"][i]]["id"]].get("other_gt_boxes_in_crop", 0) > 0)
    row = {"sequence": name, "seed": gt["seed"], "frames": gt["frames"], "gt_crossings": gt["gt_crossings"],
           "predicted": est.items_crossed, **{k: m[k] for k in ("matched", "false", "false_duplicate",
                                                               "false_spurious", "missed")},
           "signed_count_error_pct": round(100 * (est.items_crossed - gt["gt_crossings"]) / max(gt["gt_crossings"], 1), 2),
           "duplicates_on_multi_box_crops": multi,
           "unique_track_ids": len({t[1] for t in tracks}),
           "both_directions": {"predicted": replay["both_directions"].count,
                               **{k: mb[k] for k in ("matched", "false", "missed")}},
           "sensitivity": {f"{s}s": {k: match(events, gt["crossings"], s * gt["fps"])[k]
                                     for k in ("matched", "false", "missed")} for s in SENSITIVITY_S},
           "missed_item_crop_h": sorted(gt["crossings"][j]["h"] for j in m["missed_idx"]),
           "matched_item_crop_h": sorted(gt["crossings"][j]["h"] for _, j in m["pairs"])}
    return row, json.loads(est.model_dump_json())


def legacy_overnight(weights: str, name: str, gt: dict, imgsz: int, conf: float, device: str) -> dict:
    """The configuration published before the fix: persist=False on the first track() call (tracker re-created on
    every frame) and both directions counted. Reproduced only to explain the old number."""
    from ultralytics import YOLO

    model, line = YOLO(weights), CountingLine(tuple(gt["line"][0]), tuple(gt["line"][1]))
    c, ids = LineCrossingCounter(line, 0), set()
    for i, frame in enumerate(_frames(name)):
        r = model.track(frame, persist=i > 0, tracker="bytetrack.yaml", conf=conf, imgsz=imgsz, device=device,
                        verbose=False)[0]
        if r.boxes.id is not None:
            for (x1, y1, x2, y2), tid, k in zip(r.boxes.xyxy.tolist(), r.boxes.id.int().tolist(), r.boxes.cls.int().tolist()):
                c.update(tid, (x1 + x2) / 2, (y1 + y2) / 2, r.names[k], t=i)
                ids.add(tid)
    m = match(c.events, gt["crossings"], TOL_S * gt["fps"])
    return {"label": "DIAGNOSTIC - configuration published before the fix (tracker re-initialised every frame by "
                     "persist=False on the first call; both directions counted). Not a valid C6 result.",
            "sequence": name, "gt_crossings": gt["gt_crossings"], "predicted": c.count,
            "unique_track_ids": len(ids), **{k: m[k] for k in ("matched", "false", "missed")}}


def pooled(rows: list[dict], both: bool = False, boot: int = 2000) -> dict:
    P = np.array([r["both_directions"]["predicted"] if both else r["predicted"] for r in rows], float)
    G = np.array([r["gt_crossings"] for r in rows], float)
    out = {"signed_count_error_pct": round(float(100 * (P.sum() - G.sum()) / G.sum()), 2)}
    if len(rows) >= 3:
        idx = np.random.default_rng(0).integers(0, len(rows), (boot, len(rows)))
        b = 100 * (P[idx].sum(1) - G[idx].sum(1)) / G[idx].sum(1)
        out["signed_count_error_ci95_pct"] = [round(float(v), 2) for v in np.percentile(b, [2.5, 97.5])]
        out["ci_method"] = f"percentile bootstrap over {len(rows)} sequences, {boot} resamples, seed 0"
    else:
        out["signed_count_error_ci95_pct"] = None
        out["ci_method"] = "not computed (fewer than 3 sequences)"
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--weights", required=True)
    p.add_argument("--sequences", default="all", help="'all' or comma-separated names from SUITE")
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--conf", type=float, default=0.1)
    p.add_argument("--device", default=os.environ.get("T3DET_DEVICE", "mps"))
    p.add_argument("--detector-kind", default="trained baseline")
    p.add_argument("--legacy-diagnostic", action="store_true", help="also run the pre-fix configuration on seq02")
    p.add_argument("--out", default=str(RESULTS / "flux_synthetic.json"))
    a = p.parse_args()
    import torch

    torch.set_num_threads(4)
    names = list(SUITE) if a.sequences == "all" else a.sequences.split(",")
    rows, ref_est, gts = [], None, {}
    for n in names:
        gts[n] = ensure_sequence(n, SUITE[n])
        row, est = evaluate_sequence(a.weights, n, gts[n], a.imgsz, a.conf, a.device)
        rows.append(row)
        if n == REFERENCE or ref_est is None:
            ref_name, ref_est = n, est
        print(json.dumps({k: row[k] for k in ("sequence", "gt_crossings", "predicted", "matched", "false", "missed")}), flush=True)
    tot = {k: sum(r[k] for r in rows) for k in ("gt_crossings", "predicted", "matched", "false", "false_duplicate",
                                                "false_spurious", "missed", "duplicates_on_multi_box_crops")}
    both = {k: sum(r["both_directions"][k] for r in rows) for k in ("predicted", "matched", "false", "missed")}
    ref = next(r for r in rows if r["sequence"] == ref_name)
    gt0 = gts[ref_name]
    seq_args = a.sequences
    out = {
        "label": "SYNTHETIC",
        "what": "C6 count accuracy on SYNTHETIC clips: real TUD-GV test-split litter crops drift left to right over an "
                "inpainted TUD-GV water frame, with exact ground-truth line crossings",
        "detector": a.detector_kind, "detector_model_id": model_id_for(a.weights), "device": a.device,
        "imgsz": a.imgsz, "conf": a.conf,
        "tracker": "ByteTrack (ultralytics bytetrack.yaml defaults), persistent across frames, reset per clip",
        "counter_direction": {"line": gt0["line"], "gt_direction": gt0["direction"], "flow_vector": gt0["flow_vector"],
                              "direction_sign": counter_direction(gt0),
                              "rule": "derived from the ground truth via CountingLine.direction_for_flow, so the "
                                      "counter counts exactly the crossings the ground truth counts"},
        "matching": {"tolerance_s": TOL_S, "tolerance_frames": TOL_S * gt0["fps"],
                     "y_gate": f"|dy| <= max({Y_GATE_MIN_PX:.0f} px, 0.5 x item height)",
                     "assignment": "one-to-one, Hungarian (scipy linear_sum_assignment) minimising "
                                   "|dt|/tol + |dy|/gate over admissible pairs",
                     "false_duplicate": "an admissible GT crossing exists but is already matched",
                     "false_spurious": "no GT crossing within the tolerance"},
        "headline": {"sequences": len(rows), **tot,
                     "crossing_precision": round(tot["matched"] / max(tot["predicted"], 1), 4),
                     "crossing_recall": round(tot["matched"] / max(tot["gt_crossings"], 1), 4),
                     **pooled(rows),
                     "abs_count_error_pct": round(count_error_pct(tot["predicted"], tot["gt_crossings"]), 2)},
        "sensitivity_pooled": {k: {m: sum(r["sensitivity"][k][m] for r in rows) for m in ("matched", "false", "missed")}
                               for k in rows[0]["sensitivity"]},
        "diagnostics": {"both_directions_same_tracks": {
            "label": "DIAGNOSTIC - counts crossings in either direction; the ground truth counts left-to-right only",
            **both, **pooled(rows, both=True)}},
        "sequence": ref_name, "frames": gt0["frames"], "fps": gt0["fps"], "gt_crossings": ref["gt_crossings"],
        "items_crossed": ref["predicted"], "count_error_pct": round(count_error_pct(ref["predicted"], ref["gt_crossings"]), 2),
        "signed_count_error_pct": ref["signed_count_error_pct"],
        "matched": ref["matched"], "false": ref["false"], "missed": ref["missed"],
        "per_sequence": rows,
        "flux_estimate": ref_est,
        "evaluated_at": datetime.now(IST).isoformat(timespec="seconds"),
        "reproduce": (f"cd innovatex-t3-coastal-plastic/components/detection && T3DET_DEVICE={a.device} nice -n 10 "
                      f"python3.11 -m t3det.run_flux --weights {a.weights} --sequences {seq_args} --imgsz {a.imgsz} "
                      f"--conf {a.conf}" + (" --legacy-diagnostic" if a.legacy_diagnostic else "")
                      + (f" --detector-kind \"{a.detector_kind}\" --out {a.out}" if a.detector_kind != "trained baseline" else "")
                      + "   (sequences are regenerated deterministically by t3det.synth from SUITE in t3det/run_flux.py)"),
    }
    if a.legacy_diagnostic and REFERENCE in gts:
        out["diagnostics"]["legacy_overnight_config"] = legacy_overnight(a.weights, REFERENCE, gts[REFERENCE], a.imgsz,
                                                                        a.conf, a.device)
    Path(a.out).write_text(json.dumps(out, indent=1) + "\n")
    h = out["headline"]
    print(json.dumps({k: h[k] for k in ("sequences", "gt_crossings", "predicted", "matched", "false", "missed",
                                        "signed_count_error_pct", "signed_count_error_ci95_pct")}))


if __name__ == "__main__":
    main()
