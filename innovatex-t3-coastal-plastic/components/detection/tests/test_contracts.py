"""Contract tests for C5/C6 outputs against architecture/contracts/contracts.py.

    cd components/detection && python3.11 -m pytest -q tests
Output-file tests skip if the file has not been produced yet; logic tests always run (no GPU, no weights).
"""
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import pytest

from t3det._contracts import FluxEstimate, FrameDetections, Provenance
from t3det.flux import (FLOW_VECTORS, SAIGON_VISUAL_COUNT, CountingLine, FluxCounter, LineCrossingCounter,
                        MassModel, count_error_pct)
from t3det.paths import RESULTS, SPLITS

METRICS = RESULTS / "metrics.json"
SAMPLES = RESULTS / "sample_detections.json"
FLUX = RESULTS / "flux_synthetic.json"


def _need(p: Path):
    if not p.exists():
        pytest.skip(f"{p.name} not produced yet")
    return json.loads(p.read_text())


def test_sample_detections_match_contract():
    frames = [FrameDetections.model_validate(f) for f in _need(SAMPLES)]
    assert 1 <= len(frames) <= 5
    for f in frames:
        w, h = f.image_wh
        assert f.model_id and f.latency_ms is not None and f.latency_ms > 0
        for d in f.detections:
            x1, y1, x2, y2 = d.bbox_xyxy
            assert 0 <= x1 < x2 <= w + 1 and 0 <= y1 < y2 <= h + 1
            assert 0 <= d.score <= 1 and d.label == "litter"


def test_sample_images_small():
    imgs = list((RESULTS / "samples").glob("*.jpg"))
    if not imgs:
        pytest.skip("no sample images yet")
    assert len(imgs) <= 5 and all(p.stat().st_size <= 200_000 for p in imgs)


def test_metrics_json_shape():
    m = _need(METRICS)
    for k in ("dataset", "split", "n_test_images", "mAP50", "mAP50_95", "precision", "recall", "per_class",
              "latency_ms_mps", "model_id", "reproduce"):
        assert k in m, k
    assert m["n_test_images"] == len((SPLITS / "test.txt").read_text().split())
    for k in ("mAP50", "mAP50_95", "precision", "recall"):
        assert 0 <= m[k] <= 1
    assert m["mAP50_95"] <= m["mAP50"]
    assert "litter" in m["per_class"]


def test_flux_outputs_match_contract():
    files = sorted(RESULTS.glob("flux_synthetic*.json"))
    if not files:
        pytest.skip("no flux output yet")
    for fp in files:
        f = json.loads(fp.read_text())
        est = FluxEstimate.model_validate(f["flux_estimate"])
        assert f["label"] == "SYNTHETIC" and est.provenance.kind == "synthetic", fp.name
        assert est.items_crossed == f["items_crossed"]
        lo, hi = est.est_kg_ci90
        assert lo <= est.est_kg <= hi
        assert math.isclose(f["count_error_pct"], count_error_pct(f["items_crossed"], f["gt_crossings"]), abs_tol=0.01)


def test_zero_shot_reference_is_labelled():
    z = _need(RESULTS / "metrics_zeroshot.json")
    assert z["label"].startswith("ZERO-SHOT") and "ZERO-SHOT" in z["baseline_kind"]
    for k in ("mAP50", "mAP50_95", "precision", "recall"):
        assert 0 <= z[k] <= 1


def test_trained_metrics_record_training_run():
    m = _need(METRICS)
    if "ZERO-SHOT" in m.get("baseline_kind", ""):
        pytest.skip("metrics.json still holds the zero-shot reference")
    tr = m["training"]
    assert m["device"] in ("mps", "cpu") and tr["device"] == m["device"]
    assert tr["epochs_completed"] >= 1 and tr["epoch_time_s"]["median"] > 0 and tr["total_wall_clock_s"] > 0
    assert set(m["other_splits"]) >= {"val", "groningen"}
    assert m["other_splits"]["groningen"]["n_images"] == len((SPLITS / "groningen.txt").read_text().split())


def test_splits_disjoint_and_grouped():
    s = {k: set((SPLITS / f"{k}.txt").read_text().split()) for k in ("train", "val", "test")}
    assert not (s["train"] & s["val"]) and not (s["train"] & s["test"]) and not (s["val"] & s["test"])
    exp = {k: {n.split("_")[0] for n in v} for k, v in s.items()}
    assert not (exp["train"] & exp["test"]) and not (exp["val"] & exp["test"]) and not (exp["train"] & exp["val"])


def test_line_crossing_counts_each_track_once():
    c = LineCrossingCounter(CountingLine((100, 0), (100, 200)))
    for x in (80, 95, 105, 98, 110, 120):  # jitter around the line must count once
        c.update(1, x, 50)
    for x in (150, 140):  # never crosses
        c.update(2, x, 60)
    c.update(3, 90, 10)
    c.update(3, 110, 10)
    assert c.count == 2 and c.by_label["litter"] == 2


def test_direction_filter():
    c = LineCrossingCounter(CountingLine((100, 0), (100, 200)), direction=-1)
    c.update(1, 90, 50)
    c.update(1, 110, 50)  # left -> right: side +1 -> -1, matches direction -1 -> counted
    c.update(2, 110, 50)
    c.update(2, 90, 50)  # right -> left: side -1 -> +1 -> rejected
    assert c.count == 1 and 1 in c.counted


def test_mass_model_ci():
    est, (lo, hi) = SAIGON_VISUAL_COUNT.kg(100)
    assert math.isclose(est, 1.9) and lo < est < hi and lo >= 0
    assert MassModel(10, 0, "assumption", "x").kg(3) == (0.03, (0.03, 0.03))


def test_flux_estimate_constructs():
    est = FluxEstimate(site_id="s", t_start=datetime(2026, 10, 4, tzinfo=timezone.utc),
                       t_end=datetime(2026, 10, 4, 0, 1, tzinfo=timezone.utc), items_crossed=3, items_per_min=3.0,
                       by_label={"litter": 3}, est_kg=0.057, est_kg_ci90=(0.0, 0.16), method="test",
                       provenance=Provenance(kind="synthetic", source="test"))
    assert est.items_crossed == 3


def test_counter_direction_matches_ground_truth():
    """Fails if the counter and the SYNTHETIC ground truth count different crossing directions (review finding #3)."""
    from t3det import synth
    from t3det.run_flux import counter_direction

    gt = {"line": [[640.0, 0.0], [640.0, 720.0]], "direction": synth.GT_DIRECTION,
          "flow_vector": list(FLOW_VECTORS[synth.GT_DIRECTION])}
    line = CountingLine(*map(tuple, gt["line"]))
    for xs in (list(range(600, 700, 8)), list(range(700, 600, -8))):  # with the flow, then against it
        truth = sum(synth.gt_crossed(a, b, 640.0) for a, b in zip(xs, xs[1:]))
        c = LineCrossingCounter(line, counter_direction(gt))
        for x in xs:
            c.update(1, x, 360.0)
        assert c.count == truth, (xs[0], c.count, truth)
    both = LineCrossingCounter(line, 0)  # the pre-fix setting disagrees with the ground truth against the flow
    for x in range(700, 600, -8):
        both.update(1, x, 360.0)
    assert both.count == 1


def test_flux_results_count_the_ground_truth_direction():
    files = sorted(RESULTS.glob("flux_synthetic*.json"))
    if not files:
        pytest.skip("no flux output yet")
    from t3det.run_flux import counter_direction

    for fp in files:
        f = json.loads(fp.read_text())
        cd = f["counter_direction"]
        expect = counter_direction({"line": cd["line"], "direction": cd["gt_direction"], "flow_vector": cd["flow_vector"]})
        assert cd["direction_sign"] == expect != 0, fp.name
        assert "either" not in f["flux_estimate"]["method"], fp.name
        h = f["headline"]
        assert h["matched"] + h["false"] == h["predicted"] and h["matched"] + h["missed"] == h["gt_crossings"]
        assert h["false"] == h["false_duplicate"] + h["false_spurious"]
        assert sum(r["gt_crossings"] for r in f["per_sequence"]) == h["gt_crossings"]
        assert math.isclose(h["signed_count_error_pct"],
                            100 * (h["predicted"] - h["gt_crossings"]) / h["gt_crossings"], abs_tol=0.01)
        assert "DIAGNOSTIC" in f["diagnostics"]["both_directions_same_tracks"]["label"]


def test_tracker_persists_across_frames_and_resets_per_clip():
    """ultralytics binds `persist` at the first track() call; persist=False there re-creates ByteTrack every frame."""
    import torch

    class Boxes:
        def __init__(self, x):
            self.xyxy = torch.tensor([[x - 5.0, 95.0, x + 5.0, 105.0]])
            self.id = torch.tensor([7.0])
            self.cls = torch.tensor([0.0])

    class Res:
        names = {0: "litter"}

        def __init__(self, x):
            self.boxes = Boxes(x)

    class Trk:
        resets = 0

        def reset(self):
            Trk.resets += 1

    class Model:
        def __init__(self):
            self.persist, self.predictor = [], type("P", (), {"trackers": [Trk()]})()

        def track(self, frame, **kw):
            self.persist.append(kw["persist"])
            return [Res(frame)]

    fc = FluxCounter.__new__(FluxCounter)
    fc.model, fc.line, fc.site_id, fc.mass = Model(), CountingLine((100, 0), (100, 200)), "t", SAIGON_VISUAL_COUNT
    fc.imgsz, fc.conf, fc.tracker, fc.direction, fc.device = 640, 0.1, "bytetrack.yaml", -1, "cpu"
    est = fc.run([80, 90, 110, 120], datetime(2026, 10, 4, tzinfo=timezone.utc), fps=5.0,
                 provenance=Provenance(kind="synthetic", source="test"))
    assert fc.model.persist == [True] * 4 and Trk.resets == 1 and est.items_crossed == 1
    assert fc.last_counter.events[0]["t"] == 2


def test_crossing_matching():
    from t3det.run_flux import match

    gt = [{"frame": 10, "y": 100.0, "h": 40}, {"frame": 30, "y": 300.0, "h": 20}]
    pred = [{"t": 11, "y": 105.0}, {"t": 12, "y": 110.0}, {"t": 80, "y": 500.0}]
    m = match(pred, gt, tol_frames=5)
    assert (m["matched"], m["false_duplicate"], m["false_spurious"], m["missed"]) == (1, 1, 1, 1)
